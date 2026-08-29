from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.audit_splits import audit_protocol  # noqa: E402
from scripts.configlib import config_paths, resolve_config, validate_config  # noqa: E402


class ExplanationReleaseTests(unittest.TestCase):
    def test_all_configs_are_valid(self):
        failures = []
        for path in config_paths():
            failures.extend(validate_config(resolve_config(path), path))
        self.assertEqual([], failures)

    def test_natural_study_uses_fixed_symmetric_budget(self):
        config = resolve_config(
            ROOT / "configs/experiments/C9_natural_validation_strong_baselines.json"
        )
        self.assertEqual(100, config["explanation"]["sample_pairs"])
        self.assertEqual(0.2, config["explanation"]["top_node_fraction"])
        self.assertIn("symmetric_semantic_optimal_pair", config["baselines"])

    def test_truth_manifests_are_present(self):
        for config_name in (
            "C8_transformation_truth_strong_baselines.json",
            "C10_codenet_transformation_truth_strong_baselines.json",
            "C15_codenet_negative_pair_transformation_truth.json",
        ):
            config = resolve_config(ROOT / "configs/experiments" / config_name)
            self.assertTrue((ROOT / config["truth"]["manifest"]).is_file())

    def test_paper_split_has_no_fragment_leakage(self):
        config = resolve_config(ROOT / "configs/protocols/paper_clean.json")
        report = audit_protocol(config, hash_sources=False)
        self.assertEqual([], report["contract_violations"])

    def test_cli_dry_run(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "research_cli.py"),
                "--config",
                str(ROOT / "configs/experiments/C9_natural_validation_strong_baselines.json"),
                "--device",
                "cuda:0",
                "--dry-run",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()

