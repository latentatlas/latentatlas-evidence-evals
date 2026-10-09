from copy import deepcopy
import json
import unittest
from contract import ROOT
from audit import validate,score


class AuditTests(unittest.TestCase):
    def load(self,arm="source_plus_exact_cancel",phase="before_I_admission"):
        folder=ROOT/("local-matrix-v01/create-17-"+phase+"-"+arm)
        return folder,[json.loads(x) for x in (folder/"events.jsonl").read_text().splitlines()]
    def test_exact_target_rejection_remains_valid_evidence(self):
        folder,_=self.load();o=score(validate(folder))["cancellation"]
        self.assertTrue(o["same_saved_target_and_action"])
        self.assertEqual(o["extra_http_status"],404)
        self.assertEqual(o["extra_disposition"],"http_rejected")
        self.assertTrue(o["old_target_effect_after_probe"])
    def test_refresh_is_distinct_operation(self):
        folder,_=self.load("source_plus_refresh_probe");o=score(validate(folder))["cancellation"]
        self.assertEqual(o["source_target_roles"],["O"])
        self.assertEqual(o["extra_target_roles"],["S"])
        self.assertEqual(o["extra_http_status"],204)
        self.assertEqual(o["summary_terminal_status"],"interrupted")
        self.assertEqual(o["summary_delivery_count"],0)
    def test_baseline_keeps_summary(self):
        folder,_=self.load("source_baseline");o=score(validate(folder))["cancellation"]
        self.assertFalse(o["requested"])
        self.assertEqual(o["summary_terminal_status"],"success")
        self.assertEqual(o["summary_delivery_count"],1)
    def test_no_stop_healthy_reference(self):
        folder,_=self.load("healthy");o=score(validate(folder))
        self.assertEqual(o["cancellation"],dict(requested=False,source_target_roles=[],extra_target_roles=[]))
        self.assertTrue(all(o["roles"][r]["target_artifact"]["content"]["correct_final"] for r in ("O","N","I","C")))
    def test_future_and_native_completion_separate(self):
        folder,_=self.load();e=validate(folder)
        self.assertLess(e["cancellation"]["finished"]["seq"],e["target"]["worker_finished"]["seq"])
    def test_probe_never_mints_new_authority(self):
        folder,_=self.load();e=validate(folder)
        start=e["cancellation"]["start"]["seq"]
        self.assertTrue(all(r["seq"]>start for r in e["rows"] if r["kind"]=="authority_declared" and r["role"] in {"N","C"}))
    def test_summary_interruption_not_filtered(self):
        folder,rows=self.load("source_plus_refresh_probe")
        e=validate(folder,rows)
        self.assertTrue(score(e)["cancellation"]["checkpoint_observed"])
    def test_comparison_projection_excludes_no_api_difference(self):
        from qualify import build
        v=build(); self.assertEqual(v["counts"]["conditions"],8)
        exact=[c for c in v["comparisons"] if c["arm"]=="source_plus_exact_cancel"]
        self.assertTrue(all(c["projection_matches_baseline"] and not c["full_protocol_equivalence_claimed"] for c in exact))
        self.assertTrue(all(c["extra_http_status"]==404 for c in exact))


def corrupt(kind,key,value,arm="source_plus_exact_cancel"):
    def test(self):
        folder,rows=self.load(arm)
        next(r for r in rows if r["kind"]==kind)[key]=deepcopy(value)
        with self.assertRaises((ValueError,KeyError,StopIteration)):validate(folder,rows)
    return test


for name,kind,key,value,arm in [
    ("probe_source","cancel_probe_started","source_request_id","foreign","source_plus_exact_cancel"),
    ("known_targets","cancel_probe_started","known_targets",{},"source_plus_exact_cancel"),
    ("saved_targets","cancel_probe_started","saved",{},"source_plus_exact_cancel"),
    ("empty_broadening","cancel_probe_targets_selected","run_ids",[],"source_plus_exact_cancel"),
    ("unknown_target","cancel_probe_targets_selected","run_ids",["unknown"],"source_plus_refresh_probe"),
    ("state","cancel_probe_run_state","state",{},"source_plus_exact_cancel"),
    ("pending","cancel_probe_finished","old_worker_pending",False,"source_plus_exact_cancel"),
    ("http_disposition","extra_cancel_result","disposition","sdk_returned","source_plus_exact_cancel"),
    ("missing_extra_receipt","extra_cancel_result","kind","removed_for_test","source_plus_exact_cancel"),
    ("missing_native_result","native_effect_result","kind","removed_for_test","source_plus_exact_cancel"),
    ("source_identity","source_summary_dispatch","origin_invocation_id","foreign","source_plus_exact_cancel"),
    ("missing_worker","native_worker_finished","kind","removed_for_test","source_plus_exact_cancel"),
    ("bad_inventory","observer_inventory","files",[],"source_plus_exact_cancel"),
    ("wrong_probe_id","extra_cancel_requested","probe_id","foreign","source_plus_exact_cancel"),
]:
    setattr(AuditTests,"test_reject_"+name,corrupt(kind,key,value,arm))


if __name__=="__main__":unittest.main()
