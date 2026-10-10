"""Audit real LLM benchmark coverage by model and case id."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_CASES = Path("research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl")
DEFAULT_DECISION_OUTPUTS = Path("outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs_cleaned.jsonl")
DEFAULT_RERANK_OUTPUTS = Path("outputs/latentatlas/concept_boundary_real_llm_runs/voyage_rerank_outputs.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_real_llm_coverage_audit")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames or list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def audit(
    cases_path: Path = DEFAULT_CASES,
    decision_outputs_path: Path = DEFAULT_DECISION_OUTPUTS,
    rerank_outputs_path: Path = DEFAULT_RERANK_OUTPUTS,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    case_ids = [row["case_id"] for row in read_jsonl(cases_path)]
    expected = set(case_ids)
    decision_rows = read_jsonl(decision_outputs_path)
    rerank_rows = read_jsonl(rerank_outputs_path)

    by_model: dict[str, set[str]] = defaultdict(set)
    for row in decision_rows:
        by_model[str(row["model_id"])].add(str(row["case_id"]))
    for row in rerank_rows:
        by_model[str(row["model_id"])].add(str(row["case_id"]))

    coverage_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []
    raw_counts: dict[tuple[str, str], int] = defaultdict(int)
    for row in decision_rows + rerank_rows:
        raw_counts[(str(row["model_id"]), str(row["case_id"]))] += 1

    for model_id in sorted(by_model):
        seen = by_model[model_id]
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        coverage_rows.append(
            {
                "model_id": model_id,
                "expected_case_count": len(expected),
                "observed_case_count": len(seen & expected),
                "missing_case_count": len(missing),
                "extra_case_count": len(extra),
                "coverage_pct": round(len(seen & expected) / len(expected) * 100, 2) if expected else 0,
            }
        )
        for case_id in missing:
            missing_rows.append({"model_id": model_id, "case_id": case_id})

    for (model_id, case_id), count in sorted(raw_counts.items()):
        if count > 1:
            duplicate_rows.append({"model_id": model_id, "case_id": case_id, "count": count})

    write_csv(out_dir / "coverage_by_model.csv", coverage_rows)
    write_csv(out_dir / "missing_cases.csv", missing_rows, ["model_id", "case_id"])
    write_csv(out_dir / "duplicate_cases.csv", duplicate_rows, ["model_id", "case_id", "count"])

    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "real_llm_boundary_coverage_audit",
        "cases_path": str(cases_path),
        "decision_outputs_path": str(decision_outputs_path),
        "rerank_outputs_path": str(rerank_outputs_path),
        "model_count": len(coverage_rows),
        "coverage_by_model": coverage_rows,
        "missing_case_count_total": len(missing_rows),
        "duplicate_case_count_total": len(duplicate_rows),
        "status": "pass" if not missing_rows and not duplicate_rows else "needs_review",
        "outputs": {
            "coverage_by_model": str(out_dir / "coverage_by_model.csv"),
            "missing_cases": str(out_dir / "missing_cases.csv"),
            "duplicate_cases": str(out_dir / "duplicate_cases.csv"),
            "manifest": str(out_dir / "manifest.json"),
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--decision-outputs", type=Path, default=DEFAULT_DECISION_OUTPUTS)
    parser.add_argument("--rerank-outputs", type=Path, default=DEFAULT_RERANK_OUTPUTS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    manifest = audit(args.cases, args.decision_outputs, args.rerank_outputs, args.out_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
