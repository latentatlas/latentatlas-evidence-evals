"""Independent FIFO replay. Decisions are observed; policy success is scored."""
from copy import deepcopy
import json
import sys
from contract import LAB, require


def validate_queue(e):
    rows = e["rows"]
    def many(kind):
        return [r for r in rows if r["kind"] == kind]
    def one(kind):
        found = many(kind)
        require(len(found) == 1, "Expected one " + kind)
        return found[0]
    service = one("shared_file_service_created")["service_id"]
    start, exit_row, close = [one(k) for k in ("queue_consumer_started", "queue_consumer_exited", "queue_closed")]
    require(start["service_id"] == exit_row["service_id"] == close["service_id"] == service and start["worker_ident"] == exit_row["worker_ident"], "Queue consumer identity changed")
    require(start["seq"] < exit_row["seq"] < close["seq"] < one("measurement_closed")["seq"] and close["worker_joined"], "Consumer closure/order")
    ops = {x["op"]["operation_id"]: x for x in e["effects"]}
    admitted, admission, denied, terminal, claimed = {}, {}, {}, {}, {}
    waiting, active, states = [], None, {}
    checkpoint = None
    phases = {}
    policy = {"kind": "open", "root": None, "thread": None, "admission": False, "effect": False}
    decisions = []
    def snapshot():
        return {"service_id": service, "active": deepcopy(admitted[active]["op"]) if active else None,
                "waiting": [deepcopy(admitted[oid]["op"]) for oid in waiting], "states": dict(states)}
    for r in rows:
        kind = r["kind"]
        if kind in {"queue_admission_check", "queue_admission_denied", "queue_accepted", "queue_claimed", "queue_job_terminal", "receiver_check", "queue_effect_completed", "queue_after_effect_held"}:
            op = r["op"]; oid = op["operation_id"]
            require(oid in ops and op == ops[oid]["op"], "Queue operation attribution mismatch")
            if "service_id" in r:
                require(r["service_id"] == service, "Foreign queue service")
        if kind == "scope_policy_activated":
            require(r["queue"] == snapshot(), "Activation snapshot differs from replay")
            policy = r["policy"]
        elif kind in {"queue_admission_check", "receiver_check"}:
            require(r["policy"] == policy and type(r["allowed"]) is bool, "Unlogged queue policy/decision")
            decisions.append(r)
            if kind == "queue_admission_check":
                require(oid not in admission, "Duplicate admission decision")
                admission[oid] = r
            else:
                require(active == oid and r["worker_ident"] == start["worker_ident"], "Effect outside sole FIFO consumer")
        elif kind == "queue_admission_denied":
            require(oid in admission and not admission[oid]["allowed"] and oid not in denied and oid not in admitted, "Inconsistent admission denial")
            denied[oid] = r
        elif kind == "queue_accepted":
            require(oid in admission and admission[oid]["allowed"] and oid not in admitted and oid not in denied, "Inconsistent queue acceptance")
            admitted[oid] = r; waiting.append(oid); states[oid] = "waiting"
            require(r["waiting_ids"] == waiting, "FIFO pending receipt mismatch")
        elif kind == "queue_claimed":
            require(active is None and waiting and waiting[0] == oid and oid not in claimed, "FIFO claim order/concurrent consumer")
            require(r["worker_ident"] == start["worker_ident"], "Second queue consumer")
            waiting.pop(0); active = oid; states[oid] = "claimed"; claimed[oid] = r
        elif kind == "native_effect_attempt":
            require(active == r["op"]["operation_id"], "Native effect bypassed FIFO")
        elif kind == "queue_job_terminal":
            require(oid in admitted and oid not in terminal, "Duplicate/orphan terminal")
            if r["state"] == "cancelled":
                require(oid == active or oid in waiting, "Deadline target missing")
                if oid in waiting: waiting.remove(oid)
            else:
                require(active == oid, "Terminal outside claimed work")
            states[oid] = r["state"]; terminal[oid] = r
            if active == oid: active = None
        elif kind == "intervention_checkpoint":
            require(r["queue"] == snapshot(), "Checkpoint queue snapshot mismatch")
            require(r["order"] == e["result"]["order"] == "O_first" and r["schedule"] == e["result"]["schedule"] == "before_effect"
                    and r["admission_phase"] == e["result"]["admission_phase"], "Checkpoint condition differs")
            target_ids = {role: op["operation_id"] for role, op in r["ops"].items()}
            require(set(target_ids) == {"O", "I"} and all(oid in ops and r["ops"][role] == ops[oid]["op"]
                    and e["role_of"][ops[oid]["op"]["key"]] == role for role, oid in target_ids.items()), "Checkpoint jobs differ")
            old_id, iid = target_ids["O"], target_ids["I"]
            require(active == old_id and claimed[active]["held"] and states[active] == "claimed",
                    "O is not held before its effect")
            independent_ids = {oid for oid in admission if e["role_of"][ops[oid]["op"]["key"]] == "I"}
            if r["admission_phase"] == "before_I_admission":
                require(not waiting and not independent_ids and iid not in admitted,
                        "I admission occurred before its declared checkpoint")
                phases = {"O": "claimed_pre_effect", "I": "proposed_unadmitted"}
            else:
                require(waiting == [iid] and independent_ids == {iid} and states[iid] == "waiting",
                        "I first mutation is not accepted and waiting")
                phases = {"O": "claimed_pre_effect", "I": "accepted_waiting"}
            checkpoint = deepcopy(r["ops"])
        elif kind == "source_observation_complete":
            require(r["queue"] == snapshot(), "Source observation/FIFO mismatch")
            old_id, iid = (e["targets"][role]["op"]["operation_id"] for role in ("O", "I"))
            require(old_id in admitted and r["old_worker_still_pending"] == (old_id not in terminal),
                    "Old pending Future report differs")
            require(r["independent_admission_observed"] == (iid in admitted)
                    and r["independent_queue_future_pending"] == ((iid not in terminal) if iid in admitted else None),
                    "Unadmitted I was confused with a pending queue Future")
        elif kind == "queue_closed":
            require(r["snapshot"] == snapshot() and active is None and not waiting, "Queue close not reconciled")
    require(set(admission) == set(ops) and set(admitted) | set(denied) == set(ops) and not set(admitted) & set(denied), "Not all mutations admitted or denied")
    require(set(terminal) == set(admitted), "Unsettled admitted jobs")
    for oid, x in ops.items():
        if oid in denied:
            require(x["admission_denied"] and not x["attempt"] and not x["receiver_denied"], "Admission rejection produced an effect")
        else:
            require(not x["admission_denied"] and terminal[oid]["seq"] < x["worker_finished"]["seq"], "Queue/caller closure mismatch")
            if x["success"]: require(terminal[oid]["state"] == "committed", "Successful effect not committed")
            if x["receiver_denied"]: require(terminal[oid]["state"] == "denied", "Receiver denial mislabeled")
    if checkpoint:
        released = one("queue_barrier_released")
        require(e["boundary"]["seq"] < e["effective"]["seq"] < released["seq"], "Gate outside held FIFO window")
        for role, op in checkpoint.items():
            oid = op["operation_id"]; effect = ops[oid]
            release = next(r for r in rows if r["kind"] == "queue_candidate_released" and r["role"] == role)
            before_admission = role == "I" and e["result"]["admission_phase"] == "before_I_admission"
            if before_admission:
                require(e["effective"]["seq"] < release["seq"] < admission[oid]["seq"],
                        "I first admission decision did not follow release and policy")
            else:
                require(release["seq"] < admitted[oid]["seq"] < e["boundary"]["seq"],
                        "Target admission not before checkpoint")
            if effect["attempt"]:
                require(released["seq"] < effect["attempt"]["seq"], "Effect before final release")
            if oid in terminal:
                require(released["seq"] < terminal[oid]["seq"], "Admitted target settled before release")
        require(one("shared_file_service_created")["schedule"] == e["result"]["schedule"], "Service timing differs")
        require(not any(many(k) for k in ("queue_advance_to_after_effect", "queue_effect_completed",
                                          "queue_after_effect_held", "queue_reply_barrier_timeout")),
                "Unexpected native-effect timing schedule")
    return {"admitted": admitted, "admission_denied": denied, "terminal": terminal,
            "admission_decisions": admission, "decisions": decisions, "checkpoint": checkpoint, "checkpoint_phases": phases, "consumer_count": 1}


