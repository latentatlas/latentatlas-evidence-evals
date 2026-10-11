"""Run the approved protocol repair, then resume verified full checkpoints."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
RUN_ROOT = (
    REPO_ROOT
    / "outputs"
    / "inspect"
    / "20260727T152524Z-full-medium-authorized"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair-plan", type=Path, required=True)
    parser.add_argument("--resume-batch-id", default="all")
    parser.add_argument(
        "--resume-provider",
        choices=("all", "anthropic", "openai"),
        default="all",
    )
    args = parser.parse_args()
    repair = subprocess.run(
        [
            str(PYTHON),
            str(REPO_ROOT / "scripts" / "repair_authority_action_provider_batch.py"),
            "--plan",
            str(args.repair_plan.resolve()),
            "--execute",
        ],
        cwd=REPO_ROOT,
        check=False,
    )
    if repair.returncode != 0:
        return repair.returncode
    resume = subprocess.run(
        [
            str(PYTHON),
            str(REPO_ROOT / "scripts" / "run_authority_action_authorized_batches.py"),
            "--batch-id",
            args.resume_batch_id,
            "--provider",
            args.resume_provider,
            "--run-root",
            str(RUN_ROOT),
            "--execute",
        ],
        cwd=REPO_ROOT,
        check=False,
    )
    return resume.returncode


if __name__ == "__main__":
    raise SystemExit(main())
