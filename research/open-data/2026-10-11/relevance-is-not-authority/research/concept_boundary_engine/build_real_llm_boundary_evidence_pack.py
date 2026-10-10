"""Build sales-ready evidence from real Concept Boundary LLM outputs.

This consumes real API outputs already collected by
`run_real_llm_boundary_benchmark.py`, scores them locally, compares each model
decision with the deterministic LatentAtlas guard, and writes buyer-facing
before/after artifacts.
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


SCORER_PATH = Path(__file__).with_name("score_real_llm_boundary_outputs.py")
SCORER_SPEC = importlib.util.spec_from_file_location("score_real_llm_boundary_outputs", SCORER_PATH)
scorer = importlib.util.module_from_spec(SCORER_SPEC)
assert SCORER_SPEC.loader is not None
SCORER_SPEC.loader.exec_module(scorer)

SALES_PACK_PATH = Path(__file__).with_name("build_boundary_sales_evidence_pack.py")
SALES_SPEC = importlib.util.spec_from_file_location("build_boundary_sales_evidence_pack", SALES_PACK_PATH)
sales_pack = importlib.util.module_from_spec(SALES_SPEC)
assert SALES_SPEC.loader is not None
SALES_SPEC.loader.exec_module(sales_pack)

DEFAULT_RAW_OUTPUTS = Path("outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs.jsonl")
DEFAULT_RERANK_OUTPUTS = Path("outputs/latentatlas/concept_boundary_real_llm_runs/voyage_rerank_outputs.jsonl")
DEFAULT_CASES = Path("research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl")
DEFAULT_GUARD_DECISIONS = Path("outputs/latentatlas/concept_boundary_engine_1000_content/decisions.csv")
DEFAULT_SCORE_DIR = Path("outputs/latentatlas/concept_boundary_real_llm_scores_1000_full")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_real_llm_evidence_pack")

ALLOW_DECISIONS = scorer.benchmark.ALLOW_DECISIONS


def truthy(value: Any) -> bool:
    return value in {True, "True", "true", "1", 1}


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
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames or list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def model_scorecard(scored_rows: list[dict[str, Any]], guard_by_case: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored_rows:
        by_model[row["model_id"]].append(row)

    cards: list[dict[str, Any]] = []
    for model_id, rows in sorted(by_model.items()):
        correct = sum(1 for row in rows if truthy(row["is_correct"]))
        false_authority = sum(1 for row in rows if truthy(row["false_authority"]))
        false_block_valid = sum(1 for row in rows if truthy(row["false_block_valid"]))
        valid_expected = sum(1 for row in rows if row["expected_decision"] in ALLOW_DECISIONS)
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
                "accuracy_pct": round(correct / len(rows) * 100, 2) if rows else 0,
                "false_authority_before": false_authority,
                "false_authority_after_guard": guard_false_authority,
                "prevented_false_authority": false_authority - guard_false_authority,
                "false_block_valid_before": false_block_valid,
                "valid_expected_count": valid_expected,
                "valid_preserved_after_guard": guard_valid_preserved,
                "guard_expected_mismatch": guard_mismatch,
                "primary_failure": scorer.benchmark.primary_failure(rows),
            }
        )
    return cards


def category_solution_matrix(scored_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sales_pack.aggregate_category_solution_matrix(scored_rows)


def voyage_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[row["model_id"]].append(row)
    summaries: list[dict[str, Any]] = []
    for model_id, model_rows in sorted(by_model.items()):
        scores = [float(row["relevance_score"]) for row in model_rows]
        high_relevance = sum(1 for row in model_rows if row.get("high_relevance") is True)
        pressure = sum(1 for row in model_rows if row.get("high_relevance_false_authority_pressure") is True)
        summaries.append(
            {
                "model_id": model_id,
                "row_count": len(model_rows),
                "avg_relevance_score": round(sum(scores) / len(scores), 4) if scores else 0,
                "max_relevance_score": max(scores) if scores else 0,
                "high_relevance_count": high_relevance,
                "high_relevance_false_authority_pressure_count": pressure,
            }
        )
    return summaries


def select_real_examples(
    scored_rows: list[dict[str, Any]],
    cases_by_id: dict[str, dict[str, Any]],
    guard_by_case: dict[str, dict[str, str]],
    limit: int = 16,
) -> list[dict[str, Any]]:
    candidates = [row for row in scored_rows if row["error_category"] != "correct"]
    candidates.sort(key=lambda row: (not truthy(row["false_authority"]), row["error_category"], row["model_id"], row["case_id"]))
    examples: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in candidates:
        key = (row["model_id"], row["error_category"])
        if key in seen:
            continue
        case = cases_by_id[row["case_id"]]
        guard = guard_by_case.get(row["case_id"], {})
        examples.append(
            {
                "model_id": row["model_id"],
                "case_id": row["case_id"],
                "business_scenario": case.get("business_scenario", ""),
                "customer_question": case.get("customer_question", case["query"]),
                "retrieved_source": case.get("retrieved_source", case["candidate"]),
                "what_it_proves": case.get("what_it_proves", ""),
                "what_it_does_not_prove": case.get("what_it_does_not_prove", ""),
                "model_decision": row["model_decision"],
                "expected_decision": row["expected_decision"],
                "guard_decision": guard.get("boundary_decision", ""),
                "error_category": row["error_category"],
                "model_reason": row["model_reason"],
            }
        )
        seen.add(key)
        if len(examples) >= limit:
            break
    return examples


def write_markdown(
    out_dir: Path,
    scorecard: list[dict[str, Any]],
    matrix: list[dict[str, Any]],
    examples: list[dict[str, Any]],
    rerank_summary: list[dict[str, Any]],
    raw_output_count: int,
) -> None:
    total_false = sum(row["false_authority_before"] for row in scorecard)
    total_after = sum(row["false_authority_after_guard"] for row in scorecard)
    total_rows = sum(row["row_count"] for row in scorecard)
    status = "full" if all(row["row_count"] == 1000 for row in scorecard) else "partial"
    lines = [
        "# Real LLM Boundary Evidence Pack",
        "",
        f"Generated at UTC: `{datetime.now(UTC).isoformat()}`",
        "",
        "## Status",
        "",
        f"- Run status: `{status}`",
        f"- Raw decision outputs scored: `{raw_output_count}`",
        f"- Scored decision rows: `{total_rows}`",
        f"- False-authority before guard: `{total_false}`",
        f"- False-authority after LatentAtlas guard: `{total_after}`",
        "",
        "## Model Scorecard",
        "",
        "| Model | Rows | Accuracy | False authority before | After guard | Valid preserved after | Primary failure |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in scorecard:
        lines.append(
            "| {model_id} | {row_count} | {accuracy_pct}% | {false_authority_before} | "
            "{false_authority_after_guard} | {valid_preserved_after_guard}/{valid_expected_count} | {primary_failure} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Retrieval / Rerank Baseline",
            "",
            "| Model | Rows | Avg relevance | Max relevance | High relevance | High relevance false-authority pressure |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rerank_summary:
        lines.append(
            "| {model_id} | {row_count} | {avg_relevance_score} | {max_relevance_score} | "
            "{high_relevance_count} | {high_relevance_false_authority_pressure_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Commercial Readout",
            "",
            "This benchmark separates retrieval relevance from decision authority. A retrieved source can be relevant,",
            "yet still fail to grant evidence, action, publish, or customer-safe authority. LatentAtlas acts as the",
            "deterministic boundary verifier after model output.",
            "",
            "## Error Categories",
            "",
            "| Error category | Rows | Affected models | LatentAtlas solution |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for row in matrix:
        lines.append(
            "| {display_name} | {before_error_count} | {affected_models} | {latentatlas_solution} |".format(**row)
        )
    lines.extend(["", "## Example Failures", ""])
    for row in examples:
        lines.extend(
            [
                f"### {row['model_id']} / {row['case_id']} - {row['business_scenario']}",
                "",
                f"- Customer question: {row['customer_question']}",
                f"- Retrieved source: {row['retrieved_source']}",
                f"- What it proves: {row['what_it_proves']}",
                f"- What it does not prove: {row['what_it_does_not_prove']}",
                f"- Model decision: `{row['model_decision']}`",
                f"- Expected decision: `{row['expected_decision']}`",
                f"- LatentAtlas guard decision: `{row['guard_decision']}`",
                f"- Error category: `{row['error_category']}`",
                "",
            ]
        )
    (out_dir / "real_llm_executive_brief.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    raw_outputs: Path = DEFAULT_RAW_OUTPUTS,
    rerank_outputs: Path = DEFAULT_RERANK_OUTPUTS,
    cases_path: Path = DEFAULT_CASES,
    guard_decisions_path: Path = DEFAULT_GUARD_DECISIONS,
    score_dir: Path = DEFAULT_SCORE_DIR,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    score_manifest = scorer.score_outputs(raw_outputs, score_dir, cases_path)
    scored_rows = read_csv(score_dir / "scored_outputs.csv")
    cases_by_id = {row["case_id"]: row for row in read_jsonl(cases_path)}
    guard_by_case = {row["case_id"]: row for row in read_csv(guard_decisions_path)}
    rerank_rows = read_jsonl(rerank_outputs)

    scorecard = model_scorecard(scored_rows, guard_by_case)
    matrix = category_solution_matrix(scored_rows)
    examples = select_real_examples(scored_rows, cases_by_id, guard_by_case)
    rerank = voyage_summary(rerank_rows)

    write_csv(out_dir / "real_model_scorecard.csv", scorecard)
    write_csv(out_dir / "real_category_solution_matrix.csv", matrix)
    write_csv(out_dir / "real_example_failures.csv", examples)
    write_csv(out_dir / "real_rerank_summary.csv", rerank)
    write_markdown(out_dir, scorecard, matrix, examples, rerank, score_manifest["raw_output_count"])

    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "real_llm_boundary_evidence_pack",
        "status": "pass" if score_manifest["status"] == "pass" else "fail",
        "raw_outputs": str(raw_outputs),
        "rerank_outputs": str(rerank_outputs),
        "cases_path": str(cases_path),
        "score_manifest": score_manifest,
        "decision_model_count": len(scorecard),
        "decision_output_count": sum(row["row_count"] for row in scorecard),
        "false_authority_before_total": sum(row["false_authority_before"] for row in scorecard),
        "false_authority_after_guard_total": sum(row["false_authority_after_guard"] for row in scorecard),
        "rerank_model_count": len(rerank),
        "outputs": {
            "executive_brief": str(out_dir / "real_llm_executive_brief.md"),
            "model_scorecard": str(out_dir / "real_model_scorecard.csv"),
            "category_solution_matrix": str(out_dir / "real_category_solution_matrix.csv"),
            "example_failures": str(out_dir / "real_example_failures.csv"),
            "rerank_summary": str(out_dir / "real_rerank_summary.csv"),
            "manifest": str(out_dir / "manifest.json"),
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-outputs", type=Path, default=DEFAULT_RAW_OUTPUTS)
    parser.add_argument("--rerank-outputs", type=Path, default=DEFAULT_RERANK_OUTPUTS)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--guard-decisions", type=Path, default=DEFAULT_GUARD_DECISIONS)
    parser.add_argument("--score-dir", type=Path, default=DEFAULT_SCORE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    manifest = run(args.raw_outputs, args.rerank_outputs, args.cases, args.guard_decisions, args.score_dir, args.out_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
