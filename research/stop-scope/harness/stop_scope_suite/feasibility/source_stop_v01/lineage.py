"""Trusted runtime membership; a descendant shares its recorded root lock."""
from copy import deepcopy
import threading

from controller import NativeController
from contract import require


class LineageController(NativeController):
    def __init__(self, record, schedule, trusted):
        super().__init__(record, schedule)
        self.trusted = trusted
        self.members = {}

    def register(self, identity):
        key, origin = identity["key"], identity["origin_key"]
        with self.meta:
            require(self.trusted.get(key) == identity, "Caller differs from actual factory registry")
            root = self.trusted.get(origin)
            require(root is not None and root["key"] == root["origin_key"]
                    and root["thread_id"] == identity["thread_id"]
                    and root["invocation_id"] == identity["origin_invocation_id"], "Invalid root lineage")
            require(key not in self.members or self.members[key] == identity, "Caller identity rebound")
            if origin not in self.identities:
                self.identities[origin] = deepcopy(root)
                self.locks[origin] = threading.RLock()
            require(self.identities[origin] == root, "Root identity rebound")
            if key not in self.members:
                self.members[key] = deepcopy(identity)
                self.record("receiver_member_registered", identity=identity, root_identity=root)
            return self.locks[origin]
