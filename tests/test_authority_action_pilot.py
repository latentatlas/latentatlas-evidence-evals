import json
import shutil
import tempfile
import unittest
from pathlib import Path

from latentatlas.authority_action_pilot import verify_authority_action_pilot_artifact


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "data" / "authority_action_v0_7_pilot"


class AuthorityActionPilotArtifactTests(unittest.TestCase):
    def test_public_artifact_passes_integrity_verification(self):
        report = verify_authority_action_pilot_artifact(ARTIFACT_DIR)

        self.assertEqual("pass", report["status"], report["failure_reasons"])
        self.assertEqual(80, report["completed_sample_runs"])
        self.assertEqual(1, report["public_files_verified"])
        self.assertEqual(4, report["source_files_verified"])

    def test_tampered_summary_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied = Path(temp_dir) / "artifact"
            shutil.copytree(ARTIFACT_DIR, copied)
            summary_path = copied / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["results"][0]["correct_decisions"] = 39
            summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

            report = verify_authority_action_pilot_artifact(
                copied,
                repository_root=ROOT,
            )

            self.assertEqual("fail", report["status"])
            self.assertIn("SHA-256 mismatch: summary.json", report["failure_reasons"])

    def test_tampered_source_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied = Path(temp_dir) / "artifact"
            shutil.copytree(ARTIFACT_DIR, copied)
            manifest_path = copied / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["source_artifacts"][0]["sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            report = verify_authority_action_pilot_artifact(
                copied,
                repository_root=ROOT,
            )

            self.assertEqual("fail", report["status"])
            self.assertTrue(
                any(
                    reason.startswith("source SHA-256 mismatch")
                    for reason in report["failure_reasons"]
                )
            )

    def test_release_is_aggregate_only(self):
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((ARTIFACT_DIR / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual("aggregate_only", summary["data_handling"]["release_level"])
        self.assertFalse(summary["data_handling"]["contains_prompts"])
        self.assertFalse(summary["data_handling"]["contains_completions"])
        self.assertFalse(summary["data_handling"]["contains_provider_payloads"])
        self.assertFalse(summary["data_handling"]["contains_credentials"])
        self.assertEqual("aggregate_only", manifest["data_handling"]["release_level"])


if __name__ == "__main__":
    unittest.main()
