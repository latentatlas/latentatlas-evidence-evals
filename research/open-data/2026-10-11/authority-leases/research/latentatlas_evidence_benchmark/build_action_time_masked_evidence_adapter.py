#!/usr/bin/env python3
"""Merge safe masked evidence sidecars into action-time review packet V2.

The adapter never reads the internal review index, never asks for raw source
content, never calls external services, and never mutates production truth.
Without a sidecar, it generates a source-side template and reports the current
V2 insufficiency as a measurable state.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_V2_QUEUE = Path("outputs/latentatlas/action_time_review_packet_v2/action_time_review_packet_v2_queue.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_masked_evidence_adapter")

MISSING_IN_V1 = "not_available_in_v1_source"
ADAPTER_SCHEMA = "latentatlas_action_time_masked_evidence_adapter_v1"

REQUIRED_EVIDENCE_FIELDS = [
    "masked_state_before",
    "masked_state_after",
    "observed_change_type",
    "lease_validity_relationship",
    "pdp_temporal_authority_evidence",
    "decision_causal_link",
    "reviewer_visible_insufficiency_marker",
    "reviewer_visible_contradiction_marker",
]
OUTCOME_REVIEW_FIELDS = [
    "outcome_reviewer_id_hash",
    "outcome_reviewed_at",
    "reviewed_outcome",
    "outcome_confidence",
    "outcome_adjudication_status",
    "outcome_notes_code",
]

ALLOWED_SIDECAR_FIELDS = {
    "queue_id",
    "event_id",
    "evidence_adapter_version",
    "evidence_provenance_hash",
    "adapter_notes_code",
    *REQUIRED_EVIDENCE_FIELDS,
}

FORBIDDEN_KEYS = {
    "availability",
    "body",
    "canonical_title_v2",
    "condition",
    "customer_email",
    "customer_name",
    "email_body",
    "message",
    "message_body",
    "personal_data",
    "price",
    "prompt",
    "raw_content",
    "raw_customer_data",
    "raw_email",
    "raw_message",
    "raw_payload",
    "raw_text",
    "seller",
    "sensitive_data",
    "source_product_url",
    "tenant_payload",
    "text",
    "title",
    "transcript",
    "unmasked_content",
    "url",
}
FORBIDDEN_VALUE_PATTERN = re.compile(r"https?://|www\\.", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def string_value(value: Any) -> str:
    return str(value or "").strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_sidecar(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append({key: string_value(value) for key, value in json.loads(line).items()})
    return rows


def forbidden_findings(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}" if path else key_text
            if key_text.lower() in FORBIDDEN_KEYS:
                findings.append(child_path)
            findings.extend(forbidden_findings(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(forbidden_findings(child, f"{path}[{index}]"))
    elif isinstance(value, str) and FORBIDDEN_VALUE_PATTERN.search(value):
        findings.append(path or "<value>")
    return sorted(set(findings))


def validate_sidecar_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    unexpected_fields: list[str] = []
    missing_keys: list[int] = []
    duplicate_keys: list[str] = []
    keys_seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        for field in row:
            if field not in ALLOWED_SIDECAR_FIELDS:
                unexpected_fields.append(f"row_{index}.{field}")
        key = string_value(row.get("queue_id")) or string_value(row.get("event_id"))
        if not key:
            missing_keys.append(index)
        elif key in keys_seen:
            duplicate_keys.append(key)
        keys_seen.add(key)
    leak_findings = forbidden_findings(rows)
    findings = {
        "unexpected_fields": sorted(set(unexpected_fields)),
        "missing_key_rows": missing_keys,
        "duplicate_keys": sorted(set(duplicate_keys)),
        "forbidden_key_or_url_findings": leak_findings,
    }
    finding_count = sum(len(value) for value in findings.values())
    return {
        "status": "pass" if finding_count == 0 else "fail",
        "finding_count": finding_count,
        **findings,
    }


def sidecar_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        queue_id = string_value(row.get("queue_id"))
        event_id = string_value(row.get("event_id"))
        if queue_id:
            indexed[f"queue:{queue_id}"] = row
        if event_id:
            indexed[f"event:{event_id}"] = row
    return indexed


def required_values_from_sidecar(row: dict[str, str]) -> dict[str, str]:
    return {field: string_value(row.get(field)) for field in REQUIRED_EVIDENCE_FIELDS}


def evidence_sufficiency(evidence: dict[str, str]) -> dict[str, Any]:
    missing_fields = [
        field
        for field in REQUIRED_EVIDENCE_FIELDS
        if not string_value(evidence.get(field)) or evidence.get(field) == MISSING_IN_V1
    ]
    insufficiency_marker = string_value(evidence.get("reviewer_visible_insufficiency_marker")).lower()
    insufficiency_visible = bool(insufficiency_marker) and insufficiency_marker not in {
        "none",
        "no_insufficiency_observed",
    }
    label = (
        "sufficient_for_outcome_adjudication"
        if not missing_fields and not insufficiency_visible
        else "insufficient_for_outcome_adjudication"
    )
    return {
        "packet_sufficiency_label": label,
        "outcome_adjudication_allowed": label == "sufficient_for_outcome_adjudication",
        "missing_outcome_evidence_fields": missing_fields,
        "recommended_outcome_if_reviewed_now": "needs_more_evidence" if missing_fields or insufficiency_visible else "",
    }


def merge_sidecar(row: dict[str, Any], sidecar: dict[str, str] | None) -> tuple[dict[str, Any], bool]:
    merged = json.loads(json.dumps(row))
    packet = merged["reviewer_packet"]
    if not sidecar:
        packet["outcome_evidence"] = {field: MISSING_IN_V1 for field in REQUIRED_EVIDENCE_FIELDS}
        packet["packet_sufficiency"] = evidence_sufficiency(packet["outcome_evidence"])
        packet["masked_evidence_adapter"] = {
            "schema": ADAPTER_SCHEMA,
            "status": "not_provided",
            "evidence_adapter_version": "",
            "evidence_provenance_hash": "",
            "adapter_notes_code": "awaiting_masked_evidence_sidecar",
        }
        return merged, False

    evidence = required_values_from_sidecar(sidecar)
    packet["outcome_evidence"] = {
        field: evidence[field] if evidence[field] else MISSING_IN_V1
        for field in REQUIRED_EVIDENCE_FIELDS
    }
    packet["packet_sufficiency"] = evidence_sufficiency(packet["outcome_evidence"])
    packet["masked_evidence_adapter"] = {
        "schema": ADAPTER_SCHEMA,
        "status": "merged",
        "evidence_adapter_version": string_value(sidecar.get("evidence_adapter_version")),
        "evidence_provenance_hash": string_value(sidecar.get("evidence_provenance_hash")),
        "adapter_notes_code": string_value(sidecar.get("adapter_notes_code")) or "merged_masked_evidence",
    }
    return merged, True


def template_row(row: dict[str, Any]) -> dict[str, str]:
    packet = row["reviewer_packet"]
    base = {
        "queue_id": string_value(row.get("queue_id")),
        "event_id": string_value(packet.get("event_id")),
        "evidence_adapter_version": ADAPTER_SCHEMA,
        "evidence_provenance_hash": "",
        "adapter_notes_code": "",
    }
    base.update({field: "" for field in REQUIRED_EVIDENCE_FIELDS})
    return base


def write_template(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["queue_id", "event_id", "evidence_adapter_version", "evidence_provenance_hash", "adapter_notes_code"]
    fieldnames.extend(REQUIRED_EVIDENCE_FIELDS)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(template_row(row))


def reviewer_sheet_row(row: dict[str, Any]) -> dict[str, Any]:
    packet = row["reviewer_packet"]
    evidence = packet["outcome_evidence"]
    sufficiency = packet["packet_sufficiency"]
    adapter = packet.get("masked_evidence_adapter", {})
    return {
        "queue_id": row["queue_id"],
        "priority_rank": row["priority_rank"],
        "priority_band": row["priority_band"],
        "event_id": packet["event_id"],
        "action_type": packet["action_type"],
        "execution_verdict": packet["execution_verdict"],
        "signal_claimed_change_type": packet["signal_claimed_change_type"],
        **evidence,
        "adapter_status": adapter.get("status", ""),
        "adapter_notes_code": adapter.get("adapter_notes_code", ""),
        "packet_sufficiency_label": sufficiency["packet_sufficiency_label"],
        "outcome_adjudication_allowed": sufficiency["outcome_adjudication_allowed"],
        "missing_outcome_evidence_fields": "|".join(sufficiency["missing_outcome_evidence_fields"]),
        "recommended_outcome_if_reviewed_now": sufficiency["recommended_outcome_if_reviewed_now"],
        **{field: "" for field in OUTCOME_REVIEW_FIELDS},
    }


def write_reviewer_sheet(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(reviewer_sheet_row(rows[0]).keys()) if rows else ["queue_id"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(reviewer_sheet_row(row))


def summarize(
    rows: list[dict[str, Any]],
    *,
    sidecar_rows: list[dict[str, str]],
    validation: dict[str, Any],
    merged_count: int,
) -> dict[str, Any]:
    sufficiency_counts = Counter(
        row["reviewer_packet"]["packet_sufficiency"]["packet_sufficiency_label"] for row in rows
    )
    adapter_counts = Counter(
        row["reviewer_packet"].get("masked_evidence_adapter", {}).get("status", "unknown")
        for row in rows
    )
    allowed_count = sum(
        1 for row in rows if row["reviewer_packet"]["packet_sufficiency"]["outcome_adjudication_allowed"]
    )
    missing_counter: Counter[str] = Counter()
    for row in rows:
        missing_counter.update(row["reviewer_packet"]["packet_sufficiency"]["missing_outcome_evidence_fields"])
    status = "pass" if validation["status"] == "pass" else "fail"
    return {
        "generated_at": utc_now(),
        "mode": "latentatlas_action_time_masked_evidence_adapter",
        "status": status,
        "adapter_status": "merged_sidecar" if sidecar_rows and status == "pass" else "template_generated",
        "input_v2_packet_count": len(rows),
        "p0_packet_count": sum(1 for row in rows if row.get("priority_band") == "P0"),
        "sidecar_row_count": len(sidecar_rows),
        "merged_packet_count": merged_count,
        "packet_sufficiency_counts": dict(sorted(sufficiency_counts.items())),
        "adapter_status_counts": dict(sorted(adapter_counts.items())),
        "outcome_adjudication_allowed_count": allowed_count,
        "outcome_adjudication_blocked_count": len(rows) - allowed_count,
        "missing_outcome_evidence_field_counts": dict(sorted(missing_counter.items())),
        "sidecar_validation": validation,
        "internal_index_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "claim_boundary": {
            "allowed_claim": "Masked evidence sidecar readiness or merge status was measured.",
            "not_claimed": "The adapter does not prove outcomes unless sufficient masked evidence is present.",
        },
    }


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# LatentAtlas Action-Time Masked Evidence Adapter",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "## Boundary",
        "",
        "This adapter merges only allowed masked evidence sidecar fields into V2 review packets. It does not read the internal index, call external services, execute actions, or mutate production truth.",
        "",
        "## Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- adapter status: `{summary['adapter_status']}`",
        f"- input V2 packets: `{summary['input_v2_packet_count']}`",
        f"- P0 packets: `{summary['p0_packet_count']}`",
        f"- sidecar rows: `{summary['sidecar_row_count']}`",
        f"- merged packets: `{summary['merged_packet_count']}`",
        f"- outcome-adjudication allowed: `{summary['outcome_adjudication_allowed_count']}`",
        f"- outcome-adjudication blocked: `{summary['outcome_adjudication_blocked_count']}`",
        f"- sidecar validation: `{summary['sidecar_validation']['status']}`",
        "",
        "## Packet Sufficiency Counts",
        "",
    ]
    for label, count in summary["packet_sufficiency_counts"].items():
        lines.append(f"- `{label}`: `{count}`")
    lines.extend(["", "## Missing Outcome-Evidence Fields", ""])
    for field, count in summary["missing_outcome_evidence_field_counts"].items():
        lines.append(f"- `{field}`: `{count}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- allowed: {summary['claim_boundary']['allowed_claim']}",
            f"- not claimed: {summary['claim_boundary']['not_claimed']}",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    v2_queue_path: Path = DEFAULT_V2_QUEUE,
    out_dir: Path = DEFAULT_OUT_DIR,
    sidecar_path: Path | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "merged_queue": out_dir / "action_time_masked_evidence_merged_v2_queue.jsonl",
        "reviewer_sheet": out_dir / "action_time_masked_evidence_reviewer_sheet.csv",
        "reviewer_sheet_p0": out_dir / "action_time_masked_evidence_reviewer_sheet_p0.csv",
        "sidecar_template": out_dir / "action_time_masked_evidence_sidecar_template.csv",
        "sidecar_template_p0": out_dir / "action_time_masked_evidence_sidecar_template_p0.csv",
        "summary": out_dir / "action_time_masked_evidence_adapter_summary.json",
        "manifest": out_dir / "action_time_masked_evidence_adapter_manifest.json",
        "report": out_dir / "action_time_masked_evidence_adapter_report.md",
    }
    if not v2_queue_path.exists():
        manifest = {
            "generated_at": utc_now(),
            "mode": "latentatlas_action_time_masked_evidence_adapter",
            "status": "blocked",
            "failure_reason": "missing_v2_queue",
            "input": str(v2_queue_path),
            "internal_index_read": False,
            "external_calls_used_by_builder": False,
            "production_truth_mutation": False,
        }
        write_json(paths["manifest"], manifest)
        return manifest

    rows = read_jsonl(v2_queue_path)
    sidecar_rows = read_sidecar(sidecar_path) if sidecar_path else []
    validation = validate_sidecar_rows(sidecar_rows)
    index = sidecar_index(sidecar_rows) if validation["status"] == "pass" else {}
    merged_rows: list[dict[str, Any]] = []
    merged_count = 0
    for row in rows:
        packet = row["reviewer_packet"]
        sidecar = index.get(f"queue:{row['queue_id']}") or index.get(f"event:{packet['event_id']}")
        merged, did_merge = merge_sidecar(row, sidecar)
        merged_rows.append(merged)
        if did_merge:
            merged_count += 1

    summary = summarize(merged_rows, sidecar_rows=sidecar_rows, validation=validation, merged_count=merged_count)
    summary["input"] = str(v2_queue_path)
    summary["sidecar"] = str(sidecar_path) if sidecar_path else ""
    summary["outputs"] = {name: str(path) for name, path in paths.items()}

    write_jsonl(paths["merged_queue"], merged_rows)
    write_reviewer_sheet(paths["reviewer_sheet"], merged_rows)
    write_reviewer_sheet(paths["reviewer_sheet_p0"], [row for row in merged_rows if row["priority_band"] == "P0"])
    write_template(paths["sidecar_template"], rows)
    write_template(paths["sidecar_template_p0"], [row for row in rows if row["priority_band"] == "P0"])
    write_json(paths["summary"], summary)
    paths["report"].write_text(build_report(summary), encoding="utf-8")
    manifest = {
        "generated_at": summary["generated_at"],
        "mode": summary["mode"],
        "status": summary["status"],
        "adapter_status": summary["adapter_status"],
        "input": str(v2_queue_path),
        "sidecar": str(sidecar_path) if sidecar_path else "",
        "summary": str(paths["summary"]),
        "report": str(paths["report"]),
        "sidecar_template": str(paths["sidecar_template"]),
        "internal_index_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "packet_sufficiency_counts": summary["packet_sufficiency_counts"],
        "outcome_adjudication_allowed_count": summary["outcome_adjudication_allowed_count"],
        "outputs": summary["outputs"],
    }
    write_json(paths["manifest"], manifest)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v2-queue", type=Path, default=DEFAULT_V2_QUEUE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sidecar", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.v2_queue, args.out_dir, args.sidecar)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
