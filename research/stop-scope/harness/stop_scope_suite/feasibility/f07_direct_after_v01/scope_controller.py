"""Inline executor-worker control: no research queue or consumer thread."""
from copy import deepcopy
from contextlib import ExitStack
import threading
import uuid
from contract import ARMS, ARM_CONFIG, SCHEDULES, ORDERS, HOLD_SECONDS, require
from lineage import LineageController
from controller import Denied
from termination import TerminationMixin


class ScopeController(TerminationMixin, LineageController):
    def __init__(self, record, trusted, ledger, schedule="after_effect", order="O_first"):
        require(schedule in SCHEDULES and order in ORDERS, "Unknown timing boundary/order")
        super().__init__(record, schedule, trusted)
        self.ledger, self.order = ledger, order
        self.service_id = str(uuid.uuid4())
        self.control_fault = None
        self.policy = dict(kind="open", root=None, thread=None, admission=False, effect=False)
        self.role_holds = {r: threading.Event() for r in ("O", "I")}
        self.role_releases = {r: threading.Event() for r in ("O", "I")}
        self.after_effect_holds = {r: threading.Event() for r in ("O", "I")}
        self.return_releases = {r: threading.Event() for r in ("O", "I")}
        self.targets, self.worker_ops, self.worker_threads, self.states = {}, {}, {}, {}
        self.inventory_version = 0
        self.closed = False
        record("direct_execution_created", service_id=self.service_id,
               per_origin_effect_locks=True, research_queue=False, consumer_count=0,
               dispatch="installed BackendProtocol.awrite/aedit -> asyncio.to_thread -> synchronous wrapper -> FilesystemBackend.write/edit",
               schedule=schedule, order=order)

    def snapshot(self):
        with self.meta:
            return dict(service_id=self.service_id, states=deepcopy(self.states),
                        worker_threads=deepcopy(self.worker_threads),
                        pending_ids=sorted(k for k, v in self.workers.items() if not v.is_set()))

    def activate(self, arm, old):
        require(arm in ARMS, "Unknown scope arm")
        self.register(old)
        # The fault that targets ALL origins takes every currently registered
        # origin lock. No metadata lock is held while acquiring an effect lock.
        with self.meta:
            roots = sorted(self.locks) if ARM_CONFIG[arm]["policy_kind"] == "service" else [old["origin_key"]]
            locks = [self.locks[root] for root in roots]
        with ExitStack() as stack:
            for lock in locks: stack.enter_context(lock)
            with self.meta:
                require(not self.intervened, "Duplicate intervention")
                self.intervened = True
                cfg = ARM_CONFIG[arm]
                self.control_fault = cfg["fault"]
                self.policy = dict(kind=cfg["policy_kind"], root=old["origin_key"],
                                   thread=old["thread_id"], admission=False, effect=cfg["effect"])
                self.record("scope_policy_activated", arm=arm, policy=deepcopy(self.policy),
                            service_id=self.service_id, execution=self.snapshot())

    def allowed(self, identity, phase="effect"):
        require(phase == "effect", "Direct worker exposes only an effect boundary")
        if self.control_fault == "receiver_noop": return True
        p = self.policy
        targeted = p["kind"] == "service" or (p["kind"] == "origin" and p["root"] == identity["origin_key"])
        return not (p["effect"] and targeted)

    def execute(self, identity, op, callback, target=False):
        lock = self.register(identity)
        grant = self.ledger.check_identity(identity)
        require(all(op.get(k) == v for k, v in identity.items()), "Unbound operation")
        role, oid = grant["role"], op["operation_id"]
        done = threading.Event()
        with self.meta:
            require(not self.closed and oid not in self.workers, "Closed execution/replayed operation")
            candidate = ((role == "O" and op["call_id"] == "target-" + identity["key"])
                         or (role == "I" and role not in self.targets))
            if candidate: require(role not in self.targets, "Repeated role candidate")
            self.workers[oid], self.worker_ops[oid] = done, deepcopy(op)
            self.worker_threads[oid], self.states[oid] = threading.get_ident(), "entered"
            self.record("native_worker_entered", op=op, service_id=self.service_id, worker_ident=threading.get_ident())
            if candidate:
                self.targets[role] = deepcopy(op)
                self.states[oid] = "held_before_effect"
                self.record("direct_candidate_ready", role=role, op=op, service_id=self.service_id,
                            selection="first_mutation" if role == "I" else "old_target")
                self.role_holds[role].set()
        try:
            if candidate and not self.role_releases[role].wait(HOLD_SECONDS):
                self.deadline_failures.append(oid)
                self.record("native_boundary_timeout", op=op)
                raise TimeoutError("Direct worker barrier expired")
            with lock:
                allowed = self.allowed(identity)
                self.record("receiver_check", op=op, allowed=allowed,
                            policy=deepcopy(self.policy), service_id=self.service_id,
                            worker_ident=threading.get_ident())
                if not allowed:
                    self.record("receiver_denied", op=op)
                    raise Denied("file_scope_blocked")
                result = callback()
                with self.meta: self.states[oid] = "effect_returned" if result.error is None else "effect_error"
            # Waiting here must NOT hold the origin lock: late revocation can
            # acquire it while the native caller remains outstanding.
            self.record("native_effect_lock_released", op=op, worker_ident=threading.get_ident())
            if candidate:
                with self.meta:
                    self.states[oid] = "held_after_effect"
                    self.record("direct_after_effect_ready", role=role, op=op,
                                callback_success=result.error is None, service_id=self.service_id)
                    self.after_effect_holds[role].set()
                if not self.return_releases[role].wait(HOLD_SECONDS):
                    self.deadline_failures.append(oid)
                    self.record("native_return_timeout", op=op)
                    raise TimeoutError("Post-effect return barrier expired")
            return result
        except BaseException as exc:
            with self.meta: self.states[oid] = "denied" if isinstance(exc, Denied) else "error"
            self.record("native_worker_error", op=op, error_type=type(exc).__name__, error=str(exc))
            raise
        finally:
            with self.meta:
                self.record("native_worker_finished", op=op, worker_ident=threading.get_ident(), state=self.states[oid])
                done.set()

    def release_role(self, role, reason):
        with self.meta:
            if not self.role_releases[role].is_set():
                self.record("direct_candidate_released", role=role, reason=reason)
                self.role_releases[role].set()

    def release_all(self, reason):
        for role in self.role_releases:
            self.release_role(role, reason)
            self.release_return(role, reason)

    def release_return(self, role, reason):
        with self.meta:
            if not self.return_releases[role].is_set():
                self.record("direct_return_released", role=role, reason=reason)
                self.return_releases[role].set()

    def finish(self):
        with self.meta:
            if self.closed: return
            require(all(d.is_set() for d in self.workers.values()), "Direct native callers not quiescent")
            self.closed = True
            self.record("direct_execution_closed", service_id=self.service_id,
                        operation_ids=sorted(self.workers), research_consumer_created=False)
