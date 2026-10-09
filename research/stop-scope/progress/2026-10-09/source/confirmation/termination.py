"""Scoped caller inventory and claims; global cleanup remains a separate operation."""
from copy import deepcopy
import hashlib
import json
import time
import uuid
from contract import require


def inventory_hash(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class TerminationMixin:
    def capture_scope(self, root, *, omit_ids=()):
        # Same lock order as native effect -> metadata. No wait while either is held.
        with self.policy_lock, self.meta:
            require(root in self.identities and self.identities[root]["origin_key"] == root,
                    "Unknown scope root")
            self.inventory_version += 1
            members = []
            for oid, op in self.worker_ops.items():
                if op["origin_key"] != root or oid in omit_ids:
                    continue
                job = self.jobs.get(oid)
                members.append(dict(operation_id=oid, identity_key=op["key"],
                                    finished=self.workers[oid].is_set(),
                                    admitted=job is not None,
                                    queue_state=job.state if job else None))
            body = dict(inventory_id=str(uuid.uuid4()), version=self.inventory_version,
                        root=root, service_id=self.service_id, members=sorted(members, key=lambda x: x["operation_id"]),
                        policy=deepcopy(self.policy))
            row = dict(**body, sha256=inventory_hash(body))
            self.record("scope_inventory", **row)
            return row

    def drain_scope(self, root, *, timeout=10, omit_ids=(), started=None):
        did = str(uuid.uuid4())
        self.record("scoped_drain_requested", drain_id=did, root=root, service_id=self.service_id,
                    timeout_seconds=timeout)
        if started is not None: started.set()
        deadline = time.monotonic() + timeout
        captures = []
        while True:
            with self.policy_lock, self.meta:
                snapshot = self.capture_scope(root, omit_ids=omit_ids)
                captures.append(snapshot["inventory_id"])
                pending = [m["operation_id"] for m in snapshot["members"] if not m["finished"]]
                remaining = deadline - time.monotonic()
                if not pending or remaining <= 0:
                    # Final membership check and receipt share the registration lock.
                    receipt = dict(drain_id=did, root=root, service_id=self.service_id,
                                   status="completed" if not pending else "timeout",
                                   inventory_ids=captures, final_inventory_id=snapshot["inventory_id"],
                                   final_inventory_sha256=snapshot["sha256"])
                    self.record("scoped_drain_receipt", **receipt)
                    return receipt
            # Bounded event waits followed by a NEW inventory, not a stale initial list.
            self.workers[pending[0]].wait(min(remaining, .02))

    def confirm_scope(self, root, claim_scope, *, omit_ids=(), force_issue=False):
        require(claim_scope in {"snapshot_quiescent", "file_effects_closed"}, "Unknown claim scope")
        with self.policy_lock, self.meta:
            snapshot = self.capture_scope(root, omit_ids=omit_ids)
            quiet = all(m["finished"] for m in snapshot["members"])
            p = self.policy
            gated = p["kind"] == "origin" and p["root"] == root and p["admission"] and p["effect"]
            ready = quiet and (claim_scope == "snapshot_quiescent" or gated)
            result = dict(claim_id=str(uuid.uuid4()), root=root, service_id=self.service_id,
                          claim_scope=claim_scope, status="issued" if ready or force_issue else "withheld",
                          inventory_id=snapshot["inventory_id"], inventory_sha256=snapshot["sha256"],
                          producer_quiescent=quiet, producer_gates_active=bool(gated),
                          horizon="inventory_capture" if claim_scope == "snapshot_quiescent" else "measurement_closed_while_policy_unchanged",
                          force_issue=force_issue)
            self.record("scope_confirmation", **result)
            return result
