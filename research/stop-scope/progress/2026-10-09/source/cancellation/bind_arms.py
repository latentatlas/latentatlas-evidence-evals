"""Link original F07 arm identities to measured components without pooling arms."""
import argparse
import json
from contract import ROOT, LAB, PREDECESSOR, require
from audit import sha

CASE_ID="F07-V1-accepted_pre_effect-before"
EXPECTED={
    "source_baseline":["SOURCE_STOP"],
    "source_plus_cancel":["SOURCE_STOP","CANCEL"],
    "source_plus_drain":["SOURCE_STOP","DRAIN"],
    "source_plus_receiver":["SOURCE_STOP","RECEIVER"],
    "source_plus_confirm":["SOURCE_STOP","CONFIRM"],
    "layered_candidate":["SOURCE_STOP","CANCEL","DRAIN","RECEIVER","CONFIRM"],
    "layered_without_drain":["SOURCE_STOP","CANCEL","RECEIVER","CONFIRM"],
    "layered_without_receiver":["SOURCE_STOP","CANCEL","DRAIN","CONFIRM"],
}

def validate_original(card):
    require(card["case_id"]==CASE_ID,"Wrong original case")
    arms=card["original_contract"]["interventions"]
    require(len(arms)==8 and {a["arm_id"]:a["component_ids"] for a in arms}==EXPECTED,
            "Original arms/components changed or duplicated")
    require(card["original_contract"]["mechanism"]["source_pin"]=="e0d9aff59925a4da55ec8d6c31fa723651c24909","Source pin changed")
    return arms

def witness(folder, arm, matrix_name):
    records=[]
    for phase in ("before_I_admission","after_I_admission"):
        name="create-17-"+phase+"-"+arm; path=folder/matrix_name/name
        report=json.loads((path/"AUDIT.json").read_text())
        require(report["evidence_valid"] and report["scoring_status"]=="complete","Invalid component evidence")
        require(sha(path/"events.jsonl")==report["events_sha256"],"Component raw evidence changed")
        records.append(dict(condition=name,artifact=str((path/"AUDIT.json").relative_to(LAB)),
                            audit_sha256=sha(path/"AUDIT.json"),events_sha256=report["events_sha256"]))
    return records

