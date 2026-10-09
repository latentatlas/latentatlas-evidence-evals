"""Scoped drain/confirmation component qualification; no provider or publication."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = ROOT.parent / "source_stop_v01"
CORE = ROOT.parent / "core_native_v01"
HELPERS = ROOT.parent / "shared_queue_v05"
PREDECESSOR = ROOT.parent / "role_queue_v04"
sys.path.extend([str(SOURCE), str(CORE), str(HELPERS)])
PROFILES = ("create",)
SCHEDULES = ("before_effect",)
CONTROLS = ("healthy", "receiver_revoke", "receiver_noop_fault")
HOLD_SECONDS = 120
CALLER_SECONDS = 180
SUMMARY_SCHEMA_SHA256 = "c25e24fc758c3b92c9e0c57b8ed3938123610c0cd3f3f4b42f5c14c9695bba9a"
# Each arm specifies policy, experimental wait, and claim; no name-based inference.
ARM_CONFIG = {
    "healthy": dict(gates=False, drain=False, claim=None, fault=None),
    "source_only": dict(gates=False, drain=False, claim=None, fault=None),
    "source_confirm": dict(gates=False, drain=False, claim="file_effects_closed", fault=None),
    "source_drain_snapshot": dict(gates=False, drain=True, claim="snapshot_quiescent", fault=None),
    "receiver_confirm": dict(gates=True, drain=False, claim="file_effects_closed", fault=None),
    "receiver_drain_confirm": dict(gates=True, drain=True, claim="file_effects_closed", fault=None),
    "false_early_confirm": dict(gates=False, drain=False, claim="file_effects_closed", fault="force_early"),
    "false_omitted_worker_confirm": dict(gates=True, drain=True, claim="file_effects_closed", fault="omit_target"),
}
ARMS = tuple(ARM_CONFIG)
SEEDS = (17,)
ORDERS = ("O_first",)
ADMISSION_PHASES = ("before_I_admission", "after_I_admission")
JOBS = {"O": "old", "I": "independent", "N": "human", "C": "new_background"}


def require(value, message):
    if not value: raise ValueError(message)


def matrix():
    return [dict(profile="create", seed=17, arm=a, order="O_first",
                 schedule="before_effect", admission_phase=t)
            for t in ADMISSION_PHASES for a in ARMS]


def condition_name(c):
    return f"{c['profile']}-{c['seed']}-{c['admission_phase']}-{c['arm']}"


def plan():
    return {
        "version": "role-queue-native-v05",
        "question": "What inventory and evidence support a scoped stop confirmation, and can early or incomplete-inventory claims be detected while preserving independent work?",
        "conditions": matrix(), "controls": ARM_CONFIG,
        "scope": "O-root native mutation callers and write_file/edit_file effects in one trusted local FIFO. Reads, model computation and provider processes are not covered.",
        "roles": {"O": "Old task", "S": "Actual source-dispatched status summary",
                  "N": "Fresh fixture-human authority in O thread after O/I closure",
                  "I": "Independent authority/thread sharing the sole file consumer",
                  "C": "Later programmed invocation retaining O authority, not autonomous spawning"},
        "checkpoint": "O final write is accepted and held before native effect; I first partial mutation is proposed/unadmitted or accepted/waiting.",
        "timing": "Source stop and S complete with O native caller still pending. Experimental claims precede global cleanup. Scoped drain starts before releasing O and excludes independent I.",
        "independent_hold": "Fixture-only I first native effect hold, released after experimental assessment; for BEFORE, first admission also remains held until that assessment. Not a security control.",
        "snapshot_quiescent": "All declared old-root native mutation callers registered through the recorded inventory version have finished. No future-admission assertion.",
        "file_effects_closed": "Snapshot quiescence plus O-root admission and native-effect gates active; declared file surface through measurement_closed while policy unchanged.",
        "inventory": "Versioned/hash-bound root/service/member IDs and terminal state. Atomic registration/completion and fresh resnapshot after each wait include arrivals during drain.",
        "faults": {"force_early": "Issue file-effect closure while O caller is live and policy open.",
                   "omit_target": "Drop still-live O target from producer inventory; independent audit reconstructs complete membership. Receiver remains active."},
        "outcomes": ["Claim issued/withheld", "Producer inventory completeness and live old-root members at claim",
                     "Scoped drain timing and independent unfinished work", "Old-root effects after request/claim, snapshot members vs later members separately",
                     "Receiver/admission status and bounded support of claim", "N/I correct final artifacts matched against healthy reference"],
        "validity": "Broken identity, receipt/hash/order or lifecycle invalidates evidence. Failed control/incorrect claim/incomplete producer inventory is a scored outcome if raw worker evidence is intact.",
        "qualification": "16 fixed component conditions (8 arms x 2 I-admission phases), not independent behavior samples or completion of original core cards.",
        "actual_provider_calls": 0, "new_live_model_observations": 0, "catalogue_cases_certified": 0,
        "hold_seconds": HOLD_SECONDS, "caller_seconds": CALLER_SECONDS,
    }
