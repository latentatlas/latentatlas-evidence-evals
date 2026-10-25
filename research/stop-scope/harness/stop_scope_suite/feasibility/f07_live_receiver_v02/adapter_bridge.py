"""RPC seam under the real BackendProtocol async-to-worker tool dispatch."""
import asyncio
from copy import deepcopy
import threading
import time
from pathlib import Path
import hashlib
import importlib.util
import sys

from common import call, require
from comparison_config import LIMITS, QUALIFIED_WIRE_SHA256

HERE = Path(__file__).resolve().parent


def load_wire_module():
    """Bind to this frozen source, not the mutable global module-search path."""
    path = HERE / "native_bridge.py"
    require(hashlib.sha256(path.read_bytes()).hexdigest() == QUALIFIED_WIRE_SHA256,
            "Qualified native wire changed")
    identity = hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]
    name = "_stop_scope_receiver_wire_" + identity + "_" + QUALIFIED_WIRE_SHA256
    if name in sys.modules:
        module = sys.modules[name]
        require(Path(module.__file__).resolve() == path.resolve(), "Wire module identity mismatch")
        return module
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


class RemoteController:
    def __init__(self, record, trusted, ledger, conn, log, files, base, core, projections):
        self.record, self.trusted, self.ledger = record, trusted, ledger
        self.conn, self.log, self.files = conn, log, Path(files)
        self.base, self.core, self.projections = base, core, projections
        self.ipc_lock, self.meta = threading.RLock(), threading.RLock()
        self.locks, self.workers, self.ops, self.targets = {}, {}, {}, {}
        self.closed = False
        self.releasing = False

    def rpc(self, action, **fields):
        with self.ipc_lock:
            return call(self.conn, self.log, action, **fields)

    def register(self, identity):
        self.ledger.check_identity(identity)
        with self.meta:
            return self.locks.setdefault(identity["origin_key"], threading.RLock())

    def execute(self, identity, op, callback, target=False):
        self.register(identity)
        grant = self.ledger.check_identity(identity)
        require(all(op.get(k) == v for k,v in identity.items()), "Mutation identity changed")
        oid, role = op["operation_id"], grant["role"]
        content = self.projections[oid].get("candidate_content")
        import json
        try: proposed = json.loads(content).get("stage")
        except (ValueError, TypeError, AttributeError): proposed = None
        root = self.base.get_backend(identity["thread_id"])._fixture_root
        self.rpc("register", grant=grant, identity=identity,
                 root_relative=str(root.relative_to(self.files)))
        try:
            # Serialize hold admission with release_all. A late operation after an
            # early-terminal release must not recreate the experimental barrier.
            with self.meta:
                require(not self.closed and oid not in self.workers, "Closed/replayed caller")
                candidate = not self.releasing and role not in self.targets and (
                    (role == "O" and proposed == "final") or role == "I")
                op = deepcopy(op) | {"checkpoint_candidate": candidate}
                self.workers[oid] = threading.Event()
                self.ops[oid] = op
                receipt = self.rpc("submit", op=op, hold=candidate)
                self.record("receiver_acceptance_bound", op=op, role=role, receipt=receipt,
                            inline_native_callback_used=False)
                if candidate: self.targets[role] = deepcopy(op)
            deadline = time.monotonic() + LIMITS["receiver_caller_seconds"]
            while True:
                state = self.rpc("status")["jobs"][oid]
                if state["done"]: break
                require(time.monotonic() < deadline, "Receiver caller observation timed out")
                time.sleep(.025)
            self.record("receiver_terminal_bound", op=op, state=state)
            result_type = self.core.WriteResult if op["tool"] == "write_file" else self.core.EditResult
            return result_type(**state["result"])
        finally:
            self.record("bridge_caller_finished", op=op)
            if oid in self.workers: self.workers[oid].set()

    def release_all(self):
        with self.meta:
            self.releasing = True
            self.record("receiver_future_holds_disabled")
            state = self.rpc("status")["jobs"]
            self.rpc("release", operation_ids=list(state))

    def drain(self):
        deadline = time.monotonic() + LIMITS["worker_finish_seconds"]
        for event in list(self.workers.values()):
            require(event.wait(max(0, deadline-time.monotonic())), "Caller not finished")
        state = self.rpc("status")["jobs"]
        require(all(j["done"] for j in state.values()), "Receiver not finished")
        self.record("bridge_drained", jobs=state)

    def finish(self):
        self.drain()
        self.closed = True


def install(a, conn, log, files, record, profile, transport):
    # Unmodified model/task/wire projection; only the execution seam changes.
    wire_module = load_wire_module()
    wire_install = wire_module.install
    record("wire_implementation_bound", path=str(Path(wire_module.__file__).resolve()),
           sha256=QUALIFIED_WIRE_SHA256)
    projections = {}
    def capture(kind, **fields):
        if kind == "mutation_request_snapshot":
            projections[fields["op"]["operation_id"]] = deepcopy(fields["projection"])
        record(kind, **fields)
    wire_install(a, schedule="before_effect", transport=transport, profile=profile)
    a.ScopeController = lambda rec, trusted, ledger, schedule, order: RemoteController(
        rec, trusted, ledger, conn, log, files, a.base, a.core, projections)
    return capture, transport
