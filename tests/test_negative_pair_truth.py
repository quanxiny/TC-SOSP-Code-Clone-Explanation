import unittest

from scripts.build_negative_pair_transformation_truth import pair_records, problem_id
from scripts.negative_pair_truth_runner import (
    mapped_selection,
    relation_stability,
)


class NegativePairTruthTests(unittest.TestCase):
    def test_pairing_uses_each_program_once_and_never_same_problem(self):
        records = [
            {
                "sample_id": "g{:03d}".format(index),
                "validation_source": "root/code.p{:03d}.A.java".format(index % 4),
            }
            for index in range(8)
        ]
        pairs = pair_records(records)
        flattened = [row["sample_id"] for pair in pairs for row in pair]
        self.assertEqual(len(flattened), len(set(flattened)))
        self.assertTrue(all(
            problem_id(left) != problem_id(right) for left, right in pairs
        ))

    def test_mapped_selection_ignores_unmapped_nodes(self):
        self.assertEqual(mapped_selection({0, 2, 7}, {0: 3, 2: 5}), {3, 5})

    def test_relation_stability_maps_both_graph_sides(self):
        before = {"relations": [
            {"left_node": 0, "right_node": 1},
            {"left_node": 2, "right_node": 3},
        ]}
        after = {"relations": [
            {"left_node": 10, "right_node": 21},
            {"left_node": 12, "right_node": 23},
        ]}
        self.assertEqual(
            relation_stability(
                before, after, {0: 10, 2: 12}, {1: 21, 3: 23}
            ),
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
