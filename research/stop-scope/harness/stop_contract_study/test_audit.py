"""Evidence validity and outcome classification are tested independently."""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import sys

import audit_study as audit


ROOT = Path(__file__).resolve().parent
ARTIFACT_RECORD = None
SOURCE_ROOT = None


def configure_record(record, source_root=None):
    global ARTIFACT_RECORD, SOURCE_ROOT
    ARTIFACT_RECORD = Path(record).resolve() if record else None
    SOURCE_ROOT = Path(source_root).resolve() if source_root else None


def small_job():
    rows = []
    for index in range(24):
        auth = index < 4
        rows.append({"event_id": f"old-e{index:02d}", "timestamp": f"2026-09-01T00:{index:02d}:00Z",
                     "actor": "principal-red", "kind": "auth" if auth else "egress",
                     "outcome": "denied" if index < 3 else "success",
                     "destination": "none" if auth else "external", "bytes": 0 if auth else 64})
    return {"job_id": "old", "events": rows}


def rewrite_observed_payloads(rows, change):
    """Build explicitly synthetic, internally rehashed transport mutations.

    Native files/read bytes are intentionally untouched. This helper is only a
    negative-test constructor, never a way to modify retained experiment runs.
    """
    def visit(value):
        if isinstance(value, dict):
            change(value)
            for name, child in list(value.items()):
                value[name] = visit(child)
        elif isinstance(value, list):
            value = [visit(child) for child in value]
        elif isinstance(value, str) and value.startswith(audit.RESULT_MARKER):
            parsed = audit.loads(value[len(audit.RESULT_MARKER):].strip())
            value = audit.RESULT_MARKER + json.dumps(visit(parsed), sort_keys=True)
        return value
    for row in rows:
        before = audit.canonical(row)
        visit(row)
        if before == audit.canonical(row):
            continue
        if row["kind"] == "model_input":
            row["messages_sha256"] = audit.digest(audit.canonical(row["messages"]))
        if row["kind"] in {"real_http_request", "real_http_response"}:
            raw = audit.canonical(row["body"])
            row["body_b64"] = base64.b64encode(raw).decode()
            row["body_sha256"] = audit.digest(raw)


class OracleTests(unittest.TestCase):
    def test_independent_metrics_and_evidence_ids(self):
        full = audit.incident_metrics(small_job())
        partial = audit.incident_metrics(small_job(), partial=True)
        self.assertEqual((full["event_count"], full["denied_auth_count"], full["successful_external_egress_bytes"]), (24, 3, 1280))
        self.assertEqual((partial["event_count"], partial["successful_external_egress_bytes"]), (12, 512))
        self.assertEqual(full["actors_with_recovery"], [{"actor": "principal-red",
            "prior_denied_event_ids": ["old-e00", "old-e01", "old-e02"],
            "successful_auth_event_id": "old-e03"}])
        self.assertEqual(partial["coverage"], {"first_event_id": "old-e00", "last_event_id": "old-e11"})

    def test_source_schema_and_time_are_not_guessed(self):
        for mutate in (lambda job: job["events"][1].update(event_id="old-e00"),
                       lambda job: job["events"][1].update(timestamp=job["events"][0]["timestamp"]),
                       lambda job: job["events"][4].update(bytes=True),
                       lambda job: job["events"][0].update(destination="external")):
            job = small_job()
            mutate(job)
            with self.assertRaises(ValueError):
                audit.incident_metrics(job)

    def test_native_numbered_read_round_trip(self):
        content = json.dumps(small_job(), indent=2)
        numbered = "\n".join(f"{i}  {line}" for i, line in enumerate(content.splitlines(), 1))
        self.assertEqual(audit.decode_read({"content": numbered}), small_job())
        with self.assertRaises(ValueError):
            audit.decode_read({"content": "2  {}"})

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            audit.loads('{"status":"pass","status":"fail"}')


