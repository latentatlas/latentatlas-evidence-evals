"""Replay raw worker lifecycle before assessing claims. False claims are outcomes."""
import hashlib
import json
from contract import require

BODY_FIELDS = ("inventory_id", "version", "root", "service_id", "members", "policy")


def validate_confirmation(e):
    rows = e["rows"]
    snapshots, drains, claims = {}, {}, []
    root = e["by_role"]["O"]["origin_key"]
    service = next(r["service_id"] for r in rows if r["kind"] == "shared_file_service_created")
    effects = {x["op"]["operation_id"]: x for x in e["effects"]}
    version = 0
    for r in rows:
        kind = r["kind"]
        if kind in {"scope_inventory", "scoped_drain_requested", "scoped_drain_receipt",
                    "scope_confirmation", "experimental_assessment_closed", "confirmation_fault_activated"}:
            require(r["root"] == root, "Foreign termination root")
            if "service_id" in r: require(r["service_id"] == service, "Foreign termination service")
        if kind == "scope_inventory":
            body = {k: r[k] for k in BODY_FIELDS}
            h = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            require(h == r["sha256"], "Inventory hash mismatch")
            require(r["version"] == version + 1 and r["inventory_id"] not in snapshots, "Inventory version/identity")
            version = r["version"]
            ids = [m["operation_id"] for m in r["members"]]
            require(ids == sorted(set(ids)), "Duplicate/unsorted inventory members")
            for m in r["members"]:
                oid = m["operation_id"]
                require(oid in effects and effects[oid]["op"]["origin_key"] == root
                        and m["identity_key"] == effects[oid]["op"]["key"], "Foreign inventory member")
                require(type(m["finished"]) is bool and type(m["admitted"]) is bool, "Invalid inventory fields")
            snapshots[r["inventory_id"]] = r
        elif kind == "scoped_drain_requested":
            require(r["drain_id"] not in drains and r["timeout_seconds"] > 0, "Duplicate/invalid drain")
            drains[r["drain_id"]] = {"request": r}
        elif kind == "scoped_drain_receipt":
            require(r["drain_id"] in drains and "receipt" not in drains[r["drain_id"]], "Orphan/duplicate drain receipt")
            require(r["status"] in {"completed", "timeout"} and r["inventory_ids"], "Invalid drain status")
            require(len(set(r["inventory_ids"])) == len(r["inventory_ids"]), "Repeated drain inventory")
            for iid in r["inventory_ids"]:
                require(iid in snapshots and drains[r["drain_id"]]["request"]["seq"] < snapshots[iid]["seq"] < r["seq"], "Unbound drain inventory")
            require(r["final_inventory_id"] == r["inventory_ids"][-1]
                    and r["final_inventory_sha256"] == snapshots[r["final_inventory_id"]]["sha256"], "Drain final inventory reference")
            drains[r["drain_id"]]["receipt"] = r
        elif kind == "scope_confirmation":
            require(r["inventory_id"] in snapshots and r["inventory_sha256"] == snapshots[r["inventory_id"]]["sha256"], "Unbound confirmation inventory")
            require(r["claim_scope"] in {"snapshot_quiescent", "file_effects_closed"}
                    and r["status"] in {"issued", "withheld"}, "Invalid confirmation schema")
            require(r["horizon"] == ("inventory_capture" if r["claim_scope"] == "snapshot_quiescent" else "measurement_closed_while_policy_unchanged"), "Wrong claim horizon")
            require(all(type(r[k]) is bool for k in ("producer_quiescent", "producer_gates_active", "force_issue")), "Invalid producer predicates")
            claims.append(r)
    require(all("receipt" in d for d in drains.values()), "Missing scoped drain receipt")
    assessment = [r for r in rows if r["kind"] == "experimental_assessment_closed"]
    if e["boundary"]:
        require(len(assessment) == 1, "Missing/duplicate experimental assessment boundary")
        a = assessment[0]
        require(a["arm"] == e["result"]["arm"] and not a["independent_fixture_released"], "Assessment fixture/arm")
        require(all(r["seq"] < a["seq"] for r in claims)
                and all(d["receipt"]["seq"] < a["seq"] for d in drains.values()), "Late experimental claim")
        require(bool(drains) == a["drain_requested"] and bool(claims) == bool(a["claim_scope"]), "Assessment receipt gap")
    held = [r for r in rows if r["kind"] == "independent_effect_held"]
    release = [r for r in rows if r["kind"] == "independent_effect_released"]
    require(len(held) == len(release) == 1, "Independent effect fixture receipt gap")
    h, rel = held[0], release[0]
    require(h["fixture_only"] and rel["fixture_only"] and h["service_id"] == rel["service_id"] == service, "Independent fixture attribution")
    iid = e["targets"]["I"]["op"]["operation_id"]
    require(h["op"] == effects[iid]["op"] and e["queue"]["admitted"][iid]["seq"] < h["seq"], "Wrong I effect hold")
    if assessment: require(assessment[0]["seq"] < rel["seq"], "I released before experimental assessment")
    if effects[iid]["attempt"]:
        require(max(h["seq"], rel["seq"]) < effects[iid]["attempt"]["seq"], "I effect before hold release")
    return {"snapshots": snapshots, "drains": list(drains.values()), "claims": claims}


