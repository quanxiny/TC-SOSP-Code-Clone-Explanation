#!/usr/bin/env python3
"""Configuration inheritance, validation and hashing for research runs."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


RESEARCH_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = (
    "schema_version",
    "experiment_id",
    "stage",
    "dataset",
    "graph_type",
    "split",
    "seed",
    "device",
    "loss",
    "output_dir",
    "resume",
)
ALLOWED_STAGES = {"baseline", "contrastive", "continual", "explanation"}


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if key == "extends":
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def resolve_config(path: Path, stack: Optional[List[Path]] = None) -> Dict[str, Any]:
    path = path.expanduser().resolve()
    stack = list(stack or [])
    if path in stack:
        chain = " -> ".join(str(item) for item in stack + [path])
        raise ValueError("cyclic config inheritance: {}".format(chain))
    if not path.is_file():
        raise FileNotFoundError(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("config root must be an object: {}".format(path))
    parent = raw.get("extends")
    if parent is None:
        return deep_merge({}, raw)
    parent_path = (path.parent / parent).resolve()
    return deep_merge(resolve_config(parent_path, stack + [path]), raw)


def is_within(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath((str(path), str(root))) == str(root)
    except ValueError:
        return False


def validate_config(config: Dict[str, Any], source: Optional[Path] = None) -> List[str]:
    prefix = "{}: ".format(source) if source else ""
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        if field not in config:
            errors.append(prefix + "missing required field '{}'".format(field))

    if config.get("stage") not in ALLOWED_STAGES:
        errors.append(prefix + "invalid stage '{}'".format(config.get("stage")))
    if not isinstance(config.get("seed"), int) or config.get("seed", -1) < 0:
        errors.append(prefix + "seed must be a non-negative integer")
    if not isinstance(config.get("resume"), bool):
        errors.append(prefix + "resume must be boolean")

    loss = config.get("loss")
    if not isinstance(loss, dict) or not isinstance(loss.get("name"), str):
        errors.append(prefix + "loss must be an object with a string 'name'")

    evaluation = config.get("evaluation", {})
    if evaluation.get("test_policy") != "after_selection_only":
        errors.append(prefix + "test_policy must remain 'after_selection_only'")

    output_dir = config.get("output_dir")
    if isinstance(output_dir, str) and output_dir:
        output_path = Path(output_dir)
        if not output_path.is_absolute():
            output_path = (RESEARCH_ROOT / output_path).resolve()
        else:
            output_path = output_path.resolve()
        artifact_root = (RESEARCH_ROOT / "artifacts").resolve()
        if not is_within(output_path, artifact_root):
            errors.append(prefix + "output_dir must stay under research artifacts/: {}".format(output_path))
    else:
        errors.append(prefix + "output_dir must be a non-empty string")

    sampling = config.get("sampling", {})
    fraction = sampling.get("train_fraction", 1.0)
    if not isinstance(fraction, (int, float)) or not 0 < fraction <= 1:
        errors.append(prefix + "sampling.train_fraction must be in (0, 1]")
    manifest = sampling.get("manifest")
    expected_manifest_hash = sampling.get("manifest_sha256")
    if manifest:
        manifest_path = resolve_workspace_path(manifest)
        if not manifest_path.is_file():
            errors.append(prefix + "sampling manifest does not exist: {}".format(manifest_path))
        elif expected_manifest_hash:
            actual_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            if actual_hash != expected_manifest_hash:
                errors.append(
                    prefix + "sampling manifest hash mismatch: {} != {}".format(
                        actual_hash, expected_manifest_hash
                    )
                )

    if config.get("split") == "paper_clean":
        contract = config.get("data_contract", {})
        if contract and contract.get("allow_fragment_overlap") is not False:
            errors.append(prefix + "paper_clean must forbid fragment overlap")

    return errors


def config_digest(config: Dict[str, Any]) -> str:
    payload = json.dumps(config, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def config_paths() -> Iterable[Path]:
    return sorted((RESEARCH_ROOT / "configs").rglob("*.json"))


def apply_overrides(config: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    result = copy.deepcopy(config)
    for key, value in overrides.items():
        if value is None:
            continue
        if key == "loss":
            result.setdefault("loss", {})["name"] = value
        else:
            result[key] = value
    return result


def resolve_workspace_path(value: str) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (RESEARCH_ROOT / path).resolve()
