#!/usr/bin/env python3
"""Reproducible GCJ/CFG runner for CodeGraph4CCDetector.

The upstream entry points hard-code data paths and checkpoint indices.  This
runner keeps the published model and loss intact while making the paper split,
random seed, limits, checkpoints, and evaluation outputs explicit.
"""

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import f1_score, precision_score, recall_score
from tqdm import tqdm

from jsonparse import getCodePairDataList, saveTestDataToRam
from myModels.GAT_Edgepool_bi_lstm import bi_lstm_detect
from myModels.GAT_Edgepool_clone_detection import CodeCloneDetection
from myModels.GAT_Edgepool_graphEmb import graphEmb


class FocalLoss(nn.Module):
    """Focal loss used verbatim by the upstream main.py."""

    def __init__(self, alpha=1, gamma=2):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs, targets):
        bce_loss = F.binary_cross_entropy(inputs, targets, reduction="none")
        probability = torch.exp(-bce_loss)
        return torch.mean(
            self.alpha * (1 - probability) ** self.gamma * bce_loss
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train and evaluate the paper's GCJ/CFG configuration."
    )
    parser.add_argument("--mode", choices=("train", "eval", "train-eval"), default="train-eval")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--eval-batch-size", type=int, default=15000)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--weight-decay", type=float, default=5e-4)
    parser.add_argument("--num-layers", type=int, default=4)
    parser.add_argument("--hidden", type=int, default=16)
    parser.add_argument("--num-classes", type=int, default=2)
    parser.add_argument("--nheads", type=int, default=16)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--alpha", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument(
        "--train-split",
        type=Path,
        default=Path("DataSetJsonVec/GCJ/javadata/train11.txt"),
    )
    parser.add_argument(
        "--eval-split",
        type=Path,
        default=Path("DataSetJsonVec/GCJ/javadata/test.txt"),
    )
    parser.add_argument(
        "--train-limit",
        type=int,
        default=0,
        help="Use at most this many training pairs; 0 uses the complete split.",
    )
    parser.add_argument(
        "--eval-limit",
        type=int,
        default=0,
        help="Use at most this many evaluation pairs; 0 uses the complete split.",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("artifacts/gcj_cfg_full")
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        help="Checkpoint for eval mode. Train modes evaluate their last checkpoint.",
    )
    return parser.parse_args()


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def read_split(path):
    with path.open("r", encoding="utf-8") as split_file:
        return split_file.readlines()


def normalize_label(raw_label):
    return 1 if int(raw_label) == 1 else 0


def limited_lines(lines, limit, seed, shuffle):
    selected = list(lines)
    if shuffle:
        random.Random(seed).shuffle(selected)
    return selected[:limit] if limit > 0 else selected


def graph_paths(lines):
    paths = set()
    for line in lines:
        fields = line.split()
        if len(fields) >= 2:
            paths.update(fields[:2])
    return paths


def model_kwargs(args, training):
    return (
        args.num_layers,
        args.hidden,
        args.nheads,
        args.num_classes,
        args.dropout,
        args.alpha,
        training,
    )


def count_parameters(model):
    return sum(parameter.numel() for parameter in model.parameters())


def load_matching_weights(model, state_dict):
    model_state = model.state_dict()
    matching = {
        key: value for key, value in state_dict.items() if key in model_state
    }
    model_state.update(matching)
    model.load_state_dict(model_state)
    return len(matching)


def train(args, train_lines, ram_data, device):
    model = CodeCloneDetection(*model_kwargs(args, training=True)).to(device)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=args.lr, weight_decay=args.weight_decay
    )
    criterion = FocalLoss(alpha=1, gamma=2).to(device)
    history = []

    print("trainable parameters:", count_parameters(model))
    print("training pairs:", len(train_lines))

    for epoch in range(args.epochs):
        model.train()
        epoch_started = time.perf_counter()
        running_loss = 0.0
        correct = 0
        processed = 0

        batches = range(0, len(train_lines), args.batch_size)
        progress = tqdm(batches, desc="epoch {}/{}".format(epoch + 1, args.epochs))
        for start in progress:
            batch_lines = train_lines[start : start + args.batch_size]
            batch = getCodePairDataList(ram_data, batch_lines)
            if not batch:
                continue

            optimizer.zero_grad()
            batch_loss = torch.zeros((), device=device)
            for pair in batch:
                raw_label = pair[-1]
                label = normalize_label(raw_label)
                target = torch.tensor(
                    [[0.0, 1.0] if label == 1 else [1.0, 0.0]], device=device
                )
                output = model(tuple(pair[:-1]))
                batch_loss = batch_loss + criterion(output, target)
                correct += int(output.argmax(dim=1).item() == label)

            batch_loss.backward()
            optimizer.step()

            processed += len(batch)
            running_loss += batch_loss.item()
            progress.set_postfix(
                loss=running_loss / processed,
                accuracy=correct / processed,
            )

        checkpoint = args.output_dir / "epoch_{:03d}.pt".format(epoch + 1)
        torch.save(model.state_dict(), checkpoint)
        elapsed = time.perf_counter() - epoch_started
        epoch_result = {
            "epoch": epoch + 1,
            "loss": running_loss / processed,
            "accuracy": correct / processed,
            "processed_pairs": processed,
            "seconds": elapsed,
            "checkpoint": str(checkpoint),
        }
        history.append(epoch_result)
        print(json.dumps(epoch_result, ensure_ascii=False))

    return checkpoint, history, count_parameters(model)


