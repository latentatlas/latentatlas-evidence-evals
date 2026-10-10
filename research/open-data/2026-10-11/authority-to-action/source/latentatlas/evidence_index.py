"""Local evidence index for LatentAtlas candidate generation.

This module builds a local, audit-friendly evidence index and turns indexed
records into existing LatentAtlas customer packets. It is intentionally not a
general-purpose vector database and does not call external services.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .evidence_guard import ALLOWED_SOURCE_TYPES, input_hash, tokenize
from .schema_validator import (
    METADATA_REQUIRED_FIELDS,
    SCHEMA_VERSION,
    SUPPORTED_POLICIES,
    is_blocking_reason,
    validate_evidence,
)


INDEX_VERSION = "latentatlas_evidence_index_v0"

SOURCE_REQUIRED_FIELDS = {"source_id", "text", "source_type", "source_uri", "metadata"}
SOURCE_ALLOWED_FIELDS = SOURCE_REQUIRED_FIELDS

QUERY_REQUIRED_FIELDS = {"decision_id", "query_or_claim", "policy", "domain_context"}
QUERY_ALLOWED_FIELDS = QUERY_REQUIRED_FIELDS


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def stable_id_part(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9_.-]+", "-", text)
    text = text.strip("-")
    return text[:80] or "source"


def string_value(value: Any) -> str:
    return str(value or "").strip()


def retrieval_score(query: str, text: str) -> float:
    query_tokens = tokenize(query)
    text_tokens = tokenize(text)
    if not query_tokens or not text_tokens:
        return 0.0
    shared = query_tokens & text_tokens
    if not shared:
        return 0.0
    coverage = len(shared) / len(query_tokens)
    density = len(shared) / max(len(text_tokens), 1)
    score = 0.35 + (0.55 * coverage) + (0.10 * min(1.0, density * 2.0))
    return round(min(1.0, score), 4)


def source_to_evidence(source: dict[str, Any], source_hash: str | None = None) -> dict[str, Any]:
    record_hash = source_hash or stable_hash(source)
    source_id = string_value(source.get("source_id"))
    return {
        "evidence_id": f"{stable_id_part(source_id)}:{record_hash[:12]}",
        "text": string_value(source.get("text")),
        "source_type": string_value(source.get("source_type")).lower(),
        "source_uri": string_value(source.get("source_uri")),
        "retrieval_score": 0.0,
        "metadata": dict(source.get("metadata") or {}),
    }


def validate_source_record(source: Any, line_no: int) -> dict[str, Any]:
    reason_codes: list[str] = []
    warnings: list[str] = []
    if not isinstance(source, dict):
        return {
            "line": line_no,
            "source_id": f"line-{line_no}",
            "index_status": "blocked",
            "reason_codes": [f"invalid_source_{line_no}_not_object"],
            "warnings": [],
        }

    missing = sorted(SOURCE_REQUIRED_FIELDS - set(source))
    for field in missing:
        reason_codes.append(f"missing_source_{field}")
    unexpected = sorted(set(source) - SOURCE_ALLOWED_FIELDS)
    for field in unexpected:
        reason_codes.append(f"unexpected_source_field_{field}")

    if "source_id" in source and not string_value(source.get("source_id")):
        reason_codes.append("empty_source_id")
    if "text" in source and not string_value(source.get("text")):
        reason_codes.append("empty_source_text")
    if "source_uri" in source and not string_value(source.get("source_uri")):
        reason_codes.append("empty_source_uri")

    source_type = string_value(source.get("source_type")).lower()
    if "source_type" in source and source_type not in ALLOWED_SOURCE_TYPES:
        reason_codes.append("invalid_source_type")

    metadata = source.get("metadata")
    if "metadata" in source and not isinstance(metadata, dict):
        reason_codes.append("metadata_not_object_source")
    elif isinstance(metadata, dict):
        missing_metadata = sorted(METADATA_REQUIRED_FIELDS - set(metadata))
        for field in missing_metadata:
            reason_codes.append(f"missing_source_metadata_{field}")

    if not any(is_blocking_reason(reason) for reason in reason_codes):
        evidence_reasons, evidence_warnings = validate_evidence(source_to_evidence(source), f"source_{line_no}")
        reason_codes.extend(evidence_reasons)
        warnings.extend(evidence_warnings)

    unique_reasons = list(dict.fromkeys(reason_codes))
    blocking = [reason for reason in unique_reasons if is_blocking_reason(reason)]
    if blocking:
        index_status = "blocked"
    elif unique_reasons:
        index_status = "needs_review"
    else:
        index_status = "confirmed"

    return {
        "line": line_no,
        "source_id": string_value(source.get("source_id")) or f"line-{line_no}",
        "index_status": index_status,
        "reason_codes": unique_reasons,
        "warnings": list(dict.fromkeys(warnings)),
    }


def build_evidence_index(sources: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not sources:
        raise ValueError("Evidence index build blocked by empty source input")
    validations = [validate_source_record(source, line_no) for line_no, source in enumerate(sources, start=1)]
    blocked = [row for row in validations if row["index_status"] == "blocked"]
    if blocked:
        sample = "; ".join(
            f"line {row['line']} {row['source_id']}: {', '.join(row['reason_codes'])}"
            for row in blocked[:5]
        )
        raise ValueError(f"Evidence index build blocked by invalid source records: {sample}")

    index_rows: list[dict[str, Any]] = []
    validation_by_line = {row["line"]: row for row in validations}
    for line_no, source in enumerate(sources, start=1):
        source_hash = stable_hash(source)
        evidence = source_to_evidence(source, source_hash)
        tokens = tokenize(evidence["text"])
        validation = validation_by_line[line_no]
        index_rows.append(
            {
                "index_version": INDEX_VERSION,
                "index_record_id": f"laei_{source_hash[:16]}",
                "source_id": string_value(source.get("source_id")),
                "source_hash": source_hash,
                "text_hash": hashlib.sha256(evidence["text"].encode("utf-8")).hexdigest(),
                "token_count": len(tokens),
                "index_status": validation["index_status"],
                "index_reason_codes": validation["reason_codes"],
                "index_warnings": validation["warnings"],
                "evidence": evidence,
            }
        )
    return index_rows, validations


def validate_index_rows(index_rows: list[dict[str, Any]]) -> None:
    if not index_rows:
        raise ValueError("Evidence index query blocked by empty index")

    failures: list[str] = []
    for line_no, row in enumerate(index_rows, start=1):
        if not isinstance(row, dict):
            failures.append(f"line {line_no}: invalid_index_record_not_object")
            continue
        if row.get("index_version") != INDEX_VERSION:
            failures.append(f"line {line_no}: invalid_index_version")
        evidence = row.get("evidence")
        if not isinstance(evidence, dict):
            failures.append(f"line {line_no}: missing_index_evidence")
            continue
        evidence_reasons, _ = validate_evidence(candidate_from_index_row(row, 0.0), f"index_{line_no}")
        blocking_reasons = [reason for reason in evidence_reasons if is_blocking_reason(reason)]
        if blocking_reasons:
            failures.append(f"line {line_no}: {', '.join(blocking_reasons)}")

    if failures:
        sample = "; ".join(failures[:5])
        raise ValueError(f"Evidence index query blocked by invalid index records: {sample}")


def validate_query_record(query: Any, line_no: int) -> dict[str, Any]:
    reason_codes: list[str] = []
    if not isinstance(query, dict):
        return {
            "line": line_no,
            "decision_id": f"line-{line_no}",
            "query_status": "blocked",
            "reason_codes": [f"invalid_query_{line_no}_not_object"],
        }

    missing = sorted(QUERY_REQUIRED_FIELDS - set(query))
    for field in missing:
        reason_codes.append(f"missing_query_{field}")
    unexpected = sorted(set(query) - QUERY_ALLOWED_FIELDS)
    for field in unexpected:
        reason_codes.append(f"unexpected_query_field_{field}")

    if "decision_id" in query and not string_value(query.get("decision_id")):
        reason_codes.append("empty_query_decision_id")
    if "query_or_claim" in query and not string_value(query.get("query_or_claim")):
        reason_codes.append("empty_query_or_claim")
    if "domain_context" in query and not string_value(query.get("domain_context")):
        reason_codes.append("empty_query_domain_context")
    if "policy" in query and string_value(query.get("policy")) not in SUPPORTED_POLICIES:
        reason_codes.append("unsupported_query_policy")

    unique_reasons = list(dict.fromkeys(reason_codes))
    return {
        "line": line_no,
        "decision_id": string_value(query.get("decision_id")) or f"line-{line_no}",
        "query_status": "blocked" if unique_reasons else "confirmed",
        "reason_codes": unique_reasons,
    }


def candidate_from_index_row(index_row: dict[str, Any], score: float) -> dict[str, Any]:
    evidence = dict(index_row.get("evidence") or {})
    metadata = dict(evidence.get("metadata") or {})
    return {
        "evidence_id": string_value(evidence.get("evidence_id")),
        "text": string_value(evidence.get("text")),
        "source_type": string_value(evidence.get("source_type")).lower(),
        "source_uri": string_value(evidence.get("source_uri")),
        "retrieval_score": score,
        "metadata": metadata,
    }


def query_evidence_index(
    index_rows: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    *,
    limit: int = 5,
    min_score: float = 0.01,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    if min_score < 0.0 or min_score > 1.0:
        raise ValueError("min_score must be between 0 and 1")

    validate_index_rows(index_rows)
    if not queries:
        raise ValueError("Evidence index query blocked by empty query input")
    validations = [validate_query_record(query, line_no) for line_no, query in enumerate(queries, start=1)]
    blocked = [row for row in validations if row["query_status"] == "blocked"]
    if blocked:
        sample = "; ".join(
            f"line {row['line']} {row['decision_id']}: {', '.join(row['reason_codes'])}"
            for row in blocked[:5]
        )
        raise ValueError(f"Evidence index query blocked by invalid query records: {sample}")

    packets: list[dict[str, Any]] = []
    for query in queries:
        query_text = string_value(query.get("query_or_claim"))
        scored_rows = []
        for row in index_rows:
            evidence = row.get("evidence") or {}
            score = retrieval_score(query_text, string_value(evidence.get("text")))
            if score >= min_score:
                scored_rows.append((score, row))
        ranked = sorted(
            scored_rows,
            key=lambda item: (
                item[0],
                string_value((item[1].get("evidence") or {}).get("evidence_id")),
            ),
            reverse=True,
        )[:limit]
        candidates = [candidate_from_index_row(row, score) for score, row in ranked]
        packets.append(
            {
                "decision_id": string_value(query.get("decision_id")),
                "query_or_claim": query_text,
                "candidate_evidence": candidates,
                "policy": string_value(query.get("policy")),
                "domain_context": string_value(query.get("domain_context")),
            }
        )
    return packets, validations


def index_hash(index_rows: list[dict[str, Any]]) -> str:
    return stable_hash({"index_version": INDEX_VERSION, "records": index_rows})


def summarize_index_build(
    input_path: Path,
    output_path: Path,
    index_rows: list[dict[str, Any]],
    validations: list[dict[str, Any]],
) -> dict[str, Any]:
    status_counts = Counter(row["index_status"] for row in validations)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "latentatlas_build_evidence_index",
        "index_version": INDEX_VERSION,
        "input": str(input_path),
        "output": str(output_path),
        "source_count": len(validations),
        "index_record_count": len(index_rows),
        "index_status_counts": dict(sorted(status_counts.items())),
        "index_hash": index_hash(index_rows),
        "external_services_used": False,
        "production_truth_mutation": False,
    }


def summarize_index_query(
    index_path: Path,
    queries_path: Path,
    output_path: Path,
    index_rows: list[dict[str, Any]],
    packets: list[dict[str, Any]],
    validations: list[dict[str, Any]],
    *,
    limit: int,
    min_score: float,
) -> dict[str, Any]:
    candidate_counts = [len(packet.get("candidate_evidence") or []) for packet in packets]
    validation_counts = Counter(row["query_status"] for row in validations)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "latentatlas_query_evidence_index",
        "index_version": INDEX_VERSION,
        "packet_schema_version": SCHEMA_VERSION,
        "index": str(index_path),
        "queries": str(queries_path),
        "output": str(output_path),
        "query_count": len(validations),
        "packet_count": len(packets),
        "candidate_count": sum(candidate_counts),
        "empty_candidate_packet_count": sum(1 for count in candidate_counts if count == 0),
        "query_status_counts": dict(sorted(validation_counts.items())),
        "limit": limit,
        "min_score": min_score,
        "index_hash": index_hash(index_rows),
        "packet_hash": input_hash({"packets": packets}),
        "external_services_used": False,
        "production_truth_mutation": False,
    }
