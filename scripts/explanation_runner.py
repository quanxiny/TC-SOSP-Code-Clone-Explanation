#!/usr/bin/env python3
"""Faithfulness and swap-stability evaluation for dual-graph explanations."""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
import torch
import torch.nn.functional as F

from .configlib import config_digest, resolve_workspace_path
from .contrastive_runner import BASELINE_ROOT, runner_args

if str(BASELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(BASELINE_ROOT))

from myModels.GAT_Edgepool_clone_detection import CodeCloneDetection  # noqa: E402
from reproduce_gcj import count_parameters, normalize_label  # noqa: E402
from reproduce_gcj_batched import graph_paths, load_graphs, set_seed  # noqa: E402


Graph = Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]

OPTIMAL_PAIR_METHODS = {
    "symmetric_semantic_optimal_pair": "none",
    "symmetric_semantic_attention_optimal_pair": "attention",
    "symmetric_semantic_shuffled_attention_optimal_pair": "shuffled",
    "symmetric_semantic_uniform_attention_optimal_pair": "uniform",
    "symmetric_shuffled_semantic_optimal_pair": "semantic_shuffled",
}
SYMMETRIC_METHODS = {
    "symmetric_grad_x_input",
    "symmetric_keep_remove_mask",
    "symmetric_gnnexplainer_node_mask_adapted",
    "symmetric_subgraphx_mcts_shapley_adapted",
    *OPTIMAL_PAIR_METHODS,
}


def stable_balanced_subset(lines: Sequence[str], total: int) -> List[str]:
    if total % 2:
        raise ValueError("explanation sample size must be even")
    groups = {0: [], 1: []}
    for line in lines:
        groups[normalize_label(line.split()[2])].append(line)
    selected = []
    for label in (0, 1):
        ranked = sorted(
            groups[label], key=lambda item: hashlib.sha256(item.encode("utf-8")).hexdigest()
        )
        selected.extend(ranked[:total // 2])
    return sorted(selected, key=lambda item: hashlib.sha256(item.encode("utf-8")).hexdigest())


def graph_with_features(graph: Graph, features: torch.Tensor) -> Graph:
    return features, graph[1], graph[2], graph[3], graph[4]


def encode_graph(model: torch.nn.Module, graph: Graph) -> torch.Tensor:
    features, edge_index, edge_attr, attention_edge_index, attention_edge_attr = graph
    batch = torch.zeros(features.size(0), dtype=torch.long, device=features.device)
    return model.encode_batched(
        features, edge_index, edge_attr, batch, attention_edge_index, attention_edge_attr
    )


def predict(model: torch.nn.Module, left: Graph, right: Graph,
            symmetric: bool) -> torch.Tensor:
    left_embedding = encode_graph(model, left)
    right_embedding = encode_graph(model, right)
    ordered = model.detect_embeddings(left_embedding, right_embedding)[0]
    if not symmetric:
        return ordered
    swapped = model.detect_embeddings(right_embedding, left_embedding)[0]
    clone_probability = torch.minimum(ordered[1], swapped[1])
    return torch.stack((1.0 - clone_probability, clone_probability))


def random_scores(line_key: str, graph_name: str, side: str, nodes: int) -> torch.Tensor:
    values = []
    for index in range(nodes):
        payload = "{}|{}|{}|{}".format(line_key, graph_name, side, index)
        value = int(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16], 16)
        values.append(value / float(16 ** 16 - 1))
    return torch.tensor(values, dtype=torch.float32)


def gradient_scores(model: torch.nn.Module, left: Graph, right: Graph,
                    target: int, symmetric: bool) -> Tuple[torch.Tensor, torch.Tensor]:
    left_features = left[0].detach().clone().requires_grad_(True)
    right_features = right[0].detach().clone().requires_grad_(True)
    probability = predict(
        model, graph_with_features(left, left_features),
        graph_with_features(right, right_features), symmetric,
    )[target]
    left_gradient, right_gradient = torch.autograd.grad(
        probability, (left_features, right_features), retain_graph=False
    )
    left_scores = (left_gradient * left_features).abs().sum(dim=(1, 2))
    right_scores = (right_gradient * right_features).abs().sum(dim=(1, 2))
    return left_scores.detach().cpu(), right_scores.detach().cpu()


def rank_normalize(scores: torch.Tensor) -> torch.Tensor:
    """Map arbitrary node scores to deterministic [0, 1] ranks."""
    values = scores.detach().float().cpu().numpy()
    if values.size <= 1:
        return torch.ones(values.size, dtype=torch.float32)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=np.float32)
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1)
        start = end
    return torch.from_numpy(ranks / float(values.size - 1))


def internal_node_attention_prior(model: torch.nn.Module, graph: Graph) -> torch.Tensor:
    """Recover the encoder's four node-token attention coefficient masses.

    This mirrors ``SingleNodeAttentionLayer.forward`` without changing its
    output. Padding tokens are excluded before the four coefficient masses are
    averaged. The result is a prior, never an explanation by itself.
    """
    features = graph[0]
    batch = torch.zeros(features.size(0), dtype=torch.long, device=features.device)
    valid_tokens = features.detach().abs().sum(dim=-1).gt(0)
    masses = []
    for index in range(1, 5):
        weight = getattr(model.h, "W{}".format(index))
        attention_vector = getattr(model.h, "a{}".format(index))
        projected = torch.matmul(features, weight)
        coefficients = model.h._softmax(
            torch.matmul(projected, attention_vector), batch
        ).squeeze(-1)
        mass = (coefficients * valid_tokens).sum(dim=1)
        masses.append(rank_normalize(mass))
    return torch.stack(masses).mean(dim=0)


def node_semantic_similarity(model: torch.nn.Module, left: Graph,
                             right: Graph) -> torch.Tensor:
    """Cosine similarity between the encoder's statement representations."""
    with torch.no_grad():
        left_nodes = F.normalize(model.h(left[0]), dim=-1)
        right_nodes = F.normalize(model.h(right[0]), dim=-1)
        similarity = left_nodes @ right_nodes.transpose(0, 1)
    return ((similarity + 1.0) * 0.5).clamp(0.0, 1.0).cpu()


def deterministic_prior_variant(prior: torch.Tensor, graph_name: str,
                                mode: str) -> torch.Tensor:
    if mode == "attention":
        return prior
    if mode == "uniform":
        return torch.full_like(prior, 0.5)
    if mode != "shuffled":
        raise ValueError("unsupported attention prior mode: {}".format(mode))
    digest = hashlib.sha256(graph_name.encode("utf-8")).hexdigest()
    generator = torch.Generator().manual_seed(int(digest[:16], 16) % (2 ** 63 - 1))
    return prior[torch.randperm(prior.numel(), generator=generator)]


