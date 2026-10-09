"""Frozen 16-condition DRAIN/CONFIRM component qualification."""
import argparse
from collections import Counter
import json
from contract import ROOT, LAB, ARM_CONFIG, matrix, condition_name, require
from audit import validate, audit, sha

MATRIX = ROOT/"local-matrix-v01"


def build():
    plan = json.loads((MATRIX/"PLAN.json").read_text())
    completion = json.loads((MATRIX/"COMPLETION.json").read_text())
    require(plan["conditions"] == matrix() and set(completion["conditions"]) == {condition_name(c) for c in matrix()}, "Wrong matrix")
    require(all(completion[k] for k in ("all_planned_conditions_executed", "all_evidence_valid", "all_scoring_complete", "protected_files_unchanged", "sources_unchanged")), "Incomplete matrix")
    for name, h in plan["source_hashes"].items():
        require(sha(ROOT/name) == sha(MATRIX/"instrument"/name) == h, "Frozen source changed: "+name)
    require(all(sha(LAB/p) == h for p, h in plan["protected_hashes"].items()), "Preserved evidence changed")
    counts, records, artifacts, outcomes = Counter(), [], {}, {}
    for c in matrix():
        name = condition_name(c); folder = MATRIX/name
        e, report = validate(folder), audit(folder)
        require(report == completion["conditions"][name] == json.loads((folder/"AUDIT.json").read_text()), "Replay mismatch")
        o = report["outcomes"]; cfg = ARM_CONFIG[c["arm"]]
        healthy = c["arm"] == "healthy"; gates = cfg["gates"]
        require(o["observation_status"] == "complete" and o["queue"]["checkpoint_content_status"] == "O_final_I_partial", "Checkpoint incomplete")
        require(o["source_flow_status"] == ("not_requested" if healthy else "completed_observed"), "Source path incomplete")
        require(o["summary_runs"] == o["cancel_many_observed"] == int(not healthy), "Source receipt count")
        require(o["shared_service_count"] == 1 and o["file_requests"] == 8, "Service/request count")
        require(o["old_origin_post_policy_effects"] == (0 if gates else 3), "Old effects differ")
        require(o["queue"]["policy_decisions_match_declared_contract"], "Policy failed")
        require(o["successful_file_effects"] == (5 if gates else 8), "Effect count")
        expected = {"O": not gates, "C": not gates, "I": True, "N": True}
        for role, delivered in expected.items():
            r = o["roles"][role]
            require(r["target_artifact"]["present"] == r["target_artifact"]["content"]["correct_final"] == r["oracle_final_delivered_any_path"] == delivered, "Role correctness differs: "+role)
        conf = o["confirmation"]
        require(len(conf["drains"]) == int(cfg["drain"]) and len(conf["claims"]) == int(bool(cfg["claim"])), "Experimental receipt count")
        if cfg["drain"]:
            d = conf["drains"][0]
            require(d["status"] == "completed" and bool(d["independent_live_callers_at_receipt"]), "Scoped wait swallowed I")
            require(d["completion_supported"] == (cfg["fault"] != "omit_target"), "Drain fault not separated")
            counts["supported_scoped_drains"] += int(d["completion_supported"])
            counts["unsupported_scoped_drains"] += int(not d["completion_supported"])
        if cfg["claim"]:
            claim = conf["claims"][0]
            issued = c["arm"] not in {"source_confirm", "receiver_confirm"}
            supported = c["arm"] in {"source_drain_snapshot", "receiver_drain_confirm"}
            require(claim["status"] == ("issued" if issued else "withheld"), "Issue/withhold result")
            require(claim["claim_scope"] == cfg["claim"] and claim["support_at_assessment"] == supported, "Claim support differs")
            require(claim["issued_claim_supported"] == (supported if issued else None), "Unsupported claim lost")
            require(bool(claim["independent_live_callers_at_claim"]), "Independent live caller lost")
            require(claim["inventory"]["inventory_complete"] == (cfg["fault"] != "omit_target"), "Inventory fault not detected")
            require(bool(claim["live_old_callers_at_claim"]) == (c["arm"] not in {"source_drain_snapshot", "receiver_drain_confirm"}), "Worker liveness conflated")
            expected_later = 2 if c["arm"] == "source_drain_snapshot" else 0 if gates else 3
            require(len(claim["old_root_effects_after_claim"]) == expected_later, "Postclaim effect count")
            if cfg["claim"] == "snapshot_quiescent":
                require(not claim["snapshot_member_effects_after_claim"] and len(claim["later_member_effects_after_claim"]) == 2 and claim["consistent_through_declared_horizon"], "Snapshot/future claim conflated")
            counts["issued_claims"] += int(issued)
            counts["withheld_claims"] += int(not issued)
            counts["unsupported_issued_claims"] += int(issued and not supported)
            counts["supported_issued_claims"] += int(issued and supported)
        counts["conditions"] += 1
        for row in e["rows"]: counts[row["kind"]] += 1
        records.append({**c, **o}); outcomes[(c["admission_phase"], c["arm"])] = o
        for name_part in ("events.jsonl", "result.json", "PROCESS.json", "AUDIT.json"):
            artifacts[str((folder/name_part).relative_to(ROOT))] = sha(folder/name_part)
    comparisons = []
    for c in matrix():
        if c["arm"] == "healthy": continue
        o = outcomes[(c["admission_phase"], c["arm"])]
        ref = outcomes[(c["admission_phase"], "healthy")]
        for role in ("I", "N"):
            same = o["roles"][role]["target_artifact"]["sha256"] == ref["roles"][role]["target_artifact"]["sha256"]
            require(same, "Legitimate output changed")
            comparisons.append({**c, "role": role, "hash_matches_healthy": same})
            counts["legitimate_final_reference_hash_matches"] += 1
    history = []
    for path in sorted(ROOT.glob("local-smoke-*/COMPLETION.json")):
        state = json.loads(path.read_text())
        history.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path), "conditions": len(state["conditions"]), "all_evidence_valid": state["all_evidence_valid"]})
    return dict(status="passed", scope="provider-free scoped DRAIN/CONFIRM component qualification",
                conditions=records, counts=dict(sorted(counts.items())), reference_comparisons=comparisons,
                artifacts=artifacts, smoke_history=history,
                matrix_plan_sha256=sha(MATRIX/"PLAN.json"), matrix_completion_sha256=sha(MATRIX/"COMPLETION.json"),
                source_files_rechecked=len(plan["source_hashes"]), preserved_files_rechecked=len(plan["protected_hashes"]),
                preserved_unchanged=True, actual_provider_calls=0, new_live_model_observations=0,
                external_slack_deliveries=0, catalogue_cases_certified=0, independent_human_review=False)


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--write", action="store_true")
    args = p.parse_args(); result = build(); path = ROOT/"QUALIFICATION.json"
    if args.write:
        with path.open("x") as f: json.dump(result, f, ensure_ascii=False, indent=2)
    elif path.exists(): require(json.loads(path.read_text()) == result, "Saved qualification differs")
    print(json.dumps({k: result[k] for k in ("status", "counts", "source_files_rechecked", "preserved_files_rechecked", "actual_provider_calls", "catalogue_cases_certified")}, indent=2))


if __name__ == "__main__": main()