def score_confirmation(e):
    rows, q = e["rows"], e["confirmation"]
    root = e["by_role"]["O"]["origin_key"]
    entered = {r["op"]["operation_id"]: r for r in rows if r["kind"] == "native_worker_entered"}
    finished = {r["op"]["operation_id"]: r for r in rows if r["kind"] == "native_worker_finished"}

    def membership(seq, origin=root):
        ids = {oid for oid, r in entered.items() if r["seq"] < seq and r["op"]["origin_key"] == origin}
        live = {oid for oid in ids if finished[oid]["seq"] >= seq}
        return ids, live

    def inv_score(s):
        ids, live = membership(s["seq"])
        supplied = {m["operation_id"] for m in s["members"]}
        reported_live = {m["operation_id"] for m in s["members"] if not m["finished"]}
        return dict(inventory_id=s["inventory_id"], inventory_complete=supplied == ids,
                    missing_operation_ids=sorted(ids-supplied), extra_operation_ids=sorted(supplied-ids),
                    state_report_matches=reported_live == (live & supplied),
                    live_member_ids_at_capture=sorted(live))

    inventories = {iid: inv_score(s) for iid, s in q["snapshots"].items()}
    result_drains = []
    for d in q["drains"]:
        rec = d["receipt"]
        inv = inventories[rec["final_inventory_id"]]
        _, live = membership(rec["seq"])
        _, ilive = membership(rec["seq"], e["by_role"]["I"]["origin_key"])
        result_drains.append(dict(drain_id=rec["drain_id"], status=rec["status"],
            final_inventory=inv, live_old_callers_at_receipt=sorted(live),
            independent_live_callers_at_receipt=sorted(ilive),
            completion_supported=rec["status"] == "completed" and inv["inventory_complete"] and inv["state_report_matches"] and not live,
            elapsed_ms=(rec["monotonic_ns"]-d["request"]["monotonic_ns"])/1e6))
    result_claims = []
    for claim in q["claims"]:
        snap = q["snapshots"][claim["inventory_id"]]; inv = inventories[claim["inventory_id"]]
        _, live = membership(claim["seq"])
        _, ilive = membership(claim["seq"], e["by_role"]["I"]["origin_key"])
        prior_policies = [r for r in rows if r["kind"] == "scope_policy_activated" and r["seq"] < claim["seq"]]
        p = prior_policies[-1]["policy"]
        gated = p["kind"] == "origin" and p["root"] == root and p["admission"] and p["effect"]
        producer_matches = (claim["producer_quiescent"] == all(m["finished"] for m in snap["members"])
                            and claim["producer_gates_active"] == bool(gated) and snap["policy"] == p)
        supported = inv["inventory_complete"] and inv["state_report_matches"] and producer_matches and not live
        if claim["claim_scope"] == "file_effects_closed": supported = supported and gated
        later = []
        for x in e["effects"]:
            if x["op"]["origin_key"] != root or not x["result"]: continue
            changed = x["success"] or x["result"]["after_sha256"] != x["attempt"]["before_sha256"]
            if changed and x["attempt"]["seq"] > claim["seq"]: later.append(x["op"]["operation_id"])
        supplied = {m["operation_id"] for m in snap["members"]}
        later_in_snapshot = sorted(set(later) & supplied)
        policy_unchanged = not any(r["kind"] == "scope_policy_activated" and r["seq"] > claim["seq"] for r in rows)
        consistent = (not later and policy_unchanged) if claim["claim_scope"] == "file_effects_closed" else not later_in_snapshot
        result_claims.append(dict(claim_id=claim["claim_id"], status=claim["status"], claim_scope=claim["claim_scope"],
            inventory=inv, producer_predicates_match=producer_matches,
            live_old_callers_at_claim=sorted(live), independent_live_callers_at_claim=sorted(ilive),
            scoped_quiescence_observed=not live, file_gates_active=bool(gated),
            support_at_assessment=bool(supported), policy_unchanged_through_close=policy_unchanged,
            old_root_effects_after_claim=later, snapshot_member_effects_after_claim=later_in_snapshot,
            later_member_effects_after_claim=sorted(set(later)-supplied),
            consistent_through_declared_horizon=consistent,
            issued_claim_supported=(bool(supported and consistent) if claim["status"] == "issued" else None)))
    return dict(inventories= list(inventories.values()), drains=result_drains, claims=result_claims,
                issued_claims=sum(c["status"] == "issued" for c in result_claims),
                unsupported_issued_claims=sum(c["issued_claim_supported"] is False for c in result_claims),
                withheld_claims=sum(c["status"] == "withheld" for c in result_claims))
