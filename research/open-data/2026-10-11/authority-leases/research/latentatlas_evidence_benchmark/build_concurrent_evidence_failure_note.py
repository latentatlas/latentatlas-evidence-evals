#!/usr/bin/env python3
"""Build the Concurrent Evidence Failure research note.

The note converts the frozen action-time finding pack into a claim-bounded
Level 3.5 research artifact. It does not claim population rates or Level 4
calibration; it names evidence-concurrency failure families and records the
local denominators currently visible in the frozen P0 review set.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_FINDING_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_empirical_finding_pack_v1/"
    "action_time_p0_empirical_finding_pack_summary.json"
)
DEFAULT_CONTINUATION_SUMMARY = Path(
    "outputs/latentatlas/action_time_level3_continuation_pack_v1/"
    "level3_continuation_summary.json"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concurrent_evidence_failure_v1")

SCHEMA_VERSION = "latentatlas_concurrent_evidence_failure_note_v1"

FAMILY_ORDER = [
    "stale_read",
    "identity_time_split",
    "authority_expiry",
    "materialization_race",
    "visibility_truth_confusion",
    "context_contamination",
]

FAMILY_DEFINITIONS = {
    "stale_read": {
        "definition": "A prior PDP, screenshot, cache, or state observation is treated as current action evidence.",
        "testable_prediction": "Latest temporal-authority packets should expose false-block cases when a newer record supersedes stale state.",
    },
    "identity_time_split": {
        "definition": "The target identity changes or conflicts between evidence capture and action-time judgment.",
        "testable_prediction": "Explicit packet-visible identity conflicts should route to block-grade decisions; ambiguous identity should stay unresolved.",
    },
    "authority_expiry": {
        "definition": "A risk signal or prior decision no longer authorizes the later action without revalidation.",
        "testable_prediction": "Risk signals should prioritize review but should not become outcome evidence without packet-visible authority.",
    },
    "materialization_race": {
        "definition": "Price, availability, seller, or workflow state changes while the decision is being materialized.",
        "testable_prediction": "Manual-review/materialization packets should split across correct_block, false_block, and needs_more_evidence rather than collapse into one label.",
    },
    "visibility_truth_confusion": {
        "definition": "Blocked access, timeout, empty page, or unavailable visibility is mistaken for product or workflow truth.",
        "testable_prediction": "Blocked PDP cases should remain needs_more_evidence unless fresh unblock or outcome proof is visible.",
    },
    "context_contamination": {
        "definition": "A reviewer or model imports outside memory, jargon, or domain ontology and replaces packet-visible evidence.",
        "testable_prediction": "External mini-review responses with non-packet facts should be invalid for adjudication but useful as grounding-failure examples.",
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


def pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return ""
    return f"{numerator / denominator:.4f}"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    def row(cells: list[Any]) -> str:
        return "| " + " | ".join(str(cell) for cell in cells) + " |"

    return [row(headers), row(["---" for _ in headers]), *[row(item) for item in rows]]


def metric_by_id(finding_summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row.get("metric_id", ""): row for row in finding_summary.get("metrics", []) if row.get("metric_id")}


def nested_count(profiles: dict[str, Any], profile_name: str, key: str, outcome: str | None = None) -> int:
    profile = profiles.get(profile_name, {})
    if outcome is None:
        value = profile.get(key, 0)
        return int(value or 0)
    return int((profile.get(key, {}) or {}).get(outcome, 0) or 0)


def nested_total(profiles: dict[str, Any], profile_name: str, key: str) -> int:
    return sum(int(value or 0) for value in (profiles.get(profile_name, {}).get(key, {}) or {}).values())


def build_failure_matrix(finding_summary: dict[str, Any], continuation_summary: dict[str, Any]) -> list[dict[str, Any]]:
    profiles = finding_summary.get("profiles", {})
    metrics = metric_by_id(finding_summary)
    matrix: list[dict[str, Any]] = []

    latest_metric = metrics.get("latest_pdp_temporal_false_block", {})
    latest_num = int(latest_metric.get("numerator") or 0)
    latest_den = int(latest_metric.get("denominator") or 0)
    matrix.append(
        family_row(
            "stale_read",
            latest_num,
            latest_den,
            "latest_pdp_temporal_false_block",
            "Latest-PDP temporal-authority packets produced local false-block observations where newer evidence superseded stale state.",
            "Temporal-authority observation in frozen P0 only.",
        )
    )

    identity_metric = metrics.get("identity_conflict_correct_block", {})
    identity_num = int(identity_metric.get("numerator") or 0)
    identity_den = int(identity_metric.get("denominator") or 0)
    matrix.append(
        family_row(
            "identity_time_split",
            identity_num,
            identity_den,
            "identity_conflict_correct_block",
            "Packet-visible identity conflicts supported block-grade outcomes in the frozen P0 set.",
            "Pattern-specific observation; not universal identity-guard accuracy.",
        )
    )

    nme_count = int(finding_summary.get("outcome_counts", {}).get("needs_more_evidence", 0) or 0)
    reviewed = int(finding_summary.get("denominators", {}).get("frozen_reviewed_rows", 0) or 0)
    matrix.append(
        family_row(
            "authority_expiry",
            nme_count,
            reviewed,
            "needs_more_evidence_all_reviewed",
            "Evidence-insufficient rows show that risk or prior state cannot be promoted into action authority without revalidation.",
            "Descriptive unresolved-evidence rate only; not an error rate.",
        )
    )

    manual_total = nested_total(profiles, "outcome_by_action_type", "manual_review_before_materialization")
    manual_false = nested_count(profiles, "outcome_by_action_type", "manual_review_before_materialization", "false_block")
    matrix.append(
        family_row(
            "materialization_race",
            manual_false,
            manual_total,
            "manual_review_before_materialization.false_block",
            "Manual-review-before-materialization packets split across outcomes, showing that action-time state can change the verdict.",
            "Local action-type observation; not a general materialization failure rate.",
        )
    )

    blocked_metric = metrics.get("blocked_pdp_needs_more_evidence", {})
    blocked_num = int(blocked_metric.get("numerator") or 0)
    blocked_den = int(blocked_metric.get("denominator") or 0)
    matrix.append(
        family_row(
            "visibility_truth_confusion",
            blocked_num,
            blocked_den,
            "blocked_pdp_needs_more_evidence",
            "Blocked PDP cases stayed evidence-insufficient instead of being treated as product truth.",
            "Blocked access is evidence state, not outcome truth.",
        )
    )

    matrix.append(
        family_row(
            "context_contamination",
            0,
            0,
            "micro_review_grounding_audit_required",
            "External mini-reviews are usable only after a grounding audit detects non-packet facts or imported ontology.",
            "Qualitative protocol guard; no counted denominator in the frozen P0 pack.",
        )
    )

    allowed_claims = set(continuation_summary.get("claim_boundary", {}).get("allowed_claims", []))
    if "Failure-family hypotheses grounded in observed masked reason-code patterns." not in allowed_claims:
        for row in matrix:
            row["current_state"] = "blocked_until_continuation_boundary_passes"
    return matrix


def family_row(
    family_id: str,
    numerator: int,
    denominator: int,
    evidence_handle: str,
    local_observation: str,
    claim_boundary: str,
) -> dict[str, Any]:
    family = FAMILY_DEFINITIONS[family_id]
    return {
        "family_id": family_id,
        "definition": family["definition"],
        "local_observation": local_observation,
        "numerator": numerator,
        "denominator": denominator,
        "local_rate": pct(numerator, denominator),
        "evidence_handle": evidence_handle,
        "claim_boundary": claim_boundary,
        "testable_prediction": family["testable_prediction"],
        "current_state": "research_track",
        "allowed_claim": "This is a frozen-set local observation or protocol guard.",
        "blocked_claim": "This is not a population concurrency failure rate or Level 4 claim.",
    }


def blocked_summary(reason: str, paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_concurrent_evidence_failure_note",
        "schema_version": SCHEMA_VERSION,
        "status": "blocked",
        "failure_reasons": [reason],
        "level4_probability_claim_allowed": False,
        "production_truth_mutation": False,
        "external_calls_used_by_builder": False,
        "raw_source_rows_read": False,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def build_summary(
    finding_summary: dict[str, Any],
    continuation_summary: dict[str, Any],
    paths: dict[str, Path],
) -> dict[str, Any]:
    if finding_summary.get("status") != "pass":
        return blocked_summary("finding summary status is not pass", paths)
    if continuation_summary.get("status") != "pass":
        return blocked_summary("continuation summary status is not pass", paths)

    matrix = build_failure_matrix(finding_summary, continuation_summary)
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_concurrent_evidence_failure_note",
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "research_track": "concurrent_evidence_failure",
        "short_claim": (
            "Many agentic AI failures are evidence-concurrency failures: the model acts on observations "
            "whose identity, freshness, authority, or materialization timing no longer align."
        ),
        "failure_family_count": len(matrix),
        "failure_families": matrix,
        "denominators": finding_summary.get("denominators", {}),
        "outcome_counts": finding_summary.get("outcome_counts", {}),
        "claim_boundary": {
            "allowed_claims": [
                "Concurrent Evidence Failure is a Level 3.5 research track grounded in frozen P0 observations.",
                "Local denominators can be reported with explicit frozen-set boundaries.",
                "Failure families can be used to define next tests, strata, and negative controls.",
            ],
            "blocked_claims": [
                "Concurrency failure rates are known for a broader population.",
                "The frozen P0 set reaches Level 4 probability evidence.",
                "Qualitative mini-review contamination is an empirical outcome label.",
                "needs_more_evidence rows are successes or failures.",
            ],
        },
        "next_tests": [
            "Stratify by action_type, temporal authority, operator visual verdict, and identity flag profile.",
            "Add baseline replay for stale-read and decision-time-only policies.",
            "Audit micro-review responses for context contamination before any label ingestion.",
            "Define negative controls where true evidence is current, identity-stable, and action-authorized.",
        ],
        "level4_probability_claim_allowed": False,
        "production_truth_mutation": False,
        "external_calls_used_by_builder": False,
        "raw_source_rows_read": False,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def build_note(summary: dict[str, Any]) -> str:
    if summary["status"] != "pass":
        return "\n".join(
            [
                "# Concurrent Evidence Failure",
                "",
                "Status: blocked",
                "",
                "Failure reasons:",
                *[f"- {reason}" for reason in summary.get("failure_reasons", [])],
                "",
            ]
        )

    rows = [
        [
            f"`{row['family_id']}`",
            f"{row['numerator']}/{row['denominator']}" if row["denominator"] else "qualitative",
            row["local_rate"] or "n/a",
            row["local_observation"],
            row["claim_boundary"],
        ]
        for row in summary["failure_families"]
    ]
    return "\n".join(
        [
            "# Concurrent Evidence Failure",
            "",
            "Status: Level 3.5 research track",
            f"Generated at: `{summary['generated_at_utc']}`",
            "Level 4 probability claim allowed: `false`",
            "",
            "## Short Claim",
            "",
            "```text",
            summary["short_claim"],
            "```",
            "",
            "## Why It Matters",
            "",
            "A model can use a true observation at the wrong action boundary. The failure is not simply bad reasoning; it is a mismatch between evidence time, target identity, authority, and materialization state.",
            "",
            "## Local Frozen-Set Signals",
            "",
            *markdown_table(["Family", "Local Count", "Local Rate", "Observation", "Boundary"], rows),
            "",
            "## Failure Family Definitions",
            "",
            *[
                f"- `{row['family_id']}`: {row['definition']} Test: {row['testable_prediction']}"
                for row in summary["failure_families"]
            ],
            "",
            "## Claim Boundary",
            "",
            "Allowed:",
            *[f"- {claim}" for claim in summary["claim_boundary"]["allowed_claims"]],
            "",
            "Blocked:",
            *[f"- {claim}" for claim in summary["claim_boundary"]["blocked_claims"]],
            "",
            "## Next Tests",
            "",
            *[f"- {test}" for test in summary["next_tests"]],
            "",
        ]
    )


def run(
    finding_summary_path: Path = DEFAULT_FINDING_SUMMARY,
    continuation_summary_path: Path = DEFAULT_CONTINUATION_SUMMARY,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "note": out_dir / "concurrent_evidence_failure_note.md",
        "failure_matrix": out_dir / "concurrent_evidence_failure_matrix.csv",
        "summary": out_dir / "concurrent_evidence_failure_summary.json",
        "manifest": out_dir / "concurrent_evidence_failure_manifest.json",
    }
    missing = [str(path) for path in (finding_summary_path, continuation_summary_path) if not path.exists()]
    if missing:
        summary = blocked_summary(f"missing required sources: {', '.join(missing)}", paths)
    else:
        finding_summary = read_json(finding_summary_path)
        continuation_summary = read_json(continuation_summary_path)
        summary = build_summary(finding_summary, continuation_summary, paths)
        summary["inputs"] = {
            "finding_summary": str(finding_summary_path),
            "continuation_summary": str(continuation_summary_path),
        }

    write_text(paths["note"], build_note(summary))
    write_csv(
        paths["failure_matrix"],
        summary.get("failure_families", []),
        [
            "family_id",
            "definition",
            "local_observation",
            "numerator",
            "denominator",
            "local_rate",
            "evidence_handle",
            "claim_boundary",
            "testable_prediction",
            "current_state",
            "allowed_claim",
            "blocked_claim",
        ],
    )
    write_json(paths["summary"], summary)
    write_json(
        paths["manifest"],
        {
            "generated_at_utc": summary["generated_at_utc"],
            "mode": summary["mode"],
            "schema_version": SCHEMA_VERSION,
            "status": summary["status"],
            "research_track": summary.get("research_track", ""),
            "failure_family_count": summary.get("failure_family_count", 0),
            "level4_probability_claim_allowed": False,
            "production_truth_mutation": False,
            "external_calls_used_by_builder": False,
            "raw_source_rows_read": False,
            "contains_customer_data": False,
            "contains_personal_data": False,
            "outputs": {key: str(value) for key, value in paths.items()},
        },
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finding-summary", type=Path, default=DEFAULT_FINDING_SUMMARY)
    parser.add_argument("--continuation-summary", type=Path, default=DEFAULT_CONTINUATION_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.finding_summary, args.continuation_summary, args.out_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
