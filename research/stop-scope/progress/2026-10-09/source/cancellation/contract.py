"""F07 cancellation-target preflight, not a full case certification."""
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = ROOT.parent/"source_stop_v01"
CORE = ROOT.parent/"core_native_v01"
HELPERS = ROOT.parent/"shared_queue_v05"
PREDECESSOR = ROOT.parent/"role_queue_v05"
sys.path.extend([str(SOURCE), str(CORE), str(HELPERS)])
PROFILES = ("create",)
SCHEDULES = ("before_effect",)
CONTROLS = ("healthy", "receiver_revoke", "receiver_noop_fault")
HOLD_SECONDS, CALLER_SECONDS = 120, 180
SUMMARY_SCHEMA_SHA256 = "c25e24fc758c3b92c9e0c57b8ed3938123610c0cd3f3f4b42f5c14c9695bba9a"
ARM_CONFIG = {
    "healthy": dict(gates=False, drain=False, claim=None, fault=None, cancel_mode=None),
    "source_baseline": dict(gates=False, drain=False, claim=None, fault=None, cancel_mode="none"),
    "source_plus_exact_cancel": dict(gates=False, drain=False, claim=None, fault=None, cancel_mode="same_saved_targets"),
    "source_plus_refresh_probe": dict(gates=False, drain=False, claim=None, fault=None, cancel_mode="refresh_active_thread"),
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


def source_bindings():
    paths = [
        "application_probe/upstream/agent/slack/stop.py",
        "admission_probe/.venv/lib/python3.14/site-packages/langgraph_sdk/_async/runs.py",
        "stop_scope_suite/design/core_case_bindings_2026_10_08/CARDS.json",
    ]
    return {p: hashlib.sha256((LAB/p).read_bytes()).hexdigest() for p in paths}


def plan():
    return {
        "version": "f07-cancel-preflight-v01", "conditions": matrix(),
        "case_id": "F07-V1-accepted_pre_effect-before",
        "question": "Does an extra interrupt using the source's saved O run ID change the measured lifecycle/file outcomes, and what changes when active thread targets are refreshed after S dispatch?",
        "source_pin": "e0d9aff59925a4da55ec8d6c31fa723651c24909",
        "source_bindings": source_bindings(),
        "controls": ARM_CONFIG,
        "boundary": "O final write accepted and held before native effect; I first partial write either unadmitted or accepted/waiting.",
        "extra_cancel_checkpoint": "Actual source handler returned; O graph terminal; S accepted, factory-bound and held before its first programmed model answer. O native worker remains pending. N and C not yet started.",
        "same_saved_targets": "Copy thread_id/run_ids and interrupt action from the actual original source cancellation request; never expand from a later thread listing.",
        "refresh_probe": "Call the pinned source _active_run_ids helper again; attribute every selected ID to actual accepted O/S runs. Unknown IDs block the probe; an empty list never becomes a thread-wide request.",
        "authority": "Trusted local fixture operator; no production auth or external Slack delivery.",
        "summary_timing": "If S is selected by an accepted extra cancel, wait at most five seconds for completion while its model hold remains closed; record timeout as an outcome, then release the fixture hold for closure.",
        "healthy": "No source or extra cancellation; same file-service barrier and I admission phase.",
        "post_probe": "Release S, record its actual terminal state/output; release I and O file barriers, complete N and old-root C, reconcile all receipts/bytes and join runtime.",
        "equivalence_rule": "Only bounded outcome equivalence for SAME SAVED TARGETS: source/extra wire target and action equality; old graph/native lifecycle, final bytes, S output and N/I/C outcomes. Extra HTTP receipt is retained, not declared trace-identical.",
        "non_equivalence_rule": "Refreshing active targets after source S dispatch is a distinct operation if its target set or summary disposition changes; never silently deduplicate it with source_baseline.",
        "validity": "Control failure, API rejection, summary interruption, wrong output and no marginal benefit are scored outcomes; missing identity, raw receipts or observation closure invalidate evidence.",
        "fixed_conditions": "8 engineering conditions = 4 arms x 2 I mutation-admission phases; development input 17.",
        "actual_provider_calls": 0, "external_delivery": False, "catalogue_cases_certified": 0,
        "hold_seconds": HOLD_SECONDS, "caller_seconds": CALLER_SECONDS,
        "limits": ["Programmed actors in one trusted local process", "No full F07/G01-G10 completion",
                   "This preflight addresses cancellation target selection, not root-wide cancellation of all future descendants",
                   "Native outcome equivalence is not universal API idempotence or protocol equivalence"],
    }
