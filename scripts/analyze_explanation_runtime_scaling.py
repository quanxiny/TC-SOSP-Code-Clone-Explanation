#!/usr/bin/env python3
"""Summarize explainer wall time across graph-pair size quartiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = (
    ROOT / "artifacts" / "pilots"
    / "C9_natural_validation_strong_baselines_seed42"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "artifacts" / "comparisons"
        / "C9_explanation_runtime_scaling_validation.json",
    )
    return parser.parse_args()


def load(path: Path) -> List[Dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def method_summary(rows: List[Dict[str, Any]], bins: Dict[int, int]) -> Dict[str, Any]:
    nodes = np.asarray([row["left_nodes"] + row["right_nodes"] for row in rows])
    seconds = np.asarray([row["seconds"] for row in rows], dtype=float)
    rho, p_value = spearmanr(nodes, seconds)
    design = np.column_stack((np.ones(len(nodes)), nodes))
    intercept, slope = np.linalg.lstsq(design, seconds, rcond=None)[0]
    quartiles = []
    for quartile in range(1, 5):
        selected = [row for row in rows if bins[int(row["pair_index"])] == quartile]
        sizes = [row["left_nodes"] + row["right_nodes"] for row in selected]
        times = [row["seconds"] for row in selected]
        quartiles.append({
            "quartile": quartile,
            "pairs": len(selected),
            "minimum_total_nodes": min(sizes),
            "maximum_total_nodes": max(sizes),
            "mean_total_nodes": float(np.mean(sizes)),
            "mean_seconds": float(np.mean(times)),
            "median_seconds": float(np.median(times)),
        })
    return {
        "pairs": len(rows),
        "mean_seconds": float(seconds.mean()),
        "median_seconds": float(np.median(seconds)),
        "spearman_total_nodes_vs_seconds": float(rho),
        "spearman_p_raw": float(p_value),
        "ols_seconds_intercept": float(intercept),
        "ols_seconds_per_additional_node": float(slope),
        "size_quartiles": quartiles,
    }


def main() -> int:
    args = parse_args()
    paths = sorted(args.results_dir.glob("*_records.jsonl"))
    if not paths:
        raise FileNotFoundError("no natural-pair explanation records")
    methods = {}
    hashes = {}
    expected_pairs = None
    reference_rows = None
    for path in paths:
        rows = load(path)
        method = path.name[:-len("_records.jsonl")]
        if len(rows) < 100:
            raise RuntimeError("{} is incomplete: {} rows".format(path, len(rows)))
        pair_ids = {int(row["pair_index"]) for row in rows}
        if expected_pairs is None:
            expected_pairs, reference_rows = pair_ids, rows
        elif pair_ids != expected_pairs:
            raise RuntimeError("methods do not share identical natural pairs")
        methods[method] = rows
        hashes[method] = {
            "path": str(path.resolve()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    ranked = sorted(
        reference_rows,
        key=lambda row: (
            row["left_nodes"] + row["right_nodes"], int(row["pair_index"])
        ),
    )
    bins = {
        int(row["pair_index"]): min(4, index * 4 // len(ranked) + 1)
        for index, row in enumerate(ranked)
    }
    summaries = {
        method: method_summary(rows, bins) for method, rows in methods.items()
    }
    candidate = summaries.get("symmetric_semantic_optimal_pair")
    if candidate is not None:
        for method, row in summaries.items():
            row["mean_time_ratio_to_tc_sosp"] = (
                row["mean_seconds"] / candidate["mean_seconds"]
            )
    result = {
        "scope": "GCJ natural validation pairs only",
        "timing": "single-GPU end-to-end explanation wall time per graph pair",
        "records": hashes,
        "methods": summaries,
        "test_metrics": None,
        "limitations": [
            "quartiles are descriptive empirical scaling, not an asymptotic complexity proof",
            "GPU timing includes method-specific predictor calls and synchronization",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "output": str(args.output), "methods": list(summaries),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
