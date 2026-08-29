#!/usr/bin/env python3
"""Contrastive and symmetry pilots built on the reproduced graph encoder."""

from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm

from .configlib import RESEARCH_ROOT, config_digest, resolve_workspace_path


BASELINE_ROOT = Path(
    os.environ.get(
        "CODEGRAPH4CC_BASELINE_ROOT",
        str(RESEARCH_ROOT.parent / "CodeGraph4CCDetector"),
    )
).expanduser().resolve()
if str(BASELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(BASELINE_ROOT))

from myModels.GAT_Edgepool_clone_detection import CodeCloneDetection  # noqa: E402
from reproduce_gcj import FocalLoss, count_parameters, normalize_label  # noqa: E402
from reproduce_gcj_batched import (  # noqa: E402
    encode_paths,
    graph_paths,
    load_graphs,
    metrics_for_model,
    save_training_state,
    set_seed,
)


class GraphProjection(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, output_dim),
            nn.ReLU(),
            nn.Linear(output_dim, output_dim),
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        return F.normalize(self.network(values), dim=-1)


class PairSupConProjection(nn.Module):
    def __init__(self, graph_dim: int, output_dim: int):
        super().__init__()
        self.graph_projection = GraphProjection(graph_dim, output_dim)
        self.pair_projection = nn.Sequential(
            nn.Linear(2 * output_dim, output_dim),
            nn.ReLU(),
            nn.Linear(output_dim, output_dim),
        )

    def forward(self, first: torch.Tensor, second: torch.Tensor) -> torch.Tensor:
        first = self.graph_projection(first)
        second = self.graph_projection(second)
        symmetric_pair = torch.cat((torch.abs(first - second), first * second), dim=-1)
        return F.normalize(self.pair_projection(symmetric_pair), dim=-1)


class ExactSymmetricCodeCloneDetection(CodeCloneDetection):
    """Parameter-free hard symmetrization of the released ordered detector."""

    def detect_embeddings(self, first: torch.Tensor,
                          second: torch.Tensor) -> torch.Tensor:
        forward = super().detect_embeddings(first, second)
        backward = super().detect_embeddings(second, first)
        return 0.5 * (forward + backward)


def pair_contrastive_loss(first: torch.Tensor, second: torch.Tensor,
                          labels: torch.Tensor, margin: float) -> torch.Tensor:
    distances = torch.norm(first - second, p=2, dim=-1)
    positives = labels * distances.square()
    negatives = (1.0 - labels) * torch.clamp(margin - distances, min=0).square()
    return (positives + negatives).mean()


def swap_js_loss(first_probabilities: torch.Tensor,
                 swapped_probabilities: torch.Tensor) -> torch.Tensor:
    epsilon = torch.finfo(first_probabilities.dtype).eps
    first = first_probabilities.clamp_min(epsilon)
    swapped = swapped_probabilities.clamp_min(epsilon)
    midpoint = 0.5 * (first + swapped)
    first_kl = (first * (first.log() - midpoint.log())).sum(dim=1)
    swapped_kl = (swapped * (swapped.log() - midpoint.log())).sum(dim=1)
    return 0.5 * (first_kl + swapped_kl).mean()


