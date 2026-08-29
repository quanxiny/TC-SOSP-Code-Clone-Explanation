#!/usr/bin/env python3
"""Recover exact CFG-node provenance for compiled explanation transformations."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from difflib import SequenceMatcher
from json import JSONDecoder
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "external_data" / "explanation_truth" / "gcj_transformations"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--vector-dir", type=Path)
    return parser.parse_args()


def decode_objects(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    decoder = JSONDecoder()
    values = []
    position = 0
    while position < len(text):
        while position < len(text) and text[position].isspace():
            position += 1
        if position < len(text):
            value, position = decoder.raw_decode(text, position)
            values.append(value)
    return values


def merged_node_text_and_edges(path: Path) -> Tuple[List[str], List[Tuple[int, int]]]:
    nodes: List[str] = []
    edges: List[Tuple[int, int]] = []
    for method in decode_objects(path):
        old_ids = sorted(method["jsonNodes"], key=int)
        offset = len(nodes)
        mapping = {
            old_id: offset + index for index, old_id in enumerate(old_ids)
        }
        nodes.extend(method["jsonNodes"][old_id] for old_id in old_ids)
        for edge in method["jsonEdges"]:
            source, target = edge.split("->")
            edges.append((mapping[source], mapping[target]))
    return nodes, sorted(edges)


def canonical_text(value: str) -> str:
    return " ".join(value.split())


def replace_identifiers(value: str, mapping: Dict[str, str]) -> str:
    if not mapping:
        return value
    pattern = re.compile(
        r"\b(?:" + "|".join(re.escape(name) for name in sorted(
            mapping, key=len, reverse=True
        )) + r")\b"
    )
    return pattern.sub(lambda match: mapping[match.group(0)], value)


def lcs_mapping(left: Sequence[str], right: Sequence[str]) -> List[Tuple[int, int]]:
    matcher = SequenceMatcher(a=list(left), b=list(right), autojunk=False)
    mapping = []
    for left_start, right_start, length in matcher.get_matching_blocks():
        mapping.extend(
            (left_start + offset, right_start + offset) for offset in range(length)
        )
    return mapping


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = parse_args()
    raw_dir = args.raw_dir or args.root / "preprocessed_raw" / "outPut_cfg" / "codeJson"
    vector_dir = args.vector_dir or args.root / "cfg16_normalized"
    transform_manifest_path = args.root / "transformation_manifest.json"
    transform_manifest = json.loads(
        transform_manifest_path.read_text(encoding="utf-8")
    )
    truth_records = []
    pair_lines = []
    all_dead_counts = []
    for record in transform_manifest["records"]:
        files = record["files"]
        raw_paths = {
            variant: raw_dir / (filename + ".json")
            for variant, filename in files.items()
        }
        vector_paths = {
            variant: vector_dir / (filename + ".json")
            for variant, filename in files.items()
        }
        missing = [
            str(path) for path in list(raw_paths.values()) + list(vector_paths.values())
            if not path.is_file()
        ]
        if missing:
            raise FileNotFoundError("missing preprocessed variants: {}".format(missing))

        graphs = {
            variant: merged_node_text_and_edges(path)
            for variant, path in raw_paths.items()
        }
        original_nodes, original_edges = graphs["original"]
        alpha_nodes, alpha_edges = graphs["alpha"]
        dead_nodes, dead_edges = graphs["alpha_dead"]
        reverse_mapping = {
            renamed: original for original, renamed in record["alpha_mapping"].items()
        }
        canonical_original = [canonical_text(value) for value in original_nodes]
        canonical_alpha_as_original = [
            canonical_text(replace_identifiers(value, reverse_mapping))
            for value in alpha_nodes
        ]
        if canonical_original != canonical_alpha_as_original:
            raise RuntimeError(
                "alpha node correspondence is not exact for {}".format(record["sample_id"])
            )
        if original_edges != alpha_edges:
            raise RuntimeError(
                "alpha CFG topology changed for {}".format(record["sample_id"])
            )

        canonical_alpha = [canonical_text(value) for value in alpha_nodes]
        canonical_dead = [canonical_text(value) for value in dead_nodes]
        alpha_to_dead = lcs_mapping(canonical_alpha, canonical_dead)
        if len(alpha_to_dead) != len(alpha_nodes):
            raise RuntimeError(
                "dead-code insertion failed to retain every alpha node for {}".format(
                    record["sample_id"]
                )
            )
        mapped_dead = {right for _, right in alpha_to_dead}
        distractor_nodes = sorted(set(range(len(dead_nodes))) - mapped_dead)
        if not distractor_nodes:
            raise RuntimeError("dead-code transformation added no CFG nodes")
        if not any(
            record["dead_identifier"] in dead_nodes[index]
            for index in distractor_nodes
        ):
            raise RuntimeError("unmatched nodes do not contain the dead-code marker")
        all_dead_counts.append(len(distractor_nodes))

        original_to_alpha = [[index, index] for index in range(len(original_nodes))]
        truth_records.append({
            "sample_id": record["sample_id"],
            "validation_source": record["validation_source"],
            "files": files,
            "vector_graph_sha256": {
                variant: sha256(path) for variant, path in vector_paths.items()
            },
            "node_counts": {
                "original": len(original_nodes),
                "alpha": len(alpha_nodes),
                "alpha_dead": len(dead_nodes),
            },
            "original_to_alpha_node_mapping": original_to_alpha,
            "alpha_to_alpha_dead_node_mapping": [list(pair) for pair in alpha_to_dead],
            "alpha_dead_known_irrelevant_nodes": distractor_nodes,
            "alpha_dead_known_irrelevant_node_text": {
                str(index): dead_nodes[index] for index in distractor_nodes
            },
            "alpha_cfg_topology_exactly_preserved": True,
            "compilation_all_variants": True,
        })
        pair_lines.extend([
            "{} {} 1\n".format(files["original"], files["alpha"]),
            "{} {} 1\n".format(files["alpha"], files["alpha_dead"]),
        ])

    pair_path = args.root / "truth_pairs.txt"
    pair_path.write_text("".join(pair_lines), encoding="utf-8")
    report = {
        "benchmark": transform_manifest["benchmark"],
        "samples": len(truth_records),
        "pairs": len(pair_lines),
        "truth_axes": {
            "alpha_correspondence": "exact node text and CFG topology after inverse rename",
            "dead_distractor": "unmatched CFG nodes introduced by a semantics-neutral block",
        },
        "mean_known_irrelevant_nodes": sum(all_dead_counts) / len(all_dead_counts),
        "minimum_known_irrelevant_nodes": min(all_dead_counts),
        "maximum_known_irrelevant_nodes": max(all_dead_counts),
        "source_manifest": str(transform_manifest_path.resolve()),
        "source_manifest_sha256": sha256(transform_manifest_path),
        "raw_dir": str(raw_dir.resolve()),
        "vector_dir": str(vector_dir.resolve()),
        "pair_manifest": str(pair_path.resolve()),
        "pair_manifest_sha256": sha256(pair_path),
        "test_used": False,
        "records": truth_records,
    }
    report_path = args.root / "explanation_truth_manifest.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "report": str(report_path),
        "samples": report["samples"],
        "pairs": report["pairs"],
        "dead_nodes": {
            "mean": report["mean_known_irrelevant_nodes"],
            "min": report["minimum_known_irrelevant_nodes"],
            "max": report["maximum_known_irrelevant_nodes"],
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
