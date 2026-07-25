from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evals.experiment_control import DEFAULT_MANIFEST
from evals.experiment_control import LEGACY_MANIFEST
from evals.experiment_control import load_manifest
from evals.experiment_control import verify_manifest


class ExperimentControlTests(unittest.TestCase):
    def test_frozen_manifest_verifies(self) -> None:
        result = verify_manifest()

        self.assertEqual(result["sample_count"], 24)
        self.assertEqual(result["pilot_sample_count"], 6)
        self.assertEqual(result["pricing_as_of"], "2026-07-25")
        self.assertEqual(result["task_version"], "0.3.0")
        self.assertLessEqual(result["worst_case_full_cost_usd"], 10.0)

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


if __name__ == "__main__":
    unittest.main()
