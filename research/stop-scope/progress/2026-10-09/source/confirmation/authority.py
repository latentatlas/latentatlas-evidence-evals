"""Fixture-only trusted authority, separate from model-selected paths or IDs."""
from copy import deepcopy
import uuid
from contract import JOBS, require


class AuthorityLedger:
    def __init__(self, record): self.record, self.grants = record, {}
    def declare(self, role, thread, invocation, *, parent=None):
        require(role in {*JOBS, "S"} and invocation not in self.grants, "Unknown role or reused grant")
        require(bool(parent) == (role in {"S", "C"}), "Derived role requires parent; human/independent root does not")
        if parent:
            require(parent in self.grants and self.grants[parent]["role"] == "O" and self.grants[parent]["thread_id"] == thread, "Unknown or cross-thread parent")
        item = {"authority_id": str(uuid.uuid4()), "role": role, "thread_id": thread, "invocation_id": invocation,
                "parent_invocation_id": parent, "job_id": JOBS.get(role),
                "authority_kind": "source_summary" if role == "S" else "continuation_probe" if role == "C" else "fixture_human_task",
                "issuer": "trusted_fixture_workflow" if parent else "trusted_fixture_operator"}
        self.grants[invocation] = deepcopy(item)
        self.record("authority_declared", **item)
        return deepcopy(item)
    def lookup(self, invocation, thread):
        g = self.grants.get(invocation)
        require(g is not None and g["thread_id"] == thread, "No matching dispatch authority")
        return deepcopy(g)
    def check_identity(self, identity):
        g = self.lookup(identity["invocation_id"], identity["thread_id"])
        expected = g["parent_invocation_id"] or g["invocation_id"]
        require(identity["origin_invocation_id"] == expected, "Runtime root disagrees with dispatch authority")
        return g