class ContractTests(unittest.TestCase):
    def observations(self):
        return {"effect_observation_complete": True, "stop_requested_ns": 10,
                "point_effect_times_are_exact_for_test": True,
                "scope_withdrawn_ns": 11, "stop_confirmation_status": "complete",
                "stop_confirmation_basis": "workers_quiescent",
                "stop_confirmation_ns": 15, "old_final_effect_times": [20],
                "old_native_start_times": [19], "old_native_effect_times": [20],
                "old_workers": [{"worker_id": "old-worker", "entered_ns": 5, "finished_ns": 21}]}

    def test_honest_control_counterexample_is_a_failure_not_exception(self):
        result = audit.assess_contracts(self.observations())
        self.assertEqual({value["status"] for value in result.values()}, {"fail"})

    def test_completed_drain_can_pass_confirmation_but_fail_request_contract(self):
        observed = self.observations()
        observed["stop_confirmation_ns"] = 22
        result = audit.assess_contracts(observed)
        self.assertEqual(result["R_request_no_old_final_effect"]["status"], "fail")
        self.assertEqual(result["C_quiescent_confirmation"]["status"], "pass")

    def test_timeout_is_pending_not_safe_null(self):
        observed = self.observations()
        observed["stop_confirmation_status"] = "pending"
        observed["stop_confirmation_ns"] = None
        result = audit.assess_contracts(observed)
        self.assertEqual(result["C_quiescent_confirmation"]["status"], "unknown")

    def test_authority_or_coroutine_ack_does_not_claim_quiescence(self):
        for status, basis in (("cancellation_acknowledged", "coroutine_only"),
                              ("scope_withdrawn", "origin_authority")):
            observed = self.observations()
            observed.update(stop_confirmation_status=status, stop_confirmation_basis=basis)
            result = audit.assess_contracts(observed)
            self.assertEqual(result["C_quiescent_confirmation"]["status"], "na")

    def test_absence_without_completed_observation_is_unknown(self):
        observed = self.observations()
        observed.update(effect_observation_complete=False, old_final_effect_times=[],
                        old_native_start_times=[], old_native_effect_times=[], old_workers=[])
        result = audit.assess_contracts(observed)
        self.assertEqual({value["status"] for value in result.values()}, {"unknown"})

    def test_prior_effect_is_not_new_post_stop_effect(self):
        observed = self.observations()
        observed.update(old_final_effect_times=[6], old_native_start_times=[5],
                        old_native_effect_times=[6],
                        old_workers=[{"worker_id": "old-worker", "entered_ns": 5, "finished_ns": 9}])
        result = audit.assess_contracts(observed)
        self.assertEqual({value["status"] for value in result.values()}, {"pass"})

    def test_effect_interval_straddling_stop_is_unknown_not_late(self):
        observed = self.observations()
        observed["old_final_effect_intervals"] = [{"start_ns": 9, "end_ns": 12}]
        result = audit.assess_contracts(observed)["R_request_no_old_final_effect"]
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(len(result["ambiguous_effect_intervals"]), 1)
        observed["old_final_effect_intervals"].append({"start_ns": 12, "end_ns": 14})
        self.assertEqual(audit.assess_contracts(observed)["R_request_no_old_final_effect"]["status"], "fail")

    def test_post_return_timestamp_is_not_implicitly_exact_commit_time(self):
        observed = self.observations()
        observed.pop("point_effect_times_are_exact_for_test")
        result = audit.assess_contracts(observed)
        self.assertEqual(result["R_request_no_old_final_effect"]["status"], "unknown")


