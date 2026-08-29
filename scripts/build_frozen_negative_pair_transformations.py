#!/usr/bin/env python3
"""Transform disjoint correctly predicted negative pairs from frozen validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_transformation_explanation_truth import (
    alpha_rename,
    compile_source,
    insert_dead_code,
    sha256_bytes,
)


BASELINE_ROOT = ROOT.parent / "CodeGraph4CCDetector"
DEFAULT_MANIFEST = (
    ROOT / "artifacts" / "pilots" / "C1_semantic_optimal_subgraph_pair_seed42"
    / "validation_explanation_manifest.txt"
)
DEFAULT_PREDICTIONS = (
    ROOT / "artifacts" / "pilots" / "C1_semantic_optimal_subgraph_pair_seed42"
    / "symmetric_grad_x_input_records.jsonl"
)
DEFAULT_OUTPUT = (
    ROOT / "external_data" / "explanation_truth"
    / "gcj_frozen_negative_pair_transformations"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=BASELINE_ROOT)
    parser.add_argument("--validation-manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--prediction-records", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pairs", type=int, default=30)
    parser.add_argument(
        "--javac", type=Path,
        default=ROOT.parent / ".conda" / "codegraph4cc" / "bin" / "javac",
    )
    parser.add_argument("--compile-timeout", type=int, default=30)
    return parser.parse_args()


def load_predictions(path: Path) -> Dict[int, Dict[str, Any]]:
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {int(row["pair_index"]): row for row in rows}


def transform_source(
        source_name: str, source_root: Path, javac: Path, timeout: int
        ) -> Dict[str, Any]:
    source_path = source_root / source_name
    original = source_path.read_text(encoding="utf-8", errors="replace")
    alpha, alpha_mapping = alpha_rename(original)
    if len(alpha_mapping) < 2:
        return {"success": False, "reason": "fewer_than_two_identifiers"}
    try:
        alpha_dead, marker = insert_dead_code(alpha)
    except ValueError as error:
        return {"success": False, "reason": str(error)}
    contents = {"original": original, "alpha": alpha, "alpha_dead": alpha_dead}
    compilation = {
        variant: compile_source(content, javac, timeout)
        for variant, content in contents.items()
    }
    if not all(row["success"] for row in compilation.values()):
        return {
            "success": False, "reason": "compile_failure",
            "compilation": compilation,
        }
    return {
        "success": True,
        "contents": contents,
        "alpha_mapping": alpha_mapping,
        "dead_identifier": marker,
        "compilation": compilation,
    }


def main() -> int:
    args = parse_args()
    if args.output_dir.exists():
        raise FileExistsError("refusing to replace frozen truth root: {}".format(
            args.output_dir
        ))
    if args.pairs <= 0:
        raise ValueError("--pairs must be positive")
    if not args.javac.is_file():
        raise FileNotFoundError(str(args.javac))
    predictions = load_predictions(args.prediction_records)
    lines = args.validation_manifest.read_text(encoding="utf-8").splitlines()
    cache: Dict[str, Dict[str, Any]] = {}
    used = set()
    selected_pairs = []
    rejected = []

    for pair_index, line in enumerate(lines):
        fields = line.split()
        left_name, right_name, label = fields[:3]
        prediction = predictions.get(pair_index)
        if label != "0":
            continue
        if prediction is None or prediction["label"] != 0 or prediction["prediction"] != 0:
            rejected.append({
                "pair_index": pair_index, "line": line,
                "reason": "frozen_predictor_not_correct_nonclone",
            })
            continue
        if left_name in used or right_name in used:
            rejected.append({
                "pair_index": pair_index, "line": line,
                "reason": "source_reuse",
            })
            continue
        for source_name in (left_name, right_name):
            if source_name not in cache:
                cache[source_name] = transform_source(
                    source_name, args.source_root, args.javac, args.compile_timeout
                )
        failures = [
            {"source": name, **cache[name]}
            for name in (left_name, right_name) if not cache[name]["success"]
        ]
        if failures:
            rejected.append({
                "pair_index": pair_index, "line": line,
                "reason": "source_transformation_failure", "failures": failures,
            })
            continue
        used.update((left_name, right_name))
        selected_pairs.append({
            "pair_index": pair_index,
            "line": line,
            "left_source": left_name,
            "right_source": right_name,
            "frozen_prediction": prediction["prediction"],
            "frozen_base_target_probability": prediction["base_target_probability"],
        })
        if len(selected_pairs) == args.pairs:
            break
    if len(selected_pairs) != args.pairs:
        raise RuntimeError("only {} valid disjoint negative pairs".format(
            len(selected_pairs)
        ))

    source_output = args.output_dir / "sources"
    source_output.mkdir(parents=True)
    transformation_records = []
    source_to_sample = {}
    for source_position, source_name in enumerate(sorted(
        used, key=lambda name: hashlib.sha256(name.encode("utf-8")).hexdigest()
    )):
        transformed = cache[source_name]
        identifier = "n{:03d}_{}".format(
            source_position,
            hashlib.sha256(source_name.encode("utf-8")).hexdigest()[:10],
        )
        names = {
            variant: identifier + "__" + variant + ".java"
            for variant in ("original", "alpha", "alpha_dead")
        }
        for variant, filename in names.items():
            (source_output / filename).write_text(
                transformed["contents"][variant], encoding="utf-8"
            )
        source_to_sample[source_name] = identifier
        transformation_records.append({
            "sample_id": identifier,
            "validation_source": source_name,
            "validation_source_sha256": sha256_bytes(
                transformed["contents"]["original"].encode("utf-8")
            ),
            "files": names,
            "file_sha256": {
                variant: sha256_bytes(content.encode("utf-8"))
                for variant, content in transformed["contents"].items()
            },
            "alpha_mapping": transformed["alpha_mapping"],
            "dead_identifier": transformed["dead_identifier"],
            "compilation": transformed["compilation"],
            "truth": {
                "original_to_alpha": "semantic_equivalence_and_node_correspondence",
                "alpha_to_alpha_dead": (
                    "semantic_equivalence_with_known_irrelevant_nodes"
                ),
            },
        })

    transform_manifest = {
        "benchmark": "frozen correctly-predicted GCJ negative-pair transformations",
        "samples": len(transformation_records),
        "variants_per_sample": ["original", "alpha", "alpha_dead"],
        "semantic_oracle": (
            "consistent identifier alpha-renaming plus an unreachable-at-runtime "
            "zero-valued guarded empty print"
        ),
        "verification": "all original and transformed programs compile in isolation",
        "validation_manifest": str(args.validation_manifest.resolve()),
        "validation_manifest_sha256": sha256_bytes(
            args.validation_manifest.read_bytes()
        ),
        "prediction_records": str(args.prediction_records.resolve()),
        "prediction_records_sha256": sha256_bytes(
            args.prediction_records.read_bytes()
        ),
        "test_used": False,
        "records": transformation_records,
        "rejected_candidates": rejected,
    }
    transform_path = args.output_dir / "transformation_manifest.json"
    transform_path.write_text(
        json.dumps(transform_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    pair_manifest = {
        "benchmark": "frozen correctly-predicted GCJ negative pairs",
        "pairs": len(selected_pairs),
        "source_programs": len(used),
        "source_reuse": False,
        "label": 0,
        "selection": (
            "frozen manifest order; correct nonclone prediction; greedy source "
            "disjointness; both sources pass all three compilation checks"
        ),
        "test_used": False,
        "records": [
            {
                **row,
                "left_sample_id": source_to_sample[row["left_source"]],
                "right_sample_id": source_to_sample[row["right_source"]],
            } for row in selected_pairs
        ],
    }
    pair_path = args.output_dir / "selected_negative_pairs.json"
    pair_path.write_text(
        json.dumps(pair_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.output_dir),
        "pairs": len(selected_pairs),
        "programs": len(used),
        "rejected_candidates": len(rejected),
        "generated_java_files": len(transformation_records) * 3,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
