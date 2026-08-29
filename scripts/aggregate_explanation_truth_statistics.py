#!/usr/bin/env python3
"""Add multiplicity-controlled paired tests to transformation-truth studies."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from scipy.stats import wilcoxon


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_C8 = (
    ROOT / "artifacts" / "explanation_truth"
    / "C8_transformation_truth_strong_baselines_seed42" / "summary.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, action="append", default=[])
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "artifacts" / "comparisons"
        / "C_transformation_truth_paired_statistics.json",
    )
    return parser.parse_args()


def holm(raw: Dict[str, float]) -> Dict[str, float]:
    ordered = sorted(raw.items(), key=lambda item: item[1])
    adjusted: Dict[str, float] = {}
    running = 0.0
    for index, (name, value) in enumerate(ordered):
        running = max(running, min(1.0, (len(ordered) - index) * value))
        adjusted[name] = running
    return adjusted


def paired_test(values: List[float]) -> Dict[str, Any]:
    array = np.asarray(values, dtype=float)
    nonzero = array[array != 0]
    if len(nonzero) == 0:
        statistic, p_value, rank_biserial = 0.0, 1.0, 0.0
    else:
        result = wilcoxon(
            array, zero_method="pratt", correction=False,
            alternative="two-sided", method="auto",
        )
        statistic, p_value = float(result.statistic), float(result.pvalue)
        ranks = np.empty(len(nonzero), dtype=float)
        order = np.argsort(np.abs(nonzero), kind="mergesort")
        sorted_abs = np.abs(nonzero)[order]
        start = 0
        while start < len(nonzero):
            stop = start + 1
            while stop < len(nonzero) and sorted_abs[stop] == sorted_abs[start]:
                stop += 1
            ranks[order[start:stop]] = 0.5 * (start + 1 + stop)
            start = stop
        positive = float(ranks[nonzero > 0].sum())
        negative = float(ranks[nonzero < 0].sum())
        rank_biserial = (positive - negative) / (positive + negative)
    return {
        "n": int(len(array)),
        "positive": int((array > 0).sum()),
        "zero": int((array == 0).sum()),
        "negative": int((array < 0).sum()),
        "median": float(np.median(array)),
        "wilcoxon_two_sided_statistic": statistic,
        "wilcoxon_two_sided_p_raw": p_value,
        "matched_rank_biserial": float(rank_biserial),
    }


def analyze(path: Path) -> Dict[str, Any]:
    summary = json.loads(path.read_text(encoding="utf-8"))
    tests: Dict[str, Dict[str, Any]] = {}
    raw: Dict[str, float] = {}
    for comparison, metrics in summary["paired_comparisons"].items():
        for metric, payload in metrics.items():
            if not isinstance(payload, dict) or "values" not in payload:
                continue
            key = comparison + "/" + metric
            tests[key] = paired_test(payload["values"])
            raw[key] = tests[key]["wilcoxon_two_sided_p_raw"]
    adjusted = holm(raw)
    for key, value in adjusted.items():
        tests[key]["wilcoxon_two_sided_p_holm_all_endpoints"] = value
    return {
        "summary": str(path.resolve()),
        "summary_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "dataset": summary["configuration"].get("name", path.parent.name),
        "samples_or_pairs": summary.get("samples", summary.get("pairs")),
        "family_size": len(tests),
        "tests": tests,
    }


def main() -> int:
    args = parse_args()
    paths = args.summary or [DEFAULT_C8]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing explanation summaries: {}".format(missing))
    result = {
        "studies": [analyze(path) for path in paths],
        "inference": (
            "two-sided paired Wilcoxon signed-rank with Pratt zero handling; "
            "Holm correction across every baseline/endpoint test within a dataset"
        ),
        "test_metrics": None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "output": str(args.output),
        "studies": len(result["studies"]),
        "family_sizes": [row["family_size"] for row in result["studies"]],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
