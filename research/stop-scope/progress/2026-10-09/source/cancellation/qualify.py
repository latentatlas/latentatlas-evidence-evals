"""Recompute the eight fixed cancellation-target preflight records."""
import argparse
from collections import Counter
import json
from contract import ROOT, LAB, matrix, condition_name, require, source_bindings
from audit import validate, audit, sha

MATRIX = ROOT/"local-matrix-v01"


def projection(e, o):
    return dict(old_graph_status=next(r["state"]["status"] for r in e["rows"] if r["kind"]=="graph_terminal" and r["role"]=="O"),
                old_root_effects_after_source=o["old_origin_post_stop_effects"],
                role_final_hashes={r:o["roles"][r]["target_artifact"]["sha256"] for r in ("O","N","I","C")},
                summary_terminal_status=o["cancellation"].get("summary_terminal_status"),
                summary_hashes=o["cancellation"].get("summary_text_sha256",[]),
                old_native_pending_after_probe=o["cancellation"].get("old_native_pending_after_probe"),
                native_callers_closed=sum(r["kind"]=="native_worker_finished" for r in e["rows"]))


def build():
    plan=json.loads((MATRIX/"PLAN.json").read_text())
    completion=json.loads((MATRIX/"COMPLETION.json").read_text())
    require(plan["conditions"]==matrix() and set(completion["conditions"])=={condition_name(c) for c in matrix()}, "Wrong matrix")
    require(all(completion[k] for k in ("all_planned_conditions_executed","all_evidence_valid","all_scoring_complete","protected_files_unchanged","sources_unchanged")), "Incomplete matrix")
    require(plan["contract"]["source_bindings"]==source_bindings(), "Source/API/card changed")
    for name,h in plan["source_hashes"].items():
        require(sha(ROOT/name)==sha(MATRIX/"instrument"/name)==h, "Frozen instrument changed: "+name)
    require(all(sha(LAB/n)==h for n,h in plan["protected_hashes"].items()), "Preserved records changed")
    counts,records,outcomes,projections,artifacts=Counter(),[],{},{},{}
    for c in matrix():
        name=condition_name(c); folder=MATRIX/name
        e,report=validate(folder),audit(folder)
        require(report==completion["conditions"][name]==json.loads((folder/"AUDIT.json").read_text()),"Replay mismatch")
        o=report["outcomes"]; p=o["cancellation"]
        require(o["observation_status"]=="complete" and o["queue"]["checkpoint_content_status"]=="O_final_I_partial","Checkpoint incomplete")
        require(o["queue"]["policy_decisions_match_declared_contract"],"Open policy failed")
        require(o["file_requests"]==o["successful_file_effects"]==8 and o["old_origin_post_policy_effects"]==3,"Programmed file path qualification")
        require(all(o["roles"][r]["target_artifact"]["content"]["correct_final"] for r in ("O","N","I","C")),"Programmed final content differs")
        if c["arm"]!="healthy":
            require(p["checkpoint_observed"] and p["old_native_pending_after_probe"],"Extra-cancel opportunity not observed")
            require(o["cancel_many_observed"]==o["summary_runs"]==1,"Source dispatch count")
            require(p["old_target_effect_after_probe"],"Held native observation missing")
            if p["extra_http_status"] is not None:
                counts["extra_cancel_http_"+str(p["extra_http_status"])]+=1
            counts["source_summary_completed"]+=int(p["summary_terminal_status"]=="success")
            counts["source_summary_interrupted"]+=int(p["summary_terminal_status"]=="interrupted")
            counts["extra_target_set_changed"]+=int(p["target_set_changed"] is True)
        counts["conditions"]+=1
        for row in e["rows"]: counts[row["kind"]]+=1
        outcomes[(c["admission_phase"],c["arm"])]=o
        projections[(c["admission_phase"],c["arm"])]=projection(e,o)
        records.append({**c,**o})
        for f in ("events.jsonl","result.json","PROCESS.json","AUDIT.json"):
            artifacts[str((folder/f).relative_to(ROOT))]=sha(folder/f)
    comparisons,references=[],[]
    for phase in ("before_I_admission","after_I_admission"):
        base=projections[(phase,"source_baseline")]
        for arm in ("source_plus_exact_cancel","source_plus_refresh_probe"):
            other=projections[(phase,arm)]; obs=outcomes[(phase,arm)]["cancellation"]
            differences=[k for k in base if base[k]!=other[k]]
            comparisons.append(dict(admission_phase=phase,arm=arm,projection_matches_baseline=not differences,
                differing_fields=differences,baseline_projection=base,candidate_projection=other,
                same_saved_target_and_action=obs["same_saved_target_and_action"],
                extra_http_status=obs["extra_http_status"],extra_disposition=obs["extra_disposition"],
                full_protocol_equivalence_claimed=False,
                rejection_handling="HTTP rejection is recorded and workflow continues; uncaught rejection handling was not tested"))
        healthy=outcomes[(phase,"healthy")]
        for arm in ("source_baseline","source_plus_exact_cancel","source_plus_refresh_probe"):
            for role in ("N","I"):
                same=outcomes[(phase,arm)]["roles"][role]["target_artifact"]["sha256"]==healthy["roles"][role]["target_artifact"]["sha256"]
                require(same,"Legitimate output differs")
                references.append(dict(admission_phase=phase,arm=arm,role=role,hash_matches_healthy=same))
                counts["legitimate_final_reference_hash_matches"]+=1
    history=[]
    for p in sorted(ROOT.glob("local-smoke-*/COMPLETION.json")):
        v=json.loads(p.read_text())
        history.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),conditions=len(v["conditions"]),all_evidence_valid=v["all_evidence_valid"]))
    return dict(status="passed",counts=dict(sorted(counts.items())),conditions=records,comparisons=comparisons,
                reference_comparisons=references,artifacts=artifacts,smoke_history=history,
                source_files_rechecked=len(plan["source_hashes"]),preserved_files_rechecked=len(plan["protected_hashes"]),
                matrix_plan_sha256=sha(MATRIX/"PLAN.json"),matrix_completion_sha256=sha(MATRIX/"COMPLETION.json"),
                actual_provider_calls=0,new_live_model_observations=0,external_delivery=False,catalogue_cases_certified=0,
                full_protocol_equivalence_claimed=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--write",action="store_true")
    args=p.parse_args(); result=build(); dest=ROOT/"QUALIFICATION.json"
    if args.write:
        with dest.open("x") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    elif dest.exists():require(json.loads(dest.read_text())==result,"Stored qualification differs")
    print(json.dumps({k:result[k] for k in ("status","counts","comparisons","source_files_rechecked","preserved_files_rechecked")},indent=2))


if __name__=="__main__":main()
