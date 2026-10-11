#!/usr/bin/env python3
"""Build a current status and gap review for the concurrency research track.

This artifact intentionally separates the mature Level 3.5 concurrency work
from blocked Level 4 evidence. It also records that external mini-review or
paid-consulting-shaped replies cannot be counted as independent reviewer02
agreement.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUT_DIR = Path("outputs/latentatlas/concurrency_current_status_review_20260718")
DEFAULT_CONCURRENCY_SUMMARY = Path(
    "outputs/latentatlas/concurrent_evidence_failure_v1/concurrent_evidence_failure_summary.json"
)
DEFAULT_PROTOCOL_SUMMARY = Path(
    "outputs/latentatlas/concurrent_evidence_failure_protocol_v1/concurrent_evidence_failure_protocol_summary.json"
)
DEFAULT_LEVEL3_SUMMARY = Path(
    "outputs/latentatlas/action_time_level3_continuation_pack_v1/level3_continuation_summary.json"
)
DEFAULT_LEVEL4_SUMMARY = Path(
    "outputs/latentatlas/action_time_level4_data_engine_v1/action_time_level4_data_engine_summary.json"
)
DEFAULT_AGREEMENT_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_interreviewer_agreement_v1/interreviewer_agreement_summary.json"
)
DEFAULT_PAPER_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_empirical_paper_draft_v4/action_time_p0_empirical_paper_draft_summary.json"
)
DEFAULT_FIGURE_TABLE_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_figure_table_pack_v2/action_time_p0_figure_table_pack_summary.json"
)
DEFAULT_UNIT_DEDUP_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_unit_definition_dedup_v1/action_time_p0_unit_definition_dedup_summary.json"
)
DEFAULT_OVERCLAIM_AUDIT_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_overclaim_audit_v4/action_time_p0_overclaim_audit_summary.json"
)
DEFAULT_REVIEWER_TRIAGE = Path("outputs/latentatlas/action_time_second_reviewer_response_triage_20260715.md")

SCHEMA_VERSION = "latentatlas_concurrency_current_status_review_v1"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


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


def percent(numerator: int | float, denominator: int | float | None) -> str:
    if not denominator:
        return ""
    return f"{float(numerator) / float(denominator):.4f}"


def source_paths() -> dict[str, Path]:
    return {
        "concurrency_summary": DEFAULT_CONCURRENCY_SUMMARY,
        "protocol_summary": DEFAULT_PROTOCOL_SUMMARY,
        "level3_summary": DEFAULT_LEVEL3_SUMMARY,
        "level4_summary": DEFAULT_LEVEL4_SUMMARY,
        "agreement_summary": DEFAULT_AGREEMENT_SUMMARY,
        "paper_summary": DEFAULT_PAPER_SUMMARY,
        "figure_table_summary": DEFAULT_FIGURE_TABLE_SUMMARY,
        "unit_dedup_summary": DEFAULT_UNIT_DEDUP_SUMMARY,
        "overclaim_audit_summary": DEFAULT_OVERCLAIM_AUDIT_SUMMARY,
        "reviewer_triage": DEFAULT_REVIEWER_TRIAGE,
    }


def output_paths(out_dir: Path) -> dict[str, Path]:
    return {
        "report": out_dir / "concurrency_current_status_review.md",
        "gap_matrix": out_dir / "concurrency_gap_matrix.csv",
        "next_work_plan": out_dir / "concurrency_next_work_plan.md",
        "summary": out_dir / "concurrency_current_status_summary.json",
        "manifest": out_dir / "concurrency_current_status_manifest.json",
    }


def blocked_summary(reason: str, paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_concurrency_current_status_review",
        "schema_version": SCHEMA_VERSION,
        "status": "blocked",
        "failure_reasons": [reason],
        "research_maturity_level": "blocked",
        "level4_probability_claim_allowed": False,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def reviewer_state(triage_text: str, agreement: dict[str, Any], level4: dict[str, Any]) -> dict[str, Any]:
    review_metrics = level4.get("review_metrics", {})
    observed_hamit_classes = [
        marker
        for marker in ["paid_only_scope_meeting", "accepts_mini_review_examples_only", "mini_review_pdf_sent_awaiting_response"]
        if marker in triage_text
    ]
    return {
        "full_reviewer02_state": agreement.get("status"),
        "agreement_calculable": bool(agreement.get("agreement_calculable")),
        "completed_second_review_rows": agreement.get("completed_second_review_rows"),
        "missing_second_review_rows": agreement.get("missing_second_review_rows"),
        "minimum_independent_review_count": review_metrics.get("minimum_reviewed_outcome_count"),
        "current_independent_human_review_count": review_metrics.get("current_independent_human_review_count"),
        "minimum_additional_independent_reviews_needed": review_metrics.get(
            "minimum_additional_independent_reviews_needed"
        ),
        "observed_external_reply_classes": observed_hamit_classes,
        "decision": "do_not_count_mini_review_or_paid_consulting_replies_as_level4_reviewer02_evidence",
    }


def current_position(
    concurrency: dict[str, Any],
    protocol: dict[str, Any],
    level3: dict[str, Any],
    level4: dict[str, Any],
    agreement: dict[str, Any],
    paper: dict[str, Any],
    figure_table: dict[str, Any],
    unit_dedup: dict[str, Any],
    overclaim: dict[str, Any],
    triage_text: str,
) -> dict[str, Any]:
    review_metrics = level4.get("review_metrics", {})
    denominators = concurrency.get("denominators") or level3.get("denominators") or paper.get("denominators") or {}
    outcome_counts = concurrency.get("outcome_counts") or level3.get("outcome_counts") or paper.get("outcome_counts") or {}
    family_count = concurrency.get("failure_family_count") or protocol.get("family_count") or 0
    return {
        "research_maturity_level": "level3_5_protocol_plus_descriptive_local_evidence",
        "public_working_claim": concurrency.get("short_claim", ""),
        "highest_allowed_claim": (
            "Concurrent Evidence Failure is a Level 3.5 research track grounded in frozen masked P0 "
            "observations; local denominators may be reported only with explicit frozen-set boundaries."
        ),
        "current_not_level4_reasons": [
            "No completed reviewer02 sheet exists for the frozen P0 set.",
            "Inter-reviewer agreement, kappa, and reliability language are not calculable.",
            "Only 386/3000 independent human reviews are complete for the Level 4 minimum.",
            "The prepared 2,614-review backfill queue has not been executed.",
            "Major strata remain under-covered.",
            "Baseline replay for stale_read and materialization_race is not complete.",
            "Holdout or later-period replication is not complete.",
            "External mini-review or paid-consulting-shaped replies are qualitative signals only.",
        ],
        "done": {
            "failure_family_count": family_count,
            "protocol_family_count": protocol.get("family_count"),
            "frozen_reviewed_rows": denominators.get("frozen_reviewed_rows"),
            "outcome_ready_p0_rows": denominators.get("outcome_ready_p0_rows"),
            "resolved_reviewed_rows": denominators.get("resolved_reviewed_rows"),
            "outcome_counts": outcome_counts,
            "paper_status": paper.get("status"),
            "paper_title": paper.get("title"),
            "figure_table_status": figure_table.get("status"),
            "figure_count": figure_table.get("figure_count"),
            "table_count": figure_table.get("table_count"),
            "unit_dedup_status": unit_dedup.get("status"),
            "duplicate_subject_cluster_count": unit_dedup.get("duplicate_subject_cluster_count"),
            "overclaim_audit_status": overclaim.get("status"),
            "overclaim_issue_count": overclaim.get("issue_count"),
        },
        "failure_families": concurrency.get("failure_families", []),
        "reviewer_state": reviewer_state(triage_text, agreement, level4),
        "level4_state": {
            "status": level4.get("status"),
            "level4_probability_claim_allowed": bool(level4.get("level4_probability_claim_allowed")),
            "current_independent_human_review_count": review_metrics.get("current_independent_human_review_count"),
            "minimum_reviewed_outcome_count": review_metrics.get("minimum_reviewed_outcome_count"),
            "selected_backfill_queue_count": review_metrics.get("selected_backfill_queue_count"),
            "second_review_completed_rows": review_metrics.get("second_review_completed_rows"),
            "second_review_missing_rows": review_metrics.get("second_review_missing_rows"),
            "total_stratum_gap_count": review_metrics.get("total_stratum_gap_count"),
            "independent_review_stratum_gap_count": review_metrics.get("independent_review_stratum_gap_count"),
            "additional_source_events_needed_for_target": review_metrics.get("additional_source_events_needed_for_target"),
        },
        "claim_boundary": {
            "allowed_claims": [
                "Level 3.5 systems/protocol contribution.",
                "Frozen P0 descriptive outcome distribution with explicit denominators.",
                "Family-specific local observations with their local denominators and claim boundaries.",
                "Negative controls, required fields, and replay protocol as next work.",
            ],
            "blocked_claims": [
                "Level 4 probability evidence.",
                "Population concurrency rates.",
                "Reviewer agreement or reliability claims.",
                "Mini-review as full reviewer02 substitution.",
                "Customer-facing or production truth mutation.",
            ],
        },
    }


def build_gap_rows(position: dict[str, Any]) -> list[dict[str, Any]]:
    level4_state = position["level4_state"]
    reviewer = position["reviewer_state"]
    return [
        {
            "gap_id": "reviewer02_unavailable",
            "current_evidence": f"{reviewer.get('completed_second_review_rows')}/{reviewer.get('missing_second_review_rows')} completed/missing P0 reviewer02 rows",
            "why_it_matters": "No agreement, kappa, or independent reliability language can be claimed.",
            "required_next_work": "Stop treating unpaid full reviewer as the blocking path; use internal replication now and only count a full completed reviewer02 sheet later.",
            "promotion_gate": "Validated completed reviewer02 sheet and agreement artifact.",
            "priority": 1,
            "status": "blocked_external_dependency",
        },
        {
            "gap_id": "required_fields_missing",
            "current_evidence": "Protocol defines fields, but masked packets do not yet enforce them as required evidence columns for every family.",
            "why_it_matters": "Concurrency cannot be measured consistently without timestamps, identity hashes, authority windows, visibility state, and materialization state.",
            "required_next_work": "Upgrade masked packet schema with family-specific required evidence fields.",
            "promotion_gate": "Schema validation fails rows missing required fields per family.",
            "priority": 2,
            "status": "ready_to_build",
        },
        {
            "gap_id": "negative_controls_missing",
            "current_evidence": "Protocol lists negative controls; fixture pack and automated assertions are not yet built.",
            "why_it_matters": "Without negative controls, every suspicious temporal pattern can look like a concurrency failure.",
            "required_next_work": "Build at least one negative-control fixture per family before expanding counts.",
            "promotion_gate": "Negative-control fixture suite passes and prevents false promotion.",
            "priority": 3,
            "status": "ready_to_build",
        },
        {
            "gap_id": "baseline_replay_missing",
            "current_evidence": "Next tests name stale-read and decision-time-only replay, but replay artifact is not complete.",
            "why_it_matters": "We need to compare policies, not only describe cases after the fact.",
            "required_next_work": "Replay stale_read and materialization_race rows against decision-time-only and action-time freshness policies.",
            "promotion_gate": "Replay report shows delta by family and action_type with frozen inputs.",
            "priority": 4,
            "status": "ready_to_build_after_schema_fields",
        },
        {
            "gap_id": "small_family_denominators",
            "current_evidence": "Some families have local denominators of 4, 7, or qualitative 0/0.",
            "why_it_matters": "These can support hypotheses but not stable rate claims.",
            "required_next_work": "Use active sampling to fill each meaningful family/stratum toward a predeclared floor.",
            "promotion_gate": "Per-family and per-stratum denominators meet predeclared minimums.",
            "priority": 5,
            "status": "blocked_by_source_collection",
        },
        {
            "gap_id": "backfill_review_unexecuted",
            "current_evidence": (
                f"{level4_state.get('current_independent_human_review_count')}/"
                f"{level4_state.get('minimum_reviewed_outcome_count')} independent reviews complete; "
                f"{level4_state.get('selected_backfill_queue_count')} queued."
            ),
            "why_it_matters": "The Level 4 minimum is reachable in principle but not achieved in evidence.",
            "required_next_work": "Run masked backfill review batches and accept only validated outputs.",
            "promotion_gate": "3,000 reviewed outcomes complete with no schema/audit failure.",
            "priority": 6,
            "status": "blocked_by_review_execution",
        },
        {
            "gap_id": "holdout_replication_missing",
            "current_evidence": "No later-period or partner holdout replication artifact is recorded.",
            "why_it_matters": "A single frozen set can be descriptive but cannot carry broad generalization by itself.",
            "required_next_work": "Freeze a later holdout set or partner-safe replication set with the same schema.",
            "promotion_gate": "Holdout results reproduce directionally without claim-boundary violations.",
            "priority": 7,
            "status": "future_work",
        },
        {
            "gap_id": "mini_review_grounding_audit_missing",
            "current_evidence": "Mini-review packet was shared, but response is not a validated grounded label artifact.",
            "why_it_matters": "External commentary can contaminate evidence if it imports non-packet facts.",
            "required_next_work": "If a response arrives, audit each rationale for packet-only grounding before logging it as qualitative signal.",
            "promotion_gate": "Grounding audit complete; labels remain excluded from full agreement unless scope matches reviewer02.",
            "priority": 8,
            "status": "waiting_for_response",
        },
    ]


def build_next_work_plan(gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "workstream": "schema_required_fields",
            "objective": "Make every concurrency family measurable from packet-visible evidence.",
            "deliverable": "Masked packet schema extension plus validation failure report.",
            "depends_on": "",
            "acceptance": "Rows missing family-required fields fail fast and remain excluded from stronger claims.",
        },
        {
            "step": 2,
            "workstream": "negative_control_fixtures",
            "objective": "Prove the detector does not call every temporal mismatch a concurrency failure.",
            "deliverable": "Negative-control fixture CSV/JSON plus unit tests.",
            "depends_on": "schema_required_fields",
            "acceptance": "Each family has at least one passing negative control and one failing positive fixture.",
        },
        {
            "step": 3,
            "workstream": "baseline_replay",
            "objective": "Measure decision-time-only vs action-time freshness policy behavior.",
            "deliverable": "Replay report for stale_read and materialization_race.",
            "depends_on": "schema_required_fields, negative_control_fixtures",
            "acceptance": "Replay outputs deltas by action_type and keeps unresolved cases separate.",
        },
        {
            "step": 4,
            "workstream": "stratified_backfill_review",
            "objective": "Fill weak families and strata without overclaiming.",
            "deliverable": "Active sampling plan and validated batch review outputs.",
            "depends_on": "baseline_replay",
            "acceptance": "Meaningful family/stratum floors are met before any stronger rate language.",
        },
        {
            "step": 5,
            "workstream": "reviewer_strategy_pivot",
            "objective": "Stop waiting for free full reviewer while preserving external validation path.",
            "deliverable": "Reviewer path policy: internal replication first, blind micro-reviews as qualitative only, partner/paid review later if budgeted.",
            "depends_on": "",
            "acceptance": "No mini-review, consulting reply, or referral is counted as Level 4 reviewer02 evidence.",
        },
    ]


def build_summary(
    sources: dict[str, Path],
    paths: dict[str, Path],
) -> dict[str, Any]:
    missing = [str(path) for path in sources.values() if not path.exists()]
    if missing:
        return blocked_summary(f"missing required sources: {', '.join(missing)}", paths)

    concurrency = read_json(sources["concurrency_summary"])
    protocol = read_json(sources["protocol_summary"])
    level3 = read_json(sources["level3_summary"])
    level4 = read_json(sources["level4_summary"])
    agreement = read_json(sources["agreement_summary"])
    paper = read_json(sources["paper_summary"])
    figure_table = read_json(sources["figure_table_summary"])
    unit_dedup = read_json(sources["unit_dedup_summary"])
    overclaim = read_json(sources["overclaim_audit_summary"])
    triage_text = read_text(sources["reviewer_triage"])

    expected_pass = {
        "concurrency_summary": concurrency.get("status") == "pass",
        "protocol_summary": protocol.get("status") == "pass",
        "level3_summary": level3.get("status") == "pass",
        "paper_summary": paper.get("status") == "pass",
        "figure_table_summary": figure_table.get("status") == "pass",
        "unit_dedup_summary": unit_dedup.get("status") == "pass",
        "overclaim_audit_summary": overclaim.get("status") == "pass",
        "agreement_summary_waiting": agreement.get("status") == "waiting_for_second_reviewer",
        "level4_summary_blocked": level4.get("status") == "review_engine_ready_level4_blocked",
    }
    failed_expectations = [name for name, ok in expected_pass.items() if not ok]
    if failed_expectations:
        return blocked_summary(f"unexpected source status: {', '.join(failed_expectations)}", paths)

    position = current_position(
        concurrency,
        protocol,
        level3,
        level4,
        agreement,
        paper,
        figure_table,
        unit_dedup,
        overclaim,
        triage_text,
    )
    gaps = build_gap_rows(position)
    plan = build_next_work_plan(gaps)
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_concurrency_current_status_review",
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        **position,
        "gap_count": len(gaps),
        "gaps": gaps,
        "next_work_plan": plan,
        "recommended_start": "schema_required_fields",
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "inputs": {key: str(value) for key, value in sources.items()},
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def build_report(summary: dict[str, Any]) -> str:
    if summary["status"] != "pass":
        return "\n".join(
            [
                "# Concurrency Current Status Review",
                "",
                f"Generated at: `{summary['generated_at_utc']}`",
                f"Status: `{summary['status']}`",
                "",
                "## Failure Reasons",
                "",
                *[f"- {reason}" for reason in summary.get("failure_reasons", [])],
                "",
            ]
        )

    done = summary["done"]
    reviewer = summary["reviewer_state"]
    level4 = summary["level4_state"]
    gaps = summary["gaps"]
    family_rows = [
        [
            f"`{family['family_id']}`",
            f"{family.get('numerator')}/{family.get('denominator')}",
            family.get("local_rate", ""),
            family.get("claim_boundary", ""),
        ]
        for family in summary.get("failure_families", [])
    ]
    lines = [
        "# Concurrency Current Status Review",
        "",
        f"Generated at: `{summary['generated_at_utc']}`",
        f"Status: `{summary['status']}`",
        f"Research maturity: `{summary['research_maturity_level']}`",
        "",
        "## Executive Read",
        "",
        summary["highest_allowed_claim"],
        "",
        "This is not Level 4. The current work is strong enough for a bounded Paper A / Level 3.5 protocol claim, but not for population probability, reviewer reliability, or production truth claims.",
        "",
        "## What Is Already Solid",
        "",
        *markdown_table(
            ["Item", "State"],
            [
                ["Failure families", done["failure_family_count"]],
                ["Frozen reviewed P0 rows", done["frozen_reviewed_rows"]],
                ["Resolved reviewed rows", done["resolved_reviewed_rows"]],
                ["Outcome counts", json.dumps(done["outcome_counts"], sort_keys=True)],
                ["Paper draft", f"{done['paper_status']} - {done['paper_title']}"],
                ["Figure/table pack", f"{done['figure_table_status']} - {done['figure_count']} figures, {done['table_count']} tables"],
                ["Unit/dedup audit", f"{done['unit_dedup_status']} - duplicate subject clusters {done['duplicate_subject_cluster_count']}"],
                ["Overclaim audit", f"{done['overclaim_audit_status']} - issues {done['overclaim_issue_count']}"],
            ],
        ),
        "",
        "## Failure Families",
        "",
        *markdown_table(["Family", "Local Count", "Local Rate", "Boundary"], family_rows),
        "",
        "## Reviewer Reality",
        "",
        *markdown_table(
            ["Reviewer Signal", "State"],
            [
                ["Full reviewer02", reviewer["full_reviewer02_state"]],
                ["Agreement calculable", reviewer["agreement_calculable"]],
                ["P0 reviewer02 rows", f"{reviewer['completed_second_review_rows']} complete / {reviewer['missing_second_review_rows']} missing"],
                ["Independent reviews", f"{reviewer['current_independent_human_review_count']}/{reviewer['minimum_independent_review_count']}"],
                ["Observed external reply classes", ", ".join(reviewer["observed_external_reply_classes"])],
                ["Decision", reviewer["decision"]],
            ],
        ),
        "",
        "## Why Level 4 Is Still Blocked",
        "",
        *[f"- {reason}" for reason in summary["current_not_level4_reasons"]],
        "",
        "## Gap Matrix",
        "",
        *markdown_table(
            ["Priority", "Gap", "Status", "Required Next Work"],
            [[gap["priority"], f"`{gap['gap_id']}`", gap["status"], gap["required_next_work"]] for gap in gaps],
        ),
        "",
        "## Level 4 State",
        "",
        *markdown_table(
            ["Metric", "Value"],
            [
                ["Status", level4["status"]],
                ["Level 4 probability claim allowed", level4["level4_probability_claim_allowed"]],
                ["Independent human reviews", f"{level4['current_independent_human_review_count']}/{level4['minimum_reviewed_outcome_count']}"],
                ["Queued backfill reviews", level4["selected_backfill_queue_count"]],
                ["P0 reviewer02 rows", f"{level4['second_review_completed_rows']} complete / {level4['second_review_missing_rows']} missing"],
                ["Total stratum gaps", level4["total_stratum_gap_count"]],
                ["Independent-review stratum gaps", level4["independent_review_stratum_gap_count"]],
                ["Additional source events needed for 5,000 target", level4["additional_source_events_needed_for_target"]],
            ],
        ),
        "",
        "## Blocked Claims",
        "",
        *[f"- {claim}" for claim in summary["claim_boundary"]["blocked_claims"]],
        "",
        "## Data Boundary",
        "",
        "- Contains customer data: false",
        "- Contains personal data: false",
        "- Raw source rows read: false",
        "- External calls used by builder: false",
        "- Production truth mutation: false",
        "",
    ]
    return "\n".join(lines)


def build_plan_doc(summary: dict[str, Any]) -> str:
    if summary["status"] != "pass":
        return "\n".join(["# Concurrency Next Work Plan", "", "Status: blocked", ""])

    rows = summary["next_work_plan"]
    lines = [
        "# Concurrency Next Work Plan",
        "",
        f"Generated at: `{summary['generated_at_utc']}`",
        f"Recommended start: `{summary['recommended_start']}`",
        "",
        *markdown_table(
            ["Step", "Workstream", "Objective", "Deliverable", "Acceptance"],
            [
                [
                    row["step"],
                    f"`{row['workstream']}`",
                    row["objective"],
                    row["deliverable"],
                    row["acceptance"],
                ]
                for row in rows
            ],
        ),
        "",
        "## Reviewer Strategy",
        "",
        "Do not keep waiting for a free full reviewer as the main path. Continue with internal replication, schema enforcement, negative controls, and replay. Treat external mini-review replies as qualitative grounding signals unless they return a validated full reviewer02 response sheet.",
        "",
    ]
    return "\n".join(lines)


def run(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = source_paths()
    paths = output_paths(out_dir)
    summary = build_summary(sources, paths)

    write_text(paths["report"], build_report(summary))
    write_csv(
        paths["gap_matrix"],
        summary.get("gaps", []),
        ["priority", "gap_id", "status", "current_evidence", "why_it_matters", "required_next_work", "promotion_gate"],
    )
    write_text(paths["next_work_plan"], build_plan_doc(summary))
    write_json(paths["summary"], summary)
    write_json(
        paths["manifest"],
        {
            "generated_at_utc": summary["generated_at_utc"],
            "mode": summary["mode"],
            "schema_version": summary.get("schema_version", SCHEMA_VERSION),
            "status": summary["status"],
            "research_maturity_level": summary.get("research_maturity_level"),
            "level4_probability_claim_allowed": False,
            "contains_customer_data": False,
            "contains_personal_data": False,
            "external_calls_used_by_builder": False,
            "production_truth_mutation": False,
            "outputs": {key: str(value) for key, value in paths.items()},
        },
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.out_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