def score_queue(e):
    sys.path.append(str(LAB / "stop_contract_study"))
    import workload
    from mutation_scoring import content_score
    q = e["queue"]
    held = []
    for role, op in (q["checkpoint"] or {}).items():
        role = e["role_of"][op["key"]]
        source = next(s for (thread, job), s in e["sources"].items() if thread == op["thread_id"] and job == e["result"]["roles"][role]["job_id"])
        job = json.loads(source["content"])
        effect = next(x for x in e["effects"] if x["op"]["operation_id"] == op["operation_id"])
        text = effect["request_snapshot"]["projection"].get("candidate_content")
        proposed = content_score(text, job)
        classification = proposed["class"]
        held.append({"role": role, "phase": q["checkpoint_phases"][role], "operation_id": op["operation_id"],
                     "native_effect_completed_before_checkpoint": bool(effect["result"] and effect["result"]["seq"] < e["boundary"]["seq"]),
                     "content_class": classification, "proposed": proposed,
                     "candidate_sha256": effect["request_snapshot"]["projection"].get("candidate_sha256"),
                     "request_basis_sha256": effect["request_snapshot"]["before_sha256"],
                     "path": op["virtual_path"], "call_id": op["call_id"]})
    mismatches = []
    for d in q["decisions"]:
        p, op = d["policy"], d["op"]
        targeted = p["kind"] == "service" or (p["kind"] == "thread" and p["thread"] == op["thread_id"]) or (p["kind"] == "origin" and p["root"] == op["origin_key"])
        phase = "admission" if d["kind"] == "queue_admission_check" else "effect"
        expected = not (p[phase] and targeted)
        if d["allowed"] != expected:
            mismatches.append({"seq": d["seq"], "operation_id": op["operation_id"], "phase": phase})
    return {"consumer_count": q["consumer_count"], "accepted_mutations": len(q["admitted"]),
            "admission_denials": len(q["admission_denied"]),
            "accepted_but_effect_denied": sum(x["receiver_denied"] for x in e["effects"]),
            "checkpoint_target_effects": held,
            "independent_new_effect_opportunity": None if not held else True,
            "independent_accepted_unfinished_at_intervention": None if not held else q["checkpoint_phases"]["I"] == "accepted_waiting",
            "independent_reference_interpretation": q["checkpoint_phases"].get("I", "not_reached"),
            "checkpoint_content_status": "not_reached" if not held else "O_final_I_partial" if {x["role"]: x["content_class"] for x in held} == {"O": "final", "I": "partial"} else "other_content",
            "checkpoint_timings": checkpoint_timings(e),
            "policy_decision_mismatches": mismatches, "policy_decisions_match_declared_contract": not mismatches}


