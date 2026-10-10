"""Recompute final run truth from verified provider-batch checkpoints."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.experiment_control import V0_8_2_MANIFEST
from evals.experiment_control import load_manifest
from evals.experiment_control import sha256_file
from evals.experiment_control import verify_manifest
from scripts.run_authority_action_full_batches import _write_json_atomic
from scripts.run_authority_action_full_batches import summarize_checkpoints
from scripts.run_authority_action_full_batches import verify_checkpoint


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=V0_8_2_MANIFEST)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args(argv)

    run_root = args.run_root.resolve()
    try:
        run_root.relative_to(REPO_ROOT)
    except ValueError as error:
        raise ValueError("Run root must be inside the repository") from error
    manifest = load_manifest(args.manifest)
    verification = verify_manifest(args.manifest)
    completion = summarize_checkpoints(
        run_root=run_root,
        manifest=manifest,
        verification=verification,
    )
    if not completion["complete"]:
        raise ValueError("Cannot finalize an incomplete run")

    providers = [str(value) for value in manifest["execution_plan"]["provider_order"]]
    gross_cost = {provider: 0.0 for provider in providers}
    analytical_cost = {provider: 0.0 for provider in providers}
    overhead_cost = {provider: 0.0 for provider in providers}
    gross_attempts = {provider: 0 for provider in providers}
    checkpoint_artifacts: list[dict[str, Any]] = []

    for batch in manifest["execution_plan"]["batches"]:
        for provider in providers:
            checkpoint_path = (
                run_root
                / "checkpoints"
                / str(batch["batch_id"])
                / f"{provider}.json"
            )
            checkpoint = verify_checkpoint(
                checkpoint_path,
                run_root=run_root,
                manifest=manifest,
                verification=verification,
                batch=batch,
                provider=provider,
            )
            audit = checkpoint["provider_audit"]
            gross = float(audit["calculated_total_cost_usd"])
            analytical = float(audit.get("analytical_set_cost_usd", gross))
            overhead = float(audit.get("operational_overhead_cost_usd", gross - analytical))
            attempts = int(audit.get("gross_provider_attempts", audit["sample_runs"]))
            if analytical < 0 or overhead < 0 or abs(gross - analytical - overhead) > 1e-8:
                raise ValueError("Checkpoint cost decomposition is inconsistent")
            gross_cost[provider] += gross
            analytical_cost[provider] += analytical
            overhead_cost[provider] += overhead
            gross_attempts[provider] += attempts
            checkpoint_artifacts.append(
                {
                    "batch_id": batch["batch_id"],
                    "provider": provider,
                    "path": str(checkpoint_path.relative_to(run_root)),
                    "sha256": sha256_file(checkpoint_path),
                    "analytical_sample_runs": int(audit["sample_runs"]),
                    "gross_provider_attempts": attempts,
                    "gross_cost_usd": gross,
                    "analytical_cost_usd": analytical,
                    "operational_overhead_cost_usd": overhead,
                }
            )

    gross_cost = {key: round(value, 9) for key, value in gross_cost.items()}
    analytical_cost = {
        key: round(value, 9) for key, value in analytical_cost.items()
    }
    overhead_cost = {key: round(value, 9) for key, value in overhead_cost.items()}
    total_gross = round(sum(gross_cost.values()), 9)
    total_analytical = round(sum(analytical_cost.values()), 9)
    total_overhead = round(sum(overhead_cost.values()), 9)
    if abs(total_gross - float(completion["calculated_total_cost_usd"])) > 1e-8:
        raise ValueError("Checkpoint cost and completion total disagree")
    if sum(gross_attempts.values()) < int(completion["protocol_complete_runs"]):
        raise ValueError("Gross attempt total cannot be below analytical runs")

    finalized_at = datetime.now(timezone.utc).isoformat()
    run_manifest_path = run_root / "run_manifest.json"
    run_manifest = _load_json(run_manifest_path)
    run_manifest["status"] = "success"
    run_manifest["completion"] = completion
    run_manifest["calculated_provider_spend_usd"] = gross_cost
    run_manifest["analytical_provider_spend_usd"] = analytical_cost
    run_manifest["operational_overhead_provider_spend_usd"] = overhead_cost
    run_manifest["gross_provider_attempts_by_provider"] = gross_attempts
    run_manifest["finalization"] = {
        "status": "success",
        "finalized_at_utc": finalized_at,
        "source_of_truth": "verified_provider_batch_checkpoints",
        "final_summary": "final_audit_summary.json",
        "credential_values_logged": False,
    }
    run_manifest["updated_at_utc"] = finalized_at
    run_manifest["completed_at_utc"] = finalized_at
    _write_json_atomic(run_manifest_path, run_manifest)

    final_summary_path = run_root / "final_audit_summary.json"
    final_summary = {
        "schema_version": "authority_action_full_run_final_audit_v0.1",
        "status": "success",
        "experiment_id": manifest["experiment_id"],
        "manifest_sha256": verification["manifest_sha256"],
        "dataset_sha256": verification["dataset_sha256"],
        "run_manifest_sha256": sha256_file(run_manifest_path),
        "finalized_at_utc": finalized_at,
        "analytical_sample_runs": int(completion["protocol_complete_runs"]),
        "gross_provider_attempts": sum(gross_attempts.values()),
        "verified_provider_batch_checkpoints": int(
            completion["verified_provider_batch_checkpoints"]
        ),
        "gross_cost_usd": total_gross,
        "analytical_set_cost_usd": total_analytical,
        "operational_overhead_cost_usd": total_overhead,
        "gross_provider_cost_usd": gross_cost,
        "analytical_provider_cost_usd": analytical_cost,
        "operational_overhead_provider_cost_usd": overhead_cost,
        "gross_provider_attempts_by_provider": gross_attempts,
        "repair_policy": "protocol_interruption_only",
        "credential_values_logged": False,
        "checkpoints": checkpoint_artifacts,
    }
    _write_json_atomic(final_summary_path, final_summary)
    digest_path = run_root / "final_audit_summary.sha256"
    digest_path.write_text(
        f"{sha256_file(final_summary_path)}  {final_summary_path.name}\n",
        encoding="utf-8",
    )
    print(json.dumps(final_summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
