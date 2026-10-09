"""Separate stdlib raw HTTP/identity/lifecycle/disk check; no harness imports."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs

ROOT = Path(__file__).resolve().parent
MATRIX = ROOT/"local-matrix-v01"

def check(value, message):
    if not value: raise ValueError(message)

def digest(data): return hashlib.sha256(data).hexdigest()

def build():
    completion=json.loads((MATRIX/"COMPLETION.json").read_text())
    plan=json.loads((MATRIX/"PLAN.json").read_text())
    check(len(plan["conditions"])==len(completion["conditions"])==8,"Matrix size")
    counts,cases=Counter(),[]
    for name,stored in completion["conditions"].items():
        folder=MATRIX/name
        raw=(folder/"events.jsonl").read_bytes()
        check(digest(raw)==stored["events_sha256"],"Event hash")
        rows=[json.loads(x) for x in raw.splitlines()]
        check([r["seq"] for r in rows]==list(range(1,len(rows)+1)),"Event order")
        def many(k):return [r for r in rows if r["kind"]==k]
        def one(k):
            found=many(k);check(len(found)==1,"Expected one "+k);return found[0]
        bound={r["identity"]["key"]:r for r in many("authority_factory_bound")}
        roles={r["grant"]["role"]:r["identity"] for r in bound.values()}
        starts={r["op"]["operation_id"]:r for r in many("native_worker_entered")}
        ends={r["op"]["operation_id"]:r for r in many("native_worker_finished")}
        check(len(starts)==len(ends)==8 and set(starts)==set(ends),"Caller count/closure")
        for oid,r in starts.items():
            ident=bound[r["op"]["key"]]["identity"]
            check(all(r["op"][k]==v for k,v in ident.items()),"Caller identity")
            check(r["seq"]<ends[oid]["seq"],"Caller end order")
        attempts={r["op"]["operation_id"]:r for r in many("native_effect_attempt")}
        results={r["op"]["operation_id"]:r for r in many("native_effect_result")}
        check(set(attempts)==set(results)==set(starts),"Native effects missing")
        effects=[r for oid,r in results.items() if r["success"] or r["after_sha256"]!=attempts[oid]["before_sha256"]]
        check(len(effects)==stored["outcomes"]["successful_file_effects"]==8,"File effects")
        for oid,r in results.items():
            check(starts[oid]["seq"]<attempts[oid]["seq"]<r["seq"]<ends[oid]["seq"],"Native effect interval")
        requests={r["request_id"]:r for r in many("native_http_request")}
        responses={r["request_id"]:r for r in many("native_http_response")}
        cancels=[r for r in requests.values() if r["method"]=="POST" and r["path"]=="/runs/cancel"]
        terminals={r["role"]:r for r in many("graph_terminal")}
        summary=many("summary_local_delivery")
        for r in summary:
            check(digest(r["text"].encode())==r["text_sha256"] and not r["external_delivery"],"Summary bytes")
        scored=stored["outcomes"]["cancellation"]
        old=roles["O"]
        if many("source_stop_requested"):
            start,selection,finish=one("cancel_probe_started"),one("cancel_probe_targets_selected"),one("cancel_probe_finished")
            source=requests[start["source_request_id"]]
            check(source in cancels and json.loads(source["body"])=={"thread_id":old["thread_id"],"run_ids":[old["run_id"]]},"Source target")
            check(parse_qs(source["query"])=={"action":["interrupt"]},"Source action")
            known={old["run_id"]:"O",roles["S"]["run_id"]:"S"}
            check(start["known_targets"]==known,"Target identity")
            extra=[r for r in cancels if r is not source]
            check(len(extra)==int(bool(selection["run_ids"])),"Extra cancel count")
            if extra:
                wire=extra[0];receipt=responses[wire["request_id"]]
                check(selection["seq"]<wire["seq"]<receipt["seq"]<finish["seq"],"Extra order")
                check(json.loads(wire["body"])=={"thread_id":old["thread_id"],"run_ids":selection["run_ids"]},"Wire body")
                check(parse_qs(wire["query"])=={"action":["interrupt"]},"Extra action")
                status=receipt["status"]
                check(scored["extra_http_status"]==status,"Status outcome")
                counts["extra_http_"+str(status)]+=1
                check(scored["extra_target_roles"]==[known[x] for x in selection["run_ids"]],"Target roles outcome")
            else:
                check(scored["extra_http_status"] is None and not scored["requested"],"Absent extra outcome")
            if start["mode"]=="same_saved_targets":
                check(selection["run_ids"]==[old["run_id"]],"Same-target operation")
            if start["mode"]=="refresh_active_thread":
                list_requests=[r for r in requests.values() if r["method"]=="GET" and r["path"]==f"/threads/{old['thread_id']}/runs" and start["seq"]<r["seq"]<selection["seq"]]
                observed=set()
                check({parse_qs(r["query"])["status"][0] for r in list_requests}=={"pending","running"},"Active enumeration")
                for r in list_requests:
                    receipt=responses[r["request_id"]];check(receipt["status"]==200,"List receipt")
                    observed.update(x.get("run_id") or x.get("id") for x in json.loads(receipt["body"]))
                check(selection["run_ids"]==sorted(observed),"Refreshed selection")
            target=[r for r in starts.values() if r["op"]["key"]==old["key"] and r["op"]["call_id"]=="target-"+old["key"]]
            check(len(target)==1,"Native target identity")
            oid=target[0]["op"]["operation_id"]
            check(target[0]["seq"]<start["seq"]<finish["seq"]<attempts[oid]["seq"],"Accepted native survives probe")
            check(scored["old_native_pending_after_probe"] and scored["old_target_effect_after_probe"],"Native outcome")
            states={}
            for r in many("cancel_probe_run_state"):
                ident=roles[r["role"]]
                path=f"/threads/{ident['thread_id']}/runs/{ident['run_id']}"
                candidates=[q for q in requests.values() if q["method"]=="GET" and q["path"]==path and start["seq"]<q["seq"]<responses[q["request_id"]]["seq"]<r["seq"]]
                check(candidates,"State lacks HTTP")
                q=max(candidates,key=lambda x:x["seq"])
                check(json.loads(responses[q["request_id"]]["body"])==r["state"],"State not wire-backed")
                states.setdefault(r["phase"],{})[r["role"]]=r["state"]["status"]
            check(states==scored["state_before_after"],"State score")
            check(terminals["S"]["state"]["status"]==scored["summary_terminal_status"],"S terminal")
            check([s["text_sha256"] for s in summary]==scored["summary_text_sha256"],"S output")
            counts["source_stop_conditions"]+=1
            counts["summary_deliveries"]+=len(summary)
            counts["summary_interrupted"]+=int(terminals["S"]["state"]["status"]=="interrupted")
        else:check(not cancels and not summary and not scored["requested"],"Healthy source activity")
        final=next(r for r in many("observer_inventory") if r["phase"]=="final")["files"]
        actual={str(p.relative_to(folder)):digest(p.read_bytes()) for p in (folder/"files").rglob("*") if p.is_file()}
        check(actual=={f["path"]:f["sha256"] for f in final},"Disk inventory")
        check(all(digest(f["content"].encode())==f["sha256"] for f in final),"Recorded file bytes")
        check(final==stored["inventory"],"Stored inventory")
        counts["disk_files_rehashed"]+=len(actual)
        counts["native_callers_closed"]+=len(ends)
        counts["native_file_effects"]+=len(effects)
        counts["conditions"]+=1
        cases.append(dict(condition=name,events_sha256=digest(raw),disk_files=len(actual)))
    return dict(status="passed",counts=dict(counts),conditions=cases,scorer_imported=False,harness_imported=False,
                independent_human_review=False,provider_calls=0,catalogue_cases_certified=0)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--write",action="store_true")
    args=p.parse_args();result=build();dest=ROOT/"RAW_CANCEL_CROSSCHECK.json"
    if args.write:
        with dest.open("x") as f:json.dump(result,f,indent=2)
    elif dest.exists():check(json.loads(dest.read_text())==result,"Saved crosscheck differs")
    print(json.dumps({"status":result["status"],"counts":result["counts"]},indent=2))

if __name__=="__main__":main()