def deterministic_similarity_shuffle(similarity: torch.Tensor, left_name: str,
                                     right_name: str) -> torch.Tensor:
    """Break node correspondence while preserving the similarity distribution."""
    left_digest = hashlib.sha256((left_name + "|semantic").encode("utf-8")).hexdigest()
    right_digest = hashlib.sha256((right_name + "|semantic").encode("utf-8")).hexdigest()
    left_generator = torch.Generator().manual_seed(
        int(left_digest[:16], 16) % (2 ** 63 - 1)
    )
    right_generator = torch.Generator().manual_seed(
        int(right_digest[:16], 16) % (2 ** 63 - 1)
    )
    left_order = torch.randperm(similarity.size(0), generator=left_generator)
    right_order = torch.randperm(similarity.size(1), generator=right_generator)
    return similarity[left_order][:, right_order]


def diffuse_over_cfg(scores: torch.Tensor, edge_index: torch.Tensor,
                     coefficient: float = 0.25) -> torch.Tensor:
    """Add one undirected CFG-neighbour step while retaining anchor scores."""
    if not scores.numel() or not edge_index.numel():
        return scores
    edges = edge_index.detach().cpu()
    source, target = edges[0], edges[1]
    non_self = source.ne(target)
    source, target = source[non_self], target[non_self]
    if not source.numel():
        return scores
    total = torch.zeros_like(scores)
    degree = torch.zeros_like(scores)
    total.index_add_(0, source, scores[target])
    total.index_add_(0, target, scores[source])
    degree.index_add_(0, source, torch.ones_like(scores[target]))
    degree.index_add_(0, target, torch.ones_like(scores[source]))
    neighbour = total / degree.clamp_min(1.0)
    return (1.0 - coefficient) * scores + coefficient * neighbour


def fixed_budget_nodes(scores: torch.Tensor, fraction: float) -> Set[int]:
    count = max(1, int(math.ceil(scores.numel() * fraction)))
    indices = torch.topk(scores, min(count, scores.numel()), largest=True).indices
    return {int(index) for index in indices.tolist()}


def induced_cfg_coverage(graph: Graph, selected: Set[int]) -> float:
    edges = graph[1].detach().cpu()
    source, target = edges[0], edges[1]
    non_self = source.ne(target)
    if not int(non_self.sum()):
        return 1.0
    chosen = torch.zeros(graph[0].size(0), dtype=torch.bool)
    if selected:
        chosen[list(selected)] = True
    retained = chosen[source[non_self]] & chosen[target[non_self]]
    return float(retained.float().mean())


def semantic_pair_quality(similarity: torch.Tensor, left_selected: Set[int],
                          right_selected: Set[int], target: int) -> float:
    if not left_selected or not right_selected:
        return 0.0
    left_indices = sorted(left_selected)
    right_indices = sorted(right_selected)
    selected = similarity[left_indices][:, right_indices]
    evidence = selected if target == 1 else 1.0 - selected
    bidirectional = torch.cat((evidence.max(dim=1).values, evidence.max(dim=0).values))
    return float(bidirectional.mean())


def paired_node_relations(similarity: torch.Tensor, left_selected: Set[int],
                          right_selected: Set[int], target: int) -> List[Dict[str, Any]]:
    """Return a deterministic one-to-one common or contrastive node relation."""
    candidates = []
    for left_index in sorted(left_selected):
        for right_index in sorted(right_selected):
            similarity_value = float(similarity[left_index, right_index])
            evidence = similarity_value if target == 1 else 1.0 - similarity_value
            candidates.append((evidence, left_index, right_index, similarity_value))
    candidates.sort(key=lambda row: (-row[0], row[1], row[2]))
    used_left: Set[int] = set()
    used_right: Set[int] = set()
    relations = []
    for evidence, left_index, right_index, similarity_value in candidates:
        if left_index in used_left or right_index in used_right:
            continue
        used_left.add(left_index)
        used_right.add(right_index)
        relations.append({
            "left_node": left_index,
            "right_node": right_index,
            "semantic_similarity": similarity_value,
            "relation_evidence": evidence,
            "relation": "common" if target == 1 else "contrast",
        })
        if len(relations) == min(len(left_selected), len(right_selected)):
            break
    return relations


def task_conditioned_candidate_sets(
        gradient_left: torch.Tensor, gradient_right: torch.Tensor,
        similarity: torch.Tensor, left: Graph, right: Graph, target: int,
        fraction: float, attention_left: Optional[torch.Tensor] = None,
        attention_right: Optional[torch.Tensor] = None) -> List[Dict[str, Any]]:
    """Build fixed-budget, task-aware candidate subgraph pairs."""
    gradient_left = rank_normalize(gradient_left)
    gradient_right = rank_normalize(gradient_right)
    if target == 1:
        semantic_left = rank_normalize(similarity.max(dim=1).values)
        semantic_right = rank_normalize(similarity.max(dim=0).values)
        relation_matrix = similarity
    else:
        semantic_left = rank_normalize(1.0 - similarity.max(dim=1).values)
        semantic_right = rank_normalize(1.0 - similarity.max(dim=0).values)
        relation_matrix = 1.0 - similarity

    pair_saliency = torch.sqrt(
        gradient_left[:, None].clamp_min(1e-6)
        * gradient_right[None, :].clamp_min(1e-6)
    ) * relation_matrix
    pair_left = rank_normalize(pair_saliency.max(dim=1).values)
    pair_right = rank_normalize(pair_saliency.max(dim=0).values)

    score_variants: List[Tuple[str, torch.Tensor, torch.Tensor]] = [
        ("gradient", gradient_left, gradient_right),
        ("semantic_025", 0.75 * gradient_left + 0.25 * semantic_left,
         0.75 * gradient_right + 0.25 * semantic_right),
        ("semantic_050", 0.50 * gradient_left + 0.50 * semantic_left,
         0.50 * gradient_right + 0.50 * semantic_right),
        ("semantic_075", 0.25 * gradient_left + 0.75 * semantic_left,
         0.25 * gradient_right + 0.75 * semantic_right),
        ("semantic_product", gradient_left * (0.25 + 0.75 * semantic_left),
         gradient_right * (0.25 + 0.75 * semantic_right)),
        ("paired_relation", pair_left, pair_right),
    ]
    structural_left = diffuse_over_cfg(
        0.5 * gradient_left + 0.5 * semantic_left, left[1]
    )
    structural_right = diffuse_over_cfg(
        0.5 * gradient_right + 0.5 * semantic_right, right[1]
    )
    score_variants.append(("semantic_cfg", structural_left, structural_right))

    if attention_left is not None and attention_right is not None:
        attention_left = rank_normalize(attention_left)
        attention_right = rank_normalize(attention_right)
        semantic_base_left = 0.5 * gradient_left + 0.5 * semantic_left
        semantic_base_right = 0.5 * gradient_right + 0.5 * semantic_right
        for coefficient in (0.25, 0.50):
            score_variants.append((
                "attention_{:.2f}".format(coefficient),
                (1.0 - coefficient) * semantic_base_left + coefficient * attention_left,
                (1.0 - coefficient) * semantic_base_right + coefficient * attention_right,
            ))

    unique: Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], Dict[str, Any]] = {}
    for name, left_scores, right_scores in score_variants:
        left_selected = fixed_budget_nodes(left_scores, fraction)
        right_selected = fixed_budget_nodes(right_scores, fraction)
        key = (tuple(sorted(left_selected)), tuple(sorted(right_selected)))
        unique.setdefault(key, {
            "name": name,
            "left_selected": left_selected,
            "right_selected": right_selected,
            "left_scores": left_scores,
            "right_scores": right_scores,
        })
    return list(unique.values())


