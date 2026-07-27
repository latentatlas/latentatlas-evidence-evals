"""Verify the aggregate-only Authority-to-Action v0.8 review artifact."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA = "latentatlas_public_authority_action_review_manifest_v0.8"
SUMMARY_SCHEMA = "latentatlas_public_authority_action_review_summary_v0.8"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_SOURCE_PATHS = {
    "docs/authority-action-internal-blind-review-v0-8.md",
    "evals/authority_action_internal_review.py",
    "evals/data/authority_action_cases_v0_6.jsonl",
    "evals/experiment_manifest_v0_8.json",
    "scripts/run_authority_internal_review.py",
}
EXPECTED_LOCAL_EVIDENCE = {
    "answer_key",
    "review_analysis",
    "review_packet",
    "review_responses",
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


def verify_authority_action_review_artifact(
    artifact_dir: Path,
    *,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic integrity report for the public v0.8 review."""

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

    public_files = manifest.get("public_files")
    if not isinstance(public_files, list):
        failures.append("manifest public_files must be a list")
        public_files = []
    public_paths = {
        str(item.get("path", "")) for item in public_files if isinstance(item, dict)
    }
    if public_paths != {"summary.json"}:
        failures.append("manifest must list exactly summary.json as a public file")
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

    evidence = manifest.get("local_review_evidence_fingerprints")
    if not isinstance(evidence, list):
        failures.append("manifest local_review_evidence_fingerprints must be a list")
        evidence = []
    evidence_ids = {
        str(item.get("id", "")) for item in evidence if isinstance(item, dict)
    }
    if evidence_ids != EXPECTED_LOCAL_EVIDENCE:
        failures.append("review evidence fingerprints are incomplete or unexpected")
    for item in evidence:
        if not isinstance(item, dict):
            failures.append("each review evidence fingerprint must be an object")
            continue
        if not SHA256_PATTERN.fullmatch(str(item.get("sha256", ""))):
            failures.append(f"invalid review evidence SHA-256: {item.get('id')}")
        if item.get("published") is not False:
            failures.append(f"review evidence must remain unpublished: {item.get('id')}")

    review = summary.get("review")
    if not isinstance(review, dict):
        failures.append("summary review must be an object")
        review = {}
    if review.get("review_type") != "internal_blind_author_review":
        failures.append("review type must remain internal_blind_author_review")
    expected_review_values = {
        "reviewed_cases": 100,
        "action_agreement_count": 100,
        "adjudication_required_count": 0,
        "evidence_sufficient_yes_count": 100,
        "single_decision_clear_yes_count": 100,
    }
    for field, expected in expected_review_values.items():
        if review.get(field) != expected:
            failures.append(f"unexpected review value for {field}")
    if review.get("action_agreement_rate") != 1.0:
        failures.append("action agreement rate must be 1.0")
    if review.get("issue_code_counts") != {"none": 100}:
        failures.append("issue-code counts must record 100 none judgments")

    gate = summary.get("quality_gate")
    if not isinstance(gate, dict):
        failures.append("summary quality_gate must be an object")
        gate = {}
    if gate.get("status") != "ready_to_freeze_successor":
        failures.append("review quality gate is not ready_to_freeze_successor")
    if gate.get("internal_blind_review_complete") is not True:
        failures.append("internal blind review must be complete")
    if gate.get("independent_review_complete") is not False:
        failures.append("independent review must not be represented as complete")
    if gate.get("full_run_enabled") is not False:
        failures.append("full run must remain disabled in the review artifact")

    budget = summary.get("budget_review")
    if not isinstance(budget, dict):
        failures.append("summary budget_review must be an object")
        budget = {}
    if budget.get("planned_sample_runs") != 600:
        failures.append("budget plan must cover 600 sample runs")
    if budget.get("projected_cost_from_v0_7_pilot_usd") != 8.19200625:
        failures.append("unexpected pilot-based projected full-run cost")
    if budget.get("hard_ceiling_cost_usd") != 22.5:
        failures.append("unexpected hard-ceiling full-run cost")
    if budget.get("live_provider_credit_verified") is not False:
        failures.append("live provider credit must remain unverified")

    handling = summary.get("data_handling")
    if not isinstance(handling, dict):
        failures.append("summary data_handling must be an object")
        handling = {}
    if handling.get("release_level") != "aggregate_only":
        failures.append("review release must remain aggregate-only")
    for field in (
        "contains_case_prompts",
        "contains_credentials",
        "contains_customer_data",
        "contains_personal_data",
        "contains_reviewer_rationales",
    ):
        if handling.get(field) is not False:
            failures.append(f"aggregate review must record {field}=false")

    return {
        "artifact_id": summary.get("artifact_id"),
        "failure_reasons": failures,
        "public_files_verified": public_files_verified,
        "reviewed_cases": review.get("reviewed_cases"),
        "source_files_verified": source_files_verified,
        "status": "pass" if not failures else "fail",
    }
