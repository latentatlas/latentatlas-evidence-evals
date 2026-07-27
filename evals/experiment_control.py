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
V0_4_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_4.json")
V0_5_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_5.json")
V0_6_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_6.json")
V0_6_1_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_6_1.json")
V0_7_MANIFEST = Path(__file__).with_name("experiment_manifest_v0_7.json")


def provider_cost_limit(
    manifest: Mapping[str, Any], provider: str
) -> float:
    """Resolve a provider-specific cap while preserving legacy manifests."""

    limits = manifest["limits"]
    provider_limits = limits.get("cost_limit_usd_per_sample_by_provider")
    if provider_limits is None:
        return float(limits["cost_limit_usd_per_sample"])
    if not isinstance(provider_limits, Mapping):
        raise ValueError("Provider cost limits must be an object")
    if provider not in provider_limits:
        raise ValueError(f"Missing per-sample cost limit for provider: {provider}")
    value = float(provider_limits[provider])
    if value <= 0:
        raise ValueError(f"Per-sample cost limit must be positive: {provider}")
    return value


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
        "authority_action_experiment_v0.4",
        "authority_action_experiment_v0.5",
        "authority_action_experiment_v0.6",
        "authority_action_experiment_v0.6.1",
        "authority_action_experiment_v0.7",
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

    factorial = dataset.get("factorial_design")
    if factorial is not None:
        if not isinstance(factorial, Mapping):
            raise ValueError("Factorial design must be an object")
        required_factorial_fields = {
            "group_field",
            "variant_field",
            "group_count",
            "expected_variants",
            "expected_action_by_variant",
            "behavior_family_counts",
        }
        missing_factorial_fields = sorted(required_factorial_fields - factorial.keys())
        if missing_factorial_fields:
            raise ValueError(
                f"Factorial design is missing fields: {missing_factorial_fields}"
            )
        group_field = str(factorial["group_field"])
        variant_field = str(factorial["variant_field"])
        expected_variants = {str(value) for value in factorial["expected_variants"]}
        if not expected_variants:
            raise ValueError("Factorial design expected_variants must not be empty")
        grouped_rows: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            metadata = row.get("metadata", {})
            group_value = str(metadata.get(group_field, ""))
            if not group_value:
                raise ValueError(f"Factorial row is missing {group_field}")
            grouped_rows.setdefault(group_value, []).append(row)
        if len(grouped_rows) != int(factorial["group_count"]):
            raise ValueError("Factorial design group count mismatch")
        expected_action_by_variant = {
            str(key): str(value)
            for key, value in factorial["expected_action_by_variant"].items()
        }
        if set(expected_action_by_variant) != expected_variants:
            raise ValueError("Factorial expected-action variants mismatch")
        for group_id, group_rows in grouped_rows.items():
            variants = {
                str(row.get("metadata", {}).get(variant_field, "")): row
                for row in group_rows
            }
            if len(group_rows) != len(expected_variants) or set(variants) != expected_variants:
                raise ValueError(f"Factorial group {group_id} is incomplete")
            for variant, row in variants.items():
                actual_action = str(
                    row.get("metadata", {}).get("expected_action", "")
                )
                if actual_action != expected_action_by_variant[variant]:
                    raise ValueError(
                        f"Factorial group {group_id} variant {variant} "
                        "has unexpected action"
                    )
        expected_family_counts = {
            str(key): int(value)
            for key, value in factorial["behavior_family_counts"].items()
        }
        actual_family_counts = {
            family: sum(
                1
                for row in rows
                if str(row.get("metadata", {}).get("behavior_family", "")) == family
            )
            for family in expected_family_counts
        }
        if actual_family_counts != expected_family_counts:
            raise ValueError("Factorial behavior-family counts mismatch")

    difficulty = dataset.get("difficulty_design")
    if difficulty is not None:
        if not isinstance(difficulty, Mapping):
            raise ValueError("Difficulty design must be an object")
        difficulty_field = str(difficulty.get("field", ""))
        expected_difficulty_counts = {
            str(key): int(value)
            for key, value in difficulty.get("case_counts", {}).items()
        }
        if not difficulty_field or not expected_difficulty_counts:
            raise ValueError("Difficulty design is incomplete")
        actual_difficulty_counts = {
            level: sum(
                1
                for row in rows
                if str(row.get("metadata", {}).get(difficulty_field, "")) == level
            )
            for level in expected_difficulty_counts
        }
        if actual_difficulty_counts != expected_difficulty_counts:
            raise ValueError("Difficulty design case counts mismatch")

    monitoring = dataset.get("monitoring_design")
    if monitoring is not None:
        if not isinstance(monitoring, Mapping):
            raise ValueError("Monitoring design must be an object")
        direction_field = str(monitoring.get("direction_field", ""))
        expected_direction_counts = {
            str(key): int(value)
            for key, value in monitoring.get("group_counts", {}).items()
        }
        if not direction_field or not expected_direction_counts:
            raise ValueError("Monitoring design is incomplete")
        monitoring_groups: dict[str, str] = {}
        for row in rows:
            metadata = row.get("metadata", {})
            if str(metadata.get("behavior_family", "")) != "monitoring":
                continue
            group_id = str(metadata.get("pair_id", ""))
            direction = str(metadata.get(direction_field, ""))
            previous = monitoring_groups.setdefault(group_id, direction)
            if previous != direction:
                raise ValueError("Monitoring direction changes within a group")
        actual_direction_counts = {
            direction: sum(
                1 for value in monitoring_groups.values() if value == direction
            )
            for direction in expected_direction_counts
        }
        if actual_direction_counts != expected_direction_counts:
            raise ValueError("Monitoring direction group counts mismatch")

    pricing = manifest.get("pricing")
    if not isinstance(pricing, Mapping):
        raise ValueError("Manifest pricing must be an object")
    if pricing.get("config_path") not in artifacts:
        raise ValueError("Pricing config must be a frozen artifact")
    providers = sorted(str(provider) for provider in manifest["models"])
    provider_limits = {
        provider: provider_cost_limit(manifest, provider) for provider in providers
    }
    pilot_runs_per_provider = len(pilot_ids) * int(
        manifest["stages"]["pilot"]["epochs"]
    )
    worst_case_pilot_cost = round(
        pilot_runs_per_provider * sum(provider_limits.values()), 2
    )
    full_stage_enabled = bool(manifest["stages"]["full"].get("enabled", True))
    worst_case_full_cost: float | None
    if full_stage_enabled:
        full_runs_per_provider = len(rows) * int(
            manifest["stages"]["full"]["epochs"]
        )
        worst_case_full_cost = round(
            full_runs_per_provider * sum(provider_limits.values()), 2
        )
        configured_worst_case = worst_case_full_cost
    else:
        worst_case_full_cost = None
        configured_worst_case = worst_case_pilot_cost
    if configured_worst_case > float(manifest["limits"]["total_budget_usd"]):
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
        "provider_cost_limits_usd": provider_limits,
        "worst_case_pilot_cost_usd": worst_case_pilot_cost,
        "worst_case_full_cost_usd": worst_case_full_cost,
        "full_stage_enabled": full_stage_enabled,
    }