def optimize_semantic_subgraph_pair(
        model: torch.nn.Module, left_name: str, right_name: str,
        left: Graph, right: Graph, target: int, fraction: float,
        attention_mode: str, sufficiency_weight: float,
        semantic_coefficient: float, structure_coefficient: float
        ) -> Dict[str, Any]:
    """Select a task-conditioned fixed-budget subgraph pair by exact intervention."""
    swapped = right_name < left_name
    first_name, second_name = (right_name, left_name) if swapped else (left_name, right_name)
    first, second = (right, left) if swapped else (left, right)
    gradient_first, gradient_second = gradient_scores(
        model, first, second, target, symmetric=True
    )
    similarity = node_semantic_similarity(model, first, second)

    attention_first = attention_second = None
    if attention_mode == "semantic_shuffled":
        similarity = deterministic_similarity_shuffle(
            similarity, first_name, second_name
        )
    elif attention_mode != "none":
        attention_first = deterministic_prior_variant(
            internal_node_attention_prior(model, first), first_name, attention_mode
        )
        attention_second = deterministic_prior_variant(
            internal_node_attention_prior(model, second), second_name, attention_mode
        )
    candidates = task_conditioned_candidate_sets(
        gradient_first, gradient_second, similarity, first, second, target,
        fraction, attention_first, attention_second,
    )
    with torch.no_grad():
        base_probability = float(predict(model, first, second, True)[target])
        for candidate in candidates:
            first_selected = candidate["left_selected"]
            second_selected = candidate["right_selected"]
            keep_probability = float(predict(
                model,
                apply_node_mask(first, first_selected, True),
                apply_node_mask(second, second_selected, True), True,
            )[target])
            remove_probability = float(predict(
                model,
                apply_node_mask(first, first_selected, False),
                apply_node_mask(second, second_selected, False), True,
            )[target])
            semantic_quality = semantic_pair_quality(
                similarity, first_selected, second_selected, target
            )
            structure_quality = 0.5 * (
                induced_cfg_coverage(first, first_selected)
                + induced_cfg_coverage(second, second_selected)
            )
            necessity = base_probability - remove_probability
            sufficiency_gap = abs(base_probability - keep_probability)
            candidate.update({
                "base_probability": base_probability,
                "keep_probability": keep_probability,
                "remove_probability": remove_probability,
                "necessity_drop": necessity,
                "absolute_sufficiency_gap": sufficiency_gap,
                "semantic_pair_quality": semantic_quality,
                "induced_cfg_coverage": structure_quality,
                "objective": (
                    necessity - sufficiency_weight * sufficiency_gap
                    + semantic_coefficient * semantic_quality
                    + structure_coefficient * structure_quality
                ),
            })
    best = max(candidates, key=lambda row: (row["objective"], row["name"]))
    relations = paired_node_relations(
        similarity, best["left_selected"], best["right_selected"], target
    )
    payload = {
        "selected_candidate": best["name"],
        "candidate_count": len(candidates),
        "attention_mode": attention_mode,
        "objective": best["objective"],
        "semantic_pair_quality": best["semantic_pair_quality"],
        "induced_cfg_coverage": best["induced_cfg_coverage"],
        "relations": relations,
        "candidate_diagnostics": [{
            key: candidate[key] for key in (
                "name", "objective", "necessity_drop", "absolute_sufficiency_gap",
                "semantic_pair_quality", "induced_cfg_coverage",
            )
        } for candidate in candidates],
    }
    if not swapped:
        payload.update({
            "left_selected": best["left_selected"],
            "right_selected": best["right_selected"],
            "left_scores": best["left_scores"],
            "right_scores": best["right_scores"],
        })
        return payload
    payload["relations"] = [{
        **relation,
        "left_node": relation["right_node"],
        "right_node": relation["left_node"],
    } for relation in relations]
    payload.update({
        "left_selected": best["right_selected"],
        "right_selected": best["left_selected"],
        "left_scores": best["right_scores"],
        "right_scores": best["left_scores"],
    })
    return payload


def integrated_gradient_scores(model: torch.nn.Module, left: Graph, right: Graph,
                               target: int, steps: int) -> Tuple[torch.Tensor, torch.Tensor]:
    left_input = left[0].detach()
    right_input = right[0].detach()
    left_gradient_sum = torch.zeros_like(left_input)
    right_gradient_sum = torch.zeros_like(right_input)
    for step in range(1, steps + 1):
        alpha = float(step) / steps
        left_features = (left_input * alpha).requires_grad_(True)
        right_features = (right_input * alpha).requires_grad_(True)
        probability = predict(
            model, graph_with_features(left, left_features),
            graph_with_features(right, right_features), False,
        )[target]
        left_gradient, right_gradient = torch.autograd.grad(
            probability, (left_features, right_features), retain_graph=False
        )
        left_gradient_sum += left_gradient.detach()
        right_gradient_sum += right_gradient.detach()
    left_scores = (left_input * left_gradient_sum / steps).abs().sum(dim=(1, 2))
    right_scores = (right_input * right_gradient_sum / steps).abs().sum(dim=(1, 2))
    return left_scores.cpu(), right_scores.cpu()


