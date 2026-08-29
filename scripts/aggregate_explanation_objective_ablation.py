#!/usr/bin/env python3
"""Aggregate the TC-SOSP necessity/sufficiency objective-weight ablation."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.explanation_runner import aggregate, paired_comparison  # noqa: E402
STUDIES = (
    (0.0, ROOT / "artifacts" / "pilots" / "C11_semantic_optimal_objective_lambda0_seed42"),
    (0.5, ROOT / "artifacts" / "pilots" / "C12_semantic_optimal_objective_lambda05_seed42"),
    (1.0, ROOT / "artifacts" / "pilots" / "C1_semantic_optimal_subgraph_pair_seed42"),
    (2.0, ROOT / "artifacts" / "pilots" / "C13_semantic_optimal_objective_lambda2_seed42"),
)
OUTPUT = (
    ROOT / "artifacts" / "comparisons"
    / "C_tc_sosp_objective_weight_ablation_validation.json"
)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for row in rows:
        row.setdefault("absolute_sufficiency_gap", abs(row["sufficiency_gap"]))
    return rows


def main() -> int:
    rows = {}
    summaries = {}
    evidence = {}
    expected = None
    for weight, directory in STUDIES:
        summary_path = directory / "summary.json"
        record_path = directory / "symmetric_semantic_optimal_pair_records.jsonl"
        if not summary_path.is_file() or not record_path.is_file():
            raise FileNotFoundError("objective ablation incomplete: {}".format(directory))
        records = load_jsonl(record_path)
        if len(records) != 100:
            raise RuntimeError("{} has {} rather than 100 pairs".format(
                record_path, len(records)
            ))
        pair_ids = {int(row["pair_index"]) for row in records}
        if expected is None:
            expected = pair_ids
        elif pair_ids != expected:
            raise RuntimeError("objective weights do not share identical pairs")
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        configured = float(
            summary["configuration"]["explanation"]["optimal_sufficiency_weight"]
        )
        if configured != weight:
            raise RuntimeError("objective weight mismatch in {}".format(summary_path))
        rows[weight] = records
        summaries[weight] = {
            **aggregate(records, 10000, 870000 + int(weight * 10000)),
            "selected_candidate_counts": dict(sorted(Counter(
                row["selected_candidate"] for row in records
            ).items())),
        }
        evidence[str(weight)] = {
            "summary": str(summary_path.resolve()),
            "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
            "records": str(record_path.resolve()),
            "records_sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
        }

    reference = rows[1.0]
    comparisons = {
        "lambda_{}_minus_lambda_1".format(str(weight).replace(".", "_")):
        paired_comparison(
            reference, records, 10000, 880000 + int(weight * 10000)
        )
        for weight, records in rows.items() if weight != 1.0
    }
    points = {
        str(weight): (
            row["necessity_drop"]["mean"], row["absolute_sufficiency_gap"]["mean"]
        ) for weight, row in summaries.items()
    }
    pareto = []
    for weight, (necessity, sufficiency) in points.items():
        dominated = any(
            other_necessity >= necessity and other_sufficiency <= sufficiency
            and (other_necessity > necessity or other_sufficiency < sufficiency)
            for other_weight, (other_necessity, other_sufficiency) in points.items()
            if other_weight != weight
        )
        if not dominated:
            pareto.append(float(weight))
    result = {
        "scope": "GCJ natural validation objective sensitivity; fixed 20% node budget",
        "objective": "necessity_drop - lambda * absolute_sufficiency_gap",
        "weights": {str(weight): summaries[weight] for weight, _ in STUDIES},
        "comparisons_to_lambda_1": comparisons,
        "pareto_weights": sorted(pareto),
        "evidence": evidence,
        "test_metrics": None,
        "interpretation_policy": (
            "lambda=1 was fixed before this sensitivity analysis and is not "
            "reselected using test or transformation-truth outcomes"
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "output": str(OUTPUT), "pareto_weights": result["pareto_weights"]
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
