"""Receiver-side exclusion, with scheduling barriers outside the effect lock."""
from copy import deepcopy
import threading
import time

from contract import CONTROLS, SCHEDULES, HOLD_SECONDS, require


class Denied(Exception):
    pass


class NativeController:
    def __init__(self, record, schedule, timeout=HOLD_SECONDS):
        require(schedule in SCHEDULES, "Unknown boundary")
        self.record, self.schedule, self.timeout = record, schedule, timeout
        self.meta = threading.RLock()
        self.locks, self.identities, self.workers = {}, {}, {}
        self.revoked = set()
        self.held, self.released = threading.Event(), threading.Event()
        self.target = None
        self.intervened = False
        self.deadline_failures = []

    def register(self, identity):
        key = identity["origin_key"]
        with self.meta:
            previous = self.identities.get(key)
            require(previous is None or previous == identity, "Origin identity changed")
            if previous is None:
                self.identities[key] = deepcopy(identity)
                self.locks[key] = threading.RLock()
                self.record("origin_registered", identity=identity)
            return self.locks[key]

    def _barrier(self, op):
        # The barrier must not serialize intervention behind a paused worker.
        with self.meta:
            require(self.target is None, "Scheduling target reused")
            self.target = deepcopy(op)
            self.record("native_boundary_held", op=op, schedule=self.schedule)
            self.held.set()
        if not self.released.wait(self.timeout):
            with self.meta:
                self.deadline_failures.append(op["operation_id"])
                self.record("native_boundary_timeout", op=op)
            raise TimeoutError("Native scheduling barrier expired")

    def execute(self, identity, op, callback, target=False):
        lock = self.register(identity)
        require(all(op.get(k) == v for k, v in identity.items()), "Unbound operation origin")
        oid = op["operation_id"]
        done = threading.Event()
        with self.meta:
            require(oid not in self.workers, "Operation replay")
            self.workers[oid] = done
            self.record("native_worker_entered", op=op, worker_ident=threading.get_ident())
        try:
            if target and self.schedule == "before_effect":
                self._barrier(op)
            with lock:
                allowed = identity["origin_key"] not in self.revoked
                self.record("receiver_check", op=op, allowed=allowed)
                if not allowed:
                    self.record("receiver_denied", op=op)
                    raise Denied("origin_revoked")
                result = callback()
            if target and self.schedule == "after_effect":
                self._barrier(op)
            return result
        except BaseException as exc:
            self.record("native_worker_error", op=op, error_type=type(exc).__name__, error=str(exc))
            raise
        finally:
            self.record("native_worker_finished", op=op)
            done.set()

    def intervene(self, control, origin_key):
        require(control in CONTROLS, "Unknown control")
        with self.meta:
            require(origin_key in self.locks, "Unknown target origin")
            require(not self.intervened, "Duplicate control")
            self.intervened = True
        if control == "healthy":
            self.record("reference_boundary", origin_key=origin_key)
            return
        self.record("receiver_control_requested", control=control, origin_key=origin_key)
        with self.locks[origin_key]:
            if control == "receiver_revoke":
                self.revoked.add(origin_key)
                self.record("receiver_revocation_effective", control=control, origin_key=origin_key)
            else:
                self.record("receiver_fault_noop", control=control, origin_key=origin_key,
                            effective_revocation=False)

    def release(self, reason):
        with self.meta:
            if not self.released.is_set():
                self.record("native_boundary_released", reason=reason)
                self.released.set()

    def drain(self, timeout=10):
        deadline = time.monotonic() + timeout
        with self.meta:
            snapshot = list(self.workers.items())
        for _, done in snapshot:
            require(done.wait(max(0, deadline-time.monotonic())), "Worker closure deadline")
        with self.meta:
            require(len(snapshot) == len(self.workers), "New worker during quiescence check")
            self.record("receiver_workers_quiescent", operation_ids=[oid for oid, _ in snapshot],
                        all_finished=True)
        return True
