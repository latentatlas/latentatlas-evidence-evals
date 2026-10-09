"""Wire, identity and lifecycle reconciliation for additional cancellation."""
import json
from urllib.parse import parse_qs
from contract import ARM_CONFIG, require


def validate_cancellation(e):
    rows = e["rows"]
    def many(k): return [r for r in rows if r["kind"] == k]
    def one(k):
        rs = many(k); require(len(rs) == 1, "Expected one "+k); return rs[0]
    starts = many("cancel_probe_started")
    all_cancel = [r for r in rows if r["kind"] == "native_http_request" and r["method"] == "POST" and r["path"] == "/runs/cancel"]
    if not e["source_request"]:
        require(not starts and not all_cancel, "Cancellation without source in healthy reference")
        return None
    start, selection, finished, disposition = [one(k) for k in ("cancel_probe_started", "cancel_probe_targets_selected", "cancel_probe_finished", "extra_cancel_result")]
    pid = start["probe_id"]
    relevant = [r for r in rows if r["kind"].startswith(("cancel_probe_", "extra_cancel_"))]
    require(all(r["probe_id"] == pid for r in relevant), "Probe ID mismatch")
    require(start["seq"] < selection["seq"] < disposition["seq"] < finished["seq"], "Probe order")
    require(start["mode"] == selection["mode"] == ARM_CONFIG[e["result"]["arm"]]["cancel_mode"], "Probe mode mismatch")
    old, summary = e["by_role"]["O"], e["by_role"]["S"]
    known = {old["run_id"]: "O", summary["run_id"]: "S"}
    require(start["known_targets"] == known, "Unknown/changed target identity")
    require(len(e["cancel_requests"]) == 1, "Ambiguous original cancel")
    original = e["cancel_requests"][0]
    require(start["source_request_id"] == original["request_id"], "Unbound original cancel")
    original_payload = json.loads(original["body"])
    require(start["saved"] == {**original_payload, "action": "interrupt"}, "Changed saved target")
    require(selection["thread_id"] == old["thread_id"] and selection["action"] == "interrupt", "Changed extra cancel thread/action")
    ids = selection["run_ids"]
    require(len(ids) == len(set(ids)) and set(ids) <= set(known), "Unattributed/duplicate extra target")
    if start["mode"] == "same_saved_targets":
        require(ids == original_payload["run_ids"], "Saved target was refreshed")
    if start["mode"] == "none": require(ids == [], "Baseline sent extra targets")
    reqs = {r["request_id"]: r for r in rows if r["kind"] == "native_http_request"}
    responses = e["responses"]
    states = {}
    for r in many("cancel_probe_run_state"):
        role, phase = r["role"], r["phase"]
        require(role in {"O", "S"} and phase in {"before", "after"} and (phase, role) not in states, "Duplicate/foreign run snapshot")
        identity = e["by_role"][role]
        require(r["run_id"] == identity["run_id"] and r["thread_id"] == identity["thread_id"] and r["state"]["run_id"] == identity["run_id"], "Snapshot target mismatch")
        candidates = [req for rid, req in reqs.items() if req["method"] == "GET"
                      and req["path"] == f"/threads/{identity['thread_id']}/runs/{identity['run_id']}"
                      and start["seq"] < req["seq"] < responses[rid]["seq"] < r["seq"]]
        require(candidates, "Missing run state HTTP receipt")
        matched = max(candidates, key=lambda x: x["seq"])
        resp = responses[matched["request_id"]]
        require(resp["status"] == 200 and json.loads(resp["body"]) == r["state"], "Run snapshot differs from HTTP")
        require((start["seq"] < r["seq"] < selection["seq"]) if phase == "before" else (disposition["seq"] < r["seq"] < finished["seq"]), "State phase order")
        states[(phase, role)] = r
    require(set(states) == {(p,r) for p in ("before","after") for r in ("O","S")}, "Incomplete probe states")
    listings = []
    if start["mode"] == "refresh_active_thread":
        seen = set()
        for status in ("pending", "running"):
            pages = [req for req in reqs.values() if req["method"] == "GET"
                     and req["path"] == f"/threads/{old['thread_id']}/runs"
                     and states[("before","S")]["seq"] < req["seq"] < selection["seq"]
                     and parse_qs(req["query"]).get("status") == [status]]
            require(pages, "Refresh lacks status enumeration")
            offset = 0
            for ix, req in enumerate(pages):
                query = parse_qs(req["query"]); response = responses[req["request_id"]]
                require(query.get("limit") == ["100"] and query.get("offset") == [str(offset)]
                        and response["seq"] < selection["seq"] and response["status"] == 200, "Pagination/refresh receipt mismatch")
                data = json.loads(response["body"])
                require(isinstance(data, list), "Refresh response not a list")
                seen.update(x.get("run_id") or x.get("id") for x in data)
                if ix < len(pages)-1: require(len(data) == 100, "Refresh continued after final page")
                else: require(len(data) < 100, "Refresh enumeration incomplete")
                offset += len(data); listings.append(req["request_id"])
        require(ids == sorted(seen), "Selected IDs differ from actual active lists")
    extra = [r for r in all_cancel if selection["seq"] < r["seq"] < disposition["seq"]]
    require({r["request_id"] for r in all_cancel} == {r["request_id"] for r in e["cancel_requests"]+extra}, "Unaccounted cancellation request")
    requested = many("extra_cancel_requested")
    if ids:
        require(len(extra) == len(requested) == 1 and selection["seq"] < requested[0]["seq"] < extra[0]["seq"], "Extra cancel request missing")
        r = requested[0]; wire = extra[0]
        require(all(r[k] == selection[k] for k in ("thread_id","run_ids","action")), "Changed requested target")
        require(json.loads(wire["body"]) == {"thread_id": old["thread_id"], "run_ids": ids}
                and parse_qs(wire["query"]).get("action") == ["interrupt"], "Extra wire differs")
        response = responses[wire["request_id"]]
        require(response["seq"] < disposition["seq"], "Extra cancel return before HTTP receipt")
        if disposition["disposition"] == "sdk_returned": require(200 <= response["status"] < 300, "Success without accepted HTTP")
        else: require(disposition["disposition"] == "http_rejected" and disposition["status_code"] == response["status"] >= 400, "Rejection mismatch")
    else:
        require(not extra and not requested and disposition["disposition"] == "not_sent", "Empty target expanded to cancellation")
    waits = many("extra_cancel_summary_wait")
    if waits:
        require(len(waits) == 1 and summary["run_id"] in ids and disposition["disposition"] == "sdk_returned"
                and disposition["seq"] < waits[0]["seq"] < finished["seq"]
                and waits[0]["status"] in {"join_returned","timeout"}, "Unjustified summary wait")
        if waits[0]["status"] == "join_returned":
            joined = [req for req in reqs.values() if req["path"] == f"/threads/{summary['thread_id']}/runs/{summary['run_id']}/join"
                      and disposition["seq"] < req["seq"] < responses[req["request_id"]]["seq"] < waits[0]["seq"]]
            require(len(joined) == 1 and responses[joined[0]["request_id"]]["status"] < 300, "Unbound summary join receipt")
    target_id = e["target"]["op"]["operation_id"]
    terminal = e["queue"]["terminal"][target_id]
    for r in (start, finished):
        require(r["old_worker_pending"] == (terminal["seq"] > r["seq"]), "Old pending-Future snapshot mismatch")
    return dict(start=start, selected=selection, finished=finished, disposition=disposition,
                states=states, extra=extra, listings=listings, waits=waits)


