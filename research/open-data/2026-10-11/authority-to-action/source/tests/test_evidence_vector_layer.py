import json
import tempfile
from pathlib import Path
import unittest

from latentatlas.evidence_vector_layer import VECTOR_LAYER_VERSION
from latentatlas.evidence_vector_layer import run_evidence_vector_layer


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


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


def query(decision_id: str, query_or_claim: str):
    return {
        "decision_id": decision_id,
        "query_or_claim": query_or_claim,
        "policy": "audit_safe",
        "domain_context": "enterprise_it_policy",
    }


class LatentAtlasEvidenceVectorLayerTests(unittest.TestCase):
    def test_run_writes_pass_manifest_and_required_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources.jsonl"
            queries = root / "queries.jsonl"
            out_dir = root / "run"
            write_jsonl(sources, [valid_source()])
            write_jsonl(
                queries,
                [
                    query(
                        "indexed-remote-access-001",
                        "Can we approve contractor remote access after security training and manager approval are complete",
                    ),
                    query("indexed-contract-renewal-002", "Does contract ACME-42 permit automatic renewal"),
                ],
            )

            manifest = run_evidence_vector_layer(source_path=sources, query_path=queries, out_dir=out_dir)

            self.assertEqual(manifest["status"], "pass")
            self.assertEqual(manifest["vector_layer_version"], VECTOR_LAYER_VERSION)
            self.assertEqual(manifest["adapter"]["active"], "local")
            self.assertFalse(manifest["adapter"]["external_services_used"])
            self.assertFalse(manifest["adapter"]["production_truth_mutation"])
            self.assertEqual(
                [gate["name"] for gate in manifest["gates"]],
                [
                    "build_index",
                    "query_index",
                    "schema_validation",
                    "qualification",
                    "decision_verification",
                ],
            )
            self.assertEqual(manifest["outputs"]["manifest"], str(out_dir / "evidence_vector_layer_manifest.json"))
            for path in manifest["outputs"].values():
                self.assertTrue(Path(path).exists(), path)

            decision_summary = json.loads((out_dir / "decision_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(decision_summary["false_evidence_allow_count"], 0)
            self.assertEqual(decision_summary["needs_context_or_review_coerced_to_allow_count"], 0)

    def test_unsupported_adapter_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources.jsonl"
            queries = root / "queries.jsonl"
            write_jsonl(sources, [valid_source()])
            write_jsonl(queries, [query("q1", "Can we approve contractor remote access")])

            with self.assertRaisesRegex(ValueError, "Unsupported evidence vector layer adapter"):
                run_evidence_vector_layer(
                    source_path=sources,
                    query_path=queries,
                    out_dir=root / "run",
                    adapter="qdrant",
                )

    def test_blocked_source_field_stops_before_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources.jsonl"
            queries = root / "queries.jsonl"
            source = valid_source()
            source["customer_email"] = "person@example.com"
            write_jsonl(sources, [source])
            write_jsonl(queries, [query("q1", "Can we approve contractor remote access")])

            with self.assertRaisesRegex(ValueError, "unexpected_source_field_customer_email"):
                run_evidence_vector_layer(source_path=sources, query_path=queries, out_dir=root / "run")


if __name__ == "__main__":
    unittest.main()
