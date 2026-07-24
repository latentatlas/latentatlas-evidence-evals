"""Verify the aggregate-only LatentAtlas frozen-review artifact."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA = "latentatlas_public_frozen_masked_review_manifest_v1"
SUMMARY_SCHEMA = "latentatlas_public_frozen_masked_review_summary_v1"
EXPECTED_OUTCOMES = {
    "packet_supported_block",
    "packet_unsupported_block",
    "insufficient_evidence",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


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


def _as_nonnegative_int(value: Any, label: str, failures: list[str]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        failures.append(f"{label} must be a non-negative integer")
        return None
    return value


def verify_frozen_review_artifact(artifact_dir: Path) -> dict[str, Any]:
    """Return a deterministic integrity report for a public frozen-review directory."""
    artifact_dir = artifact_dir.resolve()
    manifest_path = artifact_dir / "manifest.json"
    summary_path = artifact_dir / "summary.json"
    outcomes_path = artifact_dir / "outcomes.csv"
    failures: list[str] = []

    try:
        manifest = _read_json_object(manifest_path)
        summary = _read_json_object(summary_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "artifact_id": None,
            "failure_reasons": [str(error)],
            "files_verified": 0,
            "status": "fail",
        }

    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        failures.append("unexpected manifest schema_version")
    if summary.get("schema_version") != SUMMARY_SCHEMA:
        failures.append("unexpected summary schema_version")
    if manifest.get("artifact_id") != summary.get("artifact_id"):
        failures.append("manifest and summary artifact_id values differ")
    if manifest.get("source_snapshot") != summary.get("source_snapshot"):
        failures.append("manifest and summary source_snapshot values differ")

    source_snapshot = summary.get("source_snapshot")
    if not isinstance(source_snapshot, dict):
        failures.append("summary source_snapshot must be an object")
    elif not SHA256_PATTERN.fullmatch(str(source_snapshot.get("masked_rows_sha256", ""))):
        failures.append("source masked_rows_sha256 must be a lowercase SHA-256 digest")

    files_verified = 0
    listed_files = manifest.get("public_files")
    if not isinstance(listed_files, list):
        failures.append("manifest public_files must be a list")
        listed_files = []
    listed_paths = {
        str(item.get("path", ""))
        for item in listed_files
        if isinstance(item, dict)
    }
    if listed_paths != {"summary.json", "outcomes.csv"}:
        failures.append("manifest must list exactly summary.json and outcomes.csv")
    for item in listed_files:
        if not isinstance(item, dict):
            failures.append("each public_files entry must be an object")
            continue
        relative = Path(str(item.get("path", "")))
        if relative.is_absolute() or ".." in relative.parts or relative.name == "manifest.json":
            failures.append(f"unsafe or unsupported public file path: {relative}")
            continue
        path = artifact_dir / relative
        if not path.is_file():
            failures.append(f"missing public file: {relative}")
            continue
        file_valid = True
        if _sha256(path) != item.get("sha256"):
            failures.append(f"SHA-256 mismatch: {relative}")
            file_valid = False
        if path.stat().st_size != item.get("bytes"):
            failures.append(f"byte-size mismatch: {relative}")
            file_valid = False
        if file_valid:
            files_verified += 1

    selection = summary.get("selection")
    if not isinstance(selection, dict):
        failures.append("summary selection must be an object")
        selection = {}
    selection_values = {
        key: _as_nonnegative_int(selection.get(key), f"selection.{key}", failures)
        for key in (
            "high_priority_packets",
            "outcome_ready_packets",
            "not_outcome_ready_packets",
            "reviewed_outcome_ready_packets",
            "unreviewed_outcome_ready_packets",
        )
    }
    if all(value is not None for value in selection_values.values()):
        if selection_values["high_priority_packets"] != (
            selection_values["outcome_ready_packets"] + selection_values["not_outcome_ready_packets"]
        ):
            failures.append("high-priority selection counts do not reconcile")
        if selection_values["outcome_ready_packets"] != (
            selection_values["reviewed_outcome_ready_packets"]
            + selection_values["unreviewed_outcome_ready_packets"]
        ):
            failures.append("outcome-ready review counts do not reconcile")

    json_outcomes = summary.get("outcomes")
    if not isinstance(json_outcomes, list):
        failures.append("summary outcomes must be a list")
        json_outcomes = []
    json_by_outcome: dict[str, dict[str, Any]] = {}
    for row in json_outcomes:
        if not isinstance(row, dict):
            failures.append("each summary outcome must be an object")
            continue
        outcome = str(row.get("outcome", ""))
        if outcome in json_by_outcome:
            failures.append(f"duplicate summary outcome: {outcome}")
        json_by_outcome[outcome] = row
    if set(json_by_outcome) != EXPECTED_OUTCOMES:
        failures.append("summary outcome taxonomy is incomplete or unexpected")

    try:
        with outcomes_path.open(newline="", encoding="utf-8") as handle:
            csv_rows = list(csv.DictReader(handle))
    except OSError as error:
        failures.append(str(error))
        csv_rows = []
    csv_by_outcome = {row.get("outcome", ""): row for row in csv_rows}
    if len(csv_by_outcome) != len(csv_rows):
        failures.append("outcomes.csv contains duplicate outcome rows")
    if set(csv_by_outcome) != EXPECTED_OUTCOMES:
        failures.append("outcomes.csv taxonomy is incomplete or unexpected")

    outcome_total = 0
    for outcome in sorted(EXPECTED_OUTCOMES):
        json_row = json_by_outcome.get(outcome)
        csv_row = csv_by_outcome.get(outcome)
        if not json_row or not csv_row:
            continue
        count = _as_nonnegative_int(json_row.get("count"), f"outcomes.{outcome}.count", failures)
        denominator = _as_nonnegative_int(
            json_row.get("denominator"), f"outcomes.{outcome}.denominator", failures
        )
        try:
            csv_count = int(csv_row["count"])
            csv_denominator = int(csv_row["denominator"])
            csv_rate = float(csv_row["rate"])
            json_rate = float(json_row["rate"])
        except (KeyError, TypeError, ValueError):
            failures.append(f"invalid numeric value for outcome: {outcome}")
            continue
        if count != csv_count or denominator != csv_denominator or json_rate != csv_rate:
            failures.append(f"CSV and JSON values differ for outcome: {outcome}")
        if count is not None and denominator is not None:
            outcome_total += count
            if denominator == 0 or round(count / denominator, 4) != json_rate:
                failures.append(f"rate does not match count and denominator for outcome: {outcome}")

    reviewed = selection_values.get("reviewed_outcome_ready_packets")
    if reviewed is not None and outcome_total != reviewed:
        failures.append("outcome counts do not sum to reviewed outcome-ready packets")
    checks = summary.get("checks")
    if not isinstance(checks, dict):
        failures.append("summary checks must be an object")
        checks = {}
    if checks.get("outcome_count_total") != outcome_total:
        failures.append("checks.outcome_count_total does not match outcome counts")
    resolved = sum(
        int(json_by_outcome.get(outcome, {}).get("count", 0))
        for outcome in ("packet_supported_block", "packet_unsupported_block")
    )
    if checks.get("resolved_outcome_count") != resolved:
        failures.append("checks.resolved_outcome_count does not match resolved outcomes")

    data_handling = summary.get("data_handling")
    if not isinstance(data_handling, dict) or data_handling.get("release_level") != "aggregate_only":
        failures.append("summary must declare an aggregate_only release level")
    for field in ("contains_customer_data", "contains_personal_data", "contains_row_level_records"):
        if not isinstance(data_handling, dict) or data_handling.get(field) is not False:
            failures.append(f"summary must declare {field}=false")
    manifest_data_handling = manifest.get("data_handling")
    if (
        not isinstance(manifest_data_handling, dict)
        or manifest_data_handling.get("release_level") != "aggregate_only"
    ):
        failures.append("manifest must declare an aggregate_only release level")

    return {
        "artifact_id": summary.get("artifact_id"),
        "failure_reasons": failures,
        "files_verified": files_verified,
        "outcome_count": outcome_total,
        "source_freeze_id": source_snapshot.get("freeze_id") if isinstance(source_snapshot, dict) else None,
        "status": "pass" if not failures else "fail",
    }
