#!/usr/bin/env python3
"""Export deterministic qualitative cases for the optimal subgraph-pair pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD_DIR = (
    ROOT / "artifacts" / "pilots" / "C1_semantic_optimal_subgraph_pair_seed42"
)
DEFAULT_CODE_JSON = Path(
    "../TinyPDG-DataPreprocessingVersion/"
    "artifacts/gcj_cfg_extract/outPut_cfg/codeJson"
)
DEFAULT_OUTPUT = (
    ROOT / "artifacts" / "explanation_cases"
    / "C1_semantic_optimal_subgraph_cases.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", type=Path, default=DEFAULT_RECORD_DIR)
    parser.add_argument("--code-json-dir", type=Path, default=DEFAULT_CODE_JSON)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def graph_source(code_json_dir: Path, graph_name: str) -> Dict[str, Any]:
    path = code_json_dir / f"{Path(graph_name).name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = {int(index): text.strip() for index, text in data["jsonNodes"].items()}
    return {"path": str(path), "nodes": nodes, "edges": data["jsonEdges"]}


def main() -> int:
    args = parse_args()
    gradient_path = args.record_dir / "symmetric_grad_x_input_records.jsonl"
    semantic_path = args.record_dir / "symmetric_semantic_optimal_pair_records.jsonl"
    gradient = read_jsonl(gradient_path)
    semantic = read_jsonl(semantic_path)
    gradient_by_pair = {int(record["pair_index"]): record for record in gradient}
    semantic_by_pair = {int(record["pair_index"]): record for record in semantic}
    if set(gradient_by_pair) != set(semantic_by_pair):
        raise RuntimeError("gradient and semantic records do not cover identical pairs")

    candidates = []
    for pair_index in sorted(semantic_by_pair):
        baseline = gradient_by_pair[pair_index]
        candidate = semantic_by_pair[pair_index]
        if (
            candidate["prediction"] != candidate["label"]
            or candidate["selected_candidate"] == "gradient"
        ):
            continue
        candidates.append({
            "record": candidate,
            "necessity_delta": (
                candidate["necessity_drop"] - baseline["necessity_drop"]
            ),
            "absolute_sufficiency_improvement": (
                abs(baseline["sufficiency_gap"])
                - abs(candidate["sufficiency_gap"])
            ),
        })

    chosen = []
    for label in (0, 1):
        subset = [item for item in candidates if item["record"]["label"] == label]
        values = np.asarray([item["necessity_delta"] for item in subset], dtype=float)
        median = float(np.median(values))
        representative = min(
            subset,
            key=lambda item: (
                abs(item["necessity_delta"] - median),
                item["record"]["pair_index"],
            ),
        )
        strongest = max(
            subset,
            key=lambda item: (
                item["necessity_delta"], -item["record"]["pair_index"]
            ),
        )
        chosen.extend([
            (f"label_{label}_median_necessity_gain", representative),
            (f"label_{label}_maximum_necessity_gain", strongest),
        ])

    exported = []
    for role, item in chosen:
        record = item["record"]
        left = graph_source(args.code_json_dir, record["left"])
        right = graph_source(args.code_json_dir, record["right"])
        if len(left["nodes"]) != record["left_nodes"]:
            raise RuntimeError(f"left node count mismatch: {record['left']}")
        if len(right["nodes"]) != record["right_nodes"]:
            raise RuntimeError(f"right node count mismatch: {record['right']}")
        relations = []
        for relation in record["node_relations"]:
            relations.append({
                **relation,
                "left_statement": left["nodes"][int(relation["left_node"])],
                "right_statement": right["nodes"][int(relation["right_node"])],
            })
        exported.append({
            "selection_role": role,
            "selection_rule": (
                "correctly predicted, non-gradient candidate; deterministic median or "
                "maximum necessity improvement within the true label subgroup"
            ),
            "pair_index": record["pair_index"],
            "label": record["label"],
            "relation_interpretation": (
                "contrastive unmatched statements" if record["label"] == 0
                else "common semantic statements"
            ),
            "left_graph": record["left"],
            "right_graph": record["right"],
            "left_code_json": left["path"],
            "right_code_json": right["path"],
            "selected_candidate": record["selected_candidate"],
            "base_target_probability": record["base_target_probability"],
            "necessity_drop": record["necessity_drop"],
            "necessity_delta_over_symmetric_gradient": item["necessity_delta"],
            "absolute_sufficiency_gap": abs(record["sufficiency_gap"]),
            "absolute_sufficiency_improvement_over_symmetric_gradient": item[
                "absolute_sufficiency_improvement"
            ],
            "semantic_pair_quality": record["semantic_pair_quality"],
            "induced_cfg_coverage": record["induced_cfg_coverage"],
            "left_selected_statements": [
                {"node": index, "statement": left["nodes"][index]}
                for index in record["left_selected"]
            ],
            "right_selected_statements": [
                {"node": index, "statement": right["nodes"][index]}
                for index in record["right_selected"]
            ],
            "paired_relations": relations,
        })

    output = {
        "protocol": {
            "purpose": "illustrative qualitative audit, not an additional effect estimate",
            "split": "validation_only",
            "cases": len(exported),
            "test_metrics": None,
            "selection_is_cherry_pick_safe": False,
            "note": (
                "maximum-gain cases are deliberately best cases; median-gain cases are "
                "included to show representative behavior. Neither substitutes for the "
                "100-pair quantitative result."
            ),
        },
        "record_inputs": {
            "gradient_sha256": hashlib.sha256(gradient_path.read_bytes()).hexdigest(),
            "semantic_sha256": hashlib.sha256(semantic_path.read_bytes()).hexdigest(),
        },
        "cases": exported,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(args.output)
    print(f"sha256={hashlib.sha256(args.output.read_bytes()).hexdigest()}")
    for case in exported:
        print(
            case["selection_role"], case["pair_index"], case["selected_candidate"],
            f"necessity_delta={case['necessity_delta_over_symmetric_gradient']:.6f}",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
