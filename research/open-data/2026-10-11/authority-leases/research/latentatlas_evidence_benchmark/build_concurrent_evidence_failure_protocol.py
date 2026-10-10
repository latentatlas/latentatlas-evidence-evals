#!/usr/bin/env python3
"""Build the Concurrent Evidence Failure test protocol.

The protocol turns the v1 failure-family note into an executable research plan:
family-specific hypotheses, negative controls, required evidence fields, and
promotion gates. It intentionally remains Level 3.5 until the review, strata,
baseline, and holdout requirements pass.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_CONCURRENCY_SUMMARY = Path(
    "outputs/latentatlas/concurrent_evidence_failure_v1/concurrent_evidence_failure_summary.json"
)
DEFAULT_LEVEL4_SUMMARY = Path(
    "outputs/latentatlas/action_time_level4_data_engine_v1/action_time_level4_data_engine_summary.json"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concurrent_evidence_failure_protocol_v1")

SCHEMA_VERSION = "latentatlas_concurrent_evidence_failure_protocol_v1"

FAMILY_PROTOCOLS = {
    "stale_read": {
        "positive_test": "Decision used an older PDP, screenshot, cache, or state snapshot while a newer packet-visible state superseded it.",
        "negative_control": "Current evidence timestamp is newer than or equal to action time, identity is stable, and no newer superseding record exists.",
        "required_fields": "evidence_timestamp, action_timestamp, latest_state_timestamp, subject_cluster_hash, source_type",
        "promotion_gate": "Baseline replay comparing stale-read policy vs action-time freshness policy.",
    },
    "identity_time_split": {
        "positive_test": "Packet-visible identity conflict exists between evidence capture and action-time target identity.",
        "negative_control": "Stable canonical identity across capture, review packet, and action target with no conflicting aliases.",
        "required_fields": "subject_cluster_hash, canonical_identity_hash, action_target_hash, identity_conflict_flag",
        "promotion_gate": "Independent reviewer agreement on identity-conflict labels and ambiguous-identity quarantine handling.",
    },
    "authority_expiry": {
        "positive_test": "Risk signal or prior decision is present, but packet-visible authority is expired, missing, or unresolved at action time.",
        "negative_control": "Lease-like authority fields are present, unexpired, permission-stable, and policy-stable at action time.",
        "required_fields": "decision_id, authority_issued_at, authority_expires_at, permission_hash, policy_hash",
        "promotion_gate": "Pre-registered unresolved-case treatment and second-reviewer agreement for needs_more_evidence rows.",
    },
    "materialization_race": {
        "positive_test": "Price, availability, seller, stock, or workflow state changes while the decision is being materialized.",
        "negative_control": "Materialized output matches the latest packet-visible state and no later conflicting state appears before action.",
        "required_fields": "materialization_timestamp, latest_state_timestamp, action_type, state_delta_hash, output_hash",
        "promotion_gate": "Action-type stratification and replay of manual-review-before-materialization baseline.",
    },
    "visibility_truth_confusion": {
        "positive_test": "Blocked access, timeout, empty page, or unavailable visibility is treated as product/workflow truth.",
        "negative_control": "Fresh accessible page or independent source confirms the product/workflow state after visibility is restored.",
        "required_fields": "visibility_status, fetch_status, unblock_proof_timestamp, independent_source_evidence",
        "promotion_gate": "Negative controls proving blocked visibility is not counted as correctness or falseness without fresh proof.",
    },
    "context_contamination": {
        "positive_test": "Reviewer or model imports outside memory, jargon, or ontology not present in the packet.",
        "negative_control": "Reviewer rationale cites only packet-visible fields and uses no non-packet factual additions.",
        "required_fields": "reviewer_id, rationale_short, packet_field_citations, non_packet_fact_flags",
        "promotion_gate": "Grounding audit before any external mini-review label can enter adjudication.",
    },
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def table_row(cells: list[Any]) -> str:
    return "| " + " | ".join(str(cell) for cell in cells) + " |"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    return [table_row(headers), table_row(["---" for _ in headers]), *[table_row(row) for row in rows]]


def blocked_summary(reason: str, paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_concurrent_evidence_failure_protocol",
        "schema_version": SCHEMA_VERSION,
        "status": "blocked",
        "failure_reasons": [reason],
        "level4_probability_claim_allowed": False,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def build_rows(concurrency_summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in concurrency_summary.get("failure_families", []):
        family_id = family.get("family_id", "")
        protocol = FAMILY_PROTOCOLS.get(family_id, {})
        rows.append(
            {
                "family_id": family_id,
                "current_local_count": f"{family.get('numerator', '')}/{family.get('denominator', '')}",
                "current_boundary": family.get("claim_boundary", ""),
                "positive_test": protocol.get("positive_test", ""),
                "negative_control": protocol.get("negative_control", ""),
                "required_fields": protocol.get("required_fields", ""),
                "promotion_gate": protocol.get("promotion_gate", ""),
                "minimum_next_reviewed_examples": 100 if int(family.get("denominator") or 0) > 0 else 30,
                "claim_state": "level3_5_protocol_track",
            }
        )
    return rows


def build_summary(
    concurrency_summary: dict[str, Any],
    level4_summary: dict[str, Any],
    paths: dict[str, Path],
) -> dict[str, Any]:
    if concurrency_summary.get("status") != "pass":
        return blocked_summary("concurrent evidence failure summary status is not pass", paths)

    rows = build_rows(concurrency_summary)
    review_metrics = level4_summary.get("review_metrics", {})
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_concurrent_evidence_failure_protocol",
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "research_track": "concurrent_evidence_failure",
        "short_claim": concurrency_summary.get("short_claim", ""),
        "family_count": len(rows),
        "protocol_rows": rows,
        "level4_probability_claim_allowed": False,
        "level4_state": {
            "current_independent_human_review_count": review_metrics.get("current_independent_human_review_count"),
            "minimum_reviewed_outcome_count": review_metrics.get("minimum_reviewed_outcome_count"),
            "second_review_completed_rows": review_metrics.get("second_review_completed_rows"),
            "second_review_missing_rows": review_metrics.get("second_review_missing_rows"),
        },
        "next_execution_order": [
            "Add required evidence fields to the masked review packet schema.",
            "Build negative-control fixtures for every family before expanding counts.",
            "Run baseline replay for stale_read and materialization_race.",
            "Collect second-reviewer agreement before any reliability language.",
            "Only then consider Level 4 promotion review.",
        ],
        "claim_boundary": {
            "allowed_claims": [
                "Concurrent Evidence Failure is a Level 3.5 test protocol.",
                "Family-specific local counts may be reported with frozen-set boundaries.",
                "Negative controls and required fields can be defined before new data collection.",
            ],
            "blocked_claims": [
                "Broader concurrency failure rates.",
                "Level 4 population probability.",
                "External mini-review labels without grounding audit.",
                "Production truth mutation or customer-facing verdict generation.",
            ],
        },
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "inputs": {
            "concurrency_summary": str(DEFAULT_CONCURRENCY_SUMMARY),
            "level4_summary": str(DEFAULT_LEVEL4_SUMMARY),
        },
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def build_protocol_doc(summary: dict[str, Any]) -> str:
    if summary["status"] != "pass":
        return "\n".join(["# Concurrent Evidence Failure Test Protocol", "", "Status: blocked", "", *summary.get("failure_reasons", [])])

    rows = summary["protocol_rows"]
    lines = [
        "# Concurrent Evidence Failure Test Protocol",
        "",
        f"Generated at: `{summary['generated_at_utc']}`",
        f"Status: `{summary['status']}`",
        "",
        "## Boundary",
        "",
        "This is a Level 3.5 test protocol. It defines what to measure next; it does not claim Level 4 probability, broader population rates, production readiness, or customer-facing verdict authority.",
        "",
        "## Core Claim",
        "",
        summary.get("short_claim", ""),
        "",
        "## Family Tests",
        "",
        *markdown_table(
            ["Family", "Local Count", "Positive Test", "Negative Control", "Promotion Gate"],
            [
                [
                    f"`{row['family_id']}`",
                    row["current_local_count"],
                    row["positive_test"],
                    row["negative_control"],
                    row["promotion_gate"],
                ]
                for row in rows
            ],
        ),
        "",
        "## Execution Order",
        "",
        *[f"{idx}. {item}" for idx, item in enumerate(summary["next_execution_order"], start=1)],
        "",
        "## Blocked Claims",
        "",
        *[f"- {claim}" for claim in summary["claim_boundary"]["blocked_claims"]],
        "",
    ]
    return "\n".join(lines)


def run(
    concurrency_summary_path: Path = DEFAULT_CONCURRENCY_SUMMARY,
    level4_summary_path: Path = DEFAULT_LEVEL4_SUMMARY,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "protocol": out_dir / "concurrent_evidence_failure_test_protocol.md",
        "strata_plan": out_dir / "concurrent_evidence_failure_strata_plan.csv",
        "negative_controls": out_dir / "concurrent_evidence_failure_negative_controls.csv",
        "summary": out_dir / "concurrent_evidence_failure_protocol_summary.json",
        "manifest": out_dir / "concurrent_evidence_failure_protocol_manifest.json",
    }
    missing = [str(path) for path in (concurrency_summary_path, level4_summary_path) if not path.exists()]
    if missing:
        summary = blocked_summary(f"missing required sources: {', '.join(missing)}", paths)
    else:
        summary = build_summary(read_json(concurrency_summary_path), read_json(level4_summary_path), paths)

    rows = summary.get("protocol_rows", [])
    write_text(paths["protocol"], build_protocol_doc(summary))
    write_csv(
        paths["strata_plan"],
        rows,
        [
            "family_id",
            "current_local_count",
            "current_boundary",
            "positive_test",
            "required_fields",
            "promotion_gate",
            "minimum_next_reviewed_examples",
            "claim_state",
        ],
    )
    write_csv(
        paths["negative_controls"],
        rows,
        ["family_id", "negative_control", "required_fields", "claim_state"],
    )
    write_json(paths["summary"], summary)
    manifest = {
        "generated_at_utc": summary["generated_at_utc"],
        "mode": summary["mode"],
        "schema_version": summary.get("schema_version", SCHEMA_VERSION),
        "status": summary["status"],
        "family_count": summary.get("family_count", 0),
        "level4_probability_claim_allowed": False,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": {key: str(value) for key, value in paths.items()},
    }
    write_json(paths["manifest"], manifest)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--concurrency-summary", type=Path, default=DEFAULT_CONCURRENCY_SUMMARY)
    parser.add_argument("--level4-summary", type=Path, default=DEFAULT_LEVEL4_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.concurrency_summary, args.level4_summary, args.out_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
