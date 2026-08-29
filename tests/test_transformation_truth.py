from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_transformation_explanation_truth import (  # noqa: E402
    alpha_rename,
    insert_dead_code,
)
from scripts.finalize_transformation_explanation_truth import lcs_mapping  # noqa: E402


class TransformationTruthTests(unittest.TestCase):

    def test_alpha_rename_skips_comments_and_literals(self):
        source = '''
public class Main {
  public static void main(String[] args) {
    int count = 1; // count is documented
    String text = "count";
    System.out.println(count + text.length());
  }
}
'''
        transformed, mapping = alpha_rename(source)
        self.assertIn("count", mapping)
        self.assertIn("text", mapping)
        self.assertIn("// count is documented", transformed)
        self.assertIn('"count"', transformed)
        self.assertNotIn("int count =", transformed)
        self.assertNotIn("String text =", transformed)

    def test_dead_code_has_unique_marker_and_no_output_effect_when_guard_is_zero(self):
        source = '''
public class Main {
  public static void main(String[] args) {
    System.out.println(1);
  }
}
'''
        transformed, marker = insert_dead_code(source)
        self.assertIn("int {} = 0;".format(marker), transformed)
        self.assertIn("if ({} != 0)".format(marker), transformed)
        self.assertIn('System.out.print("")', transformed)

    def test_lcs_mapping_marks_only_inserted_nodes_unmatched(self):
        original = ["read", "compute", "print"]
        transformed = ["dead init", "dead guard", "read", "compute", "print"]
        mapping = lcs_mapping(original, transformed)
        self.assertEqual([(0, 2), (1, 3), (2, 4)], mapping)
        self.assertEqual({0, 1}, set(range(len(transformed))) - {b for _, b in mapping})


if __name__ == "__main__":
    unittest.main()
