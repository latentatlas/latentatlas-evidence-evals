#!/usr/bin/env python3
"""Build a pattern-cluster review queue for P0 outcome-ready packets.

This artifact groups repeated masked decision patterns so the reviewer can
approve or reject a pattern once, without pretending that repeated patterns are
the same event. It does not apply cluster decisions automatically, does not read
the internal index, and does not mutate production truth.
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


DEFAULT_REVIEWER_SHEET = Path(
    "outputs/latentatlas/action_time_masked_evidence_adapter_p0_full/action_time_masked_evidence_reviewer_sheet_p0.csv"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_pattern_cluster_review_p0_full")
PATTERN_SCHEMA_VERSION = "p0_pattern_v2_pdp_temporal_authority"

PATTERN_FIELDS = [
    "action_type",
    "execution_verdict",
    "observed_change_type",
    "operator_visual_verdict",
    "gpt_visual_review_status",
    "official_guard_status",
    "official_guard_reason",
    "identity_match",
    "price_match",
    "seller_comparable",
    "availability_confirmed",
    "pdp_temporal_authority_evidence",
    "reviewer_visible_insufficiency_marker",
    "reviewer_visible_contradiction_marker",
    "packet_sufficiency_label",
    "outcome_adjudication_allowed",
]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def stable_hash(value: Any, length: int = 12) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def parse_pipe_state(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for part in (text or "").split("|"):
        if ":" in part:
            key, value = part.split(":", 1)
            parsed[key] = value
    return parsed


def source_subject_hash(row: dict[str, str]) -> str:
    return parse_pipe_state(row.get("masked_state_before", "")).get("source_subject_hash", "")


def state_after_fields(row: dict[str, str]) -> dict[str, str]:
    parsed = parse_pipe_state(row.get("masked_state_after", ""))
    return {
        "operator_visual_verdict": parsed.get("operator_visual_verdict", ""),
        "gpt_visual_review_status": parsed.get("gpt_visual_review_status", ""),
        "official_guard_status": parsed.get("official_guard_status", ""),
        "official_guard_reason": parsed.get("official_guard_reason", ""),
        "identity_match": parsed.get("identity_match", ""),
        "price_match": parsed.get("price_match", ""),
        "seller_comparable": parsed.get("seller_comparable", ""),
        "availability_confirmed": parsed.get("availability_confirmed", ""),
    }


def pattern_payload(row: dict[str, str]) -> dict[str, str]:
    payload = {
        "action_type": row.get("action_type", ""),
        "execution_verdict": row.get("execution_verdict", ""),
        "observed_change_type": row.get("observed_change_type", ""),
        **state_after_fields(row),
        "pdp_temporal_authority_evidence": row.get("pdp_temporal_authority_evidence", ""),
        "reviewer_visible_insufficiency_marker": row.get("reviewer_visible_insufficiency_marker", ""),
        "reviewer_visible_contradiction_marker": row.get("reviewer_visible_contradiction_marker", ""),
        "packet_sufficiency_label": row.get("packet_sufficiency_label", ""),
        "outcome_adjudication_allowed": row.get("outcome_adjudication_allowed", ""),
    }
    return payload


def flag_word(value: str) -> str:
    if value == "true":
        return "eşleşiyor/teyitli"
    if value == "false":
        return "eşleşmiyor/teyitli değil"
    return "belirsiz"


def review_prompt_tr(payload: dict[str, str], count: int) -> str:
    return (
        f"{count} case aynı paternde. "
        f"Aksiyon `{payload['action_type']}`; sistem `{payload['execution_verdict']}` demiş. "
        f"Operatör kararı `{payload['operator_visual_verdict']}`. "
        f"Kimlik {flag_word(payload['identity_match'])}; fiyat {flag_word(payload['price_match'])}; "
        f"satıcı {flag_word(payload['seller_comparable'])}; availability {flag_word(payload['availability_confirmed'])}. "
        f"PDP temporal evidence `{payload['pdp_temporal_authority_evidence']}`. "
        f"Insufficiency `{payload['reviewer_visible_insufficiency_marker']}`; "
        f"contradiction `{payload['reviewer_visible_contradiction_marker']}`."
    )


def cluster_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    outcome_ready = [row for row in rows if row.get("outcome_adjudication_allowed") == "True"]
    clusters: dict[str, list[dict[str, str]]] = defaultdict(list)
    payloads: dict[str, dict[str, str]] = {}
    for row in outcome_ready:
        payload = pattern_payload(row)
        pattern_id = f"pattern-{stable_hash(payload)}"
        clusters[pattern_id].append(row)
        payloads[pattern_id] = payload

    cluster_summaries: list[dict[str, Any]] = []
    for pattern_id, cluster in clusters.items():
        payload = payloads[pattern_id]
        reviewed = [row for row in cluster if row.get("reviewed_outcome", "").strip()]
        unreviewed = [row for row in cluster if not row.get("reviewed_outcome", "").strip()]
        outcome_counts = Counter(row.get("reviewed_outcome", "").strip() for row in reviewed)
        notes_counts = Counter(row.get("outcome_notes_code", "").strip() for row in reviewed if row.get("outcome_notes_code", "").strip())
        priority_ranks = [int(row.get("priority_rank", "0") or "0") for row in cluster]
        unique_subjects = {source_subject_hash(row) for row in cluster if source_subject_hash(row)}
        existing_outcome_values = sorted(outcome_counts)
        if not reviewed:
            review_status = "unreviewed_cluster"
        elif unreviewed and len(existing_outcome_values) == 1:
            review_status = "partially_reviewed_single_prior_outcome"
        elif unreviewed:
            review_status = "partially_reviewed_mixed_prior_outcomes"
        elif len(existing_outcome_values) == 1:
            review_status = "fully_reviewed_single_outcome"
        else:
            review_status = "fully_reviewed_mixed_outcomes"

        cluster_summaries.append(
            {
                "pattern_id": pattern_id,
                "review_status": review_status,
                "case_count": len(cluster),
                "reviewed_count": len(reviewed),
                "unreviewed_count": len(unreviewed),
                "unique_event_count": len({row.get("event_id", "") for row in cluster}),
                "unique_subject_count": len(unique_subjects),
                "priority_rank_min": min(priority_ranks),
                "priority_rank_max": max(priority_ranks),
                "example_queue_id": cluster[0].get("queue_id", ""),
                "example_event_id": cluster[0].get("event_id", ""),
                "example_priority_rank": cluster[0].get("priority_rank", ""),
                "queue_id_sample": "|".join(row.get("queue_id", "") for row in cluster[:10]),
                "event_id_sample": "|".join(row.get("event_id", "") for row in cluster[:10]),
                "existing_outcome_counts": json.dumps(dict(sorted(outcome_counts.items())), sort_keys=True),
                "existing_notes_code_counts": json.dumps(dict(sorted(notes_counts.items())), sort_keys=True),
                "cluster_review_outcome": "",
                "cluster_review_confidence": "",
                "cluster_review_notes_code": "",
                "cluster_review_status": "pending_human_cluster_review" if unreviewed else "no_unreviewed_rows",
                "review_prompt_tr": review_prompt_tr(payload, len(cluster)),
                **payload,
            }
        )

    cluster_summaries.sort(key=lambda row: (-row["unreviewed_count"], row["priority_rank_min"], row["pattern_id"]))

    event_counts = Counter(row.get("event_id", "") for row in rows)
    queue_counts = Counter(row.get("queue_id", "") for row in rows)
    subject_counts = Counter(source_subject_hash(row) for row in rows if source_subject_hash(row))
    summary = {
        "generated_at": utc_now(),
        "mode": "latentatlas_action_time_pattern_cluster_review_p0",
        "pattern_schema_version": PATTERN_SCHEMA_VERSION,
        "status": "pass",
        "p0_row_count": len(rows),
        "outcome_ready_row_count": len(outcome_ready),
        "cluster_count": len(cluster_summaries),
        "clusters_with_unreviewed_rows": sum(1 for row in cluster_summaries if row["unreviewed_count"] > 0),
        "unreviewed_outcome_ready_row_count": sum(row["unreviewed_count"] for row in cluster_summaries),
        "reviewed_outcome_ready_row_count": sum(row["reviewed_count"] for row in cluster_summaries),
        "duplicate_queue_id_count": sum(1 for count in queue_counts.values() if count > 1),
        "duplicate_event_id_count": sum(1 for count in event_counts.values() if count > 1),
        "duplicate_subject_hash_count": sum(1 for count in subject_counts.values() if count > 1),
        "unique_subject_hash_count": len(subject_counts),
        "largest_cluster_size": max((row["case_count"] for row in cluster_summaries), default=0),
        "largest_unreviewed_cluster_size": max((row["unreviewed_count"] for row in cluster_summaries), default=0),
        "review_status_counts": dict(Counter(row["review_status"] for row in cluster_summaries).most_common()),
        "claim_boundary": {
            "allowed_claim": "P0 outcome-ready packets were grouped by repeated masked decision pattern.",
            "not_claimed": "Pattern grouping does not apply decisions automatically and does not prove a population probability.",
        },
        "internal_index_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
    }
    return cluster_summaries, summary


def build_report(summary: dict[str, Any], clusters: list[dict[str, Any]]) -> str:
    lines = [
        "# LatentAtlas P0 Pattern-Cluster Review",
        "",
        f"Generated at: `{summary['generated_at']}`",
        "",
        "## Boundary",
        "",
        "This artifact groups repeated masked decision patterns for human review. It does not apply cluster decisions automatically, read the internal index, call external services, or mutate production truth.",
        "",
        "## Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- pattern schema version: `{summary['pattern_schema_version']}`",
        f"- P0 rows: `{summary['p0_row_count']}`",
        f"- outcome-ready rows: `{summary['outcome_ready_row_count']}`",
        f"- pattern clusters: `{summary['cluster_count']}`",
        f"- clusters with unreviewed rows: `{summary['clusters_with_unreviewed_rows']}`",
        f"- reviewed outcome-ready rows: `{summary['reviewed_outcome_ready_row_count']}`",
        f"- unreviewed outcome-ready rows: `{summary['unreviewed_outcome_ready_row_count']}`",
        f"- duplicate queue ids: `{summary['duplicate_queue_id_count']}`",
        f"- duplicate event ids: `{summary['duplicate_event_id_count']}`",
        f"- duplicate subject hashes: `{summary['duplicate_subject_hash_count']}`",
        f"- largest cluster size: `{summary['largest_cluster_size']}`",
        f"- largest unreviewed cluster size: `{summary['largest_unreviewed_cluster_size']}`",
        "",
        "## Top Clusters Needing Review",
        "",
    ]
    needing_review = [row for row in clusters if row["unreviewed_count"] > 0]
    for row in needing_review[:12]:
        lines.extend(
            [
                f"### `{row['pattern_id']}`",
                "",
                f"- Cases: `{row['case_count']}`",
                f"- Reviewed: `{row['reviewed_count']}`",
                f"- Unreviewed: `{row['unreviewed_count']}`",
                f"- Existing outcomes: `{row['existing_outcome_counts']}`",
                f"- Example queue: `{row['example_queue_id']}`",
                f"- Prompt: {row['review_prompt_tr']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            f"- allowed: {summary['claim_boundary']['allowed_claim']}",
            f"- not claimed: {summary['claim_boundary']['not_claimed']}",
            "",
        ]
    )
    return "\n".join(lines)


def run(reviewer_sheet_path: Path = DEFAULT_REVIEWER_SHEET, out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "clusters": out_dir / "action_time_pattern_cluster_review_p0_clusters.csv",
        "summary": out_dir / "action_time_pattern_cluster_review_p0_summary.json",
        "manifest": out_dir / "action_time_pattern_cluster_review_p0_manifest.json",
        "report": out_dir / "action_time_pattern_cluster_review_p0_report.md",
    }
    if not reviewer_sheet_path.exists():
        manifest = {
            "generated_at": utc_now(),
            "mode": "latentatlas_action_time_pattern_cluster_review_p0",
            "pattern_schema_version": PATTERN_SCHEMA_VERSION,
            "status": "blocked",
            "failure_reason": "missing_reviewer_sheet",
            "reviewer_sheet": str(reviewer_sheet_path),
            "internal_index_read": False,
            "external_calls_used_by_builder": False,
            "production_truth_mutation": False,
        }
        write_json(paths["manifest"], manifest)
        return manifest

    rows = read_csv(reviewer_sheet_path)
    clusters, summary = cluster_rows(rows)
    summary["input"] = str(reviewer_sheet_path)
    summary["outputs"] = {name: str(path) for name, path in paths.items()}
    fieldnames = [
        "pattern_id",
        "review_status",
        "case_count",
        "reviewed_count",
        "unreviewed_count",
        "unique_event_count",
        "unique_subject_count",
        "priority_rank_min",
        "priority_rank_max",
        "example_queue_id",
        "example_event_id",
        "example_priority_rank",
        "queue_id_sample",
        "event_id_sample",
        "existing_outcome_counts",
        "existing_notes_code_counts",
        "cluster_review_outcome",
        "cluster_review_confidence",
        "cluster_review_notes_code",
        "cluster_review_status",
        "review_prompt_tr",
        *PATTERN_FIELDS,
    ]
    write_csv(paths["clusters"], clusters, fieldnames)
    write_json(paths["summary"], summary)
    paths["report"].write_text(build_report(summary, clusters), encoding="utf-8")
    manifest = {
        "generated_at": summary["generated_at"],
        "mode": summary["mode"],
        "pattern_schema_version": summary["pattern_schema_version"],
        "status": summary["status"],
        "reviewer_sheet": str(reviewer_sheet_path),
        "clusters": str(paths["clusters"]),
        "summary": str(paths["summary"]),
        "report": str(paths["report"]),
        "cluster_count": summary["cluster_count"],
        "clusters_with_unreviewed_rows": summary["clusters_with_unreviewed_rows"],
        "unreviewed_outcome_ready_row_count": summary["unreviewed_outcome_ready_row_count"],
        "duplicate_queue_id_count": summary["duplicate_queue_id_count"],
        "duplicate_event_id_count": summary["duplicate_event_id_count"],
        "duplicate_subject_hash_count": summary["duplicate_subject_hash_count"],
        "internal_index_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": summary["outputs"],
    }
    write_json(paths["manifest"], manifest)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-sheet", type=Path, default=DEFAULT_REVIEWER_SHEET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.reviewer_sheet, args.out_dir)
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
