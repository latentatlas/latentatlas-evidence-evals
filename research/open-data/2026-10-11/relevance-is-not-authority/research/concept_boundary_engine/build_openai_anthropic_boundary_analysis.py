"""Build a detailed OpenAI vs Anthropic Concept Boundary analysis pack.

This is a local-only reporting layer. It consumes already-scored benchmark
outputs, joins them with the synthetic cases and deterministic guard decisions,
then writes the slices needed for sales and research review.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_SCORED = Path("outputs/latentatlas/concept_boundary_real_llm_scores_1000_full/scored_outputs.csv")
DEFAULT_CASES = Path("research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl")
DEFAULT_GUARD_DECISIONS = Path("outputs/latentatlas/concept_boundary_engine_1000_content/decisions.csv")
DEFAULT_RAW_OUTPUTS = Path("outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs_cleaned.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_openai_anthropic_analysis")
DEFAULT_MODELS = ("openai:gpt-5.5", "anthropic:claude-opus-4-7")
ALLOW_DECISIONS = {"allow_evidence", "allow_action", "allow_publish", "allow_identity_candidate"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames or list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def truthy(value: Any) -> bool:
    return value in {True, "True", "true", "1", 1}


def pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator * 100, 2) if denominator else 0.0


def output_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row["model_id"]), str(row["case_id"]))


def primary_failure(rows: list[dict[str, Any]]) -> str:
    counts = Counter(row["error_category"] for row in rows if row["error_category"] != "correct")
    if not counts:
        return "none"
    return counts.most_common(1)[0][0]


def parse_stats(rows: list[dict[str, Any]], raw_by_key: dict[tuple[str, str], dict[str, Any]]) -> tuple[int, int]:
    known = 0
    failed = 0
    for row in rows:
        raw = raw_by_key.get((row["model_id"], row["case_id"]))
        if raw and "parse_ok" in raw:
            known += 1
            if not truthy(raw["parse_ok"]):
                failed += 1
    return known, failed


def model_scorecard(
    scored_rows: list[dict[str, Any]],
    guard_by_case: dict[str, dict[str, str]],
    raw_by_key: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        by_model[row["model_id"]].append(row)

    cards: list[dict[str, Any]] = []
    for model_id, rows in sorted(by_model.items()):
        correct = sum(1 for row in rows if truthy(row["is_correct"]))
        false_authority = sum(1 for row in rows if truthy(row["false_authority"]))
        false_block = sum(1 for row in rows if truthy(row["false_block_valid"]))
        valid_expected = sum(1 for row in rows if row["expected_decision"] in ALLOW_DECISIONS)
        parse_known, parse_failed = parse_stats(rows, raw_by_key)
        guard_false_authority = 0
        guard_mismatch = 0
        guard_valid_preserved = 0
        for row in rows:
            guard = guard_by_case.get(row["case_id"], {})
            guard_decision = guard.get("boundary_decision", "")
            if guard_decision in ALLOW_DECISIONS and row["expected_decision"] not in ALLOW_DECISIONS:
                guard_false_authority += 1
            if guard_decision != row["expected_decision"]:
                guard_mismatch += 1
            if row["expected_decision"] in ALLOW_DECISIONS and guard_decision == row["expected_decision"]:
                guard_valid_preserved += 1
        cards.append(
            {
                "model_id": model_id,
                "row_count": len(rows),
                "correct_count": correct,
                "accuracy_pct": pct(correct, len(rows)),
                "false_authority_count": false_authority,
                "false_block_valid_count": false_block,
                "valid_expected_count": valid_expected,
                "parse_observed_count": parse_known,
                "parse_failure_count": parse_failed,
                "guard_false_authority_after": guard_false_authority,
                "guard_expected_mismatch_after": guard_mismatch,
                "guard_valid_preserved_after": guard_valid_preserved,
                "primary_failure": primary_failure(rows),
            }
        )
    return cards


def grouped_summary(scored_rows: list[dict[str, Any]], group_field: str) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        grouped[(row["model_id"], row[group_field])].append(row)

    rows: list[dict[str, Any]] = []
    for (model_id, group_value), items in sorted(grouped.items()):
        correct = sum(1 for row in items if truthy(row["is_correct"]))
        false_authority = sum(1 for row in items if truthy(row["false_authority"]))
        false_block = sum(1 for row in items if truthy(row["false_block_valid"]))
        rows.append(
            {
                "model_id": model_id,
                group_field: group_value,
                "row_count": len(items),
                "correct_count": correct,
                "accuracy_pct": pct(correct, len(items)),
                "false_authority_count": false_authority,
                "false_block_valid_count": false_block,
                "primary_failure": primary_failure(items),
            }
        )
    return rows


def error_category_summary(scored_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str]] = Counter()
    false_counts: Counter[tuple[str, str]] = Counter()
    for row in scored_rows:
        if row["error_category"] == "correct":
            continue
        key = (row["model_id"], row["error_category"])
        counts[key] += 1
        if truthy(row["false_authority"]):
            false_counts[key] += 1
    return [
        {
            "model_id": model_id,
            "error_category": category,
            "row_count": count,
            "false_authority_count": false_counts[(model_id, category)],
        }
        for (model_id, category), count in sorted(counts.items())
    ]


def select_examples(
    scored_rows: list[dict[str, Any]],
    cases_by_id: dict[str, dict[str, Any]],
    guard_by_case: dict[str, dict[str, str]],
    limit_per_model: int,
) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        if row["error_category"] != "correct":
            by_model[row["model_id"]].append(row)

    examples: list[dict[str, Any]] = []
    for model_id, rows in sorted(by_model.items()):
        rows.sort(
            key=lambda row: (
                not truthy(row["false_authority"]),
                not truthy(row["false_block_valid"]),
                row["error_category"],
                row["case_id"],
            )
        )
        seen_categories: set[str] = set()
        for row in rows:
            if row["error_category"] in seen_categories and len(seen_categories) < limit_per_model:
                continue
            case = cases_by_id[row["case_id"]]
            guard = guard_by_case.get(row["case_id"], {})
            examples.append(
                {
                    "model_id": model_id,
                    "case_id": row["case_id"],
                    "error_category": row["error_category"],
                    "business_scenario": case.get("business_scenario", ""),
                    "customer_question": case.get("customer_question", case.get("query", "")),
                    "retrieved_source": case.get("retrieved_source", case.get("candidate", "")),
                    "what_it_proves": case.get("what_it_proves", ""),
                    "what_it_does_not_prove": case.get("what_it_does_not_prove", ""),
                    "expected_decision": row["expected_decision"],
                    "model_decision": row["model_decision"],
                    "guard_decision": guard.get("boundary_decision", ""),
                    "model_reason": row["model_reason"],
                }
            )
            seen_categories.add(row["error_category"])
            if len(examples_for_model(examples, model_id)) >= limit_per_model:
                break
    return examples


def examples_for_model(examples: list[dict[str, Any]], model_id: str) -> list[dict[str, Any]]:
    return [row for row in examples if row["model_id"] == model_id]


def write_markdown(
    out_dir: Path,
    scorecard: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    archetypes: list[dict[str, Any]],
    authorities: list[dict[str, Any]],
    examples: list[dict[str, Any]],
) -> None:
    lines = [
        "# OpenAI / Anthropic Concept Boundary Analysis",
        "",
        f"Generated at UTC: `{datetime.now(UTC).isoformat()}`",
        "",
        "## Model Scorecard",
        "",
        "| Model | Rows | Accuracy | False authority | False valid block | Parse failures | Guard false authority after | Primary failure |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in scorecard:
        lines.append(
            "| {model_id} | {row_count} | {accuracy_pct}% | {false_authority_count} | "
            "{false_block_valid_count} | {parse_failure_count}/{parse_observed_count} | "
            "{guard_false_authority_after} | {primary_failure} |".format(**row)
        )

    lines.extend(["", "## Error Categories", "", "| Model | Category | Rows | False authority |", "| --- | --- | ---: | ---: |"])
    for row in errors:
        lines.append("| {model_id} | {error_category} | {row_count} | {false_authority_count} |".format(**row))

    lines.extend(["", "## Weakest Archetypes", "", "| Model | Archetype | Rows | Accuracy | False authority | Primary failure |", "| --- | --- | ---: | ---: | ---: | --- |"])
    for row in sorted(archetypes, key=lambda item: (item["model_id"], item["accuracy_pct"], -item["row_count"]))[:24]:
        lines.append(
            "| {model_id} | {archetype} | {row_count} | {accuracy_pct}% | {false_authority_count} | {primary_failure} |".format(**row)
        )

    lines.extend(["", "## Authority Boundary", "", "| Model | Requested authority | Rows | Accuracy | False authority | False valid block |", "| --- | --- | ---: | ---: | ---: | ---: |"])
    for row in authorities:
        lines.append(
            "| {model_id} | {requested_authority} | {row_count} | {accuracy_pct}% | {false_authority_count} | {false_block_valid_count} |".format(**row)
        )

    lines.extend(["", "## Example Failures", ""])
    for row in examples:
        lines.extend(
            [
                f"### {row['model_id']} / {row['case_id']} / {row['error_category']}",
                "",
                f"- Business scenario: {row['business_scenario']}",
                f"- Customer question: {row['customer_question']}",
                f"- Retrieved source: {row['retrieved_source']}",
                f"- What it proves: {row['what_it_proves']}",
                f"- What it does not prove: {row['what_it_does_not_prove']}",
                f"- Model decision: `{row['model_decision']}`",
                f"- Expected decision: `{row['expected_decision']}`",
                f"- LatentAtlas guard decision: `{row['guard_decision']}`",
                f"- Model reason: {row['model_reason']}",
                "",
            ]
        )
    (out_dir / "openai_anthropic_detailed_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    scored_path: Path = DEFAULT_SCORED,
    cases_path: Path = DEFAULT_CASES,
    guard_decisions_path: Path = DEFAULT_GUARD_DECISIONS,
    raw_outputs_path: Path = DEFAULT_RAW_OUTPUTS,
    out_dir: Path = DEFAULT_OUT_DIR,
    models: tuple[str, ...] = DEFAULT_MODELS,
    example_limit_per_model: int = 10,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    model_set = set(models)
    scored_rows = [row for row in read_csv(scored_path) if row.get("model_id") in model_set]
    cases_by_id = {row["case_id"]: row for row in read_jsonl(cases_path)}
    guard_by_case = {row["case_id"]: row for row in read_csv(guard_decisions_path)}
    raw_by_key = {output_key(row): row for row in read_jsonl(raw_outputs_path) if row.get("model_id") in model_set}

    scorecard = model_scorecard(scored_rows, guard_by_case, raw_by_key)
    errors = error_category_summary(scored_rows)
    archetypes = grouped_summary(scored_rows, "archetype")
    authorities = grouped_summary(scored_rows, "requested_authority")
    examples = select_examples(scored_rows, cases_by_id, guard_by_case, example_limit_per_model)

    write_csv(out_dir / "openai_anthropic_model_detail.csv", scorecard)
    write_csv(out_dir / "openai_anthropic_error_categories.csv", errors)
    write_csv(out_dir / "openai_anthropic_archetypes.csv", archetypes)
    write_csv(out_dir / "openai_anthropic_requested_authority.csv", authorities)
    write_csv(out_dir / "openai_anthropic_examples.csv", examples)
    write_markdown(out_dir, scorecard, errors, archetypes, authorities, examples)

    missing_models = sorted(model_set - {row["model_id"] for row in scored_rows})
    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "openai_anthropic_boundary_analysis",
        "status": "pass" if scored_rows and not missing_models else "needs_review",
        "scored_path": str(scored_path),
        "cases_path": str(cases_path),
        "guard_decisions_path": str(guard_decisions_path),
        "raw_outputs_path": str(raw_outputs_path),
        "models": list(models),
        "missing_models": missing_models,
        "scored_row_count": len(scored_rows),
        "outputs": {
            "markdown": str(out_dir / "openai_anthropic_detailed_analysis.md"),
            "model_detail": str(out_dir / "openai_anthropic_model_detail.csv"),
            "error_categories": str(out_dir / "openai_anthropic_error_categories.csv"),
            "archetypes": str(out_dir / "openai_anthropic_archetypes.csv"),
            "requested_authority": str(out_dir / "openai_anthropic_requested_authority.csv"),
            "examples": str(out_dir / "openai_anthropic_examples.csv"),
            "manifest": str(out_dir / "manifest.json"),
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scored", type=Path, default=DEFAULT_SCORED)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--guard-decisions", type=Path, default=DEFAULT_GUARD_DECISIONS)
    parser.add_argument("--raw-outputs", type=Path, default=DEFAULT_RAW_OUTPUTS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", action="append", default=None)
    parser.add_argument("--example-limit-per-model", type=int, default=10)
    args = parser.parse_args()
    models = tuple(args.model) if args.model else DEFAULT_MODELS
    manifest = run(
        args.scored,
        args.cases,
        args.guard_decisions,
        args.raw_outputs,
        args.out_dir,
        models,
        args.example_limit_per_model,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
