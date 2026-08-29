#!/usr/bin/env python3
"""Batched, resumable reproduction runner for the paper's GCJ/CFG model."""

import argparse
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from tqdm import tqdm

from myModels.GAT_Edgepool_clone_detection import CodeCloneDetection
from reproduce_gcj import FocalLoss, count_parameters, normalize_label


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("train", "eval", "train-eval"), default="train-eval")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--graph-batch-size", type=int, default=16)
    parser.add_argument("--eval-pair-batch-size", type=int, default=15000)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--weight-decay", type=float, default=5e-4)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--num-layers", type=int, default=4)
    parser.add_argument("--hidden", type=int, default=16)
    parser.add_argument("--num-classes", type=int, default=2)
    parser.add_argument("--nheads", type=int, default=16)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--alpha", type=float, default=0.2)
    parser.add_argument("--source-dir", type=Path, default=Path("googlejam4_src"))
    parser.add_argument(
        "--vector-dir", type=Path, default=Path("artifacts/gcj_cfg16_repaired")
    )
    parser.add_argument(
        "--train-split", type=Path,
        default=Path("artifacts/paper_protocol/train_balanced_seed1337.txt"),
    )
    parser.add_argument(
        "--validation-split", type=Path,
        default=Path("DataSetJsonVec/GCJ/javadata/valid.txt"),
    )
    parser.add_argument(
        "--test-split", type=Path,
        default=Path("DataSetJsonVec/GCJ/javadata/test.txt"),
    )
    parser.add_argument("--train-limit", type=int, default=0)
    parser.add_argument("--validation-limit", type=int, default=0)
    parser.add_argument("--test-limit", type=int, default=0)
    parser.add_argument("--evaluate-every", type=int, default=1)
    parser.add_argument("--amp", action="store_true", help="Use CUDA automatic mixed precision.")
    parser.add_argument("--no-tf32", action="store_true", help="Disable A100 TF32 matrix operations.")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("artifacts/gcj_cfg_paper_protocol")
    )
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from OUTPUT_DIR/latest_training.pt when it exists.",
    )
    return parser.parse_args()


def model_args(args, training):
    return (
        args.num_layers,
        args.hidden,
        args.nheads,
        args.num_classes,
        args.dropout,
        args.alpha,
        training,
    )


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def read_lines(path, limit=0):
    lines = path.read_text(encoding="utf-8").splitlines(True)
    return lines[:limit] if limit > 0 else lines


def graph_paths(lines):
    return {path for line in lines for path in line.split()[:2]}


def load_graph(path, vector_dir, device, hidden):
    vector_path = vector_dir / (Path(path).name + ".json")
    with vector_path.open("r", encoding="utf-8") as vector_file:
        data = json.load(vector_file)

    max_tokens = max(len(vectors) for vectors in data["jsonNodesVec"].values())
    features = []
    for node_index in range(len(data["jsonNodesVec"])):
        raw_vectors = data["jsonNodesVec"][str(node_index)]
        node_vectors = [vector for vector in raw_vectors if vector is not None]
        if not node_vectors:
            node_vectors = [[0.0] * hidden]
        node_vectors.extend(
            [[0.0] * hidden for _ in range(max_tokens - len(node_vectors))]
        )
        features.append(node_vectors)

    edge_sources = []
    edge_targets = []
    edge_attributes = []
    attention_sources = []
    attention_targets = []
    attention_attributes = []
    for edge, vectors in data["jsonEdgesVec"].items():
        source, target = (int(value) for value in edge.split("->"))
        vector = vectors[0]
        if vector is None:
            vector = [0.0] * hidden
        if len(vector) >= 4 and vector[0] == vector[1] == vector[3] == 1:
            vector = [0.0] * hidden
        edge_sources.append(source)
        edge_targets.append(target)
        edge_attributes.append(vector)
        if source != target:
            attention_sources.append(source)
            attention_targets.append(target)
            attention_attributes.append(vector)
    for node_index in range(len(features)):
        edge_sources.append(node_index)
        edge_targets.append(node_index)
        edge_attributes.append([0.0] * hidden)
        attention_sources.append(node_index)
        attention_targets.append(node_index)
        attention_attributes.append([0.0] * hidden)

    return (
        torch.tensor(features, dtype=torch.float32, device=device),
        torch.tensor([edge_sources, edge_targets], dtype=torch.long, device=device),
        torch.tensor(edge_attributes, dtype=torch.float32, device=device),
        torch.tensor(
            [attention_sources, attention_targets], dtype=torch.long, device=device
        ),
        torch.tensor(attention_attributes, dtype=torch.float32, device=device),
    )


