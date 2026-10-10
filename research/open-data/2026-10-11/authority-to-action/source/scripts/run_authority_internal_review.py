"""Build or analyze the local Authority-to-Action internal blind review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from evals.authority_action_internal_review import DEFAULT_DATASET
from evals.authority_action_internal_review import DEFAULT_OUTPUT_DIR
from evals.authority_action_internal_review import analyze_review
from evals.authority_action_internal_review import build_review_artifacts


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "analyze"))
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "build":
        report = build_review_artifacts(
            dataset_path=args.dataset,
            output_dir=args.output_dir,
        )
        exit_code = 0
    else:
        report = analyze_review(
            response_path=args.output_dir / "review_responses.csv",
            answer_key_path=args.output_dir / "answer_key.jsonl",
            require_complete=args.require_complete,
        )
        (args.output_dir / "review_analysis.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        exit_code = 0 if report["status"] == "ready_to_freeze_successor" else 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
