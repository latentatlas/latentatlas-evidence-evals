"""Build the 500-row Concept Boundary Engine fixture and proof artifacts."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROBE_PATH = Path(__file__).with_name("concept_boundary_probe.py")
SPEC = importlib.util.spec_from_file_location("concept_boundary_probe", PROBE_PATH)
probe = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(probe)

DEFAULT_OUTPUT = Path("research/concept_boundary_engine/concept_boundary_500_cases.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_engine_500")

ARCHETYPE_SPECS: list[dict[str, Any]] = [
    {
        "archetype": "related_does_not_grant_publish",
        "target_rows": 40,
        "requested_authority": "publish_safe",
        "boundary_type": "related",
        "source_authority": "medium",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "related_does_not_grant_publish_safe",
    },
    {
        "archetype": "peer_comparison_does_not_grant_identity",
        "target_rows": 50,
        "requested_authority": "same_identity",
        "boundary_type": "peer_comparison",
        "source_authority": "medium",
        "freshness_state": "current",
        "action_scope": "none",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "peer_comparison_does_not_grant_same_identity",
    },
    {
        "archetype": "bridge_context_does_not_grant_evidence",
        "target_rows": 40,
        "requested_authority": "evidence_support",
        "boundary_type": "bridge_context",
        "source_authority": "medium",
        "freshness_state": "current",
        "action_scope": "none",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "bridge_context_does_not_grant_evidence_support",
    },
    {
        "archetype": "evidence_does_not_grant_action",
        "target_rows": 45,
        "requested_authority": "action_ready",
        "boundary_type": "evidence_support",
        "source_authority": "authoritative",
        "freshness_state": "current",
        "action_scope": "none",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "evidence_support_does_not_grant_action_ready",
    },
    {
        "archetype": "evidence_does_not_grant_publish",
        "target_rows": 45,
        "requested_authority": "publish_safe",
        "boundary_type": "evidence_support",
        "source_authority": "authoritative",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "evidence_support_does_not_grant_publish_safe",
    },
    {
        "archetype": "stale_or_superseded_evidence_blocks_use",
        "target_rows": 45,
        "requested_authority": "evidence_support",
        "boundary_type": "evidence_support",
        "source_authority": "authoritative",
        "freshness_state": "stale",
        "action_scope": "none",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "freshness_blocks_use",
    },
    {
        "archetype": "contradiction_blocks_allow",
        "target_rows": 45,
        "requested_authority": "evidence_support",
        "boundary_type": "contradiction",
        "source_authority": "authoritative",
        "freshness_state": "current",
        "action_scope": "none",
        "contains_sensitive_data": False,
        "expected_decision": "block_contradiction",
        "expected_reason_family": "candidate_contradicts_requested_claim",
    },
    {
        "archetype": "privacy_blocks_all_downstream_use",
        "target_rows": 40,
        "requested_authority": "customer_safe",
        "boundary_type": "privacy_blocked",
        "source_authority": "internal",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": True,
        "expected_decision": "block_privacy",
        "expected_reason_family": "privacy_boundary_blocks_all_use",
    },
    {
        "archetype": "valid_evidence_support",
        "target_rows": 45,
        "requested_authority": "evidence_support",
        "boundary_type": "evidence_support",
        "source_authority": "authoritative",
        "freshness_state": "current",
        "action_scope": "none",
        "contains_sensitive_data": False,
        "expected_decision": "allow_evidence",
        "expected_reason_family": "boundary_grants_evidence_support",
    },
    {
        "archetype": "valid_action_ready",
        "target_rows": 40,
        "requested_authority": "action_ready",
        "boundary_type": "action_ready",
        "source_authority": "authoritative",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": False,
        "expected_decision": "allow_action",
        "expected_reason_family": "boundary_grants_action_ready",
    },
    {
        "archetype": "valid_publish_safe",
        "target_rows": 35,
        "requested_authority": "publish_safe",
        "boundary_type": "publish_safe",
        "source_authority": "authoritative",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": False,
        "expected_decision": "allow_publish",
        "expected_reason_family": "boundary_grants_publish_safe",
    },
    {
        "archetype": "adversarial_mixed_cases",
        "target_rows": 30,
        "requested_authority": "publish_safe",
        "boundary_type": "related",
        "source_authority": "medium",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "multi_signal_false_authority",
    },
]

TOPICS = [
    "refund policy",
    "procurement approval",
    "support escalation",
    "contract renewal",
    "invoice exception",
    "account termination",
    "vendor onboarding",
    "security exception",
    "pricing approval",
    "customer alert",
]

OBJECTS = [
    "policy row",
    "ticket excerpt",
    "knowledge-base article",
    "contract clause",
    "operator note",
    "dashboard row",
    "search result",
    "release note",
]

FRESHNESS_CYCLE = ["stale", "superseded", "expired", "deprecated"]

ADVERSARIAL_OVERRIDES = [
    {
        "requested_authority": "customer_safe",
        "boundary_type": "privacy_blocked",
        "source_authority": "internal",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": True,
        "expected_decision": "block_privacy",
        "expected_reason_family": "privacy_boundary_blocks_all_use",
    },
    {
        "requested_authority": "evidence_support",
        "boundary_type": "contradiction",
        "source_authority": "authoritative",
        "freshness_state": "current",
        "action_scope": "none",
        "contains_sensitive_data": False,
        "expected_decision": "block_contradiction",
        "expected_reason_family": "candidate_contradicts_requested_claim",
    },
    {
        "requested_authority": "publish_safe",
        "boundary_type": "publish_safe",
        "source_authority": "low",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "source_authority_low",
    },
    {
        "requested_authority": "action_ready",
        "boundary_type": "action_ready",
        "source_authority": "authoritative",
        "freshness_state": "expired",
        "action_scope": "approved",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "freshness_state_expired",
    },
    {
        "requested_authority": "customer_safe",
        "boundary_type": "related",
        "source_authority": "medium",
        "freshness_state": "current",
        "action_scope": "approved",
        "contains_sensitive_data": False,
        "expected_decision": "block_false_authority",
        "expected_reason_family": "related_does_not_grant_customer_safe",
    },
]


def similarity_score(index: int) -> float:
    return round(0.84 + ((index * 7) % 14) * 0.01, 2)


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    global_index = 1
    for spec in ARCHETYPE_SPECS:
        for local_index in range(1, spec["target_rows"] + 1):
            row_spec = dict(spec)
            if spec["archetype"] == "adversarial_mixed_cases":
                row_spec.update(ADVERSARIAL_OVERRIDES[(local_index - 1) % len(ADVERSARIAL_OVERRIDES)])
            if spec["archetype"] == "stale_or_superseded_evidence_blocks_use":
                row_spec["freshness_state"] = FRESHNESS_CYCLE[(local_index - 1) % len(FRESHNESS_CYCLE)]
            rows.append(build_row(row_spec, global_index, local_index))
            global_index += 1
    return rows


def build_row(spec: dict[str, Any], global_index: int, local_index: int) -> dict[str, Any]:
    topic = TOPICS[(global_index - 1) % len(TOPICS)]
    object_name = OBJECTS[(global_index + local_index - 2) % len(OBJECTS)]
    requested = spec["requested_authority"].replace("_", " ")
    boundary = spec["boundary_type"].replace("_", " ")
    case_id = f"cbe500-{global_index:04d}"
    return {
        "case_id": case_id,
        "query": f"Can this {topic} item be treated as {requested} for case {global_index}?",
        "candidate": candidate_text(spec, topic, object_name, local_index),
        "similarity_score": similarity_score(global_index),
        "requested_authority": spec["requested_authority"],
        "boundary_type": spec["boundary_type"],
        "source_authority": spec["source_authority"],
        "freshness_state": spec["freshness_state"],
        "action_scope": spec["action_scope"],
        "contains_sensitive_data": spec["contains_sensitive_data"],
        "expected_decision": spec["expected_decision"],
        "archetype": spec["archetype"],
        "variation_id": f"{spec['archetype']}-{local_index:03d}",
        "expected_reason_family": spec["expected_reason_family"],
        "synthetic_object": object_name,
        "boundary_note": f"{boundary} requested as {requested}",
    }


def candidate_text(spec: dict[str, Any], topic: str, object_name: str, local_index: int) -> str:
    boundary = spec["boundary_type"]
    requested = spec["requested_authority"]
    if boundary == "privacy_blocked":
        return (
            f"The {object_name} mentions {topic}, but includes a private tenant marker "
            f"and must not be reused for {requested}. Synthetic variation {local_index}."
        )
    if boundary == "contradiction":
        return (
            f"The authoritative {object_name} discusses {topic} and directly says the "
            f"requested claim is not allowed. Synthetic variation {local_index}."
        )
    if spec["freshness_state"] in FRESHNESS_CYCLE:
        return (
            f"The {object_name} supports {topic}, but its state is "
            f"{spec['freshness_state']} and it cannot support current use."
        )
    if boundary == "related":
        return (
            f"The {object_name} uses similar {topic} language, but only establishes "
            f"topic relatedness, not downstream authority."
        )
    if boundary == "peer_comparison":
        return (
            f"The {object_name} describes a comparable {topic} item with similar "
            f"attributes but a different identity."
        )
    if boundary == "bridge_context":
        return (
            f"The {object_name} is a navigation or glossary bridge for {topic}; it "
            f"points to context but is not direct proof."
        )
    if boundary == "evidence_support" and requested in {"action_ready", "publish_safe"}:
        return (
            f"The {object_name} supports the {topic} claim, but does not authorize "
            f"the requested downstream step."
        )
    if spec["expected_decision"].startswith("allow"):
        return (
            f"The current authoritative {object_name} directly supports {topic} and "
            f"the requested boundary conditions are satisfied."
        )
    return f"The {object_name} is a high-similarity synthetic {topic} candidate."


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_archetype_counts(path: Path, rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = dict(sorted(Counter(row["archetype"] for row in rows).items()))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["archetype", "row_count"])
        writer.writeheader()
        for archetype, row_count in counts.items():
            writer.writerow({"archetype": archetype, "row_count": row_count})
    return counts


def build_manifest(
    rows: list[dict[str, Any]],
    output: Path,
    out_dir: Path,
    summary: dict[str, Any],
    archetype_counts: dict[str, int],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "concept_boundary_500_fixture_builder",
        "status": "pass" if summary.get("status") == "pass" and len(rows) == 500 else "fail",
        "data_classification": "synthetic",
        "contains_customer_data": False,
        "external_services_used": False,
        "production_truth_mutation": False,
        "customer_surface_mutation": False,
        "row_count": len(rows),
        "archetype_count": len(archetype_counts),
        "archetype_counts": archetype_counts,
        "probe_summary": summary,
        "outputs": {
            "cases": str(output),
            "summary": str(out_dir / "summary.json"),
            "decisions": str(out_dir / "decisions.csv"),
            "report": str(out_dir / "report.md"),
            "archetype_counts": str(out_dir / "archetype_counts.csv"),
            "manifest": str(out_dir / "manifest.json"),
        },
        "commercial_boundary": {
            "buyer_facing_ready": summary.get("status") == "pass",
            "allowed_claim": "measured on a synthetic 500-row concept-boundary benchmark",
            "prohibited_claims": [
                "guarantees truth",
                "legal approval",
                "live customer deployment",
                "autonomous production write-back",
            ],
        },
    }


def run(output: Path = DEFAULT_OUTPUT, out_dir: Path = DEFAULT_OUT_DIR, threshold: float = 0.82) -> dict[str, Any]:
    rows = build_rows()
    write_jsonl(output, rows)
    summary = probe.run(output, out_dir, threshold)
    archetype_counts = write_archetype_counts(out_dir / "archetype_counts.csv", rows)
    manifest = build_manifest(rows, output, out_dir, summary, archetype_counts)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--threshold", type=float, default=0.82)
    args = parser.parse_args()
    manifest = run(args.output, args.out_dir, args.threshold)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

