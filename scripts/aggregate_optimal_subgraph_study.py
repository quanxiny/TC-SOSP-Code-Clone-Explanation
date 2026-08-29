#!/usr/bin/env python3
"""Aggregate the complete validation-only optimal subgraph-pair study.

The output intentionally recomputes absolute sufficiency metrics from records.
Some early C1--C4 summaries predate the explicit
``absolute_sufficiency_gap`` field and contain only the signed gap.
"""

from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np

from .explanation_runner import (
    aggregate,
    bootstrap_mean_ci,
    cluster_bootstrap_mean_ci,
    paired_comparison,
)


ROOT = Path(__file__).resolve().parents[1]
PILOTS = ROOT / "artifacts" / "pilots"
OUTPUT = (
    ROOT / "artifacts" / "comparisons"
    / "C_semantic_optimal_subgraph_study_validation.json"
)
RESAMPLES = 10000

RUNS = {
    "primary_20pct": PILOTS / "C1_semantic_optimal_subgraph_pair_seed42",
    "budget_10pct": PILOTS / "C2_semantic_optimal_subgraph_pair_budget10_seed42",
    "budget_30pct": PILOTS / "C3_semantic_optimal_subgraph_pair_budget30_seed42",
    "semantic_shuffle_20pct": PILOTS / "C4_shuffled_semantic_optimal_subgraph_pair_seed42",
    "checkpoint_seed42": PILOTS / "C5_optimal_subgraph_checkpoint_seed42",
    "checkpoint_seed123": PILOTS / "C6_optimal_subgraph_checkpoint_seed123",
    "checkpoint_seed2024": PILOTS / "C7_optimal_subgraph_checkpoint_seed2024",
}

GRADIENT = "symmetric_grad_x_input"
SEMANTIC = "symmetric_semantic_optimal_pair"
ATTENTION = "symmetric_semantic_attention_optimal_pair"
SHUFFLED_ATTENTION = "symmetric_semantic_shuffled_attention_optimal_pair"
SHUFFLED_SEMANTIC = "symmetric_shuffled_semantic_optimal_pair"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_records(run_dir: Path, method: str) -> List[Dict[str, Any]]:
    path = run_dir / f"{method}_records.jsonl"
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    # Normalize early artifacts without changing them on disk.
    for record in records:
        record.setdefault(
            "absolute_sufficiency_gap", abs(float(record["sufficiency_gap"]))
        )
    return records


def pair_identity(record: Dict[str, Any]) -> tuple:
    return (
        int(record["pair_index"]), record["left"], record["right"],
        int(record["label"]), record["problem_pair_cluster"],
    )


def assert_same_pairs(*record_sets: Sequence[Dict[str, Any]]) -> None:
    identities = [[pair_identity(record) for record in records] for records in record_sets]
    if not identities or any(identity != identities[0] for identity in identities[1:]):
        raise RuntimeError("runs do not cover the same ordered validation pairs")


def metric_summary(records: Sequence[Dict[str, Any]], metric: str,
                   seed: int) -> Dict[str, Any]:
    values = [float(record[metric]) for record in records]
    return {
        "mean": float(np.mean(values)),
        "bootstrap_95_ci": bootstrap_mean_ci(values, RESAMPLES, seed),
        "problem_pair_cluster_bootstrap_95_ci": cluster_bootstrap_mean_ci(
            records, metric, RESAMPLES, seed + 17,
        ),
    }


def candidate_pool_records(
    records: Sequence[Dict[str, Any]], allowed: Iterable[str],
) -> List[Dict[str, Any]]:
    allowed_set = set(allowed)
    selected = []
    for record in records:
        eligible = [
            item for item in record["candidate_diagnostics"]
            if item["name"] in allowed_set
        ]
        if not eligible:
            raise RuntimeError(f"empty candidate pool for pair {record['pair_index']}")
        # This is the same deterministic tie-break used by the explainer:
        # candidates are generated in a fixed order and max keeps the first tie.
        best = max(eligible, key=lambda item: float(item["objective"]))
        selected.append({
            "pair_index": record["pair_index"],
            "problem_pair_cluster": record["problem_pair_cluster"],
            "necessity_drop": float(best["necessity_drop"]),
            "sufficiency_gap": float(best["absolute_sufficiency_gap"]),
            "absolute_sufficiency_gap": float(best["absolute_sufficiency_gap"]),
            "swap_jaccard": 1.0,
            "seconds": 0.0,
            "selected_candidate": best["name"],
        })
    return selected