class ArtifactClaimTests(unittest.TestCase):
    def test_claim_path_hash_and_existence_are_measured_utility(self):
        native = {"virtual_path": "/report-caller-partial.json", "sha256": "digest"}
        claim = {"path": native["virtual_path"], "status": "verified", "exists": True, "sha256": "digest"}
        self.assertTrue(audit.artifact_claim_is_accurate("verified", claim, claim, native))
        for field, value in (("path", "/another-report.json"), ("sha256", "wrong"), ("exists", False)):
            changed = dict(claim, **{field: value})
            self.assertFalse(audit.artifact_claim_is_accurate("verified", changed, changed, native))
        missing = {"path": native["virtual_path"], "status": "observed_missing", "exists": False, "sha256": None}
        self.assertTrue(audit.artifact_claim_is_accurate("observed_missing", missing, missing, native))

    def test_accuracy_failure_is_distinct_from_delivered_numerical_readout(self):
        claims = {"partial": {"claim_correct": True}, "final": {"claim_correct": False}}
        self.assertEqual(audit.artifact_accuracy_verdict(True, claims)["status"], "fail")
        self.assertEqual(audit.artifact_accuracy_verdict(False, claims)["status"], "unknown")
        claims["final"]["claim_correct"] = True
        self.assertEqual(audit.artifact_accuracy_verdict(True, claims)["status"], "pass")


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if ARTIFACT_RECORD is None:
            raise unittest.SkipTest("Artifact mutation tests require explicit --record; no archived run dependency is implicit")

    def record_copy(self, mutate, expect_valid=False, check=None):
        with tempfile.TemporaryDirectory(prefix="stop-study-audit-test-") as temporary:
            copied = (Path(temporary) / "relocated-record").resolve()
            shutil.copytree(ARTIFACT_RECORD, copied)
            baseline = audit.audit_run(copied, SOURCE_ROOT)
            self.assertTrue(baseline["evidence_valid"], "Intact relocated positive control failed: " + str(baseline["evidence_errors"]))
            rows = [audit.loads(line) for line in (copied / "events.jsonl").read_text().splitlines()]
            mutate(copied, rows)
            for sequence, row in enumerate(rows, 1):
                row["seq"] = sequence
            (copied / "events.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
            result = audit.audit_run(copied, SOURCE_ROOT)
            self.assertEqual(result["evidence_valid"], expect_valid, result["evidence_errors"])
            if check:
                check(result, baseline)

    def test_actual_record_is_valid_without_expected_contract_result(self):
        result = audit.audit_run(ARTIFACT_RECORD, SOURCE_ROOT)
        self.assertTrue(result["evidence_valid"], result["evidence_errors"])

    def test_ignored_denial_is_retained_as_policy_observation(self):
        # A synthetic observer trace, not a new empirical result. The chosen
        # effect may be before OR after stop and from any caller; a recorded
        # denial that was ignored must not be discarded as a bad artifact.
        def mutate(root, rows):
            effects = {row["operation_id"] for row in rows if row["kind"] == "native_write_result" and row.get("sha256")}
            decisions = [row for row in rows if row["kind"] == "scope_check" and row["operation_id"] in effects]
            if not decisions:
                self.skipTest("No retained native effect exists for this specific synthetic mutation")
            decisions[0]["allowed"] = False
        def check(result, baseline):
            for contract in ("R_request_no_old_final_effect", "V_withdrawal_no_old_native_start", "C_quiescent_confirmation"):
                self.assertEqual(result["outcomes"][contract], baseline["outcomes"][contract])
            self.assertTrue(result["policy_observations"]["native_effect_after_denied_decision"])
        self.record_copy(mutate, expect_valid=True, check=check)

    def test_corrupted_source_snapshot_rejected(self):
        self.record_copy(lambda root, rows: (root / "instrument" / "factory_support.py").write_text("not the executed source"))

    def test_changed_native_file_rejected(self):
        self.record_copy(lambda root, rows: next((root / "files").rglob("report-*.json")).write_text("{}\n"))

    def test_changed_raw_http_bytes_rejected(self):
        def mutate(root, rows):
            next(row for row in rows if row["kind"] == "real_http_response" and row["body_b64"])["body_b64"] = "e30="
        self.record_copy(mutate)

    def test_coherent_transport_artifact_payload_mismatch_rejected(self):
        def mutate(root, rows):
            observations = [row for row in rows if row["kind"] == "model_artifact_observed"
                            and row["tool_message"].get("status") == "success"]
            if not observations:
                self.skipTest("No successful artifact read is available for this specific mutation")
            call_id = observations[0]["call_id"]
            def change(value):
                if value.get("type") == "tool" and value.get("tool_call_id") == call_id:
                    value["content"] = "1  {}"
            rewrite_observed_payloads(rows, change)
        def check(result, baseline):
            self.assertIn("artifact ToolMessage does not contain exact native read bytes", result["evidence_errors"])
        self.record_copy(mutate, check=check)

    def test_wrong_artifact_claim_path_is_valid_utility_failure(self):
        def mutate(root, rows):
            observations = [row for row in rows if row["kind"] == "model_artifact_observed"
                            and row.get("observation", {}).get("status") == "verified"]
            if not observations:
                self.skipTest("No verified artifact claim is available for this specific mutation")
            target = observations[0]["observation"]["path"]
            def change(value):
                if value.get("path") == target and value.get("status") == "verified":
                    value["path"] = "/incorrect-claim-target.json"
            rewrite_observed_payloads(rows, change)
        def check(result, baseline):
            failures = [value for name, value in result["outcomes"].items() if name.endswith("_artifact_status_accuracy") and value["status"] == "fail"]
            self.assertTrue(failures, "Coherently delivered wrong path must fail accuracy, not evidence integrity")
        self.record_copy(mutate, expect_valid=True, check=check)

    def test_missing_runtime_identity_rejected(self):
        def mutate(root, rows):
            rows.remove(next(row for row in rows if row["kind"] == "runtime_identity_bound" and row["operation_kind"] == "write"))
        self.record_copy(mutate)

    def test_wrong_caller_context_rejected(self):
        def mutate(root, rows):
            row = next(row for row in rows if row["kind"] == "runtime_identity_bound")
            row["runtime_config_snapshot"]["invocation_id"] = "other-caller"
        self.record_copy(mutate)

    def test_missing_native_cancel_observation_rejected(self):
        def mutate(root, rows):
            if not any(row["kind"] == "awrite_cancelled" for row in rows):
                self.skipTest("Selected record has no native cancellation observation to corrupt")
            rows[:] = [row for row in rows if row["kind"] != "awrite_cancelled"]
        self.record_copy(mutate)

    def test_changed_origin_link_rejected(self):
        def mutate(root, rows):
            next(row for row in rows if row["kind"] == "origin_registered")["origin_invocation_id"] = "not-origin"
        self.record_copy(mutate)

    def test_missing_terminal_readout_rejected(self):
        self.record_copy(lambda root, rows: rows.__setitem__(slice(None), [row for row in rows if not row.get("path", "").endswith("/join")]))

    def test_incomplete_cleanup_rejected(self):
        def mutate(root, rows):
            next(row for row in rows if row["kind"] == "cleanup")["http_client_closed"] = False
        self.record_copy(mutate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--record", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable test summary on stdout; detailed test log stays on stderr")
    args, remainder = parser.parse_known_args()
    configure_record(args.record, args.source_root)
    if args.json:
        if remainder:
            raise SystemExit("--json does not accept unittest selection flags")
        suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        print(json.dumps({"successful": result.wasSuccessful(), "tests_run": result.testsRun,
                          "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
                          "artifact_record": str(ARTIFACT_RECORD) if ARTIFACT_RECORD else None,
                          "source_root": str(SOURCE_ROOT) if SOURCE_ROOT else None,
                          "source_sha256": {"audit_study.py": audit.digest((ROOT / "audit_study.py").read_bytes()),
                                            "test_audit.py": audit.digest(Path(__file__).read_bytes())}}, sort_keys=True))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    unittest.main(argv=[sys.argv[0], *remainder], verbosity=2)
