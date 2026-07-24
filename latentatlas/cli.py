"""Command-line interface for the public LatentAtlas evaluation examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .action_time_revalidation import revalidate_action_packets
from .action_time_revalidation import summarize_action_revalidations
from .evidence_guard import EvidenceGuard
from .evidence_vector_layer import run_evidence_vector_layer
from .frozen_review import verify_frozen_review_artifact
from .verify_outputs import verify


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no} must contain a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def command_qualify(args: argparse.Namespace) -> int:
    packets = read_jsonl(args.input)
    guard = EvidenceGuard(policy="audit_safe")
    decisions = [guard.qualify_packet(packet) for packet in packets]
    write_jsonl(args.output, decisions)
    summary = verify(decisions, args.output)
    write_json(args.summary, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "pass" else 1


def command_vector_layer(args: argparse.Namespace) -> int:
    manifest = run_evidence_vector_layer(
        source_path=args.sources,
        query_path=args.queries,
        out_dir=args.out_dir,
        adapter="local",
        limit=args.limit,
        min_score=args.min_score,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["status"] == "pass" else 1


def command_revalidate(args: argparse.Namespace) -> int:
    packets = read_jsonl(args.input)
    decisions = revalidate_action_packets(packets)
    write_jsonl(args.output, decisions)
    summary = summarize_action_revalidations(
        input_path=args.input,
        output_path=args.output,
        decisions=decisions,
    )
    write_json(args.summary, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["unsafe_authorization_count"] == 0 else 1


def command_verify_frozen_review(args: argparse.Namespace) -> int:
    report = verify_frozen_review_artifact(args.artifact_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="latentatlas-evals",
        description="Run deterministic evidence and action-authority evaluations.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    qualify = subparsers.add_parser("qualify", help="Qualify candidate evidence packets")
    qualify.add_argument("--input", type=Path, required=True)
    qualify.add_argument("--output", type=Path, required=True)
    qualify.add_argument("--summary", type=Path, required=True)
    qualify.set_defaults(func=command_qualify)

    vector = subparsers.add_parser("run-vector-layer", help="Run the complete local evidence pipeline")
    vector.add_argument("--sources", type=Path, required=True)
    vector.add_argument("--queries", type=Path, required=True)
    vector.add_argument("--out-dir", type=Path, required=True)
    vector.add_argument("--limit", type=int, default=5)
    vector.add_argument("--min-score", type=float, default=0.01)
    vector.set_defaults(func=command_vector_layer)

    revalidate = subparsers.add_parser(
        "revalidate-actions",
        help="Check evidence, identity, policy, and permission immediately before action",
    )
    revalidate.add_argument("--input", type=Path, required=True)
    revalidate.add_argument("--output", type=Path, required=True)
    revalidate.add_argument("--summary", type=Path, required=True)
    revalidate.set_defaults(func=command_revalidate)

    frozen_review = subparsers.add_parser(
        "verify-frozen-review",
        help="Verify the public aggregate frozen-review artifact",
    )
    frozen_review.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("data/frozen_masked_review_v1"),
    )
    frozen_review.set_defaults(func=command_verify_frozen_review)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
