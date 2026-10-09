import threading
import unittest
from copy import deepcopy
import test_queue as fixtures
from termination import inventory_hash


class TerminationTests(unittest.TestCase):
    setUp = fixtures.QueueTests.setUp
    tearDown = fixtures.QueueTests.tearDown
    call = fixtures.QueueTests.call
    start = fixtures.QueueTests.start
    pair = fixtures.QueueTests.pair

    def test_inventory_root_members_and_hash(self):
        self.pair("before_I_admission")
        s = self.c.capture_scope("O")
        self.assertEqual([m["operation_id"] for m in s["members"]], ["targetO"])
        self.assertFalse(s["members"][0]["finished"])
        self.assertEqual(s["sha256"], inventory_hash({k: v for k, v in s.items() if k != "sha256"}))
        self.assertEqual(self.c.capture_scope("O")["version"], s["version"]+1)

    def test_unknown_root_rejected(self):
        with self.assertRaises(ValueError): self.c.capture_scope("unknown")

    def test_live_old_worker_withholds_confirmation_even_with_gates(self):
        self.pair("before_I_admission")
        self.c.activate("receiver_confirm", self.identities["O"])
        c = self.c.confirm_scope("O", "file_effects_closed")
        self.assertEqual(c["status"], "withheld")
        self.assertFalse(c["producer_quiescent"])
        self.assertTrue(c["producer_gates_active"])

    def test_closed_old_caller_without_gates_supports_snapshot_only(self):
        self.c.register(self.identities["O"])
        self.call("O", "partial")
        self.assertEqual(self.c.confirm_scope("O", "snapshot_quiescent")["status"], "issued")
        self.assertEqual(self.c.confirm_scope("O", "file_effects_closed")["status"], "withheld")
        self.assertEqual(self.call("C", "later"), "written")

    def test_drain_timeout_never_implies_completion(self):
        self.pair("before_I_admission")
        receipt = self.c.drain_scope("O", timeout=.02)
        self.assertEqual(receipt["status"], "timeout")
        self.assertEqual(self.c.confirm_scope("O", "snapshot_quiescent")["status"], "withheld")

    def test_drain_does_not_wait_independent_caller(self):
        self.pair("after_I_admission")
        self.c.activate("receiver_drain_confirm", self.identities["O"])
        self.c.release_queue("drain_test")
        self.assertTrue(self.c.independent_held.wait(2))
        receipt = self.c.drain_scope("O")
        self.assertEqual(receipt["status"], "completed")
        self.assertFalse(self.c.workers["arbitrary-first-mutation-nameI"].is_set())
        self.assertEqual(self.c.confirm_scope("O", "file_effects_closed")["status"], "issued")

    def test_drain_resnapshots_new_old_root_member(self):
        self.pair("before_I_admission")
        started, done, callback_entered, callback_release = (threading.Event() for _ in range(4))
        results = {}
        first_inventory = threading.Event()
        original_record = self.c.record
        def record(kind, **fields):
            original_record(kind, **fields)
            if kind == "scope_inventory": first_inventory.set()
        self.c.record = record
        def drain():
            results["drain"] = self.c.drain_scope("O", started=started)
            done.set()
        thread = threading.Thread(target=drain); self.threads.append(thread); thread.start()
        self.assertTrue(started.wait(1))
        self.assertTrue(first_inventory.wait(1))
        self.start("C", "new", results, lambda: (callback_entered.set(), callback_release.wait(2)))
        with self.c.changed:
            self.assertTrue(self.c.changed.wait_for(lambda: "newC" in self.c.jobs, 2))
        self.c.release_queue("new_member_test")
        self.assertTrue(callback_entered.wait(1))
        self.assertFalse(done.wait(.03))
        callback_release.set(); self.assertTrue(done.wait(2))
        final = next(r for r in self.rows if r["kind"] == "scope_inventory" and r["inventory_id"] == results["drain"]["final_inventory_id"])
        self.assertEqual({m["operation_id"] for m in final["members"]}, {"targetO", "newC"})
        first = next(r for r in self.rows if r["kind"] == "scope_inventory")
        self.assertEqual({m["operation_id"] for m in first["members"]}, {"targetO"})

    def test_intentional_omission_is_visible_in_producer_inventory(self):
        self.pair("before_I_admission")
        self.c.activate("false_omitted_worker_confirm", self.identities["O"])
        receipt = self.c.drain_scope("O", omit_ids=("targetO",))
        claim = self.c.confirm_scope("O", "file_effects_closed", omit_ids=("targetO",))
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(claim["status"], "issued")
        self.assertFalse(self.c.workers["targetO"].is_set())
        self.assertTrue(any(r["kind"] == "native_worker_entered" and r["op"]["operation_id"] == "targetO" for r in self.rows))

    def test_forced_early_claim_retains_failed_predicates(self):
        self.pair("before_I_admission")
        claim = self.c.confirm_scope("O", "file_effects_closed", force_issue=True)
        self.assertEqual(claim["status"], "issued")
        self.assertFalse(claim["producer_quiescent"])
        self.assertFalse(claim["producer_gates_active"])

    def test_cleanup_is_not_experimental_drain(self):
        self.c.register(self.identities["O"])
        self.call("O", "partial"); self.c.drain()
        self.assertFalse(any(r["kind"] in {"scoped_drain_receipt", "scope_confirmation"} for r in self.rows))

    def test_finished_inventory_is_a_copy(self):
        self.c.register(self.identities["O"])
        self.call("O", "partial"); s = self.c.capture_scope("O")
        s["members"][0]["finished"] = False
        self.assertTrue(self.c.capture_scope("O")["members"][0]["finished"])

    def test_unknown_claim_scope_rejected(self):
        self.c.register(self.identities["O"])
        with self.assertRaises(ValueError): self.c.confirm_scope("O", "everything_forever")


if __name__ == "__main__": unittest.main()
