"""Recompute native evidence and wire attribution; never infer effects from arm names."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.append(str(HERE.parent/"f07_live_bridge_v01"))
from audit import audit as file_audit, selected, one, journal
from comparison_config import PROPOSAL, protocol_digest, REQUEST_LIMITS, require
from transport import canonical, parse_events, usage_of
import bridge_codec

def read(p): return json.loads(Path(p).read_text())
def sha(raw): return hashlib.sha256(raw).hexdigest()
def transport_check(out,events):
    plan,result,usage,process=(read(out/n) for n in ("PLAN.json","result.json","USAGE.json","PROCESS.json"))
    live=plan["live"]
    require(process["exit_code"]==0 and not process["timed_out"] and result["completed"],"Unclosed execution")
    require(plan["protocol"]==PROPOSAL and plan["protocol_sha256"]==protocol_digest(),"Protocol drift")
    require(usage["authorization"]==plan["authorization"] and usage["usage_is_synthetic"]==(not live),"Mode/grant mismatch")
    require(usage["status"]==one(events,"provider_client_closed")["status"]=="closed_clean","Transport unclosed")
    require(result["live_model"]==live and result["arm"]==plan["arm"] and result["seed"]==17,"Condition mismatch")
    cfg=one(events,"bridge_configured")
    require(cfg["credential_access"]==cfg["live_execution_enabled"]==live,"Bridge mode mismatch")
    exchanges=selected(events,"bridge_wire_exchange")
    require(len(exchanges)==len(usage["attempts"])==usage["requests_attempted"],"Request count differs")
    requests={e["request"]["request_id"]:e for e in selected(events,"bridge_model_request")}
    replies={e["request_id"]:e for e in selected(events,"bridge_model_response")}
    require(len(requests)==len(exchanges)==len(replies),"Missing/duplicate model record")
    sessions={};seen=set();roles={}
    grants={e["invocation_id"]:e for e in selected(events,"authority_declared")}
    old_model,old_effort=bridge_codec.MODEL,bridge_codec.EFFORT
    bridge_codec.MODEL=plan["live_config"]["model"] if live else "gpt-6-astra"
    bridge_codec.EFFORT=plan["live_config"]["reasoning_effort"] if live else "high"
    try:
        for exchange,attempt in zip(exchanges,usage["attempts"]):
            req=exchange["request"];b=req["binding"]; inv=b["invocation_id"]; role=b["role"]
            require(all(b.get(k)==v for k,v in grants[inv].items() if k not in
                        {"seq","pid","actor","instance","monotonic_ns","kind"}),"Authority binding mismatch")
            session=sessions.setdefault(inv,bridge_codec.Session(b,request_limit=REQUEST_LIMITS[role]))
            require(session.prepare(req)==exchange["wire"],"Wire reconstruction differs")
            projection=session.accept(exchange["events"],req["request_id"])
            require(projection==exchange["projection"] and projection["provider_response_id"] not in seen,"Projection identity differs")
            seen.add(projection["provider_response_id"])
            require(requests[req["request_id"]]["request"]==req and
                    requests[req["request_id"]]["seq"]<exchange["seq"]<replies[req["request_id"]]["seq"],"Model sequence")
            require(replies[req["request_id"]]["message"]==projection["message"],"Native message differs")
            require(exchange["actual_provider_calls"]==int(live) and exchange["usage_is_synthetic"]==(not live),"Exchange mode differs")
            folder=out/f"request-{attempt['index']:02d}"
            require(read(folder/"bridge_request.json")==req and read(folder/"wire_request.json")==exchange["wire"],"Raw request mismatch")
            payload=deepcopy(exchange["wire"])
            if live: payload["max_output_tokens"]=plan["live_config"]["max_output_tokens"]
            require(read(folder/"api_request.json")==payload and sha(canonical(payload))==attempt["request_sha256"],"Dispatched payload mismatch")
            require(attempt["request_id"]==req["request_id"] and attempt["binding"]==b,"Attempt owner differs")
            raw=(folder/"response.sse").read_bytes()
            observation=read(folder/"observation.json")
            require(sha(raw)==observation["body_sha256"] and parse_events(raw.decode())==exchange["events"]==
                    read(folder/"events.json"),"Stream bytes differ")
            terminals=[e["response"] for e in exchange["events"] if e.get("type")=="response.completed"]
            require(len(terminals)==1,"Response incomplete")
            require(usage_of(terminals[0])==observation["usage"]==attempt["usage"],"Usage differs")
            require(attempt["status"]=="terminal_observed" and attempt["provider_status"]=="completed","Attempt incomplete")
            require(observation["actual_provider_calls"]==int(live),"Observation mode differs")
            roles[role]=roles.get(role,0)+1
    finally:
        bridge_codec.MODEL,bridge_codec.EFFORT=old_model,old_effort
    require(roles==usage["per_role_requests"] and all(v<=REQUEST_LIMITS[k] for k,v in roles.items()),"Role usage bound")
    require(usage["unknown_usage_attempts"]==0,"Unknown usage retained")
    require(usage["actual_provider_calls"]==result["actual_provider_calls"]==(len(exchanges) if live else 0),"Provider count differs")
    if live:
        config=plan["live_config"]
        require(len(exchanges)<=config["max_requests"] and usage["requested_configuration"]==config,"Live request limit")
        for a in usage["attempts"]:
            require(a["usage"]["output_tokens"]<=config["max_output_tokens"],"Live output bound")
    return dict(status="recorded",actual_provider_calls=usage["actual_provider_calls"],requests=len(exchanges),
                usage_is_synthetic=not live,per_role_requests=roles,usage=[a["usage"] for a in usage["attempts"]])
def audit(out,replacement=None):
    out=Path(out)
    report=file_audit(out,replacement)
    report.update(transport_status="needs_review",transport_errors=[],actual_provider_calls=None,new_live_episodes=None)
    report["raw_usage"]=read(out/"USAGE.json") if (out/"USAGE.json").exists() else None
    report["retained_dispatches"]=len(list(out.glob("request-*/DISPATCH.json")))
    try:
        events=replacement["source"] if replacement else journal(out/"source.jsonl")
        tr=transport_check(out,events)
        report.update(transport_status="recorded",transport=tr,actual_provider_calls=tr["actual_provider_calls"],
                      new_live_episodes=int(tr["actual_provider_calls"]>0))
    except Exception as exc:
        report["transport_errors"].append(type(exc).__name__+": "+str(exc))
    return report
