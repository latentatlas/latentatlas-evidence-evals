import json
import shutil
import tempfile
import unittest
from pathlib import Path

from latentatlas.frozen_review import verify_frozen_review_artifact


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "data" / "frozen_masked_review_v1"


class FrozenReviewArtifactTests(unittest.TestCase):
    def test_public_artifact_passes_integrity_verification(self):
        report = verify_frozen_review_artifact(ARTIFACT_DIR)

        self.assertEqual("pass", report["status"], report["failure_reasons"])
        self.assertEqual(2, report["files_verified"])
        self.assertEqual(146, report["outcome_count"])
        self.assertEqual("p0_review_freeze_6c1465ff0c315da6", report["source_freeze_id"])

    def test_tampered_summary_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            copied = Path(temp_dir) / "artifact"
            shutil.copytree(ARTIFACT_DIR, copied)
            summary_path = copied / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["outcomes"][0]["count"] = 100
            summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

            report = verify_frozen_review_artifact(copied)

            self.assertEqual("fail", report["status"])
            self.assertTrue(report["failure_reasons"])

    def test_release_is_aggregate_only(self):
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((ARTIFACT_DIR / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual("aggregate_only", summary["data_handling"]["release_level"])
        self.assertFalse(summary["data_handling"]["contains_customer_data"])
        self.assertFalse(summary["data_handling"]["contains_personal_data"])
        self.assertFalse(summary["data_handling"]["contains_row_level_records"])
        self.assertEqual("aggregate_only", manifest["data_handling"]["release_level"])

    def test_public_artifact_contains_no_private_workspace_markers(self):
        forbidden = (
            "/Us" + "ers/",
            "reviewer01" + "_hsyn",
            "queue" + "_id",
            "event" + "_id",
            "source_subject" + "_hash",
            "masked_state" + "_before",
            "masked_state" + "_after",
            "@",
        )

        for path in ARTIFACT_DIR.iterdir():
            text = path.read_text(encoding="utf-8").lower()
            for marker in forbidden:
                self.assertNotIn(marker.lower(), text, f"{marker} found in {path.name}")


if __name__ == "__main__":
    unittest.main()
