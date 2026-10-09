"""All mutations share one FIFO; admission and effect authority are distinct."""
from collections import deque
from concurrent.futures import Future, wait
from contextvars import copy_context
from copy import deepcopy
from dataclasses import dataclass
import threading
import uuid

from contract import ARMS, ARM_CONFIG, SCHEDULES, HOLD_SECONDS, CALLER_SECONDS, require
from lineage import LineageController
from controller import Denied
from termination import TerminationMixin


@dataclass
class Job:
    op: dict
    callback: object
    context: object
    future: Future
    state: str = "waiting"
    callback_returned: bool = False
    callback_value: object = None


class ScopeController(TerminationMixin, LineageController):
    def __init__(self, record, trusted, ledger, schedule="before_effect"):
        require(schedule in SCHEDULES, "Unknown timing boundary")
        super().__init__(record, schedule, trusted)
        self.ledger = ledger
        self.service_id = str(uuid.uuid4())
        self.policy_lock = threading.RLock()
        self.changed = threading.Condition(self.policy_lock)
        self.policy = {"kind": "open", "root": None, "thread": None, "admission": False, "effect": False}
        self.role_holds = {r: threading.Event() for r in ("O", "I")}
        self.role_releases = {r: threading.Event() for r in ("O", "I")}
        self.targets, self.jobs, self.pending = {}, {}, deque()
        self.active = None
        self.worker_ops = {}
        self.inventory_version = 0
        self.independent_held = threading.Event()
        self.independent_release = threading.Event()
        self.independent_did_hold = False
        self.queue_held, self.queue_release = threading.Event(), threading.Event()
        self.did_hold = self.exiting = self.joined = False
        record("shared_file_service_created", service_id=self.service_id, shared_policy_lock=True,
               discipline="FIFO", all_mutations_queued=True, consumer_count=1, schedule=schedule)
        self.thread = threading.Thread(target=self._work, name="role-scope-fifo", daemon=False)
        self.thread.start()

    def snapshot(self):
        with self.policy_lock:
            return {"service_id": self.service_id,
                    "active": deepcopy(self.active.op) if self.active else None,
                    "waiting": [deepcopy(j.op) for j in self.pending],
                    "states": {oid: j.state for oid, j in self.jobs.items()}}

    def activate(self, arm, old):
        require(arm in ARMS, "Unknown scope arm")
        self.register(old)
        with self.policy_lock:
            require(not self.intervened, "Duplicate intervention")
            self.intervened = True
            gates = ARM_CONFIG[arm]["gates"]
            self.policy = {"kind": "origin" if gates else "open",
                           "root": old["origin_key"], "thread": old["thread_id"],
                           "admission": gates, "effect": gates}
            self.record("scope_policy_activated", arm=arm, policy=deepcopy(self.policy),
                        service_id=self.service_id, queue=self.snapshot())

    def allowed(self, identity, phase):
        require(phase in {"admission", "effect"}, "Unknown control boundary")
        p = self.policy
        targeted = (p["kind"] == "service" or
                    (p["kind"] == "thread" and p["thread"] == identity["thread_id"]) or
                    (p["kind"] == "origin" and p["root"] == identity["origin_key"]))
        return not (p[phase] and targeted)

    def execute(self, identity, op, callback, target=False):
        self.register(identity)
        grant = self.ledger.check_identity(identity)
        require(all(op.get(k) == v for k, v in identity.items()), "Unbound operation")
        role, oid = grant["role"], op["operation_id"]
        done = threading.Event()
        with self.meta:
            require(oid not in self.workers, "Replayed operation")
            candidate = ((role == "O" and op["call_id"] == "target-" + identity["key"])
                         or (role == "I" and role not in self.targets))
            if candidate:
                require(role not in self.targets, "Repeated role candidate")
            # Reject an invalid repeated candidate before registering a worker.
            # Otherwise a raised guard would leave an unfinishable drain entry.
            self.workers[oid] = done
            self.worker_ops[oid] = deepcopy(op)
            self.record("native_worker_entered", op=op, service_id=self.service_id, worker_ident=threading.get_ident())
            if candidate:
                self.targets[role] = deepcopy(op)
                self.record("queue_candidate_ready", role=role, op=op, service_id=self.service_id,
                            selection="first_mutation" if role == "I" else "old_target")
                self.role_holds[role].set()
        try:
            # I's first mutation is held by trusted role/order, not by its filename.
            if candidate:
                if not self.role_releases[role].wait(HOLD_SECONDS):
                    self.deadline_failures.append(oid)
                    self.record("native_boundary_timeout", op=op)
                    raise TimeoutError("Candidate admission barrier expired")
            with self.changed:
                allowed = not self.exiting and self.allowed(identity, "admission")
                self.record("queue_admission_check", op=op, allowed=allowed,
                            policy=deepcopy(self.policy), service_id=self.service_id)
                if not allowed:
                    self.record("queue_admission_denied", op=op)
                    raise Denied("file_scope_blocked")
                job = Job(deepcopy(op), callback, copy_context(), Future())
                self.jobs[oid] = job
                self.pending.append(job)
                self.record("queue_accepted", op=op, service_id=self.service_id,
                            waiting_ids=[j.op["operation_id"] for j in self.pending])
                self.changed.notify_all()
            if job.future not in wait([job.future], timeout=CALLER_SECONDS).done:
                # Resolve deadline versus in-lock native effect atomically.
                with self.changed:
                    if not job.future.done():
                        self.pending = deque(j for j in self.pending if j is not job)
                        if job.callback_returned:
                            # An expired reply wait cannot undo a completed filesystem call.
                            self._settle_callback(job)
                        else:
                            self._terminal(job, "cancelled", error=TimeoutError("caller_deadline_expired"))
                    self.deadline_failures.append(oid)
                    self.record("queue_caller_deadline_resolved", op=op, state=job.state)
                    self.changed.notify_all()
            return job.future.result()
        except BaseException as exc:
            self.record("native_worker_error", op=op, error_type=type(exc).__name__, error=str(exc))
            raise
        finally:
            with self.meta:
                self.record("native_worker_finished", op=op)
                done.set()

    def _terminal(self, job, state, *, value=None, error=None):
        require(not job.future.done(), "Duplicate terminal settlement")
        job.state = state
        self.record("queue_job_terminal", op=job.op, state=state, service_id=self.service_id,
                    reason=type(error).__name__ if error else "native_callback_returned")
        if error is not None:
            job.future.set_exception(error)
        else:
            job.future.set_result(value)

    def _settle_callback(self, job):
        require(job.callback_returned, "Callback has not returned")
        self._terminal(job, "committed" if getattr(job.callback_value, "error", None) is None else "error", value=job.callback_value)

    def _work(self):
        self.record("queue_consumer_started", service_id=self.service_id, worker_ident=threading.get_ident())
        while True:
            with self.changed:
                self.changed.wait_for(lambda: self.pending or self.exiting)
                if self.exiting and not self.pending:
                    self.record("queue_consumer_exited", service_id=self.service_id, worker_ident=threading.get_ident())
                    return
                job = self.pending.popleft()
                self.active, job.state = job, "claimed"
                target = job.op["call_id"] == "target-" + job.op["key"] and self.ledger.check_identity(job.op)["role"] == "O"
                held = target and not self.did_hold
                self.did_hold = self.did_hold or held
                self.record("queue_claimed", op=job.op, held=held,
                            service_id=self.service_id, worker_ident=threading.get_ident())
                if held:
                    self.queue_held.set()
                    if not self.changed.wait_for(lambda: self.queue_release.is_set() or job.future.done(), HOLD_SECONDS):
                        self.deadline_failures.append(job.op["operation_id"])
                        self._terminal(job, "error", error=TimeoutError("queue_barrier_timeout"))
                if self.ledger.check_identity(job.op)["role"] == "I" and not self.independent_did_hold:
                    self.independent_did_hold = True
                    self.record("independent_effect_held", op=job.op, service_id=self.service_id,
                                fixture_only=True)
                    self.independent_held.set()
                    if not self.changed.wait_for(lambda: self.independent_release.is_set() or job.future.done(), HOLD_SECONDS):
                        self.deadline_failures.append(job.op["operation_id"])
                        self._terminal(job, "error", error=TimeoutError("independent_fixture_timeout"))
                if not job.future.done():
                    allowed = self.allowed(job.op, "effect")
                    self.record("receiver_check", op=job.op, allowed=allowed,
                                policy=deepcopy(self.policy), service_id=self.service_id, worker_ident=threading.get_ident())
                    if not allowed:
                        self.record("receiver_denied", op=job.op)
                        self._terminal(job, "denied", error=Denied("file_scope_blocked"))
                    else:
                        try:
                            value = job.context.run(job.callback)
                            job.callback_returned, job.callback_value = True, value
                            if not job.future.done(): self._settle_callback(job)
                        except BaseException as exc:
                            if not job.future.done(): self._terminal(job, "error", error=exc)
                self.active = None
                self.changed.notify_all()

    def release_role(self, role, reason):
        with self.meta:
            if not self.role_releases[role].is_set():
                self.record("queue_candidate_released", role=role, reason=reason)
                self.role_releases[role].set()

    def release_queue(self, reason):
        with self.changed:
            if not self.queue_release.is_set():
                self.record("queue_barrier_released", reason=reason, service_id=self.service_id)
                self.queue_release.set()
                self.changed.notify_all()

    def release_independent(self, reason):
        with self.changed:
            if not self.independent_release.is_set():
                self.record("independent_effect_released", reason=reason, service_id=self.service_id, fixture_only=True)
                self.independent_release.set()
                self.changed.notify_all()

    def release_all(self, reason):
        for role in self.role_releases:
            self.release_role(role, reason)
        self.release_queue(reason)
        self.release_independent(reason)

    def finish(self):
        if self.joined:
            return
        with self.changed:
            require(self.active is None and not self.pending and all(j.future.done() for j in self.jobs.values()), "FIFO not quiescent")
            self.exiting = True
            self.changed.notify_all()
        self.thread.join(10)
        require(not self.thread.is_alive(), "FIFO consumer did not exit")
        self.joined = True
        self.record("queue_closed", service_id=self.service_id, snapshot=self.snapshot(), worker_joined=True)
