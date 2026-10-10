#!/usr/bin/env python3
"""Build the LatentAtlas action-time P0 empirical finding pack.

The pack summarizes a frozen masked human-review set as empirical descriptive
evidence. It intentionally does not claim population probability, production
truth, or customer-facing readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_FREEZE_ROWS = Path("outputs/latentatlas/action_time_p0_review_freeze_v1/action_time_p0_review_freeze_rows.csv")
DEFAULT_FREEZE_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_review_freeze_v1/action_time_p0_review_freeze_summary.json"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_p0_empirical_finding_pack_v1")

PACK_SCHEMA_VERSION = "latentatlas_action_time_p0_empirical_finding_pack_v1"
RESOLVED_OUTCOMES = {"correct_block", "false_allow", "false_block", "missed_revalidation", "safe_allow"}
UNRESOLVED_OUTCOME = "needs_more_evidence"

METRIC_FIELDS = [
    "metric_id",
    "description",
    "numerator",
    "denominator",
    "rate",
    "wilson_95_low",
    "wilson_95_high",
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


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def pct(part: int, whole: int) -> float:
    if whole == 0:
        return 0.0
    return round(part / whole, 4)


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    phat = successes / total
    denom = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)


def parse_pipe_state(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for part in (text or "").split("|"):
        if ":" in part:
            key, value = part.split(":", 1)
            parsed[key] = value
    return parsed


def counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def nested_counter_dict(counter: dict[str, Counter[str]]) -> dict[str, dict[str, int]]:
    return {key: dict(sorted(value.items())) for key, value in sorted(counter.items())}


def metric(metric_id: str, description: str, numerator: int, denominator: int, boundary: str) -> dict[str, Any]:
    low, high = wilson_interval(numerator, denominator)
    return {
        "metric_id": metric_id,
        "description": description,
        "numerator": numerator,
        "denominator": denominator,
        "rate": pct(numerator, denominator),
        "wilson_95_low": low,
        "wilson_95_high": high,
        "claim_boundary": boundary,
    }


def rows_by_operator(rows: list[dict[str, str]], operator: str) -> list[dict[str, str]]:
    return [row for row in rows if row.get("operator_visual_verdict") == operator]


def build_pack(frozen_rows: list[dict[str, str]], freeze_summary: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if freeze_summary.get("status") != "pass":
        return [], {
            "generated_at_utc": utc_now(),
            "mode": "latentatlas_action_time_p0_empirical_finding_pack",
            "status": "blocked",
            "failure_reasons": ["freeze summary is not pass"],
            "freeze_id": freeze_summary.get("freeze_id", ""),
            "freeze_hash_sha256": freeze_summary.get("freeze_hash_sha256", ""),
            "denominators": {},
            "outcome_counts": {},
            "outcome_rates_all_reviewed": {},
            "metrics": [],
            "finding_cards": [],
            "level4_missing": [],
            "claim_boundary": {
                "allowed_claims": [],
                "blocked_claims": ["The empirical finding pack cannot be built from a non-pass freeze."],
            },
            "production_truth_mutation": False,
            "external_calls_used_by_builder": False,
            "internal_index_read": False,
        }

    reviewed_count = len(frozen_rows)
    outcome_counts = Counter(row.get("reviewed_outcome", "") for row in frozen_rows)
    resolved_rows = [row for row in frozen_rows if row.get("reviewed_outcome") in RESOLVED_OUTCOMES]
    resolved_count = len(resolved_rows)
    correct_count = outcome_counts.get("correct_block", 0)
    false_block_count = outcome_counts.get("false_block", 0)
    unresolved_count = outcome_counts.get(UNRESOLVED_OUTCOME, 0)

    outcome_by_change_type: dict[str, Counter[str]] = defaultdict(Counter)
    outcome_by_action_type: dict[str, Counter[str]] = defaultdict(Counter)
    outcome_by_operator: dict[str, Counter[str]] = defaultdict(Counter)
    outcome_by_temporal: dict[str, Counter[str]] = defaultdict(Counter)
    notes_by_outcome: dict[str, Counter[str]] = defaultdict(Counter)
    flag_profiles: Counter[str] = Counter()
    for row in frozen_rows:
        outcome = row.get("reviewed_outcome", "")
        outcome_by_change_type[row.get("observed_change_type", "")][outcome] += 1
        outcome_by_action_type[row.get("action_type", "")][outcome] += 1
        outcome_by_operator[row.get("operator_visual_verdict", "")][outcome] += 1
        outcome_by_temporal[row.get("pdp_temporal_authority_evidence", "")][outcome] += 1
        notes_by_outcome[outcome][row.get("notes_code", "")] += 1
        state = parse_pipe_state(row.get("masked_state_after", ""))
        flag_profiles[
            "|".join(
                [
                    f"identity:{state.get('identity_match', '')}",
                    f"price:{state.get('price_match', '')}",
                    f"seller:{state.get('seller_comparable', '')}",
                    f"availability:{state.get('availability_confirmed', '')}",
                ]
            )
        ] += 1

    identity_rows = [row for row in frozen_rows if row.get("observed_change_type") == "identity_conflict_masked"]
    blocked_pdp_rows = rows_by_operator(frozen_rows, "blocked_pdp")
    latest_temporal_rows = [
        row
        for row in frozen_rows
        if row.get("pdp_temporal_authority_evidence") == "latest_pdp_review_pool_snapshot_present"
    ]

    metrics = [
        metric(
            "review_completion",
            "Reviewed outcome-ready P0 packets in the freeze",
            reviewed_count,
            int(freeze_summary.get("outcome_ready_p0_rows") or reviewed_count),
            "Freeze completeness metric, not a population probability.",
        ),
        metric(
            "correct_block_all_reviewed",
            "correct_block among all reviewed P0 outcome-ready packets",
            correct_count,
            reviewed_count,
            "Descriptive rate within the frozen reviewed set only.",
        ),
        metric(
            "false_block_all_reviewed",
            "false_block among all reviewed P0 outcome-ready packets",
            false_block_count,
            reviewed_count,
            "Descriptive rate within the frozen reviewed set only.",
        ),
        metric(
            "needs_more_evidence_all_reviewed",
            "needs_more_evidence among all reviewed P0 outcome-ready packets",
            unresolved_count,
            reviewed_count,
            "Descriptive unresolved-evidence rate within the frozen reviewed set only.",
        ),
        metric(
            "correct_block_resolved_only",
            "correct_block among resolved reviewed outcomes",
            correct_count,
            resolved_count,
            "Resolved-only descriptive rate; unresolved packets are explicitly excluded.",
        ),
        metric(
            "false_block_resolved_only",
            "false_block among resolved reviewed outcomes",
            false_block_count,
            resolved_count,
            "Resolved-only descriptive rate; unresolved packets are explicitly excluded.",
        ),
        metric(
            "identity_conflict_correct_block",
            "identity_conflict_masked packets labeled correct_block",
            sum(1 for row in identity_rows if row.get("reviewed_outcome") == "correct_block"),
            len(identity_rows),
            "Pattern-specific observation within the frozen set.",
        ),
        metric(
            "blocked_pdp_needs_more_evidence",
            "blocked_pdp packets that remained needs_more_evidence",
            sum(1 for row in blocked_pdp_rows if row.get("reviewed_outcome") == UNRESOLVED_OUTCOME),
            len(blocked_pdp_rows),
            "Evidence-boundary observation; blocked PDP is not outcome evidence by itself.",
        ),
        metric(
            "latest_pdp_temporal_false_block",
            "latest PDP temporal-authority packets labeled false_block",
            sum(1 for row in latest_temporal_rows if row.get("reviewed_outcome") == "false_block"),
            len(latest_temporal_rows),
            "Temporal-authority observation within the frozen set.",
        ),
    ]

    finding_cards = [
        {
            "finding_id": "F1_review_complete",
            "finding": f"{reviewed_count} of {freeze_summary.get('outcome_ready_p0_rows')} P0 outcome-ready packets were reviewed and frozen.",
            "evidence": "freeze_summary + frozen_rows",
            "claim_boundary": "Review completeness only.",
        },
        {
            "finding_id": "F2_outcome_distribution",
            "finding": (
                f"Outcome distribution: correct_block={correct_count}, false_block={false_block_count}, "
                f"needs_more_evidence={unresolved_count}."
            ),
            "evidence": "frozen_rows.reviewed_outcome",
            "claim_boundary": "Frozen-set descriptive distribution only.",
        },
        {
            "finding_id": "F3_resolved_vs_unresolved",
            "finding": f"{resolved_count} packets were resolved and {unresolved_count} remained evidence-insufficient.",
            "evidence": "resolved outcome taxonomy",
            "claim_boundary": "Unresolved cases are not coerced into binary success/failure.",
        },
        {
            "finding_id": "F4_identity_conflict",
            "finding": (
                f"{sum(1 for row in identity_rows if row.get('reviewed_outcome') == 'correct_block')} of "
                f"{len(identity_rows)} identity_conflict_masked packets were labeled correct_block."
            ),
            "evidence": "observed_change_type=identity_conflict_masked",
            "claim_boundary": "Pattern-specific observation, not universal identity-guard accuracy.",
        },
        {
            "finding_id": "F5_blocked_pdp_boundary",
            "finding": (
                f"{sum(1 for row in blocked_pdp_rows if row.get('reviewed_outcome') == UNRESOLVED_OUTCOME)} of "
                f"{len(blocked_pdp_rows)} blocked_pdp packets remained needs_more_evidence."
            ),
            "evidence": "operator_visual_verdict=blocked_pdp",
            "claim_boundary": "Blocked PDP supports evidence insufficiency, not correctness or falseness.",
        },
        {
            "finding_id": "F6_temporal_authority",
            "finding": (
                f"{sum(1 for row in latest_temporal_rows if row.get('reviewed_outcome') == 'false_block')} of "
                f"{len(latest_temporal_rows)} latest-PDP temporal-authority packets were labeled false_block."
            ),
            "evidence": "pdp_temporal_authority_evidence=latest_pdp_review_pool_snapshot_present",
            "claim_boundary": "Requires packet-visible temporal authority evidence.",
        },
    ]

    summary = {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_action_time_p0_empirical_finding_pack",
        "pack_schema_version": PACK_SCHEMA_VERSION,
        "status": "pass",
        "freeze_id": freeze_summary.get("freeze_id", ""),
        "freeze_hash_sha256": freeze_summary.get("freeze_hash_sha256", ""),
        "denominators": {
            "p0_rows": freeze_summary.get("p0_rows"),
            "outcome_ready_p0_rows": freeze_summary.get("outcome_ready_p0_rows"),
            "frozen_reviewed_rows": reviewed_count,
            "resolved_reviewed_rows": resolved_count,
            "insufficient_for_outcome_adjudication_p0_rows": freeze_summary.get(
                "insufficient_for_outcome_adjudication_p0_rows"
            ),
        },
        "outcome_counts": counter_dict(outcome_counts),
        "outcome_rates_all_reviewed": {
            key: pct(value, reviewed_count) for key, value in sorted(outcome_counts.items())
        },
        "outcome_rates_resolved_only": {
            "correct_block": pct(correct_count, resolved_count),
            "false_block": pct(false_block_count, resolved_count),
        },
        "metrics": metrics,
        "finding_cards": finding_cards,
        "profiles": {
            "outcome_by_observed_change_type": nested_counter_dict(outcome_by_change_type),
            "outcome_by_action_type": nested_counter_dict(outcome_by_action_type),
            "outcome_by_operator_visual_verdict": nested_counter_dict(outcome_by_operator),
            "outcome_by_pdp_temporal_authority_evidence": nested_counter_dict(outcome_by_temporal),
            "notes_by_outcome": nested_counter_dict(notes_by_outcome),
            "flag_profile_counts": counter_dict(flag_profiles),
        },
        "level4_missing": [
            "independent second reviewer and inter-rater agreement",
            "pre-declared random or stratified sampling frame beyond P0 reviewed packets",
            "workflow-family denominators and unresolved-case treatment",
            "holdout or later-period replication",
            "claim approval separating descriptive frozen-set rates from population probability",
        ],
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "internal_index_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "claim_boundary": {
            "allowed_claims": [
                "A completed masked P0 human-review outcome set was frozen.",
                "The frozen set has descriptive empirical outcome counts and rates.",
                "Pattern-level findings can be reported with explicit denominators.",
            ],
            "blocked_claims": [
                "These rates are population probabilities.",
                "The review proves general system accuracy.",
                "Unresolved needs_more_evidence rows are failures or successes.",
                "The pack mutates production truth or customer-facing output.",
            ],
        },
    }
    return metrics, summary


def build_report(summary: dict[str, Any]) -> str:
    lines = [
        "# LatentAtlas P0 Empirical Finding Pack",
        "",
        f"Generated at: `{summary['generated_at_utc']}`",
        f"Freeze id: `{summary['freeze_id']}`",
        f"Freeze hash: `{summary['freeze_hash_sha256']}`",
        "",
        "## Boundary",
        "",
        "This is a descriptive empirical finding pack over a frozen masked P0 human-review set. It is not a population probability claim and does not mutate production truth.",
        "",
        "## Denominators",
        "",
    ]
    if summary["status"] != "pass":
        lines.extend(["## Failure Reasons", ""])
        for reason in summary.get("failure_reasons", []):
            lines.append(f"- {reason}")
        lines.append("")
        return "\n".join(lines)
    for key, value in summary["denominators"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Outcome Distribution", ""])
    for outcome, count in summary["outcome_counts"].items():
        rate = summary["outcome_rates_all_reviewed"][outcome]
        lines.append(f"- `{outcome}`: `{count}` ({rate})")
    lines.extend(["", "## Metrics", ""])
    for row in summary["metrics"]:
        lines.append(
            f"- `{row['metric_id']}`: `{row['numerator']}/{row['denominator']}` "
            f"rate=`{row['rate']}`, Wilson95=`{row['wilson_95_low']}-{row['wilson_95_high']}`"
        )
    lines.extend(["", "## Finding Cards", ""])
    for card in summary["finding_cards"]:
        lines.extend(
            [
                f"### `{card['finding_id']}`",
                "",
                card["finding"],
                "",
                f"- evidence: `{card['evidence']}`",
                f"- boundary: {card['claim_boundary']}",
                "",
            ]
        )
    lines.extend(["## Level 4 Missing", ""])
    for item in summary["level4_missing"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Claim Boundary", "", "Allowed:"])
    for claim in summary["claim_boundary"]["allowed_claims"]:
        lines.append(f"- {claim}")
    lines.append("")
    lines.append("Blocked:")
    for claim in summary["claim_boundary"]["blocked_claims"]:
        lines.append(f"- {claim}")
    lines.append("")
    return "\n".join(lines)


def run(
    freeze_rows_path: Path = DEFAULT_FREEZE_ROWS,
    freeze_summary_path: Path = DEFAULT_FREEZE_SUMMARY,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "metrics": out_dir / "action_time_p0_empirical_metrics.csv",
        "summary": out_dir / "action_time_p0_empirical_finding_pack_summary.json",
        "manifest": out_dir / "action_time_p0_empirical_finding_pack_manifest.json",
        "report": out_dir / "action_time_p0_empirical_finding_pack_report.md",
    }
    missing = [str(path) for path in (freeze_rows_path, freeze_summary_path) if not path.exists()]
    if missing:
        manifest = {
            "generated_at_utc": utc_now(),
            "mode": "latentatlas_action_time_p0_empirical_finding_pack",
            "status": "blocked",
            "failure_reason": "missing_required_sources",
            "missing_sources": missing,
            "external_calls_used_by_builder": False,
            "production_truth_mutation": False,
            "internal_index_read": False,
        }
        write_json(paths["manifest"], manifest)
        return manifest

    metrics, summary = build_pack(read_csv(freeze_rows_path), read_json(freeze_summary_path))
    summary["input"] = {
        "freeze_rows": str(freeze_rows_path),
        "freeze_summary": str(freeze_summary_path),
    }
    summary["outputs"] = {key: str(value) for key, value in paths.items()}
    write_csv(paths["metrics"], metrics, METRIC_FIELDS)
    write_json(paths["summary"], summary)
    write_text(paths["report"], build_report(summary))
    manifest = {
        "generated_at_utc": summary["generated_at_utc"],
        "mode": summary["mode"],
        "pack_schema_version": summary.get("pack_schema_version", PACK_SCHEMA_VERSION),
        "status": summary["status"],
        "freeze_id": summary.get("freeze_id", ""),
        "freeze_hash_sha256": summary.get("freeze_hash_sha256", ""),
        "summary": str(paths["summary"]),
        "report": str(paths["report"]),
        "metrics": str(paths["metrics"]),
        "outcome_counts": summary.get("outcome_counts", {}),
        "denominators": summary.get("denominators", {}),
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "internal_index_read": False,
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
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
