#!/usr/bin/env python3
"""Add corrected paired tests and label subgroups to the C9 natural study."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.aggregate_explanation_truth_statistics import holm, paired_test  # noqa: E402
from scripts.explanation_runner import (  # noqa: E402
    bootstrap_mean_ci,
    cluster_bootstrap_mean_ci,
)


RESULTS = (
    ROOT / "artifacts" / "pilots"
    / "C9_natural_validation_strong_baselines_seed42"
)
OUTPUT = (
    ROOT / "artifacts" / "comparisons"
    / "C9_natural_strong_baseline_paired_statistics_validation.json"
)
CANDIDATE = "symmetric_semantic_optimal_pair"
BASELINES = (
    "symmetric_grad_x_input",
    "symmetric_gnnexplainer_node_mask_adapted",
    "symmetric_subgraphx_mcts_shapley_adapted",
)


def load(method: str) -> tuple[List[Dict[str, Any]], Path]:
    path = RESULTS / (method + "_records.jsonl")
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 100:
        raise RuntimeError("{} is incomplete: {} rows".format(path, len(rows)))
    return rows, path


def descriptive(records: List[Dict[str, Any]], metric: str, seed: int) -> Dict[str, Any]:
    values = [float(row[metric]) for row in records]
    return {
        "n": len(values),
        "mean": float(np.mean(values)),
        "bootstrap_95_ci": bootstrap_mean_ci(values, 10000, seed),
        "problem_pair_cluster_bootstrap_95_ci": cluster_bootstrap_mean_ci(
            records, metric, 10000, seed + 17
        ),
    }


def main() -> int:
    candidate, candidate_path = load(CANDIDATE)
    candidate_by_id = {int(row["pair_index"]): row for row in candidate}
    evidence = {
        CANDIDATE: {
            "path": str(candidate_path.resolve()),
            "sha256": hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
        }
    }
    comparisons = {}
    raw_p = {}
    for baseline_index, baseline_name in enumerate(BASELINES):
        baseline, baseline_path = load(baseline_name)
        evidence[baseline_name] = {
            "path": str(baseline_path.resolve()),
            "sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
        }
        baseline_by_id = {int(row["pair_index"]): row for row in baseline}
        if set(candidate_by_id) != set(baseline_by_id):
            raise RuntimeError("methods do not cover identical natural pairs")
        deltas = []
        for pair_index in sorted(candidate_by_id):
            first, second = baseline_by_id[pair_index], candidate_by_id[pair_index]
            deltas.append({
                "pair_index": pair_index,
                "problem_pair_cluster": second["problem_pair_cluster"],
                "label": second["label"],
                "necessity_delta": second["necessity_drop"] - first["necessity_drop"],
                "absolute_sufficiency_gap_reduction": (
                    abs(first["sufficiency_gap"]) - abs(second["sufficiency_gap"])
                ),
                "swap_jaccard_delta": second["swap_jaccard"] - first["swap_jaccard"],
            })
        metrics = {}
        for metric_index, metric in enumerate((
            "necessity_delta", "absolute_sufficiency_gap_reduction",
            "swap_jaccard_delta",
        )):
            values = [row[metric] for row in deltas]
            test = paired_test(values)
            test["descriptive"] = descriptive(
                deltas, metric,
                890000 + baseline_index * 100003 + metric_index * 1013,
            )
            metrics[metric] = test
            raw_p[baseline_name + "/" + metric] = test["wilcoxon_two_sided_p_raw"]
        by_label = {
            str(label): {
                metric: descriptive(
                    [row for row in deltas if row["label"] == label], metric,
                    900000 + baseline_index * 100003 + label * 10000
                    + metric_index * 1013,
                )
                for metric_index, metric in enumerate((
                    "necessity_delta", "absolute_sufficiency_gap_reduction",
                    "swap_jaccard_delta",
                ))
            } for label in (0, 1)
        }
        comparisons[baseline_name] = {
            "positive_means_tc_sosp_is_better": True,
            "overall": metrics,
            "by_true_label": by_label,
        }
    adjusted = holm(raw_p)
    for key, value in adjusted.items():
        baseline_name, metric = key.split("/", 1)
        comparisons[baseline_name]["overall"][metric][
            "wilcoxon_two_sided_p_holm_9_endpoints"
        ] = value
    candidate_by_label = {
        str(label): dict(sorted(Counter(
            row.get("selected_candidate", "not_applicable")
            for row in candidate if row["label"] == label
        ).items())) for label in (0, 1)
    }
    result = {
        "scope": "100 balanced GCJ natural validation pairs",
        "candidate": CANDIDATE,
        "comparisons": comparisons,
        "candidate_selected_family_by_label": candidate_by_label,
        "evidence": evidence,
        "inference": (
            "problem-pair cluster bootstrap for means; two-sided paired "
            "Wilcoxon tests with Holm correction across 3 baselines x 3 endpoints"
        ),
        "test_metrics": None,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(OUTPUT), "tests": len(raw_p)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
