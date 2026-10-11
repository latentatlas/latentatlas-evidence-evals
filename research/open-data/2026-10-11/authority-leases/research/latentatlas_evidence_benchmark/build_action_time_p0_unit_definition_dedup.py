#!/usr/bin/env python3
"""Build unit-definition and deduplication audit for the frozen P0 review set.

This is the first Level 4 preparation gate before second-reviewer expansion.
It defines the current denominator and reports event-level and subject-cluster
counts without reading raw sources or mutating production truth.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_FREEZE_ROWS = Path("outputs/latentatlas/action_time_p0_review_freeze_v1/action_time_p0_review_freeze_rows.csv")
DEFAULT_FREEZE_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_review_freeze_v1/action_time_p0_review_freeze_summary.json"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_p0_unit_definition_dedup_v1")

UNIT_SCHEMA_VERSION = "latentatlas_action_time_p0_unit_definition_dedup_v1"

UNIT_INDEX_FIELDS = [
    "primary_unit_id",
    "primary_unit_type",
    "queue_id",
    "event_id",
    "subject_cluster_hash",
    "workflow_family",
    "reviewed_outcome",
    "dedup_role",
    "claim_boundary",
]

CLUSTER_FIELDS = [
    "subject_cluster_hash",
    "cluster_size",
    "workflow_family_count",
    "workflow_families",
    "outcome_count",
    "outcomes",
    "queue_id_sample",
    "event_id_sample",
    "dedup_status",
    "claim_boundary",
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


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def stable_hash(payload: Any, length: int = 16) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def primary_unit_id(row: dict[str, str]) -> str:
    return "action_attempt_event-" + stable_hash(
        {
            "queue_id": row.get("queue_id", ""),
            "event_id": row.get("event_id", ""),
            "action_type": row.get("action_type", ""),
        }
    )


def unit_index_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    subject_counts = Counter(row.get("source_subject_hash", "") for row in rows if row.get("source_subject_hash", ""))
    index_rows: list[dict[str, Any]] = []
    for row in rows:
        subject_hash = row.get("source_subject_hash", "")
        duplicate_subject = subject_counts.get(subject_hash, 0) > 1 if subject_hash else True
        index_rows.append(
            {
                "primary_unit_id": primary_unit_id(row),
                "primary_unit_type": "action_attempt_event",
                "queue_id": row.get("queue_id", ""),
                "event_id": row.get("event_id", ""),
                "subject_cluster_hash": subject_hash,
                "workflow_family": row.get("action_type", ""),
                "reviewed_outcome": row.get("reviewed_outcome", ""),
                "dedup_role": "duplicate_subject_member" if duplicate_subject else "unique_subject_member",
                "claim_boundary": "Frozen P0 descriptive unit only; not a population unit.",
            }
        )
    return index_rows


def subject_cluster_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    clusters: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        clusters[row.get("source_subject_hash", "")].append(row)

    cluster_rows: list[dict[str, Any]] = []
    for subject_hash, cluster in sorted(clusters.items()):
        workflows = sorted({row.get("action_type", "") for row in cluster if row.get("action_type", "")})
        outcomes = sorted({row.get("reviewed_outcome", "") for row in cluster if row.get("reviewed_outcome", "")})
        if not subject_hash:
            dedup_status = "missing_subject_cluster_hash"
        elif len(cluster) == 1:
            dedup_status = "unique_subject_cluster"
        else:
            dedup_status = "duplicate_subject_cluster_requires_policy"
        cluster_rows.append(
            {
                "subject_cluster_hash": subject_hash,
                "cluster_size": len(cluster),
                "workflow_family_count": len(workflows),
                "workflow_families": "|".join(workflows),
                "outcome_count": len(outcomes),
                "outcomes": "|".join(outcomes),
                "queue_id_sample": "|".join(row.get("queue_id", "") for row in cluster[:10]),
                "event_id_sample": "|".join(row.get("event_id", "") for row in cluster[:10]),
                "dedup_status": dedup_status,
                "claim_boundary": "Subject-cluster denominator for independence sensitivity; not population probability.",
            }
        )
    return cluster_rows


def unit_definitions(event_count: int, subject_count: int, workflow_count: int) -> list[dict[str, Any]]:
    return [
        {
            "unit_type": "action_attempt_event",
            "key_fields": ["queue_id", "event_id", "action_type"],
            "current_count": event_count,
            "recommended_use": "Primary unit for the current frozen P0 descriptive Paper A denominator.",
            "claim_boundary": "Descriptive frozen-set unit; not a population probability denominator.",
        },
        {
            "unit_type": "subject_cluster",
            "key_fields": ["subject_cluster_hash"],
            "current_count": subject_count,
            "recommended_use": "Independence sensitivity denominator before Level 4 probability language.",
            "claim_boundary": "If lower than event count, report both and pre-register duplicate treatment.",
        },
        {
            "unit_type": "workflow_family",
            "key_fields": ["action_type"],
            "current_count": workflow_count,
            "recommended_use": "Stratification axis, not a denominator by itself.",
            "claim_boundary": "Do not use workflow-family count as event or subject denominator.",
        },
    ]


def build_audit(rows: list[dict[str, str]], freeze_summary: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if freeze_summary.get("status") != "pass":
        summary = {
            "generated_at_utc": utc_now(),
            "mode": "latentatlas_action_time_p0_unit_definition_dedup",
            "unit_schema_version": UNIT_SCHEMA_VERSION,
            "status": "blocked",
            "failure_reasons": ["freeze summary status is not pass"],
            "production_truth_mutation": False,
            "external_calls_used_by_builder": False,
            "raw_source_rows_read": False,
        }
        return [], [], summary

    queue_ids = [row.get("queue_id", "") for row in rows]
    event_ids = [row.get("event_id", "") for row in rows]
    subject_hashes = [row.get("source_subject_hash", "") for row in rows if row.get("source_subject_hash", "")]
    missing_subject_hash_count = sum(1 for row in rows if not row.get("source_subject_hash", ""))
    duplicate_queue_ids = duplicate_values(queue_ids)
    duplicate_event_ids = duplicate_values(event_ids)
    duplicate_subject_hashes = duplicate_values(subject_hashes)

    unit_rows = unit_index_rows(rows)
    cluster_rows = subject_cluster_rows(rows)
    subject_cluster_count = len({row.get("source_subject_hash", "") for row in rows if row.get("source_subject_hash", "")})
    workflow_counts = Counter(row.get("action_type", "") for row in rows)
    outcome_counts = Counter(row.get("reviewed_outcome", "") for row in rows)
    issue_reasons = []
    if duplicate_queue_ids:
        issue_reasons.append(f"duplicate queue ids: {len(duplicate_queue_ids)}")
    if duplicate_event_ids:
        issue_reasons.append(f"duplicate event ids: {len(duplicate_event_ids)}")
    if missing_subject_hash_count:
        issue_reasons.append(f"missing subject cluster hash: {missing_subject_hash_count}")
    if duplicate_subject_hashes:
        issue_reasons.append(f"duplicate subject clusters: {len(duplicate_subject_hashes)}")

    event_count = len(rows)
    denominator_ratio = round(subject_cluster_count / event_count, 4) if event_count else 0.0
    status = "pass" if not issue_reasons else "needs_dedup_policy"
    summary = {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_action_time_p0_unit_definition_dedup",
        "unit_schema_version": UNIT_SCHEMA_VERSION,
        "status": status,
        "failure_reasons": issue_reasons,
        "freeze_id": freeze_summary.get("freeze_id", ""),
        "freeze_hash_sha256": freeze_summary.get("freeze_hash_sha256", ""),
        "event_level_count": event_count,
        "unique_queue_id_count": len(set(queue_ids)),
        "unique_event_id_count": len(set(event_ids)),
        "subject_cluster_count": subject_cluster_count,
        "missing_subject_cluster_hash_count": missing_subject_hash_count,
        "duplicate_queue_ids": duplicate_queue_ids,
        "duplicate_event_ids": duplicate_event_ids,
        "duplicate_subject_cluster_hashes": duplicate_subject_hashes,
        "duplicate_subject_cluster_count": len(duplicate_subject_hashes),
        "subject_to_event_denominator_ratio": denominator_ratio,
        "workflow_family_count": len(workflow_counts),
        "workflow_family_counts": dict(sorted(workflow_counts.items())),
        "outcome_counts_event_level": dict(sorted(outcome_counts.items())),
        "unit_definitions": unit_definitions(event_count, subject_cluster_count, len(workflow_counts)),
        "recommendation": {
            "current_paper_primary_unit": "action_attempt_event",
            "level4_sensitivity_unit": "subject_cluster",
            "second_reviewer_gate": (
                "ready_for_second_reviewer_queue"
                if status == "pass"
                else "blocked_until_duplicate_subject_policy_is_pre_registered"
            ),
            "rationale": (
                "Current frozen P0 event denominator and subject-cluster denominator match."
                if status == "pass"
                else "Repeated or missing subject clusters can inflate denominator unless pre-registered."
            ),
        },
        "claim_boundary": {
            "allowed_claims": [
                "The current frozen P0 denominator has been audited at event and subject-cluster levels.",
                "Second-reviewer expansion can use this unit policy if status is pass.",
            ],
            "blocked_claims": [
                "Population probability.",
                "General system accuracy.",
                "Counting repeated subject snapshots without pre-registered dedup policy.",
            ],
        },
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "internal_index_read": False,
        "production_truth_mutation": False,
    }
    return unit_rows, cluster_rows, summary


def build_report(summary: dict[str, Any], cluster_rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Action-Time P0 Unit Definition And Dedup Audit",
        "",
        f"Generated at: `{summary['generated_at_utc']}`",
        f"Status: `{summary['status']}`",
        f"Freeze id: `{summary.get('freeze_id', '')}`",
        f"Freeze hash: `{summary.get('freeze_hash_sha256', '')}`",
        "",
        "## Unit Decision",
        "",
        f"- Current Paper A primary unit: `{summary.get('recommendation', {}).get('current_paper_primary_unit', '')}`",
        f"- Level 4 sensitivity unit: `{summary.get('recommendation', {}).get('level4_sensitivity_unit', '')}`",
        f"- Second-reviewer gate: `{summary.get('recommendation', {}).get('second_reviewer_gate', '')}`",
        "",
        "## Denominators",
        "",
        f"- event-level count: `{summary.get('event_level_count', 0)}`",
        f"- subject-cluster count: `{summary.get('subject_cluster_count', 0)}`",
        f"- subject/event ratio: `{summary.get('subject_to_event_denominator_ratio', 0)}`",
        f"- workflow-family count: `{summary.get('workflow_family_count', 0)}`",
        f"- duplicate subject clusters: `{summary.get('duplicate_subject_cluster_count', 0)}`",
        f"- missing subject cluster hash: `{summary.get('missing_subject_cluster_hash_count', 0)}`",
        "",
        "## Unit Definitions",
        "",
    ]
    for definition in summary.get("unit_definitions", []):
        lines.extend(
            [
                f"### `{definition['unit_type']}`",
                "",
                f"- key fields: `{','.join(definition['key_fields'])}`",
                f"- current count: `{definition['current_count']}`",
                f"- recommended use: {definition['recommended_use']}",
                f"- boundary: {definition['claim_boundary']}",
                "",
            ]
        )
    duplicate_clusters = [row for row in cluster_rows if row["dedup_status"] != "unique_subject_cluster"]
    lines.extend(["## Duplicate Or Missing Subject Clusters", ""])
    if not duplicate_clusters:
        lines.append("No duplicate or missing subject clusters in the frozen P0 reviewed set.")
    else:
        for row in duplicate_clusters[:20]:
            lines.extend(
                [
                    f"- `{row['subject_cluster_hash']}` status=`{row['dedup_status']}` size=`{row['cluster_size']}`",
                    f"  - queues: `{row['queue_id_sample']}`",
                    f"  - outcomes: `{row['outcomes']}`",
                ]
            )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This artifact defines denominator policy for the frozen P0 set. It does not create a population probability claim and does not mutate production truth.",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    freeze_rows_path: Path = DEFAULT_FREEZE_ROWS,
    freeze_summary_path: Path = DEFAULT_FREEZE_SUMMARY,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "unit_index": out_dir / "action_time_p0_unit_index.csv",
        "subject_clusters": out_dir / "action_time_p0_subject_clusters.csv",
        "summary": out_dir / "action_time_p0_unit_definition_dedup_summary.json",
        "manifest": out_dir / "action_time_p0_unit_definition_dedup_manifest.json",
        "report": out_dir / "action_time_p0_unit_definition_dedup_report.md",
    }
    missing = [str(path) for path in (freeze_rows_path, freeze_summary_path) if not path.exists()]
    if missing:
        summary = {
            "generated_at_utc": utc_now(),
            "mode": "latentatlas_action_time_p0_unit_definition_dedup",
            "unit_schema_version": UNIT_SCHEMA_VERSION,
            "status": "blocked",
            "failure_reasons": [f"missing required sources: {', '.join(missing)}"],
            "contains_customer_data": False,
            "contains_personal_data": False,
            "raw_source_rows_read": False,
            "external_calls_used_by_builder": False,
            "production_truth_mutation": False,
        }
        unit_rows: list[dict[str, Any]] = []
        cluster_rows: list[dict[str, Any]] = []
    else:
        unit_rows, cluster_rows, summary = build_audit(read_csv(freeze_rows_path), read_json(freeze_summary_path))
        summary["input"] = {
            "freeze_rows": str(freeze_rows_path),
            "freeze_summary": str(freeze_summary_path),
        }

    summary["outputs"] = {key: str(value) for key, value in paths.items()}
    write_csv(paths["unit_index"], unit_rows, UNIT_INDEX_FIELDS)
    write_csv(paths["subject_clusters"], cluster_rows, CLUSTER_FIELDS)
    write_text(paths["report"], build_report(summary, cluster_rows))
    write_json(paths["summary"], summary)
    manifest = {
        "generated_at_utc": summary["generated_at_utc"],
        "mode": summary["mode"],
        "unit_schema_version": summary.get("unit_schema_version", UNIT_SCHEMA_VERSION),
        "status": summary["status"],
        "event_level_count": summary.get("event_level_count", 0),
        "subject_cluster_count": summary.get("subject_cluster_count", 0),
        "duplicate_subject_cluster_count": summary.get("duplicate_subject_cluster_count", 0),
        "second_reviewer_gate": summary.get("recommendation", {}).get("second_reviewer_gate", ""),
        "contains_customer_data": False,
        "contains_personal_data": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": summary["outputs"],
    }
    write_json(paths["manifest"], manifest)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-rows", type=Path, default=DEFAULT_FREEZE_ROWS)
    parser.add_argument("--freeze-summary", type=Path, default=DEFAULT_FREEZE_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.freeze_rows, args.freeze_summary, args.out_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["status"] not in {"pass", "needs_dedup_policy"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
