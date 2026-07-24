"""Customer packet schema validation for LatentAtlas."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .evidence_guard import (
    ALLOWED_SOURCE_TYPES,
    CONSENSUS_REQUIRED_AXES,
    input_hash,
    normalize_metadata_list,
    parse_metadata_date,
)


SCHEMA_VERSION = "latentatlas_customer_packet_schema_v0"

PACKET_REQUIRED_FIELDS = {"decision_id", "query_or_claim", "candidate_evidence", "policy", "domain_context"}
PACKET_ALLOWED_FIELDS = PACKET_REQUIRED_FIELDS
EVIDENCE_REQUIRED_FIELDS = {"evidence_id", "text", "source_type", "source_uri", "retrieval_score", "metadata"}
EVIDENCE_ALLOWED_FIELDS = EVIDENCE_REQUIRED_FIELDS
METADATA_REQUIRED_FIELDS = {
    "owner",
    "source_status",
    "source_authority",
    "review_state",
    "effective_state",
    "source_family",
    "origin_id",
    "published_at",
    "effective_from",
    "effective_to",
    "as_of_date",
    "support_axes",
}

SOURCE_STATUSES = {"approved", "draft", "archived", "deprecated", "retired", "superseded"}
SOURCE_AUTHORITIES = {"authoritative", "owner_approved", "low", "unknown", "untrusted"}
REVIEW_STATES = {"current", "review_overdue", "stale"}
EFFECTIVE_STATES = {"active", "expired", "inactive", "superseded"}
SUPPORTED_POLICIES = {"audit_safe"}

BLOCKING_REASON_PREFIXES = (
    "benchmark_only_field",
    "empty_",
    "invalid_",
    "metadata_not_object",
    "missing_",
    "retrieval_score_out_of_range",
    "unexpected_",
    "unsupported_policy",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"Line {line_no} must be a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def string_value(value: Any) -> str:
    return str(value or "").strip()


def lower_value(value: Any) -> str:
    return string_value(value).lower()


def is_blocking_reason(reason: str) -> bool:
    return reason.startswith(BLOCKING_REASON_PREFIXES)


def validate_date_field(metadata: dict[str, Any], field: str, reasons: list[str], evidence_path: str) -> None:
    value = metadata.get(field)
    if not string_value(value):
        reasons.append(f"missing_{evidence_path}_metadata_{field}")
        return
    if parse_metadata_date(value) is None:
        reasons.append(f"invalid_{evidence_path}_metadata_{field}")


def validate_evidence(evidence: Any, evidence_path: str) -> tuple[list[str], list[str]]:
    reasons: list[str] = []
    warnings: list[str] = []
    if not isinstance(evidence, dict):
        return [f"invalid_{evidence_path}_not_object"], warnings

    missing = sorted(EVIDENCE_REQUIRED_FIELDS - set(evidence))
    for field in missing:
        reasons.append(f"missing_{evidence_path}_{field}")
    unexpected = sorted(set(evidence) - EVIDENCE_ALLOWED_FIELDS)
    for field in unexpected:
        reasons.append(f"unexpected_{evidence_path}_{field}")

    if "evidence_id" in evidence and not string_value(evidence.get("evidence_id")):
        reasons.append(f"empty_{evidence_path}_evidence_id")
    if "text" in evidence and not string_value(evidence.get("text")):
        reasons.append(f"empty_{evidence_path}_text")
    if "source_uri" in evidence and not string_value(evidence.get("source_uri")):
        reasons.append(f"empty_{evidence_path}_source_uri")

    source_type = lower_value(evidence.get("source_type"))
    if "source_type" in evidence and source_type not in ALLOWED_SOURCE_TYPES:
        reasons.append(f"invalid_{evidence_path}_source_type")

    if "retrieval_score" in evidence:
        try:
            score = float(evidence.get("retrieval_score"))
        except (TypeError, ValueError):
            reasons.append(f"invalid_{evidence_path}_retrieval_score")
        else:
            if score < 0.0 or score > 1.0:
                reasons.append(f"retrieval_score_out_of_range_{evidence_path}")

    metadata = evidence.get("metadata")
    if not isinstance(metadata, dict):
        reasons.append(f"metadata_not_object_{evidence_path}")
        return reasons, warnings

    missing_metadata = sorted(METADATA_REQUIRED_FIELDS - set(metadata))
    for field in missing_metadata:
        reasons.append(f"missing_{evidence_path}_metadata_{field}")

    extra_metadata = sorted(set(metadata) - METADATA_REQUIRED_FIELDS - {"evidence_role", "section", "scenario_role"})
    if extra_metadata:
        warnings.append(f"extra_metadata_fields_present_{evidence_path}")

    for field in ("owner", "source_family", "origin_id"):
        if field in metadata and not string_value(metadata.get(field)):
            reasons.append(f"empty_{evidence_path}_metadata_{field}")

    source_status = lower_value(metadata.get("source_status"))
    if "source_status" in metadata and source_status not in SOURCE_STATUSES:
        reasons.append(f"invalid_{evidence_path}_metadata_source_status")
    elif source_status and source_status != "approved":
        reasons.append(f"review_required_{evidence_path}_source_status_{source_status}")

    source_authority = lower_value(metadata.get("source_authority"))
    if "source_authority" in metadata and source_authority not in SOURCE_AUTHORITIES:
        reasons.append(f"invalid_{evidence_path}_metadata_source_authority")
    elif source_authority and source_authority not in {"authoritative", "owner_approved"}:
        reasons.append(f"review_required_{evidence_path}_source_authority_{source_authority}")

    review_state = lower_value(metadata.get("review_state"))
    if "review_state" in metadata and review_state not in REVIEW_STATES:
        reasons.append(f"invalid_{evidence_path}_metadata_review_state")
    elif review_state and review_state != "current":
        reasons.append(f"review_required_{evidence_path}_review_state_{review_state}")

    effective_state = lower_value(metadata.get("effective_state"))
    if "effective_state" in metadata and effective_state not in EFFECTIVE_STATES:
        reasons.append(f"invalid_{evidence_path}_metadata_effective_state")
    elif effective_state and effective_state != "active":
        reasons.append(f"review_required_{evidence_path}_effective_state_{effective_state}")

    for field in ("published_at", "effective_from", "effective_to", "as_of_date"):
        validate_date_field(metadata, field, reasons, evidence_path)

    effective_from = parse_metadata_date(metadata.get("effective_from"))
    effective_to = parse_metadata_date(metadata.get("effective_to"))
    as_of_date = parse_metadata_date(metadata.get("as_of_date"))
    if effective_from and effective_to and effective_from > effective_to:
        reasons.append(f"invalid_{evidence_path}_effective_window_order")
    if effective_from and as_of_date and effective_from > as_of_date:
        reasons.append(f"review_required_{evidence_path}_future_effective")
    if effective_to and as_of_date and effective_to < as_of_date:
        reasons.append(f"review_required_{evidence_path}_expired_effective_window")

    if "support_axes" in metadata and not isinstance(metadata.get("support_axes"), list):
        reasons.append(f"invalid_{evidence_path}_metadata_support_axes")
    support_axes = normalize_metadata_list(metadata.get("support_axes"))
    if "support_axes" in metadata:
        if not support_axes:
            reasons.append(f"missing_{evidence_path}_metadata_support_axes")
        unknown_axes = sorted(set(support_axes) - set(CONSENSUS_REQUIRED_AXES))
        if unknown_axes:
            reasons.append(f"invalid_{evidence_path}_metadata_support_axes")

    return reasons, warnings


def validate_packet(packet: dict[str, Any], line_no: int | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    warnings: list[str] = []

    missing = sorted(PACKET_REQUIRED_FIELDS - set(packet))
    for field in missing:
        reasons.append(f"missing_packet_{field}")
    unexpected = sorted(set(packet) - PACKET_ALLOWED_FIELDS)
    for field in unexpected:
        if field.startswith("_expected_"):
            reasons.append(f"benchmark_only_field_{field}")
        else:
            reasons.append(f"unexpected_packet_field_{field}")

    if "decision_id" in packet and not string_value(packet.get("decision_id")):
        reasons.append("empty_packet_decision_id")
    if "query_or_claim" in packet and not string_value(packet.get("query_or_claim")):
        reasons.append("empty_packet_query_or_claim")
    if "domain_context" in packet and not string_value(packet.get("domain_context")):
        reasons.append("empty_packet_domain_context")
    if "policy" in packet and string_value(packet.get("policy")) not in SUPPORTED_POLICIES:
        reasons.append("unsupported_policy")

    candidate_evidence = packet.get("candidate_evidence")
    evidence_count = 0
    if "candidate_evidence" in packet:
        if not isinstance(candidate_evidence, list):
            reasons.append("invalid_packet_candidate_evidence")
            candidate_evidence = []
        evidence_count = len(candidate_evidence)
        if evidence_count == 0:
            reasons.append("review_required_missing_candidate_evidence")

    for idx, evidence in enumerate(candidate_evidence or [], start=1):
        evidence_reasons, evidence_warnings = validate_evidence(evidence, f"evidence_{idx}")
        reasons.extend(evidence_reasons)
        warnings.extend(evidence_warnings)

    blocking_reasons = [reason for reason in reasons if is_blocking_reason(reason)]
    if blocking_reasons:
        schema_verdict = "blocked"
    elif reasons:
        schema_verdict = "needs_review"
    else:
        schema_verdict = "confirmed"

    audit = {
        "input_hash": input_hash(packet),
        "schema_version": SCHEMA_VERSION,
        "line": line_no,
    }
    return {
        "decision_id": string_value(packet.get("decision_id")) or f"line-{line_no or 0}",
        "schema_version": SCHEMA_VERSION,
        "schema_verdict": schema_verdict,
        "evidence_count": evidence_count,
        "reason_codes": list(dict.fromkeys(reasons)),
        "warnings": list(dict.fromkeys(warnings)),
        "audit": audit,
    }


def validate_packets(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_packet(packet, line_no=idx) for idx, packet in enumerate(packets, start=1)]


def summarize(input_path: Path, output_path: Path, validations: list[dict[str, Any]]) -> dict[str, Any]:
    verdict_counts = Counter(row["schema_verdict"] for row in validations)
    reason_counts: Counter[str] = Counter()
    warning_counts: Counter[str] = Counter()
    for row in validations:
        reason_counts.update(row.get("reason_codes", []))
        warning_counts.update(row.get("warnings", []))
    blocked_count = verdict_counts.get("blocked", 0)
    needs_review_count = verdict_counts.get("needs_review", 0)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "latentatlas_customer_packet_schema_validation",
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if blocked_count == 0 else "fail",
        "input": str(input_path),
        "output": str(output_path),
        "packet_count": len(validations),
        "schema_verdict_counts": dict(sorted(verdict_counts.items())),
        "blocked_count": blocked_count,
        "needs_review_count": needs_review_count,
        "reason_code_counts": dict(sorted(reason_counts.items())),
        "warning_counts": dict(sorted(warning_counts.items())),
        "required_packet_fields": sorted(PACKET_REQUIRED_FIELDS),
        "required_evidence_fields": sorted(EVIDENCE_REQUIRED_FIELDS),
        "required_metadata_fields": sorted(METADATA_REQUIRED_FIELDS),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Input customer packet JSONL")
    parser.add_argument("--output", required=True, type=Path, help="Output validation JSONL")
    parser.add_argument("--summary", type=Path, help="Output summary JSON")
    parser.add_argument("--strict-exit", action="store_true", help="Exit non-zero when blocked packets exist")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    packets = read_jsonl(args.input)
    validations = validate_packets(packets)
    write_jsonl(args.output, validations)
    summary_path = args.summary or args.output.with_suffix(args.output.suffix + ".summary.json")
    summary = summarize(args.input, args.output, validations)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.strict_exit and summary["blocked_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
