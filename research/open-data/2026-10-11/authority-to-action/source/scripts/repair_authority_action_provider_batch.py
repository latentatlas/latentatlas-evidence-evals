"""Repair one protocol-interrupted analytical slot without hiding the attempt.

The original provider batch remains immutable.  A repair is eligible only when
the frozen plan identifies exactly one protocol-interrupted slot, and the
replacement is selected by protocol status rather than model performance.
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

from evals.experiment_control import load_manifest
from evals.experiment_control import sha256_file
from evals.experiment_control import verify_manifest
from scripts.run_authority_action_experiment import audit_provider_logs
from scripts.run_authority_action_experiment import build_command
from scripts.run_authority_action_experiment import subprocess_environment
from scripts.run_authority_action_full_batches import _write_json_atomic
from scripts.run_authority_action_full_batches import sample_ids_sha256
from scripts.run_authority_action_full_batches import select_batch
from scripts.run_authority_action_full_batches import verify_checkpoint


DEFAULT_PLAN = REPO_ROOT / "evals" / "repair_plan_v0_8_2_batch02_anthropic.json"
PLAN_SCHEMA = "authority_action_protocol_slot_repair_v0.1"


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Repair authorization timestamp lacks a timezone")
    return parsed.astimezone(timezone.utc)


def _repo_path(value: str) -> Path:
    path = (REPO_ROOT / value).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as error:
        raise ValueError("Repair artifact path escapes the repository") from error
    return path


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sample_cost(sample: Mapping[str, Any]) -> float:
    usage = sample.get("model_usage", {})
    if not isinstance(usage, Mapping):
        raise ValueError("Repair source sample lacks model usage")
    return sum(float(value.get("total_cost", 0.0)) for value in usage.values())


def _single_json_log(log_dir: Path) -> Path:
    logs = sorted(path for path in log_dir.glob("*.json") if path.is_file())
    if len(logs) != 1:
        raise ValueError(f"Expected one JSON log in {log_dir}, found {len(logs)}")
    return logs[0]


def verify_plan(plan_path: Path) -> dict[str, Any]:
    plan = _load_json(plan_path)
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise ValueError("Repair plan schema mismatch")
    if plan.get("execution_approved") is not True:
        raise ValueError("Repair plan is not approved")
    if int(plan.get("maximum_repair_attempts", -1)) != 1:
        raise ValueError("Repair plan must permit exactly one attempt")
    if plan.get("selection_basis") != "protocol_interruption_only":
        raise ValueError("Repair selection cannot depend on model performance")
    now = datetime.now(timezone.utc)
    approved_at = _parse_utc(str(plan["approved_at_utc"]))
    expires_at = _parse_utc(str(plan["expires_at_utc"]))
    if approved_at > now or now >= expires_at:
        raise ValueError("Repair authorization is not currently valid")
    repair_cost_cap = float(plan["maximum_repair_cost_usd"])
    if (
        repair_cost_cap <= 0
        or float(plan["live_anthropic_credit_snapshot_usd"]) < repair_cost_cap
        or float(plan["live_anthropic_monthly_limit_remaining_usd"])
        < repair_cost_cap
    ):
        raise ValueError("Repair credit authorization is insufficient")

    manifest_path = _repo_path(str(plan["source_manifest"]))
    verification = verify_manifest(manifest_path)
    manifest = load_manifest(manifest_path)
    if verification["manifest_sha256"] != plan["source_manifest_sha256"]:
        raise ValueError("Repair manifest digest mismatch")
    if manifest["experiment_id"] != plan["experiment_id"]:
        raise ValueError("Repair experiment identity mismatch")
    if sha256_file(Path(__file__).resolve()) != plan["repair_runner_sha256"]:
        raise ValueError("Repair runner digest mismatch")

    run_root = _repo_path(str(plan["run_root"]))
    original_log = _repo_path(str(plan["original_log"]))
    if sha256_file(original_log) != plan["original_log_sha256"]:
        raise ValueError("Original interrupted log digest mismatch")
    try:
        original_log.relative_to(run_root)
    except ValueError as error:
        raise ValueError("Original log is outside the authorized run root") from error
    original_audit = audit_provider_logs(original_log.parent)
    expected_original_audit = plan["original_provider_audit"]
    for field in (
        "sample_runs",
        "protocol_complete_runs",
        "protocol_interrupted_runs",
        "token_limit_exceeded",
    ):
        if int(original_audit[field]) != int(expected_original_audit[field]):
            raise ValueError(f"Original provider audit mismatch: {field}")

    raw_log = _load_json(original_log)
    repair_slot = plan["repair_slot"]
    interrupted = [
        sample
        for sample in raw_log["samples"]
        if sample.get("id") == repair_slot["sample_id"]
        and int(sample.get("epoch", -1)) == int(repair_slot["original_epoch"])
        and sample.get("uuid") == repair_slot["original_sample_uuid"]
        and float(sample.get("token_limit_usage", 0))
        >= float(sample.get("token_limit", float("inf")))
    ]
    if len(interrupted) != 1:
        raise ValueError("Repair slot does not identify one token-limited sample")
    if abs(_sample_cost(interrupted[0]) - float(repair_slot["original_cost_usd"])) > 1e-9:
        raise ValueError("Interrupted sample cost mismatch")

    batch = select_batch(manifest, str(plan["batch_id"]))
    if repair_slot["sample_id"] not in batch["sample_ids"]:
        raise ValueError("Repair sample is outside the frozen batch")
    provider = str(plan["provider"])
    if provider not in manifest["models"]:
        raise ValueError("Repair provider is not in the frozen manifest")
    configuration = plan["configuration_contract"]
    if (
        configuration["model"] != manifest["models"][provider]["inspect_model"]
        or configuration["reasoning_effort"]
        != manifest["models"][provider]["full_effort"]
        or float(configuration["sample_cost_limit_usd"]) != repair_cost_cap
    ):
        raise ValueError("Repair configuration differs from the frozen provider")
    return {
        "plan": plan,
        "manifest": manifest,
        "verification": verification,
        "manifest_path": manifest_path,
        "run_root": run_root,
        "original_log": original_log,
        "original_audit": original_audit,
        "batch": batch,
        "provider": provider,
    }


def _build_repair_command(context: Mapping[str, Any], repair_log_dir: Path) -> list[str]:
    plan = context["plan"]
    command = build_command(
        context["manifest"],
        context["provider"],
        "full",
        repair_log_dir,
        context["verification"]["dataset_sha256"],
        context["verification"]["manifest_sha256"],
    )
    epochs_index = command.index("--epochs") + 1
    command[epochs_index] = "1"
    sample_id = str(plan["repair_slot"]["sample_id"])
    command.extend(
        [
            "--sample-id",
            sample_id,
            "--metadata",
            f"batch_id={plan['batch_id']}",
            "--metadata",
            f"repair_plan_id={plan['repair_plan_id']}",
            "--metadata",
            f"repair_for_original_epoch={plan['repair_slot']['original_epoch']}",
        ]
    )
    return command


def _artifact(path: Path, run_root: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(run_root)), "sha256": sha256_file(path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)

    load_dotenv(REPO_ROOT / ".env")
    context = verify_plan(args.plan.resolve())
    plan = context["plan"]
    run_root = context["run_root"]
    provider = context["provider"]
    batch = context["batch"]
    repair_log_dir = run_root / str(plan["repair_log_dir"])
    command = _build_repair_command(context, repair_log_dir)
    print(
        json.dumps(
            {
                "repair_plan_id": plan["repair_plan_id"],
                "repair_sample_id": plan["repair_slot"]["sample_id"],
                "original_epoch": plan["repair_slot"]["original_epoch"],
                "maximum_repair_attempts": plan["maximum_repair_attempts"],
                "selection_basis": plan["selection_basis"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(shlex.join(command))
    if not args.execute:
        print("Dry run only. No paid repair call was made.")
        return 0

    credential_env = context["manifest"]["models"][provider]["credential_env"]
    if not os.environ.get(credential_env):
        print(f"Missing credential environment variable: {credential_env}", file=sys.stderr)
        return 2
    checkpoint_path = (
        run_root / "checkpoints" / str(batch["batch_id"]) / f"{provider}.json"
    )
    if checkpoint_path.exists():
        verify_checkpoint(
            checkpoint_path,
            run_root=run_root,
            manifest=context["manifest"],
            verification=context["verification"],
            batch=batch,
            provider=provider,
        )
        print("Verified repaired checkpoint already exists; no call made.")
        return 0
    if repair_log_dir.exists() and any(repair_log_dir.iterdir()):
        raise ValueError("Repair evidence already exists and requires review")

    repair_log_dir.mkdir(parents=True, exist_ok=False)
    started_at = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        env=subprocess_environment(),
    )
    if result.returncode != 0:
        return result.returncode
    repair_audit = audit_provider_logs(repair_log_dir)
    if (
        repair_audit["status"] != "success"
        or int(repair_audit["sample_runs"]) != 1
        or int(repair_audit["protocol_complete_runs"]) != 1
        or int(repair_audit["protocol_interrupted_runs"]) != 0
    ):
        return 3

    repair_log = _single_json_log(repair_log_dir)
    repair_raw = _load_json(repair_log)
    if len(repair_raw["samples"]) != 1:
        raise ValueError("Repair log does not contain exactly one sample")
    replacement = repair_raw["samples"][0]
    if replacement.get("id") != plan["repair_slot"]["sample_id"]:
        raise ValueError("Repair result sample identity mismatch")

    original_cost = float(context["original_audit"]["calculated_total_cost_usd"])
    interrupted_cost = float(plan["repair_slot"]["original_cost_usd"])
    repair_cost = float(repair_audit["calculated_total_cost_usd"])
    gross_cost = original_cost + repair_cost
    analytical_cost = original_cost - interrupted_cost + repair_cost
    provider_audit = {
        "status": "success",
        "log_count": 2,
        "sample_runs": 60,
        "protocol_complete_runs": 60,
        "protocol_interrupted_runs": 0,
        "gross_provider_attempts": 61,
        "operational_interruptions": 1,
        "repair_attempts": 1,
        "token_limit_exceeded": 0,
        "cost_limit_exceeded": 0,
        "other_sample_limit": 0,
        "calculated_total_cost_usd": round(gross_cost, 9),
        "analytical_set_cost_usd": round(analytical_cost, 9),
        "operational_overhead_cost_usd": round(interrupted_cost, 9),
    }
    checkpoint = {
        "schema_version": "authority_action_provider_batch_checkpoint_v0.1",
        "status": "success",
        "experiment_id": context["manifest"]["experiment_id"],
        "manifest_sha256": context["verification"]["manifest_sha256"],
        "dataset_sha256": context["verification"]["dataset_sha256"],
        "batch_id": batch["batch_id"],
        "provider": provider,
        "sample_ids_sha256": sample_ids_sha256(
            [str(value) for value in batch["sample_ids"]]
        ),
        "expected_sample_runs": 60,
        "provider_audit": provider_audit,
        "repair": {
            "repair_plan_id": plan["repair_plan_id"],
            "selection_basis": plan["selection_basis"],
            "original_interrupted_sample": {
                "id": plan["repair_slot"]["sample_id"],
                "epoch": plan["repair_slot"]["original_epoch"],
                "uuid": plan["repair_slot"]["original_sample_uuid"],
            },
            "replacement_sample": {
                "id": replacement["id"],
                "analytical_epoch": plan["repair_slot"]["original_epoch"],
                "source_epoch": replacement["epoch"],
                "uuid": replacement["uuid"],
            },
            "original_attempt_retained": True,
        },
        "log_artifacts": [
            _artifact(context["original_log"], run_root),
            _artifact(repair_log, run_root),
        ],
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "credential_values_logged": False,
    }
    _write_json_atomic(checkpoint_path, checkpoint)
    verify_checkpoint(
        checkpoint_path,
        run_root=run_root,
        manifest=context["manifest"],
        verification=context["verification"],
        batch=batch,
        provider=provider,
    )

    run_manifest_path = run_root / "run_manifest.json"
    run_manifest = _load_json(run_manifest_path)
    unit_id = f"{batch['batch_id']}:{provider}"
    run_manifest["provider_batches"][unit_id] = {
        "status": "success_repaired_protocol_slot",
        "checkpoint": str(checkpoint_path.relative_to(run_root)),
        "calculated_total_cost_usd": provider_audit["calculated_total_cost_usd"],
        "analytical_set_cost_usd": provider_audit["analytical_set_cost_usd"],
        "gross_provider_attempts": provider_audit["gross_provider_attempts"],
    }
    run_manifest["status"] = "in_progress"
    run_manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    _write_json_atomic(run_manifest_path, run_manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
