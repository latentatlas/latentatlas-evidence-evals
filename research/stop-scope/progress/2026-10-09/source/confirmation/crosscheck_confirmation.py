"""Separate stdlib-only lifecycle/claim/disk replay; imports no harness or scorer."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MATRIX = ROOT/"local-matrix-v01"


def check(value, message):
    if not value: raise ValueError(message)


def digest(value): return hashlib.sha256(value).hexdigest()


def build():
    completion = json.loads((MATRIX/"COMPLETION.json").read_text())
    plan = json.loads((MATRIX/"PLAN.json").read_text())
    counts, cases = Counter(), []
    check(len(plan["conditions"]) == len(completion["conditions"]) == 16, "Matrix size")
    for name, stored in completion["conditions"].items():
        folder = MATRIX/name
        rows = [json.loads(x) for x in (folder/"events.jsonl").read_text().splitlines()]
        check(digest((folder/"events.jsonl").read_bytes()) == stored["events_sha256"], "Event hash")
        check([r["seq"] for r in rows] == list(range(1, len(rows)+1)), "Event order")
        bound = {r["identity"]["key"]: r for r in rows if r["kind"] == "authority_factory_bound"}
        roles = {r["grant"]["role"]: r["identity"] for r in bound.values()}
        old = roles["O"]["origin_key"]; independent = roles["I"]["origin_key"]
        starts = {r["op"]["operation_id"]: r for r in rows if r["kind"] == "native_worker_entered"}
        ends = {r["op"]["operation_id"]: r for r in rows if r["kind"] == "native_worker_finished"}
        check(set(starts) == set(ends) and all(starts[k]["seq"] < ends[k]["seq"] for k in starts), "Worker closure")
        for r in starts.values():
            ident = bound[r["op"]["key"]]["identity"]
            check(all(r["op"][k] == v for k, v in ident.items()), "Worker identity")
        native = {r["op"]["operation_id"]: r for r in rows if r["kind"] == "native_effect_attempt"}
        results = [r for r in rows if r["kind"] == "native_effect_result"]
        observed = [r for r in results if r["success"] or r["after_sha256"] != native[r["op"]["operation_id"]]["before_sha256"]]
        def members(seq, root):
            return {oid for oid, r in starts.items() if r["seq"] < seq and r["op"]["origin_key"] == root}
        def live(seq, root):
            return sorted(oid for oid in members(seq, root) if ends[oid]["seq"] >= seq)
        inventories = {r["inventory_id"]: r for r in rows if r["kind"] == "scope_inventory"}
        scored = stored["outcomes"]["confirmation"]
        claims = [r for r in rows if r["kind"] == "scope_confirmation"]
        check(len(claims) == len(scored["claims"]), "Claim count")
        for claim, result in zip(claims, scored["claims"]):
            inv = inventories[claim["inventory_id"]]
            body = {k: inv[k] for k in ("inventory_id", "version", "root", "service_id", "members", "policy")}
            check(digest(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()) == inv["sha256"] == claim["inventory_sha256"], "Inventory hash")
            supplied = {m["operation_id"] for m in inv["members"]}
            missing = sorted(members(inv["seq"], old)-supplied)
            complete = supplied == members(inv["seq"], old)
            check(missing == result["inventory"]["missing_operation_ids"] and complete == result["inventory"]["inventory_complete"], "Inventory completeness")
            check(live(claim["seq"], old) == result["live_old_callers_at_claim"]
                  and live(claim["seq"], independent) == result["independent_live_callers_at_claim"], "Claim liveness")
            later = [r["op"]["operation_id"] for r in observed
                     if r["op"]["origin_key"] == old and native[r["op"]["operation_id"]]["seq"] > claim["seq"]]
            check(later == result["old_root_effects_after_claim"], "Postclaim effects")
            policies = [r for r in rows if r["kind"] == "scope_policy_activated" and r["seq"] < claim["seq"]]
            p = policies[-1]["policy"]
            gated = p["kind"] == "origin" and p["root"] == old and p["admission"] and p["effect"]
            state_match = all(m["finished"] == (m["operation_id"] not in live(inv["seq"], old)) for m in inv["members"])
            support = complete and state_match and not live(claim["seq"], old)
            if claim["claim_scope"] == "file_effects_closed": support = support and gated and not later
            else: support = support and not (set(later) & supplied)
            check(result["issued_claim_supported"] == (bool(support) if claim["status"] == "issued" else None), "Claim support")
            counts["claims_checked"] += 1
            counts["unsupported_issued_claims"] += int(claim["status"] == "issued" and not support)
        drains = [r for r in rows if r["kind"] == "scoped_drain_receipt"]
        for receipt, result in zip(drains, scored["drains"]):
            inv = inventories[receipt["final_inventory_id"]]
            supplied = {m["operation_id"] for m in inv["members"]}
            support = supplied == members(inv["seq"], old) and not live(receipt["seq"], old)
            check(result["completion_supported"] == support, "Drain support")
            check(result["live_old_callers_at_receipt"] == live(receipt["seq"], old), "Drain liveness")
            counts["drains_checked"] += 1
        final = next(r for r in rows if r["kind"] == "observer_inventory" and r["phase"] == "final")["files"]
        actual = {str(p.relative_to(folder)): digest(p.read_bytes()) for p in (folder/"files").rglob("*") if p.is_file()}
        recorded = {f["path"]: f["sha256"] for f in final}
        check(actual == recorded, "Disk inventory mismatch")
        check(all(digest(f["content"].encode()) == f["sha256"] for f in final), "Recorded byte hashes")
        counts["disk_files_rehashed"] += len(actual)
        counts["native_callers_closed"] += len(starts)
        counts["native_file_effects"] += len(observed)
        counts["conditions"] += 1
        cases.append(dict(condition=name, claims=len(claims), drains=len(drains),
                          events_sha256=digest((folder/"events.jsonl").read_bytes()), disk_files=len(actual)))
    return dict(status="passed", counts=dict(counts), conditions=cases,
                scorer_imported=False, harness_imported=False, independent_human_review=False,
                provider_calls=0, catalogue_cases_certified=0)


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--write", action="store_true")
    args = p.parse_args(); result = build(); dest = ROOT/"RAW_CONFIRMATION_CROSSCHECK.json"
    if args.write:
        with dest.open("x") as f: json.dump(result, f, indent=2)
    elif dest.exists(): check(json.loads(dest.read_text()) == result, "Saved crosscheck differs")
    print(json.dumps({"status": result["status"], "counts": result["counts"]}, indent=2))


if __name__ == "__main__": main()
