#!/usr/bin/env python3
"""Build a transcript-free v0.8.3 analysis supplement from local run evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from latentatlas.authority_action_public_analysis import ARTIFACT_ID
from latentatlas.authority_action_public_analysis import MANIFEST_SCHEMA
from latentatlas.authority_action_public_analysis import METRIC_FIELDS
from latentatlas.authority_action_public_analysis import PROTOCOL_SCHEMA
from latentatlas.authority_action_public_analysis import ROW_FIELDS
from latentatlas.authority_action_public_analysis import ROW_SCHEMA
from latentatlas.authority_action_public_analysis import summarize_public_rows
from latentatlas.authority_action_public_analysis import validate_public_row


CORE_METRICS = {
    "action_attempted",
    "correct_decision",
    "explicit_withhold",
    "malformed_or_duplicate_action",
    "model_refusal",
    "unnecessary_withhold",
    "unsafe_action",
    "usable_decision",
}
SOURCE_ARTIFACT_PATHS = (
    "data/authority_action_v0_8_2_full_medium/summary.json",
    "latentatlas/authority_action_public_analysis.py",
    "scripts/build_authority_action_public_analysis.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no} must contain an object")
            rows.append(row)
    return rows


def load_source_scores(run_root: Path, source_rows: list[Mapping[str, Any]]) -> dict[tuple[str, str], Mapping[str, Any]]:
    selected = {
        (str(row["source_log_sha256"]), str(row["source_sample_uuid"]))
        for row in source_rows
    }
    wanted_hashes = {digest for digest, _ in selected}
    scores: dict[tuple[str, str], Mapping[str, Any]] = {}
    for path in sorted(run_root.rglob("*.json")):
        if any(part in {"analysis", "checkpoints"} for part in path.parts):
            continue
        digest = sha256(path)
        if digest not in wanted_hashes:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            continue
        for sample in payload.get("samples") or []:
            if not isinstance(sample, Mapping):
                continue
            key = (digest, str(sample.get("uuid")))
            if key not in selected:
                continue
            raw_scores = sample.get("scores") or {}
            if not isinstance(raw_scores, Mapping):
                raise ValueError(f"invalid scores in {path}")
            score = raw_scores.get("authority_action_scorer_v0_7")
            if not isinstance(score, Mapping):
                raise ValueError(f"missing v0.7 score in {path}")
            scores[key] = score
    missing = selected - set(scores)
    if missing:
        raise ValueError(f"could not resolve {len(missing)} selected analytical rows")
    return scores


def build_row(source: Mapping[str, Any], score: Mapping[str, Any]) -> dict[str, Any]:
    values = score.get("value")
    if not isinstance(values, Mapping):
        raise ValueError("score value must be an object")
    source_metrics = source.get("metrics")
    if not isinstance(source_metrics, Mapping) or not CORE_METRICS.issubset(source_metrics):
        raise ValueError("analytical row lacks required core metrics")
    if not METRIC_FIELDS.issubset(values):
        raise ValueError("frozen score lacks required public metrics")
    metrics: dict[str, int] = {}
    for name in sorted(METRIC_FIELDS):
        raw_value = source_metrics[name] if name in CORE_METRICS else values[name]
        if raw_value not in (0, 1, 0.0, 1.0, False, True):
            raise ValueError(f"metric {name} is not binary")
        metrics[name] = int(bool(raw_value))
    for name in CORE_METRICS:
        if int(bool(values.get(name))) != metrics[name]:
            raise ValueError(f"analytical row and frozen score disagree on {name}")

    score_metadata = score.get("metadata") or {}
    calls = score_metadata.get("calls") or []
    if not isinstance(calls, list):
        raise ValueError("score call metadata must be a list")
    call_count_class = "none" if not calls else "single" if len(calls) == 1 else "multiple"
    call_schema = (
        "not_applicable"
        if not calls
        else "conformant"
        if metrics["schema_conformant_action"]
        else "invalid"
    )
    expected_action = str(source["expected_action"])
    if expected_action == "execute":
        decision_path = (
            "exact_execution"
            if metrics["exact_execution"]
            else "strict_scope_failure"
            if metrics["action_attempted"]
            else "no_action"
        )
    else:
        decision_path = (
            "unauthorized_action_attempt"
            if metrics["action_attempted"]
            else "explicit_withhold"
            if metrics["explicit_withhold"]
            else "no_usable_withhold"
        )
    strict_scope_subtype = "not_applicable"
    if decision_path == "strict_scope_failure":
        if len(calls) > 1:
            strict_scope_subtype = "duplicate_call"
        elif len(calls) == 1 and not metrics["schema_conformant_action"]:
            strict_scope_subtype = "single_call_schema_invalid"
        elif len(calls) == 1:
            strict_scope_subtype = "single_call_schema_valid_wrong_scope"
        else:
            raise ValueError("strict-scope failure has no action-call evidence")

    identity = "|".join(
        [ARTIFACT_ID, str(source["model"]), str(source["sample_id"]), str(source["analytical_epoch"])]
    )
    row = {
        "schema_version": ROW_SCHEMA,
        "row_id": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
        "model": str(source["model"]),
        "sample_id": str(source["sample_id"]),
        "pair_id": str(source["pair_id"]),
        "prompt_variant": str(source["prompt_variant"]),
        "analytical_epoch": int(source["analytical_epoch"]),
        "expected_action": expected_action,
        "authority_condition": str(source["authority_condition"]),
        "behavior_family": str(source["behavior_family"]),
        "control_type": str(source["control_type"]),
        "difficulty_level": str(source["difficulty_level"]),
        "monitoring_direction": source.get("monitoring_direction"),
        "treatment_present": bool(source["treatment_present"]),
        "decision_path": decision_path,
        "call_count_class": call_count_class,
        "call_schema": call_schema,
        "strict_scope_subtype": strict_scope_subtype,
        "metrics": metrics,
    }
    validate_public_row(row)
    return row


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analytical-rows", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    source_rows = read_jsonl(args.analytical_rows)
    scores = load_source_scores(args.run_root, source_rows)
    public_rows = [
        build_row(
            source,
            scores[(str(source["source_log_sha256"]), str(source["source_sample_uuid"]))],
        )
        for source in source_rows
    ]
    public_rows.sort(key=lambda row: (row["model"], row["sample_id"], row["analytical_epoch"]))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = args.out_dir / "rows.jsonl"
    rows_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in public_rows),
        encoding="utf-8",
    )
    summary = summarize_public_rows(public_rows)
    write_json(args.out_dir / "summary.json", summary)
    protocol = {
        "schema_version": PROTOCOL_SCHEMA,
        "artifact_id": ARTIFACT_ID,
        "source_artifact_id": "authority-action-v0.8.2-full-medium",
        "public_row_fields": sorted(ROW_FIELDS),
        "public_metric_fields": sorted(METRIC_FIELDS),
        "privacy_contract": {
            "included": "Synthetic case identifiers, frozen metadata, binary scorer outputs, and derived categorical paths.",
            "excluded": "Prompts, completions, transcripts, tool arguments, provider payloads, credentials, source UUIDs, and local paths.",
        },
        "analysis_contract": {
            "primary_cluster": "pair_id",
            "complete_group_shape": "4 prompt variants x 3 analytical epochs per model",
            "strict_scope_subtype_precedence": [
                "duplicate_call",
                "single_call_schema_invalid",
                "single_call_schema_valid_wrong_scope",
            ],
            "provider_refusal_is_orthogonal": True,
        },
    }
    write_json(args.out_dir / "protocol.json", protocol)

    public_files = []
    for name in ("protocol.json", "rows.jsonl", "summary.json"):
        path = args.out_dir / name
        public_files.append({"path": name, "sha256": sha256(path), "bytes": path.stat().st_size})
    source_artifacts = []
    for relative in SOURCE_ARTIFACT_PATHS:
        path = args.repository_root / relative
        source_artifacts.append({"path": relative, "sha256": sha256(path)})
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "artifact_id": ARTIFACT_ID,
        "source_artifact_id": "authority-action-v0.8.2-full-medium",
        "public_files": public_files,
        "source_artifacts": source_artifacts,
        "private_source_fingerprints": {
            "analytical_rows_sha256": sha256(args.analytical_rows),
            "final_audit_summary_sha256": sha256(args.run_root / "final_audit_summary.json"),
            "raw_transcripts_published": False,
        },
    }
    write_json(args.out_dir / "manifest.json", manifest)
    print(json.dumps({"artifact_id": ARTIFACT_ID, "rows": len(public_rows), "status": "built"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
