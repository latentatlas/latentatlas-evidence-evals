import json
import shutil
import tempfile
import unittest
from pathlib import Path

from latentatlas.authority_action_full_result import (
    verify_authority_action_full_result_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "data" / "authority_action_v0_8_2_full_medium"


class AuthorityActionFullResultArtifactTests(unittest.TestCase):
    def test_public_artifact_passes_integrity_verification(self):
        report = verify_authority_action_full_result_artifact(ARTIFACT_DIR)

        self.assertEqual("pass", report["status"], report["failure_reasons"])
        self.assertEqual(600, report["completed_analytical_runs"])
        self.assertEqual(2, report["public_files_verified"])
        self.assertEqual(3, report["source_files_verified"])

    def test_tampered_summary_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied = Path(temp_dir) / "artifact"
            shutil.copytree(ARTIFACT_DIR, copied)
            summary_path = copied / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["results"][0]["correct_decisions"] = 299
            summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

            report = verify_authority_action_full_result_artifact(
                copied,
                repository_root=ROOT,
            )

            self.assertEqual("fail", report["status"])
            self.assertIn("SHA-256 mismatch: summary.json", report["failure_reasons"])
            self.assertIn(
                "unexpected correct_decisions for openai/gpt-5.6-sol",
                report["failure_reasons"],
            )

    def test_release_excludes_private_run_material(self):
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual("aggregate_only", summary["data_handling"]["release_level"])
        self.assertFalse(summary["data_handling"]["contains_raw_transcripts"])
        self.assertFalse(summary["data_handling"]["contains_provider_payloads"])
        self.assertFalse(summary["data_handling"]["contains_credentials"])
        self.assertFalse(summary["data_handling"]["contains_live_credit_snapshots"])
        self.assertFalse(summary["review"]["independent_external_review_complete"])


if __name__ == "__main__":
    unittest.main()
