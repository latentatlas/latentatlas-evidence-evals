#!/usr/bin/env python3
"""Build a blind second-reviewer pack for the LatentAtlas action-time P0 set."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_REVIEWER_SHEET = Path(
    "outputs/latentatlas/action_time_masked_evidence_adapter_p0_full/action_time_masked_evidence_reviewer_sheet_p0.csv"
)
DEFAULT_FREEZE_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_review_freeze_v1/action_time_p0_review_freeze_summary.json"
)
DEFAULT_UNIT_DEDUP_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_unit_definition_dedup_v1/action_time_p0_unit_definition_dedup_summary.json"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_p0_reviewer_pack_v1")

REVIEWER_PACK_SCHEMA_VERSION = "latentatlas_action_time_p0_reviewer_pack_v1"
URL_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)

BLIND_CASE_FIELDS = [
    "case_id",
    "queue_id",
    "event_id",
    "priority_rank",
    "priority_band",
    "action_type",
    "execution_verdict",
    "signal_claimed_change_type",
    "observed_change_type",
    "lease_validity_relationship",
    "pdp_temporal_authority_evidence",
    "decision_causal_link",
    "reviewer_visible_insufficiency_marker",
    "reviewer_visible_contradiction_marker",
    "masked_state_before",
    "masked_state_after",
    "case_summary",
]

RESPONSE_FIELDS = [
    "case_id",
    "queue_id",
    "reviewer_id",
    "reviewed_at",
    "reviewed_outcome",
    "confidence",
    "adjudication_status",
    "notes_code",
    "rationale_short",
    "evidence_requested_if_needs_more_evidence",
]

FORBIDDEN_CASE_FIELDS = {
    "recommended_outcome_if_reviewed_now",
    "outcome_reviewer_id_hash",
    "outcome_reviewed_at",
    "reviewed_outcome",
    "outcome_confidence",
    "outcome_adjudication_status",
    "outcome_notes_code",
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def csv_text(rows: list[dict[str, str]], fieldnames: list[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def p0_outcome_ready_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("priority_band") == "P0"
        and row.get("outcome_adjudication_allowed") == "True"
        and row.get("packet_sufficiency_label") == "sufficient_for_outcome_adjudication"
    ]


def case_summary(row: dict[str, str]) -> str:
    observed = row.get("observed_change_type", "")
    execution = row.get("execution_verdict", "")
    causal = row.get("decision_causal_link", "")
    contradiction = row.get("reviewer_visible_contradiction_marker", "")
    temporal = row.get("pdp_temporal_authority_evidence", "")
    if observed == "identity_conflict_masked":
        return "Masked identity conflict at official truth boundary; reviewer should judge whether the block is supported by packet-visible identity evidence."
    if observed == "availability_or_access_uncertain_masked":
        if temporal == "latest_pdp_review_pool_snapshot_present":
            return "Availability or access is uncertain with a latest PDP review snapshot present; reviewer should judge whether revalidation/block is warranted or excessive."
        return "Availability or access is uncertain without latest PDP outcome evidence; reviewer should judge whether the packet proves the decision or needs more evidence."
    if observed == "not_action_grade_masked":
        if contradiction != "none":
            return "Revalidation signal conflicts with all reviewer-visible visual flags; reviewer should decide whether this is a false block or needs more evidence."
        return "The masked signal is not action-grade by itself; reviewer should judge whether revalidation is justified at action time."
    if observed == "price_or_materialization_conflict_masked":
        return "Masked price or materialization conflict; reviewer should decide whether the workflow context supports revalidation or whether the block is false."
    return f"Masked action-time packet with `{observed}` and `{execution}`; reviewer should adjudicate from packet-visible evidence only. Causal link: `{causal}`."


def build_cases(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    for index, row in enumerate(sorted(rows, key=lambda item: int(item.get("priority_rank") or 0)), start=1):
        case = {field: row.get(field, "") for field in BLIND_CASE_FIELDS if field != "case_id" and field != "case_summary"}
        case["case_id"] = f"reviewer2-case-{index:04d}"
        case["case_summary"] = case_summary(row)
        ordered = {field: case.get(field, "") for field in BLIND_CASE_FIELDS}
        cases.append(ordered)
    return cases


def build_response_template(cases: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for case in cases:
        rows.append(
            {
                "case_id": case["case_id"],
                "queue_id": case["queue_id"],
                "reviewer_id": "",
                "reviewed_at": "",
                "reviewed_outcome": "",
                "confidence": "",
                "adjudication_status": "",
                "notes_code": "",
                "rationale_short": "",
                "evidence_requested_if_needs_more_evidence": "",
            }
        )
    return rows


def forbidden_field_leaks(cases: list[dict[str, str]]) -> list[str]:
    leaks: list[str] = []
    for field in FORBIDDEN_CASE_FIELDS:
        if field in BLIND_CASE_FIELDS:
            leaks.append(f"forbidden field present in case schema: {field}")
    for case in cases:
        for key, value in case.items():
            if key in FORBIDDEN_CASE_FIELDS:
                leaks.append(f"{case.get('case_id')}: forbidden field present: {key}")
            if URL_PATTERN.search(str(value)):
                leaks.append(f"{case.get('case_id')}: URL-like value present in {key}")
    return leaks


def build_instructions(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# LatentAtlas Action-Time P0 Reviewer Pack v1",
            "",
            "## Purpose",
            "",
            "This is a blind second-review pack for the frozen masked P0 action-time set. The reviewer sees masked packet evidence and writes an independent outcome label. The pack does not expose reviewer01 labels, raw source rows, URLs, customer data, personal data, or production credentials.",
            "",
            "## Outcome Labels",
            "",
            "- `correct_block`: the conservative block or revalidation decision is supported by packet-visible evidence.",
            "- `false_block`: packet-visible evidence indicates the conservative block or revalidation was not warranted.",
            "- `needs_more_evidence`: the packet does not contain enough evidence to judge correctness or falseness.",
            "",
            "## Review Principles",
            "",
            "- Risk signal is not outcome evidence.",
            "- Decision-time evidence is not execution-time authority.",
            "- A blocked PDP or unavailable page can justify revalidation pressure, but it does not by itself prove the final outcome.",
            "- If the workflow context is material and missing, use `needs_more_evidence` instead of guessing.",
            "- Do not infer identity, price, availability, or permission from semantic similarity alone.",
            "",
            "## Required Response Fields",
            "",
            "- `reviewed_outcome`: one of `correct_block`, `false_block`, `needs_more_evidence`.",
            "- `confidence`: `low`, `medium`, or `high`.",
            "- `adjudication_status`: use `independent_reviewed` for completed rows.",
            "- `notes_code`: short machine-readable reason code.",
            "- `rationale_short`: one short sentence explaining the decision.",
            "- `evidence_requested_if_needs_more_evidence`: fill only when the label is `needs_more_evidence`.",
            "",
            "## Pack Counts",
            "",
            f"- cases: `{summary.get('case_count')}`",
            f"- response rows: `{summary.get('response_template_rows')}`",
            f"- source freeze id: `{summary.get('source_freeze_id')}`",
            f"- unit/dedup status: `{summary.get('unit_dedup_status')}`",
            "",
        ]
    )


def build_casebook(cases: list[dict[str, str]]) -> str:
    lines = [
        "# Reviewer Pack Casebook",
        "",
        "Each case below is intentionally short. Use the CSV for the full masked fields.",
        "",
    ]
    for case in cases:
        lines.append(f"- `{case['case_id']}` `{case['queue_id']}`: {case['case_summary']}")
    lines.append("")
    return "\n".join(lines)


def build_codebook() -> str:
    return "\n".join(
        [
            "# Reviewer Adjudication Codebook",
            "",
            "## Labels",
            "",
            "| Label | Use When | Do Not Use When |",
            "| --- | --- | --- |",
            "| `correct_block` | Packet-visible evidence supports the conservative block or revalidation decision. | The packet merely has a risk signal without outcome-grade evidence. |",
            "| `false_block` | Packet-visible evidence shows the conservative block or revalidation was not warranted. | The process context is missing and could change the answer. |",
            "| `needs_more_evidence` | The packet lacks enough evidence to decide correctness or falseness. | You can identify a clear packet-visible contradiction or support. |",
            "",
            "## Confidence",
            "",
            "- `high`: packet-visible evidence directly supports the label.",
            "- `medium`: packet-visible evidence supports the label with some context dependency.",
            "- `low`: label is possible but the packet is thin; prefer `needs_more_evidence` when uncertainty is material.",
            "",
            "## Notes Code Examples",
            "",
            "- `masked_identity_conflict_supports_block`",
            "- `blocked_pdp_not_outcome_evidence`",
            "- `latest_pdp_supports_false_block`",
            "- `workflow_context_required_for_price_change`",
            "- `availability_revalidation_supported`",
            "- `all_visual_flags_true_conflict`",
            "",
        ]
    )


def blocked_summary(reason: str, paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_action_time_p0_reviewer_pack",
        "reviewer_pack_schema_version": REVIEWER_PACK_SCHEMA_VERSION,
        "status": "blocked",
        "failure_reasons": [reason],
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def run(
    reviewer_sheet_path: Path = DEFAULT_REVIEWER_SHEET,
    freeze_summary_path: Path = DEFAULT_FREEZE_SUMMARY,
    unit_dedup_summary_path: Path = DEFAULT_UNIT_DEDUP_SUMMARY,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "instructions": out_dir / "reviewer_pack_instructions.md",
        "cases": out_dir / "reviewer_pack_cases.csv",
        "response_template": out_dir / "reviewer_response_sheet_blank.csv",
        "casebook": out_dir / "reviewer_pack_casebook.md",
        "codebook": out_dir / "reviewer_adjudication_codebook.md",
        "summary": out_dir / "reviewer_pack_summary.json",
        "manifest": out_dir / "reviewer_pack_manifest.json",
    }
    required = [reviewer_sheet_path, freeze_summary_path, unit_dedup_summary_path]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        summary = blocked_summary(f"missing required sources: {', '.join(missing)}", paths)
    else:
        freeze_summary = read_json(freeze_summary_path)
        unit_summary = read_json(unit_dedup_summary_path)
        if freeze_summary.get("status") != "pass":
            summary = blocked_summary("freeze summary status is not pass", paths)
        elif unit_summary.get("status") != "pass":
            summary = blocked_summary("unit/dedup summary status is not pass", paths)
        else:
            source_rows = read_csv(reviewer_sheet_path)
            cases = build_cases(p0_outcome_ready_rows(source_rows))
            response_rows = build_response_template(cases)
            leaks = forbidden_field_leaks(cases)
            observed_counts = dict(Counter(case["observed_change_type"] for case in cases).most_common())
            action_counts = dict(Counter(case["action_type"] for case in cases).most_common())
            summary = {
                "generated_at_utc": utc_now(),
                "mode": "latentatlas_action_time_p0_reviewer_pack",
                "reviewer_pack_schema_version": REVIEWER_PACK_SCHEMA_VERSION,
                "status": "pass" if not leaks else "blocked",
                "failure_reasons": leaks,
                "case_count": len(cases),
                "response_template_rows": len(response_rows),
                "source_reviewer_sheet": str(reviewer_sheet_path),
                "source_freeze_summary": str(freeze_summary_path),
                "source_freeze_id": freeze_summary.get("freeze_id", ""),
                "source_freeze_hash_sha256": freeze_summary.get("freeze_hash_sha256", ""),
                "source_unit_dedup_summary": str(unit_dedup_summary_path),
                "unit_dedup_status": unit_summary.get("status", ""),
                "observed_change_type_counts": observed_counts,
                "action_type_counts": action_counts,
                "blind_fields": BLIND_CASE_FIELDS,
                "response_fields": RESPONSE_FIELDS,
                "forbidden_case_fields": sorted(FORBIDDEN_CASE_FIELDS),
                "contains_customer_data": False,
                "contains_personal_data": False,
                "raw_source_rows_read": False,
                "external_calls_used_by_builder": False,
                "production_truth_mutation": False,
                "claim_boundary": {
                    "allowed": "This pack enables blind second review over masked P0 reviewer-visible packets.",
                    "not_allowed": "This pack does not create inter-reviewer agreement until another reviewer completes the blank response sheet.",
                },
            }
            if summary["status"] == "pass":
                write_csv(paths["cases"], cases, BLIND_CASE_FIELDS)
                write_csv(paths["response_template"], response_rows, RESPONSE_FIELDS)
                write_text(paths["instructions"], build_instructions(summary))
                write_text(paths["casebook"], build_casebook(cases))
                write_text(paths["codebook"], build_codebook())

    summary["outputs"] = {key: str(value) for key, value in paths.items()}
    write_json(paths["summary"], summary)
    manifest = {
        "generated_at_utc": summary["generated_at_utc"],
        "mode": summary["mode"],
        "reviewer_pack_schema_version": summary.get("reviewer_pack_schema_version", REVIEWER_PACK_SCHEMA_VERSION),
        "status": summary["status"],
        "case_count": summary.get("case_count", 0),
        "response_template_rows": summary.get("response_template_rows", 0),
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": summary["outputs"],
    }
    write_json(paths["manifest"], manifest)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-sheet", type=Path, default=DEFAULT_REVIEWER_SHEET)
    parser.add_argument("--freeze-summary", type=Path, default=DEFAULT_FREEZE_SUMMARY)
    parser.add_argument("--unit-dedup-summary", type=Path, default=DEFAULT_UNIT_DEDUP_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.reviewer_sheet, args.freeze_summary, args.unit_dedup_summary, args.out_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
