import threading
import unittest
from copy import deepcopy
from unittest.mock import patch
from authority import AuthorityLedger
from scope_controller import ScopeController
from controller import Denied
from contract import ARMS, ARM_CONFIG, ADMISSION_PHASES
import scope_controller


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.rows = []
        self.record = lambda kind, **kw: self.rows.append({"kind": kind, **deepcopy(kw)})
        self.ledger = AuthorityLedger(self.record)
        self.identities = {}
        for role in ("O", "I", "N", "C", "S"):
            parent = "inv-O" if role in {"C", "S"} else None
            thread = "other" if role == "I" else "same"
            self.ledger.declare(role, thread, "inv-"+role, parent=parent)
            self.identities[role] = {"key": role, "invocation_id": "inv-"+role, "thread_id": thread,
                                    "origin_key": "O" if parent else role, "origin_invocation_id": parent or "inv-"+role}
        self.c = ScopeController(self.record, self.identities, self.ledger)
        self.threads = []

    def tearDown(self):
        self.c.release_all("test_cleanup")
        for thread in self.threads:
            thread.join(3); self.assertFalse(thread.is_alive())
        self.c.drain(3); self.c.finish()
        self.assertFalse(self.c.thread.is_alive())

    def call(self, role, name="write", callback=lambda: "written"):
        identity = self.identities[role]
        return self.c.execute(identity, {**identity, "operation_id": name+role, "call_id": name+"-"+role}, callback)

    def start(self, role, name, results, callback=lambda: "written"):
        def run():
            try: results[role] = self.call(role, name, callback)
            except BaseException as exc: results[role] = type(exc).__name__
        thread = threading.Thread(target=run); self.threads.append(thread); thread.start()

    def pair(self, phase):
        result = {}
        self.start("O", "target", result)
        self.start("I", "arbitrary-first-mutation-name", result)
        self.assertTrue(all(e.wait(2) for e in self.c.role_holds.values()))
        self.c.release_role("O", "old_first")
        self.assertTrue(self.c.queue_held.wait(2))
        self.assertEqual(self.c.snapshot()["active"]["key"], "O")
        if phase == "after_I_admission":
            self.c.release_role("I", "before_policy")
            with self.c.changed:
                self.assertTrue(self.c.changed.wait_for(lambda: len(self.c.pending) == 1, 2))
        self.assertEqual(len(self.c.pending), int(phase == "after_I_admission"))
        return result

    def arm_check(self, arm, phase):
        result = self.pair(phase)
        self.c.activate(arm, self.identities["O"])
        if phase == "before_I_admission": self.c.release_role("I", "after_policy")
        self.c.release_queue("test_boundary")
        self.c.release_independent("test_boundary")
        for thread in self.threads: thread.join(2)
        gated = ARM_CONFIG[arm]["gates"]
        self.assertEqual(result, {"O": "Denied" if gated else "written", "I": "written"})
        iid = "arbitrary-first-mutation-nameI"
        self.assertIn(iid, self.c.jobs)
        for role, allowed in (("N", True), ("C", not gated)):
            if allowed: self.assertEqual(self.call(role), "written")
            else:
                with self.assertRaises(Denied): self.call(role)
        return result

    def test_unadmitted_I_has_worker_but_no_queue_future(self):
        self.pair("before_I_admission")
        iid = "arbitrary-first-mutation-nameI"
        self.assertIn(iid, self.c.workers)
        self.assertNotIn(iid, self.c.jobs)
        self.assertFalse(any(r["kind"] == "queue_admission_check" and r["op"]["key"] == "I" for r in self.rows))

    def test_first_I_selection_is_not_a_filename_or_target_id(self):
        self.arm_check("healthy", "before_I_admission")
        self.assertEqual(self.call("I", "another"), "written")
        holds = [r for r in self.rows if r["kind"] == "queue_candidate_ready" and r["role"] == "I"]
        self.assertEqual(len(holds), 1)
        self.assertEqual(holds[0]["selection"], "first_mutation")

    def test_changed_identity_rejected(self):
        identity = self.identities["N"]
        with self.assertRaises(ValueError): self.c.execute(identity, {**identity, "origin_key": "O"}, lambda: None)

    def test_new_invocation_cannot_mint_old_root(self):
        identity = {**self.identities["C"], "origin_key": "C", "origin_invocation_id": "inv-C"}
        with self.assertRaises(ValueError): self.c.register(identity)

    def test_duplicate_operation_rejected(self):
        self.call("N")
        with self.assertRaises(ValueError): self.call("N")

    def test_repeated_candidate_rejected_without_orphan_worker(self):
        self.arm_check("healthy", "before_I_admission")
        identity = self.identities["O"]
        op = {**identity, "operation_id": "distinct-operation-same-call", "call_id": "target-O"}
        with self.assertRaisesRegex(ValueError, "Repeated role candidate"):
            self.c.execute(identity, op, lambda: "unexpected")
        self.assertNotIn(op["operation_id"], self.c.workers)
        self.assertNotIn(op["operation_id"], self.c.jobs)
        self.assertTrue(all(v.is_set() for v in self.c.workers.values()))

    def test_duplicate_activation_rejected(self):
        self.c.activate("receiver_confirm", self.identities["O"])
        with self.assertRaises(ValueError): self.c.activate("healthy", self.identities["O"])

    def test_callback_on_sole_consumer(self):
        self.assertEqual(self.call("N", callback=threading.get_ident), self.c.thread.ident)

    def test_callback_error_is_settled_not_silenced(self):
        def fail(): raise RuntimeError("intentional")
        with self.assertRaises(RuntimeError): self.call("N", callback=fail)
        self.assertEqual(self.c.jobs["writeN"].state, "error")
        self.assertEqual(self.call("N", "later"), "written")

    def test_effect_lock_serializes_revocation(self):
        entered, release, activated = threading.Event(), threading.Event(), threading.Event()
        results = {}
        self.start("O", "earlier", results, lambda: (entered.set(), release.wait(2)))
        self.assertTrue(entered.wait(1))
        def revoke(): self.c.activate("receiver_confirm", self.identities["O"]); activated.set()
        thread = threading.Thread(target=revoke); self.threads.append(thread); thread.start()
        self.assertFalse(activated.wait(.03))
        release.set(); self.assertTrue(activated.wait(1))
        with self.assertRaises(Denied): self.call("O", "later")

    def test_unadmitted_timeout_creates_no_future_or_effect(self):
        with patch.object(scope_controller, "HOLD_SECONDS", .03):
            with self.assertRaises(TimeoutError): self.call("I", "unreleased")
        self.assertNotIn("unreleasedI", self.c.jobs)
        self.assertEqual(self.c.deadline_failures, ["unreleasedI"])

    def test_caller_timeout_cancels_accepted_unwritten_work(self):
        with patch.object(scope_controller, "CALLER_SECONDS", .2):
            result = {}
            self.start("O", "target", result)
            self.assertTrue(self.c.role_holds["O"].wait(1))
            self.c.release_role("O", "deadline_test")
            self.assertTrue(self.c.queue_held.wait(1))
            for thread in self.threads: thread.join(2)
        self.assertEqual(result, {"O": "TimeoutError"})
        self.assertFalse(any(r["kind"] == "receiver_check" for r in self.rows))
        self.assertTrue(all(j.state == "cancelled" for j in self.c.jobs.values()))


def arm_test(arm, phase):
    def test(self): self.arm_check(arm, phase)
    return test


for arm in ARMS:
    for phase in ADMISSION_PHASES:
        setattr(QueueTests, "test_"+arm+"_"+phase, arm_test(arm, phase))


if __name__ == "__main__": unittest.main()
