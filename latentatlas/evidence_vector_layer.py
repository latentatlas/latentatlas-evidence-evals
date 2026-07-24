"""Orchestrated Evidence Vector Layer pilot chain for LatentAtlas.

The layer packages local candidate generation and evidence qualification as one
auditable pilot run. It is deliberately an adapter layer over retrieval, not a
standalone vector database product.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .evidence_guard import EvidenceGuard
from .evidence_index import build_evidence_index
from .evidence_index import query_evidence_index
from .evidence_index import summarize_index_build
from .evidence_index import summarize_index_query
from .schema_validator import summarize as summarize_schema
from .schema_validator import validate_packets
from .verify_outputs import verify as verify_decisions


VECTOR_LAYER_VERSION = "latentatlas_evidence_vector_layer_v0"
SUPPORTED_ADAPTERS = {"local"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Line {line_no} must be a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def summarize_decisions(input_path: Path, output_path: Path, decisions: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_counts = Counter(row["evidence_verdict"] for row in decisions)
    identity_counts = Counter(row["identity_verdict"] for row in decisions)
    action_counts = Counter(row["recommended_action"] for row in decisions)
    reason_counts: Counter[str] = Counter()
    for row in decisions:
        reason_counts.update(row.get("reason_codes", []))
    false_evidence_allow_count = sum(
        1
        for row in decisions
        if row["recommended_action"] == "allow_answer" and row["evidence_verdict"] != "confirmed_evidence"
    )
    coerced_review_context_count = sum(
        1
        for row in decisions
        if row["evidence_verdict"] in {"needs_context", "needs_review"}
        and row["recommended_action"] == "allow_answer"
    )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "latentatlas_evidence_vector_layer_qualify",
        "input": str(input_path),
        "output": str(output_path),
        "decision_count": len(decisions),
        "evidence_verdict_counts": dict(sorted(evidence_counts.items())),
        "identity_verdict_counts": dict(sorted(identity_counts.items())),
        "recommended_action_counts": dict(sorted(action_counts.items())),
        "reason_code_counts": dict(sorted(reason_counts.items())),
        "false_evidence_allow_count": false_evidence_allow_count,
        "needs_context_or_review_coerced_to_allow_count": coerced_review_context_count,
    }


def gate(name: str, status: str, **details: Any) -> dict[str, Any]:
    return {"name": name, "status": status, **details}


def build_manifest(
    *,
    source_path: Path,
    query_path: Path,
    out_dir: Path,
    adapter: str,
    limit: int,
    min_score: float,
    paths: dict[str, Path],
    build_summary: dict[str, Any],
    query_summary: dict[str, Any],
    schema_summary: dict[str, Any],
    decision_summary: dict[str, Any],
    verification_summary: dict[str, Any],
) -> dict[str, Any]:
    schema_status = "pass" if schema_summary.get("blocked_count") == 0 else "fail"
    qualification_status = (
        "pass"
        if decision_summary.get("false_evidence_allow_count") == 0
        and decision_summary.get("needs_context_or_review_coerced_to_allow_count") == 0
        else "fail"
    )
    gates = [
        gate(
            "build_index",
            "pass",
            source_count=build_summary.get("source_count", 0),
            index_record_count=build_summary.get("index_record_count", 0),
        ),
        gate(
            "query_index",
            "pass",
            query_count=query_summary.get("query_count", 0),
            packet_count=query_summary.get("packet_count", 0),
            candidate_count=query_summary.get("candidate_count", 0),
            empty_candidate_packet_count=query_summary.get("empty_candidate_packet_count", 0),
        ),
        gate(
            "schema_validation",
            schema_status,
            blocked_count=schema_summary.get("blocked_count", 0),
            needs_review_count=schema_summary.get("needs_review_count", 0),
        ),
        gate(
            "qualification",
            qualification_status,
            false_evidence_allow_count=decision_summary.get("false_evidence_allow_count", 0),
            needs_context_or_review_coerced_to_allow_count=decision_summary.get(
                "needs_context_or_review_coerced_to_allow_count", 0
            ),
        ),
        gate(
            "decision_verification",
            str(verification_summary.get("status", "fail")),
            failure_count=verification_summary.get("failure_count", 0),
        ),
    ]
    status = "pass" if all(item["status"] == "pass" for item in gates) else "fail"
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "latentatlas_evidence_vector_layer",
        "vector_layer_version": VECTOR_LAYER_VERSION,
        "status": status,
        "adapter": {
            "requested": adapter,
            "active": adapter,
            "external_services_used": False,
            "production_truth_mutation": False,
        },
        "source_input": str(source_path),
        "query_input": str(query_path),
        "out_dir": str(out_dir),
        "limit": limit,
        "min_score": min_score,
        "gates": gates,
        "outputs": {key: str(value) for key, value in paths.items()},
        "scope": {
            "purpose": "local evidence qualification reference pipeline",
            "not_a": "general-purpose vector database replacement",
            "data_handling": "local, synthetic or deliberately public source excerpts by default",
            "decision_rule": "candidate retrieval is not evidence approval; EvidenceGuard remains the decision gate",
        },
    }


def run_evidence_vector_layer(
    *,
    source_path: Path,
    query_path: Path,
    out_dir: Path,
    adapter: str = "local",
    limit: int = 5,
    min_score: float = 0.01,
) -> dict[str, Any]:
    if adapter not in SUPPORTED_ADAPTERS:
        raise ValueError(f"Unsupported evidence vector layer adapter: {adapter}")

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "index": out_dir / "evidence_index.jsonl",
        "index_summary": out_dir / "evidence_index_summary.json",
        "packets": out_dir / "query_packets.jsonl",
        "query_summary": out_dir / "query_summary.json",
        "schema_validations": out_dir / "schema_validations.jsonl",
        "schema_summary": out_dir / "schema_summary.json",
        "decisions": out_dir / "decisions.jsonl",
        "decision_summary": out_dir / "decision_summary.json",
        "decision_verification": out_dir / "decision_verification.json",
        "manifest": out_dir / "evidence_vector_layer_manifest.json",
    }

    sources = read_jsonl(source_path)
    queries = read_jsonl(query_path)

    index_rows, source_validations = build_evidence_index(sources)
    write_jsonl(paths["index"], index_rows)
    build_summary = summarize_index_build(source_path, paths["index"], index_rows, source_validations)
    write_json(paths["index_summary"], build_summary)

    packets, query_validations = query_evidence_index(index_rows, queries, limit=limit, min_score=min_score)
    write_jsonl(paths["packets"], packets)
    query_summary = summarize_index_query(
        paths["index"],
        query_path,
        paths["packets"],
        index_rows,
        packets,
        query_validations,
        limit=limit,
        min_score=min_score,
    )
    write_json(paths["query_summary"], query_summary)

    schema_validations = validate_packets(packets)
    write_jsonl(paths["schema_validations"], schema_validations)
    schema_summary = summarize_schema(paths["packets"], paths["schema_validations"], schema_validations)
    write_json(paths["schema_summary"], schema_summary)

    guard = EvidenceGuard(policy="audit_safe")
    decisions = [guard.qualify_packet(packet) for packet in packets]
    write_jsonl(paths["decisions"], decisions)
    decision_summary = summarize_decisions(paths["packets"], paths["decisions"], decisions)
    write_json(paths["decision_summary"], decision_summary)

    verification_summary = verify_decisions(decisions, paths["decisions"])
    write_json(paths["decision_verification"], verification_summary)

    manifest = build_manifest(
        source_path=source_path,
        query_path=query_path,
        out_dir=out_dir,
        adapter=adapter,
        limit=limit,
        min_score=min_score,
        paths=paths,
        build_summary=build_summary,
        query_summary=query_summary,
        schema_summary=schema_summary,
        decision_summary=decision_summary,
        verification_summary=verification_summary,
    )
    write_json(paths["manifest"], manifest)
    return manifest
