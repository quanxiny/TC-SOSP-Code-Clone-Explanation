#!/usr/bin/env python3
"""Evaluate parameter-free order averaging on a sealed-validation checkpoint."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch

from scripts.configlib import (
    RESEARCH_ROOT,
    config_digest,
    resolve_config,
    resolve_workspace_path,
)
from scripts.contrastive_runner import (
    BASELINE_ROOT,
    ExactSymmetricCodeCloneDetection,
    runner_args,
)
from myModels.GAT_Edgepool_clone_detection import CodeCloneDetection
from reproduce_gcj import count_parameters
from reproduce_gcj_batched import graph_paths, load_graphs, metrics_for_model, set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--source-summary", type=Path)
    source.add_argument("--config", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--mode", choices=("ordered", "exact_symmetric"), default="exact_symmetric")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    return parser.parse_args()


def main() -> int:
    args_cli = parse_args()
    if args_cli.source_summary is not None:
        source_path = args_cli.source_summary.expanduser().resolve()
        source = json.loads(source_path.read_text(encoding="utf-8"))
        config = source["configuration"]
        if source.get("test_metrics") is not None:
            raise RuntimeError("posthoc pilot requires a validation-selected source checkpoint")
        checkpoint_path = Path(source["selected_checkpoint"]).resolve()
        source_digest = source["config_sha256"]
        source_description = {"source_summary": str(source_path)}
        selection_policy = "reuse_source_macro_f1_selected_checkpoint"
    else:
        if args_cli.checkpoint is None:
            raise RuntimeError("--config requires --checkpoint")
        config_path = args_cli.config.expanduser().resolve()
        config = resolve_config(config_path)
        checkpoint_path = args_cli.checkpoint.expanduser().resolve()
        source_digest = config_digest(config)
        source_description = {"source_config": str(config_path)}
        selection_policy = "externally_recorded_validation_selected_checkpoint"
    output_dir = args_cli.output_dir
    if not output_dir.is_absolute():
        output_dir = (RESEARCH_ROOT / output_dir).resolve()
    artifact_root = (RESEARCH_ROOT / "artifacts").resolve()
    if artifact_root not in output_dir.parents:
        raise RuntimeError("output must stay under research artifacts/")
    output_dir.mkdir(parents=True, exist_ok=True)

    set_seed(int(config["seed"]))
    device = torch.device(args_cli.device)
    runner = runner_args(config)
    validation_path = resolve_workspace_path(config["paths"]["validation_split"])
    validation_lines = validation_path.read_text(encoding="utf-8").splitlines(True)
    required = graph_paths(validation_lines)
    previous_directory = Path.cwd()
    try:
        os.chdir(str(BASELINE_ROOT))
        graphs = load_graphs(
            required,
            resolve_workspace_path(config["paths"]["source_dir"]),
            resolve_workspace_path(config["paths"]["vector_dir"]),
            device,
            runner.hidden,
        )
    finally:
        os.chdir(str(previous_directory))

    model_type = (
        ExactSymmetricCodeCloneDetection
        if args_cli.mode == "exact_symmetric"
        else CodeCloneDetection
    )
    model = model_type(
        runner.num_layers, runner.hidden, runner.nheads, runner.num_classes,
        runner.dropout, runner.alpha, True,
    ).to(device)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = checkpoint["model"] if "model" in checkpoint else checkpoint
    model.load_state_dict(state_dict)
    model.eval()
    predictions_path = output_dir / "validation_predictions.jsonl"
    metrics = metrics_for_model(
        runner, model, validation_lines, graphs,
        "{} validation".format(args_cli.mode), predictions_path,
    )
    result = {
        "experiment_id": (
            "A4s_posthoc_exact_symmetry"
            if args_cli.mode == "exact_symmetric"
            else "A0_ordered_checkpoint_evaluation"
        ),
        **source_description,
        "source_checkpoint": str(checkpoint_path),
        "source_config_sha256": source_digest,
        "selection_policy": selection_policy,
        "evaluation_split": "validation",
        "test_policy": "sealed_during_pilot",
        "symmetrization": (
            "mean_probability_over_both_orders"
            if args_cli.mode == "exact_symmetric"
            else "none_ordered_released_detector"
        ),
        "model_parameter_count": count_parameters(model),
        "metrics": metrics,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
