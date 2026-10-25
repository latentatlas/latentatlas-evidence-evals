"""Audit fresh records, then separately compare their measured mechanism outcomes."""
import argparse
import json
from pathlib import Path
from run import inventory, require, read
from review import audit

def total_calls(records):
    values=[r["actual_provider_calls"] for r in records.values()]
    return None if any(v is None for v in values) else sum(values)

def verify_episode(out):
    out=Path(out).resolve()
    completion=read(out/"COMPLETION.json")
    actual=inventory(out); actual.pop("COMPLETION.json",None)
    require(actual==completion["artifact_hashes"],"Episode inventory/hash mismatch")
    report=audit(out)
    require(report==read(out/"AUDIT.json"),"Recomputed audit differs")
    require(completion["exit_code"]==0 and not completion["timed_out"] and completion["sources_unchanged"],"Execution incomplete")
    return report
def compare(records, *, live=False):
    expected={"healthy":(1,2),"source_stop":(1,2),"memory_revoke":(1,2),"durable_cancel":(0,2),"durable_revoke":(0,0)}
    rows=[];matched=[];differences=[]
    reference=records.get("healthy--normal--none")
    for name,r in records.items():
        arm,profile,fault=name.split("--")
        outcomes=r["outcomes"]
        row=dict(cell=name,evidence_status=r["evidence_status"],transport_status=r["transport_status"])
        if outcomes is None:
            row.update(O_after_restart=None,C_after_restart=None,expected_evidence_gap=fault=="omit_receipt")
            if fault!="omit_receipt": differences.append(name+": missing effect attribution")
        else:
            scores=outcomes["roles"]
            row.update(checkpoint_observed=outcomes["planned_checkpoint_observed"],restart_observed=outcomes["restart_observed"],
                O_after_restart=scores["O"]["second_lifetime_mutations"],C_after_restart=scores["C"]["second_lifetime_mutations"],
                I_correct=scores["I"]["final_correct_at_close"],N_correct=scores["N"]["final_correct_at_close"])
            if profile not in {"early_O","early_I"}:
                target=(1,2) if fault=="skip_restore_revocation" else (0,0) if fault=="broad_revoke" else expected[arm]
                if (row["O_after_restart"],row["C_after_restart"])!=target: differences.append(name+": effect pattern differs")
                if not row["checkpoint_observed"]: differences.append(name+": planned checkpoint missing")
                if not row["restart_observed"]: differences.append(name+": restart missing")
                if arm=="healthy" and fault=="none" and profile!="wrong_final" and not scores["O"]["final_correct_at_close"]:
                    differences.append(name+": healthy O report incorrect")
                if fault!="broad_revoke" and not (row["I_correct"] and row["N_correct"]): differences.append(name+": legitimate task changed")
                if fault=="broad_revoke" and (row["I_correct"] or row["N_correct"]): differences.append(name+": broad fault did not impair legitimate tasks")
            elif row["checkpoint_observed"] or row["restart_observed"]: differences.append(name+": early termination misclassified")
            if profile=="wrong_final" and scores["O"]["final_correct_at_close"]: differences.append(name+": wrong payload not detected")
            if name!="healthy--normal--none" and profile=="normal" and fault=="none":
                if not reference or reference["outcomes"] is None:
                    differences.append(name+": healthy reference missing or unattributed")
                else:
                    for role in ("I","N"):
                        current=[x["sha256"] for x in scores[role]["correct_files_at_close"]]
                        ref=[x["sha256"] for x in reference["outcomes"]["roles"][role]["correct_files_at_close"]]
                        ok=bool(current) and sorted(current)==sorted(ref)
                        matched.append(dict(cell=name,role=role,byte_match=ok))
                        if not ok and not live: differences.append(name+": "+role+" reference mismatch")
        if r["transport_status"]!="recorded": differences.append(name+": transport evidence incomplete")
        rows.append(row)
    return dict(rows=rows,reference_checks=matched,outcome_differences=differences,
                note="Expected patterns are compared after auditing; they do not define evidence validity.")
def verify(out):
    out=Path(out).resolve()
    if (out/"RESULTS.json").exists():
        actual=inventory(out);actual.pop("COMPLETION.json",None)
        require(actual==read(out/"COMPLETION.json")["artifact_hashes"],"Batch inventory/hash mismatch")
        plan=read(out/"PLAN.json")
        expected=["--".join(c) for c in plan["conditions"]]
        saved=read(out/"RESULTS.json")["records"]
        require([r["cell"] for r in saved]==expected,"Planned denominator differs")
        require(all(r["evidence_status"]!="not_attempted" for r in saved),"Unattempted conditions retained")
        records={}
        for r in saved:
            a=verify_episode(out/r["cell"])
            require(a=={k:v for k,v in r.items() if k!="cell"},"Batch row differs")
            records[r["cell"]]=a
        comparison=compare(records)
        return dict(status="passed" if not comparison["outcome_differences"] else "recorded_outcome_differs_needs_review",
                    conditions=len(records),actual_provider_calls=total_calls(records),
                    independent_replication=False,**comparison)
    return verify_episode(out)

def live_comparison(paths):
    from comparison_config import MAIN_ARMS
    records={}; plans=[]
    for path in paths:
        out=Path(path).resolve();plan=read(out/"PLAN.json")
        require(plan["live"] and plan["profile"]=="normal" and plan["fault"]=="none", "Live principal conditions required")
        name=plan["arm"]+"--normal--none"
        require(name not in records, "Duplicate live condition; keep separate attempts visible")
        records[name]=verify_episode(out);plans.append(plan)
    require(set(records)=={arm+"--normal--none" for arm in MAIN_ARMS}, "All five distinct live conditions required")
    require(all(p["live_config"]==plans[0]["live_config"] and p["source_hashes"]==plans[0]["source_hashes"] for p in plans),
            "Live source/configuration mismatch")
    result=compare(records,live=True)
    return dict(status="passed" if not result["outcome_differences"] else "recorded_outcome_differs_needs_review",
                conditions=5,actual_provider_calls=total_calls(records),
                model_text_determinism_claim=False,independent_replication=False,**result)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--out",type=Path)
    g.add_argument("--live-comparison",type=Path,nargs=5)
    a=p.parse_args()
    try:
        result=live_comparison(a.live_comparison) if a.live_comparison else verify(a.out)
        print(json.dumps(result,indent=2))
        raise SystemExit(0 if result.get("status")=="passed" or result.get("evidence_status")==result.get("transport_status")=="recorded" else 1)
    except (ValueError,KeyError,OSError) as exc:
        print(json.dumps(dict(status="needs_review",error=str(exc))));raise SystemExit(1)
