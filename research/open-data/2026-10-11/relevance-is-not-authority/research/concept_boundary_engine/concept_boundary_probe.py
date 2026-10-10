"""Seed proof for the Concept Boundary Engine research lane.

The probe is deterministic and local. It compares a naive high-similarity
baseline with a boundary-aware decision rule, then writes auditable artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("research/concept_boundary_engine/concept_boundary_cases.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_engine")

AUTHORITY_RANK = {
    "related": 1,
    "bridge_context": 1,
    "peer_comparison": 1,
    "same_identity": 2,
    "evidence_support": 3,
    "action_ready": 4,
    "publish_safe": 5,
    "customer_safe": 5,
    "privacy_blocked": -1,
    "contradiction": -1,
}

REQUESTED_AUTHORITY_TO_BOUNDARY = {
    "related": "related",
    "same_identity": "same_identity",
    "evidence_support": "evidence_support",
    "action_ready": "action_ready",
    "publish_safe": "publish_safe",
    "customer_safe": "publish_safe",
}

ALLOW_DECISIONS = {"allow_evidence", "allow_action", "allow_publish"}
BLOCKING_FRESHNESS = {"stale", "expired", "superseded", "deprecated"}
LOW_AUTHORITY = {"low", "unknown", "internal", "draft"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        row["_line_number"] = line_number
        rows.append(row)
    return rows


def naive_similarity_decision(row: dict[str, Any], threshold: float) -> str:
    score = float(row.get("similarity_score", 0.0))
    return "allow" if score >= threshold else "block"


def classify_boundary(row: dict[str, Any]) -> dict[str, Any]:
    requested = str(row["requested_authority"])
    boundary = str(row["boundary_type"])
    freshness = str(row.get("freshness_state", "unknown"))
    source_authority = str(row.get("source_authority", "unknown"))
    action_scope = str(row.get("action_scope", "none"))

    if row.get("contains_sensitive_data") is True or boundary == "privacy_blocked":
        return decision(row, "block_privacy", "privacy_boundary_blocks_all_use", False)
    if boundary == "contradiction":
        return decision(row, "block_contradiction", "candidate_contradicts_requested_claim", False)
    if freshness in BLOCKING_FRESHNESS:
        return decision(row, "block_false_authority", f"freshness_state_{freshness}", False)
    if source_authority in LOW_AUTHORITY and requested not in {"related"}:
        return decision(row, "block_false_authority", f"source_authority_{source_authority}", False)

    required_boundary = REQUESTED_AUTHORITY_TO_BOUNDARY.get(requested)
    requested_rank = AUTHORITY_RANK.get(required_boundary or requested, 99)
    granted_rank = AUTHORITY_RANK.get(boundary, 0)
    if granted_rank < requested_rank:
        return decision(
            row,
            "block_false_authority",
            f"{boundary}_does_not_grant_{requested}",
            False,
        )
    if requested in {"action_ready", "publish_safe", "customer_safe"} and action_scope != "approved":
        return decision(row, "block_false_authority", "action_scope_not_approved", False)
    if requested == "evidence_support":
        return decision(row, "allow_evidence", "boundary_grants_evidence_support", True)
    if requested == "action_ready":
        return decision(row, "allow_action", "boundary_grants_action_ready", True)
    if requested in {"publish_safe", "customer_safe"}:
        return decision(row, "allow_publish", "boundary_grants_publish_safe", True)
    if requested == "same_identity":
        return decision(row, "allow_identity_candidate", "boundary_grants_same_identity", True)
    return decision(row, "candidate_only", "discovery_only_boundary", False)


def decision(
    row: dict[str, Any],
    boundary_decision: str,
    reason_code: str,
    authority_transfer_allowed: bool,
) -> dict[str, Any]:
    truth_mutation_allowed = False
    customer_surface_mutation_allowed = False
    return {
        "case_id": row["case_id"],
        "archetype": row.get("archetype", ""),
        "variation_id": row.get("variation_id", ""),
        "requested_authority": row["requested_authority"],
        "boundary_type": row["boundary_type"],
        "similarity_score": float(row["similarity_score"]),
        "source_authority": row.get("source_authority", "unknown"),
        "freshness_state": row.get("freshness_state", "unknown"),
        "action_scope": row.get("action_scope", "none"),
        "contains_sensitive_data": bool(row.get("contains_sensitive_data", False)),
        "expected_decision": row["expected_decision"],
        "expected_reason_family": row.get("expected_reason_family", ""),
        "boundary_decision": boundary_decision,
        "reason_code": reason_code,
        "authority_transfer_allowed": authority_transfer_allowed,
        "truth_mutation_allowed": truth_mutation_allowed,
        "customer_surface_mutation_allowed": customer_surface_mutation_allowed,
    }


def summarize(rows: list[dict[str, Any]], decisions: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    high_similarity_rows = [row for row in rows if float(row["similarity_score"]) >= threshold]
    naive_allows = [
        row for row in rows if naive_similarity_decision(row, threshold=threshold) == "allow"
    ]
    naive_false_authority = [
        row for row in naive_allows if row["expected_decision"] not in ALLOW_DECISIONS
    ]
    boundary_false_authority = [
        row
        for row in decisions
        if row["authority_transfer_allowed"] and row["expected_decision"] not in ALLOW_DECISIONS
    ]
    expected_mismatches = [
        row for row in decisions if row["boundary_decision"] != row["expected_decision"]
    ]
    allowed_expected = [row for row in rows if row["expected_decision"] in ALLOW_DECISIONS]
    allowed_preserved = [
        row for row in decisions if row["expected_decision"] in ALLOW_DECISIONS and row["boundary_decision"] == row["expected_decision"]
    ]
    status = "pass" if not boundary_false_authority and not expected_mismatches else "fail"
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": status,
        "similarity_threshold": threshold,
        "total_cases": len(rows),
        "high_similarity_cases": len(high_similarity_rows),
        "naive_similarity_allow_count": len(naive_allows),
        "naive_false_authority_count": len(naive_false_authority),
        "boundary_false_authority_count": len(boundary_false_authority),
        "expected_mismatch_count": len(expected_mismatches),
        "allowed_expected_count": len(allowed_expected),
        "allowed_preserved_count": len(allowed_preserved),
        "truth_mutation_allowed_count": sum(1 for row in decisions if row["truth_mutation_allowed"]),
        "customer_surface_mutation_allowed_count": sum(
            1 for row in decisions if row["customer_surface_mutation_allowed"]
        ),
        "blocked_reason_counts": reason_counts(decisions),
    }


def reason_counts(decisions: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in decisions:
        reason = str(row["reason_code"])
        counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))


def write_outputs(out_dir: Path, decisions: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = list(decisions[0].keys()) if decisions else []
    with (out_dir / "decisions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(decisions)

    report = [
        "# Concept Boundary Engine Proof Report",
        "",
        f"Generated at UTC: `{summary['generated_at_utc']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Key Result",
        "",
        f"- Total cases: `{summary['total_cases']}`",
        f"- High-similarity cases: `{summary['high_similarity_cases']}`",
        f"- Naive similarity allows: `{summary['naive_similarity_allow_count']}`",
        f"- Naive false-authority allows: `{summary['naive_false_authority_count']}`",
        f"- Boundary false-authority allows: `{summary['boundary_false_authority_count']}`",
        f"- Expected decision mismatches: `{summary['expected_mismatch_count']}`",
        f"- Allowed expected cases preserved: `{summary['allowed_preserved_count']}/{summary['allowed_expected_count']}`",
        "",
        "## Mutation Boundary",
        "",
        f"- Truth mutation allowed count: `{summary['truth_mutation_allowed_count']}`",
        f"- Customer surface mutation allowed count: `{summary['customer_surface_mutation_allowed_count']}`",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def run(input_path: Path, out_dir: Path, threshold: float) -> dict[str, Any]:
    rows = read_jsonl(input_path)
    decisions = [classify_boundary(row) for row in rows]
    summary = summarize(rows, decisions, threshold)
    write_outputs(out_dir, decisions, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--threshold", type=float, default=0.82)
    args = parser.parse_args()
    summary = run(args.input, args.out_dir, args.threshold)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
