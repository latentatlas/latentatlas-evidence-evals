import json
import shutil
import tempfile
import unittest
from pathlib import Path

from latentatlas.authority_action_review import verify_authority_action_review_artifact


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "data" / "authority_action_v0_8_internal_review"


class AuthorityActionReviewArtifactTests(unittest.TestCase):
    def test_public_artifact_passes_integrity_verification(self):
        report = verify_authority_action_review_artifact(ARTIFACT_DIR)

        self.assertEqual("pass", report["status"], report["failure_reasons"])
        self.assertEqual(100, report["reviewed_cases"])
        self.assertEqual(1, report["public_files_verified"])
        self.assertEqual(5, report["source_files_verified"])

    def test_tampered_summary_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied = Path(temp_dir) / "artifact"
            shutil.copytree(ARTIFACT_DIR, copied)
            summary_path = copied / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["review"]["action_agreement_count"] = 99
            summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

            report = verify_authority_action_review_artifact(
                copied,
                repository_root=ROOT,
            )

            self.assertEqual("fail", report["status"])
            self.assertIn("SHA-256 mismatch: summary.json", report["failure_reasons"])
            self.assertIn(
                "unexpected review value for action_agreement_count",
                report["failure_reasons"],
            )

    def test_review_is_not_misrepresented_as_independent(self):
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual("internal_blind_author_review", summary["review"]["review_type"])
        self.assertFalse(summary["quality_gate"]["independent_review_complete"])
        self.assertFalse(summary["quality_gate"]["full_run_enabled"])
        self.assertEqual("aggregate_only", summary["data_handling"]["release_level"])


if __name__ == "__main__":
    unittest.main()
