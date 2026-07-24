#!/usr/bin/env python3
"""Verify LatentAtlas qualify outputs against the product contract."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .evidence_guard import (
    RECOMMENDED_ACTIONS,
    RULE_VERSION,
    TERMINAL_EVIDENCE_VERDICTS,
    TERMINAL_IDENTITY_VERDICTS,
)


REQUIRED_FIELDS = {
    "decision_id",
    "rule_version",
    "semantic_similarity",
    "evidence_verdict",
    "identity_verdict",
    "recommended_action",
    "confidence",
    "reason_codes",
    "audit",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="LatentAtlas decisions JSONL")
    parser.add_argument("--summary", type=Path, help="Verification summary JSON")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Line {line_no} must be a JSON object")
            rows.append(row)
    return rows


def verify(rows: list[dict[str, Any]], input_path: Path) -> dict[str, Any]:
    failures = []
    evidence_counts = Counter()
    action_counts = Counter()
    for idx, row in enumerate(rows, start=1):
        missing = sorted(REQUIRED_FIELDS - set(row))
        if missing:
            failures.append({"line": idx, "failure": "missing_required_fields", "fields": missing})
            continue
        evidence_counts[row["evidence_verdict"]] += 1
        action_counts[row["recommended_action"]] += 1
        if row["rule_version"] != RULE_VERSION:
            failures.append({"line": idx, "failure": "unexpected_rule_version", "value": row["rule_version"]})
        if row["evidence_verdict"] not in TERMINAL_EVIDENCE_VERDICTS:
            failures.append({"line": idx, "failure": "invalid_evidence_verdict", "value": row["evidence_verdict"]})
        if row["identity_verdict"] not in TERMINAL_IDENTITY_VERDICTS:
            failures.append({"line": idx, "failure": "invalid_identity_verdict", "value": row["identity_verdict"]})
        if row["recommended_action"] not in RECOMMENDED_ACTIONS:
            failures.append({"line": idx, "failure": "invalid_recommended_action", "value": row["recommended_action"]})
        if not isinstance(row["reason_codes"], list) or not row["reason_codes"]:
            failures.append({"line": idx, "failure": "missing_reason_codes"})
        audit = row.get("audit") or {}
        if len(str(audit.get("input_hash", ""))) != 64:
            failures.append({"line": idx, "failure": "invalid_input_hash"})
        evidence_ids = audit.get("evidence_ids")
        if not isinstance(evidence_ids, list):
            failures.append({"line": idx, "failure": "missing_evidence_ids"})
            evidence_ids = []
        selected_ids = audit.get("selected_evidence_ids")
        if selected_ids is not None:
            if not isinstance(selected_ids, list):
                failures.append({"line": idx, "failure": "invalid_selected_evidence_ids"})
                selected_ids = []
            elif any(item not in evidence_ids for item in selected_ids):
                failures.append({"line": idx, "failure": "selected_evidence_id_not_in_input"})
        rejected_ids = audit.get("rejected_evidence_ids")
        if rejected_ids is not None:
            if not isinstance(rejected_ids, list):
                failures.append({"line": idx, "failure": "invalid_rejected_evidence_ids"})
            elif any(item not in evidence_ids for item in rejected_ids):
                failures.append({"line": idx, "failure": "rejected_evidence_id_not_in_input"})
        if row["evidence_verdict"] == "confirmed_evidence" and row["recommended_action"] == "allow_answer":
            if not selected_ids:
                failures.append({"line": idx, "failure": "confirmed_evidence_missing_selected_evidence"})
        if row["evidence_verdict"] in {"needs_context", "needs_review"} and row["recommended_action"] == "allow_answer":
            failures.append({"line": idx, "failure": "context_or_review_coerced_to_allow"})
        if row["recommended_action"] == "allow_answer" and row["evidence_verdict"] != "confirmed_evidence":
            failures.append({"line": idx, "failure": "false_evidence_allow"})

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "pass" if not failures else "fail",
        "input": str(input_path),
        "decision_count": len(rows),
        "failure_count": len(failures),
        "failure_sample": failures[:20],
        "evidence_verdict_counts": dict(sorted(evidence_counts.items())),
        "recommended_action_counts": dict(sorted(action_counts.items())),
    }


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.input)
    summary = verify(rows, args.input)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
