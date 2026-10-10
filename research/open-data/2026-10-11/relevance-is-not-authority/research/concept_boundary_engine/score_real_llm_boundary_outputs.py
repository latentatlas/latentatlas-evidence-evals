"""Score real LLM outputs against a Concept Boundary fixture.

Expected input JSONL rows:

{
  "model_id": "provider-model-name",
  "case_id": "cbe500-0001",
  "decision": "allow_evidence|allow_action|allow_publish|allow_identity_candidate|manual_review|block_false_authority|block_contradiction|block_privacy",
  "reason": "short model explanation"
}

This scorer is local-only. It does not call model APIs.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


BENCHMARK_PATH = Path(__file__).with_name("run_concept_boundary_model_benchmark.py")
SPEC = importlib.util.spec_from_file_location("run_concept_boundary_model_benchmark", BENCHMARK_PATH)
benchmark = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(benchmark)

CASES_PATH = Path("research/concept_boundary_engine/concept_boundary_500_cases.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_real_llm_scores")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def score_outputs(outputs_path: Path, out_dir: Path, cases_path: Path = CASES_PATH) -> dict[str, Any]:
    cases = {row["case_id"]: row for row in read_jsonl(cases_path)}
    raw_outputs = read_jsonl(outputs_path)
    scored: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for line_number, output in enumerate(raw_outputs, start=1):
        case_id = output.get("case_id")
        model_id = output.get("model_id")
        decision = output.get("decision")
        if case_id not in cases:
            failures.append({"line": line_number, "failure": "unknown_case_id", "case_id": case_id})
            continue
        if not model_id:
            failures.append({"line": line_number, "failure": "missing_model_id", "case_id": case_id})
            continue
        if decision not in benchmark.ALLOW_DECISIONS | benchmark.BLOCK_DECISIONS | {"manual_review"}:
            failures.append({"line": line_number, "failure": "invalid_decision", "case_id": case_id, "decision": decision})
            continue
        scored.append(
            benchmark.score_model_output(
                cases[case_id],
                str(model_id),
                str(decision),
                str(output.get("reason", "")),
            )
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "scored_outputs.csv", scored)
    model_summaries = summarize_real_models(scored)
    category_rows = benchmark.category_summary(scored)
    write_csv(out_dir / "model_summary.csv", model_summaries)
    write_csv(out_dir / "error_category_summary.csv", category_rows)

    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "concept_boundary_real_llm_output_scorer",
        "status": "pass" if not failures else "fail",
        "input": str(outputs_path),
        "cases_path": str(cases_path),
        "data_classification": "synthetic_benchmark_outputs",
        "external_llm_calls_used_by_scorer": False,
        "raw_output_count": len(raw_outputs),
        "scored_output_count": len(scored),
        "failure_count": len(failures),
        "failure_sample": failures[:20],
        "model_count": len({row["model_id"] for row in scored}),
        "model_summaries": model_summaries,
        "outputs": {
            "scored_outputs": str(out_dir / "scored_outputs.csv"),
            "model_summary": str(out_dir / "model_summary.csv"),
            "error_category_summary": str(out_dir / "error_category_summary.csv"),
            "manifest": str(out_dir / "manifest.json"),
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def summarize_real_models(scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        by_model[row["model_id"]].append(row)

    summaries: list[dict[str, Any]] = []
    for model_id, rows in sorted(by_model.items()):
        false_authority = sum(1 for row in rows if row["false_authority"])
        false_block = sum(1 for row in rows if row["false_block_valid"])
        correct = sum(1 for row in rows if row["is_correct"])
        summaries.append(
            {
                "model_id": model_id,
                "row_count": len(rows),
                "correct_count": correct,
                "accuracy_pct": round(correct / len(rows) * 100, 2),
                "false_authority_count": false_authority,
                "false_block_valid_count": false_block,
                "primary_failure": benchmark.primary_failure(rows),
            }
        )
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--cases", type=Path, default=CASES_PATH)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    manifest = score_outputs(args.input, args.out_dir, args.cases)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
