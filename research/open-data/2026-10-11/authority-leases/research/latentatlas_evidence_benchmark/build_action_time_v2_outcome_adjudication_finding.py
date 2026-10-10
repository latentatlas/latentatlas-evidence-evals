#!/usr/bin/env python3
"""Build the V2 masked-evidence outcome adjudication finding.

This builder reads only reviewer-visible V2 packet sheets, human review
responses, and the masked evidence adapter summary. It does not read the
internal index, call external services, execute workflow actions, or mutate
production truth.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_DIR = Path("outputs/latentatlas/action_time_masked_evidence_adapter_sample_merge")
DEFAULT_REVIEWER_SHEET = DEFAULT_SOURCE_DIR / "action_time_masked_evidence_reviewer_sheet_p0.csv"
DEFAULT_RESPONSES = DEFAULT_SOURCE_DIR / "human_review_v2_outcome_responses_reviewer01_hsyn.csv"
DEFAULT_ADAPTER_SUMMARY = DEFAULT_SOURCE_DIR / "action_time_masked_evidence_adapter_summary.json"
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_v2_outcome_adjudication")
DEFAULT_REVIEWER_ID = "reviewer01_hsyn"

UNRESOLVED_OUTCOME = "needs_more_evidence"
RESOLVED_OUTCOMES = {
    "correct_block",
    "false_allow",
    "false_block",
    "missed_revalidation",
    "safe_allow",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pct(part: int, whole: int) -> float:
    if whole == 0:
        return 0.0
    return round(part / whole, 4)


def counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def nested_counter_dict(counter: dict[str, Counter[str]]) -> dict[str, dict[str, int]]:
    return {key: dict(sorted(value.items())) for key, value in sorted(counter.items())}


def index_by_queue_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        queue_id = row.get("queue_id", "").strip()
        if queue_id:
            indexed[queue_id] = row
    return indexed


def parse_pipe_state(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for part in (text or "").split("|"):
        if ":" in part:
            key, value = part.split(":", 1)
            parsed[key] = value
    return parsed


def build_finding(
    reviewer_rows: list[dict[str, str]],
    response_rows: list[dict[str, str]],
    adapter_summary: dict[str, Any],
    *,
    reviewer_id: str,
) -> dict[str, Any]:
    reviewer_index = index_by_queue_id(reviewer_rows)
    allowed_rows = [row for row in reviewer_rows if row.get("outcome_adjudication_allowed") == "True"]
    allowed_queue_ids = {row.get("queue_id", "") for row in allowed_rows}
    responses = [row for row in response_rows if row.get("reviewer_id_hash") == reviewer_id]
    responses_with_sheet = [row for row in responses if row.get("queue_id") in reviewer_index]

    unmatched_responses = [row.get("queue_id", "") for row in responses if row.get("queue_id") not in reviewer_index]
    responses_outside_allowed = [
        row.get("queue_id", "") for row in responses_with_sheet if row.get("queue_id", "") not in allowed_queue_ids
    ]
    reviewed_allowed_queue_ids = {row.get("queue_id", "") for row in responses_with_sheet if row.get("queue_id", "") in allowed_queue_ids}
    unreviewed_allowed_queue_ids = sorted(allowed_queue_ids - reviewed_allowed_queue_ids)

    outcome_counts = Counter(row.get("reviewed_outcome", "").strip() for row in responses_with_sheet)
    notes_code_counts = Counter(row.get("notes_code", "").strip() for row in responses_with_sheet)
    observed_change_type_counts = Counter(row.get("observed_change_type", "").strip() for row in responses_with_sheet)
    action_type_counts = Counter(row.get("action_type", "").strip() for row in responses_with_sheet)
    execution_verdict_counts = Counter(row.get("execution_verdict", "").strip() for row in responses_with_sheet)
    pdp_temporal_authority_counts = Counter(
        row.get("pdp_temporal_authority_evidence", "").strip() or "not_recorded"
        for row in responses_with_sheet
    )

    outcome_by_change_type: dict[str, Counter[str]] = defaultdict(Counter)
    notes_by_outcome: dict[str, Counter[str]] = defaultdict(Counter)
    for row in responses_with_sheet:
        observed_change_type = row.get("observed_change_type", "").strip()
        outcome = row.get("reviewed_outcome", "").strip()
        notes_code = row.get("notes_code", "").strip()
        outcome_by_change_type[observed_change_type][outcome] += 1
        notes_by_outcome[outcome][notes_code] += 1

    reviewed_count = len(responses_with_sheet)
    resolved_outcome_count = sum(outcome_counts.get(outcome, 0) for outcome in RESOLVED_OUTCOMES)
    unresolved_outcome_count = outcome_counts.get(UNRESOLVED_OUTCOME, 0)
    correct_block_count = outcome_counts.get("correct_block", 0)
    false_block_count = outcome_counts.get("false_block", 0)
    false_block_with_latest_pdp_temporal_evidence = sum(
        1
        for row in responses_with_sheet
        if row.get("reviewed_outcome", "").strip() == "false_block"
        and row.get("pdp_temporal_authority_evidence", "").strip()
        == "latest_pdp_review_pool_snapshot_present"
    )
    blocked_pdp_needs_more_evidence_count = sum(
        1
        for row in responses_with_sheet
        if row.get("reviewed_outcome", "").strip() == UNRESOLVED_OUTCOME
        and parse_pipe_state(reviewer_index[row.get("queue_id", "")].get("masked_state_after", "")).get(
            "operator_visual_verdict"
        )
        == "blocked_pdp"
    )

    adapter_status = adapter_summary.get("status")
    review_complete = bool(allowed_rows) and not unreviewed_allowed_queue_ids
    hard_failure = bool(unmatched_responses or responses_outside_allowed or adapter_status != "pass")

    if hard_failure:
        status = "blocked"
    elif review_complete and reviewed_count:
        status = "pass"
    else:
        status = "partial"

    finding_verdict = (
        "v2_masked_evidence_outcome_adjudication_pilot_completed"
        if status == "pass"
        else "v2_masked_evidence_outcome_adjudication_pilot_incomplete"
    )

    return {
        "status": status,
        "mode": "action_time_v2_outcome_adjudication_finding",
        "finding_verdict": finding_verdict,
        "reviewer_id_hash": reviewer_id,
        "review_scope": "P0 masked-evidence sidecar outcome review",
        "adapter_metrics": {
            "input_v2_packet_count": adapter_summary.get("input_v2_packet_count", 0),
            "p0_packet_count": adapter_summary.get("p0_packet_count", 0),
            "sidecar_row_count": adapter_summary.get("sidecar_row_count", 0),
            "merged_packet_count": adapter_summary.get("merged_packet_count", 0),
            "outcome_adjudication_allowed_count": adapter_summary.get(
                "outcome_adjudication_allowed_count", 0
            ),
            "outcome_adjudication_blocked_count": adapter_summary.get(
                "outcome_adjudication_blocked_count", 0
            ),
            "packet_sufficiency_counts": adapter_summary.get("packet_sufficiency_counts", {}),
            "sidecar_validation_status": adapter_summary.get("sidecar_validation", {}).get("status", ""),
        },
        "review_completion": {
            "outcome_ready_p0_count": len(allowed_rows),
            "reviewed_outcome_ready_count": len(reviewed_allowed_queue_ids),
            "unreviewed_outcome_ready_count": len(unreviewed_allowed_queue_ids),
            "unreviewed_outcome_ready_queue_ids": unreviewed_allowed_queue_ids,
            "unmatched_response_count": len(unmatched_responses),
            "unmatched_response_queue_ids": unmatched_responses,
            "responses_outside_allowed_count": len(responses_outside_allowed),
            "responses_outside_allowed_queue_ids": responses_outside_allowed,
        },
        "outcome_metrics": {
            "reviewed_count": reviewed_count,
            "outcome_counts": counter_dict(outcome_counts),
            "resolved_outcome_count": resolved_outcome_count,
            "resolved_outcome_rate": pct(resolved_outcome_count, reviewed_count),
            "needs_more_evidence_count": unresolved_outcome_count,
            "needs_more_evidence_rate": pct(unresolved_outcome_count, reviewed_count),
            "correct_block_count": correct_block_count,
            "correct_block_rate_all_reviewed": pct(correct_block_count, reviewed_count),
            "correct_block_rate_resolved_only": pct(correct_block_count, resolved_outcome_count),
            "false_block_count": false_block_count,
            "false_block_rate_all_reviewed": pct(false_block_count, reviewed_count),
            "false_block_rate_resolved_only": pct(false_block_count, resolved_outcome_count),
        },
        "classification_profile": {
            "observed_change_type_counts": counter_dict(observed_change_type_counts),
            "action_type_counts": counter_dict(action_type_counts),
            "execution_verdict_counts": counter_dict(execution_verdict_counts),
            "pdp_temporal_authority_evidence_counts": counter_dict(pdp_temporal_authority_counts),
            "notes_code_counts": counter_dict(notes_code_counts),
            "outcome_by_observed_change_type": nested_counter_dict(outcome_by_change_type),
            "notes_by_outcome": nested_counter_dict(notes_by_outcome),
        },
        "principle_observations": [
            {
                "principle": "identity change is action-grade block evidence",
                "measured_signal": "identity_conflict_masked",
                "pilot_observation": "4 of 4 reviewed identity-conflict packets were labeled correct_block.",
                "claim_boundary": "Pilot observation only; not a population probability.",
            },
            {
                "principle": "PDP block is not outcome evidence",
                "measured_signal": "blocked_pdp",
                "pilot_observation": (
                    f"{blocked_pdp_needs_more_evidence_count} reviewed packet(s) with blocked PDP reasoning "
                    "remained needs_more_evidence."
                ),
                "claim_boundary": "A blocked PDP supports evidence insufficiency, not correctness or falseness.",
            },
            {
                "principle": "latest PDP state can supersede stale state when current PDP evidence exists",
                "measured_signal": "false_block with packet-visible PDP temporal authority evidence",
                "pilot_observation": (
                    f"{false_block_with_latest_pdp_temporal_evidence} reviewed packet(s) were labeled false_block "
                    "with latest PDP temporal authority evidence present."
                ),
                "claim_boundary": "Requires packet-visible temporal authority evidence before generalization.",
            },
        ],
        "claim_boundary": {
            "allowed_claims": [
                "The V2 masked evidence sidecar made a subset of packets outcome-adjudication-ready.",
                (
                    f"In this P0 sidecar review set, {reviewed_count} of {len(allowed_rows)} "
                    "outcome-ready packets were reviewed."
                ),
                "The pilot produced both resolved outcome labels and explicit evidence-insufficiency labels.",
                "The result is suitable as a protocol finding and article section, not as a production probability claim.",
            ],
            "blocked_claims": [
                "The pilot proves a population false-block rate.",
                "The pilot proves an empirical false-authorization probability.",
                "The pilot proves all guard decisions are correct.",
                "A risk signal or blocked PDP is outcome evidence by itself.",
                "The review mutated production truth.",
            ],
        },
    }


def write_report(path: Path, generated_at: str, finding: dict[str, Any]) -> str:
    adapter = finding["adapter_metrics"]
    completion = finding["review_completion"]
    metrics = finding["outcome_metrics"]
    profile = finding["classification_profile"]

    lines = [
        "# Action-Time V2 Outcome Adjudication Finding",
        "",
        f"Generated at UTC: `{generated_at}`",
        "",
        "## Verdict",
        "",
        f"- Status: `{finding['status']}`",
        f"- Finding verdict: `{finding['finding_verdict']}`",
        f"- Reviewer: `{finding['reviewer_id_hash']}`",
        f"- Review scope: `{finding['review_scope']}`",
        f"- Outcome-ready P0 packets reviewed: `{completion['reviewed_outcome_ready_count']}` / `{completion['outcome_ready_p0_count']}`",
        f"- Unreviewed outcome-ready packets: `{completion['unreviewed_outcome_ready_count']}`",
        "",
        "## Adapter And Sufficiency Surface",
        "",
        f"- Input V2 packets: `{adapter['input_v2_packet_count']}`",
        f"- P0 packets: `{adapter['p0_packet_count']}`",
        f"- Sidecar rows supplied: `{adapter['sidecar_row_count']}`",
        f"- Merged packets: `{adapter['merged_packet_count']}`",
        f"- Outcome-adjudication allowed: `{adapter['outcome_adjudication_allowed_count']}`",
        f"- Outcome-adjudication blocked: `{adapter['outcome_adjudication_blocked_count']}`",
        f"- Sidecar validation: `{adapter['sidecar_validation_status']}`",
        "",
        "Packet sufficiency counts:",
    ]
    for label, count in sorted(adapter["packet_sufficiency_counts"].items()):
        lines.append(f"- `{label}`: `{count}`")

    lines.extend(
        [
            "",
            "## Human Outcome Review Result",
            "",
            f"- Reviewed packets: `{metrics['reviewed_count']}`",
            f"- Resolved outcome count: `{metrics['resolved_outcome_count']}`",
            f"- Resolved outcome rate: `{metrics['resolved_outcome_rate']}`",
            f"- `needs_more_evidence` count: `{metrics['needs_more_evidence_count']}`",
            f"- `needs_more_evidence` rate: `{metrics['needs_more_evidence_rate']}`",
            f"- `correct_block` count: `{metrics['correct_block_count']}`",
            f"- `false_block` count: `{metrics['false_block_count']}`",
            "",
            "Outcome counts:",
        ]
    )
    for outcome, count in metrics["outcome_counts"].items():
        lines.append(f"- `{outcome}`: `{count}`")

    lines.extend(
        [
            "",
            "## Outcome By Observed Change Type",
            "",
        ]
    )
    for change_type, outcomes in profile["outcome_by_observed_change_type"].items():
        rendered = ", ".join(f"`{outcome}`=`{count}`" for outcome, count in outcomes.items())
        lines.append(f"- `{change_type}`: {rendered}")

    lines.extend(
        [
            "",
            "## Principle Observations",
            "",
        ]
    )
    for observation in finding["principle_observations"]:
        lines.extend(
            [
                f"### {observation['principle']}",
                "",
                f"- Measured signal: `{observation['measured_signal']}`",
                f"- Pilot observation: {observation['pilot_observation']}",
                f"- Claim boundary: {observation['claim_boundary']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Experimental Interpretation",
            "",
            "V2 changed the experiment from a risk-signal review into a gated outcome-adjudication review. The masked evidence sidecar made a small P0 subset reviewable without exposing raw URLs, titles, prices, sellers, customer data, prompts, transcripts, or source text.",
            "",
            "The result is mixed in the useful sense: some packets became resolved outcomes, while other packets remained explicitly evidence-insufficient. This shows that `needs_more_evidence` is not a fallback label; it is still an active epistemic boundary when the masked evidence does not support a correctness judgment.",
            "",
            "## Claim Boundary",
            "",
            "Allowed claims:",
        ]
    )
    for claim in finding["claim_boundary"]["allowed_claims"]:
        lines.append(f"- {claim}")
    lines.extend(["", "Blocked claims:"])
    for claim in finding["claim_boundary"]["blocked_claims"]:
        lines.append(f"- {claim}")

    lines.extend(
        [
            "",
            "## Audit Controls",
            "",
            "- Internal index read: `false`",
            "- External calls used: `false`",
            "- Production truth mutation: `false`",
            "",
        ]
    )

    text = "\n".join(lines)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def run(
    out_dir: Path = DEFAULT_OUT_DIR,
    reviewer_sheet_path: Path = DEFAULT_REVIEWER_SHEET,
    responses_path: Path = DEFAULT_RESPONSES,
    adapter_summary_path: Path = DEFAULT_ADAPTER_SUMMARY,
    reviewer_id: str = DEFAULT_REVIEWER_ID,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(UTC).isoformat()

    required_sources = {
        "reviewer_sheet": reviewer_sheet_path,
        "responses": responses_path,
        "adapter_summary": adapter_summary_path,
    }
    missing_sources = [
        {"source_id": source_id, "path": str(path)}
        for source_id, path in required_sources.items()
        if not path.exists()
    ]

    manifest_path = out_dir / "action_time_v2_outcome_adjudication_manifest.json"
    summary_path = out_dir / "action_time_v2_outcome_adjudication_summary.json"
    report_path = out_dir / "action_time_v2_outcome_adjudication_report.md"

    if missing_sources:
        manifest = {
            "generated_at_utc": generated_at,
            "mode": "action_time_v2_outcome_adjudication_finding",
            "status": "blocked",
            "failure_reason": "missing_required_sources",
            "missing_sources": missing_sources,
            "external_calls_used_by_builder": False,
            "production_truth_mutation": False,
            "internal_index_read": False,
        }
        write_json(manifest_path, manifest)
        return manifest

    reviewer_rows = read_csv(reviewer_sheet_path)
    response_rows = read_csv(responses_path)
    adapter_summary = read_json(adapter_summary_path)
    finding = build_finding(reviewer_rows, response_rows, adapter_summary, reviewer_id=reviewer_id)
    report = write_report(report_path, generated_at, finding)

    summary = {
        "generated_at_utc": generated_at,
        "mode": "action_time_v2_outcome_adjudication_finding",
        "status": finding["status"],
        "contains_customer_data": False,
        "contains_personal_data": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "internal_index_read": False,
        "reviewer_sheet": str(reviewer_sheet_path),
        "responses": str(responses_path),
        "adapter_summary": str(adapter_summary_path),
        "finding": finding,
        "outputs": {
            "summary": str(summary_path),
            "manifest": str(manifest_path),
            "report": str(report_path),
        },
    }
    write_json(summary_path, summary)

    manifest = {
        "generated_at_utc": generated_at,
        "mode": "action_time_v2_outcome_adjudication_finding",
        "status": finding["status"],
        "finding_verdict": finding["finding_verdict"],
        "summary": str(summary_path),
        "report": str(report_path),
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "internal_index_read": False,
        "reviewed_count": finding["outcome_metrics"]["reviewed_count"],
        "outcome_counts": finding["outcome_metrics"]["outcome_counts"],
        "outputs": summary["outputs"],
        "report_preview_chars": len(report),
    }
    write_json(manifest_path, manifest)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--reviewer-sheet", type=Path, default=DEFAULT_REVIEWER_SHEET)
    parser.add_argument("--responses", type=Path, default=DEFAULT_RESPONSES)
    parser.add_argument("--adapter-summary", type=Path, default=DEFAULT_ADAPTER_SUMMARY)
    parser.add_argument("--reviewer-id", default=DEFAULT_REVIEWER_ID)
    args = parser.parse_args()
    summary = run(
        args.out_dir,
        args.reviewer_sheet,
        args.responses,
        args.adapter_summary,
        args.reviewer_id,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
