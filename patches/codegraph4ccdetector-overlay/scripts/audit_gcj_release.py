#!/usr/bin/env python3
"""Audit the GCJ source, vector JSON, and released pair splits."""

import argparse
import json
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("googlejam4_src"))
    parser.add_argument(
        "--vector-dir",
        type=Path,
        default=Path("DataSetJsonVec/GCJ/dataSetCfgGCJ16"),
    )
    parser.add_argument(
        "--split-dir", type=Path, default=Path("DataSetJsonVec/GCJ/javadata")
    )
    parser.add_argument(
        "--splits", nargs="+", default=("train11.txt", "valid.txt", "test.txt")
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def read_pairs(path):
    pairs = []
    with path.open("r", encoding="utf-8") as split_file:
        for line_number, line in enumerate(split_file, start=1):
            fields = line.split()
            if len(fields) < 3:
                raise ValueError("{}:{}: malformed pair".format(path, line_number))
            pairs.append((fields[0], fields[1], 1 if int(fields[2]) == 1 else 0))
    return pairs


def main():
    args = parse_args()
    split_pairs = {
        name: read_pairs(args.split_dir / name) for name in args.splits
    }
    referenced = sorted(
        {
            path
            for pairs in split_pairs.values()
            for first, second, _ in pairs
            for path in (first, second)
        }
    )

    graph_status = {}
    invalid = {}
    missing = []
    missing_sources = []
    for source_path in referenced:
        if not Path(source_path).is_file():
            missing_sources.append(source_path)
        vector_path = args.vector_dir / (Path(source_path).name + ".json")
        if not vector_path.is_file():
            graph_status[source_path] = False
            missing.append(source_path)
            continue
        try:
            with vector_path.open("r", encoding="utf-8") as vector_file:
                json.load(vector_file)
            graph_status[source_path] = True
        except (OSError, ValueError) as error:
            graph_status[source_path] = False
            invalid[source_path] = "{}: {}".format(type(error).__name__, error)

    split_report = {}
    for name, pairs in split_pairs.items():
        usable = sum(
            graph_status[first] and graph_status[second]
            for first, second, _ in pairs
        )
        positives = sum(label for _, _, label in pairs)
        split_report[name] = {
            "pairs": len(pairs),
            "positive_pairs": positives,
            "negative_pairs": len(pairs) - positives,
            "usable_pairs": usable,
            "skipped_pairs": len(pairs) - usable,
        }

    report = {
        "released_java_files": len(list(args.source_dir.rglob("*.java"))),
        "released_vector_json_files": len(list(args.vector_dir.glob("*.json"))),
        "referenced_graphs": len(referenced),
        "valid_referenced_graphs": sum(graph_status.values()),
        "invalid_vector_graphs": len(invalid),
        "missing_vector_graphs": len(missing),
        "missing_source_graphs": len(missing_sources),
        "splits": split_report,
        "invalid_vectors": invalid,
        "missing_vectors": missing,
        "missing_sources": missing_sources,
    }
    serialized = json.dumps(report, indent=2, ensure_ascii=False)
    print(serialized)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
