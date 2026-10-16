"""Receipt/disk validity, transport validity and task outcomes remain separate."""
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / "f07_live_bridge_v01"))
from bridge_codec import Session
from smoke_astra import usage_quote, canonical, parse_events
from audit import audit as file_audit, selected, one
from comparison_config import (PROPOSAL, protocol_digest, REQUEST_LIMITS, max_requests,
                               require, CARRY, expected_prior_usage)


def read(path): return json.loads(Path(path).read_text())
def sha(value): return hashlib.sha256(value).hexdigest()


def close_file_scores(outcome, disk):
    """A historical correct write is not necessarily correct at final inventory."""
    if outcome is None: return
    for scores in outcome["roles"].values():
        current = [r for r in scores["final_reports"]
                   if r["path"] in disk and disk[r["path"]]["sha256"] == r["sha256"]]
        # Deduplicate repeated writes of identical bytes to the same path.
        current = list({(r["path"], r["sha256"]):r for r in current}.values())
        scores["final_reports_at_close"] = deepcopy(current)
        scores["final_present_at_close"] = bool(current)
        scores["final_correct_at_close"] = any(r["correct"] for r in current)


def transport_check(out, events):
    plan, result, usage, process = (read(out / n) for n in
        ("PLAN.json", "result.json", "USAGE.json", "PROCESS.json"))
    live = plan["live"]
    require(process["exit_code"] == 0 and not process["timed_out"] and result["completed"], "Unclosed observation")
    require(plan["protocol"] == PROPOSAL and plan["protocol_sha256"] == protocol_digest(), "Protocol drift")
    require(result["live_model"] == live and result["arm"] == plan["arm"] and result["seed"] == 17, "Condition mismatch")
    cfg = one(events, "bridge_configured")
    require(cfg["live_execution_enabled"] == cfg["credential_access"] == live, "Live-mode mismatch")
    require(usage["authorization"] == plan["authorization"] and usage["usage_is_synthetic"] == (not live), "Usage/grant mismatch")
    require(usage["status"] == one(events, "oauth_client_closed")["status"] == "closed_clean", "Usage unclosed")
    grants = {g["invocation_id"]: {k:v for k,v in g.items() if k not in
        {"seq", "pid", "actor", "instance", "monotonic_ns", "kind"}} for g in selected(events, "authority_declared")}
    require(len(grants) == len(selected(events, "authority_declared")), "Duplicate authority")
    identities = {}
    for r in selected(events, "factory_identity_registered"):
        require(r["key"] not in identities or all(r.get(k) == identities[r["key"]].get(k)
                for k in ("invocation_id", "thread_id", "origin_key")), "Factory identity changed")
        identities[r["key"]] = r
    requests = {r["request"]["request_id"]:r for r in selected(events, "bridge_model_request")}
    replies = {r["request_id"]:r for r in selected(events, "bridge_model_response")}
    exchanges = selected(events, "bridge_wire_exchange")
    require(len(requests) == len(selected(events, "bridge_model_request")) and
            len(replies) == len(selected(events, "bridge_model_response")) and
            set(requests) == set(replies) == {r["request"]["request_id"] for r in exchanges}, "Model record gap")
    sessions, seen, roles, total = {}, set(), {}, Decimal(0)
    require(len(exchanges) == len(usage["attempts"]) == usage["requests_attempted"], "Attempt count mismatch")
    for row, attempt in zip(exchanges, usage["attempts"]):
        req = row["request"]; b = req["binding"]; inv = b["invocation_id"]
        require(all(b.get(k) == v for k,v in grants[inv].items()), "Model/grant mismatch")
        identity = identities[b["identity_key"]]
        require(identity["invocation_id"] == inv and identity["origin_key"] == b["origin_key"], "Model origin mismatch")
        session = sessions.setdefault(inv, Session(b, request_limit=REQUEST_LIMITS[b["role"]]))
        require(session.prepare(req) == row["wire"], "Wire reconstruction mismatch")
        projected = session.accept(row["events"], req["request_id"])
        require(projected == row["projection"] and projected["provider_response_id"] not in seen, "Response identity/projection")
        seen.add(projected["provider_response_id"])
        require(requests[req["request_id"]]["request"] == req and requests[req["request_id"]]["seq"] < row["seq"] < replies[req["request_id"]]["seq"], "Model sequence")
        require(replies[req["request_id"]]["message"] == projected["message"], "Model message changed")
        require(row["actual_provider_calls"] == int(live) and row["usage_is_synthetic"] == (not live), "Provider mode changed")
        role = b["role"]; roles[role] = roles.get(role, 0) + 1
        folder = out / ("request-%02d" % attempt["index"])
        require(attempt["request_id"] == req["request_id"] and attempt["binding"] == b, "Ledger identity")
        require(read(folder / "bridge_request.json") == req and read(folder / "wire_request.json") == row["wire"] and
                read(folder / "events.json") == row["events"], "Raw record mismatch")
        raw = (folder / "response.sse").read_bytes(); observation = read(folder / "observation.json")
        require(sha(raw) == observation["body_sha256"] and list(parse_events(raw.decode().splitlines())) == row["events"], "SSE mismatch")
        require(sha(canonical(row["wire"])) == attempt["request_sha256"], "Wire hash mismatch")
        terminal = [e["response"] for e in row["events"] if e.get("type") == "response.completed"]
        require(len(terminal) == 1, "Incomplete response")
        quote = usage_quote(terminal[0])
        require(quote == observation["usage"] and Decimal(quote["standard_credit_equivalent"]) == Decimal(attempt["credit_equivalent"]), "Usage mismatch")
        total += Decimal(attempt["credit_equivalent"])
    require(roles == usage["per_role_requests"] and all(n <= REQUEST_LIMITS[r] for r,n in roles.items()) and
            len(exchanges) <= max_requests(plan["arm"]), "Role/request limit")
    require(plan["arm"] != "healthy" or "S" not in roles, "Healthy summary not authorized")
    require(total == Decimal(usage["observed_credit_equivalent"]) and usage["unknown_reserve_retained"] == "0", "Missing usage retained")
    require(usage["actual_provider_calls"] == result["actual_provider_calls"] == (len(exchanges) if live else 0), "Provider count mismatch")
    if live:
        require(usage["carryover"] == CARRY and Decimal(usage["prior_group_credit_equivalent"]) ==
                expected_prior_usage(plan["authorization"]["cell_id"]), "Prior accounting changed")
    else:
        require(usage["carryover"] is None and usage["prior_group_credit_equivalent"] == "0", "Mock accounting mixed")
    require(Decimal(usage["prior_unknown_reserve_retained"]) == 0 and total + Decimal(usage["prior_group_credit_equivalent"]) <= Decimal(PROPOSAL["reserve_credits"]), "Reserve exceeded")
    return dict(status="recorded", actual_provider_calls=usage["actual_provider_calls"],
                requests=len(exchanges), observed_credit_equivalent=str(total),
                usage_is_synthetic=not live, per_role_requests=roles)


