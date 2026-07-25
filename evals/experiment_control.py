"""Frozen experiment verification for the authority-to-action evaluation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_1.json")
V0_2_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_2.json")
DEFAULT_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_3.json")


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
        "authority_action_experiment_v0.3",
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

    dataset = manifest["dataset"]
    if "paths" in dataset:
        dataset_paths = [str(path) for path in dataset["paths"]]
    else:
        dataset_paths = [str(dataset["path"])]
    if not dataset_paths:
        raise ValueError("Frozen dataset must contain at least one path")
    if len(dataset_paths) != len(set(dataset_paths)):
        raise ValueError("Frozen dataset paths must be unique")

    rows = []
    for relative_path in dataset_paths:
        if relative_path not in artifacts:
            raise ValueError("Every dataset path must be a frozen artifact")
        dataset_path = REPO_ROOT / relative_path
        rows.extend(
            json.loads(line)
            for line in dataset_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    ids = [str(row["id"]) for row in rows]
    if len(rows) != int(dataset["sample_count"]):
        raise ValueError("Frozen dataset sample count mismatch")
    if len(ids) != len(set(ids)):
        raise ValueError("Frozen dataset contains duplicate sample IDs")

    expected_action_counts = {
        "execute": int(dataset["expected_execute"]),
        "withhold": int(dataset["expected_withhold"]),
    }
    actual_action_counts = {
        action: sum(
            1
            for row in rows
            if row.get("metadata", {}).get("expected_action") == action
        )
        for action in expected_action_counts
    }
    if actual_action_counts != expected_action_counts:
        raise ValueError(
            "Frozen dataset expected-action counts mismatch: "
            f"expected {expected_action_counts}, got {actual_action_counts}"
        )

    pilot_ids = list(manifest["stages"]["pilot"]["sample_ids"])
    missing_pilot_ids = sorted(set(pilot_ids) - set(ids))
    if missing_pilot_ids:
        raise ValueError(f"Pilot IDs missing from dataset: {missing_pilot_ids}")

    for pair in dataset.get("paired_diagnostics", []):
        required_pair_fields = {
            "pair_id",
            "pressure_sample_id",
            "neutral_sample_id",
            "domain_positive_control_id",
        }
        if not isinstance(pair, Mapping):
            raise ValueError("Paired diagnostic definitions must be objects")
        missing_pair_fields = sorted(required_pair_fields - pair.keys())
        if missing_pair_fields:
            raise ValueError(
                f"Paired diagnostic is missing fields: {missing_pair_fields}"
            )
        pair_sample_ids = {
            str(pair["pressure_sample_id"]),
            str(pair["neutral_sample_id"]),
            str(pair["domain_positive_control_id"]),
        }
        if len(pair_sample_ids) != 3:
            raise ValueError("Paired diagnostic sample IDs must be distinct")
        missing_pair_ids = sorted(pair_sample_ids - set(ids))
        if missing_pair_ids:
            raise ValueError(
                f"Paired diagnostic IDs missing from dataset: {missing_pair_ids}"
            )
        missing_pair_pilot_ids = sorted(pair_sample_ids - set(pilot_ids))
        if missing_pair_pilot_ids:
            raise ValueError(
                "Paired diagnostic IDs missing from pilot: "
                f"{missing_pair_pilot_ids}"
            )

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

    if len(dataset_paths) == 1:
        dataset_digest = str(artifacts[dataset_paths[0]])
    else:
        digest_payload = "\n".join(
            f"{relative_path}:{artifacts[relative_path]}"
            for relative_path in dataset_paths
        ).encode("utf-8")
        dataset_digest = hashlib.sha256(digest_payload).hexdigest()

    return {
        "experiment_id": manifest["experiment_id"],
        "dataset_sha256": dataset_digest,
        "sample_count": len(rows),
        "pilot_sample_count": len(pilot_ids),
        "model_count": len(manifest["models"]),
        "task_version": str(
            manifest.get("task", {}).get("version", manifest.get("task_version"))
        ),
        "pricing_as_of": str(pricing["as_of"]),
        "worst_case_full_cost_usd": worst_case_full_cost,
    }
