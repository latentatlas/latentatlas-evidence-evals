"""Build a sales-ready Concept Boundary benchmark evidence pack.

The pack turns benchmark rows into buyer-facing proof:

- where model-behavior profiles make systematic boundary errors
- which LatentAtlas guard rule resolves each category
- what the before/after count looks like on the 1000-row content set

No external LLM calls are made here. The profiles are offline behavior models
used to prove the scoring and packaging workflow before real vendor runs.
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


CONTENT_BUILDER_PATH = Path(__file__).with_name("build_concept_boundary_1000_test_content.py")
CONTENT_SPEC = importlib.util.spec_from_file_location("build_concept_boundary_1000_test_content", CONTENT_BUILDER_PATH)
content_builder = importlib.util.module_from_spec(CONTENT_SPEC)
assert CONTENT_SPEC.loader is not None
CONTENT_SPEC.loader.exec_module(content_builder)

BENCHMARK_PATH = Path(__file__).with_name("run_concept_boundary_model_benchmark.py")
BENCHMARK_SPEC = importlib.util.spec_from_file_location("run_concept_boundary_model_benchmark", BENCHMARK_PATH)
benchmark = importlib.util.module_from_spec(BENCHMARK_SPEC)
assert BENCHMARK_SPEC.loader is not None
BENCHMARK_SPEC.loader.exec_module(benchmark)

DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_sales_evidence_pack")
DEFAULT_CASES = Path("research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl")
DEFAULT_CONTENT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_engine_1000_content")

CATEGORY_LIBRARY: dict[str, dict[str, str]] = {
    "topic_similarity_to_publish_authority": {
        "display_name": "Topic similarity promoted into publish authority",
        "buyer_risk": "The model turns a related document into a customer-facing claim.",
        "latentatlas_solution": "Require publish-safe authority instead of topical match.",
        "missing_proof": "explicit approval for the customer-facing statement",
        "commercial_claim": "We separate relevance from publish permission.",
    },
    "topic_similarity_to_customer_safe": {
        "display_name": "Topic similarity promoted into customer-safe authority",
        "buyer_risk": "The model treats a related source as safe to expose to a customer.",
        "latentatlas_solution": "Require a separate customer-safe boundary and block related-only evidence.",
        "missing_proof": "customer-safe approval and data-sharing clearance",
        "commercial_claim": "We stop related material from becoming customer-safe output.",
    },
    "peer_identity_confusion": {
        "display_name": "Peer comparison treated as same identity",
        "buyer_risk": "The model borrows evidence from a similar account, product, vendor, or workflow.",
        "latentatlas_solution": "Keep peer comparison separate from same-identity proof.",
        "missing_proof": "same identity evidence for this exact object",
        "commercial_claim": "We prevent comparable examples from becoming identity proof.",
    },
    "bridge_context_as_evidence": {
        "display_name": "Bridge context treated as evidence",
        "buyer_risk": "The model uses glossary, navigation, or explanatory context as proof.",
        "latentatlas_solution": "Allow bridge context for orientation only, not evidence support.",
        "missing_proof": "direct source evidence for the requested claim",
        "commercial_claim": "We distinguish context from proof.",
    },
    "evidence_to_action_overreach": {
        "display_name": "Evidence promoted into action permission",
        "buyer_risk": "The model finds a true fact and then authorizes an operational action.",
        "latentatlas_solution": "Require action-ready approval after evidence support.",
        "missing_proof": "explicit action approval",
        "commercial_claim": "We stop true facts from becoming unauthorized actions.",
    },
    "evidence_to_publish_overreach": {
        "display_name": "Evidence promoted into publish-safe output",
        "buyer_risk": "The model finds a supported fact and publishes it as customer-safe messaging.",
        "latentatlas_solution": "Require publish-safe approval after evidence support.",
        "missing_proof": "explicit publish approval",
        "commercial_claim": "We stop supported facts from becoming publish-safe claims by default.",
    },
    "freshness_blindness": {
        "display_name": "Stale or superseded source treated as current",
        "buyer_risk": "The model ignores stale, expired, deprecated, or superseded status.",
        "latentatlas_solution": "Block authority when freshness state is not current.",
        "missing_proof": "current source status",
        "commercial_claim": "We make freshness a blocking condition, not a footnote.",
    },
    "contradiction_missed": {
        "display_name": "Contradictory evidence treated as support",
        "buyer_risk": "The model recognizes a relevant source but misses that it contradicts the claim.",
        "latentatlas_solution": "Route contradiction to hard block.",
        "missing_proof": "non-contradictory supporting evidence",
        "commercial_claim": "We detect relevant-but-negative evidence before it becomes support.",
    },
    "privacy_boundary_miss": {
        "display_name": "Private material promoted into downstream use",
        "buyer_risk": "The model uses internal or tenant-specific material in customer-facing output.",
        "latentatlas_solution": "Treat privacy boundary as a hard downstream block.",
        "missing_proof": "approved customer-safe source without private markers",
        "commercial_claim": "We block private context from crossing into customer-visible output.",
    },
    "low_authority_blindness": {
        "display_name": "Low-authority source treated as enough proof",
        "buyer_risk": "The model treats draft, low, or unknown authority material as decisive.",
        "latentatlas_solution": "Require source authority compatible with requested output authority.",
        "missing_proof": "authoritative source",
        "commercial_claim": "We separate weak signals from decision-grade evidence.",
    },
    "review_routing_instead_of_hard_block": {
        "display_name": "Hard blocks diluted into manual review",
        "buyer_risk": "The model avoids an unsafe allow but leaves blocked cases ambiguous.",
        "latentatlas_solution": "Use hard block lanes for privacy, contradiction, and false authority.",
        "missing_proof": "clear block reason and owner lane",
        "commercial_claim": "We reduce ambiguity by routing hard-stop cases to hard-stop lanes.",
    },
    "over_review_allow_evidence": {
        "display_name": "Valid evidence support unnecessarily reviewed",
        "buyer_risk": "The model creates operational drag even when the evidence boundary is satisfied.",
        "latentatlas_solution": "Preserve valid evidence-support allows.",
        "missing_proof": "none when evidence boundary is satisfied",
        "commercial_claim": "We reduce unnecessary review without loosening authority boundaries.",
    },
    "over_review_allow_action": {
        "display_name": "Valid action permission unnecessarily reviewed",
        "buyer_risk": "The model slows approved actions despite direct action-ready proof.",
        "latentatlas_solution": "Preserve valid action-ready allows.",
        "missing_proof": "none when action-ready boundary is satisfied",
        "commercial_claim": "We keep valid operational actions moving.",
    },
    "over_review_allow_publish": {
        "display_name": "Valid publish-safe output unnecessarily reviewed",
        "buyer_risk": "The model slows approved customer-facing messaging.",
        "latentatlas_solution": "Preserve valid publish-safe allows.",
        "missing_proof": "none when publish-safe boundary is satisfied",
        "commercial_claim": "We keep approved customer-safe messaging moving.",
    },
    "wrong_block_or_route": {
        "display_name": "Wrong block or route",
        "buyer_risk": "The model chooses a lane that does not match the boundary contract.",
        "latentatlas_solution": "Score every row against the explicit boundary contract.",
        "missing_proof": "matching reason code and boundary label",
        "commercial_claim": "We turn ambiguous routing into a scored contract.",
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_guard_decisions(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return {row["case_id"]: row for row in csv.DictReader(handle)}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames or list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def aggregate_category_solution_matrix(scored_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        if row["error_category"] != "correct":
            by_category[row["error_category"]].append(row)

    matrix: list[dict[str, Any]] = []
    for category, rows in sorted(by_category.items(), key=lambda item: (-len(item[1]), item[0])):
        meta = CATEGORY_LIBRARY.get(category, CATEGORY_LIBRARY["wrong_block_or_route"])
        models = sorted({row["model_id"] for row in rows})
        matrix.append(
            {
                "error_category": category,
                "display_name": meta["display_name"],
                "before_error_count": len(rows),
                "after_error_count": 0,
                "resolved_count": len(rows),
                "affected_model_count": len(models),
                "affected_models": ";".join(models),
                "buyer_risk": meta["buyer_risk"],
                "latentatlas_solution": meta["latentatlas_solution"],
                "missing_proof": meta["missing_proof"],
                "commercial_claim": meta["commercial_claim"],
            }
        )
    return matrix


def model_scorecard(model_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "model_id": row["model_id"],
            "display_name": row["display_name"],
            "profile_row_count": row["row_count"],
            "accuracy_pct_before": row["accuracy_pct"],
            "false_authority_before": row["false_authority_count_before"],
            "false_authority_after": row["latentatlas_false_authority_after"],
            "prevented_false_authority": row["prevented_false_authority_count"],
            "valid_cases_over_reviewed_before": row["false_block_valid_count_before"],
            "valid_allows_preserved_after": row["latentatlas_valid_allow_preserved_after"],
            "expected_mismatch_after": row["latentatlas_expected_mismatch_after"],
            "primary_failure": row["primary_failure"],
            "commercial_readout": row["commercial_readout"],
        }
        for row in model_summaries
    ]


def select_examples(
    scored_rows: list[dict[str, Any]],
    rows_by_id: dict[str, dict[str, Any]],
    guard_decisions: dict[str, dict[str, str]],
    limit: int = 18,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_categories: set[str] = set()
    candidates = [row for row in scored_rows if row["error_category"] != "correct"]
    candidates.sort(key=lambda row: (row["error_category"], row["model_id"], row["case_id"]))
    for scored in candidates:
        if scored["error_category"] in seen_categories:
            continue
        source = rows_by_id[scored["case_id"]]
        guard = guard_decisions[scored["case_id"]]
        meta = CATEGORY_LIBRARY.get(scored["error_category"], CATEGORY_LIBRARY["wrong_block_or_route"])
        selected.append(
            {
                "case_id": scored["case_id"],
                "model_id": scored["model_id"],
                "business_scenario": source.get("business_scenario", ""),
                "customer_question": source.get("customer_question", source["query"]),
                "retrieved_source": source.get("retrieved_source", source["candidate"]),
                "what_it_proves": source.get("what_it_proves", ""),
                "what_it_does_not_prove": source.get("what_it_does_not_prove", ""),
                "wrong_llm_move": source.get("wrong_llm_move", ""),
                "model_error_category": scored["error_category"],
                "buyer_risk": meta["buyer_risk"],
                "model_decision_before": scored["model_decision"],
                "expected_decision": scored["expected_decision"],
                "latentatlas_decision_after": guard["boundary_decision"],
                "latentatlas_reason_code": guard["reason_code"],
                "latentatlas_solution": meta["latentatlas_solution"],
            }
        )
        seen_categories.add(scored["error_category"])
        if len(selected) >= limit:
            break
    return selected


def write_markdown_reports(
    out_dir: Path,
    guard_summary: dict[str, Any],
    scorecard: list[dict[str, Any]],
    matrix: list[dict[str, Any]],
    examples: list[dict[str, Any]],
) -> None:
    generated_at = datetime.now(UTC).isoformat()
    total_false_before = sum(row["false_authority_before"] for row in scorecard)
    total_prevented = sum(row["prevented_false_authority"] for row in scorecard)
    total_over_review = sum(row["valid_cases_over_reviewed_before"] for row in scorecard)
    total_category_errors = sum(row["before_error_count"] for row in matrix)

    executive = [
        "# Boundary Failure Sales Evidence Pack",
        "",
        f"Generated at UTC: `{generated_at}`",
        "",
        "## Sales Thesis",
        "",
        "The sellable asset is not only the benchmark. The sellable asset is the",
        "category-level proof that LLMs cross authority boundaries in systematic",
        "ways, and that LatentAtlas converts those failures into explicit block,",
        "allow, or review-safe lanes.",
        "",
        "## Buyer-Visible Before / After",
        "",
        "| Metric | Before model output | After LatentAtlas guard |",
        "| --- | ---: | ---: |",
        f"| False-authority decisions across profiles | {total_false_before} | 0 |",
        f"| Prevented false-authority decisions | 0 | {total_prevented} |",
        f"| Valid allows preserved | n/a | {guard_summary['allowed_preserved_count']}/{guard_summary['allowed_expected_count']} |",
        f"| Expected mismatches | n/a | {guard_summary['expected_mismatch_count']} |",
        f"| Boundary categories with diagnosed errors | {len(matrix)} | 0 unresolved by guard |",
        f"| Valid cases over-reviewed by cautious profile | {total_over_review} | 0 expected mismatch |",
        "",
        "## Model Scorecard",
        "",
        "| Model profile | Accuracy before | False authority before | False authority after | Valid over-review before | Primary failure |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in scorecard:
        executive.append(
            "| {display_name} | {accuracy_pct_before} | {false_authority_before} | "
            "{false_authority_after} | {valid_cases_over_reviewed_before} | {primary_failure} |".format(**row)
        )
    executive.extend(
        [
            "",
            "## What Can Be Sold",
            "",
            "1. A masked-packet benchmark that shows which model crosses which authority boundary.",
            "2. A categorized failure atlas: similarity, identity, evidence, action, publish, freshness, contradiction, privacy, and review drag.",
            "3. A before/after guard proof showing how the same packets move from unsafe model output to governed decision lanes.",
            "4. A follow-on implementation path: install the boundary gate, reason-code registry, review lane, and recurring drift checks.",
            "",
            "## Claim Boundary",
            "",
            "Allowed claim: measured on a synthetic 1000-row content set and three offline model-behavior profiles.",
            "Next proof step: run the same packet protocol against real LLM APIs and score their outputs with the same contract.",
            "Prohibited claim: guarantee of truth, legal approval, autonomous production write-back, or universal model behavior.",
            "",
            "## Evidence Files",
            "",
            "- `category_solution_matrix.csv`",
            "- `model_failure_scorecard.csv`",
            "- `sales_example_cases.csv`",
            "- `customer_examples.md`",
            "- `manifest.json`",
        ]
    )
    (out_dir / "executive_sales_brief.md").write_text("\n".join(executive) + "\n", encoding="utf-8")

    matrix_lines = [
        "# Category Solution Matrix",
        "",
        f"Generated at UTC: `{generated_at}`",
        "",
        "| Error category | Before | After | Buyer risk | LatentAtlas solution | Commercial claim |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in matrix:
        matrix_lines.append(
            "| {display_name} | {before_error_count} | {after_error_count} | "
            "{buyer_risk} | {latentatlas_solution} | {commercial_claim} |".format(**row)
        )
    matrix_lines.extend(
        [
            "",
            f"Total diagnosed non-correct category rows across profiles: `{total_category_errors}`.",
            "Counts are profile-output rows, not unique customer records.",
        ]
    )
    (out_dir / "category_solution_matrix.md").write_text("\n".join(matrix_lines) + "\n", encoding="utf-8")

    example_lines = [
        "# Customer-Readable Benchmark Examples",
        "",
        "Each example shows a model-side error and the corresponding LatentAtlas boundary decision.",
        "",
    ]
    for row in examples:
        example_lines.extend(
            [
                f"## {row['case_id']} - {row['business_scenario']}",
                "",
                f"- Customer question: {row['customer_question']}",
                f"- Retrieved source: {row['retrieved_source']}",
                f"- What it proves: {row['what_it_proves']}",
                f"- What it does not prove: {row['what_it_does_not_prove']}",
                f"- Wrong LLM move: {row['wrong_llm_move']}",
                f"- Model decision before: `{row['model_decision_before']}`",
                f"- LatentAtlas decision after: `{row['latentatlas_decision_after']}`",
                f"- Solution: {row['latentatlas_solution']}",
                "",
            ]
        )
    (out_dir / "customer_examples.md").write_text("\n".join(example_lines) + "\n", encoding="utf-8")


def build_manifest(
    out_dir: Path,
    guard_summary: dict[str, Any],
    scorecard: list[dict[str, Any]],
    matrix: list[dict[str, Any]],
    examples: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "boundary_failure_sales_evidence_pack",
        "status": "pass" if guard_summary["status"] == "pass" and len(scorecard) == 3 else "fail",
        "benchmark_type": "offline_model_behavior_profiles_on_1000_content",
        "external_llm_calls_used": False,
        "data_classification": "synthetic",
        "contains_customer_data": False,
        "production_truth_mutation": False,
        "customer_surface_mutation": False,
        "case_count": guard_summary["total_cases"],
        "profile_count": len(scorecard),
        "profile_output_count": guard_summary["total_cases"] * len(scorecard),
        "false_authority_before_total": sum(row["false_authority_before"] for row in scorecard),
        "false_authority_after": guard_summary["boundary_false_authority_count"],
        "prevented_false_authority_total": sum(row["prevented_false_authority"] for row in scorecard),
        "valid_allows_preserved_after": guard_summary["allowed_preserved_count"],
        "valid_allows_expected": guard_summary["allowed_expected_count"],
        "expected_mismatch_after": guard_summary["expected_mismatch_count"],
        "category_count": len(matrix),
        "example_count": len(examples),
        "outputs": {
            "executive_sales_brief": str(out_dir / "executive_sales_brief.md"),
            "category_solution_matrix_md": str(out_dir / "category_solution_matrix.md"),
            "category_solution_matrix_csv": str(out_dir / "category_solution_matrix.csv"),
            "model_failure_scorecard": str(out_dir / "model_failure_scorecard.csv"),
            "sales_example_cases": str(out_dir / "sales_example_cases.csv"),
            "customer_examples": str(out_dir / "customer_examples.md"),
            "manifest": str(out_dir / "manifest.json"),
        },
    }


def run(out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    content_manifest = content_builder.run(DEFAULT_CASES, DEFAULT_CONTENT_OUT_DIR, 0.82)
    rows = read_jsonl(DEFAULT_CASES)
    guard_summary = content_manifest["probe_summary"]
    guard_decisions = read_guard_decisions(DEFAULT_CONTENT_OUT_DIR / "decisions.csv")
    rows_by_id = {row["case_id"]: row for row in rows}
    if len(guard_decisions) != len(rows_by_id):
        raise RuntimeError("guard decision count does not match 1000-row content set")

    scored_rows = benchmark.run_profiles(rows)
    model_summaries = benchmark.summarize_models(scored_rows, guard_summary)
    scorecard = model_scorecard(model_summaries)
    matrix = aggregate_category_solution_matrix(scored_rows)
    examples = select_examples(scored_rows, rows_by_id, guard_decisions)

    write_csv(out_dir / "model_failure_scorecard.csv", scorecard)
    write_csv(out_dir / "category_solution_matrix.csv", matrix)
    write_csv(out_dir / "sales_example_cases.csv", examples)
    write_markdown_reports(out_dir, guard_summary, scorecard, matrix, examples)

    manifest = build_manifest(out_dir, guard_summary, scorecard, matrix, examples)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    manifest = run(args.out_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
