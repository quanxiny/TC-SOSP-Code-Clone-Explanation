#!/usr/bin/env python3
"""Evaluate graph-pair explainers on transformed semantic non-clone pairs."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
import torch

from .configlib import config_digest, resolve_workspace_path
from .contrastive_runner import BASELINE_ROOT
from .explanation_runner import jaccard, load_checkpoint_model, predict
from .truth_explanation_runner import (
    attribution_share,
    bootstrap_ci,
    fidelity,
    scores_and_selection,
)

if str(BASELINE_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(BASELINE_ROOT))

from reproduce_gcj_batched import load_graphs, set_seed  # noqa: E402


def mapping(value: Sequence[Sequence[int]]) -> Dict[int, int]:
    return {int(left): int(right) for left, right in value}


def mapped_selection(selected: Set[int], correspondence: Dict[int, int]) -> Set[int]:
    return {
        correspondence[index] for index in selected if index in correspondence
    }


def relation_set(payload: Optional[Dict[str, Any]]) -> Optional[Set[Tuple[int, int]]]:
    if payload is None:
        return None
    return {
        (int(row["left_node"]), int(row["right_node"]))
        for row in payload.get("relations", [])
    }


def relation_stability(
        before: Optional[Dict[str, Any]], after: Optional[Dict[str, Any]],
        left_mapping: Dict[int, int], right_mapping: Dict[int, int]
        ) -> Optional[float]:
    before_relations, after_relations = relation_set(before), relation_set(after)
    if before_relations is None or after_relations is None:
        return None
    mapped = {
        (left_mapping[left], right_mapping[right])
        for left, right in before_relations
        if left in left_mapping and right in right_mapping
    }
    return jaccard(mapped, after_relations)


def variant_explanation(
        config: Dict[str, Any], method: str, model: torch.nn.Module,
        graphs: Dict[str, Any], filenames: Sequence[str], target: int
        ) -> Dict[str, Any]:
    left_name, right_name = filenames
    left, right = graphs[left_name], graphs[right_name]
    left_scores, right_scores, left_selected, right_selected, payload = (
        scores_and_selection(
            config, method, model, left_name, right_name, left, right, target
        )
    )
    with torch.no_grad():
        output = predict(model, left, right, True)
    return {
        "prediction": int(output.argmax()),
        "nonclone_probability": float(output[0]),
        "left_selected": left_selected,
        "right_selected": right_selected,
        "left_scores": left_scores,
        "right_scores": right_scores,
        "payload": payload,
        "fidelity": fidelity(
            model, left, right, target, left_selected, right_selected
        ),
    }


def public_variant(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "prediction": row["prediction"],
        "nonclone_probability": row["nonclone_probability"],
        "left_selected": sorted(row["left_selected"]),
        "right_selected": sorted(row["right_selected"]),
        **row["fidelity"],
    }


def evaluate(
        config: Dict[str, Any], method: str, model: torch.nn.Module,
        graphs: Dict[str, Any], truth: Dict[str, Any], device: torch.device
        ) -> Dict[str, Any]:
    torch.cuda.synchronize(device)
    started = time.perf_counter()
    base_files, alpha_files, dead_files = (
        truth["base_files"], truth["alpha_files"], truth["dead_files"]
    )
    with torch.no_grad():
        base_output = predict(
            model, graphs[base_files[0]], graphs[base_files[1]], True
        )
    target = int(base_output.argmax())
    base = variant_explanation(config, method, model, graphs, base_files, target)
    alpha = variant_explanation(config, method, model, graphs, alpha_files, target)
    dead = variant_explanation(config, method, model, graphs, dead_files, target)
    base_alpha = [mapping(value) for value in truth["base_to_alpha_mapping"]]
    alpha_dead = [mapping(value) for value in truth["alpha_to_dead_mapping"]]
    base_alpha_jaccards = [
        jaccard(
            mapped_selection(base[side + "_selected"], base_alpha[index]),
            alpha[side + "_selected"],
        ) for index, side in enumerate(("left", "right"))
    ]
    alpha_dead_jaccards = [
        jaccard(
            mapped_selection(alpha[side + "_selected"], alpha_dead[index]),
            dead[side + "_selected"],
        ) for index, side in enumerate(("left", "right"))
    ]
    distractors = [
        {int(value) for value in side}
        for side in truth["dead_known_irrelevant_nodes"]
    ]
    selected_distractors = [
        dead[side + "_selected"] & distractors[index]
        for index, side in enumerate(("left", "right"))
    ]
    total_distractors = sum(len(value) for value in distractors)
    fidelity_rows = [base["fidelity"], alpha["fidelity"], dead["fidelity"]]
    torch.cuda.synchronize(device)
    return {
        "pair_id": truth["pair_id"],
        "method": method,
        "target": target,
        "base_prediction_correct": base["prediction"] == 0,
        "prediction_invariant": (
            base["prediction"] == alpha["prediction"] == dead["prediction"]
        ),
        "base_to_alpha_selected_correspondence_jaccard": float(np.mean(
            base_alpha_jaccards
        )),
        "alpha_to_dead_selected_correspondence_jaccard": float(np.mean(
            alpha_dead_jaccards
        )),
        "dead_known_irrelevant_node_selection_recall": (
            sum(len(value) for value in selected_distractors) / total_distractors
        ),
        "dead_known_irrelevant_attribution_share": float(np.mean([
            attribution_share(dead[side + "_scores"], distractors[index])
            for index, side in enumerate(("left", "right"))
        ])),
        "base_to_alpha_relation_jaccard": relation_stability(
            base["payload"], alpha["payload"], base_alpha[0], base_alpha[1]
        ),
        "alpha_to_dead_relation_jaccard": relation_stability(
            alpha["payload"], dead["payload"], alpha_dead[0], alpha_dead[1]
        ),
        "mean_necessity_drop": float(np.mean([
            row["necessity_drop"] for row in fidelity_rows
        ])),
        "mean_absolute_sufficiency_gap": float(np.mean([
            row["absolute_sufficiency_gap"] for row in fidelity_rows
        ])),
        "base": public_variant(base),
        "alpha": public_variant(alpha),
        "dead": {
            **public_variant(dead),
            "known_irrelevant_nodes": [sorted(value) for value in distractors],
            "selected_known_irrelevant_nodes": [
                sorted(value) for value in selected_distractors
            ],
        },
        "seconds": time.perf_counter() - started,
    }


def metric(values: Sequence[float], seed: int, resamples: int) -> Dict[str, Any]:
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "bootstrap_95_ci": bootstrap_ci(values, seed, resamples),
        "values": [float(value) for value in values],
    }


def aggregate(records: Sequence[Dict[str, Any]], seed: int,
              resamples: int) -> Dict[str, Any]:
    names = (
        "base_to_alpha_selected_correspondence_jaccard",
        "alpha_to_dead_selected_correspondence_jaccard",
        "dead_known_irrelevant_node_selection_recall",
        "dead_known_irrelevant_attribution_share",
        "mean_necessity_drop",
        "mean_absolute_sufficiency_gap",
        "seconds",
    )
    output = {
        name: metric(
            [row[name] for row in records], seed + index * 1013, resamples
        ) for index, name in enumerate(names)
    }
    for index, name in enumerate((
        "base_to_alpha_relation_jaccard", "alpha_to_dead_relation_jaccard"
    )):
        values = [row[name] for row in records if row[name] is not None]
        output[name] = (
            metric(values, seed + 20000 + index * 1013, resamples)
            if values else None
        )
    output.update({
        "pairs": len(records),
        "base_prediction_accuracy": float(np.mean([
            row["base_prediction_correct"] for row in records
        ])),
        "prediction_invariance_rate": float(np.mean([
            row["prediction_invariant"] for row in records
        ])),
    })
    return output


def paired(
        baseline: Sequence[Dict[str, Any]], candidate: Sequence[Dict[str, Any]],
        seed: int, resamples: int) -> Dict[str, Any]:
    baseline_by_id = {row["pair_id"]: row for row in baseline}
    candidate_by_id = {row["pair_id"]: row for row in candidate}
    axes = {
        "base_to_alpha_correspondence_delta": (
            "base_to_alpha_selected_correspondence_jaccard", 1.0
        ),
        "alpha_to_dead_correspondence_delta": (
            "alpha_to_dead_selected_correspondence_jaccard", 1.0
        ),
        "dead_irrelevant_selection_reduction": (
            "dead_known_irrelevant_node_selection_recall", -1.0
        ),
        "dead_irrelevant_attribution_reduction": (
            "dead_known_irrelevant_attribution_share", -1.0
        ),
        "mean_necessity_delta": ("mean_necessity_drop", 1.0),
        "mean_absolute_sufficiency_gap_reduction": (
            "mean_absolute_sufficiency_gap", -1.0
        ),
    }
    output = {"positive_means_candidate_is_better": list(axes)}
    for index, (name, (source, direction)) in enumerate(axes.items()):
        values = [
            direction * (
                candidate_by_id[pair_id][source] - baseline_by_id[pair_id][source]
            ) for pair_id in sorted(candidate_by_id)
        ]
        output[name] = metric(values, seed + index * 1013, resamples)
    return output


def run(config: Dict[str, Any]) -> int:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the reproduced encoder")
    output_dir = resolve_workspace_path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = config_digest(config)
    resolved = output_dir / "resolved_config.json"
    if resolved.is_file():
        previous = json.loads(resolved.read_text(encoding="utf-8"))
        if previous["config_sha256"] != digest:
            raise RuntimeError("refusing resume with a different negative-truth config")
    else:
        resolved.write_text(json.dumps({
            "config_sha256": digest, "config": config,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    seed = int(config["seed"])
    set_seed(seed)
    device = torch.device(config["device"])
    truth_path = resolve_workspace_path(config["truth"]["manifest"])
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    required = sorted({
        filename for row in truth["records"]
        for field in ("base_files", "alpha_files", "dead_files")
        for filename in row[field]
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
    records: Dict[str, List[Dict[str, Any]]] = {method: [] for method in methods}
    completed: Dict[str, Set[str]] = {method: set() for method in methods}
    for method in methods:
        path = output_dir / (method + "_negative_truth_records.jsonl")
        if config.get("resume") and path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                records[method].append(row)
                completed[method].add(row["pair_id"])
        elif path.exists():
            path.unlink()
    for index, truth_row in enumerate(truth["records"]):
        for method in methods:
            if truth_row["pair_id"] in completed[method]:
                continue
            row = evaluate(config, method, model, graphs, truth_row, device)
            records[method].append(row)
            with (output_dir / (method + "_negative_truth_records.jsonl")).open(
                    "a", encoding="utf-8") as output:
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
        print("negative truth pair {}/{}".format(index + 1, len(truth["records"])))

    resamples = int(config["explanation"]["bootstrap_resamples"])
    candidate = "symmetric_semantic_optimal_pair"
    comparisons = {}
    if candidate in records:
        for index, baseline in enumerate(methods):
            if baseline == candidate:
                continue
            comparisons[candidate + "_minus_" + baseline] = paired(
                records[baseline], records[candidate],
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
        "pairs": len(truth["records"]),
        "methods": {
            method: aggregate(rows, seed + index * 100003, resamples)
            for index, (method, rows) in enumerate(records.items())
        },
        "paired_comparisons": comparisons,
        "test_metrics": None,
        "test_policy": "validation_derived_negative_transformations_only",
        "limitations": [
            "metamorphic truth validates transformation stability and distractor rejection, not a unique human rationale",
            "each source program belongs to exactly one different-problem negative pair",
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
