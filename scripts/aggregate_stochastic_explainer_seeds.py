#!/usr/bin/env python3
"""Aggregate C9/C16--C18 without treating explainer seeds as new samples."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.aggregate_explanation_truth_statistics import holm, paired_test  # noqa: E402
from scripts.explanation_runner import (  # noqa: E402
    bootstrap_mean_ci,
    cluster_bootstrap_mean_ci,
)


CANDIDATE = "symmetric_semantic_optimal_pair"
GNN = "symmetric_gnnexplainer_node_mask_adapted"
SUBGRAPHX = "symmetric_subgraphx_mcts_shapley_adapted"
SEEDS = (42, 123, 2024)
C9 = ROOT / "artifacts" / "pilots" / "C9_natural_validation_strong_baselines_seed42"
RUNS = {
    GNN: {
        42: ROOT / "artifacts" / "pilots" / "C16_gnnexplainer_random_init_seed42_reference",
        123: ROOT / "artifacts" / "pilots" / "C17_stochastic_explainers_seed123",
        2024: ROOT / "artifacts" / "pilots" / "C18_stochastic_explainers_seed2024",
    },
    SUBGRAPHX: {
        42: C9,
        123: ROOT / "artifacts" / "pilots" / "C17_stochastic_explainers_seed123",
        2024: ROOT / "artifacts" / "pilots" / "C18_stochastic_explainers_seed2024",
    },
}
OUTPUT = (
    ROOT / "artifacts" / "comparisons"
    / "C16_C18_stochastic_explainer_seed_robustness_validation.json"
)
CORE_METRICS = (
    "necessity_drop", "absolute_sufficiency_gap", "swap_jaccard", "seconds",
)
DELTA_METRICS = (
    "necessity_delta", "absolute_sufficiency_gap_reduction",
    "swap_jaccard_delta",
)


def load_records(directory: Path, method: str) -> tuple[List[Dict[str, Any]], Path]:
    path = directory / (method + "_records.jsonl")
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 100 or len({int(row["pair_index"]) for row in rows}) != 100:
        raise RuntimeError("{} must contain 100 unique pairs".format(path))
    return sorted(rows, key=lambda row: int(row["pair_index"])), path


def evidence(path: Path) -> Dict[str, str]:
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def mean_metrics(rows: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    return {
        metric: float(np.mean([float(row[metric]) for row in rows]))
        for metric in CORE_METRICS
    }


def validate_pairing(reference: Sequence[Dict[str, Any]],
                     candidate: Sequence[Dict[str, Any]]) -> float:
    keys = (
        "pair_index", "left", "right", "label", "prediction",
        "problem_pair_cluster",
    )
    maximum_probability_drift = 0.0
    for first, second in zip(reference, candidate):
        if any(first[key] != second[key] for key in keys):
            raise RuntimeError("pair provenance differs at {}".format(first["pair_index"]))
        drift = abs(
            float(first["base_target_probability"])
            - float(second["base_target_probability"])
        )
        maximum_probability_drift = max(maximum_probability_drift, drift)
        if drift > 2e-5:
            raise RuntimeError("base prediction differs at {}".format(first["pair_index"]))
    return maximum_probability_drift


def descriptive(records: List[Dict[str, Any]], metric: str,
                seed: int) -> Dict[str, Any]:
    values = [float(row[metric]) for row in records]
    return {
        "n": len(values),
        "mean": float(np.mean(values)),
        "bootstrap_95_ci": bootstrap_mean_ci(values, 10000, seed),
        "problem_pair_cluster_bootstrap_95_ci": cluster_bootstrap_mean_ci(
            records, metric, 10000, seed + 17
        ),
    }


def jaccard(first: Sequence[int], second: Sequence[int]) -> float:
    left, right = set(first), set(second)
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def stability(rows_by_seed: Dict[int, List[Dict[str, Any]]],
              method_index: int) -> Dict[str, Any]:
    records = []
    exact = 0
    for pair_index in range(100):
        rows = [rows_by_seed[seed][pair_index] for seed in SEEDS]
        pairwise = []
        for first_index, second_index in itertools.combinations(range(3), 2):
            pairwise.append(0.5 * (
                jaccard(
                    rows[first_index]["left_selected"],
                    rows[second_index]["left_selected"],
                )
                + jaccard(
                    rows[first_index]["right_selected"],
                    rows[second_index]["right_selected"],
                )
            ))
        is_exact = all(
            rows[0]["left_selected"] == row["left_selected"]
            and rows[0]["right_selected"] == row["right_selected"]
            for row in rows[1:]
        )
        exact += int(is_exact)
        records.append({
            "pair_index": pair_index,
            "problem_pair_cluster": rows[0]["problem_pair_cluster"],
            "label": rows[0]["label"],
            "mean_pairwise_selection_jaccard": float(np.mean(pairwise)),
        })
    return {
        "exact_three_seed_selection_agreement_pairs": exact,
        "changed_selection_pairs": 100 - exact,
        "mean_pairwise_selection_jaccard": descriptive(
            records, "mean_pairwise_selection_jaccard",
            970000 + method_index * 100003,
        ),
    }


def main() -> int:
    candidate, candidate_path = load_records(C9, CANDIDATE)
    all_rows: Dict[str, Dict[int, List[Dict[str, Any]]]] = {}
    evidence_rows: Dict[str, Any] = {"candidate": evidence(candidate_path)}
    for method in (GNN, SUBGRAPHX):
        all_rows[method] = {}
        evidence_rows[method] = {}
        for seed in SEEDS:
            rows, path = load_records(RUNS[method][seed], method)
            maximum_probability_drift = validate_pairing(candidate, rows)
            record_seeds = {row.get("explainer_seed", 42) for row in rows}
            if record_seeds != {seed}:
                raise RuntimeError(
                    "{} seed metadata {} != {}".format(path, record_seeds, seed)
                )
            all_rows[method][seed] = rows
            evidence_rows[method][str(seed)] = {
                **evidence(path),
                "maximum_absolute_base_probability_drift_vs_c9": (
                    maximum_probability_drift
                ),
                "prediction_and_target_exactly_equal": True,
            }

    methods = {}
    comparisons = {}
    raw_p: Dict[str, float] = {}
    for method_index, method in enumerate((GNN, SUBGRAPHX)):
        rows_by_seed = all_rows[method]
        seed_means = {
            str(seed): mean_metrics(rows_by_seed[seed]) for seed in SEEDS
        }
        seed_average_rows = []
        seed_comparisons = {}
        for pair_index, candidate_row in enumerate(candidate):
            seed_rows = [rows_by_seed[seed][pair_index] for seed in SEEDS]
            seed_average_rows.append({
                "pair_index": pair_index,
                "problem_pair_cluster": candidate_row["problem_pair_cluster"],
                "label": candidate_row["label"],
                **{
                    metric: float(np.mean([
                        float(row[metric]) for row in seed_rows
                    ])) for metric in CORE_METRICS
                },
            })
        for seed_index, seed in enumerate(SEEDS):
            deltas = []
            for candidate_row, baseline_row in zip(candidate, rows_by_seed[seed]):
                deltas.append({
                    "pair_index": int(candidate_row["pair_index"]),
                    "problem_pair_cluster": candidate_row["problem_pair_cluster"],
                    "label": candidate_row["label"],
                    "necessity_delta": (
                        float(candidate_row["necessity_drop"])
                        - float(baseline_row["necessity_drop"])
                    ),
                    "absolute_sufficiency_gap_reduction": (
                        float(baseline_row["absolute_sufficiency_gap"])
                        - float(candidate_row["absolute_sufficiency_gap"])
                    ),
                    "swap_jaccard_delta": (
                        float(candidate_row["swap_jaccard"])
                        - float(baseline_row["swap_jaccard"])
                    ),
                })
            seed_comparisons[str(seed)] = {
                metric: descriptive(
                    deltas, metric,
                    1000000 + method_index * 200003
                    + seed_index * 30011 + metric_index * 1013,
                )
                for metric_index, metric in enumerate(DELTA_METRICS)
            }

        averaged_deltas = []
        for candidate_row, baseline_row in zip(candidate, seed_average_rows):
            averaged_deltas.append({
                "pair_index": int(candidate_row["pair_index"]),
                "problem_pair_cluster": candidate_row["problem_pair_cluster"],
                "label": candidate_row["label"],
                "necessity_delta": (
                    float(candidate_row["necessity_drop"])
                    - float(baseline_row["necessity_drop"])
                ),
                "absolute_sufficiency_gap_reduction": (
                    float(baseline_row["absolute_sufficiency_gap"])
                    - float(candidate_row["absolute_sufficiency_gap"])
                ),
                "swap_jaccard_delta": (
                    float(candidate_row["swap_jaccard"])
                    - float(baseline_row["swap_jaccard"])
                ),
            })
        averaged_tests = {}
        for metric_index, metric in enumerate(DELTA_METRICS):
            values = [float(row[metric]) for row in averaged_deltas]
            test = paired_test(values)
            test["descriptive"] = descriptive(
                averaged_deltas, metric,
                1200000 + method_index * 200003 + metric_index * 1013,
            )
            averaged_tests[metric] = test
            raw_p[method + "/" + metric] = test["wilcoxon_two_sided_p_raw"]

        methods[method] = {
            "seed_means": seed_means,
            "mean_of_seed_means": {
                metric: float(np.mean([
                    seed_means[str(seed)][metric] for seed in SEEDS
                ])) for metric in CORE_METRICS
            },
            "sample_standard_deviation_of_seed_means": {
                metric: float(np.std([
                    seed_means[str(seed)][metric] for seed in SEEDS
                ], ddof=1)) for metric in CORE_METRICS
            },
            "selection_stability": stability(rows_by_seed, method_index),
        }
        comparisons[method] = {
            "positive_means_tc_sosp_is_better": True,
            "by_explainer_seed": seed_comparisons,
            "candidate_vs_per_pair_seed_averaged_baseline": averaged_tests,
            "worst_seed_mean_delta": {
                metric: float(min(
                    seed_comparisons[str(seed)][metric]["mean"] for seed in SEEDS
                )) for metric in DELTA_METRICS
            },
        }

    adjusted = holm(raw_p)
    for key, value in adjusted.items():
        method, metric = key.split("/", 1)
        comparisons[method]["candidate_vs_per_pair_seed_averaged_baseline"][metric][
            "wilcoxon_two_sided_p_holm_6_endpoints"
        ] = value

    zero_init, zero_init_path = load_records(C9, GNN)
    result = {
        "scope": "C9 100 balanced GCJ natural validation pairs",
        "predictor": "one frozen seed-1337 epoch-13 checkpoint",
        "explainer_seeds": list(SEEDS),
        "candidate": {
            "method": CANDIDATE,
            "deterministic_fixed_records": mean_metrics(candidate),
        },
        "methods": methods,
        "comparisons": comparisons,
        "zero_initialized_gnnexplainer_diagnostic_excluded_from_seed_average": {
            "reason": (
                "the original C9 adaptation initialized node-mask logits at zero; "
                "the seed study uses the PyG-style Gaussian 0.1 initialization"
            ),
            "metrics": mean_metrics(zero_init),
            "evidence": evidence(zero_init_path),
        },
        "evidence": evidence_rows,
        "inference": (
            "explainer seeds are repeated measurements, not independent samples; "
            "the primary comparison averages each baseline over seeds within pair, "
            "then uses problem-pair cluster bootstrap and paired Wilcoxon with Holm "
            "correction across 2 baselines x 3 endpoints"
        ),
        "test_metrics": None,
        "test_policy": "validation only; sealed test not read",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(OUTPUT), "methods": list(methods), "tests": len(raw_p),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
