#!/usr/bin/env python3
"""Aggregate C1 after excluding the four sample-specific smoke pairs."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Dict, List

from .explanation_runner import aggregate, paired_comparison


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "artifacts" / "pilots" / "C1_semantic_optimal_subgraph_pair_seed42"
DEFAULT_SMOKE = (
    ROOT / "artifacts" / "tests"
    / "C1_semantic_optimal_subgraph_pair_four_pair_smoke"
    / "validation_explanation_manifest.txt"
)
DEFAULT_OUTPUT = (
    ROOT / "artifacts" / "comparisons"
    / "C1_semantic_optimal_subgraph_pair_heldout96_validation.json"
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--smoke-manifest", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def pair_key(record: dict):
    return record["left"], record["right"], int(record["label"])


def manifest_key(line: str):
    left, right, raw_label = line.split()[:3]
    # GCJ uses 0/1 here, so no model-specific normalization is needed.
    return left, right, int(raw_label)


def read_records(input_dir: Path) -> Dict[str, List[dict]]:
    result = {}
    for path in sorted(input_dir.glob("*_records.jsonl")):
        method = path.name[:-len("_records.jsonl")]
        result[method] = [
            json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
        ]
    return result


def main() -> int:
    args = parse_args()
    smoke_keys = {
        manifest_key(line)
        for line in args.smoke_manifest.read_text(encoding="utf-8").splitlines()
    }
    all_records = read_records(args.input_dir)
    heldout = {
        method: [record for record in records if pair_key(record) not in smoke_keys]
        for method, records in all_records.items()
    }
    if not heldout or {len(records) for records in heldout.values()} != {96}:
        raise RuntimeError("expected identical 96-pair held-out records per method")

    baseline_name = "symmetric_grad_x_input"
    candidate_names = [name for name in heldout if name != baseline_name]
    output = {
        "protocol": {
            "scope": "validation pairs not used by the four-pair C1 smoke",
            "pairs": 96,
            "development_smoke_pairs": 4,
            "primary_budget": 0.2,
            "test_policy": "sealed_during_method_comparison",
            "caveat": "C0 baseline outcomes on the same validation pool were known before C1",
        },
        "input_summary_sha256": hashlib.sha256(
            (args.input_dir / "summary.json").read_bytes()
        ).hexdigest(),
        "smoke_manifest_sha256": hashlib.sha256(
            args.smoke_manifest.read_bytes()
        ).hexdigest(),
        "methods": {
            name: aggregate(records, 10000, 420000 + index * 100003)
            for index, (name, records) in enumerate(sorted(heldout.items()))
        },
        "comparisons_vs_symmetric_grad_x_input": {
            name: paired_comparison(
                heldout[baseline_name], heldout[name], 10000,
                900000 + index * 100003,
            )
            for index, name in enumerate(sorted(candidate_names))
        },
        "real_attention_minus_shuffled_attention": paired_comparison(
            heldout["symmetric_semantic_shuffled_attention_optimal_pair"],
            heldout["symmetric_semantic_attention_optimal_pair"],
            10000, 1400001,
        ),
        "selected_candidate_counts": {
            name: dict(collections.Counter(
                record["selected_candidate"] for record in records
            ))
            for name, records in heldout.items()
            if name != baseline_name
        },
        "test_metrics": None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
