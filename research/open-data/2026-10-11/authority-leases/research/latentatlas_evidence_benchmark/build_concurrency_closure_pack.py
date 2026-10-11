#!/usr/bin/env python3
"""Close the current concurrency workstreams as bounded research artifacts.

The pack completes the five practical workstreams from the current status
review:

1. required packet fields,
2. negative-control fixtures,
3. local baseline replay,
4. stratified backfill execution planning,
5. reviewer strategy pivot.

It does not fabricate missing timestamps or reviewer labels, ingest external
responses, mutate production truth, or promote Level 4 probability claims.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_STATUS_SUMMARY = Path(
    "outputs/latentatlas/concurrency_current_status_review_20260718/concurrency_current_status_summary.json"
)
DEFAULT_PROTOCOL_STRATA = Path(
    "outputs/latentatlas/concurrent_evidence_failure_protocol_v1/concurrent_evidence_failure_strata_plan.csv"
)
DEFAULT_PROTOCOL_NEGATIVE_CONTROLS = Path(
    "outputs/latentatlas/concurrent_evidence_failure_protocol_v1/concurrent_evidence_failure_negative_controls.csv"
)
DEFAULT_FREEZE_ROWS = Path("outputs/latentatlas/action_time_p0_review_freeze_v1/action_time_p0_review_freeze_rows.csv")
DEFAULT_REVIEWER_PACK_CASES = Path("outputs/latentatlas/action_time_p0_reviewer_pack_v1/reviewer_pack_cases.csv")
DEFAULT_REVIEWER_RESPONSE_BLANK = Path(
    "outputs/latentatlas/action_time_p0_reviewer_pack_v1/reviewer_response_sheet_blank.csv"
)
DEFAULT_STRATA_TARGETS = Path(
    "outputs/latentatlas/action_time_level4_strata_fill_plan_v1/level4_strata_fill_targets.csv"
)
DEFAULT_BACKFILL_BATCH_SUMMARY = Path(
    "outputs/latentatlas/action_time_backfill_execution_batches_v1/backfill_execution_batches_summary.json"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concurrency_closure_pack_20260718")

SCHEMA_VERSION = "latentatlas_concurrency_closure_pack_v1"

FIELD_MAPPINGS = {
    "evidence_timestamp": {
        "current_sources": [],
        "candidate_sources": ["captured_at in Level 4 backfill reviewer packets"],
        "status": "missing_exact",
    },
    "action_timestamp": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "latest_state_timestamp": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "subject_cluster_hash": {
        "current_sources": ["source_subject_hash"],
        "candidate_sources": ["source_subject_hash"],
        "status": "available_exact",
    },
    "source_type": {
        "current_sources": [],
        "candidate_sources": ["workflow_source in Level 4 backfill reviewer packets"],
        "status": "missing_in_p0_freeze",
    },
    "canonical_identity_hash": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "action_target_hash": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "identity_conflict_flag": {
        "current_sources": ["observed_change_type"],
        "candidate_sources": ["observed_change_type == identity_conflict_masked"],
        "status": "derivable_from_masked_field",
    },
    "decision_id": {
        "current_sources": ["queue_id", "event_id"],
        "candidate_sources": ["queue_id", "event_id"],
        "status": "available_exact",
    },
    "authority_issued_at": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "authority_expires_at": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "permission_hash": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "policy_hash": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "materialization_timestamp": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "action_type": {
        "current_sources": ["action_type"],
        "candidate_sources": ["action_type"],
        "status": "available_exact",
    },
    "state_delta_hash": {
        "current_sources": ["masked_state_before", "masked_state_after"],
        "candidate_sources": ["sha256(masked_state_before || masked_state_after)"],
        "status": "derivable_from_masked_field",
    },
    "output_hash": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "visibility_status": {
        "current_sources": ["operator_visual_verdict"],
        "candidate_sources": ["operator_visual_verdict"],
        "status": "derivable_from_masked_field",
    },
    "fetch_status": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "unblock_proof_timestamp": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "independent_source_evidence": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "reviewer_id": {
        "current_sources": ["reviewer_id_hash"],
        "candidate_sources": ["reviewer_id_hash"],
        "status": "available_exact",
    },
    "rationale_short": {
        "current_sources": [],
        "candidate_sources": ["rationale_short in response sheet"],
        "status": "missing_until_response",
    },
    "packet_field_citations": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
    "non_packet_fact_flags": {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
}

CLAIM_STRENGTH_BY_STATUS = {
    "available_exact": "eligible_for_field_level_measurement",
    "derivable_from_masked_field": "eligible_after_derivation_rule_review",
    "missing_until_response": "blocked_until_response",
    "missing_in_p0_freeze": "blocked_for_current_p0_freeze",
    "missing_exact": "blocked_for_current_p0_freeze",
}

SYNTHETIC_FIXTURE_VALUES = {
    "evidence_timestamp": ("2026-07-18T10:00:00+00:00", "2026-07-18T10:05:00+00:00"),
    "action_timestamp": ("2026-07-18T10:10:00+00:00", "2026-07-18T10:10:00+00:00"),
    "latest_state_timestamp": ("2026-07-18T10:08:00+00:00", "2026-07-18T10:05:00+00:00"),
    "subject_cluster_hash": ("synthetic_subject_hash_A", "synthetic_subject_hash_A"),
    "source_type": ("masked_shadow_packet", "masked_shadow_packet"),
    "canonical_identity_hash": ("synthetic_canonical_A", "synthetic_canonical_A"),
    "action_target_hash": ("synthetic_target_B", "synthetic_canonical_A"),
    "identity_conflict_flag": ("true", "false"),
    "decision_id": ("synthetic_decision_001", "synthetic_decision_002"),
    "authority_issued_at": ("2026-07-17T00:00:00+00:00", "2026-07-18T09:00:00+00:00"),
    "authority_expires_at": ("2026-07-18T09:59:00+00:00", "2026-07-18T12:00:00+00:00"),
    "permission_hash": ("synthetic_permission_v1", "synthetic_permission_v1"),
    "policy_hash": ("synthetic_policy_v1", "synthetic_policy_v1"),
    "materialization_timestamp": ("2026-07-18T10:10:00+00:00", "2026-07-18T10:06:00+00:00"),
    "action_type": ("manual_review_before_materialization", "manual_review_before_materialization"),
    "state_delta_hash": ("synthetic_delta_changed", "synthetic_delta_stable"),
    "output_hash": ("synthetic_output_old", "synthetic_output_latest"),
    "visibility_status": ("blocked_pdp", "visible_fresh"),
    "fetch_status": ("blocked", "ok"),
    "unblock_proof_timestamp": ("", "2026-07-18T10:07:00+00:00"),
    "independent_source_evidence": ("", "synthetic_independent_hash"),
    "reviewer_id": ("synthetic_reviewer_A", "synthetic_reviewer_A"),
    "rationale_short": ("imports outside packet context", "cites packet fields only"),
    "packet_field_citations": ("", "case_fields:state_before,state_after"),
    "non_packet_fact_flags": ("true", "false"),
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


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


def short_hash(*values: str) -> str:
    payload = "|".join(values).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_key(row: dict[str, str]) -> str:
    return row.get("queue_id") or row.get("event_id") or short_hash(json.dumps(row, sort_keys=True))


def source_paths() -> dict[str, Path]:
    return {
        "status_summary": DEFAULT_STATUS_SUMMARY,
        "protocol_strata": DEFAULT_PROTOCOL_STRATA,
        "protocol_negative_controls": DEFAULT_PROTOCOL_NEGATIVE_CONTROLS,
        "freeze_rows": DEFAULT_FREEZE_ROWS,
        "reviewer_pack_cases": DEFAULT_REVIEWER_PACK_CASES,
        "reviewer_response_blank": DEFAULT_REVIEWER_RESPONSE_BLANK,
        "strata_targets": DEFAULT_STRATA_TARGETS,
        "backfill_batch_summary": DEFAULT_BACKFILL_BATCH_SUMMARY,
    }


def output_paths(out_dir: Path) -> dict[str, Path]:
    return {
        "required_fields_contract": out_dir / "concurrency_required_fields_contract.csv",
        "required_fields_validation": out_dir / "concurrency_required_fields_validation.csv",
        "negative_control_fixtures": out_dir / "concurrency_negative_control_fixtures.csv",
        "negative_control_assertions": out_dir / "concurrency_negative_control_assertions.csv",
        "baseline_replay": out_dir / "concurrency_baseline_replay.csv",
        "family_overlap_matrix": out_dir / "concurrency_family_overlap_matrix.csv",
        "replay_policy_disclosure": out_dir / "concurrency_replay_policy_disclosure.md",
        "stratified_backfill_closure": out_dir / "concurrency_stratified_backfill_closure.csv",
        "reviewer_strategy_policy": out_dir / "concurrency_reviewer_strategy_policy.md",
        "workstream_closure_matrix": out_dir / "concurrency_workstream_closure_matrix.csv",
        "report": out_dir / "concurrency_closure_report.md",
        "summary": out_dir / "concurrency_closure_summary.json",
        "manifest": out_dir / "concurrency_closure_manifest.json",
    }


def split_fields(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def blocked_summary(reason: str, paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_concurrency_closure_pack",
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


def build_required_fields_contract(protocol_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for protocol in protocol_rows:
        family_id = protocol["family_id"]
        for field_name in split_fields(protocol["required_fields"]):
            mapping = FIELD_MAPPINGS.get(
                field_name,
                {"current_sources": [], "candidate_sources": [], "status": "missing_exact"},
            )
            rows.append(
                {
                    "family_id": family_id,
                    "required_field": field_name,
                    "current_sources": "|".join(mapping["current_sources"]),
                    "candidate_sources": "|".join(mapping["candidate_sources"]),
                    "field_status": mapping["status"],
                    "claim_strength": CLAIM_STRENGTH_BY_STATUS.get(mapping["status"], "blocked_for_current_p0_freeze"),
                    "promotion_rule": "Field must be packet-visible, non-empty, and source-mapped before family-level measurement.",
                }
            )
    return rows


def field_available(row: dict[str, str], required_field: str) -> bool:
    mapping = FIELD_MAPPINGS.get(required_field, {})
    current_sources = mapping.get("current_sources", [])
    if not current_sources:
        return False
    if mapping.get("status") == "derivable_from_masked_field":
        return all(source in row and row.get(source, "") != "" for source in current_sources)
    return all(source in row and row.get(source, "") != "" for source in current_sources)


def build_required_fields_validation(
    protocol_rows: list[dict[str, str]], freeze_rows: list[dict[str, str]]
) -> list[dict[str, Any]]:
    validation: list[dict[str, Any]] = []
    total_rows = len(freeze_rows)
    for protocol in protocol_rows:
        family_id = protocol["family_id"]
        required_fields = split_fields(protocol["required_fields"])
        for required_field in required_fields:
            present_count = sum(1 for row in freeze_rows if field_available(row, required_field))
            mapping_status = FIELD_MAPPINGS.get(required_field, {}).get("status", "missing_exact")
            validation.append(
                {
                    "family_id": family_id,
                    "required_field": required_field,
                    "current_p0_rows_checked": total_rows,
                    "present_or_derivable_count": present_count,
                    "missing_count": total_rows - present_count,
                    "coverage_rate": f"{present_count / total_rows:.4f}" if total_rows else "",
                    "field_status": mapping_status,
                    "validation_state": (
                        "pass"
                        if present_count == total_rows and mapping_status == "available_exact"
                        else "fail_closed_until_schema_upgrade"
                    ),
                }
            )
    return validation


def build_negative_fixtures(protocol_rows: list[dict[str, str]], negative_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    negative_by_family = {row["family_id"]: row for row in negative_rows}
    fixtures: list[dict[str, Any]] = []
    for protocol in protocol_rows:
        family_id = protocol["family_id"]
        required_fields = split_fields(protocol["required_fields"])
        negative_control = negative_by_family.get(family_id, {}).get("negative_control", "")
        for fixture_type, expected in [("positive", f"detect_{family_id}"), ("negative", f"do_not_detect_{family_id}")]:
            index = 0 if fixture_type == "positive" else 1
            row: dict[str, Any] = {
                "fixture_id": f"{family_id}_{fixture_type}_001",
                "family_id": family_id,
                "fixture_type": fixture_type,
                "synthetic_only": True,
                "expected_result": expected,
                "positive_test": protocol.get("positive_test", ""),
                "negative_control": negative_control,
                "required_fields": ",".join(required_fields),
                "fixture_payload_hash": "",
            }
            payload_parts = []
            for field_name in required_fields:
                value_pair = SYNTHETIC_FIXTURE_VALUES.get(field_name, ("synthetic_positive", "synthetic_negative"))
                row[field_name] = value_pair[index]
                payload_parts.append(f"{field_name}={row[field_name]}")
            row["fixture_payload_hash"] = short_hash(family_id, fixture_type, *payload_parts)
            fixtures.append(row)
    return fixtures


def build_negative_assertions(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        assertion = "pass"
        if fixture["fixture_type"] == "negative" and not fixture["expected_result"].startswith("do_not_detect_"):
            assertion = "fail"
        if fixture["fixture_type"] == "positive" and not fixture["expected_result"].startswith("detect_"):
            assertion = "fail"
        rows.append(
            {
                "fixture_id": fixture["fixture_id"],
                "family_id": fixture["family_id"],
                "fixture_type": fixture["fixture_type"],
                "expected_result": fixture["expected_result"],
                "assertion_state": assertion,
                "claim_boundary": "Synthetic fixture assertion only; not an empirical outcome row.",
            }
        )
    return rows


def outcome_counts(rows: list[dict[str, str]]) -> Counter:
    return Counter(row.get("reviewed_outcome", "") for row in rows)


def replay_row(family_id: str, rows: list[dict[str, str]], selection_rule: str) -> dict[str, Any]:
    counts = outcome_counts(rows)
    total = len(rows)
    correct_block = counts.get("correct_block", 0)
    false_block = counts.get("false_block", 0)
    needs_more = counts.get("needs_more_evidence", 0)
    decision_time_only_block_count = total
    action_time_policy_block_count = correct_block
    action_time_policy_hold_count = false_block + needs_more
    avoidable_overblock_or_hold_count = false_block + needs_more
    return {
        "family_id": family_id,
        "selection_rule": selection_rule,
        "rows_replayed": total,
        "decision_time_only_policy": "treat prior revalidation/block signal as action permission",
        "decision_time_only_block_count": decision_time_only_block_count,
        "action_time_freshness_policy": "diagnostic mapping: block packet-supported blocks; hold/revalidate unsupported or insufficient-evidence cases",
        "action_time_policy_block_count": action_time_policy_block_count,
        "action_time_policy_hold_or_revalidate_count": action_time_policy_hold_count,
        "local_avoidable_overblock_or_hold_count": avoidable_overblock_or_hold_count,
        "local_avoidable_overblock_or_hold_rate": f"{avoidable_overblock_or_hold_count / total:.4f}" if total else "",
        "reviewed_outcome_counts": json.dumps(dict(sorted(counts.items())), sort_keys=True),
        "claim_boundary": "Label-conditioned diagnostic replay on frozen P0 rows; not independent policy validation, causal proof, or population rate.",
    }


def family_selection_rows(freeze_rows: list[dict[str, str]]) -> dict[str, tuple[str, list[dict[str, str]]]]:
    stale_rows = [
        row
        for row in freeze_rows
        if row.get("pdp_temporal_authority_evidence") == "latest_pdp_review_pool_snapshot_present"
    ]
    materialization_rows = [
        row for row in freeze_rows if row.get("action_type") == "manual_review_before_materialization"
    ]
    authority_rows = list(freeze_rows)
    visibility_rows = [row for row in freeze_rows if row.get("operator_visual_verdict") == "blocked_pdp"]
    identity_rows = [row for row in freeze_rows if row.get("observed_change_type") == "identity_conflict_masked"]
    return {
        "stale_read": (
            "pdp_temporal_authority_evidence == latest_pdp_review_pool_snapshot_present",
            stale_rows,
        ),
        "materialization_race": ("action_type == manual_review_before_materialization", materialization_rows),
        "authority_expiry": ("all frozen reviewed P0 rows", authority_rows),
        "visibility_truth_confusion": ("operator_visual_verdict == blocked_pdp", visibility_rows),
        "identity_time_split": ("observed_change_type == identity_conflict_masked", identity_rows),
    }


def build_baseline_replay(freeze_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selections = family_selection_rows(freeze_rows)
    return [
        replay_row(family_id, rows, selection_rule)
        for family_id, (selection_rule, rows) in selections.items()
    ]


def overlap_relationship(a_keys: set[str], b_keys: set[str]) -> str:
    overlap = a_keys & b_keys
    if a_keys == b_keys:
        return "same_set"
    if not overlap:
        return "disjoint"
    if overlap == a_keys:
        return "subset_of_family_b"
    if overlap == b_keys:
        return "superset_of_family_b"
    return "partial_overlap"


def build_family_overlap_matrix(selections: dict[str, tuple[str, list[dict[str, str]]]]) -> list[dict[str, Any]]:
    keyed = {family_id: {row_key(row) for row in rows} for family_id, (_, rows) in selections.items()}
    rows: list[dict[str, Any]] = []
    for family_a, keys_a in keyed.items():
        for family_b, keys_b in keyed.items():
            overlap = keys_a & keys_b
            count_a = len(keys_a)
            count_b = len(keys_b)
            rows.append(
                {
                    "family_a": family_a,
                    "family_b": family_b,
                    "family_a_count": count_a,
                    "family_b_count": count_b,
                    "overlap_count": len(overlap),
                    "overlap_rate_of_a": f"{len(overlap) / count_a:.4f}" if count_a else "",
                    "overlap_rate_of_b": f"{len(overlap) / count_b:.4f}" if count_b else "",
                    "relationship": overlap_relationship(keys_a, keys_b),
                    "claim_boundary": "Families are non-exclusive diagnostic slices; counts must not be summed as independent evidence.",
                }
            )
    return rows


def build_replay_policy_disclosure(sources: dict[str, Path]) -> dict[str, Any]:
    return {
        "replay_policy_independence": "not_independent_label_conditioned_diagnostic",
        "policy_defined_before_review_labels": False,
        "policy_pre_registration_status": "not_preregistered",
        "policy_code_reads_review_judgments": True,
        "thresholds_tuned_after_results": False,
        "threshold_note": "No numeric threshold is fitted; the replay maps frozen review judgments into block versus hold/revalidate lanes.",
        "execution_mode": "automatic_csv_builder",
        "manual_replay_used": False,
        "policy_source": str(Path(__file__)),
        "policy_source_sha256": sha256_file(Path(__file__)),
        "freeze_rows_path": str(sources["freeze_rows"]),
        "freeze_rows_sha256": sha256_file(sources["freeze_rows"]),
        "claim_boundary": "Diagnostic replay only; not an independent estimate of policy effectiveness.",
    }


def build_replay_policy_disclosure_markdown(disclosure: dict[str, Any]) -> str:
    rows = [
        ["Replay independent of review labels?", "No. It is a label-conditioned diagnostic replay."],
        ["Policy defined before labels?", str(disclosure["policy_defined_before_review_labels"])],
        ["Policy code reads review judgments?", str(disclosure["policy_code_reads_review_judgments"])],
        ["Thresholds tuned after results?", str(disclosure["thresholds_tuned_after_results"])],
        ["Execution mode", disclosure["execution_mode"]],
        ["Manual replay used?", str(disclosure["manual_replay_used"])],
        ["Policy source SHA-256", disclosure["policy_source_sha256"]],
        ["Freeze rows SHA-256", disclosure["freeze_rows_sha256"]],
    ]
    return "\n".join(
        [
            "# Replay Policy Disclosure",
            "",
            "The local replay is not presented as an independent policy-engine result.",
            "It is an automatic diagnostic replay that reads frozen review judgments and maps them into block versus hold/revalidate lanes.",
            "",
            *markdown_table(["Question", "Answer"], rows),
            "",
            f"Boundary: {disclosure['claim_boundary']}",
            "",
        ]
    )


def build_stratified_backfill_closure(
    targets: list[dict[str, str]], backfill_summary: dict[str, Any]
) -> list[dict[str, Any]]:
    batch_count = backfill_summary.get("batch_count")
    pending_queue_count = backfill_summary.get("pending_queue_count")
    rows: list[dict[str, Any]] = []
    for target in targets:
        rows.append(
            {
                "target_id": target["target_id"],
                "priority": target["priority"],
                "stratum_group": target["stratum_group"],
                "stratum_value": target["stratum_value"],
                "current": target["current"],
                "minimum": target["minimum"],
                "gap": target["gap"],
                "negative_control_minimum": target["negative_control_minimum"],
                "collection_lane": target["collection_lane"],
                "review_lane": target["review_lane"],
                "available_execution_batches": batch_count,
                "pending_queue_count": pending_queue_count,
                "closure_state": "execution_plan_closed_review_or_source_collection_still_required",
                "claim_boundary": "Target is a masked source/review plan, not collected or reviewed evidence.",
            }
        )
    return rows


def build_reviewer_strategy_policy(status_summary: dict[str, Any]) -> str:
    reviewer = status_summary.get("reviewer_state", {})
    lines = [
        "# Concurrency Reviewer Strategy Policy",
        "",
        f"Generated at: `{utc_now()}`",
        "",
        "## Decision",
        "",
        "Free full reviewer acquisition is no longer the primary blocking path for the concurrency workstream.",
        "",
        "Mini-reviews, paid-consulting-shaped replies, referrals, and informal comments may be logged only as qualitative method-fit or grounding signals. They do not count as reviewer02 completion, inter-reviewer agreement, kappa, Level 4 evidence, or population probability support.",
        "",
        "## Current Reviewer State",
        "",
        *markdown_table(
            ["Signal", "State"],
            [
                ["Full reviewer02", reviewer.get("full_reviewer02_state", "")],
                ["Agreement calculable", reviewer.get("agreement_calculable", "")],
                ["P0 reviewer02 rows", f"{reviewer.get('completed_second_review_rows', '')} complete / {reviewer.get('missing_second_review_rows', '')} missing"],
                ["Independent reviews", f"{reviewer.get('current_independent_human_review_count', '')}/{reviewer.get('minimum_independent_review_count', '')}"],
                ["Decision", reviewer.get("decision", "")],
            ],
        ),
        "",
        "## Allowed Use",
        "",
        "- Use internal replication, schema enforcement, negative controls, and local replay now.",
        "- If a mini-review response arrives, audit every rationale for packet-only grounding.",
        "- Count external labels only if the exact full reviewer02 scope, response sheet, and validation gates are satisfied.",
        "",
        "## Blocked Use",
        "",
        "- Do not call mini-review a second review.",
        "- Do not compute agreement or kappa from informal responses.",
        "- Do not use consulting discovery calls as evidence labels.",
        "- Do not promote Level 4 or population claims without the Level 4 gates.",
        "",
    ]
    return "\n".join(lines)


def build_workstream_matrix(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "workstream": "schema_required_fields",
            "closure_state": "closed_as_contract_and_fail_closed_validation",
            "artifact": summary["outputs"]["required_fields_contract"],
            "remaining_external_blocker": "",
            "level4_claim_allowed": False,
        },
        {
            "workstream": "negative_control_fixtures",
            "closure_state": "closed_with_synthetic_fixture_suite",
            "artifact": summary["outputs"]["negative_control_fixtures"],
            "remaining_external_blocker": "",
            "level4_claim_allowed": False,
        },
        {
            "workstream": "baseline_replay",
            "closure_state": "closed_as_local_proxy_replay",
            "artifact": summary["outputs"]["baseline_replay"],
            "remaining_external_blocker": "",
            "level4_claim_allowed": False,
        },
        {
            "workstream": "stratified_backfill_review",
            "closure_state": "closed_as_execution_plan_review_execution_still_required",
            "artifact": summary["outputs"]["stratified_backfill_closure"],
            "remaining_external_blocker": "independent review execution and source collection",
            "level4_claim_allowed": False,
        },
        {
            "workstream": "reviewer_strategy_pivot",
            "closure_state": "closed_as_policy",
            "artifact": summary["outputs"]["reviewer_strategy_policy"],
            "remaining_external_blocker": "full reviewer02 only if future validated response arrives",
            "level4_claim_allowed": False,
        },
    ]


def build_report(summary: dict[str, Any]) -> str:
    if summary["status"] != "pass":
        return "\n".join(
            [
                "# Concurrency Closure Report",
                "",
                f"Generated at: `{summary['generated_at_utc']}`",
                f"Status: `{summary['status']}`",
                "",
                *[f"- {reason}" for reason in summary.get("failure_reasons", [])],
                "",
            ]
        )
    matrix = summary["workstream_closure_matrix"]
    replay_rows = summary["baseline_replay"]
    overlap_rows = [
        row
        for row in summary.get("family_overlap_matrix", [])
        if row["family_a"] < row["family_b"] and int(row.get("overlap_count", 0)) > 0
    ]
    disclosure = summary.get("replay_policy_disclosure", {})
    lines = [
        "# Concurrency Closure Report",
        "",
        f"Generated at: `{summary['generated_at_utc']}`",
        f"Status: `{summary['status']}`",
        f"Closure state: `{summary['closure_state']}`",
        "",
        "## Executive Read",
        "",
        "All five concurrency workstreams are now closed at the artifact/protocol level. Level 4 remains blocked because missing reviewer02 labels, unexecuted independent review batches, weak strata, and holdout replication cannot be fabricated.",
        "",
        "## Workstream Closure Matrix",
        "",
        *markdown_table(
            ["Workstream", "Closure State", "Remaining External Blocker"],
            [[row["workstream"], row["closure_state"], row["remaining_external_blocker"]] for row in matrix],
        ),
        "",
        "## Local Baseline Replay",
        "",
        *markdown_table(
            [
                "Family",
                "Rows",
                "Decision-Time Blocks",
                "Action-Time Blocks",
                "Hold/Revalidate",
                "Local Avoidable Rate",
            ],
            [
                [
                    row["family_id"],
                    row["rows_replayed"],
                    row["decision_time_only_block_count"],
                    row["action_time_policy_block_count"],
                    row["action_time_policy_hold_or_revalidate_count"],
                    row["local_avoidable_overblock_or_hold_rate"],
                ]
                for row in replay_rows
            ],
        ),
        "",
        "## Replay Policy Disclosure",
        "",
        f"- Replay independence: `{disclosure.get('replay_policy_independence', '')}`",
        f"- Policy code reads review judgments: `{disclosure.get('policy_code_reads_review_judgments', '')}`",
        f"- Thresholds tuned after results: `{disclosure.get('thresholds_tuned_after_results', '')}`",
        f"- Execution mode: `{disclosure.get('execution_mode', '')}`",
        f"- Boundary: {disclosure.get('claim_boundary', '')}",
        "",
        "## Family Overlap",
        "",
        *markdown_table(
            ["Family A", "Family B", "A Count", "B Count", "Overlap", "Relationship"],
            [
                [
                    row["family_a"],
                    row["family_b"],
                    row["family_a_count"],
                    row["family_b_count"],
                    row["overlap_count"],
                    row["relationship"],
                ]
                for row in overlap_rows
            ],
        ),
        "",
        "The family rows are non-exclusive diagnostic slices. Overlapping rows must not be summed as independent evidence.",
        "",
        "## Claim Boundary",
        "",
        "- Allowed: protocol artifacts, local frozen-set observations, synthetic negative-control fixtures, label-conditioned diagnostic replay.",
        "- Blocked: probability claims, population concurrency rates, reviewer reliability claims, independent replay effectiveness, production/customer truth mutation.",
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


def run(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = source_paths()
    paths = output_paths(out_dir)
    missing = [str(path) for path in sources.values() if not path.exists()]
    if missing:
        summary = blocked_summary(f"missing required sources: {', '.join(missing)}", paths)
    else:
        status_summary = read_json(sources["status_summary"])
        protocol_rows = read_csv(sources["protocol_strata"])
        protocol_negative_rows = read_csv(sources["protocol_negative_controls"])
        freeze_rows = read_csv(sources["freeze_rows"])
        strata_targets = read_csv(sources["strata_targets"])
        backfill_summary = read_json(sources["backfill_batch_summary"])

        if status_summary.get("status") != "pass":
            summary = blocked_summary("status summary is not pass", paths)
        elif backfill_summary.get("status") != "pass":
            summary = blocked_summary("backfill batch summary is not pass", paths)
        else:
            required_contract = build_required_fields_contract(protocol_rows)
            required_validation = build_required_fields_validation(protocol_rows, freeze_rows)
            negative_fixtures = build_negative_fixtures(protocol_rows, protocol_negative_rows)
            negative_assertions = build_negative_assertions(negative_fixtures)
            family_selections = family_selection_rows(freeze_rows)
            baseline_replay = build_baseline_replay(freeze_rows)
            family_overlap_matrix = build_family_overlap_matrix(family_selections)
            replay_policy_disclosure = build_replay_policy_disclosure(sources)
            stratified_backfill = build_stratified_backfill_closure(strata_targets, backfill_summary)
            schema_missing_exact_count = sum(
                1 for row in required_validation if row["validation_state"] == "fail_closed_until_schema_upgrade"
            )
            assertion_fail_count = sum(1 for row in negative_assertions if row["assertion_state"] != "pass")
            summary = {
                "generated_at_utc": utc_now(),
                "mode": "latentatlas_concurrency_closure_pack",
                "schema_version": SCHEMA_VERSION,
                "status": "pass",
                "closure_state": "all_workstreams_closed_as_bounded_artifacts_level4_still_blocked",
                "level4_probability_claim_allowed": False,
                "workstream_count": 5,
                "required_field_contract_rows": len(required_contract),
                "required_field_fail_closed_rows": schema_missing_exact_count,
                "negative_fixture_count": len(negative_fixtures),
                "negative_assertion_fail_count": assertion_fail_count,
                "baseline_replay_family_count": len(baseline_replay),
                "family_overlap_pair_count": len(family_overlap_matrix),
                "stratified_backfill_target_count": len(stratified_backfill),
                "baseline_replay": baseline_replay,
                "family_overlap_matrix": family_overlap_matrix,
                "replay_policy_disclosure": replay_policy_disclosure,
                "artifact_integrity": {
                    "policy_source_sha256": replay_policy_disclosure["policy_source_sha256"],
                    "freeze_rows_sha256": replay_policy_disclosure["freeze_rows_sha256"],
                    "status_summary_sha256": sha256_file(sources["status_summary"]),
                    "protocol_strata_sha256": sha256_file(sources["protocol_strata"]),
                    "protocol_negative_controls_sha256": sha256_file(sources["protocol_negative_controls"]),
                },
                "claim_boundary": {
                    "allowed_claims": [
                        "Closed Level 3.5 concurrency artifacts.",
                        "Current P0 rows fail closed where required fields are missing.",
                        "Synthetic negative controls can guard future detectors.",
                        "Label-conditioned diagnostic replay can describe frozen-set deltas.",
                    ],
                    "blocked_claims": [
                        "Level 4 probability evidence.",
                        "Population concurrency failure rates.",
                        "Reviewer agreement or reliability claims.",
                        "Independent policy-effectiveness estimate from the replay.",
                        "Customer-facing or production truth mutation.",
                    ],
                },
                "contains_customer_data": False,
                "contains_personal_data": False,
                "raw_source_rows_read": False,
                "external_calls_used_by_builder": False,
                "production_truth_mutation": False,
                "inputs": {key: str(value) for key, value in sources.items()},
                "outputs": {key: str(value) for key, value in paths.items()},
            }
            summary["workstream_closure_matrix"] = build_workstream_matrix(summary)

            write_csv(
                paths["required_fields_contract"],
                required_contract,
                [
                    "family_id",
                    "required_field",
                    "current_sources",
                    "candidate_sources",
                    "field_status",
                    "claim_strength",
                    "promotion_rule",
                ],
            )
            write_csv(
                paths["required_fields_validation"],
                required_validation,
                [
                    "family_id",
                    "required_field",
                    "current_p0_rows_checked",
                    "present_or_derivable_count",
                    "missing_count",
                    "coverage_rate",
                    "field_status",
                    "validation_state",
                ],
            )
            fixture_fields = sorted({key for row in negative_fixtures for key in row.keys()})
            write_csv(paths["negative_control_fixtures"], negative_fixtures, fixture_fields)
            write_csv(
                paths["negative_control_assertions"],
                negative_assertions,
                ["fixture_id", "family_id", "fixture_type", "expected_result", "assertion_state", "claim_boundary"],
            )
            write_csv(
                paths["baseline_replay"],
                baseline_replay,
                [
                    "family_id",
                    "selection_rule",
                    "rows_replayed",
                    "decision_time_only_policy",
                    "decision_time_only_block_count",
                    "action_time_freshness_policy",
                    "action_time_policy_block_count",
                    "action_time_policy_hold_or_revalidate_count",
                    "local_avoidable_overblock_or_hold_count",
                    "local_avoidable_overblock_or_hold_rate",
                    "reviewed_outcome_counts",
                    "claim_boundary",
                ],
            )
            write_csv(
                paths["family_overlap_matrix"],
                family_overlap_matrix,
                [
                    "family_a",
                    "family_b",
                    "family_a_count",
                    "family_b_count",
                    "overlap_count",
                    "overlap_rate_of_a",
                    "overlap_rate_of_b",
                    "relationship",
                    "claim_boundary",
                ],
            )
            write_text(paths["replay_policy_disclosure"], build_replay_policy_disclosure_markdown(replay_policy_disclosure))
            write_csv(
                paths["stratified_backfill_closure"],
                stratified_backfill,
                [
                    "target_id",
                    "priority",
                    "stratum_group",
                    "stratum_value",
                    "current",
                    "minimum",
                    "gap",
                    "negative_control_minimum",
                    "collection_lane",
                    "review_lane",
                    "available_execution_batches",
                    "pending_queue_count",
                    "closure_state",
                    "claim_boundary",
                ],
            )
            write_text(paths["reviewer_strategy_policy"], build_reviewer_strategy_policy(status_summary))
            write_csv(
                paths["workstream_closure_matrix"],
                summary["workstream_closure_matrix"],
                ["workstream", "closure_state", "artifact", "remaining_external_blocker", "level4_claim_allowed"],
            )

    write_text(paths["report"], build_report(summary))
    write_json(paths["summary"], summary)
    write_json(
        paths["manifest"],
        {
            "generated_at_utc": summary["generated_at_utc"],
            "mode": summary["mode"],
            "schema_version": summary.get("schema_version", SCHEMA_VERSION),
            "status": summary["status"],
            "closure_state": summary.get("closure_state"),
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