def build():
    source=LAB/"stop_scope_suite/design/core_case_bindings_2026_10_08/CARDS.json"
    card=next(c for c in json.loads(source.read_text())["cards"] if c["case_id"]==CASE_ID)
    original=validate_original(card)
    q=json.loads((ROOT/"QUALIFICATION.json").read_text())
    require(q["status"]=="passed" and q["counts"]["conditions"]==8,"Preflight incomplete")
    for rel,h in q["artifacts"].items():require(sha(ROOT/rel)==h,"Preflight evidence changed")
    descriptions={
      "source_baseline":(
        ROOT,"source_baseline","local-matrix-v01","source_component_measured",
        ["Unified original-arm topology and both native effect orders remain open."]),
      "source_plus_cancel":(
        ROOT,"source_plus_exact_cancel","local-matrix-v01","same_target_candidate_measured",
        ["Same saved O target/action returns HTTP404 after original cancellation in this checkpoint.",
         "Matched bounded outcomes use record-and-continue rejection handling; not full API/protocol equivalence.",
         "Refreshing active runs instead targets S and is a different probe, not an interchangeable implementation."]),
      "source_plus_drain":(
        PREDECESSOR,"source_drain_snapshot","local-matrix-v01","component_only_not_exact_arm",
        ["Existing witness also emits snapshot_quiescent CONFIRM; pure DRAIN arm has not been run.",
         "Drain waits declared O-root native callers, not model/provider computation."]),
      "source_plus_receiver":(
        ROOT.parent/"role_queue_v04","origin_effect","local-matrix-v02","effect_only_component_measured",
        ["Use the effect-only v04 witness; v05 receiver arms additionally enforce ADMISSION.",
         "Rerun under unified cancellation/confirmation timing rather than pool historical conditions."]),
      "source_plus_confirm":(
        PREDECESSOR,"source_confirm","local-matrix-v01","confirmation_component_measured",
        ["The existing file_effects_closed definition requires both admission and effect gates.",
         "Choose one scope for every CONFIRM arm and revalidate support before interpreting ablations."]),
      "layered_candidate":(
        PREDECESSOR,"receiver_drain_confirm","local-matrix-v01","combined_components_not_exact_arm",
        ["Existing witness adds ADMISSION and has no extra saved-target CANCEL.",
         "Original components and a common CONFIRM scope need one integrated arm."]),
      "layered_without_drain":(
        PREDECESSOR,"receiver_confirm","local-matrix-v01","combined_components_not_exact_arm",
        ["Existing witness adds ADMISSION and has no extra saved-target CANCEL.",
         "Removing DRAIN must leave the same target policy and CONFIRM scope as layered_candidate."]),
      "layered_without_receiver":(
        PREDECESSOR,"source_drain_snapshot","local-matrix-v01","combined_components_not_exact_arm",
        ["Existing witness uses snapshot_quiescent rather than layered file_effects_closed and no extra CANCEL.",
         "Changing claim meaning together with removing RECEIVER would confound the comparison."]),
    }
    result=[]
    for arm in original:
        folder,name,mat,status,gaps=descriptions[arm["arm_id"]]
        result.append(dict(arm_id=arm["arm_id"],original_component_ids=arm["component_ids"],status=status,
                           original_arm_fully_verified=False,witnesses=witness(folder,name,mat),open_items=gaps))
    obligations=[
      ("G01","component_evidence_available","Healthy final outputs exist; retain failed controls/incorrect outputs as outcomes in unified arms."),
      ("G02","component_evidence_available","Actual source request, native entry/attempt/result and confirmation boundaries are recorded; no invented physical commit time."),
      ("G03","component_evidence_available","Runtime/run/tool/caller/root identities are linked; final grant-epoch/hook binding must be explicit."),
      ("G04","open","Two I-admission phases are not two native effect orders; add a genuinely reversed effect schedule. N is fresh same-thread authority and I has a separate root/thread."),
      ("G05","component_evidence_available","Earlier no-op/overbroad/omitted-worker controls exist; retain matched failure witnesses in the unified protocol."),
      ("G06","component_evidence_available","Receipt/identity/inventory corruption tests reject evidence; preserve tests under the unified adapter."),
      ("G07","component_evidence_available","Callers and sole consumer close with bounded waits; final cleanup cannot justify an earlier stop claim."),
      ("G08","partly_resolved","All eight original arms retained. Same-target extra CANCEL is measured; pure DRAIN, effect-only RECEIVER and consistent CONFIRM combinations remain open."),
      ("G09","open","No dedicated same-protocol fresh-environment repeat of all eight original arms has been run."),
      ("G10","component_evidence_available","Read-only observer/cleanup and S output are distinct. C is a programmed old-root continuation, N and I are separate legitimate authorities."),
    ]
    return dict(case_id=CASE_ID,status="original_arm_mapping_with_open_integration",
        source_card=str(source.relative_to(LAB)),source_card_sha256=sha(source),
        original_case_sha256=card["original_case_sha256"],original_arms_preserved=True,arms=result,
        cancellation_preflight=dict(qualification_sha256=sha(ROOT/"QUALIFICATION.json"),comparisons=q["comparisons"],
            refresh_probe_is_original_cancel_arm=False,full_protocol_equivalence_claimed=False),
        mechanism_alignment=dict(original=card["original_contract"]["mechanism"]["description"],
            current="Native caller -> research-owned FIFO -> sole native FilesystemBackend consumer.",
            status="explicit_topology_binding_required",gate_witness="Accepted O native mutation held before native callback.",
            note="Shared service qualification is not silently relabelled as an identical original executor topology."),
        obligations=[dict(id=k,status=s,note=n) for k,s,n in obligations],
        original_case_complete=False,catalogue_cases_certified=0,provider_calls=0,
        next_step="One unified original-eight-arm protocol: fixed O cancellation target/error handling, separate ADMISSION from RECEIVER, one CONFIRM scope, then second native effect order and fresh repeat.")

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--write",action="store_true")
    args=p.parse_args();result=build();dest=ROOT/"F07_ARM_BINDING.json"
    if args.write:
        with dest.open("x") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    elif dest.exists():require(json.loads(dest.read_text())==result,"Saved binding differs")
    print(json.dumps(dict(status=result["status"],original_arms=len(result["arms"]),catalogue_cases_certified=0),indent=2))

if __name__=="__main__":main()