def checkpoint_timings(e):
    """Measured scheduling intervals, never an estimate of production cost."""
    rows, q = e["rows"], e["queue"]
    def elapsed(start, end):
        return None if start is None or end is None else (end["monotonic_ns"]-start["monotonic_ns"])/1_000_000
    output = {}
    for role, effect in e["targets"].items():
        oid = effect["op"]["operation_id"]
        ready = next(r for r in rows if r["kind"] == "queue_candidate_ready" and r["role"] == role)
        release = next(r for r in rows if r["kind"] == "queue_candidate_released" and r["role"] == role)
        admitted = q["admitted"].get(oid)
        decision = q["admission_decisions"][oid]
        receiver = next((r for r in rows if r["kind"] == "receiver_check" and r["op"]["operation_id"] == oid), None)
        output[role] = {
            "operation_id": oid,
            "first_mutation": role == "I",
            "admission_phase_at_checkpoint": q["checkpoint_phases"][role],
            "admission_allowed": decision["allowed"],
            "admission_after_policy": decision["seq"] > e["effective"]["seq"],
            "admission_denied": effect["admission_denied"],
            "effect_denied": effect["receiver_denied"],
            "scheduling_hold_ms": elapsed(ready, release),
            "release_to_admission_decision_ms": elapsed(release, decision),
            "accepted_to_receiver_check_ms": elapsed(admitted, receiver),
            "native_callback_interval_ms": elapsed(effect["attempt"], effect["result"]),
            "request_to_worker_closed_ms": elapsed(effect["request_snapshot"], effect["worker_finished"]),
        }
    return output
