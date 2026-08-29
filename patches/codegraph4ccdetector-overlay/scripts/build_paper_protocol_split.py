#!/usr/bin/env python3
"""Build a balanced training split that remains disjoint from valid/test."""

import argparse
import json
import random
from pathlib import Path


def paths(lines):
    return {path for line in lines for path in line.split()[:2]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive", type=Path, default=Path("DataSetJsonVec/GCJ/javadata/trainpos.txt"))
    parser.add_argument("--negative", type=Path, default=Path("DataSetJsonVec/GCJ/javadata/trainneg.txt"))
    parser.add_argument("--validation", type=Path, default=Path("DataSetJsonVec/GCJ/javadata/valid.txt"))
    parser.add_argument("--test", type=Path, default=Path("DataSetJsonVec/GCJ/javadata/test.txt"))
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    positive = args.positive.read_text(encoding="utf-8").splitlines(True)
    negative = args.negative.read_text(encoding="utf-8").splitlines(True)
    validation = args.validation.read_text(encoding="utf-8").splitlines(True)
    test = args.test.read_text(encoding="utf-8").splitlines(True)
    rng = random.Random(args.seed)
    selected_negative = rng.sample(negative, len(positive))
    balanced = positive + selected_negative
    rng.shuffle(balanced)

    training_paths = paths(balanced)
    validation_paths = paths(validation)
    test_paths = paths(test)
    if training_paths & validation_paths or training_paths & test_paths or validation_paths & test_paths:
        raise ValueError("source-code leakage detected between train/valid/test")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(balanced), encoding="utf-8")
    report = {
        "seed": args.seed,
        "pairs": len(balanced),
        "positive_pairs": len(positive),
        "negative_pairs": len(selected_negative),
        "training_graphs": len(training_paths),
        "validation_graphs": len(validation_paths),
        "test_graphs": len(test_paths),
        "train_validation_overlap": len(training_paths & validation_paths),
        "train_test_overlap": len(training_paths & test_paths),
        "validation_test_overlap": len(validation_paths & test_paths),
    }
    report_path = args.output.with_suffix(args.output.suffix + ".report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
