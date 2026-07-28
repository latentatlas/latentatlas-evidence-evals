from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from latentatlas.authority_action_public_analysis import read_public_rows
from latentatlas.authority_action_public_analysis import summarize_public_rows
from latentatlas.authority_action_public_analysis import validate_public_row
from latentatlas.authority_action_public_analysis import verify_authority_action_public_analysis


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "data" / "authority_action_v0_8_3_analysis"


class AuthorityActionPublicAnalysisTests(unittest.TestCase):
    def test_public_artifact_recomputes_and_verifies(self) -> None:
        report = verify_authority_action_public_analysis(
            ARTIFACT_DIR,
            repository_root=ROOT,
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["failure_reasons"], [])
        self.assertEqual(report["rows_verified"], 600)
        self.assertEqual(report["public_files_verified"], 3)
        self.assertEqual(report["source_files_verified"], 3)

    def test_stored_summary_equals_row_recomputation(self) -> None:
        rows = read_public_rows(ARTIFACT_DIR / "rows.jsonl")
        stored = json.loads((ARTIFACT_DIR / "summary.json").read_text())

        self.assertEqual(summarize_public_rows(rows), stored)

    def test_row_schema_rejects_transcript_bearing_field(self) -> None:
        row = json.loads((ARTIFACT_DIR / "rows.jsonl").read_text().splitlines()[0])
        row["completion"] = "not public"

        with self.assertRaisesRegex(ValueError, "unexpected fields"):
            validate_public_row(row)

    def test_recomputation_detects_metric_path_disagreement(self) -> None:
        row = json.loads((ARTIFACT_DIR / "rows.jsonl").read_text().splitlines()[0])
        mutated = copy.deepcopy(row)
        mutated["decision_path"] = "strict_scope_failure"
        mutated["strict_scope_subtype"] = "single_call_schema_invalid"

        with self.assertRaisesRegex(ValueError, "decision_path disagrees"):
            validate_public_row(mutated)

    def test_error_taxonomy_and_refusal_overlap_are_explicit(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text())
        fable = summary["models"]["anthropic/claude-fable-5"]

        self.assertEqual(
            fable["strict_scope_taxonomy"]["exclusive_subtypes"],
            {
                "duplicate_call": 23,
                "single_call_schema_invalid": 3,
                "single_call_schema_valid_wrong_scope": 0,
            },
        )
        self.assertEqual(
            fable["provider_refusal_cross_tab"]["strict_scope_failure"],
            {"all_rows": 26, "provider_refusal_rows": 5},
        )
        self.assertEqual(
            fable["provider_refusal_cross_tab"]["no_action"],
            {"all_rows": 25, "provider_refusal_rows": 15},
        )


if __name__ == "__main__":
    unittest.main()
