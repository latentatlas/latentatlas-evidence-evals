#!/usr/bin/env python3
"""Build the public-safe publication package for the authority-leases paper.

The public package integrates the concurrency closure artifacts into a bounded
technical report:

- front-loaded claim scope,
- fail-closed required-field contract,
- synthetic negative controls,
- local baseline replay,
- explicit validity boundaries.

It remains a bounded technical report. It does not promote population rates,
reviewer reliability, independent benchmark validation, or production/customer
truth claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_MANUSCRIPT_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_submission_manuscript_v2/"
    "action_time_p0_submission_manuscript_summary.json"
)
DEFAULT_UNIT_DEDUP_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_unit_definition_dedup_v1/"
    "action_time_p0_unit_definition_dedup_summary.json"
)
DEFAULT_CLOSURE_SUMMARY = Path(
    "outputs/latentatlas/concurrency_closure_pack_20260718/concurrency_closure_summary.json"
)
DEFAULT_FIGURE_TABLE_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_figure_table_pack_v3/action_time_p0_figure_table_pack_summary.json"
)
DEFAULT_OVERCLAIM_AUDIT_SUMMARY = Path(
    "outputs/latentatlas/action_time_p0_overclaim_audit_v4/action_time_p0_overclaim_audit_summary.json"
)
DEFAULT_OUT_DIR = Path("outputs/latentatlas/action_time_p0_publication_package_v3")

PUBLICATION_SCHEMA_VERSION = "latentatlas_action_time_p0_publication_package_v3"
TITLE = "Authority Leases and Concurrent Evidence Failure in Safe Agentic Execution"
SUBTITLE = "Evidence Is Not Action Permission"
PUBLIC_RESEARCH_LEVEL = "bounded_technical_report_pre_independent_benchmark"
AUTHOR_NAME = "Huseyin Buldurgan"
AFFILIATION = "LatentAtlas"
CONTACT = "huseyin@latentatlas.ai"
PUBLICATION_DATE = "2026-07-18"
PUBLIC_VERSION_LABEL = "bounded public research note"

FAMILY_PUBLIC_NAMES = {
    "stale_read": "Stale evidence read",
    "identity_time_split": "Identity and timing split",
    "authority_expiry": "Expired or missing authority",
    "materialization_race": "State changed before execution",
    "visibility_truth_confusion": "Visibility mistaken for truth",
    "context_contamination": "Outside-context contamination",
}

OUTCOME_PUBLIC_NAMES = {
    "correct_block": "packet-supported block",
    "false_block": "packet-unsupported block",
    "needs_more_evidence": "insufficient evidence",
    "identity_conflict_masked": "masked identity conflict",
}

REVIEW_LABEL_ROWS = [
    (
        "Packet-supported block",
        "The conservative block or revalidation decision was supported by evidence visible in the review packet.",
    ),
    (
        "Packet-unsupported block",
        "The review packet did not support the conservative block as warranted.",
    ),
    (
        "Insufficient evidence",
        "The packet did not contain enough evidence to judge whether the block was supported or unsupported.",
    ),
]

ADDITIONAL_REFERENCES = [
    {
        "key": "Gray1989",
        "citation": "Gray, C. and Cheriton, D. (1989). Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency. SOSP 1989.",
        "url": "https://dl.acm.org/doi/10.1145/74850.74870",
        "use": "Positions leases as an established distributed-systems mechanism; this report adapts the lease idea to AI action authority rather than claiming the base mechanism is new.",
    },
    {
        "key": "Birgisson2014",
        "citation": "Birgisson, A. et al. (2014). Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud.",
        "url": "https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/",
        "use": "Frames contextual caveats and capability-style authorization as prior work for conditional execution authority.",
    },
    {
        "key": "NIST800207",
        "citation": "Rose, S. et al. (2020). Zero Trust Architecture. NIST Special Publication 800-207.",
        "url": "https://doi.org/10.6028/NIST.SP.800-207",
        "use": "Frames continuous verification and policy-aware access decisions as security prior art.",
    },
    {
        "key": "OpenIDSSF",
        "citation": "OpenID Foundation. Shared Signals Framework and Continuous Access Evaluation Profile specifications.",
        "url": "https://openid.net/wg/sharedsignals/",
        "use": "Positions continuous access evaluation as adjacent authority-state revalidation work.",
    },
    {
        "key": "Zanzibar2019",
        "citation": "Pang, R. et al. (2019). Zanzibar: Google's Consistent, Global Authorization System. USENIX ATC 2019.",
        "url": "https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/",
        "use": "Positions consistency and authorization checks as prior work for action-time authority alignment.",
    },
    {
        "key": "AIRGuard2026",
        "citation": "Qin, S. et al. (2026). AIRGuard: Guarding Agent Actions with Runtime Authority Control. arXiv:2605.28914.",
        "url": "https://arxiv.org/abs/2605.28914",
        "use": "Directly adjacent agentic runtime authority-control work that the paper must position against before stronger novelty claims.",
    },
]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table_row(cells: list[Any]) -> str:
    return "| " + " | ".join(str(cell) for cell in cells) + " |"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    return [table_row(headers), table_row(["---" for _ in headers]), *[table_row(row) for row in rows]]


def pct(value: Any) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return str(value)


def metric_by_id(metrics: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row.get("metric_id", ""): row for row in metrics}


def reference_entries(references: list[dict[str, Any]]) -> list[str]:
    entries: list[str] = []
    for ref in references:
        key = ref.get("key", "")
        citation = ref.get("citation", "")
        url = ref.get("url", "")
        entries.append(f"- [{key}] {citation} Link: {url}")
    return entries


def merged_references(references: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ref in [*references, *ADDITIONAL_REFERENCES]:
        key = str(ref.get("key", "")).strip()
        if not key or key in seen:
            continue
        merged.append(ref)
        seen.add(key)
    return merged


def public_text(value: Any) -> str:
    text = str(value)
    replacements = {
        "P0 packets": "high-priority packets",
        "P0 packet": "high-priority packet",
        "P0 rows": "high-priority rows",
        "P0 row": "high-priority row",
        "P0 set": "high-priority set",
        "P0 review set": "high-priority review set",
        "P0 observations": "high-priority observations",
        "P0": "high-priority",
        "PDP": "product-detail-page",
        "Reviewer02": "a second independent reviewer",
        "reviewer02": "second independent reviewer",
        "internal-shadow": "masked internal review",
        "packet-visible evidence": "evidence visible in the review packet",
        "Packet-visible evidence": "Evidence visible in the review packet",
        "packet-visible": "review-packet",
        "Packet-visible": "Review-packet",
        "correct-block": "packet-supported block",
        "false-block": "packet-unsupported block",
        "needs-more-evidence": "insufficient evidence",
        "correct_block": "packet-supported block",
        "false_block": "packet-unsupported block",
        "needs_more_evidence": "insufficient evidence",
        "identity_conflict_masked": "masked identity conflict",
        "subject_cluster": "review topic group",
        "identity-guard": "identity guard",
    }
    for needle, replacement in replacements.items():
        text = text.replace(needle, replacement)
    return text


def public_family_name(family_id: Any) -> str:
    return FAMILY_PUBLIC_NAMES.get(str(family_id), public_text(str(family_id).replace("_", " ")).title())


def public_bool(value: Any) -> str:
    return "yes" if value is True else "no" if value is False else str(value)


def public_relationship(value: Any) -> str:
    relationships = {
        "same_set": "same set",
        "subset_of_family_b": "inside Family B",
        "superset_of_family_b": "contains Family B",
        "partial_overlap": "partial overlap",
        "disjoint": "no overlap",
    }
    return relationships.get(str(value), public_text(str(value).replace("_", " ")))


def concurrent_rows(concurrency: dict[str, Any]) -> list[list[Any]]:
    return [
        [
            public_family_name(family.get("family_id", "")),
            f"{family.get('numerator', '')}/{family.get('denominator', '')}",
            public_text(family.get("local_observation", "")),
            public_text(family.get("claim_boundary", "")),
        ]
        for family in concurrency.get("failure_families", [])
    ]


def replay_rows(closure: dict[str, Any]) -> list[list[Any]]:
    rows = []
    for row in closure.get("baseline_replay", []):
        rows.append(
            [
                public_family_name(row.get("family_id", "")),
                row.get("rows_replayed", ""),
                row.get("decision_time_only_block_count", ""),
                row.get("action_time_policy_block_count", ""),
                f"{row.get('action_time_policy_hold_or_revalidate_count', '')} ({pct(row.get('local_avoidable_overblock_or_hold_rate', ''))})",
            ]
        )
    return rows


def overlap_rows(closure: dict[str, Any]) -> list[list[Any]]:
    rows = []
    for row in closure.get("family_overlap_matrix", []):
        family_a = str(row.get("family_a", ""))
        family_b = str(row.get("family_b", ""))
        try:
            overlap_count = int(row.get("overlap_count", 0))
        except (TypeError, ValueError):
            overlap_count = 0
        if family_a >= family_b or overlap_count == 0:
            continue
        rows.append(
            [
                public_family_name(family_a),
                public_family_name(family_b),
                row.get("family_a_count", ""),
                row.get("family_b_count", ""),
                overlap_count,
                public_relationship(row.get("relationship", "")),
            ]
        )
    return rows


def short_sha(value: Any) -> str:
    text = str(value or "")
    return text[:12] if text else ""


def supplementary_rows(summary: dict[str, Any]) -> list[list[Any]]:
    integrity = summary.get("artifact_integrity", {})
    return [
        [
            "Closure summary",
            "local supplementary closure artifact",
            short_sha(integrity.get("closure_summary_sha256", "")),
        ],
        [
            "Replay policy disclosure",
            "local supplementary replay-disclosure artifact",
            short_sha(integrity.get("policy_source_sha256", "")),
        ],
        [
            "Family overlap matrix",
            "local supplementary overlap-matrix artifact",
            short_sha(integrity.get("family_overlap_matrix_sha256", "")),
        ],
        [
            "Figure and table pack",
            "local supplementary figure-table artifact",
            short_sha(integrity.get("figure_table_summary_sha256", "")),
        ],
        [
            "Public paper source",
            "generated public manuscript artifact",
            "generated",
        ],
    ]


def safe_concurrency_claim(concurrency: dict[str, Any]) -> str:
    raw_claim = str(concurrency.get("short_claim", "")).strip()
    if not raw_claim:
        return (
            "This paper treats Concurrent Evidence Failure as a recurring local "
            "failure family in the frozen masked high-priority evidence chain, not as a "
            "population-wide statement about most agentic AI failures."
        )
    if raw_claim.lower().startswith("many agentic ai failures"):
        return (
            "The frozen masked high-priority review supports a bounded claim: a recurring "
            "class of agentic workflow failures can be explained as evidence-"
            "concurrency failures, where decision-time evidence no longer "
            "authorizes action-time execution."
        )
    return raw_claim


def blocked_summary(reason: str, paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_action_time_p0_publication_package",
        "publication_schema_version": PUBLICATION_SCHEMA_VERSION,
        "status": "blocked",
        "failure_reasons": [reason],
        "research_level": "blocked",
        "publication_readiness": "blocked",
        "level4_probability_claim_allowed": False,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def build_summary(
    manuscript_summary: dict[str, Any],
    unit_summary: dict[str, Any],
    closure_summary: dict[str, Any],
    figure_table_summary: dict[str, Any],
    overclaim_summary: dict[str, Any],
    paths: dict[str, Path],
    inputs: dict[str, Path],
) -> dict[str, Any]:
    gates = {
        "manuscript_summary": manuscript_summary.get("status") == "pass",
        "unit_dedup_summary": unit_summary.get("status") == "pass",
        "concurrency_closure_summary": closure_summary.get("status") == "pass",
        "figure_table_summary": figure_table_summary.get("status") == "pass",
        "overclaim_audit_summary": overclaim_summary.get("status") == "pass",
        "level4_still_blocked": closure_summary.get("level4_probability_claim_allowed") is False,
        "negative_control_assertions": closure_summary.get("negative_assertion_fail_count") == 0,
    }
    failed = [name for name, ok in gates.items() if not ok]
    if failed:
        return blocked_summary(f"publication readiness gate failed: {', '.join(failed)}", paths)

    concurrency = dict(manuscript_summary.get("concurrent_evidence_failure", {}))
    concurrency["short_claim"] = safe_concurrency_claim(concurrency)

    return {
        "generated_at_utc": utc_now(),
        "mode": "latentatlas_action_time_p0_publication_package",
        "publication_schema_version": PUBLICATION_SCHEMA_VERSION,
        "status": "pass",
        "title": TITLE,
        "subtitle": SUBTITLE,
        "author": {
            "name": AUTHOR_NAME,
            "affiliation": AFFILIATION,
            "date": PUBLICATION_DATE,
            "version": PUBLIC_VERSION_LABEL,
            "contact": CONTACT,
        },
        "research_level": PUBLIC_RESEARCH_LEVEL,
        "publication_readiness": "not_yet_ready_for_public_release_until_author_attribution_and_citation_audit",
        "claim_level": "bounded_protocol_plus_frozen_set_descriptive_findings_plus_local_proxy_replay",
        "level4_probability_claim_allowed": False,
        "independent_benchmark_claim_allowed": False,
        "denominators": manuscript_summary.get("denominators", {}),
        "outcome_counts": manuscript_summary.get("outcome_counts", {}),
        "metrics": manuscript_summary.get("metrics", []),
        "references": merged_references(manuscript_summary.get("references", [])),
        "concurrent_evidence_failure": concurrency,
        "closure": {
            "closure_state": closure_summary.get("closure_state", ""),
            "workstream_count": closure_summary.get("workstream_count", 0),
            "required_field_contract_rows": closure_summary.get("required_field_contract_rows", 0),
            "required_field_fail_closed_rows": closure_summary.get("required_field_fail_closed_rows", 0),
            "negative_fixture_count": closure_summary.get("negative_fixture_count", 0),
            "negative_assertion_fail_count": closure_summary.get("negative_assertion_fail_count", 0),
            "baseline_replay_family_count": closure_summary.get("baseline_replay_family_count", 0),
            "stratified_backfill_target_count": closure_summary.get("stratified_backfill_target_count", 0),
            "baseline_replay": closure_summary.get("baseline_replay", []),
            "family_overlap_matrix": closure_summary.get("family_overlap_matrix", []),
            "replay_policy_disclosure": closure_summary.get("replay_policy_disclosure", {}),
            "artifact_integrity": closure_summary.get("artifact_integrity", {}),
            "outputs": closure_summary.get("outputs", {}),
        },
        "artifact_integrity": {
            "closure_summary_sha256": sha256_file(inputs["closure_summary"]),
            "figure_table_summary_sha256": sha256_file(inputs["figure_table_summary"]),
            "overclaim_audit_summary_sha256": sha256_file(inputs["overclaim_audit_summary"]),
            "policy_source_sha256": closure_summary.get("artifact_integrity", {}).get("policy_source_sha256", ""),
            "freeze_rows_sha256": closure_summary.get("artifact_integrity", {}).get("freeze_rows_sha256", ""),
            "family_overlap_matrix_sha256": (
                sha256_file(Path(closure_summary.get("outputs", {}).get("family_overlap_matrix", "")))
                if closure_summary.get("outputs", {}).get("family_overlap_matrix")
                and Path(closure_summary.get("outputs", {}).get("family_overlap_matrix", "")).exists()
                else ""
            ),
        },
        "figure_table_pack": {
            "figure_count": figure_table_summary.get("figure_count", 0),
            "rendered_figure_count": figure_table_summary.get("rendered_figure_count", 0),
            "rendered_png_count": figure_table_summary.get("rendered_png_count", 0),
            "caption_count": figure_table_summary.get("caption_count", 0),
            "table_count": figure_table_summary.get("table_count", 0),
            "table_row_counts": figure_table_summary.get("table_row_counts", {}),
        },
        "unit_dedup": {
            "event_level_count": unit_summary.get("event_level_count", 0),
            "subject_cluster_count": unit_summary.get("subject_cluster_count", 0),
            "duplicate_subject_cluster_count": unit_summary.get("duplicate_subject_cluster_count", 0),
            "second_reviewer_gate": unit_summary.get("recommendation", {}).get("second_reviewer_gate", ""),
        },
        "publication_quality_gates": gates,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "raw_source_rows_read": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "public_tone": "assertive_scope_aware_pre_benchmark",
        "claim_boundary": {
            "allowed_claims": [
                "Technical report / research note contribution.",
                "Frozen masked high-priority descriptive findings with explicit denominators.",
                "Concurrent Evidence Failure as a bounded descriptive research family.",
                "Fail-closed measurement contract and synthetic negative controls.",
                "Local proxy replay over frozen rows.",
            ],
            "blocked_claims": [
                "Population-level probability evidence.",
                "Population concurrency rates.",
                "Reviewer agreement or reliability claims.",
                "General agent accuracy or zero-risk claims.",
                "Customer-facing or production truth mutation.",
            ],
        },
        "inputs": {key: str(value) for key, value in inputs.items()},
        "outputs": {key: str(value) for key, value in paths.items()},
    }


def build_public_paper(summary: dict[str, Any]) -> str:
    if summary["status"] != "pass":
        return "\n".join([f"# {TITLE}", "", "Status: blocked", "", *summary.get("failure_reasons", [])])

    denominators = summary["denominators"]
    outcomes = summary["outcome_counts"]
    metrics = metric_by_id(summary["metrics"])
    references = summary["references"]
    unit = summary["unit_dedup"]
    concurrency = summary.get("concurrent_evidence_failure", {})
    closure = summary.get("closure", {})
    figure_pack = summary.get("figure_table_pack", {})
    author = summary.get("author", {})
    replay_disclosure = closure.get("replay_policy_disclosure", {})
    false_block = metrics.get("false_block_all_reviewed", {})
    nme = metrics.get("needs_more_evidence_all_reviewed", {})
    resolved_false_block = metrics.get("false_block_resolved_only", {})
    latest_pdp = metrics.get("latest_pdp_temporal_false_block", {})

    lines = [
        f"# {TITLE}",
        "",
        f"## {SUBTITLE}",
        "",
        f"Author: {author.get('name', AUTHOR_NAME)}",
        f"Affiliation: {author.get('affiliation', AFFILIATION)}",
        f"Date: {author.get('date', PUBLICATION_DATE)}",
        f"Version: {author.get('version', PUBLIC_VERSION_LABEL)}",
        f"Contact: {author.get('contact', CONTACT)}",
        "",
        "## Abstract",
        "",
        "This bounded technical report introduces authority leases for safe agentic execution: execution contracts that must still hold when a model, worker, tool, scheduler, or delegated automation acts. The report uses a frozen masked high-priority review set, fail-closed measurement checks, synthetic negative controls, and local proxy replay to describe a local class of action-time evidence-validity failures. It does not claim population-level probability, general failure rates, reviewer reliability, production validation, or customer outcome improvement.",
        "",
        "Agentic systems often make a decision before they act. A model, worker, automation, or delegated tool can inspect evidence, queue an action, and execute later. Between decision and action, identity, permission, policy, target state, availability, actor, impact, or timing can change.",
        "",
        "This paper argues that a recurring class of AI workflow failures is not best explained as generic reasoning error alone. In this class, the system acts on evidence whose freshness, identity, authority, visibility, or materialization timing no longer matches the action being taken.",
        "",
        "## Scope Of Claims",
        "",
        *markdown_table(
            ["Claim Area", "Supported Statement", "Boundary"],
            [
                [
                    "Protocol contribution",
                    "Authority leases define execution contracts that must still hold when a model, worker, tool, scheduler, or delegated automation acts.",
                    "Protocol proposal and engineering framework, not a production-effectiveness result.",
                ],
                [
                    "Empirical evidence",
                    "The frozen masked review set shows packet-supported, packet-unsupported, and insufficient-evidence states under a conservative review instrument.",
                    "Descriptive evidence over this frozen set only; no population rate or general failure probability.",
                ],
                [
                    "Failure-family model",
                    "Concurrent evidence failure describes cases where true or observed evidence is no longer action-valid because authority, identity, freshness, visibility, or state changed before execution.",
                    "Local diagnostic families and next-test structure; not independent prevalence evidence.",
                ],
                [
                    "Replay",
                    "The replay maps frozen review judgments into a stricter action-time authority framing.",
                    "Label-conditioned diagnostic mapping, not independent policy evaluation or causal proof.",
                ],
            ],
        ),
        "",
        "The central principle is:",
        "",
        "```text",
        "evidence is not action permission",
        "decision-time evidence is not execution-time authority",
        "true observation is not necessarily action-valid evidence",
        "```",
        "",
        "## Methods",
        "",
        "The unit of analysis is a specific attempted action evaluated from the evidence visible in its review packet. The evidence source is a frozen masked internal review set of high-priority action-time packets. The publication builder does not read raw customer rows, credentials, URLs, source systems, or production access.",
        "",
        "Each review-eligible packet is assigned one of three review judgments: packet-supported block, packet-unsupported block, or insufficient evidence. These judgments are not real-world ground truth. They state only whether the evidence visible in the review packet supported a conservative block, failed to support it, or left the case undecidable. The 5 rows that were insufficient before review remain outside the reviewed denominator rather than being silently converted into success or failure evidence.",
        "",
        "The current report adds three methodological controls: a required-field contract that fails closed when action-time fields are missing, synthetic negative controls for detector promotion, and a local counterfactual replay that compares a defined decision-time-only policy with an action-time authority policy. These controls improve auditability, but they do not establish prospective or population-level effect.",
        "",
        "## Contribution",
        "",
        "We introduce **authority leases**: bounded execution contracts that tie a prior decision to the actor, action, target, evidence, permission, policy, impact ceiling, and expiry state that made it valid. At action time, the system checks whether the lease still holds and recommends one of four lanes: dry-run execution, revalidation, block, or manual review.",
        "",
        "In operational form, an authority lease should carry at least: issuer; agent, worker, or session identity; permitted action; exact target identity and version; allowed argument constraints; evidence references and hashes; permission version; policy version; issue time; expiry time; revocation handle; impact or spending ceiling; delegation depth; single-use nonce or idempotency key; and revalidation triggers.",
        "",
        "We also define **Concurrent Evidence Failure**: a family of failures where evidence may be true or locally observed, but no longer action-valid because identity, freshness, authority, visibility, or materialization timing diverged before execution.",
        "",
        "## Formal Lease Validity Rule",
        "",
        "A lease is valid only when every execution precondition still matches the permission that justified the original decision. A minimal validity rule is:",
        "",
        "```text",
        "valid =",
        "    issuer_signature_valid",
        "    AND current_time within authority_window",
        "    AND actor matches",
        "    AND action matches",
        "    AND exact target and target_version match",
        "    AND arguments satisfy constraints",
        "    AND permission_version is current",
        "    AND policy_version is acceptable",
        "    AND authority is not revoked",
        "    AND impact is below ceiling",
        "    AND nonce has not been consumed",
        "    AND required evidence hashes still match",
        "```",
        "",
        "The lease check and the side effect must be bound to the same transaction precondition, compare-and-swap condition, idempotency key, or atomic commit. Otherwise, a system merely turns a decision-execution race into a smaller check-use race: the lease can validate, the target or permission can change, and the side effect can still execute under stale conditions.",
        "",
        "## Threat Model And Trust Boundary",
        "",
        "The model may request an action, but it must not mint, edit, or self-approve its own lease. The issuer is a trusted policy or orchestration component; the tool server must verify the lease before side effects; and the scheduler is treated as a delivery component, not an authority oracle.",
        "",
        "The verifier must handle clock skew with bounded tolerance, fresh revocation state, single-use nonce or idempotency enforcement, target-version checks, policy-version checks, and explicit delegation limits. A delegated subagent needs a lease scoped to its own actor, action, target, and impact ceiling. Replayed leases must fail after nonce consumption, expiry, revocation, target-version drift, permission-version drift, or evidence-hash mismatch.",
        "",
        "If the target system cannot enforce idempotency, version preconditions, or atomic side-effect commits, the lease should degrade to revalidation or manual review rather than being treated as sufficient execution authority.",
        "",
        "## Prior Work And Positioning",
        "",
        "The base mechanism is not presented as a new security primitive. Leases are established in distributed systems [Gray1989], and conditional authorization appears in capability-style systems [Birgisson2014], zero-trust access [NIST800207], continuous access evaluation [OpenIDSSF], and globally consistent authorization systems [Zanzibar2019]. The contribution here is narrower: applying a lease-like execution contract to agentic AI workflows where a model or delegated automation may move from evidence collection to side-effecting action after the decision context has changed.",
        "",
        "The paper is also adjacent to runtime authority-control work for agent actions [AIRGuard2026]. That related work strengthens the case for positioning this report as an evidence-boundary and execution-authority framework, not as proof that the proposed control has already reduced production failures.",
        "",
        "## Study",
        "",
        f"We evaluated the protocol on a frozen masked high-priority review set built from real action-time review packets. The set contains {denominators.get('p0_rows')} high-priority packets. Of these, {denominators.get('outcome_ready_p0_rows')} were review-eligible, {denominators.get('insufficient_for_outcome_adjudication_p0_rows')} were insufficient before review, and {denominators.get('frozen_reviewed_rows')} review-eligible packets were reviewed and frozen.",
        "",
        *markdown_table(
            ["Review Judgment", "Count", "Meaning"],
            [
                [REVIEW_LABEL_ROWS[0][0], outcomes.get("correct_block"), REVIEW_LABEL_ROWS[0][1]],
                [REVIEW_LABEL_ROWS[1][0], outcomes.get("false_block"), REVIEW_LABEL_ROWS[1][1]],
                [REVIEW_LABEL_ROWS[2][0], outcomes.get("needs_more_evidence"), REVIEW_LABEL_ROWS[2][1]],
            ],
        ),
        "",
        "The insufficient-evidence bucket is not discarded. It is a measured state of the review instrument: the packet requires additional evidence before it can become a supported or unsupported block judgment.",
        "",
        "## Findings",
        "",
        f"1. **Review completion:** {denominators.get('frozen_reviewed_rows')} of {denominators.get('outcome_ready_p0_rows')} review-eligible high-priority packets were reviewed and frozen.",
        f"2. **Packet-unsupported blocks are measurable:** {outcomes.get('false_block')} of {denominators.get('frozen_reviewed_rows')} reviewed packets were judged packet-unsupported ({pct(false_block.get('rate'))} of all reviewed packets; {pct(resolved_false_block.get('rate'))} of resolved packets).",
        f"3. **Evidence insufficiency is a first-class result:** {outcomes.get('needs_more_evidence')} reviewed packets remained insufficient-evidence judgments ({pct(nme.get('rate'))} of all reviewed packets).",
        "4. **Identity conflict behaved as block-supporting packet evidence in the reviewed set:** 4 of 4 masked identity-conflict packets were judged packet-supported blocks.",
        "5. **Blocked product-detail-page access was not outcome evidence:** 7 of 7 access-blocked product-detail-page packets remained insufficient-evidence judgments.",
        f"6. **Temporal authority matters:** {latest_pdp.get('numerator')} of {latest_pdp.get('denominator')} latest product-detail-page temporal-authority packets were judged packet-unsupported blocks.",
        "7. **Concurrent evidence failure is now a bounded, measurement-ready research family:** the method controls add a measurement contract, negative controls, and local replay while keeping stronger claims blocked.",
        "",
        "## Concurrent Evidence Failure Families",
        "",
        safe_concurrency_claim(concurrency),
        "",
        *markdown_table(["Family", "Local Count", "Observation", "Boundary"], concurrent_rows(concurrency)),
        "",
        "These rows are reported as local observations over the frozen evidence chain. They define failure families and next tests; they do not establish population rates.",
        "",
        "## Fail-Closed Measurement Contract",
        "",
        f"The current report adds a required-field contract with {closure.get('required_field_contract_rows')} required evidence fields. Of these, {closure.get('required_field_fail_closed_rows')} fail closed for the current reviewed set because exact action-time fields such as timestamps, authority windows, fetch state, or evidence-grounding fields are not yet present.",
        "",
        "This is an intentional measurement guardrail: missing action-time evidence does not get silently converted into a stronger claim. Rows with missing required fields remain bounded to the current descriptive report until the schema is upgraded.",
        "",
        "## Negative Controls",
        "",
        f"The current report adds {closure.get('negative_fixture_count')} synthetic positive/negative fixtures across the concurrency families. Assertion failures: {closure.get('negative_assertion_fail_count')}. These fixtures are not empirical outcome rows; they are guardrails for future detectors so that suspicious timing patterns are not automatically promoted into concurrency failures.",
        "",
        "## Local Baseline Replay",
        "",
        "The local replay compares a decision-time-only baseline with an action-time authority mapping over frozen rows. It is a label-conditioned diagnostic replay, not an independent policy engine, not causal proof, and not a claim about a live production policy.",
        "",
        *markdown_table(
            [
                "Family",
                "Rows",
                "Prior Blocks",
                "Lease Blocks",
                "Hold/Revalidate",
            ],
            replay_rows(closure),
        ),
        "",
        "## Replay Policy Disclosure",
        "",
        f"Replay disclosure: the replay is not independent of the review labels; the policy code reads review judgments: {public_bool(replay_disclosure.get('policy_code_reads_review_judgments', ''))}; thresholds tuned after results: {public_bool(replay_disclosure.get('thresholds_tuned_after_results', ''))}; execution mode: automatic local builder.",
        "",
        "The replay should therefore be read as a diagnostic description of how the frozen labels map into a stricter action-time authority framing. It does not show that an independent prospective policy would produce the same result.",
        "",
        "## Failure-Family Overlap",
        "",
        "The failure families are non-exclusive diagnostic slices. The overlap matrix is included so readers do not sum family rows as if they were independent evidence.",
        "",
        *markdown_table(["Family A", "Family B", "A Count", "B Count", "Overlap", "Relationship"], overlap_rows(closure)),
        "",
        "The strongest local signal appears in overlapping stale-evidence and state-changed-before-execution slices. That overlap strengthens the mechanism story, but it also limits how independently those family counts can be interpreted.",
        "",
        "## Unit And Deduplication",
        "",
        f"The primary unit is the attempted action event; the independence sensitivity unit is the review topic group. In the current frozen set, both denominators match: {unit.get('event_level_count')} event-level units and {unit.get('subject_cluster_count')} review topic groups. Duplicate topic groups: {unit.get('duplicate_subject_cluster_count')}.",
        "",
        "## Supporting Materials",
        "",
        f"The supplementary package includes {figure_pack.get('figure_count', 0)} conceptual figures, {figure_pack.get('caption_count', 0)} figure captions, and {figure_pack.get('table_count', 0)} publication tables. The access references and short hash prefixes below identify the local artifact versions used for this public note.",
        "",
        *markdown_table(["Material", "Access", "SHA-256 Prefix"], supplementary_rows(summary)),
        "",
        "## Evidence Upgrade Path",
        "",
        "Stronger empirical claims require independent blind review, disagreement adjudication, inter-rater agreement reporting, exact action-time schema fields, explicit baseline comparisons, stratified holdout or prospective evaluation, and joint safety-utility measurement. Until those gates exist, the result should be read as a protocol contribution and frozen-set descriptive finding.",
        "",
        "## What Would Prove Effectiveness",
        "",
        "A stronger empirical claim requires tests that the current report does not yet contain:",
        "",
        "- Independent blind review by at least two reviewers, disagreement adjudication, and inter-rater agreement reporting.",
        "- Comparison against explicit baselines such as current block policy, time-to-live-only checks, identity-only checks, and full authority leases.",
        "- Safety-utility metrics that separate wrong allow, unsupported block, completion rate, latency, human-review burden, and real downstream outcome.",
        "- Holdout or prospective evaluation on unseen cases before any production-effect claim.",
        "- Reproducible materials: schema, label guide, synthetic generator, policy code, fixtures, hashes, and run instructions.",
        "",
        "## Safety-Utility Boundary",
        "",
        "The current tables analyze blocking and hold/revalidate behavior. They do not measure wrong allow or unsafe authorization. A stronger security evaluation must jointly show that the control reduces unsupported blocks without increasing dangerous allows, and it must report completion rate, latency, human-review load, and downstream outcome impact.",
        "",
        "## Validity Boundaries",
        "",
        "- The evidence is a single frozen masked high-priority review set; it supports descriptive claims over this set, not population rates.",
        "- Review judgments evaluate packet support, not direct real-world safety, harm, customer outcome, or financial impact.",
        "- Reviewer reliability is not measured because independent blind review and adjudication are not yet complete.",
        "- The replay reads the review judgments, so it is a diagnostic mapping rather than independent policy validation.",
        "- The current evidence measures block and hold/revalidate behavior; wrong allow and unsafe authorization are not measured.",
        "- Required action-time fields fail closed when incomplete, which protects the claim boundary but limits family-specific measurement.",
        "",
        "## Reproducibility And Artifact Boundary",
        "",
        "The artifacts are generated locally. The builders produce a public paper, brief, supporting figures and tables, PDF, and post drafts. They do not call external services, read customer data, read raw source rows, use credentials, mutate production truth, or send public posts.",
        "",
        "## References",
        "",
        *reference_entries(references),
        "",
    ]
    return "\n".join(lines)


def build_public_brief(summary: dict[str, Any]) -> str:
    if summary["status"] != "pass":
        return "\n".join(["# Publication Brief", "", "Status: blocked"])

    denominators = summary["denominators"]
    outcomes = summary["outcome_counts"]
    closure = summary["closure"]
    lines = [
        "# Publication Brief",
        "",
        f"Title: {TITLE}: {SUBTITLE}",
        "",
        f"Author: {AUTHOR_NAME}",
        f"Affiliation: {AFFILIATION}",
        f"Date: {PUBLICATION_DATE}",
        f"Version: {PUBLIC_VERSION_LABEL}",
        f"Contact: {CONTACT}",
        "",
        "Claim scope: bounded protocol plus frozen-set descriptive findings plus local proxy replay. Not independent benchmark or population-level validation.",
        "",
        "Core claim:",
        "",
        "Authority at decision time should not be treated as authority at action time. Agentic systems need a bounded action-time lease that can be revalidated before execution.",
        "",
        "Method boundary:",
        "",
        "The unit is the attempted action event. Review judgments are assigned from evidence visible in the review packet only: packet-supported block, packet-unsupported block, or insufficient evidence. Insufficient evidence remains a separate measured state, not a hidden success or failure. The local replay is label-conditioned diagnostic replay, not an independent policy engine, causal proof, or a live production policy.",
        "",
        "Main evidence:",
        "",
        f"- Frozen masked high-priority review set: {denominators.get('frozen_reviewed_rows')} reviewed review-eligible packets.",
        f"- Review judgments: {outcomes.get('correct_block')} packet-supported blocks, {outcomes.get('false_block')} packet-unsupported blocks, {outcomes.get('needs_more_evidence')} insufficient-evidence cases.",
        f"- Method controls: {closure.get('workstream_count')} concurrency workstreams closed as bounded artifacts.",
        f"- Negative controls: {closure.get('negative_fixture_count')} synthetic fixtures, {closure.get('negative_assertion_fail_count')} assertion failures.",
        f"- Required fields: {closure.get('required_field_fail_closed_rows')} required evidence fields fail closed until schema upgrade.",
        f"- Local replay: {closure.get('baseline_replay_family_count')} family slices replayed.",
        "",
        "Blocked claims:",
        "",
        "- No population-level probability.",
        "- No population concurrency rate.",
        "- No reviewer agreement claim.",
        "- No production/customer truth claim.",
        "",
    ]
    return "\n".join(lines)


def run(
    manuscript_summary_path: Path = DEFAULT_MANUSCRIPT_SUMMARY,
    unit_dedup_summary_path: Path = DEFAULT_UNIT_DEDUP_SUMMARY,
    closure_summary_path: Path = DEFAULT_CLOSURE_SUMMARY,
    figure_table_summary_path: Path = DEFAULT_FIGURE_TABLE_SUMMARY,
    overclaim_audit_summary_path: Path = DEFAULT_OVERCLAIM_AUDIT_SUMMARY,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "paper": out_dir / "paper_public_v3.md",
        "brief": out_dir / "publication_brief_v3.md",
        "summary": out_dir / "publication_package_summary.json",
        "manifest": out_dir / "publication_package_manifest.json",
    }
    inputs = {
        "manuscript_summary": manuscript_summary_path,
        "unit_dedup_summary": unit_dedup_summary_path,
        "closure_summary": closure_summary_path,
        "figure_table_summary": figure_table_summary_path,
        "overclaim_audit_summary": overclaim_audit_summary_path,
    }
    missing = [str(path) for path in inputs.values() if not path.exists()]
    if missing:
        summary = blocked_summary(f"missing required sources: {', '.join(missing)}", paths)
    else:
        summary = build_summary(
            read_json(manuscript_summary_path),
            read_json(unit_dedup_summary_path),
            read_json(closure_summary_path),
            read_json(figure_table_summary_path),
            read_json(overclaim_audit_summary_path),
            paths,
            inputs,
        )

    write_text(paths["paper"], build_public_paper(summary))
    write_text(paths["brief"], build_public_brief(summary))
    write_json(paths["summary"], summary)
    manifest = {
        "generated_at_utc": summary["generated_at_utc"],
        "mode": summary["mode"],
        "publication_schema_version": summary.get("publication_schema_version", PUBLICATION_SCHEMA_VERSION),
        "status": summary["status"],
        "research_level": summary.get("research_level", ""),
        "publication_readiness": summary.get("publication_readiness", ""),
        "level4_probability_claim_allowed": False,
        "independent_benchmark_claim_allowed": False,
        "contains_customer_data": False,
        "contains_personal_data": False,
        "external_calls_used_by_builder": False,
        "production_truth_mutation": False,
        "outputs": summary["outputs"],
    }
    write_json(paths["manifest"], manifest)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manuscript-summary", type=Path, default=DEFAULT_MANUSCRIPT_SUMMARY)
    parser.add_argument("--unit-dedup-summary", type=Path, default=DEFAULT_UNIT_DEDUP_SUMMARY)
    parser.add_argument("--closure-summary", type=Path, default=DEFAULT_CLOSURE_SUMMARY)
    parser.add_argument("--figure-table-summary", type=Path, default=DEFAULT_FIGURE_TABLE_SUMMARY)
    parser.add_argument("--overclaim-audit-summary", type=Path, default=DEFAULT_OVERCLAIM_AUDIT_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(
        args.manuscript_summary,
        args.unit_dedup_summary,
        args.closure_summary,
        args.figure_table_summary,
        args.overclaim_audit_summary,
        args.out_dir,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if summary["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
