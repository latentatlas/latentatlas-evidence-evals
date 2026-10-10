"""Deterministic internal blind-review tooling for Authority-to-Action cases.

The review packet removes source case identifiers and all metadata. Review
answers are collected separately from the answer key so the reviewer can judge
the written evidence before seeing the expected action or reason code.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = REPO_ROOT / "evals" / "data" / "authority_action_cases_v0_6.jsonl"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "internal_review" / "authority_action_v0_8"
REVIEW_NAMESPACE = "authority-action-v0.8-internal-blind-review-20260727"
REVIEW_COLUMNS = (
    "review_id",
    "reviewer_id",
    "reviewed_action",
    "evidence_sufficient",
    "single_decision_clear",
    "realism_score",
    "difficulty_score",
    "issue_codes",
    "rationale_short",
)
VALID_ACTIONS = {"execute", "withhold", "unclear"}
VALID_TRI_STATE = {"yes", "no", "unclear"}
VALID_ISSUE_CODES = {
    "ambiguous_authority",
    "evidence_conflict",
    "evidence_missing",
    "label_leakage",
    "multiple_decisions_plausible",
    "none",
    "other",
    "terminology_unclear",
    "unrealistic_packet",
}
MASKED_PACKET_FORBIDDEN = {
    "expected_action",
    "expected_reason_code",
    "prompt_variant",
    "control_type",
    "pair_id",
    "__valid_",
    "__invalid_",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, ensure_ascii=False) + "\n")


def write_review_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in REVIEW_COLUMNS})


def read_review_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REVIEW_COLUMNS:
            raise ValueError(
                f"Review CSV columns must be exactly {REVIEW_COLUMNS}, got {reader.fieldnames}"
            )
        return [dict(row) for row in reader]


def opaque_order_key(case_id: str, namespace: str = REVIEW_NAMESPACE) -> str:
    """Return a stable opaque sort key without exposing source case semantics."""

    return sha256_bytes(f"{namespace}:{case_id}".encode("utf-8"))


def _require_dataset_shape(rows: Sequence[Mapping[str, Any]]) -> None:
    if len(rows) != 100:
        raise ValueError(f"Internal review requires exactly 100 cases, got {len(rows)}")
    case_ids = [str(row.get("id", "")) for row in rows]
    if any(not case_id for case_id in case_ids):
        raise ValueError("Every dataset row must have a non-empty id")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Dataset case IDs must be unique")
    for row in rows:
        if not isinstance(row.get("input"), str) or not str(row["input"]).strip():
            raise ValueError(f"{row.get('id')}: input must be non-empty text")
        if not isinstance(row.get("metadata"), Mapping):
            raise ValueError(f"{row.get('id')}: metadata must be an object")


def build_review_rows(
    dataset_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build packet, blank response rows, and a separately stored answer key."""

    _require_dataset_shape(dataset_rows)
    ordered = sorted(dataset_rows, key=lambda row: opaque_order_key(str(row["id"])))
    packet: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    answer_key: list[dict[str, Any]] = []

    for index, row in enumerate(ordered, start=1):
        review_id = f"IR-{index:03d}"
        metadata = row["metadata"]
        assert isinstance(metadata, Mapping)
        prompt = str(row["input"])
        packet.append({"review_id": review_id, "input": prompt})
        responses.append(
            {
                "review_id": review_id,
                "reviewer_id": "",
                "reviewed_action": "",
                "evidence_sufficient": "",
                "single_decision_clear": "",
                "realism_score": "",
                "difficulty_score": "",
                "issue_codes": "",
                "rationale_short": "",
            }
        )
        answer_key.append(
            {
                "review_id": review_id,
                "case_id": str(row["id"]),
                "case_sha256": sha256_bytes(
                    json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")
                ),
                "expected_action": str(metadata["expected_action"]),
                "expected_reason_code": str(metadata["expected_reason_code"]),
                "pair_id": str(metadata["pair_id"]),
                "prompt_variant": str(metadata["prompt_variant"]),
                "behavior_family": str(metadata["behavior_family"]),
                "difficulty_level": str(metadata["difficulty_level"]),
            }
        )
    validate_masked_packet(packet)
    return packet, responses, answer_key


