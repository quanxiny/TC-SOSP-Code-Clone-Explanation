#!/usr/bin/env python3
"""Screen rebuilt transformed negative pairs before explanation evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.configlib import resolve_config, resolve_workspace_path  # noqa: E402
from scripts.contrastive_runner import BASELINE_ROOT  # noqa: E402
from scripts.explanation_runner import load_checkpoint_model, predict  # noqa: E402

if str(BASELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(BASELINE_ROOT))

from reproduce_gcj_batched import load_graphs, set_seed  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "experiments" / "C14_gcj_negative_pair_transformation_truth.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = resolve_config(args.config)
    set_seed(int(config["seed"]))
    device = torch.device(args.device)
    truth_path = resolve_workspace_path(config["truth"]["manifest"])
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    required = sorted({
        filename for row in truth["records"]
        for field in ("base_files", "alpha_files", "dead_files")
        for filename in row[field]
    })
    previous = Path.cwd()
    try:
        os.chdir(str(BASELINE_ROOT))
        graphs = load_graphs(
            required,
            resolve_workspace_path(config["paths"]["source_dir"]),
            resolve_workspace_path(config["paths"]["vector_dir"]),
            device, int(config["model"]["hidden"]),
        )
    finally:
        os.chdir(str(previous))
    model = load_checkpoint_model(config, device)
    rows = []
    with torch.no_grad():
        for truth_row in truth["records"]:
            variants = {}
            for field in ("base_files", "alpha_files", "dead_files"):
                left, right = truth_row[field]
                output = predict(model, graphs[left], graphs[right], True)
                variants[field] = {
                    "prediction": int(output.argmax()),
                    "nonclone_probability": float(output[0]),
                }
            rows.append({
                "pair_id": truth_row["pair_id"],
                "original_validation_pair_index": truth_row.get(
                    "original_validation_pair_index"
                ),
                "variants": variants,
                "rebuilt_base_correct_nonclone": (
                    variants["base_files"]["prediction"] == 0
                ),
                "all_variants_nonclone": all(
                    row["prediction"] == 0 for row in variants.values()
                ),
                "prediction_invariant": len({
                    row["prediction"] for row in variants.values()
                }) == 1,
            })
    output = args.output or truth_path.parent / "rebuilt_prediction_screen.json"
    result = {
        "scope": "validation-only pre-explanation eligibility screen",
        "truth_manifest": str(truth_path.resolve()),
        "truth_manifest_sha256": hashlib.sha256(truth_path.read_bytes()).hexdigest(),
        "checkpoint": str(resolve_workspace_path(config["predictor"]["checkpoint"])),
        "pairs": len(rows),
        "rebuilt_base_correct_nonclone": sum(
            row["rebuilt_base_correct_nonclone"] for row in rows
        ),
        "all_variants_nonclone": sum(row["all_variants_nonclone"] for row in rows),
        "prediction_invariant": sum(row["prediction_invariant"] for row in rows),
        "rows": rows,
        "test_used": False,
    }
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        key: result[key] for key in (
            "pairs", "rebuilt_base_correct_nonclone",
            "all_variants_nonclone", "prediction_invariant"
        )
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
