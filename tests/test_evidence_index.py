import unittest

from latentatlas.evidence_guard import EvidenceGuard
from latentatlas.evidence_index import INDEX_VERSION
from latentatlas.evidence_index import build_evidence_index
from latentatlas.evidence_index import query_evidence_index
from latentatlas.evidence_index import summarize_index_build
from latentatlas.evidence_index import summarize_index_query
from latentatlas.schema_validator import validate_packets


def valid_metadata():
    return {
        "owner": "security-policy-owner",
        "source_status": "approved",
        "source_authority": "authoritative",
        "review_state": "current",
        "effective_state": "active",
        "source_family": "security-policy",
        "origin_id": "remote-access-policy-2026",
        "published_at": "2026-04-01",
        "effective_from": "2026-04-01",
        "effective_to": "2026-12-31",
        "as_of_date": "2026-07-06",
        "support_axes": ["claim_subject", "approval_condition", "traceability"],
    }


def valid_source():
    return {
        "source_id": "policy-remote-access-2026-section-12",
        "text": (
            "Contractor remote access can be approved when security training and "
            "documented manager approval are complete. The request must include "
            "requester, contractor sponsor, access scope, expiration date, and "
            "ticket reference before activation."
        ),
        "source_type": "policy",
        "source_uri": "local://policies/remote-access#12",
        "metadata": valid_metadata(),
    }


def valid_query():
    return {
        "decision_id": "indexed-remote-access-001",
        "query_or_claim": (
            "Can we approve contractor remote access after security training and "
            "manager approval are complete"
        ),
        "policy": "audit_safe",
        "domain_context": "enterprise_it_policy",
    }


class LatentAtlasEvidenceIndexTests(unittest.TestCase):
    def test_build_index_preserves_audit_boundary_without_external_services(self):
        index_rows, validations = build_evidence_index([valid_source()])

        self.assertEqual(len(index_rows), 1)
        self.assertEqual(validations[0]["index_status"], "confirmed")
        row = index_rows[0]
        self.assertEqual(row["index_version"], INDEX_VERSION)
        self.assertEqual(row["index_status"], "confirmed")
        self.assertIn("source_hash", row)
        self.assertIn("text_hash", row)
        self.assertEqual(row["evidence"]["metadata"]["owner"], "security-policy-owner")

        summary = summarize_index_build("sources.jsonl", "index.jsonl", index_rows, validations)
        self.assertFalse(summary["external_services_used"])
        self.assertFalse(summary["production_truth_mutation"])
        self.assertEqual(summary["index_status_counts"], {"confirmed": 1})

    def test_query_outputs_schema_clean_packet_without_index_fields(self):
        index_rows, _ = build_evidence_index([valid_source()])
        packets, validations = query_evidence_index(index_rows, [valid_query()], limit=3)

        self.assertEqual(validations[0]["query_status"], "confirmed")
        self.assertEqual(len(packets), 1)
        packet = packets[0]
        self.assertEqual(
            set(packet),
            {"decision_id", "query_or_claim", "candidate_evidence", "policy", "domain_context"},
        )
        self.assertEqual(len(packet["candidate_evidence"]), 1)
        candidate = packet["candidate_evidence"][0]
        self.assertEqual(
            set(candidate),
            {"evidence_id", "text", "source_type", "source_uri", "retrieval_score", "metadata"},
        )
        self.assertNotIn("source_hash", candidate)
        self.assertGreaterEqual(candidate["retrieval_score"], 0.72)

        schema = validate_packets(packets)
        self.assertEqual(schema[0]["schema_verdict"], "confirmed")

        decision = EvidenceGuard().qualify_packet(packet)
        self.assertEqual(decision["evidence_verdict"], "confirmed_evidence")
        self.assertEqual(decision["recommended_action"], "allow_answer")

    def test_query_summary_records_packet_hash_and_no_mutation(self):
        index_rows, _ = build_evidence_index([valid_source()])
        packets, validations = query_evidence_index(index_rows, [valid_query()], limit=3)
        summary = summarize_index_query(
            "index.jsonl",
            "queries.jsonl",
            "packets.jsonl",
            index_rows,
            packets,
            validations,
            limit=3,
            min_score=0.01,
        )

        self.assertEqual(summary["candidate_count"], 1)
        self.assertEqual(summary["empty_candidate_packet_count"], 0)
        self.assertIn("packet_hash", summary)
        self.assertFalse(summary["external_services_used"])
        self.assertFalse(summary["production_truth_mutation"])

    def test_build_blocks_unexpected_source_fields_before_indexing(self):
        source = valid_source()
        source["customer_email"] = "person@example.com"

        with self.assertRaisesRegex(ValueError, "unexpected_source_field_customer_email"):
            build_evidence_index([source])

    def test_build_blocks_empty_source_input(self):
        with self.assertRaisesRegex(ValueError, "empty source input"):
            build_evidence_index([])

    def test_query_blocks_invalid_index_version(self):
        index_rows, _ = build_evidence_index([valid_source()])
        index_rows[0]["index_version"] = "stale_index_version"

        with self.assertRaisesRegex(ValueError, "invalid_index_version"):
            query_evidence_index(index_rows, [valid_query()], limit=3)

    def test_query_blocks_empty_query_input(self):
        index_rows, _ = build_evidence_index([valid_source()])

        with self.assertRaisesRegex(ValueError, "empty query input"):
            query_evidence_index(index_rows, [], limit=3)

    def test_query_preserves_empty_candidate_packets_for_downstream_review(self):
        index_rows, _ = build_evidence_index([valid_source()])
        unrelated_query = {
            "decision_id": "indexed-unrelated-002",
            "query_or_claim": "Does contract ACME-42 permit automatic renewal",
            "policy": "audit_safe",
            "domain_context": "contract_review",
        }

        packets, _ = query_evidence_index(index_rows, [unrelated_query], limit=3)

        self.assertEqual(packets[0]["candidate_evidence"], [])
        schema = validate_packets(packets)
        self.assertEqual(schema[0]["schema_verdict"], "needs_review")
        decision = EvidenceGuard().qualify_packet(packets[0])
        self.assertEqual(decision["evidence_verdict"], "needs_context")
        self.assertEqual(decision["recommended_action"], "request_more_context")


if __name__ == "__main__":
    unittest.main()
