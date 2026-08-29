#!/usr/bin/env python3
"""Build one immutable, label-stratified pilot manifest shared by A0/A1/A2."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

try:
    from .configlib import RESEARCH_ROOT, resolve_workspace_path
except ImportError:  # Direct execution
    from configlib import RESEARCH_ROOT, resolve_workspace_path


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selection_key(seed: int, index: int, line: str) -> str:
    value = "{}\0{}\0{}".format(seed, index, line.rstrip("\n"))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalized_label(line: str) -> int:
    fields = line.split()
    if len(fields) < 3:
        raise ValueError("malformed pair row: {!r}".format(line))
    return 1 if int(fields[2]) == 1 else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fraction", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--balance-labels", action="store_true",
        help="Select the same count from every normalized label.",
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0 < args.fraction <= 1:
        raise ValueError("--fraction must be in (0, 1]")
    input_path = resolve_workspace_path(args.input)
    output_path = resolve_workspace_path(args.output)
    metadata_path = output_path.with_suffix(output_path.suffix + ".meta.json")
    if (output_path.exists() or metadata_path.exists()) and not args.force:
        raise FileExistsError("refusing to overwrite existing pilot manifest")

    lines = input_path.read_text(encoding="utf-8").splitlines(True)
    candidates = defaultdict(list)
    for index, line in enumerate(lines):
        label = normalized_label(line)
        candidates[label].append((selection_key(args.seed, index, line), index, line))

    selected = []
    selected_by_label = {}
    requested_counts = {
        label: round(len(items) * args.fraction)
        for label, items in candidates.items()
    }
    balanced_count = min(requested_counts.values()) if args.balance_labels else None
    for label in sorted(candidates):
        items = sorted(candidates[label])
        count = balanced_count if balanced_count is not None else requested_counts[label]
        selected_by_label[str(label)] = count
        selected.extend(items[:count])
    selected.sort()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(item[2] for item in selected), encoding="utf-8")
    fragments = {
        field
        for _, _, line in selected
        for field in line.split()[:2]
    }
    metadata = {
        "method": "lowest_sha256_per_normalized_label",
        "seed": args.seed,
        "fraction": args.fraction,
        "balance_labels": bool(args.balance_labels),
        "input": str(input_path),
        "input_sha256": file_digest(input_path),
        "input_pairs": len(lines),
        "selected_pairs": len(selected),
        "selected_by_normalized_label": selected_by_label,
        "selected_unique_fragments": len(fragments),
        "output": str(output_path),
        "output_sha256": file_digest(output_path),
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
