import json
from pathlib import Path
import unittest

from latentatlas.evidence_guard import EvidenceGuard


EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "examples" / "sample_decisions.jsonl"


def load_examples():
    return [json.loads(line) for line in EXAMPLE_PATH.read_text(encoding="utf-8").splitlines() if line]


class EvidenceGuardTests(unittest.TestCase):
    def test_empty_evidence_requests_more_context(self):
        packet = next(row for row in load_examples() if row["decision_id"] == "demo-needs-context-004")
        decision = EvidenceGuard().qualify_packet(packet)
        self.assertEqual(decision["evidence_verdict"], "needs_context")
        self.assertEqual(decision["recommended_action"], "request_more_context")

    def test_false_neighbor_is_not_allowed_as_answer_evidence(self):
        packet = next(row for row in load_examples() if row["decision_id"] == "demo-quarantine-false-neighbor-005")
        decision = EvidenceGuard().qualify_packet(packet)
        self.assertNotEqual(decision["recommended_action"], "allow_answer")

    def test_audit_record_contains_input_hash_and_source_ids(self):
        packet = load_examples()[0]
        decision = EvidenceGuard().qualify_packet(packet)
        self.assertEqual(len(decision["audit"]["input_hash"]), 64)
        self.assertEqual(decision["audit"]["evidence_ids"], ["policy-remote-access-12"])


if __name__ == "__main__":
    unittest.main()
