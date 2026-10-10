"""Lock paid real-API benchmark artifacts with checksums and copies."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_LOCK_DIR = Path("outputs/latentatlas/locked_benchmarks/concept_boundary_real_api_20260513")
DEFAULT_ARTIFACTS = [
    Path("outputs/latentatlas/concept_boundary_real_llm_runs/manifest.json"),
    Path("outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs_cleaned.jsonl"),
    Path("outputs/latentatlas/concept_boundary_real_llm_runs/voyage_rerank_outputs.jsonl"),
    Path("outputs/latentatlas/concept_boundary_real_llm_evidence_pack/manifest.json"),
    Path("outputs/latentatlas/concept_boundary_real_llm_evidence_pack/real_llm_executive_brief.md"),
    Path("outputs/latentatlas/concept_boundary_real_llm_evidence_pack/real_model_scorecard.csv"),
    Path("outputs/latentatlas/concept_boundary_openai_anthropic_analysis/openai_anthropic_detailed_analysis.md"),
    Path("outputs/latentatlas/concept_boundary_openai_anthropic_analysis/openai_anthropic_model_detail.csv"),
    Path("outputs/latentatlas/concept_boundary_real_llm_coverage_audit/manifest.json"),
    Path("outputs/latentatlas/concept_boundary_real_llm_coverage_audit/coverage_by_model.csv"),
    Path("outputs/latentatlas/concept_boundary_real_llm_coverage_audit/missing_cases.csv"),
    Path("outputs/latentatlas/concept_boundary_voyage_rerank_analysis/manifest.json"),
    Path("outputs/latentatlas/concept_boundary_voyage_rerank_analysis/voyage_rerank_analysis.md"),
    Path("outputs/latentatlas/concept_boundary_voyage_rerank_analysis/voyage_threshold_pressure.csv"),
    Path("outputs/latentatlas/concept_boundary_voyage_rerank_analysis/voyage_archetype_summary.csv"),
    Path("commercial/latentatlas_first_customer/24_real_api_vs_offline_benchmark_comparison.md"),
    Path("commercial/latentatlas_first_customer/26_real_api_model_performance_breakdown.md"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(path: Path) -> str:
    return path.as_posix().lstrip("/").replace("/", "__")


def run(lock_dir: Path = DEFAULT_LOCK_DIR, artifacts: list[Path] | None = None) -> dict[str, Any]:
    selected = artifacts or DEFAULT_ARTIFACTS
    lock_dir.mkdir(parents=True, exist_ok=True)
    copied: list[dict[str, Any]] = []
    missing: list[str] = []

    for source in selected:
        if not source.exists():
            missing.append(str(source))
            continue
        target = lock_dir / safe_name(source)
        shutil.copy2(source, target)
        copied.append(
            {
                "source": str(source),
                "locked_copy": str(target),
                "size_bytes": source.stat().st_size,
                "sha256": sha256(source),
            }
        )

    checksum_lines = [f"{row['sha256']}  {row['source']}" for row in copied]
    (lock_dir / "sha256_checksums.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    readme = [
        "# Locked Concept Boundary Real API Benchmark",
        "",
        f"Locked at UTC: `{datetime.now(UTC).isoformat()}`",
        "",
        "This folder preserves the paid 2026-05-13 real API benchmark artifacts.",
        "Do not rerun this benchmark just to recover the same evidence; use the locked copies and checksums first.",
        "",
        "Known limitation: Cohere has 990/1000 decision coverage because the provider returned 429 quota/rate-limit errors for 10 rows.",
        "OpenAI, Anthropic, and Voyage have 1000/1000 coverage.",
        "",
        "## Checksums",
        "",
        "See `sha256_checksums.txt`.",
        "",
    ]
    (lock_dir / "README.md").write_text("\n".join(readme), encoding="utf-8")

    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "locked_real_llm_boundary_benchmark_artifacts",
        "status": "pass" if copied and not missing else "needs_review",
        "lock_dir": str(lock_dir),
        "artifact_count": len(copied),
        "missing_artifacts": missing,
        "artifacts": copied,
        "outputs": {
            "readme": str(lock_dir / "README.md"),
            "checksums": str(lock_dir / "sha256_checksums.txt"),
            "manifest": str(lock_dir / "LOCK_MANIFEST.json"),
        },
    }
    (lock_dir / "LOCK_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock-dir", type=Path, default=DEFAULT_LOCK_DIR)
    parser.add_argument("--artifact", type=Path, action="append", default=None)
    args = parser.parse_args()
    manifest = run(args.lock_dir, args.artifact)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
