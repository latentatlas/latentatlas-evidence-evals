"""Stable IPC endpoint while a supervisor replaces the durable receiver process."""
from copy import deepcopy
import json
from pathlib import Path
import threading
import time
import uuid
from bridge_dependencies import common, load
from comparison_config import LIMITS

require = common.require


class OfflineTransport:
    live = False
    actor = "programmed_wire_persistent_bridge"

    def __init__(self):
        self.count = 0

    async def complete(self, request, wire, *, fixture_events=None):
        require(fixture_events is not None, "Provider-free transport requires recorded fixture events")
        self.count += 1
        return deepcopy(fixture_events)

    def halt(self, reason):
        raise RuntimeError("Offline codec halted: " + reason)


class PersistentController:
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
            rid = str(uuid.uuid4())
            request = dict(rpc_id=rid, action=action, **fields)
            self.log.emit("rpc_sent", request=request)
            self.conn.send(request)
            require(self.conn.poll(60 if action == "restart" else 15), "Supervisor RPC timeout: " + action)
            reply = self.conn.recv()
            self.log.emit("rpc_returned", rpc_id=rid, reply=reply)
            require(reply["rpc_id"] == rid and reply.get("ok"), "Supervisor RPC failed")
            return reply

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
        try: proposed = json.loads(content).get("stage")
        except (ValueError, TypeError, AttributeError): proposed = None
        root = self.base.get_backend(identity["thread_id"])._fixture_root
        self.rpc("register", grant=grant, identity=identity, root_relative=str(root.relative_to(self.files)))
        try:
            with self.meta:
                require(not self.closed and oid not in self.workers, "Closed or replayed native caller")
                candidate = not self.releasing and role not in self.targets and (
                    (role == "O" and proposed == "final") or role == "I")
                op = deepcopy(op) | {"checkpoint_candidate": candidate}
                self.workers[oid] = threading.Event()
                self.ops[oid] = op
                receipt = self.rpc("submit", op=op)
                self.record("receiver_acceptance_bound", op=op, role=role, receipt=receipt,
                            inline_native_callback_used=False)
                if candidate:
                    self.targets[role] = deepcopy(op)
                else:
                    self.rpc("execute", operation_id=oid)
            deadline = time.monotonic() + LIMITS["receiver_caller_seconds"]
            while True:
                state = self.rpc("status")["jobs"][oid]
                if state["done"]: break
                require(time.monotonic() < deadline, "Persistent caller observation timed out")
                time.sleep(.04)
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
            for oid, job in state.items():
                if job["state"] == "queued": self.rpc("execute", operation_id=oid)

    def drain(self):
        deadline = time.monotonic() + LIMITS["worker_finish_seconds"]
        for event in list(self.workers.values()):
            require(event.wait(max(0, deadline-time.monotonic())), "Native caller not finished")
        state = self.rpc("status")["jobs"]
        require(all(j["done"] for j in state.values()), "Persistent receiver work remains unresolved")
        self.record("bridge_drained", jobs=state)

    def finish(self):
        self.drain()
        self.closed = True


def install(a, conn, log, files, record, profile, transport):
    wire_module = load("bridge_prior_adapter").load_wire_module()
    projections = {}
    def capture(kind, **fields):
        if kind == "mutation_request_snapshot":
            projections[fields["op"]["operation_id"]] = deepcopy(fields["projection"])
        record(kind, **fields)
    wire_module.install(a, schedule="before_effect", transport=transport, profile=profile)
    a.ScopeController = lambda rec,trusted,ledger,schedule,order: PersistentController(
        rec,trusted,ledger,conn,log,files,a.base,a.core,projections)
    record("persistent_bridge_installed", wire_file=str(Path(wire_module.__file__).resolve()),
           wire_sha256=common.sha(Path(wire_module.__file__).read_bytes()),
           execution="serial durable receiver RPC", credentials_accessed=transport.live)
    return capture, transport
