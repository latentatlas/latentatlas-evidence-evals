from copy import deepcopy
import json
import unittest
from contract import ROOT
from audit import validate, score
from qualify import build
from queue_audit import validate_queue


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.folder = ROOT/"local-matrix-v01/create-17-before_I_admission-receiver_drain_confirm"
        self.rows = [json.loads(x) for x in (self.folder/"events.jsonl").read_text().splitlines()]

    def item(self, kind): return next(r for r in self.rows if r["kind"] == kind)

    def test_replay(self):
        outcome = score(validate(self.folder, self.rows))
        self.assertEqual(outcome["old_origin_post_policy_effects"], 0)
        self.assertEqual(outcome["queue"]["checkpoint_content_status"], "O_final_I_partial")

    def test_control_failure_is_outcome_not_invalid_evidence(self):
        for row in self.rows:
            if row["kind"] in {"scope_policy_activated", "queue_admission_check", "receiver_check"}:
                row["policy"]["effect"] = False
        outcome = score(validate(self.folder, self.rows))
        self.assertFalse(outcome["queue"]["policy_decisions_match_declared_contract"])
        self.assertTrue(outcome["queue"]["policy_decision_mismatches"])

    def test_wrong_candidate_is_measured_not_a_checkpoint_integrity_filter(self):
        evidence = validate(self.folder, self.rows)
        evidence["targets"]["I"]["request_snapshot"]["projection"]["candidate_content"] = '{"wrong":true}'
        outcome = score(evidence)
        self.assertEqual(outcome["queue"]["checkpoint_content_status"], "other_content")
        self.assertTrue(outcome["roles"]["I"]["oracle_final_delivered_any_path"])

    def test_I_unadmitted_not_a_pending_queue_future(self):
        observation = self.item("source_observation_complete")
        self.assertFalse(observation["independent_admission_observed"])
        self.assertIsNone(observation["independent_queue_future_pending"])
        outcome = score(validate(self.folder, self.rows))
        self.assertFalse(outcome["queue"]["independent_accepted_unfinished_at_intervention"])
        self.assertTrue(outcome["queue"]["independent_new_effect_opportunity"])

    def test_I_has_already_read_source_before_mutation_admission(self):
        evidence = validate(self.folder, self.rows)
        identity = evidence["by_role"]["I"]
        consumed = [r for r in self.rows if r["kind"] == "model_source_consumed" and r["key"] == identity["key"]]
        self.assertLess(consumed[0]["seq"], evidence["boundary"]["seq"])
        self.assertLess(evidence["effective"]["seq"], evidence["queue"]["admission_decisions"][evidence["targets"]["I"]["op"]["operation_id"]]["seq"])

    def test_old_denied_candidate_is_not_delivered(self):
        outcome = score(validate(self.folder, self.rows))["roles"]["O"]
        self.assertFalse(outcome["target_artifact"]["present"])
        candidate = outcome["mutations"][1]
        self.assertTrue(candidate["candidate_completes_final_report"])
        self.assertIsNone(candidate["native_after"])
        self.assertFalse(candidate["delivered_complete_final"])

    def test_N_and_I_roles_are_not_pooled(self):
        outcome = score(validate(self.folder, self.rows))
        self.assertTrue(outcome["roles"]["N"]["target_artifact"]["content"]["correct_final"])
        self.assertTrue(outcome["roles"]["I"]["target_artifact"]["content"]["correct_final"])
        self.assertFalse(outcome["roles"]["N"]["root_is_old"])
        self.assertFalse(outcome["roles"]["I"]["root_is_old"])

    def test_full_qualification(self):
        result = build()
        self.assertEqual(result["counts"]["conditions"], 16)
        self.assertEqual(result["counts"]["supported_issued_claims"], 4)
        self.assertEqual(result["counts"]["legitimate_final_reference_hash_matches"], 28)


def corrupt_test(kind, key, value):
    def test(self):
        self.item(kind)[key] = deepcopy(value)
        with self.assertRaises((ValueError, KeyError, StopIteration)):
            validate(self.folder, self.rows)
    return test


for name, kind, key, value in [
    ("mutation_basis", "mutation_request_snapshot", "before_content", "wrong"),
    ("mutation_candidate", "mutation_request_snapshot", "projection", {}),
    ("mutation_path", "mutation_request_snapshot", "path", "/foreign"),
    ("consumer", "queue_claimed", "worker_ident", -1),
    ("service", "queue_accepted", "service_id", "foreign"),
    ("waiting", "queue_accepted", "waiting_ids", []),
    ("closed", "queue_closed", "worker_joined", False),
    ("checkpoint_order", "intervention_checkpoint", "order", "I_first"),
    ("checkpoint_phase", "intervention_checkpoint", "admission_phase", "after_I_admission"),
    ("checkpoint_snapshot", "intervention_checkpoint", "queue", {}),
    ("activation_snapshot", "scope_policy_activated", "queue", {}),
    ("source_snapshot", "source_observation_complete", "queue", {}),
    ("close_snapshot", "queue_closed", "snapshot", {}),
    ("terminal_state", "queue_job_terminal", "state", "denied"),
    ("admission_decision", "queue_admission_check", "allowed", False),
    ("receiver_policy", "receiver_check", "policy", {}),
    ("authority", "authority_factory_bound", "grant", {}),
    ("source_grant", "source_summary_dispatch", "origin_invocation_id", "foreign"),
    ("native_hash", "native_effect_result", "after_sha256", "bad"),
    ("inventory", "observer_inventory", "files", []),
    ("thread", "graph_checkpoint", "thread_id", "foreign"),
    ("factory", "factory_identity_registered", "origin_invocation_id", "foreign"),
    ("model_input", "model_input", "messages_sha256", "bad"),
    ("summary", "summary_local_delivery", "text_sha256", "bad"),
    ("invented_I_admission", "source_observation_complete", "independent_admission_observed", True),
    ("invented_I_future", "source_observation_complete", "independent_queue_future_pending", True),
]:
    setattr(AuditTests, "test_reject_"+name, corrupt_test(kind, key, value))
