#!/usr/bin/env python3
"""Freeze the completed LatentAtlas action-time P0 human-review set.

The freeze is an immutable research snapshot over masked reviewer-visible
artifacts. It does not read raw sources, call external services, mutate
production truth, or turn the review set into a population probability claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_REVIEWER_SHEET = Path(
    "outputs/latentatlas/action_time_masked_evidence_adapter_p0_full/action_time_masked_evidence_reviewer_sheet_p0.csv"
)
DEFAULT_RESPONSES = Path(
    "outputs/latentatlas/action_time_masked_evidence_adapter_p0_full/"
    "human_review_v2_outcome_responses_reviewer01_hsyn.csv"
)
DEFAULT_CLUSTERS = Path(
    "outputs/latentatlas/action_time_pattern_cluster_review_p0_full/"
    "action_time_pattern_cluster_review_p0_clusters.csv"
)
DEFAULT_FINDING_SUMMARY = Path(
    "outputs/latentatlas/action_time_v2_outcome_adjudication_p0_full/"
    "action_time_v2_outcome_adjudication_summary.json"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_p0_review_freeze_v1")
DEFAULT_REVIEWER_ID = "reviewer01_hsyn"

FREEZE_SCHEMA_VERSION = "latentatlas_action_time_p0_review_freeze_v1"

FROZEN_FIELDS = [
    "freeze_schema_version",
    "queue_id",
    "event_id",
    "priority_rank",
    "priority_band",
    "reviewer_id_hash",
    "reviewed_at",
    "reviewed_outcome",
    "confidence",
    "adjudication_status",
    "notes_code",
    "action_type",
    "execution_verdict",
    "observed_change_type",
    "operator_visual_verdict",
    "identity_match",
    "price_match",
    "seller_comparable",
    "availability_confirmed",
    "packet_sufficiency_label",
    "outcome_adjudication_allowed",
    "pdp_temporal_authority_evidence",
    "lease_validity_relationship",
    "decision_causal_link",
    "insufficiency_marker",
    "contradiction_marker",
    "source_subject_hash",
    "masked_state_before",
    "masked_state_after",
]


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


def parse_pipe_state(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for part in (text or "").split("|"):
        if ":" in part:
            key, value = part.split(":", 1)
            parsed[key] = value
    return parsed


def canonical_csv(rows: list[dict[str, str]], fieldnames: list[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def short_hash(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key, "")}


def allowed_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("priority_band") == "P0"
        and row.get("outcome_adjudication_allowed") == "True"
        and row.get("packet_sufficiency_label") == "sufficient_for_outcome_adjudication"
    ]


def frozen_row(sheet_row: dict[str, str], response: dict[str, str]) -> dict[str, str]:
    state_before = parse_pipe_state(sheet_row.get("masked_state_before", ""))
    state_after = parse_pipe_state(sheet_row.get("masked_state_after", ""))
    return {
        "freeze_schema_version": FREEZE_SCHEMA_VERSION,
        "queue_id": sheet_row.get("queue_id", ""),
        "event_id": sheet_row.get("event_id", ""),
        "priority_rank": sheet_row.get("priority_rank", ""),
        "priority_band": sheet_row.get("priority_band", ""),
        "reviewer_id_hash": response.get("reviewer_id_hash", ""),
        "reviewed_at": response.get("reviewed_at", ""),
        "reviewed_outcome": response.get("reviewed_outcome", ""),
        "confidence": response.get("confidence", ""),
        "adjudication_status": response.get("adjudication_status", ""),
        "notes_code": response.get("notes_code", ""),
        "action_type": sheet_row.get("action_type", ""),
        "execution_verdict": sheet_row.get("execution_verdict", ""),
        "observed_change_type": sheet_row.get("observed_change_type", ""),
        "operator_visual_verdict": state_after.get("operator_visual_verdict", ""),
        "identity_match": state_after.get("identity_match", ""),
        "price_match": state_after.get("price_match", ""),
        "seller_comparable": state_after.get("seller_comparable", ""),
        "availability_confirmed": state_after.get("availability_confirmed", ""),
        "packet_sufficiency_label": sheet_row.get("packet_sufficiency_label", ""),
        "outcome_adjudication_allowed": sheet_row.get("outcome_adjudication_allowed", ""),
        "pdp_temporal_authority_evidence": sheet_row.get("pdp_temporal_authority_evidence", ""),
        "lease_validity_relationship": sheet_row.get("lease_validity_relationship", ""),
        "decision_causal_link": sheet_row.get("decision_causal_link", ""),
        "insufficiency_marker": sheet_row.get("reviewer_visible_insufficiency_marker", ""),
        "contradiction_marker": sheet_row.get("reviewer_visible_contradiction_marker", ""),
        "source_subject_hash": state_before.get("source_subject_hash", ""),
        "masked_state_before": sheet_row.get("masked_state_before", ""),
        "masked_state_after": sheet_row.get("masked_state_after", ""),
    }


def cluster_failures(cluster_rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    unreviewed_clusters = [row["pattern_id"] for row in cluster_rows if int(row.get("unreviewed_count") or 0) > 0]
    mixed_clusters = [
        row["pattern_id"]
        for row in cluster_rows
        if len(json.loads(row.get("existing_outcome_counts") or "{}")) > 1
    ]
    non_complete = [
        row["pattern_id"]
        for row in cluster_rows
        if row.get("review_status") != "fully_reviewed_single_outcome"
    ]
    if unreviewed_clusters:
        failures.append(f"clusters still have unreviewed rows: {len(unreviewed_clusters)}")
    if mixed_clusters:
        failures.append(f"clusters have mixed prior outcomes: {len(mixed_clusters)}")
    if non_complete:
        failures.append(f"clusters are not fully reviewed single-outcome: {len(non_complete)}")
    return failures


def build_freeze(
    reviewer_rows: list[dict[str, str]],
    response_rows: list[dict[str, str]],
    cluster_rows: list[dict[str, str]],
    finding_summary: dict[str, Any],
    *,
    reviewer_id: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    reviewer_index = index_by(reviewer_rows, "queue_id")
    allowed = allowed_rows(reviewer_rows)
    allowed_ids = {row["queue_id"] for row in allowed}
    responses = [row for row in response_rows if row.get("reviewer_id_hash") == reviewer_id]
    response_index = index_by(responses, "queue_id")
    response_ids = set(response_index)

    unmatched_responses = sorted(response_ids - set(reviewer_index))
    responses_outside_allowed = sorted(response_ids - allowed_ids)
    unreviewed_allowed = sorted(allowed_ids - response_ids)
    duplicate_response_queue_ids = duplicate_values([row.get("queue_id", "") for row in responses])

    frozen_rows = [
        frozen_row(reviewer_index[queue_id], response_index[queue_id])
        for queue_id in sorted(allowed_ids & response_ids, key=lambda value: int(reviewer_index[value].get("priority_rank") or 0))
    ]

    row_mismatches = []
    for row in frozen_rows:
        sheet_row = reviewer_index[row["queue_id"]]
        if sheet_row.get("reviewed_outcome") != row["reviewed_outcome"]:
            row_mismatches.append(row["queue_id"])

    duplicate_queue_ids = duplicate_values([row["queue_id"] for row in frozen_rows])
    duplicate_event_ids = duplicate_values([row["event_id"] for row in frozen_rows])
    duplicate_subject_hashes = duplicate_values([row["source_subject_hash"] for row in frozen_rows if row["source_subject_hash"]])
    cluster_validation_failures = cluster_failures(cluster_rows)

    finding = finding_summary.get("finding", {})
    finding_completion = finding.get("review_completion", {})
    finding_status = finding_summary.get("status", "")
    finding_reviewed_count = int(finding_completion.get("reviewed_outcome_ready_count") or 0)
    finding_unreviewed_count = int(finding_completion.get("unreviewed_outcome_ready_count") or 0)

    failures = []
    if unmatched_responses:
        failures.append(f"unmatched responses: {len(unmatched_responses)}")
    if responses_outside_allowed:
        failures.append(f"responses outside allowed P0 set: {len(responses_outside_allowed)}")
    if unreviewed_allowed:
        failures.append(f"unreviewed outcome-ready rows: {len(unreviewed_allowed)}")
    if duplicate_response_queue_ids:
        failures.append(f"duplicate response queue ids: {len(duplicate_response_queue_ids)}")
    if row_mismatches:
        failures.append(f"sheet/response reviewed_outcome mismatches: {len(row_mismatches)}")
    if duplicate_queue_ids or duplicate_event_ids or duplicate_subject_hashes:
        failures.append("duplicate frozen identifiers present")
    failures.extend(cluster_validation_failures)
    if finding_status != "pass":
        failures.append(f"finding summary status is not pass: {finding_status}")
    if finding_reviewed_count != len(allowed) or finding_unreviewed_count != 0:
        failures.append("finding summary review completion does not match freeze input")

    csv_text = canonical_csv(frozen_rows, FROZEN_FIELDS)
    freeze_hash = sha256_text(csv_text)
    freeze_id = f"p0_review_freeze_{short_hash(freeze_hash)}"
    outcome_counts = Counter(row["reviewed_outcome"] for row in frozen_rows)
    status = "pass" if not failures else "blocked"

    summary = {
        "freeze_id": freeze_id,
        "freeze_schema_version": FREEZE_SCHEMA_VERSION,
        "freeze_hash_sha256": freeze_hash,
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_action_time_p0_review_freeze",
        "status": status,
        "failure_reasons": failures,
        "reviewer_id_hash": reviewer_id,
        "p0_rows": sum(1 for row in reviewer_rows if row.get("priority_band") == "P0"),
        "outcome_ready_p0_rows": len(allowed),
        "insufficient_for_outcome_adjudication_p0_rows": sum(
            1
            for row in reviewer_rows
            if row.get("priority_band") == "P0" and row.get("outcome_adjudication_allowed") != "True"
        ),
        "frozen_reviewed_rows": len(frozen_rows),
        "unreviewed_outcome_ready_rows": len(unreviewed_allowed),
        "response_rows": len(responses),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "duplicate_queue_ids": duplicate_queue_ids,
        "duplicate_event_ids": duplicate_event_ids,
        "duplicate_subject_hashes": duplicate_subject_hashes,
        "unmatched_response_queue_ids": unmatched_responses,
        "responses_outside_allowed_queue_ids": responses_outside_allowed,
        "row_mismatch_queue_ids": row_mismatches,
        "cluster_count": len(cluster_rows),
        "cluster_review_status_counts": dict(Counter(row.get("review_status", "") for row in cluster_rows).most_common()),
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "internal_index_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "claim_boundary": {
            "allowed_claim": "This freezes the completed masked P0 human-review outcome set.",
            "not_claimed": "The freeze does not prove a population probability or mutate production truth.",
        },
    }
    return frozen_rows, summary


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# LatentAtlas P0 Human Review Freeze",
        "",
        f"Generated at: `{summary['generated_at_utc']}`",
        f"Freeze id: `{summary['freeze_id']}`",
        f"Freeze hash: `{summary['freeze_hash_sha256']}`",
        "",
        "## Boundary",
        "",
        "This freeze is a masked, reviewer-visible research artifact. It does not read raw source rows, call external services, mutate production truth, or establish a population probability.",
        "",
        "## Completion",
        "",
        f"- status: `{summary['status']}`",
        f"- P0 rows: `{summary['p0_rows']}`",
        f"- outcome-ready P0 rows: `{summary['outcome_ready_p0_rows']}`",
        f"- frozen reviewed rows: `{summary['frozen_reviewed_rows']}`",
        f"- unreviewed outcome-ready rows: `{summary['unreviewed_outcome_ready_rows']}`",
        f"- insufficient P0 rows: `{summary['insufficient_for_outcome_adjudication_p0_rows']}`",
        f"- cluster status counts: `{json.dumps(summary['cluster_review_status_counts'], sort_keys=True)}`",
        "",
        "## Outcome Counts",
        "",
    ]
    for outcome, count in summary["outcome_counts"].items():
        lines.append(f"- `{outcome}`: `{count}`")
    lines.extend(["", "## Claim Boundary", ""])
    lines.append(f"- allowed: {summary['claim_boundary']['allowed_claim']}")
    lines.append(f"- not claimed: {summary['claim_boundary']['not_claimed']}")
    if summary["failure_reasons"]:
        lines.extend(["", "## Failure Reasons", ""])
        for reason in summary["failure_reasons"]:
            lines.append(f"- {reason}")
    lines.append("")
    return "\n".join(lines)


def run(
    reviewer_sheet_path: Path = DEFAULT_REVIEWER_SHEET,
    responses_path: Path = DEFAULT_RESPONSES,
    clusters_path: Path = DEFAULT_CLUSTERS,
    finding_summary_path: Path = DEFAULT_FINDING_SUMMARY,
    out_dir: Path = DEFAULT_OUT_DIR,
    reviewer_id: str = DEFAULT_REVIEWER_ID,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "frozen_rows": out_dir / "action_time_p0_review_freeze_rows.csv",
        "summary": out_dir / "action_time_p0_review_freeze_summary.json",
        "manifest": out_dir / "action_time_p0_review_freeze_manifest.json",
        "report": out_dir / "action_time_p0_review_freeze_report.md",
    }
    required = [reviewer_sheet_path, responses_path, clusters_path, finding_summary_path]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        manifest = {
            "generated_at_utc": utc_now(),
            "mode": "latentatlas_action_time_p0_review_freeze",
            "status": "blocked",
            "failure_reason": "missing_required_sources",
            "missing_sources": missing,
            "external_calls_used_by_builder": False,
            "production_truth_mutation": False,
            "internal_index_read": False,
        }
        write_json(paths["manifest"], manifest)
        return manifest

    frozen_rows, summary = build_freeze(
        read_csv(reviewer_sheet_path),
        read_csv(responses_path),
        read_csv(clusters_path),
        read_json(finding_summary_path),
        reviewer_id=reviewer_id,
    )
    summary["input"] = {
        "reviewer_sheet": str(reviewer_sheet_path),
        "responses": str(responses_path),
        "clusters": str(clusters_path),
        "finding_summary": str(finding_summary_path),
    }
    summary["outputs"] = {key: str(value) for key, value in paths.items()}

    write_text(paths["frozen_rows"], canonical_csv(frozen_rows, FROZEN_FIELDS))
    write_json(paths["summary"], summary)
    write_text(paths["report"], build_report(summary))
    manifest = {
        "generated_at_utc": summary["generated_at_utc"],
        "mode": summary["mode"],
        "status": summary["status"],
        "freeze_id": summary["freeze_id"],
        "freeze_hash_sha256": summary["freeze_hash_sha256"],
        "frozen_rows": str(paths["frozen_rows"]),
        "summary": str(paths["summary"]),
        "report": str(paths["report"]),
        "frozen_reviewed_rows": summary["frozen_reviewed_rows"],
        "outcome_counts": summary["outcome_counts"],
        "contains_customer_data": False,
        "contains_personal_data": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "internal_index_read": False,
        "outputs": summary["outputs"],
    }
    write_json(paths["manifest"], manifest)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-sheet", type=Path, default=DEFAULT_REVIEWER_SHEET)
    parser.add_argument("--responses", type=Path, default=DEFAULT_RESPONSES)
    parser.add_argument("--clusters", type=Path, default=DEFAULT_CLUSTERS)
    parser.add_argument("--finding-summary", type=Path, default=DEFAULT_FINDING_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--reviewer-id", default=DEFAULT_REVIEWER_ID)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.reviewer_sheet, args.responses, args.clusters, args.finding_summary, args.out_dir, args.reviewer_id)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
