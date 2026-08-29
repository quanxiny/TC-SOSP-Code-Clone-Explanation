#!/usr/bin/env python3
"""Unified, guarded entry point for the research experiment family."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.configlib import apply_overrides, config_digest, resolve_config, validate_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dataset")
    parser.add_argument("--graph_type")
    parser.add_argument("--split")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--device")
    parser.add_argument("--loss")
    parser.add_argument("--output_dir")
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--train_limit", type=int)
    parser.add_argument("--epochs_per_task", type=int)
    parser.add_argument("--task_train_limit", type=int)
    parser.add_argument("--task_limit", type=int)
    parser.add_argument("--task_order", help="Comma-separated continual task order, e.g. T3,T2,T1")
    parser.add_argument("--memory_budget_mb", type=float)
    parser.add_argument("--sample_pairs", type=int)
    parser.add_argument("--lambda_aux", type=float)
    parser.add_argument("--margin", type=float)
    parser.add_argument("--temperature", type=float)
    resume = parser.add_mutually_exclusive_group()
    resume.add_argument("--resume", dest="resume", action="store_true")
    resume.add_argument("--no-resume", dest="resume", action="store_false")
    parser.set_defaults(resume=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = resolve_config(args.config)
    config = apply_overrides(
        config,
        dataset=args.dataset,
        graph_type=args.graph_type,
        split=args.split,
        seed=args.seed,
        device=args.device,
        loss=args.loss,
        output_dir=args.output_dir,
        resume=args.resume,
    )
    if args.epochs is not None:
        config.setdefault("training", {})["epochs"] = args.epochs
    if args.train_limit is not None:
        config.setdefault("training", {})["train_limit"] = args.train_limit
    if args.epochs_per_task is not None:
        config.setdefault("training", {})["epochs_per_task"] = args.epochs_per_task
    if args.task_train_limit is not None:
        config.setdefault("training", {})["task_train_limit"] = args.task_train_limit
    if args.task_limit is not None:
        config.setdefault("training", {})["task_limit"] = args.task_limit
    if args.task_order is not None:
        order = [item.strip() for item in args.task_order.split(",") if item.strip()]
        if len(order) != len(set(order)) or not order:
            parser.error("--task_order must contain unique comma-separated task names")
        config.setdefault("stream", {})["pilot_order"] = order
        config["stream"]["ordering_claim"] = "command_line_fixed_order_for_order_sensitivity"
    if args.memory_budget_mb is not None:
        config.setdefault("strategy", {})["memory_budget_mb"] = args.memory_budget_mb
    if args.sample_pairs is not None:
        config.setdefault("explanation", {})["sample_pairs"] = args.sample_pairs
    if args.lambda_aux is not None:
        components = config.setdefault("loss", {}).setdefault("components", {})
        auxiliary_names = [name for name in components if name != "focal"]
        if len(auxiliary_names) != 1:
            parser.error("--lambda_aux requires exactly one non-focal loss component")
        components[auxiliary_names[0]] = args.lambda_aux
    if args.margin is not None:
        config.setdefault("loss", {})["margin"] = args.margin
    if args.temperature is not None:
        config.setdefault("loss", {})["temperature"] = args.temperature
    errors = validate_config(config, args.config)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    resolved = {
        "config_sha256": config_digest(config),
        "resolved_config": config,
    }
    print(json.dumps(resolved, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0
    if config["stage"] == "contrastive" and config["experiment_id"] == "A0_focal":
        from scripts.contrastive_runner import run
        return run(config)
    if config["stage"] == "explanation" and config["experiment_id"] in {
        "C0_symmetric_explanation", "C1_semantic_optimal_subgraph_pair",
        "C2_semantic_optimal_subgraph_pair_budget10",
        "C3_semantic_optimal_subgraph_pair_budget30",
        "C4_shuffled_semantic_optimal_subgraph_pair",
        "C5_optimal_subgraph_checkpoint_seed42",
        "C6_optimal_subgraph_checkpoint_seed123",
        "C7_optimal_subgraph_checkpoint_seed2024",
        "C9_natural_validation_strong_baselines",
        "C11_semantic_optimal_objective_lambda0",
        "C12_semantic_optimal_objective_lambda05",
        "C13_semantic_optimal_objective_lambda2",
        "C16_gnnexplainer_random_init_seed42_reference",
        "C17_stochastic_explainers_seed123",
        "C18_stochastic_explainers_seed2024",
    }:
        from scripts.explanation_runner import run
        return run(config)
    if config["stage"] == "explanation" and config["experiment_id"] in {
        "C8_transformation_truth_strong_baselines",
        "C10_codenet_transformation_truth_strong_baselines",
    }:
        from scripts.truth_explanation_runner import run
        return run(config)
    if config["stage"] == "explanation" and config["experiment_id"] in {
        "C15_codenet_negative_pair_transformation_truth",
    }:
        from scripts.negative_pair_truth_runner import run
        return run(config)
    print("No execution adapter for this stage/status; use --dry-run.", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
