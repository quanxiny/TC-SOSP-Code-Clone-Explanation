#!/usr/bin/env python3
"""Merge legacy concatenated method JSON into one validated file-level graph."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from json import JSONDecoder
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dimension", type=int, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def decode_objects(path):
    text = path.read_text(encoding="utf-8")
    decoder = JSONDecoder()
    values = []
    position = 0
    while position < len(text):
        while position < len(text) and text[position].isspace():
            position += 1
        if position >= len(text):
            break
        value, position = decoder.raw_decode(text, position)
        values.append(value)
    return values


def merge_methods(methods):
    nodes = {}
    edges = {}
    next_node = 0
    for method in methods:
        mapping = {}
        method_nodes = method["jsonNodesVec"]
        for old_id in sorted(method_nodes, key=int):
            new_id = str(next_node)
            next_node += 1
            mapping[old_id] = new_id
            nodes[new_id] = method_nodes[old_id]
        for old_edge, value in method["jsonEdgesVec"].items():
            source, target = old_edge.split("->")
            edges["{}->{}".format(mapping[source], mapping[target])] = value
    return {"jsonEdgesVec": edges, "jsonNodesVec": nodes}


def validate(graph, dimension):
    expected = [str(index) for index in range(len(graph["jsonNodesVec"]))]
    if sorted(graph["jsonNodesVec"], key=int) != expected:
        raise ValueError("non-contiguous node identifiers")
    if not expected:
        raise ValueError("graph has no nodes")
    for node_id, token_vectors in graph["jsonNodesVec"].items():
        if not token_vectors:
            raise ValueError("node {} has no token vectors".format(node_id))
        for vector in token_vectors:
            if vector is not None and len(vector) != dimension:
                raise ValueError("node {} vector dimension mismatch".format(node_id))
    for edge_id, vectors in graph["jsonEdgesVec"].items():
        source, target = edge_id.split("->")
        if source not in graph["jsonNodesVec"] or target not in graph["jsonNodesVec"]:
            raise ValueError("edge {} references an absent node".format(edge_id))
        if not vectors or vectors[0] is None or len(vectors[0]) != dimension:
            raise ValueError("edge {} vector dimension mismatch".format(edge_id))


def main():
    args = parse_args()
    inputs = sorted(args.input_dir.glob("*.json"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    distribution = Counter()
    failures = []
    node_counts = []
    edge_counts = []
    output_hashes = {}
    for path in inputs:
        try:
            methods = decode_objects(path)
            distribution[len(methods)] += 1
            graph = merge_methods(methods)
            validate(graph, args.dimension)
            node_counts.append(len(graph["jsonNodesVec"]))
            edge_counts.append(len(graph["jsonEdgesVec"]))
            payload = json.dumps(
                graph, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ) + "\n"
            output = args.output_dir / path.name
            output.write_text(payload, encoding="utf-8")
            output_hashes[path.name] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        except Exception as error:
            failures.append({"file": path.name, "error": str(error)})
    report = {
        "input_dir": str(args.input_dir.resolve()),
        "output_dir": str(args.output_dir.resolve()),
        "dimension": args.dimension,
        "input_files": len(inputs),
        "output_files": len(output_hashes),
        "method_object_count_distribution": {
            str(key): value for key, value in sorted(distribution.items())
        },
        "multi_method_files": sum(
            count for methods, count in distribution.items() if methods > 1
        ),
        "minimum_nodes": min(node_counts) if node_counts else None,
        "maximum_nodes": max(node_counts) if node_counts else None,
        "average_nodes": sum(node_counts) / len(node_counts) if node_counts else None,
        "minimum_edges": min(edge_counts) if edge_counts else None,
        "maximum_edges": max(edge_counts) if edge_counts else None,
        "average_edges": sum(edge_counts) / len(edge_counts) if edge_counts else None,
        "failures": failures,
        "output_manifest_sha256": hashlib.sha256(
            "".join("{} {}\n".format(name, output_hashes[name]) for name in sorted(output_hashes))
            .encode("utf-8")
        ).hexdigest(),
    }
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures and len(output_hashes) == len(inputs) else 2


if __name__ == "__main__":
    raise SystemExit(main())
