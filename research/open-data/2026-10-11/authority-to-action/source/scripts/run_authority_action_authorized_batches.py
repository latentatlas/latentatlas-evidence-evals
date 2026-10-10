"""Execute the frozen v0.8.2 medium benchmark under a one-time authorization.

This file intentionally leaves the preauthorization manifest and its frozen batch
runner unchanged.  A separate, expiring authorization envelope supplies the live
credit check, explicit approval, and provider-specific operational spend caps.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.experiment_control import V0_8_2_MANIFEST
from evals.experiment_control import load_manifest
from evals.experiment_control import sha256_file
from evals.experiment_control import verify_manifest
from scripts.run_authority_action_experiment import audit_provider_logs
from scripts.run_authority_action_experiment import subprocess_environment
from scripts.run_authority_action_full_batches import _load_or_create_run_audit
from scripts.run_authority_action_full_batches import _log_fingerprints
from scripts.run_authority_action_full_batches import _write_json_atomic
from scripts.run_authority_action_full_batches import build_provider_batch_command
from scripts.run_authority_action_full_batches import sample_ids_sha256
from scripts.run_authority_action_full_batches import select_batch
from scripts.run_authority_action_full_batches import selected_batch_providers
from scripts.run_authority_action_full_batches import summarize_checkpoints
from scripts.run_authority_action_full_batches import verify_checkpoint


DEFAULT_MANIFEST = V0_8_2_MANIFEST
DEFAULT_AUTHORIZATION = REPO_ROOT / "evals" / "execution_authorization_v0_8_2.json"
FROZEN_BATCH_RUNNER = REPO_ROOT / "scripts" / "run_authority_action_full_batches.py"
AUTHORIZATION_SCHEMA = "authority_action_execution_authorization_v0.1"


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Authorization timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def _resolve_repo_file(value: str) -> Path:
    path = (REPO_ROOT / value).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as error:
        raise ValueError("Authorization path escapes the repository") from error
    if not path.is_file():
        raise ValueError(f"Authorized artifact is missing: {value}")
    return path


def load_and_verify_authorization(
    path: Path,
    *,
    manifest: Mapping[str, Any],
    verification: Mapping[str, Any],
) -> dict[str, Any]:
    authorization_path = path.resolve()
    try:
        authorization_path.relative_to(REPO_ROOT)
    except ValueError as error:
        raise ValueError("Authorization file must be inside the repository") from error
    authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise ValueError("Execution authorization schema mismatch")
    if authorization.get("execution_approved") is not True:
        raise ValueError("Execution authorization is not approved")
    if authorization.get("live_provider_credit_verified") is not True:
        raise ValueError("Live provider credit was not verified")
    if authorization.get("experiment_id") != manifest["experiment_id"]:
        raise ValueError("Execution authorization experiment mismatch")

    now = datetime.now(timezone.utc)
    approved_at = _parse_utc(str(authorization["approved_at_utc"]))
    expires_at = _parse_utc(str(authorization["expires_at_utc"]))
    if approved_at > now or now >= expires_at:
        raise ValueError("Execution authorization is not currently valid")

    source_manifest = _resolve_repo_file(str(authorization["source_manifest"]))
    source_runner = _resolve_repo_file(str(authorization["source_batch_runner"]))
    authorized_runner = _resolve_repo_file(str(authorization["authorized_runner"]))
    expected_artifacts = {
        source_manifest: str(authorization["source_manifest_sha256"]),
        source_runner: str(authorization["source_batch_runner_sha256"]),
        authorized_runner: str(authorization["authorized_runner_sha256"]),
    }
    for artifact_path, expected_sha256 in expected_artifacts.items():
        if sha256_file(artifact_path) != expected_sha256:
            raise ValueError(f"Authorized artifact digest mismatch: {artifact_path.name}")
    if source_manifest != DEFAULT_MANIFEST.resolve():
        raise ValueError("Authorization does not target the frozen v0.8.2 manifest")
    if source_runner != FROZEN_BATCH_RUNNER.resolve():
        raise ValueError("Authorization does not target the frozen batch runner")
    if authorized_runner != Path(__file__).resolve():
        raise ValueError("Authorization does not target this execution runner")
    if authorization["source_manifest_sha256"] != verification["manifest_sha256"]:
        raise ValueError("Authorization and verified manifest digests disagree")

    provider_caps = authorization.get("provider_authorized_spend_cap_usd")
    provider_balances = authorization.get("live_credit_snapshot_usd")
    provider_projections = authorization.get("provider_operational_projection_usd")
    if not all(isinstance(value, Mapping) for value in (
        provider_caps,
        provider_balances,
        provider_projections,
    )):
        raise ValueError("Authorization provider budget maps are missing")
    for provider in manifest["execution_plan"]["provider_order"]:
        cap = float(provider_caps[provider])
        balance = float(provider_balances[provider])
        projection = float(provider_projections[provider])
        if projection <= 0 or cap < projection or balance < cap:
            raise ValueError(f"Provider budget authorization is insufficient: {provider}")
    monthly_remaining = authorization.get("provider_monthly_limit_remaining_usd", {})
    for provider, remaining in monthly_remaining.items():
        if float(remaining) < float(provider_caps[provider]):
            raise ValueError(f"Provider monthly limit is insufficient: {provider}")
    return authorization


def _provider_spend_from_checkpoints(
    *,
    run_root: Path,
    manifest: Mapping[str, Any],
    verification: Mapping[str, Any],
) -> dict[str, float]:
    totals = {str(provider): 0.0 for provider in manifest["models"]}
    for batch in manifest["execution_plan"]["batches"]:
        for provider in manifest["execution_plan"]["provider_order"]:
            checkpoint_path = (
                run_root / "checkpoints" / str(batch["batch_id"]) / f"{provider}.json"
            )
            if not checkpoint_path.is_file():
                continue
            checkpoint = verify_checkpoint(
                checkpoint_path,
                run_root=run_root,
                manifest=manifest,
                verification=verification,
                batch=batch,
                provider=str(provider),
            )
            totals[str(provider)] += float(
                checkpoint["provider_audit"]["calculated_total_cost_usd"]
            )
    return totals


def _selected_batches(
    manifest: Mapping[str, Any], batch_id: str
) -> list[dict[str, Any]]:
    if batch_id == "all":
        return [dict(batch) for batch in manifest["execution_plan"]["batches"]]
    return [select_batch(manifest, batch_id)]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--authorization", type=Path, default=DEFAULT_AUTHORIZATION)
    parser.add_argument("--batch-id", default="all")
    parser.add_argument(
        "--provider", choices=("all", "anthropic", "openai"), default="all"
    )
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)

    load_dotenv(REPO_ROOT / ".env")
    verification = verify_manifest(args.manifest)
    manifest = load_manifest(args.manifest)
    authorization = load_and_verify_authorization(
        args.authorization,
        manifest=manifest,
        verification=verification,
    )
    batches = _selected_batches(manifest, args.batch_id)
    providers = selected_batch_providers(manifest, args.provider)
    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = (
        args.run_root.resolve()
        if args.run_root
        else REPO_ROOT / "outputs" / "inspect" / f"{run_stamp}-full-medium-authorized"
    )
    authorization_sha256 = sha256_file(args.authorization.resolve())

    commands: list[tuple[dict[str, Any], str, list[str], Path]] = []
    for batch in batches:
        for provider in providers:
            log_dir = run_root / "full" / str(batch["batch_id"]) / provider
            command = build_provider_batch_command(
                manifest, verification, provider, batch, log_dir
            )
            commands.append((batch, provider, command, log_dir))

    print(
        json.dumps(
            {
                "authorization_id": authorization["authorization_id"],
                "authorization_sha256": authorization_sha256,
                "expires_at_utc": authorization["expires_at_utc"],
                "manifest_sha256": verification["manifest_sha256"],
                "provider_authorized_spend_cap_usd": authorization[
                    "provider_authorized_spend_cap_usd"
                ],
                "selected_provider_batches": len(commands),
            },
            indent=2,
            sort_keys=True,
        )
    )
    for batch, provider, command, _log_dir in commands:
        print(f"[{batch['batch_id']}:{provider}] {shlex.join(command)}")
    if not args.execute:
        print("Dry run only. No paid provider calls were made.")
        return 0

    missing_credentials = [
        manifest["models"][provider]["credential_env"]
        for provider in providers
        if not os.environ.get(manifest["models"][provider]["credential_env"])
    ]
    if missing_credentials:
        print(
            "Missing credential environment variables: " + ", ".join(missing_credentials),
            file=sys.stderr,
        )
        return 2

    run_root.mkdir(parents=True, exist_ok=True)
    audit = _load_or_create_run_audit(
        manifest=manifest, verification=verification, run_root=run_root
    )
    audit["execution_authorization"] = {
        "authorization_id": authorization["authorization_id"],
        "authorization_sha256": authorization_sha256,
        "approved_at_utc": authorization["approved_at_utc"],
        "expires_at_utc": authorization["expires_at_utc"],
        "credential_values_logged": False,
    }
    audit_path = run_root / "run_manifest.json"
    _write_json_atomic(audit_path, audit)

    provider_caps = {
        str(provider): float(value)
        for provider, value in authorization["provider_authorized_spend_cap_usd"].items()
    }
    provider_batch_projections = {
        str(provider): float(value)
        for provider, value in authorization["provider_operational_projection_per_batch_usd"].items()
    }

    for batch, provider, command, log_dir in commands:
        unit_id = f"{batch['batch_id']}:{provider}"
        checkpoint_path = (
            run_root / "checkpoints" / str(batch["batch_id"]) / f"{provider}.json"
        )
        if checkpoint_path.exists():
            verify_checkpoint(
                checkpoint_path,
                run_root=run_root,
                manifest=manifest,
                verification=verification,
                batch=batch,
                provider=provider,
            )
            audit["provider_batches"][unit_id] = {
                "status": "skipped_verified_checkpoint",
                "checkpoint": str(checkpoint_path.relative_to(run_root)),
            }
            _write_json_atomic(audit_path, audit)
            continue
        if log_dir.exists() and any(log_dir.iterdir()):
            raise ValueError(
                f"Uncheckpointed provider-batch evidence requires review: {unit_id}"
            )

        provider_spend = _provider_spend_from_checkpoints(
            run_root=run_root,
            manifest=manifest,
            verification=verification,
        )
        projected_after_unit = provider_spend[provider] + provider_batch_projections[
            provider
        ]
        if projected_after_unit > provider_caps[provider]:
            audit["provider_batches"][unit_id] = {
                "status": "blocked_by_provider_spend_cap",
                "calculated_spend_before_unit_usd": provider_spend[provider],
                "projected_unit_cost_usd": provider_batch_projections[provider],
                "provider_authorized_spend_cap_usd": provider_caps[provider],
            }
            audit["status"] = "needs_review"
            _write_json_atomic(audit_path, audit)
            return 4

        log_dir.mkdir(parents=True, exist_ok=False)
        started_at = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            env=subprocess_environment(),
        )
        if result.returncode != 0:
            audit["provider_batches"][unit_id] = {
                "status": "failed",
                "returncode": result.returncode,
                "started_at_utc": started_at,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            audit["status"] = "needs_review"
            _write_json_atomic(audit_path, audit)
            return result.returncode

        provider_audit = audit_provider_logs(log_dir)
        expected_sample_runs = len(batch["sample_ids"]) * int(
            manifest["stages"]["full"]["epochs"]
        )
        if (
            provider_audit["status"] != "success"
            or provider_audit["sample_runs"] != expected_sample_runs
            or provider_audit["protocol_complete_runs"] != expected_sample_runs
            or provider_audit["protocol_interrupted_runs"] != 0
        ):
            audit["provider_batches"][unit_id] = {
                "status": "needs_review",
                "provider_audit": provider_audit,
                "started_at_utc": started_at,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            audit["status"] = "needs_review"
            _write_json_atomic(audit_path, audit)
            return 3

        projected_total = provider_spend[provider] + float(
            provider_audit["calculated_total_cost_usd"]
        )
        if projected_total > provider_caps[provider]:
            audit["provider_batches"][unit_id] = {
                "status": "needs_review_spend_cap_exceeded",
                "provider_audit": provider_audit,
                "started_at_utc": started_at,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            audit["status"] = "needs_review"
            _write_json_atomic(audit_path, audit)
            return 4

        checkpoint = {
            "schema_version": "authority_action_provider_batch_checkpoint_v0.1",
            "status": "success",
            "experiment_id": manifest["experiment_id"],
            "manifest_sha256": verification["manifest_sha256"],
            "dataset_sha256": verification["dataset_sha256"],
            "batch_id": batch["batch_id"],
            "provider": provider,
            "sample_ids_sha256": sample_ids_sha256(
                [str(value) for value in batch["sample_ids"]]
            ),
            "expected_sample_runs": expected_sample_runs,
            "provider_audit": provider_audit,
            "log_artifacts": _log_fingerprints(log_dir, run_root),
            "started_at_utc": started_at,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "credential_values_logged": False,
        }
        _write_json_atomic(checkpoint_path, checkpoint)
        audit["provider_batches"][unit_id] = {
            "status": "success",
            "checkpoint": str(checkpoint_path.relative_to(run_root)),
            "calculated_total_cost_usd": provider_audit[
                "calculated_total_cost_usd"
            ],
        }
        audit["status"] = "in_progress"
        audit["calculated_provider_spend_usd"] = _provider_spend_from_checkpoints(
            run_root=run_root,
            manifest=manifest,
            verification=verification,
        )
        audit["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        _write_json_atomic(audit_path, audit)

    completion = summarize_checkpoints(
        run_root=run_root, manifest=manifest, verification=verification
    )
    audit["completion"] = completion
    audit["status"] = "success" if completion["complete"] else "in_progress"
    audit["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    if completion["complete"]:
        audit["completed_at_utc"] = audit["updated_at_utc"]
    _write_json_atomic(audit_path, audit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
