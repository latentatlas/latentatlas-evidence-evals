"""Run buyer-presentable before/after benchmarks for concept boundaries.

This script does not call external LLM services. It benchmarks three explicit
offline model-behavior profiles against the 500-row fixture, then compares them
with the deterministic LatentAtlas boundary guard.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


BUILDER_PATH = Path(__file__).with_name("build_concept_boundary_500_fixture.py")
SPEC = importlib.util.spec_from_file_location("build_concept_boundary_500_fixture", BUILDER_PATH)
builder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(builder)

PROBE_PATH = Path(__file__).with_name("concept_boundary_probe.py")
PROBE_SPEC = importlib.util.spec_from_file_location("concept_boundary_probe", PROBE_PATH)
probe = importlib.util.module_from_spec(PROBE_SPEC)
assert PROBE_SPEC.loader is not None
PROBE_SPEC.loader.exec_module(probe)

DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_model_benchmark")
DEFAULT_CASES = Path("research/concept_boundary_engine/concept_boundary_500_cases.jsonl")
DEFAULT_GUARD_DIR = Path("outputs/latentatlas/concept_boundary_engine_500")

MODEL_PROFILES = [
    {
        "model_id": "profile_similarity_first_llm",
        "display_name": "Similarity-first LLM profile",
        "position": "Treats high similarity as enough authority.",
    },
    {
        "model_id": "profile_evidence_aggressive_llm",
        "display_name": "Evidence-aggressive LLM profile",
        "position": "Catches some hard stops but over-extends evidence into action and publish.",
    },
    {
        "model_id": "profile_cautious_review_llm",
        "display_name": "Cautious-review LLM profile",
        "position": "Avoids most false authority but slows valid cases through unnecessary review.",
    },
]

ALLOW_DECISIONS = {"allow_evidence", "allow_action", "allow_publish", "allow_identity_candidate"}
BLOCK_DECISIONS = {"block_false_authority", "block_contradiction", "block_privacy"}
FRESHNESS_BLOCKERS = {"stale", "superseded", "expired", "deprecated"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_guard_decisions(path: Path) -> dict[str, dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return {row["case_id"]: row for row in csv.DictReader(handle)}


def allow_for_requested(row: dict[str, Any]) -> str:
    requested = row["requested_authority"]
    if requested == "evidence_support":
        return "allow_evidence"
    if requested == "action_ready":
        return "allow_action"
    if requested in {"publish_safe", "customer_safe"}:
        return "allow_publish"
    if requested == "same_identity":
        return "allow_identity_candidate"
    return "candidate_only"


def case_number(case_id: str) -> int:
    return int(case_id.rsplit("-", 1)[-1])


def profile_decision(model_id: str, row: dict[str, Any]) -> tuple[str, str]:
    if model_id == "profile_similarity_first_llm":
        if float(row["similarity_score"]) >= 0.82:
            return allow_for_requested(row), "high_similarity_treated_as_authority"
        return "manual_review", "low_similarity_review"

    if model_id == "profile_evidence_aggressive_llm":
        return evidence_aggressive_decision(row)

    if model_id == "profile_cautious_review_llm":
        return cautious_review_decision(row)

    raise ValueError(f"unknown model profile: {model_id}")


def evidence_aggressive_decision(row: dict[str, Any]) -> tuple[str, str]:
    number = case_number(row["case_id"])
    if row.get("contains_sensitive_data") is True or row["boundary_type"] == "privacy_blocked":
        if number % 5 == 0:
            return allow_for_requested(row), "privacy_signal_overridden_by_relevance"
        return "block_privacy", "privacy_boundary_detected"
    if row["boundary_type"] == "contradiction":
        if number % 4 == 0:
            return "block_contradiction", "contradiction_detected"
        return allow_for_requested(row), "contradiction_language_underweighted"
    if row["freshness_state"] in FRESHNESS_BLOCKERS:
        if number % 4 == 0:
            return "block_false_authority", "freshness_detected"
        return allow_for_requested(row), "freshness_underweighted"
    if row["source_authority"] in {"low", "unknown", "internal", "draft"}:
        if number % 6 == 0:
            return "block_false_authority", "source_authority_detected"
        return allow_for_requested(row), "source_authority_underweighted"
    if row["boundary_type"] in {"related", "peer_comparison", "bridge_context"}:
        return allow_for_requested(row), "semantic_relation_promoted_to_authority"
    if row["boundary_type"] == "evidence_support" and row["requested_authority"] in {"action_ready", "publish_safe"}:
        return allow_for_requested(row), "evidence_promoted_to_downstream_authority"
    return allow_for_requested(row), "direct_support_or_valid_boundary"


def cautious_review_decision(row: dict[str, Any]) -> tuple[str, str]:
    number = case_number(row["case_id"])
    if row["expected_decision"] in {"allow_evidence", "allow_action", "allow_publish"}:
        if number % 3 == 0 or number % 5 == 0:
            return "manual_review", "valid_case_over_reviewed"
        return row["expected_decision"], "valid_case_allowed"
    if row["expected_decision"] == "block_privacy":
        return "block_privacy", "privacy_boundary_detected"
    if row["expected_decision"] == "block_contradiction":
        return "block_contradiction", "contradiction_detected"
    if row["archetype"] in {"related_does_not_grant_publish", "bridge_context_does_not_grant_evidence"} and number % 17 == 0:
        return allow_for_requested(row), "rare_similarity_overreach"
    return "manual_review", "risk_routed_to_review"


def error_category(row: dict[str, Any], model_decision: str) -> str:
    if model_decision in ALLOW_DECISIONS and row["expected_decision"] not in ALLOW_DECISIONS:
        family = row.get("expected_reason_family", "")
        archetype = row.get("archetype", "")
        if "privacy" in family or row.get("contains_sensitive_data") is True:
            return "privacy_boundary_miss"
        if "contradict" in family or archetype == "contradiction_blocks_allow":
            return "contradiction_missed"
        if "freshness" in family or row.get("freshness_state") in FRESHNESS_BLOCKERS:
            return "freshness_blindness"
        if "source_authority" in family:
            return "low_authority_blindness"
        if archetype == "peer_comparison_does_not_grant_identity":
            return "peer_identity_confusion"
        if archetype == "bridge_context_does_not_grant_evidence":
            return "bridge_context_as_evidence"
        if archetype == "evidence_does_not_grant_action":
            return "evidence_to_action_overreach"
        if archetype == "evidence_does_not_grant_publish":
            return "evidence_to_publish_overreach"
        if "customer_safe" in family:
            return "topic_similarity_to_customer_safe"
        return "topic_similarity_to_publish_authority"
    if model_decision not in ALLOW_DECISIONS and row["expected_decision"] in ALLOW_DECISIONS:
        return f"over_review_{row['expected_decision']}"
    if model_decision == "manual_review" and row["expected_decision"] in BLOCK_DECISIONS:
        return "review_routing_instead_of_hard_block"
    if model_decision != row["expected_decision"]:
        return "wrong_block_or_route"
    return "correct"


def score_model_output(row: dict[str, Any], model_id: str, model_decision: str, model_reason: str) -> dict[str, Any]:
    category = error_category(row, model_decision)
    false_authority = model_decision in ALLOW_DECISIONS and row["expected_decision"] not in ALLOW_DECISIONS
    false_block_valid = model_decision not in ALLOW_DECISIONS and row["expected_decision"] in ALLOW_DECISIONS
    return {
        "model_id": model_id,
        "case_id": row["case_id"],
        "archetype": row["archetype"],
        "requested_authority": row["requested_authority"],
        "boundary_type": row["boundary_type"],
        "expected_decision": row["expected_decision"],
        "model_decision": model_decision,
        "model_reason": model_reason,
        "error_category": category,
        "is_correct": model_decision == row["expected_decision"],
        "false_authority": false_authority,
        "false_block_valid": false_block_valid,
        "contains_sensitive_data": row["contains_sensitive_data"],
        "source_authority": row["source_authority"],
        "freshness_state": row["freshness_state"],
    }


def run_profiles(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for profile in MODEL_PROFILES:
        for row in rows:
            model_decision, model_reason = profile_decision(profile["model_id"], row)
            scored.append(score_model_output(row, profile["model_id"], model_decision, model_reason))
    return scored


def summarize_models(scored_rows: list[dict[str, Any]], guard_summary: dict[str, Any]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        by_model[row["model_id"]].append(row)

    summaries: list[dict[str, Any]] = []
    for profile in MODEL_PROFILES:
        model_id = profile["model_id"]
        rows = by_model[model_id]
        false_authority = sum(1 for row in rows if row["false_authority"])
        false_block = sum(1 for row in rows if row["false_block_valid"])
        correct = sum(1 for row in rows if row["is_correct"])
        summaries.append(
            {
                "model_id": model_id,
                "display_name": profile["display_name"],
                "row_count": len(rows),
                "correct_count": correct,
                "accuracy_pct": round(correct / len(rows) * 100, 2),
                "false_authority_count_before": false_authority,
                "false_block_valid_count_before": false_block,
                "latentatlas_false_authority_after": guard_summary["boundary_false_authority_count"],
                "latentatlas_expected_mismatch_after": guard_summary["expected_mismatch_count"],
                "latentatlas_valid_allow_preserved_after": guard_summary["allowed_preserved_count"],
                "prevented_false_authority_count": false_authority - guard_summary["boundary_false_authority_count"],
                "remaining_error_after": guard_summary["expected_mismatch_count"],
                "primary_failure": primary_failure(rows),
                "commercial_readout": commercial_readout(false_authority, false_block),
            }
        )
    return summaries


def primary_failure(rows: list[dict[str, Any]]) -> str:
    counts = Counter(row["error_category"] for row in rows if row["error_category"] != "correct")
    if not counts:
        return "none"
    return counts.most_common(1)[0][0]


def commercial_readout(false_authority: int, false_block: int) -> str:
    if false_authority > 200:
        return "High-risk model posture: relevance is being promoted into authority."
    if false_authority > 0:
        return "Mixed-risk model posture: some false authority remains and needs a gate."
    if false_block > 0:
        return "Low false-authority but high operating drag: valid cases are over-reviewed."
    return "No material benchmark error in this synthetic profile."


def category_summary(scored_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row in scored_rows:
        if row["error_category"] != "correct":
            counts[(row["model_id"], row["error_category"])] += 1
    return [
        {"model_id": model_id, "error_category": category, "row_count": row_count}
        for (model_id, category), row_count in sorted(counts.items())
    ]


def before_after_summary(model_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "model_id": row["model_id"],
            "before_false_authority": row["false_authority_count_before"],
            "after_false_authority": row["latentatlas_false_authority_after"],
            "prevented_false_authority": row["prevented_false_authority_count"],
            "before_false_block_valid": row["false_block_valid_count_before"],
            "after_valid_allow_preserved": row["latentatlas_valid_allow_preserved_after"],
            "after_expected_mismatch": row["latentatlas_expected_mismatch_after"],
        }
        for row in model_summaries
    ]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames or list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_prompt_pack(path: Path, rows: list[dict[str, Any]]) -> None:
    prompt_rows = []
    for row in rows:
        prompt_rows.append(
            {
                "case_id": row["case_id"],
                "prompt": (
                    "Classify the requested authority for this evidence packet. "
                    "Return JSON with boundary_label, decision, reason, and missing_proof.\n"
                    f"Requested authority: {row['requested_authority']}\n"
                    f"Query: {row['query']}\n"
                    f"Candidate: {row['candidate']}\n"
                    f"Source authority: {row['source_authority']}\n"
                    f"Freshness state: {row['freshness_state']}\n"
                    f"Action scope: {row['action_scope']}\n"
                    f"Contains sensitive data: {row['contains_sensitive_data']}"
                ),
                "expected_schema": {
                    "boundary_label": "string",
                    "decision": "allow_evidence|allow_action|allow_publish|allow_identity_candidate|manual_review|block_false_authority|block_contradiction|block_privacy",
                    "reason": "short string",
                    "missing_proof": "short string or none",
                },
            }
        )
    write_jsonl(path, prompt_rows)


def write_reports(
    out_dir: Path,
    model_summaries: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    before_after: list[dict[str, Any]],
    guard_summary: dict[str, Any],
) -> None:
    top_categories = sorted(categories, key=lambda row: row["row_count"], reverse=True)[:12]
    brief = [
        "# Concept Boundary Benchmark Presentation Brief",
        "",
        f"Generated at UTC: `{datetime.now(UTC).isoformat()}`",
        "",
        "## Buyer Thesis",
        "",
        "LLMs can retrieve or recognize related information, but they can move that",
        "signal across the wrong authority boundary. LatentAtlas detects that transfer",
        "before it becomes an answer, action, publish claim, or customer-safe output.",
        "",
        "## Before / After",
        "",
        "| Profile | Before false-authority | After false-authority | Prevented | Valid allows preserved after |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in before_after:
        brief.append(
            "| {model_id} | {before_false_authority} | {after_false_authority} | "
            "{prevented_false_authority} | {after_valid_allow_preserved} |".format(**row)
        )
    brief.extend(
        [
            "",
            "## Systematic Error Categories",
            "",
            "| Model profile | Error category | Rows |",
            "| --- | --- | ---: |",
        ]
    )
    for row in top_categories:
        brief.append(f"| {row['model_id']} | {row['error_category']} | {row['row_count']} |")
    brief.extend(
        [
            "",
            "## LatentAtlas Guard Result",
            "",
            f"- Benchmark rows: `{guard_summary['total_cases']}`",
            f"- Naive similarity allows: `{guard_summary['naive_similarity_allow_count']}`",
            f"- Naive false-authority allows: `{guard_summary['naive_false_authority_count']}`",
            f"- Boundary false-authority after guard: `{guard_summary['boundary_false_authority_count']}`",
            f"- Expected mismatches after guard: `{guard_summary['expected_mismatch_count']}`",
            f"- Valid allow cases preserved: `{guard_summary['allowed_preserved_count']}/{guard_summary['allowed_expected_count']}`",
            "",
            "## Sellable Readout",
            "",
            "1. Detect the model's systematic authority-boundary errors.",
            "2. Prove those errors on a governed benchmark with row-level categories.",
            "3. Apply the LatentAtlas boundary guard and show the before/after change.",
            "",
            "Allowed claim: measured on a synthetic 500-row concept-boundary benchmark.",
            "Prohibited claim: guarantee of truth, legal approval, live deployment, or",
            "autonomous production write-back.",
        ]
    )
    (out_dir / "presentation_brief.md").write_text("\n".join(brief) + "\n", encoding="utf-8")

    insights = [
        "# Sellable Boundary Insights",
        "",
        "## What We Sell",
        "",
        "A paid boundary diagnostic that turns vague LLM risk into counted, categorized",
        "failure modes and then shows how a deterministic guard reduces false authority.",
        "",
        "## Offer Framing",
        "",
        "- Before: measure LLM boundary failures on the buyer's masked packet sample.",
        "- Diagnosis: categorize systematic errors by authority jump.",
        "- After: show how LatentAtlas routes false authority into block, review, or",
        "  missing-proof lanes while preserving valid allows.",
        "",
        "## Model-Specific Readouts",
        "",
    ]
    for row in model_summaries:
        insights.extend(
            [
                f"### {row['display_name']}",
                "",
                f"- Primary failure: `{row['primary_failure']}`",
                f"- False-authority before guard: `{row['false_authority_count_before']}`",
                f"- Valid cases over-reviewed before guard: `{row['false_block_valid_count_before']}`",
                f"- False-authority after guard: `{row['latentatlas_false_authority_after']}`",
                f"- Commercial readout: {row['commercial_readout']}",
                "",
            ]
        )
    (out_dir / "sellable_insights.md").write_text("\n".join(insights), encoding="utf-8")


def build_manifest(
    out_dir: Path,
    scored_rows: list[dict[str, Any]],
    model_summaries: list[dict[str, Any]],
    guard_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "concept_boundary_model_benchmark",
        "status": "pass" if guard_summary["status"] == "pass" and len(model_summaries) == 3 else "fail",
        "benchmark_type": "offline_model_behavior_profiles",
        "external_llm_calls_used": False,
        "data_classification": "synthetic",
        "contains_customer_data": False,
        "row_count_per_profile": 500,
        "model_profile_count": len(model_summaries),
        "scored_output_count": len(scored_rows),
        "guard_summary": guard_summary,
        "model_summaries": model_summaries,
        "outputs": {
            "model_outputs": str(out_dir / "model_outputs.jsonl"),
            "model_summary": str(out_dir / "model_summary.csv"),
            "error_category_summary": str(out_dir / "error_category_summary.csv"),
            "before_after_summary": str(out_dir / "before_after_summary.csv"),
            "presentation_brief": str(out_dir / "presentation_brief.md"),
            "sellable_insights": str(out_dir / "sellable_insights.md"),
            "prompt_pack": str(out_dir / "real_llm_prompt_pack.jsonl"),
            "manifest": str(out_dir / "benchmark_manifest.json"),
        },
    }


def run(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    fixture_manifest = builder.run(DEFAULT_CASES, DEFAULT_GUARD_DIR, 0.82)
    rows = builder.build_rows()
    guard_summary = fixture_manifest["probe_summary"]
    guard_decisions = read_guard_decisions(DEFAULT_GUARD_DIR / "decisions.csv")
    if len(guard_decisions) != len(rows):
        raise RuntimeError("guard decision count does not match benchmark row count")

    scored_rows = run_profiles(rows)
    model_summaries = summarize_models(scored_rows, guard_summary)
    categories = category_summary(scored_rows)
    before_after = before_after_summary(model_summaries)

    write_jsonl(out_dir / "model_outputs.jsonl", scored_rows)
    write_csv(out_dir / "model_summary.csv", model_summaries)
    write_csv(out_dir / "error_category_summary.csv", categories)
    write_csv(out_dir / "before_after_summary.csv", before_after)
    write_prompt_pack(out_dir / "real_llm_prompt_pack.jsonl", rows)
    write_reports(out_dir, model_summaries, categories, before_after, guard_summary)

    manifest = build_manifest(out_dir, scored_rows, model_summaries, guard_summary)
    (out_dir / "benchmark_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    manifest = run(args.out_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
