"""Extra cancellation probe with explicit immutable targets and real SDK receipts."""
import asyncio
from copy import deepcopy
import json
import uuid
from urllib.parse import parse_qs
import httpx
from contract import require

MODES = {"none", "same_saved_targets", "refresh_active_thread"}


def saved_target(req, old):
    body = json.loads(req["body"])
    require(req["method"] == "POST" and req["path"] == "/runs/cancel", "Not a source cancellation")
    require(body == {"thread_id": old["thread_id"], "run_ids": [old["run_id"]]}, "Source target not the old run")
    require(parse_qs(req["query"]).get("action") == ["interrupt"], "Source action differs")
    return dict(thread_id=body["thread_id"], run_ids=list(body["run_ids"]), action="interrupt")


def validate_targets(targets, known):
    require(isinstance(targets, list) and all(isinstance(x, str) and x for x in targets), "Malformed target IDs")
    require(len(targets) == len(set(targets)), "Duplicate target ID")
    require(set(targets) <= set(known), "Unknown cancellation target")
    return list(targets)


async def run_probe(client, source, record, rows, old, summary, mode, old_pending):
    require(mode in MODES, "Unknown cancellation strategy")
    source_requests = [r for r in rows if r["kind"] == "native_http_request" and r["method"] == "POST" and r["path"] == "/runs/cancel"]
    require(len(source_requests) == 1, "Missing/ambiguous source cancellation")
    source_req = source_requests[0]; saved = saved_target(source_req, old)
    known = {old["run_id"]: "O", summary["run_id"]: "S"}
    pid = str(uuid.uuid4())
    record("cancel_probe_started", probe_id=pid, mode=mode,
           source_request_id=source_req["request_id"], saved=deepcopy(saved),
           known_targets=known, old_worker_pending=old_pending())
    async def snapshot(phase):
        for label, role in (("O", old), ("S", summary)):
            state = await client.runs.get(role["thread_id"], role["run_id"])
            record("cancel_probe_run_state", probe_id=pid, phase=phase, role=label,
                   thread_id=role["thread_id"], run_id=role["run_id"], state=state)
    await snapshot("before")
    targets = (saved["run_ids"] if mode == "same_saved_targets"
               else await source._active_run_ids(client, old["thread_id"]) if mode == "refresh_active_thread"
               else [])
    targets = validate_targets(targets, known)
    record("cancel_probe_targets_selected", probe_id=pid, mode=mode,
           thread_id=old["thread_id"], run_ids=targets, action="interrupt")
    if not targets:
        # SDK omits run_ids when empty; never accidentally broaden to all thread runs.
        record("extra_cancel_result", probe_id=pid, disposition="not_sent", reason="baseline" if mode == "none" else "no_active_targets")
    else:
        record("extra_cancel_requested", probe_id=pid, thread_id=old["thread_id"], run_ids=targets, action="interrupt")
        accepted = False
        try:
            await client.runs.cancel_many(thread_id=old["thread_id"], run_ids=targets, action="interrupt")
            accepted = True
            record("extra_cancel_result", probe_id=pid, disposition="sdk_returned")
        except httpx.HTTPStatusError as exc:
            record("extra_cancel_result", probe_id=pid, disposition="http_rejected",
                   status_code=exc.response.status_code, error_type=type(exc).__name__)
        if accepted and summary["run_id"] in targets:
            try:
                await asyncio.wait_for(client.runs.join(summary["thread_id"], summary["run_id"]), 5)
                record("extra_cancel_summary_wait", probe_id=pid, status="join_returned", timeout_seconds=5)
            except TimeoutError:
                record("extra_cancel_summary_wait", probe_id=pid, status="timeout", timeout_seconds=5)
    await snapshot("after")
    record("cancel_probe_finished", probe_id=pid, old_worker_pending=old_pending())
