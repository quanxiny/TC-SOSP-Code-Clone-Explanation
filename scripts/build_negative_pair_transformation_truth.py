#!/usr/bin/env python3
"""Pair transformed validation programs into disjoint semantic non-clones."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "external_data" / "explanation_truth" / "gcj_negative_transformations"
PROBLEM = re.compile(r"\.p([0-9]+)\.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def problem_id(record: Dict[str, Any]) -> str:
    match = PROBLEM.search(record["validation_source"])
    if match is not None:
        return match.group(1)
    first = Path(record["validation_source"]).parts[0]
    if re.fullmatch(r"p[0-9]+", first):
        return first
    raise ValueError("cannot recover semantic problem ID: {}".format(
        record["validation_source"]
    ))


def pair_records(records: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    if len(records) % 2:
        raise ValueError("an even number of source programs is required")
    ordered = sorted(records, key=lambda row: row["sample_id"])
    midpoint = len(ordered) // 2
    left, right = ordered[:midpoint], ordered[midpoint:]
    for rotation in range(len(right)):
        rotated = right[rotation:] + right[:rotation]
        if all(problem_id(a) != problem_id(b) for a, b in zip(left, rotated)):
            return list(zip(left, rotated))
    raise RuntimeError("could not form disjoint different-problem pairs")


def main() -> int:
    args = parse_args()
    truth_path = args.root / "explanation_truth_manifest.json"
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    pairs = pair_records(truth["records"])
    rows = []
    for index, (left, right) in enumerate(pairs):
        rows.append({
            "pair_id": "n{:03d}_{}_{}".format(
                index, left["sample_id"], right["sample_id"]
            ),
            "label": 0,
            "left_sample_id": left["sample_id"],
            "right_sample_id": right["sample_id"],
            "left_problem_id": problem_id(left),
            "right_problem_id": problem_id(right),
            "left_validation_source": left["validation_source"],
            "right_validation_source": right["validation_source"],
            "base_files": [left["files"]["original"], right["files"]["original"]],
            "alpha_files": [left["files"]["alpha"], right["files"]["alpha"]],
            "dead_files": [
                left["files"]["alpha_dead"], right["files"]["alpha_dead"]
            ],
            "base_to_alpha_mapping": [
                left["original_to_alpha_node_mapping"],
                right["original_to_alpha_node_mapping"],
            ],
            "alpha_to_dead_mapping": [
                left["alpha_to_alpha_dead_node_mapping"],
                right["alpha_to_alpha_dead_node_mapping"],
            ],
            "dead_known_irrelevant_nodes": [
                left["alpha_dead_known_irrelevant_nodes"],
                right["alpha_dead_known_irrelevant_nodes"],
            ],
        })
    if len({row["left_sample_id"] for row in rows} | {
        row["right_sample_id"] for row in rows
    }) != 2 * len(rows):
        raise RuntimeError("source programs are reused across negative pairs")
    if any(row["left_problem_id"] == row["right_problem_id"] for row in rows):
        raise RuntimeError("a negative pair shares the same semantic problem")
    result = {
        "benchmark": "GCJ validation negative-pair metamorphic explanation truth",
        "pairs": len(rows),
        "source_programs": 2 * len(rows),
        "label": 0,
        "pairing": "SHA-ranked disjoint source halves with first valid cyclic rotation",
        "truth_axes": [
            "sidewise explanation correspondence under bilateral alpha-renaming",
            "sidewise correspondence after bilateral dead-code insertion",
            "rejection of known irrelevant dead-code nodes on both graphs",
            "prediction invariance under semantic-preserving transformations",
        ],
        "source_truth_manifest": str(truth_path.resolve()),
        "source_truth_manifest_sha256": hashlib.sha256(
            truth_path.read_bytes()
        ).hexdigest(),
        "test_used": False,
        "records": rows,
    }
    output = args.output or args.root / "negative_pair_truth_manifest.json"
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "output": str(output), "pairs": len(rows),
        "different_problem_pairs": sum(
            row["left_problem_id"] != row["right_problem_id"] for row in rows
        ),
        "unique_programs": result["source_programs"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
