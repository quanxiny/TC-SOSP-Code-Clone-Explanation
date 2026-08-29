#!/usr/bin/env python3
"""Attach CFG-node mappings to the frozen natural negative-pair selection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = (
    ROOT / "external_data" / "explanation_truth"
    / "gcj_frozen_negative_pair_transformations"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    return parser.parse_args()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = parse_args()
    selection_path = args.root / "selected_negative_pairs.json"
    truth_path = args.root / "explanation_truth_manifest.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    by_id: Dict[str, Dict[str, Any]] = {
        row["sample_id"]: row for row in truth["records"]
    }
    rows = []
    used = set()
    for selected in selection["records"]:
        left, right = (
            by_id[selected["left_sample_id"]],
            by_id[selected["right_sample_id"]],
        )
        if selected["frozen_prediction"] != 0:
            raise RuntimeError("selection contains a non-nonclone prediction")
        if left["sample_id"] in used or right["sample_id"] in used:
            raise RuntimeError("a source program is reused")
        used.update((left["sample_id"], right["sample_id"]))
        rows.append({
            "pair_id": "fn{:03d}_{}_{}".format(
                int(selected["pair_index"]), left["sample_id"], right["sample_id"]
            ),
            "original_validation_pair_index": int(selected["pair_index"]),
            "original_validation_line": selected["line"],
            "label": 0,
            "frozen_prediction": 0,
            "frozen_base_target_probability": selected[
                "frozen_base_target_probability"
            ],
            "left_sample_id": left["sample_id"],
            "right_sample_id": right["sample_id"],
            "base_files": [left["files"]["original"], right["files"]["original"]],
            "alpha_files": [left["files"]["alpha"], right["files"]["alpha"]],
            "dead_files": [
                left["files"]["alpha_dead"], right["files"]["alpha_dead"]
            ],
            "base_to_alpha_mapping": [
                left["original_to_alpha_node_mapping"],
                right["original_to_alpha_node_mapping"],
            ],
            "alpha_to_dead_mapping": [
                left["alpha_to_alpha_dead_node_mapping"],
                right["alpha_to_alpha_dead_node_mapping"],
            ],
            "dead_known_irrelevant_nodes": [
                left["alpha_dead_known_irrelevant_nodes"],
                right["alpha_dead_known_irrelevant_nodes"],
            ],
        })
    result = {
        "benchmark": "frozen correctly-predicted GCJ negative-pair metamorphic truth",
        "pairs": len(rows),
        "source_programs": len(used),
        "label": 0,
        "base_prediction_correct_by_construction": True,
        "source_reuse": False,
        "truth_axes": [
            "sidewise explanation correspondence under bilateral alpha-renaming",
            "sidewise correspondence after bilateral dead-code insertion",
            "rejection of known irrelevant dead-code nodes on both graphs",
            "nonclone prediction invariance under semantic-preserving transformations",
        ],
        "selected_pair_manifest": str(selection_path.resolve()),
        "selected_pair_manifest_sha256": digest(selection_path),
        "source_truth_manifest": str(truth_path.resolve()),
        "source_truth_manifest_sha256": digest(truth_path),
        "test_used": False,
        "records": rows,
    }
    output = args.root / "negative_pair_truth_manifest.json"
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "output": str(output), "pairs": len(rows), "unique_programs": len(used),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