def score_cancellation(e):
    data = e["cancellation"]
    if data is None: return {"requested": False, "source_target_roles": [], "extra_target_roles": []}
    start, sel = data["start"], data["selected"]
    known = start["known_targets"]
    checkpoint = (data["states"][("before","O")]["state"]["status"] in {"interrupted","success","error"}
                  and data["states"][("before","S")]["state"]["status"] in {"pending","running"}
                  and start["old_worker_pending"])
    statuses = {p: {role: data["states"][(p,role)]["state"]["status"] for role in ("O","S")} for p in ("before","after")}
    summary_term = next(r["state"]["status"] for r in e["rows"] if r["kind"] == "graph_terminal" and r["role"] == "S")
    target = e["target"]
    observed_effect = bool(target["result"] and (target["success"] or target["result"]["after_sha256"] != target["attempt"]["before_sha256"]))
    summary_key = e["by_role"]["S"]["key"]
    held = any(r["kind"] == "scripted_model_waiting" and r["key"] == summary_key and r["seq"] < start["seq"] for r in e["rows"])
    return {
        "requested": bool(data["extra"]), "mode": start["mode"], "checkpoint_observed": checkpoint and held,
        "summary_hold_observed": held,
        "source_target_roles": [known[x] for x in start["saved"]["run_ids"]],
        "extra_target_roles": [known[x] for x in sel["run_ids"]],
        "same_saved_target_and_action": (sel["run_ids"] == start["saved"]["run_ids"] and sel["action"] == start["saved"]["action"]) if data["extra"] else None,
        "target_set_changed": sel["run_ids"] != start["saved"]["run_ids"] if data["extra"] else None,
        "extra_http_status": e["responses"][data["extra"][0]["request_id"]]["status"] if data["extra"] else None,
        "extra_disposition": data["disposition"]["disposition"],
        "state_before_after": statuses, "old_native_pending_after_probe": data["finished"]["old_worker_pending"],
        "old_target_effect_after_probe": observed_effect and target["attempt"]["seq"] > data["finished"]["seq"],
        "summary_terminal_status": summary_term,
        "summary_delivery_count": len(e["deliveries"]),
        "summary_text_sha256": [d["text_sha256"] for d in e["deliveries"]],
        "summary_wait": data["waits"][0]["status"] if data["waits"] else None,
        "interpretation_scope": "Saved-target wire comparison and measured outcome projection, not universal cancellation equivalence",
    }