def audit(out, replacement=None):
    out = Path(out).resolve()
    report = file_audit(out, replacement)
    close_file_scores(report["outcomes"], report["raw_disk_files"])
    report.update(transport_status="needs_review", transport_errors=[], actual_provider_calls=None,
                  checkpoint_content_correct=False, summary_candidates=[])
    # Raw usage is visible even when native evidence or stream reconstruction fails.
    usage = read(out / "USAGE.json") if (out / "USAGE.json").exists() else None
    report["raw_usage"] = ({k:usage.get(k) for k in ("actual_provider_calls", "observed_credit_equivalent",
        "unknown_reserve_retained", "usage_is_synthetic", "status")} if usage else None)
    try:
        events = replacement["source"] if replacement else [json.loads(x) for x in (out / "source.jsonl").read_text().splitlines()]
        tr = transport_check(out, events)
        report.update(transport_status="recorded", transport=tr, actual_provider_calls=tr["actual_provider_calls"],
                      new_live_episodes=int(tr["actual_provider_calls"] > 0))
    except (AssertionError, ValueError, KeyError, TypeError, FileNotFoundError) as exc:
        report["transport_errors"].append(type(exc).__name__ + ": " + str(exc))
        return report
    # All content coding below is observational, never evidence validity.
    plan = read(out / "PLAN.json")
    cps = selected(events, "intervention_checkpoint")
    if cps:
        snapshots = {r["op"]["operation_id"]:r["projection"] for r in selected(events, "mutation_request_snapshot")}
        scores = {}
        for role, job, stage in (("O", "old", "final"), ("I", "independent", "partial")):
            oid = cps[0]["targets"][role]["operation_id"]
            try: candidate = json.loads(snapshots[oid].get("candidate_content"))
            except (ValueError, TypeError): candidate = None
            scores[role] = candidate == plan["expected_" + stage][role]
        report["checkpoint_content_correct"] = all(scores.values())
        report["checkpoint_content_scores"] = scores
    for r in selected(events, "bridge_model_response"):
        if r["binding"]["role"] != "S": continue
        message = r["message"]
        texts = [("assistant", message.get("content"))]
        texts += [("slack_thread_reply", c["args"].get("message")) for c in message.get("tool_calls", [])
                  if c["name"] == "slack_thread_reply"]
        for channel, text in texts:
            if isinstance(text, str) and text:
                report["summary_candidates"].append(dict(channel=channel, text=text, sha256=sha(text.encode()),
                    request_id=r["request_id"], author_review="pending", live=not tr["usage_is_synthetic"]))
    return report