def load_graphs(paths, source_dir, vector_dir, device, hidden):
    graphs = {}
    failures = {}
    for path in tqdm(sorted(paths), desc="load graphs"):
        try:
            source_path = Path(path)
            if not source_path.is_file() and not source_path.is_absolute():
                source_path = source_dir / source_path
            if not source_path.is_file():
                raise FileNotFoundError("source file does not exist")
            graphs[path] = load_graph(path, vector_dir, device, hidden)
        except (OSError, ValueError, KeyError, TypeError) as error:
            failures[path] = "{}: {}".format(type(error).__name__, error)
    if failures:
        raise RuntimeError("failed to load {} graphs: {}".format(len(failures), failures))
    return graphs


def collate_graphs(paths, graphs):
    selected = [graphs[path] for path in paths]
    max_tokens = max(graph[0].size(1) for graph in selected)
    features = []
    edge_indices = []
    edge_attributes = []
    batches = []
    attention_edge_indices = []
    attention_edge_attributes = []
    offset = 0
    for graph_index, graph in enumerate(selected):
        node_features, edge_index, edge_attr, attention_edge_index, attention_edge_attr = graph
        features.append(F.pad(node_features, (0, 0, 0, max_tokens - node_features.size(1))))
        edge_indices.append(edge_index + offset)
        edge_attributes.append(edge_attr)
        attention_edge_indices.append(attention_edge_index + offset)
        attention_edge_attributes.append(attention_edge_attr)
        batches.append(
            torch.full(
                (node_features.size(0),), graph_index,
                dtype=torch.long, device=node_features.device,
            )
        )
        offset += node_features.size(0)
    return (
        torch.cat(features, dim=0),
        torch.cat(edge_indices, dim=1),
        torch.cat(edge_attributes, dim=0),
        torch.cat(batches, dim=0),
        torch.cat(attention_edge_indices, dim=1),
        torch.cat(attention_edge_attributes, dim=0),
    )


def encode_paths(model, paths, graphs, graph_batch_size, description):
    outputs = []
    starts = range(0, len(paths), graph_batch_size)
    if description:
        starts = tqdm(starts, desc=description, leave=False)
    for start in starts:
        batch_paths = paths[start : start + graph_batch_size]
        outputs.append(model.encode_batched(*collate_graphs(batch_paths, graphs)))
    return torch.cat(outputs, dim=0)


