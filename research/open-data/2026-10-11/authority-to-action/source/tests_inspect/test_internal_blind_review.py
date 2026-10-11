from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from evals.authority_action_internal_review import DEFAULT_DATASET
from evals.authority_action_internal_review import MASKED_PACKET_FORBIDDEN
from evals.authority_action_internal_review import REVIEW_COLUMNS
from evals.authority_action_internal_review import analyze_review
from evals.authority_action_internal_review import build_review_artifacts
from evals.authority_action_internal_review import read_jsonl


class InternalBlindReviewTests(unittest.TestCase):
    def build(self, directory: Path) -> None:
        build_review_artifacts(dataset_path=DEFAULT_DATASET, output_dir=directory)

    def complete_responses(self, directory: Path, *, disagree_first: bool = False) -> None:
        key = {
            row["review_id"]: row
            for row in read_jsonl(directory / "answer_key.jsonl")
        }
        response_path = directory / "review_responses.csv"
        with response_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for index, row in enumerate(rows):
            action = str(key[row["review_id"]]["expected_action"])
            if disagree_first and index == 0:
                action = "withhold" if action == "execute" else "execute"
            row.update(
                {
                    "reviewer_id": "internal-reviewer-01",
                    "reviewed_action": action,
                    "evidence_sufficient": "yes",
                    "single_decision_clear": "yes",
                    "realism_score": "4",
                    "difficulty_score": "4",
                    "issue_codes": "none",
                    "rationale_short": "The written records support one exact decision.",
                }
            )
        with response_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REVIEW_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    def test_build_produces_opaque_complete_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            self.build(output)
            packet = read_jsonl(output / "review_packet.jsonl")

            self.assertEqual(100, len(packet))
            self.assertEqual({"review_id", "input"}, set(packet[0]))
            rendered = "\n".join(str(row) for row in packet).lower()
            for token in MASKED_PACKET_FORBIDDEN:
                self.assertNotIn(token, rendered)

    def test_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            self.build(Path(first))
            self.build(Path(second))

            for name in ("review_packet.jsonl", "review_responses.csv", "answer_key.jsonl"):
                self.assertEqual((Path(first) / name).read_bytes(), (Path(second) / name).read_bytes())

    def test_blank_template_reports_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            self.build(output)
            report = analyze_review(
                response_path=output / "review_responses.csv",
                answer_key_path=output / "answer_key.jsonl",
            )

            self.assertEqual("incomplete", report["status"])
            self.assertEqual(100, report["incomplete_count"])
            self.assertFalse(report["full_run_gate"]["full_run_enabled"])

    def test_complete_agreeing_review_is_ready_for_successor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            self.build(output)
            self.complete_responses(output)
            report = analyze_review(
                response_path=output / "review_responses.csv",
                answer_key_path=output / "answer_key.jsonl",
                require_complete=True,
            )

            self.assertEqual("ready_to_freeze_successor", report["status"])
            self.assertEqual(100, report["action_agreement_count"])
            self.assertEqual(0, report["adjudication_required_count"])
            self.assertFalse(report["full_run_gate"]["full_run_enabled"])

    def test_disagreement_routes_to_adjudication(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            self.build(output)
            self.complete_responses(output, disagree_first=True)
            report = analyze_review(
                response_path=output / "review_responses.csv",
                answer_key_path=output / "answer_key.jsonl",
                require_complete=True,
            )

            self.assertEqual("needs_adjudication", report["status"])
            self.assertEqual(1, report["adjudication_required_count"])
            self.assertEqual("adjudicate_flagged_cases", report["full_run_gate"]["next_action"])


if __name__ == "__main__":
    unittest.main()
