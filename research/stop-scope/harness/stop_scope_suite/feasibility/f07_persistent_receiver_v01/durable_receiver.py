"""SQLite queue and stop decisions across receiver process lifetimes.

Reuse Service.apply unchanged for installed FilesystemBackend.write/edit.
Scheduling is deliberately explicit and serial in this provider-free slice.
An executing row on recovery is quarantined, never silently retried.
"""
from copy import deepcopy
import json
import inspect
import os
from pathlib import Path
import sqlite3
import sys
import uuid

from dependencies import common, prior_receiver

require, sha = common.require, common.sha


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def inspect_database(path):
    """Read-only inspection independent of the service's in-memory state."""
    conn = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        require(conn.execute("PRAGMA integrity_check").fetchall() == [("ok",)], "SQLite integrity failure")
        return {table:[dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]
                for table in ("meta", "grants", "jobs", "controls")
                for cur in (conn.execute("SELECT * FROM " + table + " ORDER BY 1"),)}
    finally:
        conn.close()


class Service(prior_receiver.Service):
    def __init__(self, root, database, log, fault="none"):
        super().__init__(root, log, "omit_receipt" if fault == "omit_receipt" else "none")
        self.recovery_fault = fault
        self.database = Path(database).resolve()
        require(self.database.parent.is_dir() and not self.database.is_symlink(), "Unsafe database path")
        self.db = sqlite3.connect(self.database)
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA synchronous=FULL")
        with self.db:
            self.db.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS grants (invocation TEXT PRIMARY KEY, body TEXT NOT NULL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS jobs (operation TEXT PRIMARY KEY, body TEXT NOT NULL, state TEXT NOT NULL, result TEXT)")
            self.db.execute("CREATE TABLE IF NOT EXISTS controls (kind TEXT NOT NULL, target TEXT NOT NULL, PRIMARY KEY(kind,target))")
            self.db.execute("INSERT OR IGNORE INTO meta VALUES ('database_id', ?)", (str(uuid.uuid4()),))
        self.database_id = self.db.execute("SELECT value FROM meta WHERE key='database_id'").fetchone()[0]
        self.cancelled, self.deny_all = set(), False
        for (body,) in self.db.execute("SELECT body FROM grants ORDER BY invocation"):
            binding = json.loads(body)
            super().register(**binding)
        for kind, target in self.db.execute("SELECT kind,target FROM controls"):
            if kind == "cancel": self.cancelled.add(target)
            elif kind == "revoke":
                if fault != "skip_restore_revocation": self.revoked.add(target)
            elif kind == "deny_all": self.deny_all = True
            else: raise ValueError("Unknown persisted control")
        for oid, body, state, result in self.db.execute("SELECT operation,body,state,result FROM jobs ORDER BY operation").fetchall():
            op = json.loads(body)
            self.validate(op)
            require(oid == op["operation_id"], "Recovered operation identity changed")
            require(state in {"queued", "executing", "uncertain", "completed", "denied", "path_denied", "native_error"}, "Unknown persisted state")
            if state == "executing":
                state = "uncertain"
                with self.db: self.db.execute("UPDATE jobs SET state=? WHERE operation=?", (state, oid))
            self.jobs[oid] = self.job(op, state, json.loads(result) if result else None)
            self.log.emit("job_recovered", operation_id=oid, op=op, state=state, database_id=self.database_id)
        self.log.emit("receiver_recovered", database_id=self.database_id, database_path=str(self.database),
            jobs=sorted(self.jobs), cancelled=sorted(self.cancelled), revoked=sorted(self.revoked), deny_all=self.deny_all)

    def validate(self, op):
        binding = self.grants[op["invocation_id"]]
        require(all(op.get(k) == v for k,v in binding["identity"].items()), "Operation identity mismatch")
        require(op["tool"] in {"write_file", "edit_file"}, "Mutation tool not offered")
        payload = op["args"]["content"] if op["tool"] == "write_file" else op["args"]["new_string"]
        require(op["virtual_path"] == op["args"]["file_path"] and sha(payload) == op["content_sha256"], "Operation payload mismatch")
        require(isinstance(op["operation_id"], str) and op["operation_id"], "Missing operation identity")
        return binding

    def job(self, op, state="queued", result=None):
        b = self.grants[op["invocation_id"]]
        return dict(op=deepcopy(op), grant=deepcopy(b["grant"]), root_relative=b["root_relative"], state=state, result=result)

    def register(self, grant, identity, root_relative):
        result = super().register(grant, identity, root_relative)
        binding = dict(grant=grant, identity=identity, root_relative=root_relative)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO grants VALUES (?,?)", (grant["invocation_id"], canon(binding)))
        self.log.emit("grant_persisted", invocation_id=grant["invocation_id"], binding_sha256=sha(canon(binding)))
        return result

    def view(self, job):
        return dict(operation_id=job["op"]["operation_id"], state=job["state"],
                    done=job["state"] not in {"queued", "executing", "uncertain"}, result=deepcopy(job["result"]),
                    role=job["grant"]["role"])

    def submit(self, op):
        self.validate(op)
        oid = op["operation_id"]
        if oid in self.jobs:
            require(self.jobs[oid]["op"] == op, "Operation ID rebound to different content/identity")
            row = self.log.emit("duplicate_delivery", operation_id=oid, state=self.jobs[oid]["state"])
            return dict(status="existing", operation_id=oid, receiver_seq=row["seq"], job=self.view(self.jobs[oid]))
        with self.db:
            self.db.execute("INSERT INTO jobs VALUES (?,?,?,NULL)", (oid, canon(op), "queued"))
        self.jobs[oid] = self.job(op)
        row = self.log.emit("job_persisted", operation_id=oid, op=op, body_sha256=sha(canon(op)), database_id=self.database_id)
        return dict(status="accepted", operation_id=oid, receiver_seq=row["seq"], body_sha256=sha(canon(op)))

    def control(self, kind, target, durable):
        require(kind in {"cancel", "revoke", "deny_all"}, "Unknown control")
        if kind == "cancel": require(target in self.jobs, "Unknown cancelled operation")
        if kind == "revoke": require(target in {x["identity"]["origin_invocation_id"] for x in self.grants.values()}, "Unknown revoked origin")
        if durable:
            with self.db:
                self.db.execute("INSERT OR IGNORE INTO controls VALUES (?,?)", (kind, target))
                if kind == "revoke" and self.recovery_fault == "broad_revoke":
                    self.db.execute("INSERT OR IGNORE INTO controls VALUES ('deny_all','*')")
        if kind == "cancel": self.cancelled.add(target)
        elif kind == "revoke": self.revoked.add(target)
        else: self.deny_all = True
        if kind == "revoke" and self.recovery_fault == "broad_revoke": self.deny_all = True
        row = self.log.emit("control_acknowledged", control_kind=kind, target=target, durable=durable)
        return dict(status="registered", receiver_seq=row["seq"], durable=durable, quiescence_claim=False)

    def execute(self, oid):
        job = self.jobs[oid]
        if job["state"] != "queued":
            self.log.emit("execution_not_repeated", operation_id=oid, state=job["state"])
            return self.view(job)
        # The DB intent, authority check and actual native effect share this
        # receiver lock. Filesystem and SQLite are not one crash transaction.
        with self.lock:
            with self.db: self.db.execute("UPDATE jobs SET state='executing' WHERE operation=?", (oid,))
            job["state"] = "executing"
            self.log.emit("execution_started", operation_id=oid)
            denied = oid in self.cancelled or job["op"]["origin_invocation_id"] in self.revoked or self.deny_all
            self.log.emit("effect_decision", operation_id=oid, allowed=not denied)
            if denied:
                job.update(state="denied", result=dict(error="The requested file write was not performed."))
                self.log.emit("effect_denied", operation_id=oid)
            else:
                self.apply(job)
            with self.db:
                self.db.execute("UPDATE jobs SET state=?,result=? WHERE operation=?", (job["state"], canon(job["result"]), oid))
            self.log.emit("job_terminal", operation_id=oid, state=job["state"], result=job["result"])
            return self.view(job)

    def dispatch(self, q):
        with self.lock:
            action = q["action"]
            if action == "register": return self.register(q["grant"], q["identity"], q["root_relative"])
            if action == "submit": return self.submit(q["op"])
            if action == "control": return self.control(q["kind"], q["target"], q["durable"])
            if action == "execute": return self.execute(q["operation_id"])
            if action == "status": return dict(database_id=self.database_id, jobs={k:self.view(j) for k,j in self.jobs.items()},
                                                 revoked=sorted(self.revoked), cancelled=sorted(self.cancelled), deny_all=self.deny_all)
            if action == "close":
                # Explicit suspension: queued work is retained, not claimed done.
                pending = [k for k,j in self.jobs.items() if not self.view(j)["done"]]
                self.db.close()
                self.log.emit("receiver_closed", pending=pending, quiescence_claim=False)
                return dict(status="closed_with_persisted_state", pending=pending, quiescence_claim=False)
        raise ValueError("Unknown action")


def main(conn, root, database, log_path, fault):
    common.offline()
    log = common.Journal(log_path, "receiver")
    service = None
    try:
        service = Service(root, database, log, fault)
        backend_file=Path(inspect.getfile(service.backend_type)).resolve()
        log.emit("receiver_started", backend="inherited installed FilesystemBackend.write/edit", fault=fault,
            backend_file=str(backend_file), backend_sha256=sha(backend_file.read_bytes()),
            python_version=sys.version, sqlite_version=sqlite3.sqlite_version)
        conn.send(dict(ready=True, pid=os.getpid(), instance=log.instance, database_id=service.database_id))
        while True:
            q = conn.recv()
            log.emit("rpc_received", request=q)
            try: reply = dict(ok=True, **service.dispatch(q))
            except Exception as exc: reply = dict(ok=False, error_type=type(exc).__name__, error=str(exc))
            reply.update(rpc_id=q["rpc_id"], receiver_pid=os.getpid(), receiver_instance=log.instance)
            log.emit("rpc_replied", rpc_id=q["rpc_id"], reply=reply)
            conn.send(reply)
            if q["action"] == "close" and reply["ok"]: return
    finally:
        if service:
            try: service.db.close()
            except sqlite3.ProgrammingError: pass
        conn.close()
        log.close()