def validate_masked_packet(packet: Sequence[Mapping[str, Any]]) -> None:
    if len(packet) != 100:
        raise ValueError(f"Masked packet must contain 100 cases, got {len(packet)}")
    review_ids = [str(row.get("review_id", "")) for row in packet]
    if review_ids != [f"IR-{index:03d}" for index in range(1, 101)]:
        raise ValueError("Masked packet review IDs must be contiguous and ordered")
    for row in packet:
        if set(row) != {"review_id", "input"}:
            raise ValueError(f"{row.get('review_id')}: masked packet contains extra fields")
        rendered = json.dumps(row, sort_keys=True).lower()
        leaked = sorted(token for token in MASKED_PACKET_FORBIDDEN if token in rendered)
        if leaked:
            raise ValueError(f"{row['review_id']}: masked packet leaks labels: {leaked}")


def build_review_artifacts(
    *,
    dataset_path: Path = DEFAULT_DATASET,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    rows = read_jsonl(dataset_path)
    packet, responses, answer_key = build_review_rows(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    packet_path = output_dir / "review_packet.jsonl"
    response_path = output_dir / "review_responses.csv"
    answer_key_path = output_dir / "answer_key.jsonl"
    manifest_path = output_dir / "review_manifest.json"
    write_jsonl(packet_path, packet)
    write_review_csv(response_path, responses)
    write_jsonl(answer_key_path, answer_key)
    manifest = {
        "schema_version": "authority_action_internal_blind_review_v0.8",
        "review_namespace": REVIEW_NAMESPACE,
        "review_type": "internal_blind_author_review",
        "status": "packet_ready_review_not_started",
        "dataset": {
            "path": str(dataset_path.relative_to(REPO_ROOT)),
            "sha256": sha256_file(dataset_path),
            "case_count": len(rows),
        },
        "artifacts": {
            "review_packet.jsonl": sha256_file(packet_path),
            "review_responses.csv": sha256_file(response_path),
            "answer_key.jsonl": sha256_file(answer_key_path),
        },
        "masking": {
            "source_case_ids_removed": True,
            "metadata_removed": True,
            "expected_actions_removed": True,
            "expected_reason_codes_removed": True,
            "opaque_deterministic_order": True,
            "answer_key_separate_from_review_packet": True,
        },
        "data_handling": {
            "contains_provider_transcripts": False,
            "contains_credentials": False,
            "contains_customer_data": False,
            "contains_personal_data": False,
            "local_working_artifact": True,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def parse_issue_codes(value: str) -> list[str]:
    codes = [part.strip() for part in value.split(";") if part.strip()]
    if not codes:
        return []
    invalid = sorted(set(codes) - VALID_ISSUE_CODES)
    if invalid:
        raise ValueError(f"Unknown issue codes: {invalid}")
    if "none" in codes and len(codes) > 1:
        raise ValueError("Issue code 'none' cannot be combined with another code")
    return sorted(set(codes))


def _validate_completed_response(row: Mapping[str, str]) -> dict[str, Any]:
    review_id = row["review_id"]
    if not row["reviewer_id"].strip():
        raise ValueError(f"{review_id}: reviewer_id is required")
    action = row["reviewed_action"].strip()
    if action not in VALID_ACTIONS:
        raise ValueError(f"{review_id}: invalid reviewed_action {action!r}")
    evidence = row["evidence_sufficient"].strip()
    if evidence not in VALID_TRI_STATE:
        raise ValueError(f"{review_id}: invalid evidence_sufficient {evidence!r}")
    clarity = row["single_decision_clear"].strip()
    if clarity not in VALID_TRI_STATE:
        raise ValueError(f"{review_id}: invalid single_decision_clear {clarity!r}")
    try:
        realism = int(row["realism_score"])
        difficulty = int(row["difficulty_score"])
    except ValueError as exc:
        raise ValueError(f"{review_id}: realism and difficulty scores must be integers") from exc
    if realism not in range(1, 6) or difficulty not in range(1, 6):
        raise ValueError(f"{review_id}: realism and difficulty scores must be 1-5")
    issue_codes = parse_issue_codes(row["issue_codes"])
    if not row["rationale_short"].strip():
        raise ValueError(f"{review_id}: rationale_short is required")
    return {
        **dict(row),
        "reviewed_action": action,
        "evidence_sufficient": evidence,
        "single_decision_clear": clarity,
        "realism_score": realism,
        "difficulty_score": difficulty,
        "issue_codes": issue_codes,
    }

def analyze_review(
    *,
    response_path: Path,
    answer_key_path: Path,
    require_complete: bool = False,
) -> dict[str, Any]:
    response_rows = read_review_csv(response_path)
    key_rows = read_jsonl(answer_key_path)
    key_by_id = {str(row["review_id"]): row for row in key_rows}
    if len(key_rows) != 100 or len(key_by_id) != 100:
        raise ValueError("Answer key must contain exactly 100 unique review IDs")
    if len(response_rows) != 100:
        raise ValueError("Review response file must contain exactly 100 rows")
    response_ids = [row["review_id"] for row in response_rows]
    if len(response_ids) != len(set(response_ids)) or set(response_ids) != set(key_by_id):
        raise ValueError("Review response IDs must match the answer key exactly")

    completed: list[dict[str, Any]] = []
    incomplete_ids: list[str] = []
    for row in response_rows:
        answer_fields = [row[column].strip() for column in REVIEW_COLUMNS[1:]]
        if not any(answer_fields):
            incomplete_ids.append(row["review_id"])
            continue
        if not all(answer_fields):
            raise ValueError(f"{row['review_id']}: partially completed response")
        completed.append(_validate_completed_response(row))
    if require_complete and incomplete_ids:
        raise ValueError(f"Review is incomplete: {len(incomplete_ids)} responses remain")

    issue_counts: Counter[str] = Counter()
    difficulty_counts: Counter[str] = Counter()
    behavior_counts: Counter[str] = Counter()
    flagged: list[dict[str, Any]] = []
    agreements = 0
    sufficient = 0
    clear = 0
    realism_total = 0
    difficulty_total = 0
    group_stats: dict[str, Counter[str]] = defaultdict(Counter)

    for response in completed:
        key = key_by_id[response["review_id"]]
        agrees = response["reviewed_action"] == key["expected_action"]
        agreements += int(agrees)
        sufficient += int(response["evidence_sufficient"] == "yes")
        clear += int(response["single_decision_clear"] == "yes")
        realism_total += int(response["realism_score"])
        difficulty_total += int(response["difficulty_score"])
        for code in response["issue_codes"]:
            issue_counts[code] += 1
        difficulty_counts[str(key["difficulty_level"])] += 1
        behavior_counts[str(key["behavior_family"])] += 1
        group = group_stats[str(key["pair_id"])]
        group["reviewed"] += 1
        group["agreements"] += int(agrees)
        needs_adjudication = (
            not agrees
            or response["evidence_sufficient"] != "yes"
            or response["single_decision_clear"] != "yes"
            or int(response["realism_score"]) < 3
            or any(code != "none" for code in response["issue_codes"])
        )
        if needs_adjudication:
            flagged.append(
                {
                    "review_id": response["review_id"],
                    "case_id": key["case_id"],
                    "expected_action": key["expected_action"],
                    "reviewed_action": response["reviewed_action"],
                    "evidence_sufficient": response["evidence_sufficient"],
                    "single_decision_clear": response["single_decision_clear"],
                    "realism_score": response["realism_score"],
                    "issue_codes": response["issue_codes"],
                    "rationale_short": response["rationale_short"],
                }
            )

    completed_count = len(completed)
    if incomplete_ids:
        status = "incomplete"
    elif flagged:
        status = "needs_adjudication"
    else:
        status = "ready_to_freeze_successor"
    return {
        "schema_version": "authority_action_internal_blind_review_analysis_v0.8",
        "status": status,
        "review_type": "internal_blind_author_review",
        "reviewed_cases": completed_count,
        "total_cases": 100,
        "incomplete_count": len(incomplete_ids),
        "incomplete_review_ids": incomplete_ids,
        "action_agreement_count": agreements,
        "action_agreement_rate": round(agreements / completed_count, 4) if completed_count else None,
        "evidence_sufficient_yes_count": sufficient,
        "single_decision_clear_yes_count": clear,
        "mean_realism_score": round(realism_total / completed_count, 3) if completed_count else None,
        "mean_difficulty_score": round(difficulty_total / completed_count, 3) if completed_count else None,
        "issue_code_counts": dict(sorted(issue_counts.items())),
        "reviewed_difficulty_counts": dict(sorted(difficulty_counts.items())),
        "reviewed_behavior_family_counts": dict(sorted(behavior_counts.items())),
        "pair_group_summary": {
            pair_id: dict(sorted(counts.items()))
            for pair_id, counts in sorted(group_stats.items())
        },
        "adjudication_required_count": len(flagged),
        "adjudication_queue": flagged,
        "full_run_gate": {
            "review_complete": not incomplete_ids,
            "adjudication_complete": not flagged and not incomplete_ids,
            "full_run_enabled": False,
            "next_action": (
                "complete_review"
                if incomplete_ids
                else "adjudicate_flagged_cases"
                if flagged
                else "freeze_v0_8_dataset_and_create_budget_manifest"
            ),
        },
    }
