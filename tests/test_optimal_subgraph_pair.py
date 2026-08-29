from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.explanation_runner import (  # noqa: E402
    canonical_explainer_seed_key,
    cluster_bootstrap_mean_ci,
    deterministic_prior_variant,
    deterministic_similarity_shuffle,
    rank_normalize,
    task_conditioned_candidate_sets,
)


def graph(nodes: int):
    features = torch.ones((nodes, 2, 3), dtype=torch.float32)
    source = list(range(nodes)) + list(range(max(nodes - 1, 0)))
    target = list(range(nodes)) + list(range(1, nodes))
    edge_index = torch.tensor([source, target], dtype=torch.long)
    edge_attr = torch.zeros((len(source), 3), dtype=torch.float32)
    return features, edge_index, edge_attr, edge_index, edge_attr


class OptimalSubgraphPairTests(unittest.TestCase):
    def test_explainer_seed_key_is_pair_canonical_and_seed_sensitive(self):
        first = canonical_explainer_seed_key("b.java", "a.java", 1, 123)
        swapped = canonical_explainer_seed_key("a.java", "b.java", 1, 123)
        changed = canonical_explainer_seed_key("a.java", "b.java", 1, 2024)
        legacy = canonical_explainer_seed_key(
            "b.java", "a.java", 1, 42, legacy_seed42=True
        )
        self.assertEqual(first, swapped)
        self.assertNotEqual(first, changed)
        self.assertEqual("a.java|b.java|1", legacy)

    def test_vectorized_cluster_bootstrap_matches_materialized_cluster_mean(self):
        records = [
            {"problem_pair_cluster": "a", "metric": 1.0},
            {"problem_pair_cluster": "a", "metric": 3.0},
            {"problem_pair_cluster": "b", "metric": 10.0},
        ]
        actual = cluster_bootstrap_mean_ci(records, "metric", 1000, 123)
        generator = np.random.default_rng(123)
        sampled = generator.integers(0, 2, size=(1000, 2), endpoint=False)
        group_sums = np.asarray([4.0, 10.0])
        group_counts = np.asarray([2.0, 1.0])
        means = group_sums[sampled].sum(axis=1) / group_counts[sampled].sum(axis=1)
        expected = [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]
        self.assertTrue(np.allclose(actual, expected))

    def test_rank_normalize_averages_ties(self):
        ranked = rank_normalize(torch.tensor([2.0, 2.0, 5.0]))
        self.assertTrue(torch.allclose(ranked, torch.tensor([0.25, 0.25, 1.0])))
        uniform = rank_normalize(torch.ones(4))
        self.assertTrue(torch.allclose(uniform, torch.full((4,), 0.5)))

    def test_shuffled_attention_is_deterministic_and_distribution_preserving(self):
        prior = torch.tensor([0.1, 0.2, 0.4, 0.8])
        first = deterministic_prior_variant(prior, "graph.java", "shuffled")
        second = deterministic_prior_variant(prior, "graph.java", "shuffled")
        self.assertTrue(torch.equal(first, second))
        self.assertEqual(sorted(prior.tolist()), sorted(first.tolist()))

    def test_candidates_keep_fixed_per_graph_budget_and_gradient_control(self):
        left = graph(5)
        right = graph(4)
        candidates = task_conditioned_candidate_sets(
            torch.tensor([0.1, 0.8, 0.2, 0.7, 0.3]),
            torch.tensor([0.9, 0.1, 0.6, 0.2]),
            torch.tensor([
                [0.9, 0.2, 0.1, 0.3],
                [0.3, 0.8, 0.2, 0.1],
                [0.2, 0.1, 0.4, 0.3],
                [0.1, 0.3, 0.2, 0.7],
                [0.2, 0.4, 0.3, 0.1],
            ]),
            left, right, target=1, fraction=0.4,
            attention_left=torch.linspace(0.0, 1.0, 5),
            attention_right=torch.linspace(1.0, 0.0, 4),
        )
        self.assertIn("gradient", {candidate["name"] for candidate in candidates})
        for candidate in candidates:
            self.assertEqual(2, len(candidate["left_selected"]))
            self.assertEqual(2, len(candidate["right_selected"]))

    def test_similarity_shuffle_preserves_values_and_is_deterministic(self):
        similarity = torch.arange(12, dtype=torch.float32).reshape(3, 4)
        first = deterministic_similarity_shuffle(similarity, "a.java", "b.java")
        second = deterministic_similarity_shuffle(similarity, "a.java", "b.java")
        self.assertTrue(torch.equal(first, second))
        self.assertEqual(sorted(similarity.flatten().tolist()), sorted(first.flatten().tolist()))


if __name__ == "__main__":
    unittest.main()