def metrics_for_model(args, model, lines, graphs, description, prediction_path=None):
    model.eval()
    usable = [line.split() for line in lines]
    required = sorted({path for fields in usable for path in fields[:2]})
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    started = time.perf_counter()
    with torch.no_grad(), torch.cuda.amp.autocast(enabled=args.amp):
        encoded = encode_paths(
            model, required, graphs, args.graph_batch_size,
            description + " graph embeddings",
        )
        embeddings = dict(zip(required, encoded))
        embedding_seconds = time.perf_counter() - started
        predictions = []
        probabilities = []
        swapped_probabilities = []
        labels = []
        detection_started = time.perf_counter()
        for start in range(0, len(usable), args.eval_pair_batch_size):
            batch = usable[start : start + args.eval_pair_batch_size]
            first = torch.stack([embeddings[fields[0]] for fields in batch])
            second = torch.stack([embeddings[fields[1]] for fields in batch])
            output = model.detect_embeddings(first, second)
            swapped_output = model.detect_embeddings(second, first)
            predictions.extend(output.argmax(dim=1).cpu().tolist())
            probabilities.extend(output[:, 1].cpu().tolist())
            swapped_probabilities.extend(swapped_output[:, 1].cpu().tolist())
            labels.extend(normalize_label(fields[2]) for fields in batch)
        torch.cuda.synchronize()
        detection_seconds = time.perf_counter() - detection_started
    if prediction_path is not None:
        prediction_path.parent.mkdir(parents=True, exist_ok=True)
        with prediction_path.open("w", encoding="utf-8") as prediction_file:
            for fields, label, prediction, probability, swapped_probability in zip(
                    usable, labels, predictions, probabilities, swapped_probabilities):
                prediction_file.write(json.dumps({
                    "left": fields[0],
                    "right": fields[1],
                    "raw_label": fields[2],
                    "label": label,
                    "prediction": prediction,
                    "clone_probability": probability,
                    "swapped_clone_probability": swapped_probability,
                }, ensure_ascii=False) + "\n")
    per_class_f1 = f1_score(
        labels, predictions, labels=[0, 1], average=None, zero_division=0
    )
    matrix = confusion_matrix(labels, predictions, labels=[0, 1]).tolist()
    swap_errors = [
        abs(probability - swapped_probability)
        for probability, swapped_probability in zip(probabilities, swapped_probabilities)
    ]
    result = {
        "pairs": len(labels),
        "graphs": len(required),
        "positive_pairs": sum(labels),
        "negative_pairs": len(labels) - sum(labels),
        "accuracy": accuracy_score(labels, predictions),
        "precision_macro": precision_score(labels, predictions, average="macro", zero_division=0),
        "recall_macro": recall_score(labels, predictions, average="macro", zero_division=0),
        "f1_macro": f1_score(labels, predictions, average="macro", zero_division=0),
        "f1_negative": float(per_class_f1[0]),
        "f1_positive": float(per_class_f1[1]),
        "mcc": matthews_corrcoef(labels, predictions),
        "pr_auc": average_precision_score(labels, probabilities),
        "roc_auc": roc_auc_score(labels, probabilities),
        "brier_score": brier_score_loss(labels, probabilities),
        "confusion_matrix_labels_0_1": matrix,
        "mean_abs_swap_probability_error": sum(swap_errors) / len(swap_errors),
        "max_abs_swap_probability_error": max(swap_errors),
        "embedding_seconds": embedding_seconds,
        "detection_seconds": detection_seconds,
        "encoder_graphs_per_second": len(required) / embedding_seconds,
        "ordered_and_swapped_pairs_per_second": (2 * len(labels)) / detection_seconds,
        "peak_gpu_memory_allocated_mb": torch.cuda.max_memory_allocated() / (1024 ** 2),
        "peak_gpu_memory_reserved_mb": torch.cuda.max_memory_reserved() / (1024 ** 2),
    }
    if prediction_path is not None:
        result["predictions"] = str(prediction_path)
    return result


