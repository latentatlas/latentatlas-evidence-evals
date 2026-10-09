from copy import deepcopy
import json
import unittest
from contract import ROOT
from audit import validate, score


class ConfirmationAuditTests(unittest.TestCase):
    def load(self, arm="receiver_drain_confirm", phase="after_I_admission"):
        folder = ROOT/("local-matrix-v01/create-17-"+phase+"-"+arm)
        rows = [json.loads(x) for x in (folder/"events.jsonl").read_text().splitlines()]
        return folder, rows

    def outcome(self, arm, phase="after_I_admission"):
        return score(validate(self.load(arm, phase)[0]))["confirmation"]

    def test_supported_drain_while_I_live(self):
        o = self.outcome("receiver_drain_confirm")
        self.assertTrue(o["drains"][0]["completion_supported"])
        self.assertTrue(o["claims"][0]["issued_claim_supported"])
        self.assertTrue(o["claims"][0]["independent_live_callers_at_claim"])

    def test_source_confirmation_withheld(self):
        o = self.outcome("source_confirm")["claims"][0]
        self.assertEqual(o["status"], "withheld")
        self.assertFalse(o["file_gates_active"])

    def test_receiver_confirmation_withheld_until_worker_finishes(self):
        o = self.outcome("receiver_confirm")["claims"][0]
        self.assertEqual(o["status"], "withheld")
        self.assertTrue(o["file_gates_active"])
        self.assertFalse(o["scoped_quiescence_observed"])

    def test_early_claim_is_valid_evidence_of_unsupported_claim(self):
        o = self.outcome("false_early_confirm")["claims"][0]
        self.assertFalse(o["issued_claim_supported"])
        self.assertEqual(len(o["old_root_effects_after_claim"]), 3)

    def test_omitted_worker_detected_even_without_late_effect(self):
        o = self.outcome("false_omitted_worker_confirm")
        self.assertFalse(o["drains"][0]["completion_supported"])
        self.assertFalse(o["claims"][0]["issued_claim_supported"])
        self.assertEqual(o["claims"][0]["old_root_effects_after_claim"], [])
        self.assertEqual(len(o["claims"][0]["inventory"]["missing_operation_ids"]), 1)

    def test_future_C_does_not_retroactively_falsify_snapshot(self):
        c = self.outcome("source_drain_snapshot")["claims"][0]
        self.assertTrue(c["issued_claim_supported"])
        self.assertEqual(c["snapshot_member_effects_after_claim"], [])
        self.assertEqual(len(c["later_member_effects_after_claim"]), 2)

    def test_final_cleanup_does_not_repair_early_claim(self):
        folder, rows = self.load("false_early_confirm")
        self.assertTrue(any(r["kind"] == "receiver_workers_quiescent" for r in rows))
        self.assertFalse(score(validate(folder, rows))["confirmation"]["claims"][0]["issued_claim_supported"])

    def test_correct_file_gate_has_zero_effects_and_fresh_N(self):
        folder, _ = self.load()
        o = score(validate(folder))
        self.assertEqual(o["old_origin_post_policy_effects"], 0)
        self.assertTrue(o["roles"]["N"]["target_artifact"]["content"]["correct_final"])

    def test_source_ack_precedes_pending_native_completion(self):
        folder, rows = self.load()
        e = validate(folder, rows)
        r = next(r for r in rows if r["kind"] == "source_stop_handler_returned")
        self.assertLess(r["seq"], e["target"]["worker_finished"]["seq"])

    def reject_mutation(self, mutate):
        folder, rows = self.load()
        mutate(rows)
        with self.assertRaises((ValueError, KeyError, StopIteration)): validate(folder, rows)

    def test_missing_bound_inventory(self):
        self.reject_mutation(lambda rs: next(r for r in rs if r["kind"] == "scope_inventory").update(kind="missing_for_test"))

    def test_inventory_hash_corruption(self):
        self.reject_mutation(lambda rs: next(r for r in rs if r["kind"] == "scope_inventory").update(sha256="bad"))

    def test_confirmation_reference_corruption(self):
        self.reject_mutation(lambda rs: next(r for r in rs if r["kind"] == "scope_confirmation").update(inventory_id="foreign"))

    def test_missing_drain_receipt(self):
        self.reject_mutation(lambda rs: next(r for r in rs if r["kind"] == "scoped_drain_receipt").update(kind="missing_for_test"))

    def test_missing_worker_receipt(self):
        self.reject_mutation(lambda rs: next(r for r in rs if r["kind"] == "native_worker_finished").update(kind="missing_for_test"))

    def test_wrong_scope_identity(self):
        self.reject_mutation(lambda rs: next(r for r in rs if r["kind"] == "scope_confirmation").update(root="foreign"))

    def test_wrong_quiescence_assertion_is_scored_not_invalidated(self):
        folder, rows = self.load("receiver_confirm")
        c = next(r for r in rows if r["kind"] == "scope_confirmation")
        c.update(status="issued", producer_quiescent=True)
        o = score(validate(folder, rows))["confirmation"]["claims"][0]
        self.assertFalse(o["producer_predicates_match"])
        self.assertFalse(o["issued_claim_supported"])

    def test_healthy_and_source_only_have_no_experimental_claims(self):
        for arm in ("healthy", "source_only"):
            o = self.outcome(arm)
            self.assertEqual(o["claims"], [])
            self.assertEqual(o["drains"], [])

    def test_I_effect_fixture_cannot_be_released_before_assessment(self):
        self.reject_mutation(lambda rs: next(r for r in rs if r["kind"] == "experimental_assessment_closed").update(independent_fixture_released=True))


if __name__ == "__main__": unittest.main()
