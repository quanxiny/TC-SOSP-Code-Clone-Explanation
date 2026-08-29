#!/usr/bin/env python3
"""Audit pair manifests, exact source duplicates and cross-split leakage."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Pattern, Set, Tuple

try:
    from .configlib import RESEARCH_ROOT, resolve_config, resolve_workspace_path
except ImportError:  # Direct execution: python3 scripts/audit_splits.py
    from configlib import RESEARCH_ROOT, resolve_config, resolve_workspace_path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_label(raw: str) -> int:
    return 1 if int(raw) == 1 else 0


def read_split(path: Path, group_pattern: Optional[Pattern[str]] = None) -> Dict[str, Any]:
    graphs: Set[str] = set()
    groups: Set[str] = set()
    ordered: Counter[Tuple[str, str, int]] = Counter()
    unordered: Counter[Tuple[str, str, int]] = Counter()
    positives = 0
    rows = 0
    malformed = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            fields = line.split()
            if not fields:
                continue
            if len(fields) < 3:
                malformed.append(line_number)
                continue
            try:
                label = normalize_label(fields[2])
            except ValueError:
                malformed.append(line_number)
                continue
            left, right = fields[:2]
            rows += 1
            positives += label
            graphs.update((left, right))
            ordered[(left, right, label)] += 1
            unordered[(min(left, right), max(left, right), label)] += 1
            if group_pattern:
                for graph in (left, right):
                    match = group_pattern.search(graph)
                    if match:
                        groups.add(match.group(1) if match.groups() else match.group(0))
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "pairs": rows,
        "positive_pairs": positives,
        "negative_pairs": rows - positives,
        "positive_fraction": positives / rows if rows else None,
        "unique_fragments": len(graphs),
        "fragments": graphs,
        "verified_groups": len(groups) if group_pattern else None,
        "malformed_lines": malformed[:20],
        "malformed_count": len(malformed),
        "duplicate_ordered_rows": sum(count - 1 for count in ordered.values() if count > 1),
        "duplicate_unordered_rows": sum(count - 1 for count in unordered.values() if count > 1),
    }


def exact_source_duplicates(graphs: Iterable[str], source_dir: Path) -> Dict[str, Any]:
    repository_root = source_dir.parent
    by_digest = defaultdict(list)
    missing = []
    for graph in sorted(set(graphs)):
        source = repository_root / graph
        if not source.is_file():
            missing.append(graph)
            continue
        by_digest[sha256_file(source)].append(graph)
    duplicates = [items for items in by_digest.values() if len(items) > 1]
    duplicates.sort(key=lambda items: (-len(items), items))
    return {
        "missing_source_count": len(missing),
        "missing_source_examples": missing[:20],
        "exact_duplicate_groups": len(duplicates),
        "fragments_in_exact_duplicate_groups": sum(len(items) for items in duplicates),
        "exact_duplicate_examples": duplicates[:20],
    }


def audit_protocol(config: Dict[str, Any], group_regex: Optional[str] = None,
                   hash_sources: bool = True) -> Dict[str, Any]:
    paths = config.get("paths") or {}
    required = ("train_split", "validation_split", "test_split")
    missing_keys = [key for key in required if key not in paths]
    if missing_keys:
        raise ValueError("protocol lacks paths: {}".format(", ".join(missing_keys)))
    pattern = re.compile(group_regex) if group_regex else None
    reports = {
        name: read_split(resolve_workspace_path(paths[key]), pattern)
        for name, key in (
            ("train", "train_split"),
            ("validation", "validation_split"),
            ("test", "test_split"),
        )
    }
    graph_sets = {name: report.pop("fragments") for name, report in reports.items()}
    overlaps = {
        "train_validation": sorted(graph_sets["train"] & graph_sets["validation"]),
        "train_test": sorted(graph_sets["train"] & graph_sets["test"]),
        "validation_test": sorted(graph_sets["validation"] & graph_sets["test"]),
    }
    overlap_counts = {name: len(items) for name, items in overlaps.items()}
    contract = config.get("data_contract", {})
    violations = []
    if not contract.get("allow_fragment_overlap", False):
        violations = [name for name, count in overlap_counts.items() if count]
    result: Dict[str, Any] = {
        "experiment_id": config.get("experiment_id"),
        "dataset": config.get("dataset"),
        "graph_type": config.get("graph_type"),
        "split": config.get("split"),
        "group_regex": group_regex,
        "warning": None if group_regex else "No verified group metadata supplied; group counts intentionally omitted.",
        "splits": reports,
        "cross_split_fragment_overlap": overlap_counts,
        "overlap_examples": {name: items[:20] for name, items in overlaps.items()},
        "contract_violations": violations,
    }
    if hash_sources:
        source_dir = resolve_workspace_path(paths["source_dir"])
        result["exact_source_duplicate_audit"] = exact_source_duplicates(
            set().union(*graph_sets.values()), source_dir
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument(
        "--group-regex",
        help="Use only after the captured field is verified as true project/problem/function metadata.",
    )
    parser.add_argument("--no-source-hash", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = resolve_config(args.protocol)
    report = audit_protocol(config, args.group_regex, not args.no_source_hash)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else RESEARCH_ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(output.resolve())
    else:
        print(payload, end="")
    return 2 if report["contract_violations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
