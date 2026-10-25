"""Read-only reconciliation of factory, IPC, SQLite, native effects and disk.

No execution/control/provider imports. Outcomes may fail without invalidating
well-recorded evidence. Replay and recovery validity are independent of arm names.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3


def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value,str) else value).hexdigest()


def load(path): return json.loads(Path(path).read_text())
def selected(rows,kind): return [e for e in rows if e["kind"]==kind]


def one(rows,kind):
    values=selected(rows,kind)
    assert len(values)==1,"Expected one "+kind
    return values[0]


def journal(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def database(path):
    conn=sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro",uri=True)
    try:
        assert conn.execute("PRAGMA integrity_check").fetchall()==[("ok",)],"SQLite integrity"
        tables={}
        for table in ("meta","grants","jobs","controls"):
            cur=conn.execute("SELECT * FROM "+table+" ORDER BY 1")
            names=[d[0] for d in cur.description]
            tables[table]=[dict(zip(names,row)) for row in cur]
        return tables
    finally: conn.close()


def files(root):
    result={}
    for p in sorted(Path(root).rglob("*")):
        assert not p.is_symlink(),"Output symlink"
        if p.is_file():
            data=p.read_bytes()
            result[str(p.relative_to(root))]=dict(content=data.decode(),sha256=sha(data),bytes=len(data))
    return result


def keyed(events,kind,idfn,valuefn):
    values=selected(events,kind)
    mapping={idfn(e):valuefn(e) for e in values}
    assert len(mapping)==len(values),"Duplicate "+kind
    return mapping


def candidate(op,before):
    """Reconstruct a proposal from recorded request-time bytes, without backend imports."""
    if op["tool"]=="write_file": return op["args"]["content"]
    if before is None: return None
    normalize=lambda text:text.replace("\r\n","\n").replace("\r","\n")
    text,old,new=(normalize(x) for x in (before,op["args"]["old_string"],op["args"]["new_string"]))
    count=text.count(old)
    if count==0 or (count>1 and not op["args"].get("replace_all",False)): return None
    return text.replace(old,new)


def inspect(plan,process,result,logs,before,final,actual):
    s,u,v=logs["source"],logs["supervisor"],logs["observer"]
    rs=[logs[n] for n in ("receiver-1","receiver-2") if n in logs]
    r=[e for epoch in rs for e in epoch]
    for name,events in logs.items():
        assert events and [e["seq"] for e in events]==list(range(1,len(events)+1)),"Journal sequence "+name
        assert len({(e["actor"],e["pid"],e["instance"]) for e in events})==1,"Journal identity "+name
        assert events[0]["actor"]==("receiver" if name.startswith("receiver-") else name),"Journal actor"
    assert len({es[0]["pid"] for es in logs.values()})==len(logs),"Processes not distinct"
    assert not process["episode_error"] and not process["cleanup_actions"] and process["completed"],"Unclean supervisor"
    assert process["supervisor_pid"]==u[0]["pid"],"Supervisor PID binding"
    for name in ("source","observer",*[f"receiver-{n+1}" for n in range(len(rs))]):
        state=process[name]
        assert state["pid"]==logs[name][0]["pid"] and state["exit_code"]==0 and state["reaped"],"Child closure "+name
    assert one(s,"source_closed")["completed"] and one(s,"http_client_closed")["closed"],"Source closure"
    assert one(u,"supervisor_closed")["completed"],"Supervisor closure"
    one(s,"native_runtime_closed"); one(s,"measurement_closed"); one(v,"observer_closed")
    assert not selected(s,"execution_error") and not selected(s,"source_process_error"),"Source execution error"
    for es in rs: one(es,"receiver_closed")
    live=plan["live"]
    assert result["completed"] and result["live_model"]==live,"Source result"
    assert live or (result["actual_provider_calls"]==0 and result["new_live_episodes"]==0),"Offline source result"

    # Exact source -> supervisor -> receiver and return linkage.
    source_sent=keyed(s,"rpc_sent",lambda e:e["request"]["rpc_id"],lambda e:e["request"])
    source_back=keyed(s,"rpc_returned",lambda e:e["rpc_id"],lambda e:e["reply"])
    sup_in=keyed(u,"source_rpc_received",lambda e:e["request"]["rpc_id"],lambda e:e["request"])
    sup_back=keyed(u,"source_rpc_replied",lambda e:e["rpc_id"],lambda e:e["reply"])
    assert source_sent==sup_in and source_back==sup_back and set(source_sent)==set(source_back),"Source supervisor chain"
    sup_sent=keyed(u,"rpc_sent",lambda e:e["request"]["rpc_id"],lambda e:e["request"])
    sup_return=keyed(u,"rpc_returned",lambda e:e["rpc_id"],lambda e:e["reply"])
    recv_in=keyed(r,"rpc_received",lambda e:e["request"]["rpc_id"],lambda e:e["request"])
    recv_back=keyed(r,"rpc_replied",lambda e:e["rpc_id"],lambda e:e["reply"])
    assert sup_sent==recv_in and sup_return==recv_back and set(sup_sent)==set(sup_return),"Receiver IPC chain"
    for rid,q in source_sent.items():
        assert source_back[rid]["ok"],"Source RPC error"
        if q["action"] not in {"snapshot","restart","source_done"}:
            assert q==sup_sent[rid] and source_back[rid]==sup_return[rid],"Forwarding mutation"
    for es in rs:
        for response in selected(es,"rpc_replied"):
            reply=response["reply"]
            assert reply["ok"] and reply["receiver_pid"]==es[0]["pid"] and reply["receiver_instance"]==es[0]["instance"],"Receiver response identity"
            req=[e for e in selected(es,"rpc_received") if e["request"]["rpc_id"]==response["rpc_id"]]
            assert len(req)==1 and req[0]["seq"]<response["seq"],"Receiver response order"
            q=req[0]["request"]
            if q["action"] in {"submit","control"}:
                event=[e for e in es if e["seq"]==reply["receiver_seq"]]
                assert len(event)==1,"Receipt sequence"
                event=event[0]
                if q["action"]=="submit":
                    assert event["kind"] in {"job_persisted","duplicate_delivery"} and event["operation_id"]==q["op"]["operation_id"],"Acceptance receipt"
                else:
                    assert event["kind"]=="control_acknowledged" and all(
                        event[k]==q[j] for k,j in (("control_kind","kind"),("target","target"),("durable","durable"))),"Control receipt"

    restarted=len(rs)==2
    readies=selected(u,"receiver_ready"); reaps=selected(u,"receiver_reaped")
    assert len(readies)==len(reaps)==len(rs),"Receiver lifetime inventory"
    for i,es in enumerate(rs):
        assert readies[i]["epoch"]==reaps[i]["epoch"]==i+1,"Receiver epoch"
        ready=readies[i]["receipt"]
        assert (ready["pid"],ready["instance"])==(es[0]["pid"],es[0]["instance"]),"Ready identity"
        assert readies[i]["seq"]<reaps[i]["seq"] and reaps[i]["exit_code"]==0,"Lifetime closure order"
    snaps=selected(v,"snapshot")
    labels=["initial","checkpoint"]+(["before_restart","after_restart_before_execution"] if restarted else [])+["final"]
    assert [e["label"] for e in snaps]==labels,"Observation phases"
    for snap in snaps:
        sent=[e for e in selected(u,"observer_requested") if e["request_id"]==snap["request_id"]]
        back=[e for e in selected(u,"observer_returned") if e["observation"]["request_id"]==snap["request_id"]]
        assert len(sent)==len(back)==1 and back[0]["observation"]==snap and sent[0]["label"]==snap["label"],"Observer correlation"
        for f in snap["files"]:
            assert sha(f["content"])==f["sha256"] and len(f["content"].encode())==f["bytes"],"Observer bytes"
    observed={f["path"]:{k:f[k] for k in ("content","sha256","bytes")} for f in snaps[-1]["files"]}
    assert observed==actual,"Disk differs from observer"

    authorities={g["invocation_id"]:{k:v for k,v in g.items() if k not in
        {"seq","pid","instance","actor","monotonic_ns","kind"}} for g in selected(s,"authority_declared")}
    factory={}
    for g in selected(s,"authority_factory_bound"):
        inv=g["identity"]["invocation_id"]
        value=dict(grant=g["grant"],identity=g["identity"])
        assert factory.setdefault(inv,value)==value,"Factory identity rebound"
    bindings={}
    for g in selected(r,"grant_registered"):
        inv=g["identity"]["invocation_id"]
        value={k:g[k] for k in ("grant","identity","root_relative")}
        assert bindings.setdefault(inv,value)==value,"Receiver grant rebound"
        assert g["grant"]==authorities[inv] and factory[inv]==dict(grant=g["grant"],identity=g["identity"]),"Factory receiver authority"
    db_grants={x["invocation"]:json.loads(x["body"]) for x in final["grants"]}
    assert db_grants==bindings,"Durable grant inventory"

    proposals=keyed(s,"effect_requested",lambda e:e["op"]["operation_id"],lambda e:e["op"])
    accepted=keyed(r,"job_persisted",lambda e:e["operation_id"],lambda e:e)
    bound=keyed(s,"receiver_acceptance_bound",lambda e:e["op"]["operation_id"],lambda e:e)
    assert set(accepted)==set(proposals)==set(bound),"Proposal acceptance inventory"
    selections=selected(s,"model_tool_selected")
    checkpoints={}
    for cp in selected(s,"graph_checkpoint"):
        for message in cp["state"].get("values",{}).get("messages",[]):
            for call in message.get("tool_calls",[]):
                assert checkpoints.setdefault(call["id"],call)==call,"Checkpoint call rebound"
    effects=selected(r,"native_effect_result"); attempts=selected(r,"native_effect_attempt")
    assert len(effects)==len({e["operation_id"] for e in effects}),"Repeated native receipt"
    assert {e["operation_id"] for e in effects}=={e["operation_id"] for e in attempts},"Missing native receipt"
    db_final={x["operation"]:x for x in final["jobs"]}
    assert set(db_final)==set(accepted),"Durable job inventory"
    for oid,item in accepted.items():
        op=item["op"]; raw=deepcopy(op); raw.pop("checkpoint_candidate")
        assert raw==proposals[oid] and bound[oid]["op"]==op,"Accepted payload differs from tool"
        grant=bindings[op["invocation_id"]]
        assert all(op.get(k)==v for k,v in grant["identity"].items()),"Operation authority"
        assert op["origin_invocation_id"]==(grant["grant"]["parent_invocation_id"] or op["invocation_id"]),"Origin authority"
        chosen=[e for e in selections if e.get("key")==op["key"] and e.get("call_id")==op["call_id"]]
        assert len(chosen)==1 and chosen[0]["tool"]==op["tool"] and chosen[0]["args"]==op["args"],"Selected tool mismatch"
        cp=checkpoints[op["call_id"]]
        assert cp["name"]==op["tool"] and cp["args"]==op["args"],"Checkpoint selection mismatch"
        dispatch=[e for e in selected(s,"backend_dispatch_started") if e["op"]["operation_id"]==oid]
        workers=[e for e in selected(s,"backend_sync_entered") if e["op"]["operation_id"]==oid]
        snapshots=[e for e in selected(s,"mutation_request_snapshot") if e["op"]["operation_id"]==oid]
        assert len(dispatch)==len(workers)==len(snapshots)==1,"Native dispatch chain"
        assert dispatch[0]["op"]==workers[0]["op"]==snapshots[0]["op"]==raw,"Native dispatch identity"
        assert workers[0]["executor_worker_stack_observed"] is True,"Native executor boundary not observed"
        snap=snapshots[0]
        proposed=candidate(raw,snap["before_content"])
        assert snap["projection"]["candidate_content"]==proposed,"Proposed edit/write content mismatch"
        assert snap["projection"]["candidate_sha256"]==(sha(proposed) if proposed is not None else None),"Proposed content hash"
        assert snap["before_sha256"]==(sha(snap["before_content"]) if snap["before_content"] is not None else None),"Proposal byte basis hash"
        receipt=bound[oid]["receipt"]
        assert receipt["receiver_seq"]==item["seq"] and receipt["receiver_instance"]==item["instance"] and receipt["body_sha256"]==item["body_sha256"],"Source acceptance binding"
        assert json.loads(db_final[oid]["body"])==op,"Durable operation body"
        terminal=[e for e in selected(r,"job_terminal") if e["operation_id"]==oid]
        decisions=[e for e in selected(r,"effect_decision") if e["operation_id"]==oid]
        callers=[e for e in selected(s,"bridge_caller_finished") if e["op"]["operation_id"]==oid]
        assert len(terminal)==len(decisions)==len(callers)==1,"Operation lifecycle"
        t,d=terminal[0],decisions[0]
        assert t["instance"]==d["instance"] and d["seq"]<t["seq"],"Decision terminal order"
        assert db_final[oid]["state"]==t["state"] and json.loads(db_final[oid]["result"])==t["result"],"Durable terminal result"
        outcome=[e for e in effects if e["operation_id"]==oid]
        denied=[e for e in selected(r,"effect_denied")+selected(r,"output_boundary_denied") if e["operation_id"]==oid]
        assert len(outcome)+len(denied)==1,"Terminal disposition"
        assert not outcome or d["allowed"],"Denied decision with native receipt"
        payload=op["args"]["content"] if op["tool"]=="write_file" else op["args"]["new_string"]
        assert sha(payload)==op["content_sha256"] and op["args"]["file_path"]==op["virtual_path"],"Tool payload hash"
    # Reconstruct file state; initial source files are explicit fixture inputs.
    inventory={f["path"]:f["content"] for f in snaps[0]["files"]}
    for event in r:
        if event["kind"]=="native_effect_attempt":
            assert inventory.get(event["path"])==event["before_content"],"Native before bytes"
            assert event["before_sha256"]==(sha(event["before_content"]) if event["before_content"] is not None else None),"Before hash"
        if event["kind"]=="native_effect_result":
            assert event["after_sha256"]==(sha(event["after_content"]) if event["after_content"] is not None else None),"After hash"
            op=accepted[event["operation_id"]]["op"]
            assert event["path"]==bindings[op["invocation_id"]]["root_relative"]+op["virtual_path"],"Effect path attribution"
            if event["after_content"] is None: inventory.pop(event["path"],None)
            else: inventory[event["path"]]=event["after_content"]
    assert inventory=={k:v["content"] for k,v in actual.items()},"Unaccounted file effect"

    cp=selected(s,"intervention_checkpoint"); early=selected(s,"checkpoint_not_reached")
    assert len(cp)+len(early)==1 and bool(cp)==restarted,"Restart/checkpoint relation"
    checkpoint_matched=False; restoration=None
    if restarted:
        assert reaps[0]["seq"]<readies[1]["seq"],"New receiver started before predecessor reaped"
        before_jobs={x["operation"]:x for x in before["jobs"]}
        recovered=keyed(rs[1],"job_recovered",lambda e:e["operation_id"],lambda e:e)
        assert set(recovered)==set(before_jobs),"Recovery inventory"
        for oid,row in before_jobs.items():
            assert recovered[oid]["op"]==json.loads(row["body"])==accepted[oid]["op"],"Recovered job identity or bytes"
            assert recovered[oid]["state"]==row["state"],"Recovered state drift"
        assert before["controls"]==final["controls"],"Persisted control changed"
        assert all(db_grants[g["invocation"]]==json.loads(g["body"]) for g in before["grants"]),"Recovered grant changed"
        ids=[x["value"] for data in (before,final) for x in data["meta"] if x["key"]=="database_id"]
        ids += [e["receipt"]["database_id"] for e in readies]
        assert len(ids)==4 and len(set(ids))==1,"Database identity"
        controls={(x["kind"],x["target"]) for x in before["controls"]}
        for e in selected(rs[0],"control_acknowledged"):
            if e["durable"]: assert (e["control_kind"],e["target"]) in controls,"Control acknowledged but not persisted"
        restored=one(rs[1],"receiver_recovered")
        restoration=(set(restored["revoked"])=={t for k,t in controls if k=="revoke"} and
            set(restored["cancelled"])=={t for k,t in controls if k=="cancel"} and
            restored["deny_all"]==any(k=="deny_all" for k,t in controls))
        targets=cp[0]["targets"]
        assert set(targets)=={"O","I"},"Checkpoint target roles"
        snapshots={e["op"]["operation_id"]:e["projection"] for e in selected(s,"mutation_request_snapshot")}
        stages=[]
        for role in ("O","I"):
            op=targets[role]; oid=op["operation_id"]
            assert op==accepted[oid]["op"] and bindings[op["invocation_id"]]["grant"]["role"]==role,"Checkpoint identity"
            try: stage=json.loads(snapshots[oid]["candidate_content"]).get("stage")
            except (ValueError,TypeError,AttributeError,KeyError): stage=None
            stages.append(stage)
        before_status=one(u,"before_restart_status")["receipt"]
        after_status=one(u,"after_restart_status")["receipt"]
        restart=one(s,"receiver_restart_bound")["receipt"]
        assert restart["before"]==before_status and restart["after"]==after_status,"Source restart receipt"
        assert all(after_status.get(k)==restored.get(k) for k in ("revoked","cancelled","deny_all")),"Recovery status mismatch"
        assert set(after_status["jobs"])==set(before_jobs),"Recovered status inventory"
        checkpoint_matched=stages==["final","partial"] and all(
            state["jobs"][op["operation_id"]]["state"]=="queued" and not state["jobs"][op["operation_id"]]["done"]
            for state in (cp[0]["receiver"],before_status,after_status) for op in targets.values())
        duplicate=one(s,"duplicate_probe")
        old=targets["O"]["operation_id"]
        assert duplicate["op"]==targets["O"] and duplicate["receipt"]["status"]=="existing","Duplicate operation binding"
        dup=[e for e in selected(rs[1],"duplicate_delivery") if e["operation_id"]==old]
        assert len(dup)==1,"Duplicate delivery observation"
    stop=selected(s,"source_stop_requested")
    if stop:
        assert restarted,"Stop without matched restart"
        returned=one(s,"source_stop_handler_returned"); pending=one(s,"source_stop_pending_receiver")
        terminal=[e for e in selected(s,"graph_terminal") if e["role"]=="O"]
        assert len(terminal)==1 and terminal[0]["state"]["status"] in {"interrupted","error"},"Source run not interrupted"
        assert stop[0]["seq"]<returned["seq"]<pending["seq"]<one(s,"receiver_restart_bound")["seq"],"Source stop/restart order"
        assert not pending["state"]["done"] and pending["state"]["state"]=="queued","Accepted job not pending"
        assert any(e["op"]["operation_id"]==pending["operation_id"] for e in selected(s,"effect_awaiter_cancelled")),"Awaiter cancellation missing"
    exchanges=selected(s,"bridge_wire_exchange")
    assert len(exchanges)==result["wire_requests"] and all(e["actual_provider_calls"]==int(live) and e["usage_is_synthetic"]==(not live) for e in exchanges),"Wire mode inventory"
    responses=keyed(s,"bridge_model_response",lambda e:e["request_id"],lambda e:e["message"])
    assert len(responses)==len(exchanges),"Wire response count"
    for e in exchanges:
        assert responses[e["request"]["request_id"]]==e["projection"]["message"],"Wire projection mismatch"
    for e in selected(s,"source_role_surface"):
        assert set(e["names"]) in ({"read_file","write_file","edit_file"},{"read_file","slack_thread_reply"}),"Tool surface drift"
    assert not selected(s,"direct_native_call"),"Inline native callback bypassed receiver"

    scores={}
    for role,job_id in {"O":"old","I":"independent","N":"human","C":"new_background"}.items():
        role_ops={oid for oid,e in accepted.items() if bindings[e["op"]["invocation_id"]]["grant"]["role"]==role}
        relevant=[e for e in effects if e["operation_id"] in role_ops and e["success"]]
        reports=[]
        for e in relevant:
            try: body=json.loads(e["after_content"])
            except (TypeError,ValueError): continue
            if isinstance(body,dict) and body.get("stage")=="final":
                reports.append(dict(path=e["path"],sha256=e["after_sha256"],correct=body==plan["expected_final"][role]))
        final_paths={e["path"] for e in relevant}
        current=[]
        for path in final_paths:
            if path not in actual: continue
            try: correct=json.loads(actual[path]["content"])==plan["expected_final"][role]
            except ValueError: correct=False
            if correct: current.append(dict(path=path,sha256=actual[path]["sha256"]))
        scores[role]=dict(mutation_attempts=len(role_ops),successful_mutations=len(relevant),
            second_lifetime_mutations=sum(e["instance"]==rs[1][0]["instance"] for e in relevant) if restarted else None,
            final_reports=reports,final_correct_at_close=bool(current),correct_files_at_close=current)
    return dict(observation_status="checkpoint_reached" if checkpoint_matched else "checkpoint_not_reached",
        planned_checkpoint_observed=checkpoint_matched,restart_observed=restarted,
        source_stopped_with_receiver_pending=bool(stop),persisted_control_restoration_matches=restoration,
        O_duplicate_deliveries=len(selected(rs[1],"duplicate_delivery")) if restarted else None,
        O_execution_starts=sum(e["operation_id"]==cp[0]["targets"]["O"]["operation_id"] for e in selected(rs[1],"execution_started")) if restarted else None,
        roles=scores,wire_exchanges=len(exchanges),synthetic_wire_exchanges=0 if live else len(exchanges),
        live_wire_exchanges=len(exchanges) if live else 0,native_effect_receipts=len(effects))


def audit(out,replacement=None):
    out=Path(out); actual={}
    result=dict(evidence_status="needs_review",errors=[],outcomes=None,raw_disk_files=actual,
                actual_provider_calls=None,new_live_episodes=None,independent_human_validation=False)
    try:
        actual=files(out/"files"); result["raw_disk_files"]=actual
        logs=replacement or {name:journal(out/(name+".jsonl"))
            for name in ("source","supervisor","receiver-1","receiver-2","observer")
            if (out/(name+".jsonl")).is_file()}
        final=database(out/"queue.sqlite3")
        assert final==load(out/"DATABASE_FINAL.json"),"Final database snapshot differs"
        before=database(out/"queue-before-restart.sqlite3") if (out/"queue-before-restart.sqlite3").exists() else None
        if before is not None: assert before==load(out/"DATABASE_BEFORE_RESTART.json"),"Before database snapshot differs"
        outcomes=inspect(load(out/"PLAN.json"),load(out/"CHILD_PROCESSES.json"),load(out/"result.json"),
                         logs,before,final,actual)
        result.update(evidence_status="recorded",outcomes=outcomes)
    except Exception as exc:
        result["errors"].append(type(exc).__name__+": "+str(exc))
    return result
