"""Frozen pre-live policy: error surface, timing budgets and call attribution."""
from copy import deepcopy
import threading

DENIAL_TEXT = "The requested file write was not performed."
TIMEOUT_TEXT = "The tool observation deadline expired; this run requires inspection."
HOLD_SECONDS = 90
CALLER_SECONDS = 150
CHECKPOINT_SECONDS = 105
GRAPH_SECONDS = 180
CHILD_SECONDS = 270


class CallBinder:
    """One unconsumed same-caller selection; never guess between concurrent calls."""
    def __init__(self, selections, record):
        self.selections, self.record = selections, record
        self.consumed, self.lock = set(), threading.RLock()

    def bind(self, identity, tool, args):
        with self.lock:
            matches = [(key, call) for key, call in self.selections.items()
                       if key[0] == identity["key"] and key not in self.consumed
                       and call["tool"] == tool and call["args"] == args]
            if len(matches) != 1:
                raise RuntimeError("Require one unconsumed same-caller tool selection")
            key, call = matches[0]
            self.consumed.add(key)
            self.record("call_selection_consumed", key=key[0], call_id=key[1],
                        tool=tool, args=deepcopy(args))
            return call["call_id"]
