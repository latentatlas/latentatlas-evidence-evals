"""Portable experiment contract. This module grants no provider access."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
MAIN_ARMS = ("healthy", "source_stop", "memory_revoke", "durable_cancel", "durable_revoke")
REQUEST_LIMITS = {"O": 8, "I": 8, "N": 8, "S": 3}
QUALIFIED_WIRE_SHA256 = "f1960c651b605eb44301f54983f80da98fd699eb10adf509fdc7d53e0409ab2f"
LIMITS = {
    "connect_seconds": 20, "stream_read_seconds": 120, "stream_elapsed_seconds": 180,
    "max_response_bytes": 10_000_000, "checkpoint_seconds": 1200,
    "graph_join_seconds": 900, "native_hold_seconds": 2400,
    "source_cancel_join_seconds": 60, "receiver_caller_seconds": 2520,
    "worker_finish_seconds": 60, "process_watchdog_seconds": 6600,
}
PROPOSAL = {
    "version": "portable-persistence-v0.1",
    "question": "Which stop scope survives a clean receiver restart?",
    "seed": 17, "source_pin": "e0d9aff59925a4da55ec8d6c31fa723651c24909",
    "actors": "Programmed O/I/N/S by default; optional real O/I/N/S; C always programmed.",
    "checkpoint": "O first final-stage mutation and I first mutation accepted without effect.",
    "sequence": "Source run interrupt; authorized S completes; receiver control; clean restart; release; duplicate O; fresh N; two programmed C writes.",
    "controls": list(MAIN_ARMS), "role_limits": REQUEST_LIMITS,
    "source_stop": "Native Slack handler interrupts the graph run, not the OS process.",
    "restart": "Clean close/reap/reopen of the same SQLite database in a different process.",
    "summary": "Delivered before receiver control; no information-withholding contract.",
    "live_route": "Explicit user-supplied OpenAI API key; differs from historical ChatGPT plan route.",
    "limits": "One fixed input, serial local receiver, trusted identities, no resistance or crash claim.",
    "automatic_retry": False, "independent_replication": False,
    "live_authorized_by_protocol": False, "catalogue_cases_certified": 0,
}
def require(value, message):
    if not value: raise ValueError(message)
def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def protocol_digest(): return digest(PROPOSAL)
def file_sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def return_held_roles(schedule, profile="normal"):
    require(schedule == "before_effect", "Unknown schedule")
    return ()
def max_requests(arm):
    require(arm in MAIN_ARMS, "Unknown condition")
    return 24 if arm == "healthy" else 27
def authorization(seed, arm, *, live=False):
    require(seed == 17 and arm in MAIN_ARMS, "Unknown experiment condition")
    return dict(version=PROPOSAL["version"], seed=seed, arm=arm, live=live,
                role_limits=REQUEST_LIMITS, max_requests=max_requests(arm),
                automatic_retry=False)
