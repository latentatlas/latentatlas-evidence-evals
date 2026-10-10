"""Verify the aggregate-only Authority-to-Action v0.8.2 full result."""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA = "latentatlas_public_authority_action_full_medium_manifest_v0.8.2"
SUMMARY_SCHEMA = "latentatlas_public_authority_action_full_medium_summary_v0.8.2"
PROTOCOL_SCHEMA = "latentatlas_public_authority_action_protocol_v0.8.2"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_SOURCE_PATHS = {
    "evals/analyze_authority_results.py",
    "evals/authority_action_eval_v0_7.py",
    "evals/data/authority_action_cases_v0_6.jsonl",
}
EXPECTED_LOCAL_EVIDENCE = {
    "aggregate_json",
    "aggregate_markdown",
    "analytical_rows",
    "final_audit_summary",
    "repair_plan_batch02_anthropic",
    "repair_plan_batch03_anthropic",
    "repair_plan_batch05_anthropic",
    "result_manifest",
}
EXPECTED_RESULTS = {
    "openai/gpt-5.6-sol": {
        "sample_runs": 300,
        "correct_decisions": 300,
        "usable_decisions": 294,
        "execute_runs": 150,
        "exact_executions": 150,
        "malformed_or_wrong_scope_execute_attempts": 0,
        "execute_no_action_outcomes": 0,
        "withhold_runs": 150,
        "explicit_withholds": 150,
        "unauthorized_withhold_action_attempts": 0,
        "strict_scope_failures": 0,
        "provider_refusals": 0,
    },
    "anthropic/claude-fable-5": {
        "sample_runs": 300,
        "correct_decisions": 249,
        "usable_decisions": 205,
        "execute_runs": 150,
        "exact_executions": 99,
        "malformed_or_wrong_scope_execute_attempts": 26,
        "execute_no_action_outcomes": 25,
        "withhold_runs": 150,
        "explicit_withholds": 133,
        "unauthorized_withhold_action_attempts": 0,
        "strict_scope_failures": 26,
        "provider_refusals": 38,
    },
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


def _decimal(value: Any, label: str, failures: list[str]) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        failures.append(f"{label} must be numeric")
        return None


def verify_authority_action_full_result_artifact(
    artifact_dir: Path,
    *,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic integrity report for the public v0.8.2 result."""

    artifact_dir = artifact_dir.resolve()
    repository_root = (
        repository_root.resolve() if repository_root is not None else artifact_dir.parents[1]
    )
    failures: list[str] = []

    try:
        manifest = _read_json_object(artifact_dir / "manifest.json")
        summary = _read_json_object(artifact_dir / "summary.json")
        protocol_document = _read_json_object(artifact_dir / "protocol.json")
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
    if protocol_document.get("schema_version") != PROTOCOL_SCHEMA:
        failures.append("unexpected protocol schema_version")
    for field in ("artifact_id", "experiment_id"):
        if manifest.get(field) != summary.get(field):
            failures.append(f"manifest and summary {field} values differ")
        if protocol_document.get(field) != summary.get(field):
            failures.append(f"protocol and summary {field} values differ")

    public_files = manifest.get("public_files")
    if not isinstance(public_files, list):
        failures.append("manifest public_files must be a list")
        public_files = []
    public_paths = {
        str(item.get("path", "")) for item in public_files if isinstance(item, dict)
    }
    if public_paths != {"protocol.json", "summary.json"}:
        failures.append("manifest must list exactly protocol.json and summary.json")
    public_files_verified = 0
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
    source_files_verified = 0
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
    if evidence_ids != EXPECTED_LOCAL_EVIDENCE:
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
    expected_scope = {
        "synthetic_case_count": 100,
        "complete_factorial_group_count": 25,
        "model_count": 2,
        "epochs_per_case_and_model": 3,
        "planned_analytical_runs": 600,
        "completed_analytical_runs": 600,
        "gross_provider_attempts": 603,
        "verified_provider_batch_checkpoints": 10,
    }
    for field, expected in expected_scope.items():
        if scope.get(field) != expected:
            failures.append(f"unexpected scope value for {field}")
    if scope.get("stage") != "full_medium" or scope.get("reasoning_effort") != "medium":
        failures.append("scope must identify the full medium condition")

    protocol_execution = protocol_document.get("execution")
    if not isinstance(protocol_execution, dict):
        failures.append("protocol execution must be an object")
        protocol_execution = {}
    for field in (
        "planned_analytical_runs",
        "completed_analytical_runs",
        "gross_provider_attempts",
    ):
        if protocol_execution.get(field) != scope.get(field):
            failures.append(f"protocol and summary {field} values differ")
    if protocol_execution.get("external_side_effects") is not False:
        failures.append("protocol must declare external_side_effects=false")

    protocol_hashes = protocol_document.get("public_source_hashes")
    if not isinstance(protocol_hashes, dict):
        failures.append("protocol public_source_hashes must be an object")
        protocol_hashes = {}
    manifest_source_hashes = {
        str(item.get("path")): str(item.get("sha256"))
        for item in source_artifacts
        if isinstance(item, dict)
    }
    if protocol_hashes != manifest_source_hashes:
        failures.append("protocol and manifest source hashes differ")

    protocol = summary.get("protocol_audit")
    if not isinstance(protocol, dict):
        failures.append("summary protocol_audit must be an object")
        protocol = {}
    expected_protocol = {
        "analytical_protocol_complete_runs": 600,
        "protocol_interrupted_original_attempts": 3,
        "one_for_one_replacement_attempts": 3,
        "protocol_interrupted_rows_in_analytical_set": 0,
    }
    for field, expected in expected_protocol.items():
        if protocol.get(field) != expected:
            failures.append(f"unexpected protocol value for {field}")
    if protocol.get("original_interrupted_attempts_retained_in_local_audit") is not True:
        failures.append("original interrupted attempts must remain in the local audit")
    if protocol.get("repair_attempts_selected_by_score") is not False:
        failures.append("repair selection must remain independent of score")

    results = summary.get("results")
    if not isinstance(results, list):
        failures.append("summary results must be a list")
        results = []
    result_map = {
        str(item.get("model")): item for item in results if isinstance(item, dict)
    }
    if set(result_map) != set(EXPECTED_RESULTS):
        failures.append("summary model set is incomplete or unexpected")
    analytical_cost = Decimal("0")
    gross_cost = Decimal("0")
    for model, expected_result in EXPECTED_RESULTS.items():
        result = result_map.get(model, {})
        for field, expected in expected_result.items():
            if result.get(field) != expected:
                failures.append(f"unexpected {field} for {model}")
        if result.get("execute_runs") != (
            result.get("exact_executions", 0)
            + result.get("malformed_or_wrong_scope_execute_attempts", 0)
            + result.get("execute_no_action_outcomes", 0)
        ):
            failures.append(f"execute paths do not reconcile for {model}")
        for field, accumulator in (
            ("analytical_cost_usd", "analytical"),
            ("gross_cost_usd", "gross"),
        ):
            value = _decimal(result.get(field), f"{model} {field}", failures)
            if value is not None:
                if accumulator == "analytical":
                    analytical_cost += value
                else:
                    gross_cost += value

    repairs = summary.get("repairs")
    if not isinstance(repairs, list) or len(repairs) != 3:
        failures.append("summary must record exactly three protocol repairs")
        repairs = []
    repair_cost = Decimal("0")
    for repair in repairs:
        if not isinstance(repair, dict):
            failures.append("each repair must be an object")
            continue
        value = _decimal(repair.get("overhead_cost_usd"), "repair overhead", failures)
        if value is not None:
            repair_cost += value
        if repair.get("observed_output_tokens", 0) <= repair.get(
            "frozen_output_token_limit", 0
        ):
            failures.append("repair trigger must exceed the frozen output-token limit")

    cost = summary.get("cost")
    if not isinstance(cost, dict):
        failures.append("summary cost must be an object")
        cost = {}
    reported_gross = _decimal(cost.get("gross_total_usd"), "gross total", failures)
    reported_analytical = _decimal(
        cost.get("analytical_set_total_usd"), "analytical total", failures
    )
    reported_overhead = _decimal(
        cost.get("protocol_repair_overhead_usd"), "repair overhead total", failures
    )
    hard_ceiling = _decimal(cost.get("hard_ceiling_usd"), "hard ceiling", failures)
    if reported_gross is not None and reported_gross != gross_cost:
        failures.append("model gross costs do not sum to the reported gross total")
    if reported_analytical is not None and reported_analytical != analytical_cost:
        failures.append("model analytical costs do not sum to the reported analytical total")
    if reported_overhead is not None and reported_overhead != repair_cost:
        failures.append("repair costs do not sum to the reported overhead")
    if None not in (reported_gross, reported_analytical, reported_overhead):
        if reported_gross - reported_analytical != reported_overhead:
            failures.append("gross, analytical, and repair costs do not reconcile")
    if reported_gross is not None and hard_ceiling is not None and reported_gross > hard_ceiling:
        failures.append("gross cost exceeds the frozen hard ceiling")

    review = summary.get("review")
    if not isinstance(review, dict):
        failures.append("summary review must be an object")
        review = {}
    if review.get("review_type") != "internal_blind_author_review":
        failures.append("review type must remain internal_blind_author_review")
    if review.get("independent_external_review_complete") is not False:
        failures.append("independent external review must not be represented as complete")

    handling = summary.get("data_handling")
    if not isinstance(handling, dict) or handling.get("release_level") != "aggregate_only":
        failures.append("summary must declare an aggregate_only release level")
        handling = {}
    for field in (
        "contains_raw_transcripts",
        "contains_prompts",
        "contains_completions",
        "contains_provider_payloads",
        "contains_credentials",
        "contains_live_credit_snapshots",
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

    protocol_release = protocol_document.get("release")
    if (
        not isinstance(protocol_release, dict)
        or protocol_release.get("level") != "aggregate_only"
    ):
        failures.append("protocol must declare an aggregate_only release level")
        protocol_release = {}
    for field in (
        "raw_transcripts_published",
        "provider_payloads_published",
        "row_level_records_published",
        "credentials_published",
        "live_credit_snapshots_published",
    ):
        if protocol_release.get(field) is not False:
            failures.append(f"protocol must declare {field}=false")

    return {
        "artifact_id": summary.get("artifact_id"),
        "completed_analytical_runs": scope.get("completed_analytical_runs"),
        "failure_reasons": failures,
        "public_files_verified": public_files_verified,
        "source_files_verified": source_files_verified,
        "status": "pass" if not failures else "fail",
    }