def compact_method(records: List[Dict[str, Any]], seed: int) -> Dict[str, Any]:
    summary = aggregate(records, RESAMPLES, seed, include_subgroups=False)
    return {
        "pairs": summary["pairs"],
        "problem_pair_clusters": summary["problem_pair_clusters"],
        "prediction_accuracy": summary["prediction_accuracy"],
        "necessity_drop": summary["necessity_drop"],
        "absolute_sufficiency_gap": summary["absolute_sufficiency_gap"],
        "swap_jaccard": summary["swap_jaccard"],
        "seconds": summary["seconds"],
        **({"semantic_pair_quality": summary["semantic_pair_quality"]}
           if "semantic_pair_quality" in summary else {}),
        **({"induced_cfg_coverage": summary["induced_cfg_coverage"]}
           if "induced_cfg_coverage" in summary else {}),
    }


def main() -> int:
    for name, run_dir in RUNS.items():
        if not (run_dir / "summary.json").is_file():
            raise FileNotFoundError(f"missing completed run {name}: {run_dir}")

    primary_grad = read_records(RUNS["primary_20pct"], GRADIENT)
    primary_semantic = read_records(RUNS["primary_20pct"], SEMANTIC)
    primary_attention = read_records(RUNS["primary_20pct"], ATTENTION)
    primary_shuffled_attention = read_records(
        RUNS["primary_20pct"], SHUFFLED_ATTENTION
    )
    shuffled_semantic = read_records(
        RUNS["semantic_shuffle_20pct"], SHUFFLED_SEMANTIC
    )
    assert_same_pairs(
        primary_grad, primary_semantic, primary_attention,
        primary_shuffled_attention, shuffled_semantic,
    )

    budget_runs = {
        "0.10": RUNS["budget_10pct"],
        "0.20": RUNS["primary_20pct"],
        "0.30": RUNS["budget_30pct"],
    }
    budget_curve = {}
    for index, (fraction, run_dir) in enumerate(budget_runs.items()):
        gradient_records = read_records(run_dir, GRADIENT)
        semantic_records = read_records(run_dir, SEMANTIC)
        assert_same_pairs(primary_grad, gradient_records, semantic_records)
        budget_curve[fraction] = {
            "gradient": compact_method(gradient_records, 210000 + index * 10003),
            "semantic_optimal_pair": compact_method(
                semantic_records, 220000 + index * 10003
            ),
            "semantic_optimal_pair_minus_gradient": paired_comparison(
                gradient_records, semantic_records, RESAMPLES,
                230000 + index * 10003,
            ),
        }

    pool_order = [
        ("gradient_only", ["gradient"]),
        ("plus_semantic_reranking", [
            "gradient", "semantic_025", "semantic_050", "semantic_075",
            "semantic_product",
        ]),
        ("plus_paired_relation", [
            "gradient", "semantic_025", "semantic_050", "semantic_075",
            "semantic_product", "paired_relation",
        ]),
        ("plus_cfg_diffusion", [
            "gradient", "semantic_025", "semantic_050", "semantic_075",
            "semantic_product", "paired_relation", "semantic_cfg",
        ]),
    ]
    pool_records = {
        name: candidate_pool_records(primary_semantic, candidates)
        for name, candidates in pool_order
    }
    component_ablation = {
        "candidate_pool_metrics": {
            name: {
                "necessity_drop": metric_summary(
                    records, "necessity_drop", 310000 + index * 10003
                ),
                "absolute_sufficiency_gap": metric_summary(
                    records, "absolute_sufficiency_gap", 320000 + index * 10003
                ),
                "selected_candidate_counts": dict(collections.Counter(
                    record["selected_candidate"] for record in records
                )),
            }
            for index, (name, records) in enumerate(pool_records.items())
        },
        "incremental_comparisons": {},
    }
    for index in range(1, len(pool_order)):
        previous_name = pool_order[index - 1][0]
        current_name = pool_order[index][0]
        component_ablation["incremental_comparisons"][
            f"{current_name}_minus_{previous_name}"
        ] = paired_comparison(
            pool_records[previous_name], pool_records[current_name],
            RESAMPLES, 330000 + index * 10003,
        )

    checkpoint_results = {}
    checkpoint_deltas = []
    for index, run_name in enumerate((
        "checkpoint_seed42", "checkpoint_seed123", "checkpoint_seed2024",
    )):
        run_dir = RUNS[run_name]
        gradient_records = read_records(run_dir, GRADIENT)
        semantic_records = read_records(run_dir, SEMANTIC)
        assert_same_pairs(primary_grad, gradient_records, semantic_records)
        comparison = paired_comparison(
            gradient_records, semantic_records, RESAMPLES,
            410000 + index * 10003,
        )
        checkpoint_results[run_name] = {
            "summary_sha256": sha256(run_dir / "summary.json"),
            "checkpoint_sha256": json.loads(
                (run_dir / "summary.json").read_text(encoding="utf-8")
            )["checkpoint_sha256"],
            "gradient": compact_method(gradient_records, 420000 + index * 10003),
            "semantic_optimal_pair": compact_method(
                semantic_records, 430000 + index * 10003
            ),
            "comparison": comparison,
        }
        checkpoint_deltas.append({
            "necessity_drop_delta": comparison["necessity_drop_delta"]["mean"],
            "absolute_sufficiency_gap_improvement": comparison[
                "absolute_sufficiency_gap_improvement"
            ]["mean"],
        })

    heldout_path = (
        ROOT / "artifacts" / "comparisons"
        / "C1_semantic_optimal_subgraph_pair_heldout96_validation.json"
    )
    heldout = json.loads(heldout_path.read_text(encoding="utf-8"))
    output = {
        "study": "task-conditioned symmetric discrete optimal subgraph pairs",
        "protocol": {
            "split": "validation_only",
            "test_metrics": None,
            "test_policy": "sealed_during_method_development_and_comparison",
            "pairs": 100,
            "primary_node_budget_fraction": 0.20,
            "selection_objective": (
                "maximize target-class necessity drop minus absolute sufficiency gap "
                "at a fixed per-graph node budget"
            ),
            "positive_relation": "common semantic statement pairs",
            "negative_relation": "contrastive unmatched statement pairs",
            "swap_policy": "canonical unordered graph pair with symmetric predictor",
            "attention_role": (
                "encoder internal node-token attention is an optional candidate prior; "
                "it is never treated as the explanation itself"
            ),
            "known_boundary": (
                "natural GCJ pairs have no node-level rationale or correspondence ground truth"
            ),
        },
        "input_artifacts": {
            name: {
                "relative_path": str(run_dir.relative_to(ROOT)),
                "summary_sha256": sha256(run_dir / "summary.json"),
            }
            for name, run_dir in RUNS.items()
        },
        "primary_20pct": {
            "gradient": compact_method(primary_grad, 510000),
            "semantic_optimal_pair": compact_method(primary_semantic, 520000),
            "comparison": paired_comparison(
                primary_grad, primary_semantic, RESAMPLES, 530000
            ),
            "selected_candidate_counts": dict(collections.Counter(
                record["selected_candidate"] for record in primary_semantic
            )),
        },
        "heldout_after_four_pair_smoke": {
            "relative_path": str(heldout_path.relative_to(ROOT)),
            "sha256": sha256(heldout_path),
            "protocol": heldout["protocol"],
            "comparison": heldout[
                "comparisons_vs_symmetric_grad_x_input"
            ][SEMANTIC],
        },
        "attention_prior_control": {
            "real_attention": compact_method(primary_attention, 540000),
            "shuffled_attention": compact_method(
                primary_shuffled_attention, 550000
            ),
            "real_minus_shuffled": paired_comparison(
                primary_shuffled_attention, primary_attention, RESAMPLES, 560000
            ),
            "decision": (
                "reject attention-specific contribution: real prior does not beat "
                "the deterministic shuffled-attention control"
            ),
        },
        "semantic_prior_control": {
            "shuffled_semantic": compact_method(shuffled_semantic, 570000),
            "shuffled_semantic_minus_gradient": paired_comparison(
                primary_grad, shuffled_semantic, RESAMPLES, 580000
            ),
            "real_semantic_minus_shuffled_semantic": paired_comparison(
                shuffled_semantic, primary_semantic, RESAMPLES, 590000
            ),
            "decision": (
                "real task-conditioned semantic relations explain most of the necessity gain; "
                "discrete multi-candidate search alone explains a smaller residual"
            ),
        },
        "budget_curve": budget_curve,
        "component_ablation": component_ablation,
        "checkpoint_robustness": {
            "runs": checkpoint_results,
            "mean_over_three_checkpoints": {
                "necessity_drop_delta": float(np.mean([
                    item["necessity_drop_delta"] for item in checkpoint_deltas
                ])),
                "absolute_sufficiency_gap_improvement": float(np.mean([
                    item["absolute_sufficiency_gap_improvement"]
                    for item in checkpoint_deltas
                ])),
                "checkpoint_level_positive_counts": {
                    "necessity_drop_delta": int(sum(
                        item["necessity_drop_delta"] > 0 for item in checkpoint_deltas
                    )),
                    "absolute_sufficiency_gap_improvement": int(sum(
                        item["absolute_sufficiency_gap_improvement"] > 0
                        for item in checkpoint_deltas
                    )),
                },
            },
        },
        "interpretation": {
            "recommended_variant": "symmetric_semantic_optimal_pair_without_attention",
            "evidence_status": "GO_EXPLANATION_METHOD_PILOT_NOT_YET_STANDALONE_PAPER",
            "supported": [
                "improved perturbation faithfulness over symmetric Grad×Input",
                "exact swap consistency by construction",
                "effect across three node budgets and three additional predictor checkpoints",
                "task semantic relations contribute beyond shuffled-semantic control",
            ],
            "not_supported": [
                "attention-specific explanatory contribution",
                "node-level semantic correctness or causal ground-truth alignment",
                "independent-dataset generalization",
            ],
        },
        "test_metrics": None,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(OUTPUT)
    print(f"sha256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
