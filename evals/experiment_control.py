"""Frozen experiment verification for the authority-to-action evaluation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_1.json")
DEFAULT_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_2.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Experiment manifest must be a JSON object")
    return manifest


def verify_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest = load_manifest(path)
    if manifest.get("schema_version") not in {
        "authority_action_experiment_v0.1",
        "authority_action_experiment_v0.2",
    }:
        raise ValueError("Unsupported experiment manifest schema")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, Mapping) or not artifacts:
        raise ValueError("Manifest artifacts must be a non-empty object")
    for relative_path, expected_digest in artifacts.items():
        artifact_path = REPO_ROOT / str(relative_path)
        if not artifact_path.is_file():
            raise FileNotFoundError(artifact_path)
        actual_digest = sha256_file(artifact_path)
        if actual_digest != expected_digest:
            raise ValueError(
                f"Frozen artifact digest mismatch for {relative_path}: "
                f"expected {expected_digest}, got {actual_digest}"
            )

    dataset_path = REPO_ROOT / str(manifest["dataset"]["path"])
    rows = [
        json.loads(line)
        for line in dataset_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ids = [str(row["id"]) for row in rows]
    if len(rows) != int(manifest["dataset"]["sample_count"]):
        raise ValueError("Frozen dataset sample count mismatch")
    if len(ids) != len(set(ids)):
        raise ValueError("Frozen dataset contains duplicate sample IDs")

    pilot_ids = list(manifest["stages"]["pilot"]["sample_ids"])
    missing_pilot_ids = sorted(set(pilot_ids) - set(ids))
    if missing_pilot_ids:
        raise ValueError(f"Pilot IDs missing from dataset: {missing_pilot_ids}")

    per_sample_cost_limit = float(manifest["limits"]["cost_limit_usd_per_sample"])
    pricing = manifest.get("pricing")
    if not isinstance(pricing, Mapping):
        raise ValueError("Manifest pricing must be an object")
    if pricing.get("config_path") not in artifacts:
        raise ValueError("Pricing config must be a frozen artifact")
    full_runs = len(manifest["models"]) * len(rows) * int(
        manifest["stages"]["full"]["epochs"]
    )
    worst_case_full_cost = round(full_runs * per_sample_cost_limit, 2)
    if worst_case_full_cost > float(manifest["limits"]["total_budget_usd"]):
        raise ValueError("Configured per-sample limits exceed the total experiment budget")

    return {
        "experiment_id": manifest["experiment_id"],
        "dataset_sha256": manifest["artifacts"][manifest["dataset"]["path"]],
        "sample_count": len(rows),
        "pilot_sample_count": len(pilot_ids),
        "model_count": len(manifest["models"]),
        "task_version": str(
            manifest.get("task", {}).get("version", manifest.get("task_version"))
        ),
        "pricing_as_of": str(pricing["as_of"]),
        "worst_case_full_cost_usd": worst_case_full_cost,
    }
