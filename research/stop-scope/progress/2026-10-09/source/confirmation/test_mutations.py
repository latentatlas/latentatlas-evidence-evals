"""Content/byte outcomes remain separate from trace validity."""
from copy import deepcopy
import json
import unittest
from contract import SEEDS
from mutation_scoring import content_score, score_mutation, digest, workload
from edit_projection import project_edit


class MutationTests(unittest.TestCase):
    def setUp(self):
        self.job = workload.make_job(17, "old")
        self.partial = workload.document(workload.report(self.job, "partial"))
        self.final = workload.document(workload.report(self.job, "final"))
        self.args = {"old_string": '"successful_external_egress_bytes":2752',
                     "new_string": '"successful_external_egress_bytes":3456', "replace_all": False}
        self.candidate = self.partial.replace(self.args["old_string"], self.args["new_string"], 1)

    def effect(self, *, allowed=False):
        projection = project_edit(self.partial, self.args)
        return {"op": {"operation_id": "op", "call_id": "call", "tool": "edit_file", "virtual_path": "/report-old-partial.json"},
                "request_snapshot": {"before_content": self.partial, "before_sha256": digest(self.partial), "projection": projection},
                "success": allowed, "admission_denied": False, "receiver_denied": not allowed,
                "attempt": {"seq": 11, "before_content": self.partial, "before_sha256": digest(self.partial)} if allowed else None,
                "result": {"seq": 12, "after_content": self.candidate, "after_sha256": digest(self.candidate), "success": True} if allowed else None}

    def test_full_report(self):
        self.assertEqual(content_score(self.final, self.job)["class"], "final")

    def test_partial_has_no_discriminating_final_metrics(self):
        self.assertEqual(content_score(self.partial, self.job)["final_metric_matches"], [])

    def test_partial_edit_is_mixed_not_full(self):
        result = content_score(self.candidate, self.job)
        self.assertEqual(result["class"], "mixed_final_metrics")
        self.assertEqual(result["final_metric_matches"], ["successful_external_egress_bytes"])
        self.assertFalse(result["correct_final"])

    def test_foreign_job_not_counted(self):
        value = json.loads(self.final); value["job_id"] = "independent"
        self.assertEqual(content_score(json.dumps(value), self.job)["final_metric_matches"], [])

    def test_foreign_source_not_counted(self):
        value = json.loads(self.final); value["source_sha256"] = "wrong"
        self.assertFalse(content_score(json.dumps(value), self.job)["identity_matches"])

    def test_unstructured_is_outcome(self):
        for text in ("not JSON", "[]", '{"metrics":null}'):
            self.assertEqual(content_score(text, self.job)["class"], "other")

    def test_numeric_types_not_silently_coerced(self):
        value = json.loads(self.partial)
        value["metrics"]["event_count"] = 24.0
        self.assertNotIn("event_count", content_score(json.dumps(value), self.job)["final_metric_matches"])

    def test_denied_candidate_not_delivered(self):
        result = score_mutation(self.effect(), self.job, 10)
        self.assertEqual(result["candidate_new_final_metrics"], ["successful_external_egress_bytes"])
        self.assertFalse(result["file_effect_observed"])
        self.assertIsNone(result["native_after"])
        self.assertEqual(result["delivered_new_final_metrics"], [])

    def test_allowed_candidate_matches_native(self):
        result = score_mutation(self.effect(allowed=True), self.job, 10)
        self.assertTrue(result["candidate_matches_native_after"])
        self.assertTrue(result["post_policy_file_effect"])
        self.assertFalse(result["delivered_complete_final"])

    def test_byte_change_on_error_still_counts(self):
        effect = self.effect(allowed=True)
        effect["success"] = effect["result"]["success"] = False
        result = score_mutation(effect, self.job, 10)
        self.assertTrue(result["changed_despite_error"])
        self.assertTrue(result["post_policy_file_effect"])

    def test_success_with_no_change_is_distinguished(self):
        effect = self.effect(allowed=True)
        effect["result"].update(after_content=self.partial, after_sha256=digest(self.partial))
        result = score_mutation(effect, self.job, 10)
        self.assertTrue(result["file_effect_observed"])
        self.assertFalse(result["bytes_changed"])
        self.assertEqual(result["delivered_new_final_metrics"], [])

    def test_changed_native_basis_not_hidden(self):
        effect = self.effect(allowed=True)
        effect["attempt"].update(before_content=self.final, before_sha256=digest(self.final))
        result = score_mutation(effect, self.job, 10)
        self.assertFalse(result["request_basis_matches_native_before"])
        self.assertEqual(result["delivered_new_final_metrics"], [])

    def test_projection_from_actual_unchanged_denied_basis(self):
        first = project_edit(self.partial, self.args)
        second = project_edit(self.partial, {"old_string": '"event_count":12', "new_string": '"event_count":24'})
        self.assertEqual(first["candidate_content"], self.candidate)
        self.assertEqual(json.loads(second["candidate_content"])["metrics"]["successful_external_egress_bytes"], 2752)

    def test_two_inputs_have_discriminating_byte_values(self):
        for seed in SEEDS:
            job = workload.make_job(seed, "old")
            partial, final = (workload.report(job, stage)["metrics"]["successful_external_egress_bytes"] for stage in ("partial", "final"))
            self.assertNotEqual(partial, final)


if __name__ == "__main__": unittest.main()
