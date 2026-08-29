#!/usr/bin/env python3
"""Repair the released GCJ CFG vectors without mixing embedding spaces.

The upstream writer appends one JSON object per Java method to a file.  This
script decodes those concatenated objects and merges their disconnected method
graphs into one file-level graph.  It also reconstructs the released token to
vector lookup from aligned plain/vector graphs so that the one missing released
file can be vectorized in the same embedding space.
"""

import argparse
import json
import re
from collections import Counter
from json import JSONDecoder
from pathlib import Path


DIMENSION = 16


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--plain-dir", type=Path, required=True)
    parser.add_argument("--released-vector-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def decode_objects(path):
    text = path.read_text(encoding="utf-8")
    decoder = JSONDecoder()
    objects = []
    position = 0
    while position < len(text):
        while position < len(text) and text[position].isspace():
            position += 1
        if position >= len(text):
            break
        value, position = decoder.raw_decode(text, position)
        objects.append(value)
    return objects


def align_plain_methods(plain_objects, vector_objects):
    if len(plain_objects) == len(vector_objects):
        return plain_objects
    nonempty = [value for value in plain_objects if value["jsonNodes"]]
    if len(nonempty) == len(vector_objects):
        return nonempty

    unused = list(plain_objects)
    aligned = []
    for vector in vector_objects:
        signature = (
            len(vector["jsonNodesVec"]), len(vector["jsonEdgesVec"])
        )
        match = next(
            (
                plain
                for plain in unused
                if (len(plain["jsonNodes"]), len(plain["jsonEdges"])) == signature
            ),
            None,
        )
        if match is None:
            return plain_objects
        aligned.append(match)
        unused.remove(match)
    return aligned


def java_split(text):
    if text == "":
        return [""]
    fields = re.split(r"\s+", text)
    while len(fields) > 1 and fields[-1] == "":
        fields.pop()
    return fields


def edge_tokens(text):
    return java_split(text.replace(";", " ;").replace("\n", "\\n").replace("\r", "\\r"))


def learn_vectors(plain_objects, vector_objects, lookup, conflicts, alignment_errors):
    if len(plain_objects) != len(vector_objects):
        alignment_errors.append(
            "method count {} != {}".format(len(plain_objects), len(vector_objects))
        )
        return
    for method_index, (plain, vector) in enumerate(zip(plain_objects, vector_objects)):
        for plain_key, vector_key, tokenizer in (
            ("jsonNodes", "jsonNodesVec", java_split),
            ("jsonEdges", "jsonEdgesVec", edge_tokens),
        ):
            if set(plain[plain_key]) != set(vector[vector_key]):
                alignment_errors.append(
                    "method {} {} keys differ".format(method_index, plain_key)
                )
                continue
            for item_id, text in plain[plain_key].items():
                tokens = tokenizer(text)
                vectors = vector[vector_key][item_id]
                if len(tokens) != len(vectors):
                    alignment_errors.append(
                        "method {} {} {} token count {} != {}".format(
                            method_index, plain_key, item_id, len(tokens), len(vectors)
                        )
                    )
                    continue
                for token, embedding in zip(tokens, vectors):
                    if embedding is None or token == "":
                        continue
                    if len(embedding) != DIMENSION:
                        alignment_errors.append(
                            "method {} {} {} has dimension {}".format(
                                method_index, plain_key, item_id, len(embedding)
                            )
                        )
                        continue
                    previous = lookup.setdefault(token, embedding)
                    if previous != embedding:
                        conflicts[token] += 1


def vectorize_plain(plain_objects, lookup, unknown_tokens):
    result = []
    zeros = [0.0] * DIMENSION
    ones = [1.0] * DIMENSION
    for plain in plain_objects:
        node_vectors = {}
        for node_id, text in plain["jsonNodes"].items():
            vectors = []
            for token in java_split(text):
                embedding = lookup.get(token)
                if embedding is None:
                    unknown_tokens[token] += 1
                    embedding = zeros
                vectors.append(embedding)
            node_vectors[node_id] = vectors

        edge_vectors = {}
        for edge_id, text in plain["jsonEdges"].items():
            tokens = edge_tokens(text)
            if tokens == [""]:
                edge_vectors[edge_id] = [ones]
                continue
            vectors = []
            for token in tokens:
                embedding = lookup.get(token)
                if embedding is None:
                    unknown_tokens[token] += 1
                    embedding = zeros
                vectors.append(embedding)
            edge_vectors[edge_id] = vectors
        result.append({"jsonNodesVec": node_vectors, "jsonEdgesVec": edge_vectors})
    return result


def merge_methods(methods):
    merged_nodes = {}
    merged_edges = {}
    next_node = 0
    for method in methods:
        id_map = {}
        for old_id in sorted(method["jsonNodesVec"], key=int):
            new_id = str(next_node)
            next_node += 1
            id_map[old_id] = new_id
            merged_nodes[new_id] = method["jsonNodesVec"][old_id]
        for old_edge, value in method["jsonEdgesVec"].items():
            source, target = old_edge.split("->")
            merged_edges[id_map[source] + "->" + id_map[target]] = value
    return {"jsonEdgesVec": merged_edges, "jsonNodesVec": merged_nodes}


def validate_graph(graph):
    expected_ids = [str(index) for index in range(len(graph["jsonNodesVec"]))]
    if sorted(graph["jsonNodesVec"], key=int) != expected_ids:
        raise ValueError("node identifiers are not contiguous")
    for vectors in graph["jsonNodesVec"].values():
        if not vectors:
            raise ValueError("node has no token vectors")
        for vector in vectors:
            if vector is not None and len(vector) != DIMENSION:
                raise ValueError("node vector has wrong dimension")
    for edge_id, vectors in graph["jsonEdgesVec"].items():
        source, target = edge_id.split("->")
        if source not in graph["jsonNodesVec"] or target not in graph["jsonNodesVec"]:
            raise ValueError("edge references an absent node")
        if not vectors or vectors[0] is None or len(vectors[0]) != DIMENSION:
            raise ValueError("edge vector is missing or has wrong dimension")


def main():
    args = parse_args()
    sources = sorted(args.source_dir.rglob("*.java"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    lookup = {}
    conflicts = Counter()
    alignment_errors = []
    released_method_counts = Counter()
    aligned_files = 0
    for source in sources:
        plain_path = args.plain_dir / (source.name + ".json")
        vector_path = args.released_vector_dir / (source.name + ".json")
        if not plain_path.is_file() or not vector_path.is_file():
            continue
        plain_objects = decode_objects(plain_path)
        vector_objects = decode_objects(vector_path)
        plain_objects = align_plain_methods(plain_objects, vector_objects)
        released_method_counts[len(vector_objects)] += 1
        file_errors = []
        learn_vectors(
            plain_objects, vector_objects, lookup, conflicts, file_errors
        )
        if file_errors:
            alignment_errors.extend(
                "{}: {}".format(source.name, error) for error in file_errors
            )
        else:
            aligned_files += 1

    unknown_tokens = Counter()
    missing_released = []
    node_counts = []
    edge_counts = []
    for source in sources:
        plain_path = args.plain_dir / (source.name + ".json")
        vector_path = args.released_vector_dir / (source.name + ".json")
        if vector_path.is_file():
            method_vectors = decode_objects(vector_path)
        else:
            if not plain_path.is_file():
                raise FileNotFoundError("plain graph missing: {}".format(plain_path))
            missing_released.append(source.name)
            method_vectors = vectorize_plain(
                decode_objects(plain_path), lookup, unknown_tokens
            )
        graph = merge_methods(method_vectors)
        validate_graph(graph)
        node_counts.append(len(graph["jsonNodesVec"]))
        edge_counts.append(len(graph["jsonEdgesVec"]))
        output_path = args.output_dir / (source.name + ".json")
        output_path.write_text(
            json.dumps(graph, separators=(",", ":"), ensure_ascii=False),
            encoding="utf-8",
        )

    report = {
        "source_files": len(sources),
        "output_files": len(list(args.output_dir.glob("*.json"))),
        "aligned_released_files": aligned_files,
        "released_method_count_distribution": dict(sorted(released_method_counts.items())),
        "recovered_token_vectors": len(lookup),
        "vector_conflict_tokens": len(conflicts),
        "vector_conflict_occurrences": sum(conflicts.values()),
        "alignment_errors": alignment_errors,
        "missing_released_files": missing_released,
        "unknown_tokens_in_reconstructed_files": dict(unknown_tokens.most_common()),
        "average_nodes": sum(node_counts) / len(node_counts),
        "average_edges": sum(edge_counts) / len(edge_counts),
    }
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
