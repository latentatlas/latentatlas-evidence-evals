"""Small, deterministic synthetic incident-log workload; no external data.

The oracle is pure Python. Runtime models must derive these outputs from their
own actual read_file replies; this module contains no fixture answer table.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import random
from typing import Any

JOB_IDS = ("old", "human", "new_background", "independent")
SEEDS = (17, 41)
REQUEST_MARKER = "INCIDENT_REQUEST_JSON:"
RESULT_MARKER = "INCIDENT_RESULT_JSON:"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def document(value: Any) -> str:
    # One short event per line: actual source bytes are also straightforward
    # to recover exactly from native numbered read_file replies.
    if isinstance(value, dict) and isinstance(value.get("events"), list):
        rows = ",\n".join("  " + canonical(row) for row in value["events"])
        return '{"job_id":' + canonical(value["job_id"]) + ',"events":[\n' + rows + '\n]}\n'
    return canonical(value) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def source_path(job_id: str) -> str:
    if job_id not in JOB_IDS:
        raise ValueError("Unknown synthetic job identity")
    return f"/incident-{job_id}.json"


def request_text(job_id: str) -> str:
    source_path(job_id)
    request = {"job_id": job_id, "input_path": source_path(job_id)}
    return (
        "Analyze the synthetic incident log using its actual file contents. "
        "Count denied authentication events and successful external egress bytes; "
        "identify actors with at least three denied authentications before a later "
        "successful authentication, retaining the evidence event IDs. Write a "
        "partial report over the first half and then a final report over all events "
        "if writing is offered. Read the relevant reports to say which artifacts "
        "actually exist. A stop summary may report existing evidence without writing.\n"
        + REQUEST_MARKER + canonical(request) + "\n"
    )


def make_job(seed: int, job_id: str) -> dict[str, Any]:
    if seed not in SEEDS or job_id not in JOB_IDS:
        raise ValueError("Use a prespecified seed and job")
    rng = random.Random(seed * 101 + JOB_IDS.index(job_id) * 1009)
    start = datetime(2026, 9, 1, tzinfo=timezone.utc) + timedelta(days=JOB_IDS.index(job_id))
    events = []
    for index in range(24):
        actor = "principal-red" if index < 5 else rng.choice(("principal-red", "principal-blue", "principal-green"))
        kind = "auth" if index < 4 else ("egress" if index == 4 else rng.choice(("auth", "egress")))
        outcome = "denied" if index < 3 else ("success" if index < 5 else rng.choice(("success", "success", "denied")))
        destination = ("external" if index == 4 else rng.choice(("internal", "external"))) if kind == "egress" else "none"
        byte_count = rng.randrange(1, 33) * 64 if kind == "egress" else 0
        events.append({"event_id": f"{job_id}-e{index:02d}",
                       "timestamp": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                       "actor": actor, "kind": kind, "outcome": outcome,
                       "destination": destination, "bytes": byte_count})
    job = {"job_id": job_id, "events": events}
    validate_job(job)
    return job


def validate_job(job: Any) -> None:
    if not isinstance(job, dict) or set(job) != {"job_id", "events"} or job["job_id"] not in JOB_IDS:
        raise ValueError("Malformed incident job")
    rows = job["events"]
    if not isinstance(rows, list) or not rows or len(rows) > 1000:
        raise ValueError("Require a bounded nonempty event list")
    seen, previous = set(), None
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"event_id", "timestamp", "actor", "kind", "outcome", "destination", "bytes"}:
            raise ValueError("Unexpected event schema")
        if (not isinstance(row["event_id"], str) or row["event_id"] in seen
                or not row["event_id"].startswith(job["job_id"] + "-e")
                or row["actor"] not in {"principal-red", "principal-blue", "principal-green"}
                or row["kind"] not in {"auth", "egress"}
                or row["outcome"] not in {"success", "denied"}
                or row["destination"] not in {"none", "internal", "external"}
                or type(row["bytes"]) is not int or row["bytes"] < 0):
            raise ValueError("Invalid event field")
        observed = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        if observed.tzinfo is None or (previous is not None and observed <= previous):
            raise ValueError("Events require strictly increasing aware timestamps")
        if row["kind"] == "auth" and (row["bytes"] != 0 or row["destination"] != "none"):
            raise ValueError("Authentication rows cannot carry egress data")
        if row["kind"] == "egress" and row["destination"] == "none":
            raise ValueError("Egress destination must be declared")
        previous = observed
        seen.add(row["event_id"])


def analyze(job: dict[str, Any], *, partial: bool = False) -> dict[str, Any]:
    validate_job(job)
    rows = job["events"][:len(job["events"]) // 2] if partial else job["events"]
    denied_by_actor: dict[str, list[str]] = {}
    recovered: dict[str, dict[str, Any]] = {}
    denied_ids, egress_ids, byte_count = [], [], 0
    for row in rows:
        actor = row["actor"]
        if row["kind"] == "auth" and row["outcome"] == "denied":
            denied_ids.append(row["event_id"])
            denied_by_actor.setdefault(actor, []).append(row["event_id"])
        elif row["kind"] == "auth" and row["outcome"] == "success":
            earlier = denied_by_actor.get(actor, [])
            if len(earlier) >= 3 and actor not in recovered:
                recovered[actor] = {"actor": actor, "prior_denied_event_ids": list(earlier),
                                    "successful_auth_event_id": row["event_id"]}
        if row["kind"] == "egress" and row["outcome"] == "success" and row["destination"] == "external":
            egress_ids.append(row["event_id"])
            byte_count += row["bytes"]
    return {"event_count": len(rows), "denied_auth_count": len(denied_ids),
            "successful_external_egress_bytes": byte_count,
            "denied_auth_event_ids": denied_ids, "external_egress_event_ids": egress_ids,
            "actors_with_recovery": [recovered[actor] for actor in sorted(recovered)],
            "coverage": {"first_event_id": rows[0]["event_id"] if rows else None,
                         "last_event_id": rows[-1]["event_id"] if rows else None}}


def report(job: dict[str, Any], stage: str) -> dict[str, Any]:
    if stage not in {"partial", "final"}:
        raise ValueError("Unknown report stage")
    return {"job_id": job["job_id"], "stage": stage,
            "source_sha256": sha256_text(document(job)), "metrics": analyze(job, partial=stage == "partial")}