def supervised_contrastive_loss(features: torch.Tensor, labels: torch.Tensor,
                                temperature: float,
                                denominator_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
    count = features.size(0)
    if count < 2:
        return features.sum() * 0.0
    device = features.device
    identity = torch.eye(count, dtype=torch.bool, device=device)
    allowed = ~identity
    if denominator_mask is not None:
        allowed &= denominator_mask
    positive = labels[:, None].eq(labels[None, :]) & allowed
    logits = features @ features.transpose(0, 1) / temperature
    logits = logits - logits.max(dim=1, keepdim=True).values.detach()
    exp_logits = torch.exp(logits) * allowed.float()
    log_prob = logits - torch.log(exp_logits.sum(dim=1, keepdim=True).clamp_min(1e-12))
    positive_count = positive.sum(dim=1)
    valid = positive_count > 0
    if not valid.any():
        return features.sum() * 0.0
    mean_positive_log_prob = (
        (positive.float() * log_prob).sum(dim=1) / positive_count.clamp_min(1)
    )
    return -mean_positive_log_prob[valid].mean()


def shared_fragment_denominator_mask(fields: List[List[str]], device: torch.device) -> torch.Tensor:
    count = len(fields)
    allowed = torch.ones((count, count), dtype=torch.bool, device=device)
    fragments = [set(item[:2]) for item in fields]
    labels = [normalize_label(item[2]) for item in fields]
    for left in range(count):
        for right in range(left + 1, count):
            if labels[left] != labels[right] and fragments[left] & fragments[right]:
                allowed[left, right] = False
                allowed[right, left] = False
    return allowed


def read_lines(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines(True)


def runner_args(config: Dict[str, Any]) -> SimpleNamespace:
    training = config["training"]
    model = config["model"]
    return SimpleNamespace(
        amp=bool(training.get("amp", False)),
        graph_batch_size=int(training["graph_batch_size"]),
        eval_pair_batch_size=15000,
        num_layers=4,
        hidden=int(model["hidden"]),
        nheads=int(model["gat_heads"]),
        num_classes=2,
        dropout=float(model["dropout"]),
        alpha=0.2,
    )


def build_auxiliary(config: Dict[str, Any], graph_dim: int,
                    device: torch.device) -> Optional[nn.Module]:
    name = config["loss"]["name"]
    if name in {"focal", "focal_plus_swap_js"}:
        return None
    output_dim = int(config.get("projection", {}).get("output_dim", 128))
    if name == "focal_plus_pair_contrastive":
        return GraphProjection(graph_dim, output_dim).to(device)
    if name == "focal_plus_supervised_contrastive":
        return PairSupConProjection(graph_dim, output_dim).to(device)
    raise ValueError("unsupported pilot loss: {}".format(name))


def auxiliary_loss(config: Dict[str, Any], model: nn.Module,
                   auxiliary: Optional[nn.Module], output: torch.Tensor,
                   first: torch.Tensor, second: torch.Tensor,
                   labels: torch.Tensor, fields: List[List[str]]) -> torch.Tensor:
    name = config["loss"]["name"]
    if name == "focal":
        return first.sum() * 0.0
    if name == "focal_plus_swap_js":
        swapped_output = model.detect_embeddings(second, first)
        return swap_js_loss(output, swapped_output)
    if name == "focal_plus_pair_contrastive":
        projected_first = auxiliary(first)
        projected_second = auxiliary(second)
        return pair_contrastive_loss(
            projected_first, projected_second, labels,
            float(config["loss"]["margin"]),
        )
    pair_features = auxiliary(first, second)
    denominator_mask = shared_fragment_denominator_mask(fields, first.device)
    return supervised_contrastive_loss(
        pair_features, labels.long(), float(config["loss"]["temperature"]),
        denominator_mask,
    )


def rng_state() -> Dict[str, Any]:
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
        "cuda": torch.cuda.get_rng_state_all(),
    }


def restore_rng_state(state: Dict[str, Any]) -> None:
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    # map_location=device may move serialized RNG byte tensors onto CUDA.
    torch.set_rng_state(state["torch"].cpu())
    torch.cuda.set_rng_state_all([value.cpu() for value in state["cuda"]])


def run(config: Dict[str, Any]) -> int:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the reproduced encoder")
    identifier = config["experiment_id"]
    if identifier not in {
        "A0_focal", "A1_pair_contrastive", "A2_supcon", "A4a_swap_consistency",
        "A4s_exact_symmetry", "B2_task_oracle_T1", "B2_task_oracle_T2",
        "B2_task_oracle_T3",
    }:
        raise ValueError("pilot runner only supports A0/A1/A2/A4a")
    digest = config_digest(config)
    args = runner_args(config)
    output_dir = resolve_workspace_path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_path = output_dir / "resolved_config.json"
    if resolved_path.exists():
        previous = json.loads(resolved_path.read_text(encoding="utf-8"))
        if previous["config_sha256"] != digest:
            raise RuntimeError("refusing resume/overwrite with a different config hash")
    else:
        resolved_path.write_text(json.dumps({
            "config_sha256": digest,
            "config": config,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    set_seed(int(config["seed"]))
    torch.backends.cuda.matmul.allow_tf32 = bool(config["training"].get("tf32", True))
    torch.backends.cudnn.allow_tf32 = bool(config["training"].get("tf32", True))
    device = torch.device(config["device"])
    paths = config["paths"]
    manifest = config.get("sampling", {}).get("manifest")
    train_path = resolve_workspace_path(manifest or paths["train_split"])
    validation_path = resolve_workspace_path(paths["validation_split"])
    train_lines = read_lines(train_path)
    train_limit = int(config["training"].get("train_limit", 0))
    if train_limit > 0:
        train_lines = train_lines[:train_limit]
    validation_lines = read_lines(validation_path)
    required = graph_paths(train_lines + validation_lines)
    previous_directory = Path.cwd()
    try:
        os.chdir(str(BASELINE_ROOT))
        graphs = load_graphs(
            required,
            resolve_workspace_path(paths["source_dir"]),
            resolve_workspace_path(paths["vector_dir"]),
            device,
            args.hidden,
        )
    finally:
        os.chdir(str(previous_directory))

    model_type = (
        ExactSymmetricCodeCloneDetection
        if identifier == "A4s_exact_symmetry"
        else CodeCloneDetection
    )
    model = model_type(
        args.num_layers, args.hidden, args.nheads, args.num_classes,
        args.dropout, args.alpha, True,
    ).to(device)
    graph_dim = args.hidden * (1 + args.nheads * 2 + 2)
    auxiliary = build_auxiliary(config, graph_dim, device)
    parameters = list(model.parameters())
    if auxiliary is not None:
        parameters.extend(auxiliary.parameters())
    optimizer = torch.optim.Adam(
        parameters,
        lr=float(config["training"]["learning_rate"]),
        weight_decay=float(config["training"]["weight_decay"]),
    )
    scaler = torch.cuda.amp.GradScaler(enabled=args.amp)
    criterion = FocalLoss(
        alpha=float(config["loss"].get("alpha", 1.0)),
        gamma=float(config["loss"].get("gamma", 2.0)),
    ).to(device)
    history = []
    best_f1 = -1.0
    best_checkpoint = None
    start_epoch = 0
    early_config = config["training"].get("early_stopping", {})
    early_enabled = bool(early_config.get("enabled", False))
    early_patience = int(early_config.get("patience", 0))
    early_min_delta = float(early_config.get("min_delta", 0.0))
    early_min_epochs = int(early_config.get("min_epochs", 0))
    early_reference = -1.0
    epochs_without_meaningful_improvement = 0
    stopped_early = False
    latest_path = output_dir / "latest_training.pt"
    if config.get("resume") and latest_path.is_file():
        state = torch.load(latest_path, map_location=device)
        if state["config_sha256"] != digest:
            raise RuntimeError("checkpoint config hash mismatch")
        model.load_state_dict(state["model"])
        if auxiliary is not None:
            auxiliary.load_state_dict(state["auxiliary"])
        optimizer.load_state_dict(state["optimizer"])
        scaler.load_state_dict(state["scaler"])
        history = state["history"]
        best_f1 = state["best_f1"]
        best_checkpoint = Path(state["best_checkpoint"]) if state["best_checkpoint"] else None
        start_epoch = int(state["epoch"])
        early_reference = float(state.get("early_reference", -1.0))
        epochs_without_meaningful_improvement = int(
            state.get("epochs_without_meaningful_improvement", 0)
        )
        if early_enabled and "early_reference" not in state:
            for previous in history:
                previous_f1 = float(previous["validation"]["f1_macro"])
                if previous_f1 > early_reference + early_min_delta:
                    early_reference = previous_f1
                    epochs_without_meaningful_improvement = 0
                elif int(previous["epoch"]) >= early_min_epochs:
                    epochs_without_meaningful_improvement += 1
        restore_rng_state(state["rng_state"])
        print("resumed at epoch", start_epoch)

    batch_size = int(config["training"]["batch_size"])
    max_epochs = int(config["training"]["epochs"])
    components = config["loss"].get("components", {})
    auxiliary_weight = sum(
        float(weight) for name, weight in components.items() if name != "focal"
    )
    for epoch in range(start_epoch, max_epochs):
        model.train()
        if auxiliary is not None:
            auxiliary.train()
        started = time.perf_counter()
        running_total = 0.0
        running_focal = 0.0
        running_auxiliary = 0.0
        processed = 0
        correct = 0
        batches = range(0, len(train_lines), batch_size)
        progress = tqdm(batches, desc="{} epoch {}/{}".format(identifier, epoch + 1, max_epochs))
        for start in progress:
            fields = [line.split() for line in train_lines[start:start + batch_size]]
            optimizer.zero_grad()
            graph_sequence = [item[0] for item in fields] + [item[1] for item in fields]
            with torch.cuda.amp.autocast(enabled=args.amp):
                encoded = encode_paths(model, graph_sequence, graphs, args.graph_batch_size, None)
                pair_count = len(fields)
                first, second = encoded[:pair_count], encoded[pair_count:]
                output = model.detect_embeddings(first, second)
                label_values = [normalize_label(item[2]) for item in fields]
                labels = torch.tensor(label_values, dtype=torch.float32, device=device)
                targets = torch.stack((1.0 - labels, labels), dim=1)
                focal = criterion(output.float(), targets)
                contrastive = auxiliary_loss(
                    config, model, auxiliary, output, first, second, labels, fields
                )
                total_mean = focal + auxiliary_weight * contrastive
                loss = total_mean * pair_count
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            running_total += total_mean.item() * pair_count
            running_focal += focal.item() * pair_count
            running_auxiliary += contrastive.item() * pair_count
            processed += pair_count
            correct += sum(
                prediction == label
                for prediction, label in zip(output.argmax(dim=1).tolist(), label_values)
            )
            progress.set_postfix(
                loss=running_total / processed,
                focal=running_focal / processed,
                auxiliary=running_auxiliary / processed,
                accuracy=correct / processed,
            )

        model.eval()
        if auxiliary is not None:
            auxiliary.eval()
        validation = metrics_for_model(
            args, model, validation_lines, graphs,
            "{} validation epoch {}".format(identifier, epoch + 1),
        )
        checkpoint = output_dir / "epoch_{:03d}.pt".format(epoch + 1)
        torch.save({
            "model": model.state_dict(),
            "auxiliary": auxiliary.state_dict() if auxiliary is not None else None,
            "epoch": epoch + 1,
            "config_sha256": digest,
        }, checkpoint)
        if validation["f1_macro"] > best_f1:
            best_f1 = validation["f1_macro"]
            best_checkpoint = checkpoint
        if validation["f1_macro"] > early_reference + early_min_delta:
            early_reference = validation["f1_macro"]
            epochs_without_meaningful_improvement = 0
        elif epoch + 1 >= early_min_epochs:
            epochs_without_meaningful_improvement += 1
        result = {
            "epoch": epoch + 1,
            "loss": running_total / processed,
            "focal_loss": running_focal / processed,
            "auxiliary_loss": running_auxiliary / processed,
            "accuracy": correct / processed,
            "processed_pairs": processed,
            "seconds": time.perf_counter() - started,
            "validation": validation,
            "checkpoint": str(checkpoint),
            "epochs_without_meaningful_improvement": epochs_without_meaningful_improvement,
        }
        history.append(result)
        print(json.dumps(result, ensure_ascii=False))
        save_training_state(latest_path, {
            "config_sha256": digest,
            "model": model.state_dict(),
            "auxiliary": auxiliary.state_dict() if auxiliary is not None else None,
            "optimizer": optimizer.state_dict(),
            "scaler": scaler.state_dict(),
            "epoch": epoch + 1,
            "history": history,
            "best_f1": best_f1,
            "best_checkpoint": str(best_checkpoint),
            "early_reference": early_reference,
            "epochs_without_meaningful_improvement": epochs_without_meaningful_improvement,
            "rng_state": rng_state(),
        })
        if (
            early_enabled
            and early_patience > 0
            and epoch + 1 >= early_min_epochs
            and epochs_without_meaningful_improvement >= early_patience
        ):
            stopped_early = True
            print("early stopping at epoch {} after {} non-improving epochs".format(
                epoch + 1, epochs_without_meaningful_improvement
            ))
            break

    selected = torch.load(best_checkpoint, map_location=device)
    model.load_state_dict(selected["model"])
    if auxiliary is not None:
        auxiliary.load_state_dict(selected["auxiliary"])
    final_validation = metrics_for_model(
        args, model, validation_lines, graphs, "selected validation",
        output_dir / "validation_predictions.jsonl",
    )
    summary = {
        "config_sha256": digest,
        "configuration": config,
        "environment": {
            "torch": torch.__version__,
            "cuda_build": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(device),
        },
        "model_parameter_count": count_parameters(model),
        "auxiliary_parameter_count": sum(
            parameter.numel() for parameter in auxiliary.parameters()
        ) if auxiliary is not None else 0,
        "loaded_graphs": len(graphs),
        "selected_checkpoint": str(best_checkpoint),
        "best_validation": final_validation,
        "history": history,
        "epochs_completed": len(history),
        "stopped_early": stopped_early,
        "early_stopping": early_config,
        "test_metrics": None,
        "test_policy": "sealed_during_pilot",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("summary:", output_dir / "summary.json")
    return 0
