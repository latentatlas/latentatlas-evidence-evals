from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evals.experiment_control import DEFAULT_MANIFEST
from evals.experiment_control import LEGACY_MANIFEST
from evals.experiment_control import V0_2_MANIFEST
from evals.experiment_control import V0_4_MANIFEST
from evals.experiment_control import V0_5_MANIFEST
from evals.experiment_control import V0_6_MANIFEST
from evals.experiment_control import V0_6_1_MANIFEST
from evals.experiment_control import V0_7_MANIFEST
from evals.experiment_control import load_manifest
from evals.experiment_control import verify_manifest


class ExperimentControlTests(unittest.TestCase):
    def test_frozen_manifest_verifies(self) -> None:
        result = verify_manifest()

        self.assertEqual(result["sample_count"], 25)
        self.assertEqual(result["pilot_sample_count"], 3)
        self.assertEqual(result["pricing_as_of"], "2026-07-25")
        self.assertEqual(result["task_version"], "0.3.1")
        self.assertEqual(result["worst_case_full_cost_usd"], 7.5)
        self.assertLessEqual(result["worst_case_full_cost_usd"], 10.0)

    def test_v0_2_manifest_still_verifies(self) -> None:
        result = verify_manifest(V0_2_MANIFEST)

        self.assertEqual(result["sample_count"], 24)
        self.assertEqual(result["pilot_sample_count"], 6)
        self.assertEqual(result["task_version"], "0.3.0")

    def test_v0_4_factorial_manifest_verifies(self) -> None:
        result = verify_manifest(V0_4_MANIFEST)

        self.assertEqual(result["sample_count"], 100)
        self.assertEqual(result["pilot_sample_count"], 16)
        self.assertEqual(result["task_version"], "0.4.0")
        self.assertEqual(result["worst_case_full_cost_usd"], 9.0)
        self.assertLessEqual(result["worst_case_full_cost_usd"], 10.0)

    def test_v0_5_high_discrimination_manifest_verifies(self) -> None:
        result = verify_manifest(V0_5_MANIFEST)

        self.assertEqual(result["sample_count"], 100)
        self.assertEqual(result["pilot_sample_count"], 20)
        self.assertEqual(result["task_version"], "0.5.0")
        self.assertEqual(result["worst_case_full_cost_usd"], 9.0)
        self.assertLessEqual(result["worst_case_full_cost_usd"], 10.0)

    def test_v0_6_proof_contract_manifest_verifies(self) -> None:
        result = verify_manifest(V0_6_MANIFEST)

        self.assertEqual(result["sample_count"], 100)
        self.assertEqual(result["pilot_sample_count"], 20)
        self.assertEqual(result["task_version"], "0.6.0")
        self.assertEqual(result["worst_case_full_cost_usd"], 9.0)
        self.assertLessEqual(result["worst_case_full_cost_usd"], 10.0)

    def test_v0_6_1_cost_calibrated_pilot_manifest_verifies(self) -> None:
        result = verify_manifest(V0_6_1_MANIFEST)

        self.assertEqual(result["sample_count"], 100)
        self.assertEqual(result["pilot_sample_count"], 20)
        self.assertEqual(result["task_version"], "0.6.0")
        self.assertEqual(
            result["provider_cost_limits_usd"],
            {"anthropic": 0.04, "openai": 0.02},
        )
        self.assertEqual(result["worst_case_pilot_cost_usd"], 2.4)
        self.assertIsNone(result["worst_case_full_cost_usd"])
        self.assertFalse(result["full_stage_enabled"])

    def test_v0_6_1_pilot_budget_fails_closed(self) -> None:
        manifest = load_manifest(V0_6_1_MANIFEST)
        manifest["limits"]["total_budget_usd"] = 2.39
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "total experiment budget"):
                verify_manifest(path)

    def test_v0_7_usable_pilot_manifest_verifies(self) -> None:
        result = verify_manifest(V0_7_MANIFEST)

        self.assertEqual(result["sample_count"], 100)
        self.assertEqual(result["pilot_sample_count"], 20)
        self.assertEqual(result["task_version"], "0.7.0")
        self.assertEqual(
            result["provider_cost_limits_usd"],
            {"anthropic": 0.055, "openai": 0.02},
        )
        self.assertEqual(result["worst_case_pilot_cost_usd"], 3.0)
        self.assertIsNone(result["worst_case_full_cost_usd"])
        self.assertFalse(result["full_stage_enabled"])

    def test_v0_7_pilot_budget_fails_closed(self) -> None:
        manifest = load_manifest(V0_7_MANIFEST)
        manifest["limits"]["total_budget_usd"] = 2.99
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "total experiment budget"):
                verify_manifest(path)

    def test_legacy_pilot_manifest_still_verifies(self) -> None:
        result = verify_manifest(LEGACY_MANIFEST)

        self.assertEqual(result["task_version"], "0.2.0")
        self.assertEqual(
            result["experiment_id"],
            "latentatlas-authority-action-frontier-pilot-20260725",
        )

    def test_changed_digest_fails_closed(self) -> None:
        manifest = load_manifest()
        manifest["artifacts"]["evals/data/authority_action_cases.jsonl"] = "0" * 64
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                verify_manifest(path)

    def test_expected_action_count_mismatch_fails_closed(self) -> None:
        manifest = load_manifest()
        manifest["dataset"]["expected_withhold"] = 16
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expected-action counts mismatch"):
                verify_manifest(path)

    def test_missing_pair_member_from_pilot_fails_closed(self) -> None:
        manifest = load_manifest()
        manifest["stages"]["pilot"]["sample_ids"].remove(
            "withhold_similarity_neutral"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "IDs missing from pilot"):
                verify_manifest(path)

    def test_incomplete_v0_4_factorial_group_fails_closed(self) -> None:
        manifest = load_manifest(V0_4_MANIFEST)
        manifest["dataset"]["factorial_design"]["expected_variants"].remove(
            "invalid_treatment"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "variants mismatch"):
                verify_manifest(path)


if __name__ == "__main__":
    unittest.main()
