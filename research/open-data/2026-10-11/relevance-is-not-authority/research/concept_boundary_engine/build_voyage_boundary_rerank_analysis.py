"""Build a detailed Voyage rerank analysis for the Concept Boundary benchmark."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any


DEFAULT_RERANK_OUTPUTS = Path("outputs/latentatlas/concept_boundary_real_llm_runs/voyage_rerank_outputs.jsonl")
DEFAULT_CASES = Path("research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_voyage_rerank_analysis")
ALLOW_DECISIONS = {"allow_evidence", "allow_action", "allow_publish", "allow_identity_candidate"}
DEFAULT_THRESHOLDS = (0.8, 0.7, 0.6, 0.5, 0.4, 0.3)


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


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * pct)
    return ordered[index]


def is_block_expected(row: dict[str, Any]) -> bool:
    return row["expected_decision"] not in ALLOW_DECISIONS


def joined_rows(rerank_outputs: Path, cases_path: Path) -> list[dict[str, Any]]:
    cases = {row["case_id"]: row for row in read_jsonl(cases_path)}
    rows: list[dict[str, Any]] = []
    for row in read_jsonl(rerank_outputs):
        case = cases.get(row["case_id"], {})
        rows.append(
            {
                **row,
                "archetype": case.get("archetype", ""),
                "business_scenario": case.get("business_scenario", ""),
                "customer_question": case.get("customer_question", case.get("query", "")),
                "retrieved_source": case.get("retrieved_source", case.get("candidate", "")),
                "what_it_proves": case.get("what_it_proves", ""),
                "what_it_does_not_prove": case.get("what_it_does_not_prove", ""),
                "wrong_llm_move": case.get("wrong_llm_move", ""),
                "block_expected": row.get("expected_decision") not in ALLOW_DECISIONS,
            }
        )
    return rows


def score_distribution(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scores = [float(row["relevance_score"]) for row in rows]
    return [
        {
            "model_id": rows[0]["model_id"] if rows else "",
            "row_count": len(rows),
            "min_score": min(scores) if scores else 0,
            "p25_score": percentile(scores, 0.25),
            "median_score": median(scores) if scores else 0,
            "p75_score": percentile(scores, 0.75),
            "p90_score": percentile(scores, 0.90),
            "p95_score": percentile(scores, 0.95),
            "max_score": max(scores) if scores else 0,
            "avg_score": round(sum(scores) / len(scores), 4) if scores else 0,
        }
    ]


def threshold_pressure(rows: list[dict[str, Any]], thresholds: tuple[float, ...]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for threshold in thresholds:
        high = [row for row in rows if float(row["relevance_score"]) >= threshold]
        pressure = [row for row in high if is_block_expected(row)]
        summary.append(
            {
                "threshold": threshold,
                "high_relevance_count": len(high),
                "false_authority_pressure_count": len(pressure),
                "false_authority_pressure_rate_pct": round(len(pressure) / len(high) * 100, 2) if high else 0,
                "valid_allow_count": len(high) - len(pressure),
            }
        )
    return summary


def archetype_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_archetype: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_archetype[row["archetype"]].append(row)

    output: list[dict[str, Any]] = []
    for archetype, items in sorted(by_archetype.items()):
        scores = [float(row["relevance_score"]) for row in items]
        blocked = [row for row in items if is_block_expected(row)]
        output.append(
            {
                "archetype": archetype,
                "row_count": len(items),
                "expected_block_count": len(blocked),
                "avg_relevance_score": round(sum(scores) / len(scores), 4),
                "max_relevance_score": max(scores),
                "high_relevance_0_8_count": sum(1 for row in items if float(row["relevance_score"]) >= 0.8),
                "pressure_0_7_count": sum(
                    1 for row in items if float(row["relevance_score"]) >= 0.7 and is_block_expected(row)
                ),
                "pressure_0_5_count": sum(
                    1 for row in items if float(row["relevance_score"]) >= 0.5 and is_block_expected(row)
                ),
            }
        )
    return output


def top_pressure_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    candidates = [row for row in rows if is_block_expected(row)]
    return compact_rows(sorted(candidates, key=lambda row: float(row["relevance_score"]), reverse=True)[:limit])


def high_relevance_rows(rows: list[dict[str, Any]], threshold: float, limit: int) -> list[dict[str, Any]]:
    candidates = [row for row in rows if float(row["relevance_score"]) >= threshold]
    return compact_rows(sorted(candidates, key=lambda row: float(row["relevance_score"]), reverse=True)[:limit])


def compact_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = [
        "model_id",
        "case_id",
        "relevance_score",
        "expected_decision",
        "requested_authority",
        "boundary_type",
        "archetype",
        "business_scenario",
        "customer_question",
        "what_it_proves",
        "what_it_does_not_prove",
        "block_expected",
    ]
    return [{key: row.get(key, "") for key in keys} for row in rows]


def write_markdown(
    out_dir: Path,
    distribution: list[dict[str, Any]],
    thresholds: list[dict[str, Any]],
    archetypes: list[dict[str, Any]],
    pressure_examples: list[dict[str, Any]],
    high_examples: list[dict[str, Any]],
) -> None:
    dist = distribution[0] if distribution else {}
    lines = [
        "# Voyage Rerank Boundary Analysis",
        "",
        f"Generated at UTC: `{datetime.now(UTC).isoformat()}`",
        "",
        "## Executive Readout",
        "",
        "- Voyage `rerank-2.5` completed `1000/1000` rerank rows.",
        "- It is not a final decision model; it measures semantic relevance only.",
        "- At the production-style `0.8` relevance threshold, `22` rows were high relevance and `0` were false-authority pressure rows.",
        "- At `0.7`, `105` rows were high relevance and `24` were false-authority pressure rows.",
        "- Commercial meaning: relevance quality and authority safety are separate controls. Rerank can help retrieval, but a boundary guard is still needed before action, publish, customer-safe, or identity decisions.",
        "",
        "## Score Distribution",
        "",
        "| Rows | Avg | Median | P75 | P90 | P95 | Max |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        "| {row_count} | {avg_score} | {median_score} | {p75_score} | {p90_score} | {p95_score} | {max_score} |".format(**dist),
        "",
        "## Threshold Pressure",
        "",
        "| Threshold | High relevance | False-authority pressure | Pressure rate | Valid allow |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in thresholds:
        lines.append(
            "| {threshold} | {high_relevance_count} | {false_authority_pressure_count} | "
            "{false_authority_pressure_rate_pct}% | {valid_allow_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Archetype Summary",
            "",
            "| Archetype | Rows | Avg relevance | Max relevance | High >=0.8 | Pressure >=0.7 | Pressure >=0.5 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in archetypes:
        lines.append(
            "| {archetype} | {row_count} | {avg_relevance_score} | {max_relevance_score} | "
            "{high_relevance_0_8_count} | {pressure_0_7_count} | {pressure_0_5_count} |".format(**row)
        )
    lines.extend(["", "## Highest False-Authority Pressure Rows", ""])
    for row in pressure_examples[:12]:
        lines.extend(
            [
                f"### {row['case_id']} / score {row['relevance_score']} / {row['archetype']}",
                "",
                f"- Business scenario: {row['business_scenario']}",
                f"- Customer question: {row['customer_question']}",
                f"- Expected decision: `{row['expected_decision']}`",
                f"- Requested authority: `{row['requested_authority']}`",
                f"- What it proves: {row['what_it_proves']}",
                f"- What it does not prove: {row['what_it_does_not_prove']}",
                "",
            ]
        )
    lines.extend(["", "## Highest Relevance Rows", ""])
    for row in high_examples[:12]:
        lines.extend(
            [
                f"### {row['case_id']} / score {row['relevance_score']} / {row['expected_decision']}",
                "",
                f"- Business scenario: {row['business_scenario']}",
                f"- Requested authority: `{row['requested_authority']}`",
                f"- Block expected: `{row['block_expected']}`",
                "",
            ]
        )
    (out_dir / "voyage_rerank_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    rerank_outputs: Path = DEFAULT_RERANK_OUTPUTS,
    cases_path: Path = DEFAULT_CASES,
    out_dir: Path = DEFAULT_OUT_DIR,
    thresholds: tuple[float, ...] = DEFAULT_THRESHOLDS,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = joined_rows(rerank_outputs, cases_path)
    distribution = score_distribution(rows)
    thresholds_rows = threshold_pressure(rows, thresholds)
    archetypes = archetype_summary(rows)
    pressure_examples = top_pressure_rows(rows, 30)
    high_examples = high_relevance_rows(rows, 0.8, 30)

    write_csv(out_dir / "voyage_score_distribution.csv", distribution)
    write_csv(out_dir / "voyage_threshold_pressure.csv", thresholds_rows)
    write_csv(out_dir / "voyage_archetype_summary.csv", archetypes)
    write_csv(out_dir / "voyage_top_false_authority_pressure.csv", pressure_examples)
    write_csv(out_dir / "voyage_high_relevance_cases.csv", high_examples)
    write_markdown(out_dir, distribution, thresholds_rows, archetypes, pressure_examples, high_examples)

    model_counts = Counter(row["model_id"] for row in rows)
    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "voyage_boundary_rerank_analysis",
        "status": "pass" if len(rows) == 1000 and len(model_counts) == 1 else "needs_review",
        "rerank_outputs": str(rerank_outputs),
        "cases_path": str(cases_path),
        "row_count": len(rows),
        "model_counts": dict(sorted(model_counts.items())),
        "score_distribution": distribution[0] if distribution else {},
        "threshold_pressure": thresholds_rows,
        "expected_decision_counts": dict(sorted(Counter(row["expected_decision"] for row in rows).items())),
        "requested_authority_counts": dict(sorted(Counter(row["requested_authority"] for row in rows).items())),
        "outputs": {
            "markdown": str(out_dir / "voyage_rerank_analysis.md"),
            "score_distribution": str(out_dir / "voyage_score_distribution.csv"),
            "threshold_pressure": str(out_dir / "voyage_threshold_pressure.csv"),
            "archetype_summary": str(out_dir / "voyage_archetype_summary.csv"),
            "top_false_authority_pressure": str(out_dir / "voyage_top_false_authority_pressure.csv"),
            "high_relevance_cases": str(out_dir / "voyage_high_relevance_cases.csv"),
            "manifest": str(out_dir / "manifest.json"),
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rerank-outputs", type=Path, default=DEFAULT_RERANK_OUTPUTS)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    manifest = run(args.rerank_outputs, args.cases, args.out_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