def evaluate(args, checkpoint, eval_lines, ram_data, device):
    state_dict = torch.load(checkpoint, map_location=device)
    encoder = graphEmb(*model_kwargs(args, training=False)).to(device)
    decoder = bi_lstm_detect(*model_kwargs(args, training=False)).to(device)
    encoder_keys = load_matching_weights(encoder, state_dict)
    decoder_keys = load_matching_weights(decoder, state_dict)
    encoder.eval()
    decoder.eval()

    usable_lines = []
    required_graphs = set()
    for line in eval_lines:
        fields = line.split()
        if len(fields) >= 3 and fields[0] in ram_data and fields[1] in ram_data:
            usable_lines.append(line)
            required_graphs.update(fields[:2])

    torch.cuda.synchronize()
    embedding_started = time.perf_counter()
    embeddings = {}
    with torch.no_grad():
        for code_path in tqdm(sorted(required_graphs), desc="graph embeddings"):
            embeddings[code_path] = encoder(tuple(ram_data[code_path]))
    torch.cuda.synchronize()
    embedding_seconds = time.perf_counter() - embedding_started

    predictions = []
    labels = []
    torch.cuda.synchronize()
    detection_started = time.perf_counter()
    with torch.no_grad():
        for start in tqdm(
            range(0, len(usable_lines), args.eval_batch_size), desc="clone detection"
        ):
            fields = [line.split() for line in usable_lines[start : start + args.eval_batch_size]]
            first = torch.cat([embeddings[item[0]] for item in fields], dim=0)
            second = torch.cat([embeddings[item[1]] for item in fields], dim=0)
            output = decoder(first, second)
            predictions.extend(output.argmax(dim=1).cpu().tolist())
            labels.extend(normalize_label(item[2]) for item in fields)
    torch.cuda.synchronize()
    detection_seconds = time.perf_counter() - detection_started

    result = {
        "checkpoint": str(checkpoint),
        "training_model_parameter_count": count_parameters(
            CodeCloneDetection(*model_kwargs(args, training=False))
        ),
        "checkpoint_tensor_values": sum(value.numel() for value in state_dict.values()),
        "evaluation_parameter_count": count_parameters(encoder) + count_parameters(decoder),
        "pairs": len(labels),
        "graphs": len(required_graphs),
        "positive_pairs": sum(labels),
        "negative_pairs": len(labels) - sum(labels),
        "precision_macro": precision_score(
            labels, predictions, average="macro", zero_division=0
        ),
        "recall_macro": recall_score(
            labels, predictions, average="macro", zero_division=0
        ),
        "f1_macro": f1_score(labels, predictions, average="macro", zero_division=0),
        "embedding_seconds": embedding_seconds,
        "detection_seconds": detection_seconds,
        "loaded_encoder_tensors": encoder_keys,
        "loaded_decoder_tensors": decoder_keys,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main():
    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError(
            "The published implementation hard-codes CUDA tensors; a CUDA GPU is required."
        )
    device = torch.device("cuda")
    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_lines = []
    if args.mode in ("train", "train-eval"):
        train_lines = limited_lines(
            read_split(args.train_split), args.train_limit, args.seed, shuffle=True
        )
    eval_lines = []
    if args.mode in ("eval", "train-eval"):
        eval_lines = limited_lines(
            read_split(args.eval_split), args.eval_limit, args.seed, shuffle=False
        )

    all_lines = train_lines + eval_lines
    required_paths = graph_paths(all_lines)
    print("loading {} graphs into GPU memory".format(len(required_paths)))
    ram_data = saveTestDataToRam(
        required_paths,
        "googlejam4_src/",
        "DataSetJsonVec/GCJ/dataSetCfgGCJ16/",
    )
    missing = required_paths.difference(ram_data)
    if missing:
        print(
            "WARNING: {} required graphs could not be loaded; upstream training "
            "also skips pairs containing them.".format(len(missing))
        )

    checkpoint = args.checkpoint
    history = []
    parameter_count = None
    if args.mode in ("train", "train-eval"):
        checkpoint, history, parameter_count = train(
            args, train_lines, ram_data, device
        )
    if args.mode == "eval" and checkpoint is None:
        raise ValueError("--checkpoint is required in eval mode")

    metrics = None
    if args.mode in ("eval", "train-eval"):
        metrics = evaluate(args, checkpoint, eval_lines, ram_data, device)
        if parameter_count is None:
            parameter_count = metrics["training_model_parameter_count"]

    summary = {
        "configuration": {
            key: str(value) if isinstance(value, Path) else value
            for key, value in vars(args).items()
        },
        "environment": {
            "torch": torch.__version__,
            "cuda_build": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0),
        },
        "parameter_count": parameter_count,
        "data": {
            "requested_graphs": len(required_paths),
            "loaded_graphs": len(ram_data),
            "missing_graphs": sorted(missing),
        },
        "history": history,
        "metrics": metrics,
    }
    summary_path = args.output_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as output_file:
        json.dump(summary, output_file, indent=2, ensure_ascii=False)
    print("summary:", summary_path)


if __name__ == "__main__":
    main()
