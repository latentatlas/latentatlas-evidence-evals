"""Deterministic evidence qualification for LatentAtlas.

This module implements deterministic evidence qualification, reason codes, and
replayable audit output for local JSONL evaluation packets.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, date, datetime
from itertools import combinations
from typing import Any


RULE_VERSION = "latentatlas_evidence_guard_v0"

ALLOWED_SOURCE_TYPES = {"doc", "ticket", "policy", "contract", "email", "web", "other"}

TERMINAL_EVIDENCE_VERDICTS = {
    "confirmed_evidence",
    "related_not_enough",
    "contradictory",
    "needs_context",
    "needs_review",
    "quarantine_false_neighbor",
}

TERMINAL_IDENTITY_VERDICTS = {
    "confirmed_same",
    "confirmed_not_same",
    "needs_context",
    "needs_review",
    "quarantine_false_neighbor",
}

RECOMMENDED_ACTIONS = {
    "allow_answer",
    "keep_separate",
    "request_more_context",
    "manual_review",
    "quarantine_do_not_use",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "if",
    "in",
    "is",
    "it",
    "may",
    "must",
    "of",
    "on",
    "or",
    "our",
    "should",
    "that",
    "the",
    "this",
    "to",
    "we",
    "when",
    "with",
}

CONTRADICTION_TERMS = {
    "cannot",
    "can't",
    "do not",
    "does not",
    "forbidden",
    "ineligible",
    "must not",
    "never",
    "no longer",
    "not allowed",
    "not eligible",
    "prohibited",
    "rejected",
}

INSUFFICIENT_CONTEXT_TERMS = {
    "cannot determine",
    "does not define",
    "does not include",
    "insufficient",
    "missing",
    "need review",
    "needs review",
    "not define",
    "not enough",
    "not the full",
    "outside this excerpt",
    "pending",
    "requires review",
}

WEAK_EVIDENCE_SURFACE_TERMS = {
    "glossary",
    "index entry",
    "keyword index",
    "mentions",
    "navigation aid",
    "not evidence",
    "phrase list",
    "reference terms",
    "search index",
    "searchable phrases",
    "separate workflow",
    "terminology index",
}

BLOCKING_SOURCE_STATUSES = {"archived", "deprecated", "draft", "retired", "superseded"}
BLOCKING_EFFECTIVE_STATES = {"expired", "inactive", "superseded"}
BLOCKING_REVIEW_STATES = {"stale"}
BLOCKING_SOURCE_AUTHORITIES = {"untrusted"}
CONTEXT_SOURCE_AUTHORITIES = {"low", "unknown"}
CONTEXT_REVIEW_STATES = {"review_overdue"}
CONSENSUS_REQUIRED_AXES = frozenset({"claim_subject", "approval_condition", "traceability"})
CONSENSUS_MIN_RETRIEVAL_SCORE = 0.60
CONSENSUS_MIN_LEXICAL_OVERLAP = 0.12
CONSENSUS_MIN_SPECIFICITY = 0.60


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def input_hash(packet: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(packet).encode("utf-8")).hexdigest()


def tokenize(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text.lower()))
    return {token for token in tokens if token not in STOPWORDS}


def lexical_overlap(query: str, evidence_text: str) -> float:
    query_tokens = tokenize(query)
    evidence_tokens = tokenize(evidence_text)
    if not query_tokens or not evidence_tokens:
        return 0.0
    return len(query_tokens & evidence_tokens) / len(query_tokens)


def clamp_score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, score))


def normalize_metadata_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        parts = re.split(r"[,|]", value)
        return [part.strip().lower() for part in parts if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    return [str(value).strip().lower()]


def parse_metadata_date(value: Any) -> date | None:
    if value in {None, ""}:
        return None
    text = str(value).strip()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None


def has_contradiction_signal(query: str, evidence: dict[str, Any]) -> bool:
    metadata = evidence.get("metadata") or {}
    if str(metadata.get("evidence_role", "")).lower() == "contradictory":
        return True
    text = str(evidence.get("text", "")).lower()
    if not any(term in text for term in CONTRADICTION_TERMS):
        return False
    strong_terms = CONTRADICTION_TERMS - {"cannot", "does not", "do not"}
    if has_insufficient_context_signal(evidence) and not any(term in text for term in strong_terms):
        return False
    # Require at least one shared non-stopword so generic negations do not overfire.
    return lexical_overlap(query, text) >= 0.12


def has_insufficient_context_signal(evidence: dict[str, Any]) -> bool:
    text = str(evidence.get("text", "")).lower()
    return any(term in text for term in INSUFFICIENT_CONTEXT_TERMS)


def has_weak_evidence_surface_signal(evidence: dict[str, Any]) -> bool:
    text = str(evidence.get("text", "")).lower()
    return any(term in text for term in WEAK_EVIDENCE_SURFACE_TERMS)


def provenance_assessment(evidence: dict[str, Any]) -> dict[str, Any]:
    metadata = evidence.get("metadata") or {}
    source_status = str(metadata.get("source_status", "")).strip().lower()
    effective_state = str(metadata.get("effective_state", "")).strip().lower()
    review_state = str(metadata.get("review_state", "")).strip().lower()
    source_authority = str(metadata.get("source_authority", "")).strip().lower()
    owner = str(metadata.get("owner", "")).strip()

    blocking_reasons: list[str] = []
    context_reasons: list[str] = []
    if source_status in BLOCKING_SOURCE_STATUSES:
        blocking_reasons.append(f"source_status_{source_status}")
    if effective_state in BLOCKING_EFFECTIVE_STATES:
        blocking_reasons.append(f"effective_state_{effective_state}")
    if review_state in BLOCKING_REVIEW_STATES:
        blocking_reasons.append(f"review_state_{review_state}")
    if source_authority in BLOCKING_SOURCE_AUTHORITIES:
        blocking_reasons.append(f"source_authority_{source_authority}")
    if source_authority in CONTEXT_SOURCE_AUTHORITIES:
        context_reasons.append(f"source_authority_{source_authority}")
    if review_state in CONTEXT_REVIEW_STATES:
        context_reasons.append(f"review_state_{review_state}")
    if source_status and source_status != "approved" and source_status not in BLOCKING_SOURCE_STATUSES:
        context_reasons.append(f"source_status_{source_status}")
    if source_authority and source_authority not in {
        "authoritative",
        "owner_approved",
        *BLOCKING_SOURCE_AUTHORITIES,
        *CONTEXT_SOURCE_AUTHORITIES,
    }:
        context_reasons.append(f"source_authority_{source_authority}")
    if "source_status" in metadata and source_status == "":
        context_reasons.append("missing_source_status")
    if "source_authority" in metadata and source_authority == "":
        context_reasons.append("missing_source_authority")
    if "owner" in metadata and not owner:
        context_reasons.append("missing_source_owner")

    return {
        "blocking": bool(blocking_reasons),
        "context": bool(context_reasons),
        "blocking_reasons": blocking_reasons,
        "context_reasons": context_reasons,
    }


def temporal_assessment(evidence: dict[str, Any]) -> dict[str, Any]:
    metadata = evidence.get("metadata") or {}
    as_of = parse_metadata_date(metadata.get("as_of_date")) or date.today()
    effective_from = parse_metadata_date(metadata.get("effective_from"))
    effective_to = parse_metadata_date(metadata.get("effective_to"))
    published_at = parse_metadata_date(metadata.get("published_at"))

    blocking_reasons: list[str] = []
    context_reasons: list[str] = []
    if effective_from and effective_from > as_of:
        blocking_reasons.append("temporal_future_effective")
    if effective_to and effective_to < as_of:
        blocking_reasons.append("temporal_expired")
    if str(metadata.get("superseded_by", "")).strip():
        blocking_reasons.append("temporal_superseded")
    if "effective_from" in metadata and metadata.get("effective_from") and effective_from is None:
        context_reasons.append("invalid_effective_from")
    if "effective_to" in metadata and metadata.get("effective_to") and effective_to is None:
        context_reasons.append("invalid_effective_to")
    if "published_at" in metadata and metadata.get("published_at") and published_at is None:
        context_reasons.append("invalid_published_at")
    if "as_of_date" in metadata and metadata.get("as_of_date") and parse_metadata_date(metadata.get("as_of_date")) is None:
        context_reasons.append("invalid_as_of_date")

    return {
        "blocking": bool(blocking_reasons),
        "context": bool(context_reasons),
        "blocking_reasons": blocking_reasons,
        "context_reasons": context_reasons,
    }


def evidence_specificity(evidence: dict[str, Any]) -> float:
    score = 0.0
    if str(evidence.get("evidence_id", "")).strip():
        score += 0.25
    if str(evidence.get("source_type", "")).strip() in ALLOWED_SOURCE_TYPES - {"other"}:
        score += 0.25
    if str(evidence.get("source_uri", "")).strip():
        score += 0.20
    if len(str(evidence.get("text", "")).strip()) >= 80:
        score += 0.20
    metadata = evidence.get("metadata") or {}
    if metadata:
        score += 0.10
    return min(1.0, score)


def covers_consensus_required_axes(item: dict[str, Any]) -> bool:
    support_axes = set(item.get("support_axes") or [])
    return bool(support_axes) and CONSENSUS_REQUIRED_AXES.issubset(support_axes)


def evidence_axes_allow_direct(item: dict[str, Any]) -> bool:
    support_axes = set(item.get("support_axes") or [])
    return not support_axes or CONSENSUS_REQUIRED_AXES.issubset(support_axes)


def select_multi_source_consensus(candidates: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
    ranked = sorted(
        candidates,
        key=lambda item: (
            len(set(item["support_axes"]) & CONSENSUS_REQUIRED_AXES),
            item["retrieval_score"],
            item["overlap"],
            item["specificity"],
        ),
        reverse=True,
    )[:8]
    best_combo: tuple[dict[str, Any], ...] | None = None
    best_key: tuple[int, int, float, float, int] | None = None
    max_combo_size = min(4, len(ranked))
    for combo_size in range(2, max_combo_size + 1):
        for combo in combinations(ranked, combo_size):
            source_families = {item["source_family"] for item in combo if item["source_family"]}
            origin_ids = {item["origin_id"] for item in combo if item["origin_id"]}
            if len(source_families) < 2 or len(origin_ids) < 2:
                continue
            combined_axes: set[str] = set()
            for item in combo:
                combined_axes.update(item["support_axes"])
            if not CONSENSUS_REQUIRED_AXES.issubset(combined_axes):
                continue
            avg_score = sum(item["retrieval_score"] for item in combo) / len(combo)
            avg_overlap = sum(item["overlap"] for item in combo) / len(combo)
            key = (
                len(source_families),
                len(origin_ids),
                avg_score,
                avg_overlap,
                -combo_size,
            )
            if best_key is None or key > best_key:
                best_key = key
                best_combo = combo
    if best_combo is None:
        return None
    return list(best_combo)


class EvidenceGuard:
    """Qualify retrieved evidence against a query or claim."""

    def __init__(self, policy: str = "audit_safe") -> None:
        if policy != "audit_safe":
            raise ValueError("Only policy='audit_safe' is supported in this prototype")
        self.policy = policy

    def qualify(
        self,
        query_or_claim: str,
        candidate_evidence: list[dict[str, Any]],
        decision_id: str | None = None,
        domain_context: str | None = None,
        original_packet: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        packet_for_hash = original_packet or {
            "decision_id": decision_id,
            "query_or_claim": query_or_claim,
            "candidate_evidence": candidate_evidence,
            "policy": self.policy,
            "domain_context": domain_context,
        }
        evidence_ids = [
            str(item.get("evidence_id", f"evidence_{idx + 1}"))
            for idx, item in enumerate(candidate_evidence or [])
        ]
        now = datetime.now(UTC).isoformat()
        reason_codes: list[str] = []

        if not str(query_or_claim or "").strip():
            return self._decision(
                decision_id,
                0.0,
                "needs_context",
                "needs_context",
                "request_more_context",
                0.0,
                ["missing_query_or_claim", "request_more_context"],
                packet_for_hash,
                evidence_ids,
                now,
            )

        if not candidate_evidence:
            return self._decision(
                decision_id,
                0.0,
                "needs_context",
                "needs_context",
                "request_more_context",
                0.0,
                ["missing_candidate_evidence", "request_more_context"],
                packet_for_hash,
                evidence_ids,
                now,
            )

        metrics = []
        for idx, evidence in enumerate(candidate_evidence):
            text = str(evidence.get("text", "")).strip()
            source_type = str(evidence.get("source_type", "")).strip() or "other"
            retrieval_score = clamp_score(evidence.get("retrieval_score"))
            overlap = lexical_overlap(query_or_claim, text)
            specificity = evidence_specificity(evidence)
            provenance = provenance_assessment(evidence)
            temporal = temporal_assessment(evidence)
            metadata = evidence.get("metadata") or {}
            metrics.append(
                {
                    "idx": idx,
                    "evidence_id": str(evidence.get("evidence_id", f"evidence_{idx + 1}")),
                    "text": text,
                    "source_type": source_type,
                    "retrieval_score": retrieval_score,
                    "overlap": overlap,
                    "specificity": specificity,
                    "contradiction": has_contradiction_signal(query_or_claim, evidence),
                    "insufficient_context": has_insufficient_context_signal(evidence),
                    "weak_evidence_surface": has_weak_evidence_surface_signal(evidence),
                    "provenance_blocking": provenance["blocking"],
                    "provenance_context": provenance["context"],
                    "provenance_reasons": provenance["blocking_reasons"] + provenance["context_reasons"],
                    "temporal_blocking": temporal["blocking"],
                    "temporal_context": temporal["context"],
                    "temporal_reasons": temporal["blocking_reasons"] + temporal["context_reasons"],
                    "support_axes": normalize_metadata_list(metadata.get("support_axes")),
                    "source_family": str(metadata.get("source_family", "")).strip().lower(),
                    "origin_id": str(metadata.get("origin_id", "")).strip().lower(),
                }
            )

        best = max(metrics, key=lambda item: (item["retrieval_score"], item["overlap"], item["specificity"]))
        semantic_similarity = round(max(best["retrieval_score"], best["overlap"]), 4)
        usable_metrics = [
            item
            for item in metrics
            if item["text"] and item["source_type"] in ALLOWED_SOURCE_TYPES
        ]
        direct_candidates = [
            item
            for item in usable_metrics
            if item["retrieval_score"] >= 0.72
            and item["overlap"] >= 0.24
            and item["specificity"] >= 0.60
            and not item["insufficient_context"]
            and not item["weak_evidence_surface"]
            and not item["provenance_blocking"]
            and not item["provenance_context"]
            and not item["temporal_blocking"]
            and not item["temporal_context"]
            and evidence_axes_allow_direct(item)
        ]
        consensus_candidates = [
            item
            for item in usable_metrics
            if item["retrieval_score"] >= CONSENSUS_MIN_RETRIEVAL_SCORE
            and item["overlap"] >= CONSENSUS_MIN_LEXICAL_OVERLAP
            and item["specificity"] >= CONSENSUS_MIN_SPECIFICITY
            and item["support_axes"]
            and item["source_family"]
            and item["origin_id"]
            and not item["contradiction"]
            and not item["insufficient_context"]
            and not item["weak_evidence_surface"]
            and not item["provenance_blocking"]
            and not item["provenance_context"]
            and not item["temporal_blocking"]
            and not item["temporal_context"]
        ]
        consensus_selection = select_multi_source_consensus(consensus_candidates)
        false_neighbor_candidates = [
            item
            for item in usable_metrics
            if item["retrieval_score"] >= 0.80 and item["overlap"] < 0.12
        ]
        related_candidates = [
            item
            for item in usable_metrics
            if item["retrieval_score"] >= 0.60 and item["overlap"] >= 0.12
        ]
        best_direct = max(
            direct_candidates,
            key=lambda item: (item["overlap"], item["retrieval_score"], item["specificity"]),
            default=None,
        )
        best_false_neighbor = max(
            false_neighbor_candidates,
            key=lambda item: (item["retrieval_score"], item["specificity"]),
            default=None,
        )
        best_related = max(
            related_candidates,
            key=lambda item: (item["overlap"], item["retrieval_score"], item["specificity"]),
            default=None,
        )

        missing_text_count = sum(1 for item in metrics if not item["text"])
        invalid_source_count = sum(1 for item in metrics if item["source_type"] not in ALLOWED_SOURCE_TYPES)
        weak_surface_count = sum(1 for item in metrics if item["weak_evidence_surface"])
        partial_axis_candidate_count = sum(
            1 for item in usable_metrics if item["support_axes"] and not covers_consensus_required_axes(item)
        )
        provenance_blocking_candidates = [item for item in metrics if item["provenance_blocking"]]
        provenance_context_candidates = [item for item in metrics if item["provenance_context"]]
        temporal_blocking_candidates = [item for item in metrics if item["temporal_blocking"]]
        temporal_context_candidates = [item for item in metrics if item["temporal_context"]]
        active_contradiction_candidates = [
            item
            for item in metrics
            if item["contradiction"]
            and not item["provenance_blocking"]
            and not item["provenance_context"]
            and not item["temporal_blocking"]
            and not item["temporal_context"]
        ]
        if missing_text_count:
            reason_codes.append("missing_evidence_text")
        if invalid_source_count:
            reason_codes.append("invalid_source_type")
        if weak_surface_count:
            reason_codes.append("weak_evidence_surface")

        if active_contradiction_candidates:
            reason_codes.extend(["contradictory_evidence_signal", "manual_review_required"])
            return self._decision(
                decision_id,
                semantic_similarity,
                "contradictory",
                "confirmed_not_same",
                "manual_review",
                0.76,
                reason_codes,
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=[item["evidence_id"] for item in active_contradiction_candidates],
            )

        insufficient_context_count = sum(1 for item in metrics if item["insufficient_context"])
        if best_direct:
            selected_ids = [best_direct["evidence_id"]]
            rejected_ids = [item["evidence_id"] for item in metrics if item["evidence_id"] not in selected_ids]
            reason_codes.extend(["direct_evidence_sufficient", "source_specificity_present"])
            if false_neighbor_candidates:
                reason_codes.append("non_supporting_false_neighbor_ignored")
            if insufficient_context_count:
                reason_codes.append("insufficient_candidate_ignored")
            if weak_surface_count:
                reason_codes.append("weak_surface_candidate_ignored")
            if provenance_blocking_candidates or provenance_context_candidates:
                reason_codes.append("provenance_candidate_ignored")
            if temporal_blocking_candidates or temporal_context_candidates:
                reason_codes.append("temporal_candidate_ignored")
            if missing_text_count:
                reason_codes.append("malformed_candidate_ignored")
            if invalid_source_count:
                reason_codes.append("invalid_source_candidate_ignored")
            return self._decision(
                decision_id,
                round(max(best_direct["retrieval_score"], best_direct["overlap"]), 4),
                "confirmed_evidence",
                "confirmed_same",
                "allow_answer",
                0.91,
                reason_codes,
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=selected_ids,
                rejected_evidence_ids=rejected_ids,
            )

        if consensus_selection:
            selected_ids = [item["evidence_id"] for item in consensus_selection]
            rejected_ids = [item["evidence_id"] for item in metrics if item["evidence_id"] not in selected_ids]
            reason_codes.extend(
                [
                    "multi_source_consensus_sufficient",
                    "independent_sources_present",
                    "combined_support_axes_present",
                ]
            )
            if false_neighbor_candidates:
                reason_codes.append("non_supporting_false_neighbor_ignored")
            if partial_axis_candidate_count:
                reason_codes.append("partial_axis_candidates_combined")
            if weak_surface_count:
                reason_codes.append("weak_surface_candidate_ignored")
            if provenance_blocking_candidates or provenance_context_candidates:
                reason_codes.append("provenance_candidate_ignored")
            if temporal_blocking_candidates or temporal_context_candidates:
                reason_codes.append("temporal_candidate_ignored")
            if missing_text_count:
                reason_codes.append("malformed_candidate_ignored")
            if invalid_source_count:
                reason_codes.append("invalid_source_candidate_ignored")
            return self._decision(
                decision_id,
                round(max(max(item["retrieval_score"], item["overlap"]) for item in consensus_selection), 4),
                "confirmed_evidence",
                "confirmed_same",
                "allow_answer",
                0.84,
                reason_codes,
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=selected_ids,
                rejected_evidence_ids=rejected_ids,
            )

        if provenance_blocking_candidates:
            reason_codes.extend(["provenance_blocking_state", "manual_review_required"])
            for item in provenance_blocking_candidates:
                reason_codes.extend(item["provenance_reasons"])
        if provenance_context_candidates:
            reason_codes.extend(["provenance_context_required", "request_more_context"])
            for item in provenance_context_candidates:
                reason_codes.extend(item["provenance_reasons"])
        if temporal_blocking_candidates:
            reason_codes.extend(["temporal_blocking_state", "manual_review_required"])
            for item in temporal_blocking_candidates:
                reason_codes.extend(item["temporal_reasons"])
        if temporal_context_candidates:
            reason_codes.extend(["temporal_context_required", "request_more_context"])
            for item in temporal_context_candidates:
                reason_codes.extend(item["temporal_reasons"])

        if provenance_blocking_candidates:
            return self._decision(
                decision_id,
                semantic_similarity,
                "needs_review",
                "needs_review",
                "manual_review",
                0.57,
                reason_codes,
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=[item["evidence_id"] for item in provenance_blocking_candidates],
            )

        if temporal_blocking_candidates:
            return self._decision(
                decision_id,
                semantic_similarity,
                "needs_review",
                "needs_review",
                "manual_review",
                0.57,
                reason_codes,
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=[item["evidence_id"] for item in temporal_blocking_candidates],
            )

        if best_false_neighbor:
            reason_codes.extend(["high_similarity_not_sufficient", "low_claim_evidence_overlap"])
            return self._decision(
                decision_id,
                round(max(best_false_neighbor["retrieval_score"], best_false_neighbor["overlap"]), 4),
                "quarantine_false_neighbor",
                "quarantine_false_neighbor",
                "quarantine_do_not_use",
                0.86,
                reason_codes,
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=[best_false_neighbor["evidence_id"]],
            )

        if provenance_context_candidates:
            if best_related:
                return self._decision(
                    decision_id,
                    round(max(best_related["retrieval_score"], best_related["overlap"]), 4),
                    "related_not_enough",
                    "needs_context",
                    "request_more_context",
                    0.64,
                    reason_codes,
                    packet_for_hash,
                    evidence_ids,
                    now,
                    selected_evidence_ids=[best_related["evidence_id"]],
                )
            return self._decision(
                decision_id,
                semantic_similarity,
                "needs_review",
                "needs_review",
                "manual_review",
                0.55,
                reason_codes + ["manual_review_required"],
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=[item["evidence_id"] for item in provenance_context_candidates],
            )

        if temporal_context_candidates:
            if best_related:
                return self._decision(
                    decision_id,
                    round(max(best_related["retrieval_score"], best_related["overlap"]), 4),
                    "related_not_enough",
                    "needs_context",
                    "request_more_context",
                    0.64,
                    reason_codes,
                    packet_for_hash,
                    evidence_ids,
                    now,
                    selected_evidence_ids=[best_related["evidence_id"]],
                )
            return self._decision(
                decision_id,
                semantic_similarity,
                "needs_review",
                "needs_review",
                "manual_review",
                0.55,
                reason_codes + ["manual_review_required"],
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=[item["evidence_id"] for item in temporal_context_candidates],
            )

        if insufficient_context_count:
            reason_codes.extend(["evidence_self_reports_insufficient_context", "request_more_context"])
            if best_related:
                return self._decision(
                    decision_id,
                    round(max(best_related["retrieval_score"], best_related["overlap"]), 4),
                    "related_not_enough",
                    "needs_context",
                    "request_more_context",
                    0.66,
                    reason_codes,
                    packet_for_hash,
                    evidence_ids,
                    now,
                    selected_evidence_ids=[best_related["evidence_id"]],
                )
            return self._decision(
                decision_id,
                semantic_similarity,
                "needs_review",
                "needs_review",
                "manual_review",
                0.58,
                reason_codes + ["manual_review_required"],
                packet_for_hash,
                evidence_ids,
                now,
            )

        if missing_text_count:
            return self._decision(
                decision_id,
                semantic_similarity,
                "needs_review",
                "needs_review",
                "manual_review",
                0.52,
                reason_codes + ["manual_review_required", "malformed_or_incomplete_evidence"],
                packet_for_hash,
                evidence_ids,
                now,
            )

        if best_related:
            reason_codes.extend(["related_context_not_enough", "request_more_context"])
            if best_related["specificity"] < 0.60:
                reason_codes.append("missing_source_specificity")
            if best_related["weak_evidence_surface"]:
                reason_codes.append("evidence_surface_is_index_or_reference")
            if consensus_candidates:
                reason_codes.append("multi_source_consensus_not_sufficient")
                combined_axes = set()
                for item in consensus_candidates:
                    combined_axes.update(item["support_axes"])
                if not CONSENSUS_REQUIRED_AXES.issubset(combined_axes):
                    reason_codes.append("combined_support_axes_missing")
                if len({item["source_family"] for item in consensus_candidates}) < 2:
                    reason_codes.append("independent_source_family_missing")
                if len({item["origin_id"] for item in consensus_candidates}) < 2:
                    reason_codes.append("independent_origin_missing")
            return self._decision(
                decision_id,
                round(max(best_related["retrieval_score"], best_related["overlap"]), 4),
                "related_not_enough",
                "needs_context",
                "request_more_context",
                0.68,
                reason_codes,
                packet_for_hash,
                evidence_ids,
                now,
                selected_evidence_ids=[best_related["evidence_id"]],
            )

        reason_codes.extend(["insufficient_evidence_signal", "manual_review_required"])
        if missing_text_count or invalid_source_count:
            reason_codes.append("malformed_or_incomplete_evidence")
        return self._decision(
            decision_id,
            semantic_similarity,
            "needs_review",
            "needs_review",
            "manual_review",
            0.55,
            reason_codes,
            packet_for_hash,
            evidence_ids,
            now,
        )

    def qualify_packet(self, packet: dict[str, Any]) -> dict[str, Any]:
        policy = str(packet.get("policy") or self.policy)
        if policy != self.policy:
            guard = EvidenceGuard(policy=policy)
            return guard.qualify_packet(packet)
        return self.qualify(
            query_or_claim=str(packet.get("query_or_claim", "")),
            candidate_evidence=list(packet.get("candidate_evidence") or []),
            decision_id=packet.get("decision_id"),
            domain_context=packet.get("domain_context"),
            original_packet=packet,
        )

    def _decision(
        self,
        decision_id: str | None,
        semantic_similarity: float,
        evidence_verdict: str,
        identity_verdict: str,
        recommended_action: str,
        confidence: float,
        reason_codes: list[str],
        packet_for_hash: dict[str, Any],
        evidence_ids: list[str],
        generated_at_utc: str,
        selected_evidence_ids: list[str] | None = None,
        rejected_evidence_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        audit = {
            "input_hash": input_hash(packet_for_hash),
            "evidence_ids": evidence_ids,
            "generated_at_utc": generated_at_utc,
            "policy": self.policy,
        }
        if selected_evidence_ids is not None:
            audit["selected_evidence_ids"] = selected_evidence_ids
        if rejected_evidence_ids is not None:
            audit["rejected_evidence_ids"] = rejected_evidence_ids
        return {
            "decision_id": str(decision_id or input_hash(packet_for_hash)[:12]),
            "rule_version": RULE_VERSION,
            "semantic_similarity": round(semantic_similarity, 4),
            "evidence_verdict": evidence_verdict,
            "identity_verdict": identity_verdict,
            "recommended_action": recommended_action,
            "confidence": round(confidence, 4),
            "reason_codes": list(dict.fromkeys(reason_codes)),
            "audit": audit,
        }
