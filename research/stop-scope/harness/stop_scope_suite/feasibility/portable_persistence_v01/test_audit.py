"""Counterexamples modify in-memory copies, never the preserved smoke evidence."""
from copy import deepcopy
from pathlib import Path
import unittest
import os
import audit as a

HERE=Path(__file__).resolve().parent


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.out=Path(os.environ["STOP_SCOPE_TEST_EVIDENCE"]).resolve()
        self.plan=a.load(self.out/"PLAN.json")
        self.process=a.load(self.out/"CHILD_PROCESSES.json")
        self.result=a.load(self.out/"result.json")
        self.logs={n:a.journal(self.out/(n+".jsonl")) for n in ("source","supervisor","receiver-1","receiver-2","observer")}
        self.before=a.database(self.out/"queue-before-restart.sqlite3")
        self.final=a.database(self.out/"queue.sqlite3")
        self.actual=a.files(self.out/"files")

    def check(self):
        return a.inspect(self.plan,self.process,self.result,self.logs,self.before,self.final,self.actual)

    def test_real_smoke_reconciles(self):
        self.assertTrue(self.check()["restart_observed"])

    def test_arm_name_does_not_score(self):
        before=self.check()
        self.plan["arm"]="durable_revoke"
        self.assertEqual(before,self.check())

    def test_wrong_answer_remains_valid(self):
        self.plan["expected_final"]["O"]["metrics"]["event_count"]=999
        result=self.check()
        self.assertFalse(result["roles"]["O"]["final_correct_at_close"])
        self.assertEqual(result["roles"]["O"]["second_lifetime_mutations"],1)

    def test_missing_receipt_retains_raw_disk(self):
        es=self.logs["receiver-2"]
        target=a.selected(es,"native_effect_result")[0]
        es.remove(target)
        for i,e in enumerate(es,1): e["seq"]=i
        result=a.audit(self.out,replacement=self.logs)
        self.assertEqual(result["evidence_status"],"needs_review")
        self.assertIsNone(result["outcomes"])
        self.assertTrue(result["raw_disk_files"])

    def test_recovery_inventory_gap(self):
        es=self.logs["receiver-2"]
        # Keep all receipt sequence numbers intact so this isolates the recovery
        # inventory rather than being caught by the earlier receipt binding.
        a.selected(es,"job_recovered")[0]["kind"]="unrecognized_recovery_event"
        with self.assertRaisesRegex(AssertionError,"Recovery inventory"): self.check()

    def test_recovered_payload_changed(self):
        a.selected(self.logs["receiver-2"],"job_recovered")[0]["op"]["content_sha256"]="bad"
        with self.assertRaisesRegex(AssertionError,"Recovered job"): self.check()

    def test_durable_job_body_changed(self):
        self.final["jobs"][0]["body"]="{}"
        with self.assertRaisesRegex(AssertionError,"Durable operation body"): self.check()

    def test_same_receiver_pid_rejected(self):
        pid=self.logs["receiver-1"][0]["pid"]
        for e in self.logs["receiver-2"]: e["pid"]=pid
        with self.assertRaisesRegex(AssertionError,"Processes not distinct"): self.check()

    def test_new_database_rejected(self):
        row=next(x for x in self.final["meta"] if x["key"]=="database_id")
        row["value"]="different"
        with self.assertRaisesRegex(AssertionError,"Database identity"): self.check()

    def test_disk_change_rejected(self):
        next(iter(self.actual.values()))["content"]="unlogged edit"
        with self.assertRaisesRegex(AssertionError,"Disk differs"): self.check()

    def test_source_rpc_payload_change(self):
        a.selected(self.logs["source"],"rpc_sent")[0]["request"]["action"]="invented"
        with self.assertRaisesRegex(AssertionError,"Source supervisor chain"): self.check()

    def test_factory_identity_mismatch(self):
        a.selected(self.logs["source"],"authority_factory_bound")[0]["identity"]["origin_invocation_id"]="invented"
        with self.assertRaises(AssertionError): self.check()

    def test_executor_boundary_missing(self):
        a.selected(self.logs["source"],"backend_sync_entered")[0]["executor_worker_stack_observed"]=False
        with self.assertRaisesRegex(AssertionError,"executor boundary"): self.check()

    def test_candidate_content_changed(self):
        a.selected(self.logs["source"],"mutation_request_snapshot")[0]["projection"]["candidate_content"]="invented"
        with self.assertRaisesRegex(AssertionError,"Proposed edit/write"): self.check()

    def test_wrong_tool_surface(self):
        a.selected(self.logs["source"],"source_role_surface")[0]["names"].append("execute")
        with self.assertRaisesRegex(AssertionError,"Tool surface drift"): self.check()

    def test_provider_flag_rejected(self):
        a.selected(self.logs["source"],"bridge_wire_exchange")[0]["actual_provider_calls"]=1
        with self.assertRaisesRegex(AssertionError,"Wire mode"): self.check()

    def test_forced_cleanup_rejected(self):
        self.process["cleanup_actions"]=[dict(action="terminate")]
        with self.assertRaisesRegex(AssertionError,"Unclean"): self.check()

    def test_stop_smoke_reconciles(self):
        result=a.audit(Path(os.environ["STOP_SCOPE_TEST_STOP_EVIDENCE"]).resolve())
        self.assertEqual(result["evidence_status"],"recorded",result["errors"])
        self.assertTrue(result["outcomes"]["source_stopped_with_receiver_pending"])
        self.assertEqual(result["outcomes"]["roles"]["O"]["second_lifetime_mutations"],0)


class ProjectionTests(unittest.TestCase):
    def op(self,old,new,all=False):
        return dict(tool="edit_file",args=dict(old_string=old,new_string=new,replace_all=all))

    def test_small_edit(self):
        self.assertEqual(a.candidate(self.op('12','24'),'{"event_count":12}'),'{"event_count":24}')

    def test_missing_file(self):
        self.assertIsNone(a.candidate(self.op('12','24'),None))

    def test_ambiguous_edit(self):
        self.assertIsNone(a.candidate(self.op('12','24'),'12 12'))

    def test_all_matches(self):
        self.assertEqual(a.candidate(self.op('12','24',True),'12 12'),'24 24')

    def test_newline_normalization(self):
        self.assertEqual(a.candidate(self.op('a\r\nb','z\r\nx'),'a\nb'),'z\nx')

    def test_no_implicit_eof_repair(self):
        self.assertIsNone(a.candidate(self.op('a\n','b\n'),'a'))


if __name__=="__main__": unittest.main()
