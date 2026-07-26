"""Verify and optionally run the frozen Inspect authority-action experiment."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv
from inspect_ai.log import read_eval_log

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.experiment_control import DEFAULT_MANIFEST
from evals.experiment_control import load_manifest
from evals.experiment_control import provider_cost_limit
from evals.experiment_control import verify_manifest


SUPPORTED_LOG_SUFFIXES = {".eval", ".json"}


def subprocess_environment() -> dict[str, str]:
    """Return an environment that lets Inspect load repo-local task imports.

    Inspect executes task files through its installed CLI entry point, whose
    import path does not reliably include the current working directory. Keep
    any caller-provided PYTHONPATH entries, but place the repository root first
    so task modules can import the frozen ``evals`` package consistently.
    """

    environment = os.environ.copy()
    existing_entries = [
        entry
        for entry in environment.get("PYTHONPATH", "").split(os.pathsep)
        if entry
    ]
    python_path_entries = list(
        dict.fromkeys([str(REPO_ROOT), *existing_entries])
    )
    environment["PYTHONPATH"] = os.pathsep.join(python_path_entries)
    return environment


def build_command(
    manifest: dict[str, Any],
    provider: str,
    stage: str,
    log_dir: Path,
    dataset_sha256: str,
) -> list[str]:
    inspect_binary = shutil.which("inspect")
    if inspect_binary is None:
        candidate = Path(sys.executable).with_name("inspect")
        if not candidate.is_file():
            raise RuntimeError("Inspect CLI is not available in this Python environment")
        inspect_binary = str(candidate)

    model = manifest["models"][provider]
    stage_config = manifest["stages"][stage]
    limits = manifest["limits"]
    command = [
        inspect_binary,
        "eval",
        str(manifest.get("task", {}).get("path", "evals/authority_action_eval.py")),
        "--model",
        model["inspect_model"],
        "-T",
        "case_type=all",
        "--epochs",
        str(stage_config["epochs"]),
        "--max-connections",
        str(limits["max_connections"]),
        "--max-samples",
        str(limits["max_samples"]),
        "--max-retries",
        str(limits["max_retries"]),
        "--timeout",
        str(limits["timeout_seconds"]),
        "--message-limit",
        str(limits["message_limit"]),
        "--max-tokens",
        str(limits["max_tokens_per_generation"]),
        "--token-limit",
        f"output:{limits['output_token_limit_per_sample']}",
        "--cost-limit",
        str(provider_cost_limit(manifest, provider)),
        "--model-cost-config",
        str(REPO_ROOT / manifest["pricing"]["config_path"]),
        "--reasoning-effort",
        str(model[f"{stage}_effort"]),
        "--log-format",
        str(manifest["logging"]["format"]),
        "--log-dir",
        str(log_dir),
        "--display",
        "none",
        "--no-log-model-api",
        "--log-refusals",
        "--metadata",
        f"experiment_id={manifest['experiment_id']}",
        "--metadata",
        f"dataset_sha256={dataset_sha256}",
    ]
    if stage == "pilot":
        command.extend(["--sample-id", ",".join(stage_config["sample_ids"])])
    return command


def selected_providers(manifest: dict[str, Any], provider: str) -> list[str]:
    if provider == "all":
        return sorted(manifest["models"])
    if provider not in manifest["models"]:
        raise ValueError(f"Unknown provider: {provider}")
    return [provider]


def audit_provider_logs(log_dir: Path) -> dict[str, Any]:
    """Fail closed when a nominally successful log contains sample limits."""

    log_paths = sorted(
        path
        for path in log_dir.rglob("*")
        if path.is_file() and path.suffix in SUPPORTED_LOG_SUFFIXES
    )
    if not log_paths:
        raise ValueError(f"No Inspect logs found in {log_dir}")

    sample_runs = 0
    cost_limit_exceeded = 0
    token_limit_exceeded = 0
    other_sample_limit = 0
    calculated_total_cost_usd = 0.0
    for path in log_paths:
        log = read_eval_log(path)
        if log.status != "success" or log.samples is None:
            raise ValueError(f"Inspect log is incomplete: {path}")
        if log.stats is None:
            raise ValueError(f"Inspect log lacks usage stats: {path}")
        calculated_total_cost_usd += sum(
            float(usage.total_cost or 0.0)
            for usage in log.stats.model_usage.values()
        )
        for sample in log.samples:
            sample_runs += 1
            limit_types = {
                str(getattr(event, "type", ""))
                for event in (sample.events or [])
                if getattr(event, "event", None) == "sample_limit"
            }
            cost_limit_exceeded += int("cost" in limit_types)
            token_limit_exceeded += int("token" in limit_types)
            other_sample_limit += int(
                bool(limit_types)
                and "cost" not in limit_types
                and "token" not in limit_types
            )

    interrupted = (
        cost_limit_exceeded + token_limit_exceeded + other_sample_limit
    )
    return {
        "log_count": len(log_paths),
        "sample_runs": sample_runs,
        "protocol_complete_runs": sample_runs - interrupted,
        "protocol_interrupted_runs": interrupted,
        "cost_limit_exceeded": cost_limit_exceeded,
        "token_limit_exceeded": token_limit_exceeded,
        "other_sample_limit": other_sample_limit,
        "calculated_total_cost_usd": round(calculated_total_cost_usd, 9),
        "status": "needs_review" if interrupted else "success",
    }


def write_run_manifest(run_root: Path, audit: dict[str, Any]) -> None:
    """Persist the current audit state after every provider transition."""

    (run_root / "run_manifest.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("verify", "pilot", "full"), default="verify")
    parser.add_argument("--provider", choices=("all", "anthropic", "openai"), default="all")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Make paid provider calls. Without this flag, print the frozen plan only.",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)

    load_dotenv(REPO_ROOT / ".env")
    verification = verify_manifest(args.manifest)
    manifest = load_manifest(args.manifest)
    print(json.dumps({"verification": verification}, indent=2, sort_keys=True))
    if args.stage == "verify":
        return 0
    if not bool(manifest["stages"][args.stage].get("enabled", True)):
        print(f"Stage is disabled in the frozen manifest: {args.stage}", file=sys.stderr)
        return 2

    providers = selected_providers(manifest, args.provider)
    missing_credentials = [
        manifest["models"][name]["credential_env"]
        for name in providers
        if not os.environ.get(manifest["models"][name]["credential_env"])
    ]
    if args.execute and missing_credentials:
        print(
            "Missing credential environment variables: "
            + ", ".join(missing_credentials),
            file=sys.stderr,
        )
        return 2

    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    commands: list[tuple[str, list[str], Path]] = []
    for provider in providers:
        log_dir = REPO_ROOT / "outputs" / "inspect" / run_stamp / args.stage / provider
        commands.append(
            (
                provider,
                build_command(
                    manifest,
                    provider,
                    args.stage,
                    log_dir,
                    str(verification["dataset_sha256"]),
                ),
                log_dir,
            )
        )

    for provider, command, _ in commands:
        print(f"[{provider}] {shlex.join(command)}")
    if not args.execute:
        print("Dry run only. Add --execute after credentials are set.")
        return 0

    run_root = REPO_ROOT / "outputs" / "inspect" / run_stamp
    run_root.mkdir(parents=True, exist_ok=False)
    audit = {
        "experiment_id": manifest["experiment_id"],
        "stage": args.stage,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "verification": verification,
        "providers": providers,
        "commands": [command for _, command, _ in commands],
        "credential_values_logged": False,
        "status": "running",
        "provider_runs": {},
    }
    write_run_manifest(run_root, audit)

    for provider, command, log_dir in commands:
        log_dir.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            env=subprocess_environment(),
        )
        if result.returncode != 0:
            audit["provider_runs"][provider] = {
                "returncode": result.returncode,
                "status": "failed",
            }
            audit["status"] = "failed"
            audit["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            write_run_manifest(run_root, audit)
            print(f"{provider} evaluation failed with code {result.returncode}", file=sys.stderr)
            return result.returncode
        try:
            provider_audit = audit_provider_logs(log_dir)
        except (OSError, ValueError) as error:
            audit["provider_runs"][provider] = {
                "returncode": result.returncode,
                "status": "invalid_log",
                "error": str(error),
            }
            audit["status"] = "failed"
            audit["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            write_run_manifest(run_root, audit)
            print(str(error), file=sys.stderr)
            return 3
        audit["provider_runs"][provider] = {
            "returncode": result.returncode,
            **provider_audit,
        }
        write_run_manifest(run_root, audit)

    protocol_interrupted = any(
        provider_run.get("status") == "needs_review"
        for provider_run in audit["provider_runs"].values()
    )
    audit["status"] = "needs_review" if protocol_interrupted else "success"
    audit["calculated_total_cost_usd"] = round(
        sum(
            float(provider_run.get("calculated_total_cost_usd", 0.0))
            for provider_run in audit["provider_runs"].values()
        ),
        9,
    )
    audit["worst_case_stage_cost_usd"] = verification.get(
        f"worst_case_{args.stage}_cost_usd"
    )
    audit["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_run_manifest(run_root, audit)
    if protocol_interrupted:
        print(
            "Run completed with sample-limit interruptions; see run_manifest.json",
            file=sys.stderr,
        )
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
