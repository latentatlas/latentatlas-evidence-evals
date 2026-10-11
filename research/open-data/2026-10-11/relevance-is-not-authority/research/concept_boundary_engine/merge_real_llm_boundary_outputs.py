"""Merge real LLM benchmark outputs with explicit replacement provenance.

The full API runner supports resume, so a later full run can intentionally skip
rows that were collected during an earlier smoke run. When an earlier smoke row
is known to be superseded by a cleaner rerun, this utility writes a separate
cleaned JSONL for scoring without mutating the original raw artifact.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_PRIMARY = Path("outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs.jsonl")
DEFAULT_REPLACEMENT = Path("outputs/latentatlas/concept_boundary_real_llm_runs_cohere_rerun/real_llm_outputs.jsonl")
DEFAULT_OUTPUT = Path("outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs_cleaned.jsonl")
DEFAULT_MANIFEST = Path("outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs_cleaned_manifest.json")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def output_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row["model_id"]), str(row["case_id"]))


def merge_outputs(primary_path: Path, replacement_paths: list[Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    primary_rows = read_jsonl(primary_path)
    replacement_rows: dict[tuple[str, str], dict[str, Any]] = {}
    replacement_sources: dict[tuple[str, str], str] = {}
    replacement_source_counts: Counter[str] = Counter()

    for path in replacement_paths:
        for row in read_jsonl(path):
            key = output_key(row)
            replacement_rows[key] = row
            replacement_sources[key] = str(path)
            replacement_source_counts[str(path)] += 1

    merged: list[dict[str, Any]] = []
    seen: Counter[tuple[str, str]] = Counter()
    replaced: list[dict[str, str]] = []
    used_replacements: set[tuple[str, str]] = set()

    for row in primary_rows:
        key = output_key(row)
        seen[key] += 1
        if key in replacement_rows:
            merged.append(replacement_rows[key])
            used_replacements.add(key)
            replaced.append(
                {
                    "model_id": key[0],
                    "case_id": key[1],
                    "replacement_source": replacement_sources[key],
                }
            )
        else:
            merged.append(row)

    appended: list[dict[str, str]] = []
    for key in sorted(set(replacement_rows) - used_replacements):
        merged.append(replacement_rows[key])
        appended.append(
            {
                "model_id": key[0],
                "case_id": key[1],
                "replacement_source": replacement_sources[key],
            }
        )

    duplicate_keys = [
        {"model_id": key[0], "case_id": key[1], "count": count}
        for key, count in sorted(seen.items())
        if count > 1
    ]
    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "real_llm_output_clean_merge",
        "primary_path": str(primary_path),
        "replacement_paths": [str(path) for path in replacement_paths],
        "primary_row_count": len(primary_rows),
        "replacement_candidate_count": len(replacement_rows),
        "replacement_source_counts": dict(sorted(replacement_source_counts.items())),
        "merged_row_count": len(merged),
        "replaced_count": len(replaced),
        "appended_replacement_count": len(appended),
        "duplicate_primary_key_count": len(duplicate_keys),
        "duplicate_primary_key_sample": duplicate_keys[:20],
        "replacement_sample": replaced[:20],
        "appended_sample": appended[:20],
        "status": "pass" if not duplicate_keys else "needs_review",
    }
    return merged, manifest


def run(
    primary_path: Path = DEFAULT_PRIMARY,
    replacement_paths: list[Path] | None = None,
    output_path: Path = DEFAULT_OUTPUT,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> dict[str, Any]:
    paths = replacement_paths or [DEFAULT_REPLACEMENT]
    merged, manifest = merge_outputs(primary_path, paths)
    manifest["output_path"] = str(output_path)
    write_jsonl(output_path, merged)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--replacement", type=Path, action="append", default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest = run(args.primary, args.replacement, args.output, args.manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
