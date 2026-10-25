"""Separate process executing installed native backend mutations, not fixtures."""
from copy import deepcopy
from dataclasses import asdict
import os
from pathlib import Path
import threading

# Loaded by the isolated driver before importing the Open-SWE experiment stack.
from common import Journal, offline, require, sha
from comparison_config import LIMITS


class Service:
    def __init__(self, root, log, fault="none"):
        from deepagents.backends.filesystem import FilesystemBackend
        self.backend_type = FilesystemBackend
        self.root, self.log, self.fault = Path(root).resolve(), log, fault
        self.lock = threading.RLock()
        self.grants, self.jobs, self.revoked = {}, {}, set()

    def register(self, grant, identity, root_relative):
        inv = grant["invocation_id"]
        require(identity["invocation_id"] == inv and identity["thread_id"] == grant["thread_id"],
                "Caller/grant mismatch")
        require(identity["origin_invocation_id"] == (grant["parent_invocation_id"] or inv),
                "Origin/grant mismatch")
        root = self.root / root_relative
        require(root.is_dir() and self.root in root.resolve().parents and not root.is_symlink(),
                "Invalid sandbox root")
        value = dict(grant=grant, identity=identity, root_relative=root_relative)
        with self.lock:
            require(inv not in self.grants or self.grants[inv] == value, "Grant rebound")
            if inv not in self.grants:
                self.grants[inv] = deepcopy(value)
                self.log.emit("grant_registered", **value)
        return dict(status="registered")

    def view(self, job):
        return dict(operation_id=job["op"]["operation_id"], state=job["state"],
                    done=job["done"].is_set(), result=deepcopy(job.get("result")),
                    role=job["grant"]["role"])

    def submit(self, op, hold):
        with self.lock:
            binding = self.grants[op["invocation_id"]]
            require(all(op.get(k) == v for k,v in binding["identity"].items()),
                    "Operation identity mismatch")
            require(op["tool"] in {"write_file","edit_file"}, "Mutation tool not offered")
            payload = op["args"]["content"] if op["tool"] == "write_file" else op["args"]["new_string"]
            require(op["virtual_path"] == op["args"]["file_path"] and sha(payload) == op["content_sha256"],
                    "Operation payload mismatch")
            oid = op["operation_id"]
            require(oid not in self.jobs, "Duplicate operation ID")
            job = dict(op=deepcopy(op), grant=deepcopy(binding["grant"]),
                       root_relative=binding["root_relative"], state="accepted",
                       release=threading.Event(), done=threading.Event(), cancelled=False)
            if not hold: job["release"].set()
            self.jobs[oid] = job
            row = self.log.emit("job_accepted", op=op, grant=job["grant"], hold=hold)
            thread = threading.Thread(target=self.work, args=(job,), daemon=True)
            job["thread"] = thread
            thread.start()
            return dict(operation_id=oid, acceptance_seq=row["seq"],
                        receiver_instance=self.log.instance, payload_sha256=op["content_sha256"])

    def work(self, job):
        op, oid = job["op"], job["op"]["operation_id"]
        try:
            with self.lock:
                job["state"] = "held_before_effect"
                self.log.emit("worker_entered", operation_id=oid, thread_id=threading.get_ident())
            require(job["release"].wait(LIMITS["native_hold_seconds"]), "Receiver effect barrier timed out")
            with self.lock:
                denied = job["cancelled"] or op["origin_invocation_id"] in self.revoked
                self.log.emit("effect_decision", operation_id=oid, allowed=not denied)
                if denied:
                    job["result"] = dict(error="The requested file write was not performed.")
                    job["state"] = "denied"
                    self.log.emit("effect_denied", operation_id=oid)
                else:
                    self.apply(job)
        except BaseException as exc:
            with self.lock:
                job["state"] = "error"
                job["result"] = dict(error="Receiving executor failed.")
                self.log.emit("worker_error", operation_id=oid, error_type=type(exc).__name__, error=str(exc))
        finally:
            with self.lock:
                self.log.emit("worker_finished", operation_id=oid, state=job["state"], result=job.get("result"))
                job["done"].set()

    def apply(self, job):
        from path_policy import safe_output
        op = job["op"]
        root = self.root / job["root_relative"]
        target = safe_output(root, op["virtual_path"])
        if target is None:
            job["result"] = dict(error="Output path is outside the permitted local output area.")
            job["state"] = "path_denied"
            self.log.emit("output_boundary_denied", operation_id=op["operation_id"])
            return
        before = target.read_bytes().decode() if target.is_file() else None
        self.log.emit("native_effect_attempt", operation_id=op["operation_id"],
                      path=str(target.relative_to(self.root)), before_content=before,
                      before_sha256=sha(before) if before is not None else None)
        backend = self.backend_type(root_dir=root, virtual_mode=True)
        function = backend.write if op["tool"] == "write_file" else backend.edit
        result = function(**op["args"])
        after = target.read_bytes().decode() if target.is_file() else None
        job["result"] = asdict(result)
        job["state"] = "completed" if result.error is None else "native_error"
        if not (self.fault == "omit_receipt" and job["grant"]["role"] == "O"
                and op.get("checkpoint_candidate")):
            self.log.emit("native_effect_result", operation_id=op["operation_id"],
                          path=str(target.relative_to(self.root)), success=result.error is None,
                          error=result.error, after_content=after,
                          after_sha256=sha(after) if after is not None else None)

    def dispatch(self, q):
        action = q["action"]
        with self.lock:
            if action == "register": return self.register(q["grant"], q["identity"], q["root_relative"])
            if action == "submit": return self.submit(q["op"], q["hold"])
            if action == "status": return dict(jobs={k:self.view(j) for k,j in self.jobs.items()})
            if action == "boundary":
                row = self.log.emit("intervention_boundary", token=q["token"])
                return dict(receiver_seq=row["seq"])
            if action == "cancel_job":
                job = self.jobs[q["operation_id"]]
                status = "already_terminal" if job["done"].is_set() else "cancellation_registered"
                if not job["done"].is_set(): job["cancelled"] = True
                row = self.log.emit("cancel_response", operation_id=q["operation_id"], status=status)
                return dict(status=status, receiver_seq=row["seq"], quiescence_claim=False)
            if action == "revoke_origin":
                require(q["origin"] in {v["identity"]["origin_invocation_id"] for v in self.grants.values()},
                        "Unknown origin")
                if self.fault != "noop_revoke":
                    self.revoked.update({v["identity"]["origin_invocation_id"] for v in self.grants.values()}
                                        if self.fault == "broad_revoke" else {q["origin"]})
                # Fault also denies later newly-authorized identities for its sensitivity check.
                self.broad = self.fault == "broad_revoke"
                row = self.log.emit("revocation_response", origin=q["origin"])
                return dict(status="revocation_registered", receiver_seq=row["seq"])
            if action == "release":
                for oid in q["operation_ids"]: self.jobs[oid]["release"].set()
                self.log.emit("jobs_released", operation_ids=q["operation_ids"])
                return dict(status="released")
            if action == "shutdown":
                require(all(j["done"].is_set() for j in self.jobs.values()), "Pending receiver work")
                return dict(status="closed")
        raise ValueError("Unknown receiver action")


def main(conn, root, log_path, fault):
    offline()
    log = Journal(log_path, "receiver")
    service = Service(root, log, fault)
    log.emit("receiver_started", backend="installed FilesystemBackend.write/edit", fault=fault)
    conn.send(dict(ready=True, pid=os.getpid(), instance=log.instance))
    try:
        while True:
            q = conn.recv()
            log.emit("rpc_received", request=q)
            try:
                if q["action"] == "register" and getattr(service, "broad", False):
                    service.revoked.add(q["identity"]["origin_invocation_id"])
                reply = dict(ok=True, **service.dispatch(q))
            except Exception as exc:
                reply = dict(ok=False, error_type=type(exc).__name__, error=str(exc))
            reply.update(rpc_id=q["rpc_id"], receiver_pid=os.getpid(), receiver_instance=log.instance)
            log.emit("rpc_replied", rpc_id=q["rpc_id"], reply=reply)
            conn.send(reply)
            if q["action"] == "shutdown" and reply["ok"]:
                for job in service.jobs.values():
                    job["thread"].join(2)
                    require(not job["thread"].is_alive(), "Receiver thread not joined")
                log.emit("receiver_closed")
                return
    finally:
        conn.close()
        log.close()