def optimize_mask_scores(model: torch.nn.Module, left: Graph, right: Graph,
                         target: int, symmetric: bool, steps: int,
                         learning_rate: float, sparsity_lambda: float
                         ) -> Tuple[torch.Tensor, torch.Tensor]:
    left_logits = torch.full(
        (left[0].size(0),), 2.0, dtype=left[0].dtype,
        device=left[0].device, requires_grad=True,
    )
    right_logits = torch.full(
        (right[0].size(0),), 2.0, dtype=right[0].dtype,
        device=right[0].device, requires_grad=True,
    )
    optimizer = torch.optim.Adam((left_logits, right_logits), lr=learning_rate)
    for _ in range(steps):
        optimizer.zero_grad()
        left_mask = left_logits.sigmoid()
        right_mask = right_logits.sigmoid()
        keep = predict(
            model,
            graph_with_features(left, left[0] * left_mask[:, None, None]),
            graph_with_features(right, right[0] * right_mask[:, None, None]),
            symmetric,
        )[target].clamp(1e-6, 1.0 - 1e-6)
        remove = predict(
            model,
            graph_with_features(left, left[0] * (1.0 - left_mask[:, None, None])),
            graph_with_features(right, right[0] * (1.0 - right_mask[:, None, None])),
            symmetric,
        )[target].clamp(1e-6, 1.0 - 1e-6)
        sparsity = 0.5 * (left_mask.mean() + right_mask.mean())
        loss = -keep.log() - (1.0 - remove).log() + sparsity_lambda * sparsity
        loss.backward()
        optimizer.step()
    return left_logits.sigmoid().detach().cpu(), right_logits.sigmoid().detach().cpu()


def canonical_explainer_seed_key(
        left_name: str, right_name: str, target: int, explainer_seed: int,
        legacy_seed42: bool = False) -> str:
    first_name, second_name = sorted((left_name, right_name))
    base = "{}|{}|{}".format(first_name, second_name, target)
    if legacy_seed42 and explainer_seed == 42:
        return base
    return "{}|explainer_seed={}".format(base, explainer_seed)


def optimize_gnnexplainer_node_scores(
        model: torch.nn.Module, left: Graph, right: Graph, target: int,
        steps: int, learning_rate: float, size_coefficient: float,
        entropy_coefficient: float, initialization_seed_key: str,
        initialization_std: float = 0.1) -> Tuple[torch.Tensor, torch.Tensor]:
    """Pair-level adaptation of the GNNExplainer mutual-information objective.

    The released encoder does not expose a PyG ``MessagePassing`` edge-mask
    hook, so this strong baseline optimizes node-feature gates while retaining
    the original CFG topology.  Unlike our keep/remove baseline, it uses only
    target sufficiency plus the standard size and binary-entropy penalties.
    """
    generator = torch.Generator(device=left[0].device)
    generator.manual_seed(
        int(hashlib.sha256(initialization_seed_key.encode("utf-8")).hexdigest()[:16], 16)
        % (2 ** 63 - 1)
    )
    left_logits = (
        torch.randn(
            left[0].size(0), dtype=left[0].dtype,
            device=left[0].device, generator=generator,
        ) * initialization_std
    ).requires_grad_()
    right_logits = (
        torch.randn(
            right[0].size(0), dtype=right[0].dtype,
            device=right[0].device, generator=generator,
        ) * initialization_std
    ).requires_grad_()
    optimizer = torch.optim.Adam((left_logits, right_logits), lr=learning_rate)
    for _ in range(steps):
        optimizer.zero_grad()
        left_mask = left_logits.sigmoid()
        right_mask = right_logits.sigmoid()
        probability = predict(
            model,
            graph_with_features(left, left[0] * left_mask[:, None, None]),
            graph_with_features(right, right[0] * right_mask[:, None, None]),
            symmetric=True,
        )[target].clamp(1e-6, 1.0 - 1e-6)
        size = 0.5 * (left_mask.mean() + right_mask.mean())
        left_entropy = -(
            left_mask * left_mask.clamp_min(1e-6).log()
            + (1.0 - left_mask)
            * (1.0 - left_mask).clamp_min(1e-6).log()
        ).mean()
        right_entropy = -(
            right_mask * right_mask.clamp_min(1e-6).log()
            + (1.0 - right_mask)
            * (1.0 - right_mask).clamp_min(1e-6).log()
        ).mean()
        entropy = 0.5 * (left_entropy + right_entropy)
        loss = (
            -probability.log()
            + size_coefficient * size
            + entropy_coefficient * entropy
        )
        loss.backward()
        optimizer.step()
    return left_logits.sigmoid().detach().cpu(), right_logits.sigmoid().detach().cpu()


def pair_shapley_reward(
        model: torch.nn.Module, left: Graph, right: Graph, target: int,
        left_selected: Set[int], right_selected: Set[int], samples: int,
        seed_key: str) -> float:
    """Monte-Carlo marginal contribution of one dual-graph coalition."""
    cache_seed = "{}|{}|{}".format(
        seed_key, ",".join(map(str, sorted(left_selected))),
        ",".join(map(str, sorted(right_selected))),
    )
    generator = random.Random(
        int(hashlib.sha256(cache_seed.encode("utf-8")).hexdigest()[:16], 16)
    )
    left_complement = [
        index for index in range(left[0].size(0)) if index not in left_selected
    ]
    right_complement = [
        index for index in range(right[0].size(0)) if index not in right_selected
    ]
    values = []
    with torch.no_grad():
        for _ in range(samples):
            left_context = {
                index for index in left_complement if generator.random() < 0.5
            }
            right_context = {
                index for index in right_complement if generator.random() < 0.5
            }
            with_probability = float(predict(
                model,
                apply_node_mask(left, left_context | left_selected, True),
                apply_node_mask(right, right_context | right_selected, True),
                symmetric=True,
            )[target])
            without_probability = float(predict(
                model,
                apply_node_mask(left, left_context, True),
                apply_node_mask(right, right_context, True),
                symmetric=True,
            )[target])
            values.append(with_probability - without_probability)
    return float(np.mean(values))


