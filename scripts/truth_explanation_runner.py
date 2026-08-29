#!/usr/bin/env python3
"""Evaluate pair explainers against transformation-derived CFG-node truth."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

import numpy as np
import torch

from .configlib import config_digest, resolve_workspace_path
from .contrastive_runner import BASELINE_ROOT, runner_args
from .explanation_runner import (
    OPTIMAL_PAIR_METHODS,
    apply_node_mask,
    explain,
    jaccard,
    load_checkpoint_model,
    optimize_semantic_subgraph_pair,
    predict,
    top_nodes,
)

if str(BASELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(BASELINE_ROOT))

from reproduce_gcj_batched import load_graphs, set_seed  # noqa: E402


def bootstrap_ci(values: Sequence[float], seed: int,
                 resamples: int) -> List[float]:
    array = np.asarray(values, dtype=float)
    generator = np.random.default_rng(seed)
    sampled = generator.integers(0, len(array), size=(resamples, len(array)))
    means = array[sampled].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def metric(values: Sequence[float], seed: int, resamples: int) -> Dict[str, Any]:
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "bootstrap_95_ci": bootstrap_ci(values, seed, resamples),
        "values": [float(value) for value in values],
    }


def scores_and_selection(
        config: Dict[str, Any], method: str, model: torch.nn.Module,
        left_name: str, right_name: str, left: Any, right: Any,
        target: int) -> Tuple[torch.Tensor, torch.Tensor, Set[int], Set[int], Any]:
    explanation = config["explanation"]
    fraction = float(explanation["top_node_fraction"])
    payload = None
    if method in OPTIMAL_PAIR_METHODS:
        payload = optimize_semantic_subgraph_pair(
            model, left_name, right_name, left, right, target, fraction,
            OPTIMAL_PAIR_METHODS[method],
            float(explanation.get("optimal_sufficiency_weight", 1.0)),
            float(explanation.get("optimal_semantic_coefficient", 0.0)),
            float(explanation.get("optimal_structure_coefficient", 0.0)),
        )
        return (
            payload["left_scores"], payload["right_scores"],
            payload["left_selected"], payload["right_selected"], payload,
        )
    left_scores, right_scores = explain(
        method, model, "{} {} 1".format(left_name, right_name),
        left_name, right_name, left, right, target,
        int(explanation["integrated_gradients_steps"]),
        int(explanation["mask_optimization_steps"]),
        float(explanation["mask_learning_rate"]),
        float(explanation["mask_sparsity_lambda"]),
        fraction,
        float(explanation.get("gnnexplainer_entropy_coefficient", 0.1)),
        int(explanation.get("subgraphx_mcts_iterations", 48)),
        int(explanation.get("subgraphx_shapley_samples", 4)),
    )
    return (
        left_scores, right_scores,
        top_nodes(left_scores, fraction), top_nodes(right_scores, fraction), None,
    )


def fidelity(model: torch.nn.Module, left: Any, right: Any, target: int,
             left_selected: Set[int], right_selected: Set[int]) -> Dict[str, float]:
    with torch.no_grad():
        base = float(predict(model, left, right, True)[target])
        keep = float(predict(
            model,
            apply_node_mask(left, left_selected, True),
            apply_node_mask(right, right_selected, True), True,
        )[target])
        remove = float(predict(
            model,
            apply_node_mask(left, left_selected, False),
            apply_node_mask(right, right_selected, False), True,
        )[target])
    return {
        "base_target_probability": base,
        "keep_target_probability": keep,
        "remove_target_probability": remove,
        "necessity_drop": base - remove,
        "absolute_sufficiency_gap": abs(base - keep),
    }


def attribution_share(scores: torch.Tensor, selected: Set[int]) -> float:
    values = scores.detach().float().abs().cpu()
    denominator = float(values.sum())
    if denominator <= 0:
        return 0.0
    return float(values[list(selected)].sum()) / denominator


def evaluate_method_sample(config: Dict[str, Any], method: str,
                           model: torch.nn.Module, graphs: Dict[str, Any],
                           truth: Dict[str, Any], device: torch.device
                           ) -> Dict[str, Any]:
    files = truth["files"]
    original = graphs[files["original"]]
    alpha = graphs[files["alpha"]]
    alpha_dead = graphs[files["alpha_dead"]]
    torch.cuda.synchronize(device)
    started = time.perf_counter()

    with torch.no_grad():
        alpha_output = predict(model, original, alpha, True)
    alpha_target = int(alpha_output.argmax())
    (original_scores, alpha_scores, original_selected, alpha_selected,
     alpha_payload) = scores_and_selection(
        config, method, model, files["original"], files["alpha"],
        original, alpha, alpha_target,
    )
    alpha_fidelity = fidelity(
        model, original, alpha, alpha_target, original_selected, alpha_selected
    )
    alpha_relation_precision = None
    if alpha_payload is not None and alpha_payload["relations"]:
        alpha_relation_precision = float(np.mean([
            relation["left_node"] == relation["right_node"]
            for relation in alpha_payload["relations"]
        ]))

    with torch.no_grad():
        dead_output = predict(model, alpha, alpha_dead, True)
    dead_target = int(dead_output.argmax())
    (dead_left_scores, dead_right_scores, dead_left_selected,
     dead_right_selected, dead_payload) = scores_and_selection(
        config, method, model, files["alpha"], files["alpha_dead"],
        alpha, alpha_dead, dead_target,
    )
    dead_fidelity = fidelity(
        model, alpha, alpha_dead, dead_target,
        dead_left_selected, dead_right_selected,
    )
    correspondence = {
        int(left_index): int(right_index)
        for left_index, right_index in truth["alpha_to_alpha_dead_node_mapping"]
    }
    mapped_left = {
        correspondence[index] for index in dead_left_selected if index in correspondence
    }
    distractors = set(truth["alpha_dead_known_irrelevant_nodes"])
    selected_distractors = dead_right_selected & distractors
    dead_relation_precision = None
    if dead_payload is not None and dead_payload["relations"]:
        dead_relation_precision = float(np.mean([
            correspondence.get(relation["left_node"]) == relation["right_node"]
            for relation in dead_payload["relations"]
        ]))
    torch.cuda.synchronize(device)
    return {
        "sample_id": truth["sample_id"],
        "method": method,
        "alpha_pair": {
            "prediction": alpha_target,
            "clone_probability": float(alpha_output[1]),
            "selected_correspondence_jaccard": jaccard(
                original_selected, alpha_selected
            ),
            "relation_correspondence_precision": alpha_relation_precision,
            "left_selected": sorted(original_selected),
            "right_selected": sorted(alpha_selected),
            **alpha_fidelity,
        },
        "dead_pair": {
            "prediction": dead_target,
            "clone_probability": float(dead_output[1]),
            "selected_correspondence_jaccard": jaccard(
                mapped_left, dead_right_selected
            ),
            "relation_correspondence_precision": dead_relation_precision,
            "known_irrelevant_nodes": sorted(distractors),
            "selected_known_irrelevant_nodes": sorted(selected_distractors),
            "known_irrelevant_node_selection_recall": (
                len(selected_distractors) / len(distractors)
            ),
            "known_irrelevant_node_selection_precision": (
                len(selected_distractors) / len(dead_right_selected)
                if dead_right_selected else 0.0
            ),
            "known_irrelevant_attribution_share": attribution_share(
                dead_right_scores, distractors
            ),
            "left_selected": sorted(dead_left_selected),
            "right_selected": sorted(dead_right_selected),
            **dead_fidelity,
        },
        "seconds": time.perf_counter() - started,
    }


def aggregate_method(records: Sequence[Dict[str, Any]], seed: int,
                     resamples: int) -> Dict[str, Any]:
    paths = {
        "alpha_selected_correspondence_jaccard": (
            "alpha_pair", "selected_correspondence_jaccard"
        ),
        "dead_selected_correspondence_jaccard": (
            "dead_pair", "selected_correspondence_jaccard"
        ),
        "dead_known_irrelevant_node_selection_recall": (
            "dead_pair", "known_irrelevant_node_selection_recall"
        ),
        "dead_known_irrelevant_node_selection_precision": (
            "dead_pair", "known_irrelevant_node_selection_precision"
        ),
        "dead_known_irrelevant_attribution_share": (
            "dead_pair", "known_irrelevant_attribution_share"
        ),
        "alpha_necessity_drop": ("alpha_pair", "necessity_drop"),
        "dead_necessity_drop": ("dead_pair", "necessity_drop"),
        "alpha_absolute_sufficiency_gap": (
            "alpha_pair", "absolute_sufficiency_gap"
        ),
        "dead_absolute_sufficiency_gap": (
            "dead_pair", "absolute_sufficiency_gap"
        ),
    }
    result = {
        name: metric(
            [float(record[section][field]) for record in records],
            seed + index * 1009, resamples,
        )
        for index, (name, (section, field)) in enumerate(paths.items())
    }
    for name, section in (
        ("alpha_relation_correspondence_precision", "alpha_pair"),
        ("dead_relation_correspondence_precision", "dead_pair"),
    ):
        values = [
            record[section]["relation_correspondence_precision"]
            for record in records
            if record[section]["relation_correspondence_precision"] is not None
        ]
        result[name] = metric(values, seed + 20000, resamples) if values else None
    result.update({
        "samples": len(records),
        "alpha_clone_prediction_rate": float(np.mean([
            record["alpha_pair"]["prediction"] == 1 for record in records
        ])),
        "dead_clone_prediction_rate": float(np.mean([
            record["dead_pair"]["prediction"] == 1 for record in records
        ])),
        "seconds": metric(
            [record["seconds"] for record in records], seed + 30000, resamples
        ),
    })
    return result


def paired_comparison(baseline: Sequence[Dict[str, Any]],
                      candidate: Sequence[Dict[str, Any]], seed: int,
                      resamples: int) -> Dict[str, Any]:
    baseline_by_id = {record["sample_id"]: record for record in baseline}
    candidate_by_id = {record["sample_id"]: record for record in candidate}
    axes = {
        "alpha_correspondence_delta": (
            lambda row: row["alpha_pair"]["selected_correspondence_jaccard"], 1.0
        ),
        "dead_correspondence_delta": (
            lambda row: row["dead_pair"]["selected_correspondence_jaccard"], 1.0
        ),
        "dead_irrelevant_selection_reduction": (
            lambda row: row["dead_pair"]["known_irrelevant_node_selection_recall"], -1.0
        ),
        "dead_irrelevant_attribution_reduction": (
            lambda row: row["dead_pair"]["known_irrelevant_attribution_share"], -1.0
        ),
        "mean_necessity_delta": (
            lambda row: 0.5 * (
                row["alpha_pair"]["necessity_drop"]
                + row["dead_pair"]["necessity_drop"]
            ), 1.0
        ),
        "mean_absolute_sufficiency_gap_reduction": (
            lambda row: 0.5 * (
                row["alpha_pair"]["absolute_sufficiency_gap"]
                + row["dead_pair"]["absolute_sufficiency_gap"]
            ), -1.0
        ),
    }
    result = {"positive_means_candidate_is_better": list(axes)}
    for index, (name, (extract, direction)) in enumerate(axes.items()):
        values = [
            direction * (
                extract(candidate_by_id[sample_id])
                - extract(baseline_by_id[sample_id])
            )
            for sample_id in sorted(candidate_by_id)
        ]
        result[name] = metric(values, seed + index * 1013, resamples)
    return result


def run(config: Dict[str, Any]) -> int:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the reproduced encoder")
    output_dir = resolve_workspace_path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = config_digest(config)
    resolved_path = output_dir / "resolved_config.json"
    if resolved_path.is_file():
        previous = json.loads(resolved_path.read_text(encoding="utf-8"))
        if previous["config_sha256"] != digest:
            raise RuntimeError("refusing resume with a different truth config")
    else:
        resolved_path.write_text(json.dumps({
            "config_sha256": digest, "config": config,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    seed = int(config["seed"])
    set_seed(seed)
    device = torch.device(config["device"])
    truth_path = resolve_workspace_path(config["truth"]["manifest"])
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    required = sorted({
        filename for record in truth["records"] for filename in record["files"].values()
    })
    previous_directory = Path.cwd()
    try:
        os.chdir(str(BASELINE_ROOT))
        graphs = load_graphs(
            required,
            resolve_workspace_path(config["paths"]["source_dir"]),
            resolve_workspace_path(config["paths"]["vector_dir"]),
            device, int(config["model"]["hidden"]),
        )
    finally:
        os.chdir(str(previous_directory))
    model = load_checkpoint_model(config, device)

    methods = list(config["baselines"])
    method_records: Dict[str, List[Dict[str, Any]]] = {method: [] for method in methods}
    completed: Dict[str, Set[str]] = {method: set() for method in methods}
    for method in methods:
        path = output_dir / (method + "_truth_records.jsonl")
        if config.get("resume") and path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                record = json.loads(line)
                method_records[method].append(record)
                completed[method].add(record["sample_id"])
        elif path.exists():
            path.unlink()

    for index, truth_record in enumerate(truth["records"]):
        for method in methods:
            if truth_record["sample_id"] in completed[method]:
                continue
            record = evaluate_method_sample(
                config, method, model, graphs, truth_record, device
            )
            method_records[method].append(record)
            with (output_dir / (method + "_truth_records.jsonl")).open(
                    "a", encoding="utf-8") as output:
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
        print("truth sample {}/{}".format(index + 1, len(truth["records"])))

    resamples = int(config["explanation"]["bootstrap_resamples"])
    candidate_name = "symmetric_semantic_optimal_pair"
    comparisons = {}
    if candidate_name in method_records:
        for index, baseline in enumerate(methods):
            if baseline == candidate_name:
                continue
            comparisons[candidate_name + "_minus_" + baseline] = paired_comparison(
                method_records[baseline], method_records[candidate_name],
                seed + 500000 + index * 100003, resamples,
            )
    checkpoint = resolve_workspace_path(config["predictor"]["checkpoint"])
    summary = {
        "config_sha256": digest,
        "configuration": config,
        "truth_manifest": str(truth_path),
        "truth_manifest_sha256": hashlib.sha256(truth_path.read_bytes()).hexdigest(),
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        "samples": len(truth["records"]),
        "methods": {
            method: aggregate_method(records, seed + index * 100003, resamples)
            for index, (method, records) in enumerate(method_records.items())
        },
        "paired_comparisons": comparisons,
        "metric_direction": {
            "selected_correspondence_jaccard": "higher_is_better",
            "relation_correspondence_precision": "higher_is_better",
            "known_irrelevant_node_selection_recall": "lower_is_better",
            "known_irrelevant_attribution_share": "lower_is_better",
            "necessity_drop": "higher_is_better",
            "absolute_sufficiency_gap": "lower_is_better",
        },
        "test_metrics": None,
        "test_policy": "validation_derived_transformations_only",
        "limitations": [
            "transformation truth validates correspondence and distractor rejection, not a unique complete human rationale",
            "node-feature interventions retain the original CFG topology",
            "SubgraphX and GNNExplainer are explicitly adapted to a dual-graph classifier",
        ],
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("summary:", summary_path)
    return 0
