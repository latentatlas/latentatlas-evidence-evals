"""Verify the aggregate-only Authority-to-Action v0.7 pilot artifact."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA = "latentatlas_public_authority_action_pilot_manifest_v0.7"
SUMMARY_SCHEMA = "latentatlas_public_authority_action_pilot_summary_v0.7"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_SOURCE_PATHS = {
    "evals/analyze_authority_results.py",
    "evals/authority_action_eval_v0_7.py",
    "evals/data/authority_action_cases_v0_6.jsonl",
    "evals/experiment_manifest_v0_7.json",
}
EXPECTED_MODELS = {"anthropic/claude-fable-5", "openai/gpt-5.6-sol"}
EXPECTED_RUN_EVIDENCE = {
    "aggregate_json",
    "anthropic_raw_log",
    "openai_raw_log",
    "run_manifest",
}


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(value: Any) -> Path | None:
    relative = Path(str(value))
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        return None
    return relative


def _nonnegative_int(value: Any, label: str, failures: list[str]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        failures.append(f"{label} must be a non-negative integer")
        return None
    return value


def verify_authority_action_pilot_artifact(
    artifact_dir: Path,
    *,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic integrity report for the public v0.7 pilot."""
    artifact_dir = artifact_dir.resolve()
    repository_root = (
        repository_root.resolve() if repository_root is not None else artifact_dir.parents[1]
    )
    failures: list[str] = []

    try:
        manifest = _read_json_object(artifact_dir / "manifest.json")
        summary = _read_json_object(artifact_dir / "summary.json")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "artifact_id": None,
            "failure_reasons": [str(error)],
            "public_files_verified": 0,
            "source_files_verified": 0,
            "status": "fail",
        }

    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        failures.append("unexpected manifest schema_version")
    if summary.get("schema_version") != SUMMARY_SCHEMA:
        failures.append("unexpected summary schema_version")
    for field in ("artifact_id", "experiment_id"):
        if manifest.get(field) != summary.get(field):
            failures.append(f"manifest and summary {field} values differ")

    public_files_verified = 0
    public_files = manifest.get("public_files")
    if not isinstance(public_files, list):
        failures.append("manifest public_files must be a list")
        public_files = []
    public_paths = {
        str(item.get("path", "")) for item in public_files if isinstance(item, dict)
    }
    if public_paths != {"summary.json"}:
        failures.append("manifest must list exactly summary.json as a public file")
    for item in public_files:
        if not isinstance(item, dict):
            failures.append("each public_files entry must be an object")
            continue
        relative = _safe_relative_path(item.get("path"))
        if relative is None or relative.name == "manifest.json":
            failures.append("unsafe or unsupported public file path")
            continue
        public_path = artifact_dir / relative
        if not public_path.is_file():
            failures.append(f"missing public file: {relative}")
            continue
        valid = True
        if _sha256(public_path) != item.get("sha256"):
            failures.append(f"SHA-256 mismatch: {relative}")
            valid = False
        if public_path.stat().st_size != item.get("bytes"):
            failures.append(f"byte-size mismatch: {relative}")
            valid = False
        if valid:
            public_files_verified += 1

    source_files_verified = 0
    source_artifacts = manifest.get("source_artifacts")
    if not isinstance(source_artifacts, list):
        failures.append("manifest source_artifacts must be a list")
        source_artifacts = []
    source_paths = {
        str(item.get("path", ""))
        for item in source_artifacts
        if isinstance(item, dict)
    }
    if source_paths != EXPECTED_SOURCE_PATHS:
        failures.append("manifest source_artifacts are incomplete or unexpected")
    for item in source_artifacts:
        if not isinstance(item, dict):
            failures.append("each source_artifacts entry must be an object")
            continue
        relative = _safe_relative_path(item.get("path"))
        if relative is None:
            failures.append("unsafe source artifact path")
            continue
        source_path = repository_root / relative
        if not source_path.is_file():
            failures.append(f"missing source artifact: {relative}")
            continue
        if _sha256(source_path) != item.get("sha256"):
            failures.append(f"source SHA-256 mismatch: {relative}")
            continue
        source_files_verified += 1

    evidence = manifest.get("local_run_evidence_fingerprints")
    if not isinstance(evidence, list):
        failures.append("manifest local_run_evidence_fingerprints must be a list")
        evidence = []
    evidence_ids = {
        str(item.get("id", "")) for item in evidence if isinstance(item, dict)
    }
    if evidence_ids != EXPECTED_RUN_EVIDENCE:
        failures.append("run evidence fingerprints are incomplete or unexpected")
    for item in evidence:
        if not isinstance(item, dict):
            failures.append("each run evidence fingerprint must be an object")
            continue
        if not SHA256_PATTERN.fullmatch(str(item.get("sha256", ""))):
            failures.append(f"invalid run evidence SHA-256: {item.get('id')}")
        if item.get("published") is not False:
            failures.append(f"run evidence must remain unpublished: {item.get('id')}")

    scope = summary.get("scope")
    if not isinstance(scope, dict):
        failures.append("summary scope must be an object")
        scope = {}
    planned = _nonnegative_int(scope.get("planned_sample_runs"), "planned runs", failures)
    completed = _nonnegative_int(
        scope.get("completed_sample_runs"), "completed runs", failures
    )
    if planned != 80 or completed != 80:
        failures.append("pilot must record 80 planned and completed runs")
    if scope.get("full_stage_enabled") is not False:
        failures.append("full stage must remain disabled")

    protocol = summary.get("protocol_audit")
    if not isinstance(protocol, dict):
        failures.append("summary protocol_audit must be an object")
        protocol = {}
    if protocol.get("protocol_complete_runs") != completed:
        failures.append("protocol-complete count must match completed runs")
    for field in (
        "protocol_interrupted_runs",
        "cost_limit_exceeded",
        "token_limit_exceeded",
        "other_sample_limit",
    ):
        if protocol.get(field) != 0:
            failures.append(f"protocol_audit.{field} must equal zero")

    results = summary.get("results")
    if not isinstance(results, list):
        failures.append("summary results must be a list")
        results = []
    result_models = {
        str(item.get("model", "")) for item in results if isinstance(item, dict)
    }
    if result_models != EXPECTED_MODELS:
        failures.append("summary model set is incomplete or unexpected")
    result_run_total = 0
    result_cost_total = Decimal("0")
    for item in results:
        if not isinstance(item, dict):
            failures.append("each result must be an object")
            continue
        runs = _nonnegative_int(item.get("sample_runs"), "result sample_runs", failures)
        if runs is not None:
            result_run_total += runs
        execute_runs = item.get("execute_runs")
        withhold_runs = item.get("withhold_runs")
        if execute_runs != 20 or withhold_runs != 20:
            failures.append(f"unexpected decision balance for {item.get('model')}")
        if item.get("unauthorized_withhold_action_attempts") != 0:
            failures.append(f"unexpected unauthorized withhold action for {item.get('model')}")
        try:
            result_cost_total += Decimal(str(item.get("calculated_cost_usd")))
        except (InvalidOperation, TypeError, ValueError):
            failures.append(f"invalid calculated cost for {item.get('model')}")
    if result_run_total != completed:
        failures.append("result sample runs do not reconcile with completed runs")

    cost = summary.get("cost")
    if not isinstance(cost, dict):
        failures.append("summary cost must be an object")
        cost = {}
    try:
        reported_total = Decimal(str(cost.get("calculated_total_usd")))
        ceiling = Decimal(str(cost.get("frozen_pilot_ceiling_usd")))
        if reported_total != result_cost_total:
            failures.append("model costs do not sum to calculated total")
        if reported_total > ceiling:
            failures.append("calculated total exceeds frozen pilot ceiling")
    except (InvalidOperation, TypeError, ValueError):
        failures.append("summary cost values must be numeric")

    handling = summary.get("data_handling")
    if not isinstance(handling, dict) or handling.get("release_level") != "aggregate_only":
        failures.append("summary must declare an aggregate_only release level")
        handling = {}
    for field in (
        "contains_prompts",
        "contains_completions",
        "contains_provider_payloads",
        "contains_credentials",
        "contains_customer_data",
        "contains_personal_data",
        "contains_row_level_records",
    ):
        if handling.get(field) is not False:
            failures.append(f"summary must declare {field}=false")

    manifest_handling = manifest.get("data_handling")
    if (
        not isinstance(manifest_handling, dict)
        or manifest_handling.get("release_level") != "aggregate_only"
    ):
        failures.append("manifest must declare an aggregate_only release level")

    return {
        "artifact_id": summary.get("artifact_id"),
        "completed_sample_runs": completed,
        "failure_reasons": failures,
        "public_files_verified": public_files_verified,
        "source_files_verified": source_files_verified,
        "status": "pass" if not failures else "fail",
    }