def save_training_state(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(value, temporary)
    os.replace(str(temporary), str(path))


def train(args, train_lines, validation_lines, graphs, device):
    model = CodeCloneDetection(*model_args(args, training=True)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scaler = torch.cuda.amp.GradScaler(enabled=args.amp)
    criterion = FocalLoss(alpha=1, gamma=2).to(device)
    history = []
    best_f1 = -1.0
    best_checkpoint = None
    start_epoch = 0
    latest_path = args.output_dir / "latest_training.pt"

    if args.resume and latest_path.is_file():
        state = torch.load(latest_path, map_location=device)
        model.load_state_dict(state["model"])
        optimizer.load_state_dict(state["optimizer"])
        if "scaler" in state:
            scaler.load_state_dict(state["scaler"])
        history = state["history"]
        start_epoch = state["epoch"]
        best_f1 = state["best_f1"]
        best_checkpoint = Path(state["best_checkpoint"]) if state["best_checkpoint"] else None
        print("resumed at epoch", start_epoch)

    print("trainable parameters:", count_parameters(model))
    for epoch in range(start_epoch, args.epochs):
        model.train()
        epoch_started = time.perf_counter()
        running_loss = 0.0
        processed = 0
        correct = 0
        batches = range(0, len(train_lines), args.batch_size)
        progress = tqdm(batches, desc="epoch {}/{}".format(epoch + 1, args.epochs))
        for start in progress:
            fields = [line.split() for line in train_lines[start : start + args.batch_size]]
            optimizer.zero_grad()
            graph_sequence = [item[0] for item in fields] + [item[1] for item in fields]
            with torch.cuda.amp.autocast(enabled=args.amp):
                encoded = encode_paths(
                    model, graph_sequence, graphs, args.graph_batch_size, None
                )
                pair_count = len(fields)
                output = model.detect_embeddings(encoded[:pair_count], encoded[pair_count:])
                labels = [normalize_label(item[2]) for item in fields]
                targets = torch.tensor(
                    [[0.0, 1.0] if label == 1 else [1.0, 0.0] for label in labels],
                    device=device,
                )
            loss = criterion(output.float(), targets) * pair_count
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            running_loss += loss.item()
            processed += pair_count
            correct += sum(
                prediction == label
                for prediction, label in zip(output.argmax(dim=1).tolist(), labels)
            )
            progress.set_postfix(loss=running_loss / processed, accuracy=correct / processed)

        checkpoint = args.output_dir / "epoch_{:03d}.pt".format(epoch + 1)
        torch.save(model.state_dict(), checkpoint)
        validation = None
        if (epoch + 1) % args.evaluate_every == 0:
            validation = metrics_for_model(
                args, model, validation_lines, graphs,
                "validation epoch {}".format(epoch + 1),
            )
            if validation["f1_macro"] > best_f1:
                best_f1 = validation["f1_macro"]
                best_checkpoint = checkpoint
        result = {
            "epoch": epoch + 1,
            "loss": running_loss / processed,
            "accuracy": correct / processed,
            "processed_pairs": processed,
            "seconds": time.perf_counter() - epoch_started,
            "checkpoint": str(checkpoint),
            "validation": validation,
        }
        history.append(result)
        print(json.dumps(result, ensure_ascii=False))
        save_training_state(
            latest_path,
            {
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "scaler": scaler.state_dict(),
                "epoch": epoch + 1,
                "history": history,
                "best_f1": best_f1,
                "best_checkpoint": str(best_checkpoint) if best_checkpoint else None,
            },
        )
    return model, best_checkpoint or checkpoint, history


def main():
    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the released model implementation")
    if args.graph_batch_size < 1:
        raise ValueError("--graph-batch-size must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    set_seed(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = not args.no_tf32
    torch.backends.cudnn.allow_tf32 = not args.no_tf32
    device = torch.device("cuda")

    train_lines = read_lines(args.train_split, args.train_limit) if args.mode != "eval" else []
    validation_lines = (
        read_lines(args.validation_split, args.validation_limit)
        if args.mode != "eval" else []
    )
    test_lines = read_lines(args.test_split, args.test_limit) if args.mode != "train" else []
    required = graph_paths(train_lines + validation_lines + test_lines)
    graphs = load_graphs(required, args.source_dir, args.vector_dir, device, args.hidden)

    model = None
    checkpoint = args.checkpoint
    history = []
    if args.mode in ("train", "train-eval"):
        model, checkpoint, history = train(
            args, train_lines, validation_lines, graphs, device
        )
    if args.mode == "eval":
        if checkpoint is None:
            raise ValueError("--checkpoint is required in eval mode")
        model = CodeCloneDetection(*model_args(args, training=False)).to(device)
        model.load_state_dict(torch.load(checkpoint, map_location=device))

    test_metrics = None
    if args.mode in ("eval", "train-eval"):
        if args.mode == "train-eval":
            model.load_state_dict(torch.load(checkpoint, map_location=device))
        test_metrics = metrics_for_model(
            args, model, test_lines, graphs, "test",
            args.output_dir / "test_predictions.jsonl",
        )
        print(json.dumps(test_metrics, indent=2, ensure_ascii=False))

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
        "parameter_count": count_parameters(model),
        "loaded_graphs": len(graphs),
        "selected_checkpoint": str(checkpoint) if checkpoint else None,
        "history": history,
        "test_metrics": test_metrics,
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("summary:", summary_path)


if __name__ == "__main__":
    main()