def subgraphx_mcts_shapley_scores(
        model: torch.nn.Module, left_name: str, right_name: str,
        left: Graph, right: Graph, target: int, fraction: float,
        iterations: int, shapley_samples: int,
        explainer_seed: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Model-agnostic SubgraphX-style MCTS over a dual-graph node coalition.

    This preserves SubgraphX's two defining mechanisms--discrete subgraph
    exploration by MCTS and Monte-Carlo Shapley rewards--while adapting its
    intervention from one graph to the pair classifier's two CFGs.
    """
    swapped = right_name < left_name
    first_name, second_name = (
        (right_name, left_name) if swapped else (left_name, right_name)
    )
    first, second = (right, left) if swapped else (left, right)
    first_gradient, second_gradient = gradient_scores(
        model, first, second, target, symmetric=True
    )
    first_budget = max(1, int(math.ceil(first[0].size(0) * fraction)))
    second_budget = max(1, int(math.ceil(second[0].size(0) * fraction)))
    initial = (
        frozenset(range(first[0].size(0))),
        frozenset(range(second[0].size(0))),
    )
    # Preserve the already frozen C9 trajectory as the seed-42 member while
    # making subsequent explainer seeds explicit and pair-order independent.
    seed_key = canonical_explainer_seed_key(
        first_name, second_name, target, explainer_seed, legacy_seed42=True,
    )
    generator = random.Random(
        int(hashlib.sha256(seed_key.encode("utf-8")).hexdigest()[:16], 16)
    )
    tree: Dict[Tuple[frozenset, frozenset], Dict[str, Any]] = {}
    reward_cache: Dict[Tuple[frozenset, frozenset], float] = {}

    def is_terminal(state: Tuple[frozenset, frozenset]) -> bool:
        return len(state[0]) == first_budget and len(state[1]) == second_budget

    def actions(state: Tuple[frozenset, frozenset]) -> List[Tuple[int, int]]:
        available = []
        if len(state[0]) > first_budget:
            available.extend((0, index) for index in state[0])
        if len(state[1]) > second_budget:
            available.extend((1, index) for index in state[1])
        # Low-gradient removals are considered first, while MCTS/rollout
        # randomness still explores alternatives.
        return sorted(available, key=lambda action: (
            float(first_gradient[action[1]]) if action[0] == 0
            else float(second_gradient[action[1]]),
            action[0], action[1],
        ))

    def transition(state: Tuple[frozenset, frozenset],
                   action: Tuple[int, int]) -> Tuple[frozenset, frozenset]:
        sides = [set(state[0]), set(state[1])]
        sides[action[0]].remove(action[1])
        return frozenset(sides[0]), frozenset(sides[1])

    def rollout(state: Tuple[frozenset, frozenset]) -> Tuple[frozenset, frozenset]:
        current = state
        while not is_terminal(current):
            candidates = actions(current)
            # Mostly follow the low-gradient policy, but retain stochastic
            # exploration so distinct MCTS visits reach distinct coalitions.
            head = max(1, int(math.ceil(len(candidates) * 0.25)))
            pool = candidates[:head] if generator.random() < 0.8 else candidates
            current = transition(current, pool[generator.randrange(len(pool))])
        return current

    def reward(state: Tuple[frozenset, frozenset]) -> float:
        if state not in reward_cache:
            reward_cache[state] = pair_shapley_reward(
                model, first, second, target, set(state[0]), set(state[1]),
                shapley_samples, seed_key,
            )
        return reward_cache[state]

    gradient_terminal = (
        frozenset(fixed_budget_nodes(first_gradient, fraction)),
        frozenset(fixed_budget_nodes(second_gradient, fraction)),
    )
    best_state = gradient_terminal
    best_reward = reward(best_state)
    for _ in range(iterations):
        state = initial
        path = []
        while not is_terminal(state):
            node = tree.setdefault(state, {
                "visits": 0,
                "total": 0.0,
                "children": {},
                "untried": actions(state),
            })
            path.append(state)
            if node["untried"]:
                # Mix deterministic promising removals with broader actions.
                if generator.random() < 0.8:
                    action_index = generator.randrange(
                        max(1, int(math.ceil(len(node["untried"]) * 0.25)))
                    )
                else:
                    action_index = generator.randrange(len(node["untried"]))
                action = node["untried"].pop(action_index)
                child = transition(state, action)
                node["children"][action] = child
                state = child
                path.append(state)
                break
            log_parent = math.log(max(1, node["visits"]))
            state = max(node["children"].values(), key=lambda child: (
                tree.get(child, {}).get("total", 0.0)
                / max(1, tree.get(child, {}).get("visits", 0))
                + 1.414 * math.sqrt(
                    log_parent / max(1, tree.get(child, {}).get("visits", 0))
                )
            ))
        terminal = state if is_terminal(state) else rollout(state)
        value = reward(terminal)
        if value > best_reward:
            best_reward, best_state = value, terminal
        for visited in path:
            node = tree.setdefault(visited, {
                "visits": 0, "total": 0.0, "children": {},
                "untried": actions(visited),
            })
            node["visits"] += 1
            node["total"] += value

    first_scores = torch.zeros(first[0].size(0), dtype=torch.float32)
    second_scores = torch.zeros(second[0].size(0), dtype=torch.float32)
    first_scores[list(best_state[0])] = 1.0
    second_scores[list(best_state[1])] = 1.0
    return (
        (second_scores, first_scores) if swapped
        else (first_scores, second_scores)
    )


def explain(method: str, model: torch.nn.Module, line_key: str,
            left_name: str, right_name: str, left: Graph, right: Graph,
            target: int, integrated_steps: int, mask_steps: int,
            mask_learning_rate: float, mask_sparsity_lambda: float,
            fraction: float = 0.2, gnnexplainer_entropy: float = 0.1,
            subgraphx_iterations: int = 48, subgraphx_shapley_samples: int = 4,
            explainer_seed: int = 42,
            gnnexplainer_initialization_std: float = 0.1,
            ) -> Tuple[torch.Tensor, torch.Tensor]:
    if method == "random":
        return (
            random_scores(line_key, left_name, "left", left[0].size(0)),
            random_scores(line_key, right_name, "right", right[0].size(0)),
        )
    if method == "grad_x_input":
        return gradient_scores(model, left, right, target, symmetric=False)
    if method == "symmetric_grad_x_input":
        return gradient_scores(model, left, right, target, symmetric=True)
    if method == "integrated_gradients":
        return integrated_gradient_scores(model, left, right, target, integrated_steps)
    if method in {"ordered_keep_remove_mask", "symmetric_keep_remove_mask"}:
        return optimize_mask_scores(
            model, left, right, target,
            symmetric=(method == "symmetric_keep_remove_mask"),
            steps=mask_steps, learning_rate=mask_learning_rate,
            sparsity_lambda=mask_sparsity_lambda,
        )
    if method == "symmetric_gnnexplainer_node_mask_adapted":
        swapped = right_name < left_name
        first_name, second_name = (
            (right_name, left_name) if swapped else (left_name, right_name)
        )
        first, second = (right, left) if swapped else (left, right)
        first_scores, second_scores = optimize_gnnexplainer_node_scores(
            model, first, second, target, steps=mask_steps,
            learning_rate=mask_learning_rate,
            size_coefficient=mask_sparsity_lambda,
            entropy_coefficient=gnnexplainer_entropy,
            initialization_seed_key=canonical_explainer_seed_key(
                first_name, second_name, target, explainer_seed,
            ),
            initialization_std=gnnexplainer_initialization_std,
        )
        return (
            (second_scores, first_scores) if swapped
            else (first_scores, second_scores)
        )
    if method == "symmetric_subgraphx_mcts_shapley_adapted":
        return subgraphx_mcts_shapley_scores(
            model, left_name, right_name, left, right, target, fraction,
            subgraphx_iterations, subgraphx_shapley_samples, explainer_seed,
        )
    raise ValueError("unsupported explanation method: {}".format(method))


def top_nodes(scores: torch.Tensor, fraction: float) -> Set[int]:
    count = max(1, int(math.ceil(scores.numel() * fraction)))
    indices = torch.topk(scores, min(count, scores.numel()), largest=True).indices.tolist()
    return set(int(index) for index in indices)


def apply_node_mask(graph: Graph, selected: Set[int], keep_selected: bool) -> Graph:
    mask = torch.zeros(graph[0].size(0), dtype=graph[0].dtype, device=graph[0].device)
    if keep_selected:
        if selected:
            mask[list(selected)] = 1.0
    else:
        mask.fill_(1.0)
        if selected:
            mask[list(selected)] = 0.0
    features = graph[0] * mask[:, None, None]
    return graph_with_features(graph, features)


def jaccard(first: Set[int], second: Set[int]) -> float:
    union = first | second
    return len(first & second) / len(union) if union else 1.0


def bootstrap_mean_ci(values: Sequence[float], resamples: int, seed: int) -> List[float]:
    if not values:
        return [float("nan"), float("nan")]
    array = np.asarray(values, dtype=float)
    generator = np.random.default_rng(seed)
    draws = generator.integers(0, len(array), size=(resamples, len(array)))
    means = array[draws].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def cluster_bootstrap_mean_ci(records: Sequence[Dict[str, Any]], metric: str,
                              resamples: int, seed: int) -> List[float]:
    grouped: Dict[str, List[float]] = {}
    for record in records:
        grouped.setdefault(record["problem_pair_cluster"], []).append(float(record[metric]))
    keys = sorted(grouped)
    generator = np.random.default_rng(seed)
    # Sampling clusters retains every observation in each sampled cluster.  The
    # vectorized sums/counts formulation is equivalent to materializing those
    # observations, while avoiding a Python loop over thousands of resamples.
    group_sums = np.asarray([sum(grouped[key]) for key in keys], dtype=float)
    group_counts = np.asarray([len(grouped[key]) for key in keys], dtype=float)
    sampled = generator.integers(
        0, len(keys), size=(resamples, len(keys)), endpoint=False
    )
    means = group_sums[sampled].sum(axis=1) / group_counts[sampled].sum(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def aggregate(records: Sequence[Dict[str, Any]], resamples: int, seed: int,
              include_subgroups: bool = True) -> Dict[str, Any]:
    metrics = [
        "necessity_drop", "sufficiency_gap", "swap_jaccard",
        "selected_node_fraction", "seconds",
    ]
    for optional_metric in (
        "absolute_sufficiency_gap", "semantic_pair_quality",
        "induced_cfg_coverage", "candidate_objective",
    ):
        if records and all(optional_metric in record for record in records):
            metrics.append(optional_metric)
    result: Dict[str, Any] = {
        "pairs": len(records),
        "problem_pair_clusters": len({record["problem_pair_cluster"] for record in records}),
    }
    for metric_index, metric in enumerate(metrics):
        values = [float(record[metric]) for record in records]
        result[metric] = {
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "bootstrap_95_ci": bootstrap_mean_ci(
                values, resamples, seed + metric_index * 1009
            ),
            "problem_pair_cluster_bootstrap_95_ci": cluster_bootstrap_mean_ci(
                records, metric, resamples, seed + metric_index * 1009 + 17
            ),
        }
    result["prediction_accuracy"] = float(np.mean([
        record["prediction"] == record["label"] for record in records
    ]))
    if include_subgroups:
        result["by_label"] = {
            str(label): aggregate(
                [record for record in records if record["label"] == label],
                resamples, seed + 20000 + label, include_subgroups=False,
            )
            for label in (0, 1)
        }
        result["by_prediction_correctness"] = {
            name: aggregate(subset, resamples, seed + 30000 + index, include_subgroups=False)
            for index, (name, subset) in enumerate((
                ("correct", [record for record in records if record["prediction"] == record["label"]]),
                ("incorrect", [record for record in records if record["prediction"] != record["label"]]),
            )) if subset
        }
    return result


def paired_comparison(baseline: Sequence[Dict[str, Any]],
                      candidate: Sequence[Dict[str, Any]],
                      resamples: int, seed: int) -> Dict[str, Any]:
    baseline_by_pair = {int(record["pair_index"]): record for record in baseline}
    candidate_by_pair = {int(record["pair_index"]): record for record in candidate}
    if set(baseline_by_pair) != set(candidate_by_pair):
        raise RuntimeError("explanation methods do not cover identical pairs")
    delta_records = []
    for pair_index in sorted(baseline_by_pair):
        first = baseline_by_pair[pair_index]
        second = candidate_by_pair[pair_index]
        delta_records.append({
            "problem_pair_cluster": second["problem_pair_cluster"],
            "necessity_drop_delta": second["necessity_drop"] - first["necessity_drop"],
            "absolute_sufficiency_gap_improvement": (
                abs(first["sufficiency_gap"]) - abs(second["sufficiency_gap"])
            ),
            "swap_jaccard_delta": second["swap_jaccard"] - first["swap_jaccard"],
            "seconds_delta": second["seconds"] - first["seconds"],
        })
    result = {"pairs": len(delta_records), "positive_means_candidate_is_better_for": [
        "necessity_drop_delta", "absolute_sufficiency_gap_improvement", "swap_jaccard_delta",
    ]}
    for index, metric in enumerate((
        "necessity_drop_delta", "absolute_sufficiency_gap_improvement",
        "swap_jaccard_delta", "seconds_delta",
    )):
        values = [float(record[metric]) for record in delta_records]
        result[metric] = {
            "mean": float(np.mean(values)),
            "bootstrap_95_ci": bootstrap_mean_ci(values, resamples, seed + index * 1013),
            "problem_pair_cluster_bootstrap_95_ci": cluster_bootstrap_mean_ci(
                delta_records, metric, resamples, seed + index * 1013 + 19
            ),
        }
    return result


def load_checkpoint_model(config: Dict[str, Any], device: torch.device) -> torch.nn.Module:
    args = runner_args(config)
    model = CodeCloneDetection(
        args.num_layers, args.hidden, args.nheads, args.num_classes,
        args.dropout, args.alpha, True,
    ).to(device)
    checkpoint_path = resolve_workspace_path(config["predictor"]["checkpoint"])
    state = torch.load(checkpoint_path, map_location=device)
    if isinstance(state, dict) and "model" in state:
        state = state["model"]
    model.load_state_dict(state)
    model.eval()
    # The released cuDNN BiLSTM requires training mode for input-gradient
    # backward. It has no dropout, while the graph encoder remains in eval mode.
    model.bi_lstm.train()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    return model


def run(config: Dict[str, Any]) -> int:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the reproduced encoder")
    output_dir = resolve_workspace_path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = config_digest(config)
    resolved_path = output_dir / "resolved_config.json"
    if resolved_path.exists():
        previous = json.loads(resolved_path.read_text(encoding="utf-8"))
        if previous["config_sha256"] != digest:
            raise RuntimeError("refusing resume/overwrite with a different config hash")
    else:
        resolved_path.write_text(json.dumps({
            "config_sha256": digest, "config": config,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    seed = int(config["seed"])
    set_seed(seed)
    random.seed(seed)
    device = torch.device(config["device"])
    checkpoint_path = resolve_workspace_path(config["predictor"]["checkpoint"])
    checkpoint_sha = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
    validation_path = resolve_workspace_path(config["paths"]["validation_split"])
    validation_lines = validation_path.read_text(encoding="utf-8").splitlines(True)
    sample_count = int(config["explanation"]["sample_pairs"])
    selected_lines = stable_balanced_subset(validation_lines, sample_count)
    manifest_path = output_dir / "validation_explanation_manifest.txt"
    manifest_path.write_text("".join(selected_lines), encoding="utf-8")
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    required = graph_paths(selected_lines)
    previous_directory = Path.cwd()
    try:
        os.chdir(str(BASELINE_ROOT))
        graphs = load_graphs(
            required,
            resolve_workspace_path(config["paths"]["source_dir"]),
            resolve_workspace_path(config["paths"]["vector_dir"]),
            device,
            int(config["model"]["hidden"]),
        )
    finally:
        os.chdir(str(previous_directory))
    model = load_checkpoint_model(config, device)
    methods = list(config["baselines"])
    fraction = float(config["explanation"]["top_node_fraction"])
    integrated_steps = int(config["explanation"]["integrated_gradients_steps"])
    mask_steps = int(config["explanation"]["mask_optimization_steps"])
    mask_learning_rate = float(config["explanation"]["mask_learning_rate"])
    mask_sparsity_lambda = float(config["explanation"]["mask_sparsity_lambda"])
    gnnexplainer_entropy = float(
        config["explanation"].get("gnnexplainer_entropy_coefficient", 0.1)
    )
    subgraphx_iterations = int(
        config["explanation"].get("subgraphx_mcts_iterations", 48)
    )
    subgraphx_shapley_samples = int(
        config["explanation"].get("subgraphx_shapley_samples", 4)
    )
    explainer_seed = int(config["explanation"].get("explainer_seed", seed))
    gnnexplainer_initialization_std = float(
        config["explanation"].get("gnnexplainer_initialization_std", 0.1)
    )
    optimal_sufficiency_weight = float(
        config["explanation"].get("optimal_sufficiency_weight", 1.0)
    )
    optimal_semantic_coefficient = float(
        config["explanation"].get("optimal_semantic_coefficient", 0.0)
    )
    optimal_structure_coefficient = float(
        config["explanation"].get("optimal_structure_coefficient", 0.0)
    )
    method_records: Dict[str, List[Dict[str, Any]]] = {method: [] for method in methods}
    completed: Dict[str, Set[int]] = {method: set() for method in methods}
    for method in methods:
        record_path = output_dir / "{}_records.jsonl".format(method)
        if config.get("resume") and record_path.is_file():
            for existing_line in record_path.read_text(encoding="utf-8").splitlines():
                record = json.loads(existing_line)
                method_records[method].append(record)
                completed[method].add(int(record["pair_index"]))
        elif record_path.exists():
            record_path.unlink()
    prediction_cache: Dict[Tuple[str, str], Tuple[int, float]] = {}

    for pair_index, line in enumerate(selected_lines):
        fields = line.split()
        left_name, right_name = fields[:2]
        label = normalize_label(fields[2])
        left, right = graphs[left_name], graphs[right_name]
        line_key = line.rstrip("\n")
        for method in methods:
            if pair_index in completed[method]:
                continue
            symmetric = method in SYMMETRIC_METHODS
            cache_key = (line_key, "symmetric" if symmetric else "ordered")
            if cache_key not in prediction_cache:
                with torch.no_grad():
                    base_output = predict(model, left, right, symmetric)
                prediction_cache[cache_key] = (
                    int(base_output.argmax().item()), float(base_output.max().item())
                )
            target, base_probability = prediction_cache[cache_key]
            torch.cuda.synchronize(device)
            started = time.perf_counter()
            optimal_payload = None
            if method in OPTIMAL_PAIR_METHODS:
                optimal_payload = optimize_semantic_subgraph_pair(
                    model, left_name, right_name, left, right, target, fraction,
                    OPTIMAL_PAIR_METHODS[method], optimal_sufficiency_weight,
                    optimal_semantic_coefficient, optimal_structure_coefficient,
                )
                left_scores = optimal_payload["left_scores"]
                right_scores = optimal_payload["right_scores"]
                left_selected = optimal_payload["left_selected"]
                right_selected = optimal_payload["right_selected"]
            else:
                left_scores, right_scores = explain(
                    method, model, line_key, left_name, right_name,
                    left, right, target, integrated_steps, mask_steps,
                    mask_learning_rate, mask_sparsity_lambda, fraction,
                    gnnexplainer_entropy, subgraphx_iterations,
                    subgraphx_shapley_samples, explainer_seed,
                    gnnexplainer_initialization_std,
                )
                left_selected = top_nodes(left_scores, fraction)
                right_selected = top_nodes(right_scores, fraction)
            with torch.no_grad():
                keep_probability = float(predict(
                    model,
                    apply_node_mask(left, left_selected, True),
                    apply_node_mask(right, right_selected, True),
                    symmetric,
                )[target].item())
                remove_probability = float(predict(
                    model,
                    apply_node_mask(left, left_selected, False),
                    apply_node_mask(right, right_selected, False),
                    symmetric,
                )[target].item())
            swapped_line_key = "{} {} {}".format(right_name, left_name, fields[2])
            if method in OPTIMAL_PAIR_METHODS:
                # The optimizer canonicalizes the unordered graph-name pair,
                # so its swapped explanation is exactly the mapped selection.
                # The smoke test additionally verifies this equivalence by
                # recomputing both orders; formal runs avoid duplicate search.
                swapped_original_right = right_selected
                swapped_original_left = left_selected
            else:
                swapped_left_scores, swapped_right_scores = explain(
                    method, model, swapped_line_key, right_name, left_name,
                    right, left, target, integrated_steps, mask_steps,
                    mask_learning_rate, mask_sparsity_lambda, fraction,
                    gnnexplainer_entropy, subgraphx_iterations,
                    subgraphx_shapley_samples, explainer_seed,
                    gnnexplainer_initialization_std,
                )
                swapped_original_right = top_nodes(swapped_left_scores, fraction)
                swapped_original_left = top_nodes(swapped_right_scores, fraction)
            swap_score = 0.5 * (
                jaccard(left_selected, swapped_original_left)
                + jaccard(right_selected, swapped_original_right)
            )
            torch.cuda.synchronize(device)
            elapsed = time.perf_counter() - started
            selected_fraction = 0.5 * (
                len(left_selected) / left_scores.numel()
                + len(right_selected) / right_scores.numel()
            )
            record = {
                "pair_index": pair_index,
                "left": left_name,
                "right": right_name,
                "problem_pair_cluster": "--".join(sorted((
                    Path(left_name).parent.name, Path(right_name).parent.name,
                ))),
                "label": label,
                "prediction": target,
                "base_target_probability": base_probability,
                "keep_target_probability": keep_probability,
                "remove_target_probability": remove_probability,
                "necessity_drop": base_probability - remove_probability,
                "sufficiency_gap": base_probability - keep_probability,
                "absolute_sufficiency_gap": abs(base_probability - keep_probability),
                "swap_jaccard": swap_score,
                "selected_node_fraction": selected_fraction,
                "left_nodes": left_scores.numel(),
                "right_nodes": right_scores.numel(),
                "left_selected": sorted(left_selected),
                "right_selected": sorted(right_selected),
                "seconds": elapsed,
                "predictor": "symmetric_min" if symmetric else "ordered",
                "explainer_seed": explainer_seed,
            }
            if optimal_payload is not None:
                record.update({
                    "selected_candidate": optimal_payload["selected_candidate"],
                    "candidate_count": optimal_payload["candidate_count"],
                    "attention_prior_mode": optimal_payload["attention_mode"],
                    "candidate_objective": optimal_payload["objective"],
                    "semantic_pair_quality": optimal_payload["semantic_pair_quality"],
                    "induced_cfg_coverage": optimal_payload["induced_cfg_coverage"],
                    "node_relations": optimal_payload["relations"],
                    "candidate_diagnostics": optimal_payload["candidate_diagnostics"],
                    "swap_evaluation": "canonical_exact_equivariance",
                })
            method_records[method].append(record)
            with (output_dir / "{}_records.jsonl".format(method)).open(
                    "a", encoding="utf-8") as record_file:
                record_file.write(json.dumps(record, ensure_ascii=False) + "\n")
        print("explained pair {}/{}".format(pair_index + 1, len(selected_lines)))

    resamples = int(config["explanation"]["bootstrap_resamples"])
    comparisons = {}
    if {"grad_x_input", "symmetric_grad_x_input"}.issubset(method_records):
        comparisons["symmetric_grad_x_input_minus_grad_x_input"] = paired_comparison(
            method_records["grad_x_input"], method_records["symmetric_grad_x_input"],
            resamples, seed + 700001,
        )
    if {"ordered_keep_remove_mask", "symmetric_keep_remove_mask"}.issubset(method_records):
        comparisons[
            "symmetric_keep_remove_mask_minus_ordered_keep_remove_mask"
        ] = paired_comparison(
            method_records["ordered_keep_remove_mask"],
            method_records["symmetric_keep_remove_mask"],
            resamples, seed + 800001,
        )
    if "symmetric_grad_x_input" in method_records:
        for comparison_index, method in enumerate(OPTIMAL_PAIR_METHODS):
            if method in method_records:
                comparisons[method + "_minus_symmetric_grad_x_input"] = paired_comparison(
                    method_records["symmetric_grad_x_input"], method_records[method],
                    resamples, seed + 900001 + comparison_index * 100003,
                )
    if "symmetric_semantic_optimal_pair" in method_records:
        for comparison_index, baseline in enumerate((
            "symmetric_gnnexplainer_node_mask_adapted",
            "symmetric_subgraphx_mcts_shapley_adapted",
        )):
            if baseline in method_records:
                comparisons[
                    "symmetric_semantic_optimal_pair_minus_" + baseline
                ] = paired_comparison(
                    method_records[baseline],
                    method_records["symmetric_semantic_optimal_pair"],
                    resamples, seed + 1600001 + comparison_index * 100003,
                )
    if {
        "symmetric_semantic_shuffled_attention_optimal_pair",
        "symmetric_semantic_attention_optimal_pair",
    }.issubset(method_records):
        comparisons["real_attention_minus_shuffled_attention"] = paired_comparison(
            method_records["symmetric_semantic_shuffled_attention_optimal_pair"],
            method_records["symmetric_semantic_attention_optimal_pair"],
            resamples, seed + 1400001,
        )

    summary = {
        "config_sha256": digest,
        "configuration": config,
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": checkpoint_sha,
        "model_parameter_count": count_parameters(model),
        "validation_manifest": str(manifest_path),
        "validation_manifest_sha256": manifest_sha,
        "sample_pairs": len(selected_lines),
        "unique_graphs": len(required),
        "explainer_seed": explainer_seed,
        "explainer_randomness": {
            "gnnexplainer_initialization": "pair-canonical Gaussian node logits",
            "gnnexplainer_initialization_std": gnnexplainer_initialization_std,
            "subgraphx_seed42_compatibility": (
                "seed 42 preserves the frozen content-hash trajectory"
            ),
        },
        "methods": {
            method: aggregate(records, resamples, seed + index * 100003)
            for index, (method, records) in enumerate(method_records.items())
        },
        "paired_comparisons": comparisons,
        "metric_direction": {
            "necessity_drop": "higher_is_better",
            "sufficiency_gap": "lower_absolute_is_better",
            "swap_jaccard": "higher_is_better",
            "semantic_pair_quality": "higher_is_better_task_conditioned_proxy",
            "induced_cfg_coverage": "higher_is_better_structural_proxy",
            "seconds": "lower_is_better",
        },
        "test_metrics": None,
        "test_policy": "sealed_during_method_comparison",
        "limitations": [
            "feature masking keeps graph topology fixed",
            "integrated gradients uses a zero-feature baseline",
            "node-level provenance ground truth is unavailable for natural validation pairs",
        ],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("summary:", output_dir / "summary.json")
    return 0
