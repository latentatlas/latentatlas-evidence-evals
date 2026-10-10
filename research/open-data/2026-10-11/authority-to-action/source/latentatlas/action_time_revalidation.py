"""Action-time revalidation guard for agentic LatentAtlas workflows.

This layer treats an evidence decision as a time-bounded authority lease. It
does not execute tools, mutate production truth, or convert evidence support
into permission. It only decides whether a planned action may proceed in dry-run
or must be blocked/revalidated at execution time.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


ACTION_TIME_REVALIDATION_VERSION = "latentatlas_action_time_revalidation_v0"
ACTION_TIME_EXPOSURE_VERSION = "latentatlas_action_time_exposure_v0"

ACTION_TIME_VERDICTS = {
    "action_authorized",
    "revalidation_required",
    "blocked_authority_expired",
    "blocked_action_out_of_scope",
    "blocked_impact_out_of_scope",
    "blocked_actor_mismatch",
    "blocked_scope_mismatch",
    "blocked_evidence_changed",
    "blocked_permission_changed",
    "blocked_identity_changed",
    "blocked_policy_changed",
    "blocked_non_dry_run",
    "needs_review",
}

ACTION_TIME_RECOMMENDED_ACTIONS = {
    "execute_dry_run",
    "request_revalidation",
    "block_action",
    "manual_review",
}

ACTION_IMPACT_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
ACTION_IMPACT_RISK_SCORE = {"low": 5, "medium": 15, "high": 30, "critical": 45}
ACTION_IMPACT_EXPOSURE_SCORE = {"low": 1, "medium": 2, "high": 4, "critical": 5}

LIKELIHOOD_PRIOR_EXPOSURE_SCORE = {
    "low": 1,
    "possible": 2,
    "likely": 3,
    "active_issue": 5,
}

REVERSIBILITY_COST_BY_ACTION = {
    "send_followup": 2,
    "update_ticket": 2,
    "publish_customer_reply": 4,
    "suppress_record": 4,
    "approve_request": 4,
    "refund_payment": 4,
    "tool_call_execution": 4,
    "production_state_change": 5,
}

DETECTION_DIFFICULTY_BY_RISK_POINT = {
    "scheduled_execution_window": 3,
    "near_expiry_window": 2,
    "aging_revalidation_window": 4,
    "lease_expired": 2,
    "scheduled_after_lease_expiry": 3,
    "missing_pre_execution_revalidation": 3,
    "stale_pre_execution_revalidation": 4,
    "evidence_drift": 3,
    "permission_drift": 2,
    "identity_drift": 3,
    "policy_drift": 4,
    "action_scope_drift": 1,
    "impact_escalation": 2,
    "actor_drift": 1,
    "target_scope_drift": 2,
    "live_execution_boundary": 1,
    "incomplete_action_authority_packet": 3,
    "invalid_action_timing": 3,
    "new_decision_required": 4,
    "lease_renewal_required": 3,
    "high_impact_action_surface": 2,
}

EXPOSURE_FACTOR_MAX = 5
MAX_EXPOSURE_PRODUCT = EXPOSURE_FACTOR_MAX**4

DEFAULT_ACTION_IMPACT = {
    "send_followup": "medium",
    "update_ticket": "medium",
    "publish_customer_reply": "high",
    "suppress_record": "high",
    "approve_request": "high",
    "refund_payment": "high",
    "tool_call_execution": "high",
    "production_state_change": "critical",
}

REVALIDATION_HASH_FIELDS = (
    "evidence_hash",
    "permission_hash",
    "identity_hash",
    "policy_hash",
)

CURRENT_STATES = {
    "evidence_state": {"current", "confirmed", "unchanged"},
    "permission_state": {"granted", "approved", "unchanged"},
    "identity_state": {"confirmed", "unchanged"},
    "policy_state": {"active", "current", "unchanged"},
}

BLOCKED_STATE_REASON = {
    "evidence_state": "action_time_evidence_changed",
    "permission_state": "action_time_permission_changed",
    "identity_state": "action_time_identity_changed",
    "policy_state": "action_time_policy_changed",
}

BLOCKED_HASH_REASON = {
    "evidence_hash": "action_time_evidence_changed",
    "permission_hash": "action_time_permission_changed",
    "identity_hash": "action_time_identity_changed",
    "policy_hash": "action_time_policy_changed",
}

VERDICT_PRIORITY = (
    ("action_time_missing_required_field", "needs_review"),
    ("action_time_invalid_timestamp", "needs_review"),
    ("action_time_authority_lease_expired", "blocked_authority_expired"),
    ("action_time_scheduled_after_lease_expiry", "blocked_authority_expired"),
    ("action_time_requested_action_out_of_scope", "blocked_action_out_of_scope"),
    ("action_time_impact_out_of_scope", "blocked_impact_out_of_scope"),
    ("action_time_actor_mismatch", "blocked_actor_mismatch"),
    ("action_time_scope_mismatch", "blocked_scope_mismatch"),
    ("action_time_non_dry_run_blocked", "blocked_non_dry_run"),
    ("action_time_revalidation_missing", "revalidation_required"),
    ("action_time_revalidation_stale", "revalidation_required"),
    ("action_time_evidence_changed", "blocked_evidence_changed"),
    ("action_time_permission_changed", "blocked_permission_changed"),
    ("action_time_identity_changed", "blocked_identity_changed"),
    ("action_time_policy_changed", "blocked_policy_changed"),
)

ACTION_BY_VERDICT = {
    "action_authorized": "execute_dry_run",
    "revalidation_required": "request_revalidation",
    "blocked_authority_expired": "request_revalidation",
    "blocked_evidence_changed": "request_revalidation",
    "blocked_policy_changed": "request_revalidation",
    "blocked_action_out_of_scope": "block_action",
    "blocked_impact_out_of_scope": "block_action",
    "blocked_actor_mismatch": "block_action",
    "blocked_scope_mismatch": "block_action",
    "blocked_permission_changed": "block_action",
    "blocked_identity_changed": "block_action",
    "blocked_non_dry_run": "block_action",
    "needs_review": "manual_review",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def parse_timestamp(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def format_timestamp(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def required_string(mapping: dict[str, Any], field: str) -> bool:
    return isinstance(mapping.get(field), str) and bool(mapping[field].strip())


def scope_matches(lease_scope: dict[str, Any], action_scope: dict[str, Any]) -> bool:
    for key, value in lease_scope.items():
        if key not in action_scope or action_scope[key] != value:
            return False
    return True


def add_reason(reason_codes: list[str], reason: str) -> None:
    if reason not in reason_codes:
        reason_codes.append(reason)


def choose_verdict(reason_codes: list[str]) -> str:
    if not reason_codes:
        return "action_authorized"
    for reason_prefix, verdict in VERDICT_PRIORITY:
        if any(reason == reason_prefix or reason.startswith(reason_prefix + "_") for reason in reason_codes):
            return verdict
    return "needs_review"


def normalize_hash(value: Any) -> str:
    return str(value).strip()


def normalize_impact(value: Any) -> str | None:
    if value is None or value == "":
        return None
    text = str(value).strip().lower()
    if text in ACTION_IMPACT_LEVELS:
        return text
    return None


def infer_action_impact(action_request: dict[str, Any], reason_codes: list[str]) -> str:
    requested_action = str(action_request.get("requested_action", "")).strip()
    explicit_impact = action_request.get("impact")
    normalized = normalize_impact(explicit_impact)
    if explicit_impact is not None and explicit_impact != "" and normalized is None:
        add_reason(reason_codes, "action_time_missing_required_field_action_request_impact")
    return normalized or DEFAULT_ACTION_IMPACT.get(requested_action, "medium")


def lease_max_impact(lease: dict[str, Any], reason_codes: list[str]) -> str:
    normalized = normalize_impact(lease.get("max_action_impact", "medium"))
    if normalized is None:
        add_reason(reason_codes, "action_time_missing_required_field_authority_lease_max_action_impact")
        return "medium"
    return normalized


def impact_exceeds(requested_impact: str, max_impact: str) -> bool:
    return ACTION_IMPACT_LEVELS[requested_impact] > ACTION_IMPACT_LEVELS[max_impact]


def parse_max_age_seconds(value: Any, reason_codes: list[str]) -> int:
    if value is None or value == "":
        return 300
    try:
        max_age_seconds = int(value)
    except (TypeError, ValueError):
        add_reason(reason_codes, "action_time_missing_required_field_authority_lease_revalidation_max_age_seconds")
        return 300
    if max_age_seconds <= 0:
        add_reason(reason_codes, "action_time_missing_required_field_authority_lease_revalidation_max_age_seconds")
        return 300
    return max_age_seconds


def choose_followup_lane(reason_codes: list[str], verdict: str) -> str:
    if verdict == "action_authorized":
        return "none"
    if any(
        reason in {
            "action_time_evidence_changed",
            "action_time_permission_changed",
            "action_time_identity_changed",
            "action_time_policy_changed",
        }
        for reason in reason_codes
    ):
        return "new_decision_required"
    if any(
        reason
        in {
            "action_time_authority_lease_expired",
            "action_time_scheduled_after_lease_expiry",
            "action_time_revalidation_missing",
            "action_time_revalidation_stale",
        }
        for reason in reason_codes
    ):
        return "lease_renewal_required"
    if any(reason.startswith("action_time_missing_required_field") for reason in reason_codes) or any(
        reason.startswith("action_time_invalid_timestamp") for reason in reason_codes
    ):
        return "manual_review_required"
    return "blocked_request_not_renewable"


def seconds_between(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None:
        return None
    return (end - start).total_seconds()


def add_risk_point(risk_points: list[dict[str, str]], code: str, status: str, note: str) -> None:
    if any(item["code"] == code for item in risk_points):
        return
    risk_points.append({"code": code, "status": status, "note": note})


def likelihood_band(risk_score: int, has_active_issue: bool) -> str:
    if has_active_issue:
        return "active_issue"
    if risk_score >= 55:
        return "likely"
    if risk_score >= 30:
        return "possible"
    return "low"


def build_risk_assessment(
    *,
    reason_codes: list[str],
    verdict: str,
    requested_impact: str,
    max_action_impact: str,
    scheduled_for: datetime | None,
    expires_at: datetime | None,
    performed_at: datetime | None,
    effective_action_at: datetime | None,
    max_age_seconds: int,
    followup_lane: str,
) -> dict[str, Any]:
    risk_points: list[dict[str, str]] = []
    risk_score = ACTION_IMPACT_RISK_SCORE[requested_impact]

    if scheduled_for is not None:
        risk_score += 15
        add_risk_point(
            risk_points,
            "scheduled_execution_window",
            "potential",
            "Queued or scheduled actions can drift between approval and execution.",
        )

    if ACTION_IMPACT_LEVELS[requested_impact] >= ACTION_IMPACT_LEVELS["high"]:
        risk_score += 20
        add_risk_point(
            risk_points,
            "high_impact_action_surface",
            "potential",
            "Customer-visible or state-changing actions need stricter authority checks.",
        )

    seconds_until_expiry = seconds_between(effective_action_at, expires_at)
    if seconds_until_expiry is not None and seconds_until_expiry >= 0 and seconds_until_expiry <= max_age_seconds:
        risk_score += 15
        add_risk_point(
            risk_points,
            "near_expiry_window",
            "potential",
            "The effective action time is close to lease expiry.",
        )

    revalidation_age = seconds_between(performed_at, effective_action_at)
    if revalidation_age is not None and revalidation_age >= max_age_seconds * 0.75:
        risk_score += 15
        add_risk_point(
            risk_points,
            "aging_revalidation_window",
            "potential",
            "The revalidation record is close to or beyond the allowed freshness window.",
        )

    active_reason_risk_points = {
        "action_time_authority_lease_expired": ("lease_expired", "The authority lease expired before action."),
        "action_time_scheduled_after_lease_expiry": (
            "scheduled_after_lease_expiry",
            "The scheduled action would run after lease expiry.",
        ),
        "action_time_revalidation_missing": (
            "missing_pre_execution_revalidation",
            "The action lacks a required execution-time revalidation record.",
        ),
        "action_time_revalidation_stale": (
            "stale_pre_execution_revalidation",
            "The execution-time revalidation record is stale.",
        ),
        "action_time_evidence_changed": (
            "evidence_drift",
            "The evidence state changed after the authority lease was issued.",
        ),
        "action_time_permission_changed": (
            "permission_drift",
            "Permission no longer supports the requested action.",
        ),
        "action_time_identity_changed": (
            "identity_drift",
            "Identity no longer matches the authority lease.",
        ),
        "action_time_policy_changed": (
            "policy_drift",
            "The controlling policy changed after lease issue.",
        ),
        "action_time_requested_action_out_of_scope": (
            "action_scope_drift",
            "The requested action does not match the authority lease.",
        ),
        "action_time_impact_out_of_scope": (
            "impact_escalation",
            "The requested action impact exceeds the lease limit.",
        ),
        "action_time_actor_mismatch": (
            "actor_drift",
            "The execution actor does not match the authority lease.",
        ),
        "action_time_scope_mismatch": (
            "target_scope_drift",
            "The requested target or tenant is outside the lease scope.",
        ),
        "action_time_non_dry_run_blocked": (
            "live_execution_boundary",
            "The packet attempts live execution instead of dry-run authorization.",
        ),
    }
    for reason in reason_codes:
        risk = active_reason_risk_points.get(reason)
        if risk:
            risk_score += 30
            add_risk_point(risk_points, risk[0], "active", risk[1])
        elif reason.startswith("action_time_missing_required_field"):
            risk_score += 20
            add_risk_point(
                risk_points,
                "incomplete_action_authority_packet",
                "active",
                "Required action-time authority data is missing.",
            )
        elif reason.startswith("action_time_invalid_timestamp"):
            risk_score += 20
            add_risk_point(
                risk_points,
                "invalid_action_timing",
                "active",
                "A required action-time timestamp is invalid.",
            )

    if followup_lane == "new_decision_required":
        risk_score += 20
        add_risk_point(
            risk_points,
            "new_decision_required",
            "active",
            "State changed enough that lease renewal is not sufficient.",
        )
    elif followup_lane == "lease_renewal_required":
        risk_score += 10
        add_risk_point(
            risk_points,
            "lease_renewal_required",
            "active",
            "The lease or revalidation should be refreshed before action.",
        )

    has_active_issue = verdict != "action_authorized"
    risk_score = min(100, risk_score)
    return {
        "model": "latentatlas_action_time_heuristic_risk_v0",
        "calibration": "heuristic_not_statistical_probability",
        "likelihood_band": likelihood_band(risk_score, has_active_issue),
        "risk_score": risk_score,
        "risk_points": risk_points,
    }


def exposure_band(score: float) -> str:
    if score >= 60:
        return "critical"
    if score >= 30:
        return "severe"
    if score >= 15:
        return "material"
    if score >= 5:
        return "elevated"
    return "minimal"


def build_risk_exposure(
    *,
    risk_assessment: dict[str, Any],
    requested_action: str,
    requested_impact: str,
    verdict: str,
    recommended_action: str,
    followup_lane: str,
) -> dict[str, Any]:
    likelihood_band_value = str(risk_assessment.get("likelihood_band", "low"))
    likelihood_score = LIKELIHOOD_PRIOR_EXPOSURE_SCORE.get(likelihood_band_value, 1)
    impact_score = ACTION_IMPACT_EXPOSURE_SCORE.get(requested_impact, 2)

    detection_score = 1
    detection_basis = "no_material_pre_execution_drift_signal"
    for point in risk_assessment.get("risk_points", []):
        code = str(point.get("code", ""))
        point_score = DETECTION_DIFFICULTY_BY_RISK_POINT.get(code)
        if point_score is not None and (
            point_score > detection_score or detection_basis == "no_material_pre_execution_drift_signal"
        ):
            detection_score = point_score
            detection_basis = code

    action_reversibility_score = REVERSIBILITY_COST_BY_ACTION.get(requested_action, 2)
    reversibility_score = max(action_reversibility_score, impact_score)
    raw_product = likelihood_score * impact_score * detection_score * reversibility_score
    score = round((raw_product / MAX_EXPOSURE_PRODUCT) * 100, 2)

    return {
        "model": ACTION_TIME_EXPOSURE_VERSION,
        "calibration": "heuristic_relative_prior_not_empirical_probability",
        "formula": "event_likelihood_prior * action_impact * detection_difficulty * reversibility_cost",
        "score": score,
        "band": exposure_band(score),
        "factor_scale": {
            "min": 1,
            "max": EXPOSURE_FACTOR_MAX,
            "score_max": 100,
            "meaning": "relative benchmark exposure, not empirical probability",
        },
        "factors": {
            "event_likelihood_prior": {
                "score": likelihood_score,
                "label": likelihood_band_value,
                "basis": "risk_assessment.likelihood_band",
            },
            "action_impact": {
                "score": impact_score,
                "label": requested_impact,
                "basis": "action_request.impact_or_default_action_impact",
            },
            "detection_difficulty": {
                "score": detection_score,
                "label": detection_basis,
                "basis": "highest_detection_difficulty_risk_point",
            },
            "reversibility_cost": {
                "score": reversibility_score,
                "label": requested_action,
                "basis": "action_type_and_impact_reversibility",
            },
        },
        "authorization_effect": "none_hard_gates_control_execution",
        "recommended_action": recommended_action,
        "followup_lane": followup_lane,
        "verdict": verdict,
    }


def revalidate_action_packet(packet: dict[str, Any]) -> dict[str, Any]:
    lease = packet.get("authority_lease")
    action_request = packet.get("action_request")
    revalidation = packet.get("revalidation")
    reason_codes: list[str] = []

    if not isinstance(lease, dict):
        lease = {}
        add_reason(reason_codes, "action_time_missing_required_field_authority_lease")
    if not isinstance(action_request, dict):
        action_request = {}
        add_reason(reason_codes, "action_time_missing_required_field_action_request")
    if revalidation is not None and not isinstance(revalidation, dict):
        revalidation = {}
        add_reason(reason_codes, "action_time_missing_required_field_revalidation")

    for field in ("lease_id", "decision_id", "issued_at", "expires_at", "actor", "allowed_action"):
        if not required_string(lease, field):
            add_reason(reason_codes, f"action_time_missing_required_field_authority_lease_{field}")
    for field in ("action_id", "requested_at", "actor", "requested_action"):
        if not required_string(action_request, field):
            add_reason(reason_codes, f"action_time_missing_required_field_action_request_{field}")

    issued_at = parse_timestamp(lease.get("issued_at"))
    expires_at = parse_timestamp(lease.get("expires_at"))
    requested_at = parse_timestamp(action_request.get("requested_at"))
    scheduled_for = parse_timestamp(action_request.get("scheduled_for"))
    if lease.get("issued_at") and issued_at is None:
        add_reason(reason_codes, "action_time_invalid_timestamp_issued_at")
    if lease.get("expires_at") and expires_at is None:
        add_reason(reason_codes, "action_time_invalid_timestamp_expires_at")
    if action_request.get("requested_at") and requested_at is None:
        add_reason(reason_codes, "action_time_invalid_timestamp_requested_at")
    if action_request.get("scheduled_for") and scheduled_for is None:
        add_reason(reason_codes, "action_time_invalid_timestamp_scheduled_for")
    if requested_at and scheduled_for and scheduled_for < requested_at:
        add_reason(reason_codes, "action_time_invalid_timestamp_scheduled_before_requested")

    if issued_at and expires_at and expires_at <= issued_at:
        add_reason(reason_codes, "action_time_invalid_timestamp_expires_before_issued")
    effective_action_at = scheduled_for or requested_at
    if expires_at and requested_at and requested_at > expires_at:
        add_reason(reason_codes, "action_time_authority_lease_expired")
    if expires_at and scheduled_for and scheduled_for > expires_at:
        add_reason(reason_codes, "action_time_scheduled_after_lease_expiry")
    elif expires_at and effective_action_at and effective_action_at > expires_at:
        add_reason(reason_codes, "action_time_authority_lease_expired")

    if lease.get("allowed_action") and action_request.get("requested_action"):
        if lease["allowed_action"] != action_request["requested_action"]:
            add_reason(reason_codes, "action_time_requested_action_out_of_scope")
    requested_impact = infer_action_impact(action_request, reason_codes)
    max_action_impact = lease_max_impact(lease, reason_codes)
    if impact_exceeds(requested_impact, max_action_impact):
        add_reason(reason_codes, "action_time_impact_out_of_scope")
    if lease.get("actor") and action_request.get("actor") and lease["actor"] != action_request["actor"]:
        add_reason(reason_codes, "action_time_actor_mismatch")

    lease_scope = lease.get("scope") or {}
    action_scope = action_request.get("scope") or {}
    if not isinstance(lease_scope, dict) or not isinstance(action_scope, dict):
        add_reason(reason_codes, "action_time_scope_mismatch")
    elif lease_scope and not scope_matches(lease_scope, action_scope):
        add_reason(reason_codes, "action_time_scope_mismatch")

    if action_request.get("dry_run") is not True:
        add_reason(reason_codes, "action_time_non_dry_run_blocked")

    revalidation_required = lease.get("revalidation_required", True) is not False
    if revalidation_required and not revalidation:
        max_age_seconds = parse_max_age_seconds(lease.get("revalidation_max_age_seconds", 300), reason_codes)
        performed_at = None
        add_reason(reason_codes, "action_time_revalidation_missing")
    elif revalidation:
        performed_at = parse_timestamp(revalidation.get("performed_at"))
        if revalidation.get("performed_at") and performed_at is None:
            add_reason(reason_codes, "action_time_invalid_timestamp_revalidation_performed_at")
        if revalidation_required and performed_at is None:
            add_reason(reason_codes, "action_time_revalidation_missing")
        max_age_seconds = parse_max_age_seconds(lease.get("revalidation_max_age_seconds", 300), reason_codes)
        if performed_at and effective_action_at and effective_action_at - performed_at > timedelta(
            seconds=max_age_seconds
        ):
            add_reason(reason_codes, "action_time_revalidation_stale")

        for field in REVALIDATION_HASH_FIELDS:
            lease_hash = normalize_hash(lease.get(field))
            current_hash = normalize_hash(revalidation.get(field))
            if lease_hash and current_hash and lease_hash != current_hash:
                add_reason(reason_codes, BLOCKED_HASH_REASON[field])
            elif lease_hash and revalidation_required and not current_hash:
                add_reason(reason_codes, f"action_time_missing_required_field_revalidation_{field}")

        for field, allowed_values in CURRENT_STATES.items():
            state = str(revalidation.get(field, "")).strip().lower()
            if state and state not in allowed_values:
                add_reason(reason_codes, BLOCKED_STATE_REASON[field])
            elif revalidation_required and not state:
                add_reason(reason_codes, f"action_time_missing_required_field_revalidation_{field}")
    else:
        max_age_seconds = parse_max_age_seconds(lease.get("revalidation_max_age_seconds", 300), reason_codes)
        performed_at = None

    verdict = choose_verdict(reason_codes)
    if verdict == "action_authorized":
        reason_codes = ["action_time_authority_lease_valid", "action_time_revalidation_passed"]
    recommended_action = ACTION_BY_VERDICT[verdict]
    followup_lane = choose_followup_lane(reason_codes, verdict)
    risk_assessment = build_risk_assessment(
        reason_codes=reason_codes,
        verdict=verdict,
        requested_impact=requested_impact,
        max_action_impact=max_action_impact,
        scheduled_for=scheduled_for,
        expires_at=expires_at,
        performed_at=performed_at,
        effective_action_at=effective_action_at,
        max_age_seconds=max_age_seconds,
        followup_lane=followup_lane,
    )
    requested_action = str(action_request.get("requested_action", "")).strip()
    risk_exposure = build_risk_exposure(
        risk_assessment=risk_assessment,
        requested_action=requested_action,
        requested_impact=requested_impact,
        verdict=verdict,
        recommended_action=recommended_action,
        followup_lane=followup_lane,
    )

    evidence_ids = lease.get("evidence_ids") if isinstance(lease.get("evidence_ids"), list) else []
    return {
        "case_id": str(packet.get("case_id", "")),
        "decision_id": str(lease.get("decision_id", "")),
        "lease_id": str(lease.get("lease_id", "")),
        "action_id": str(action_request.get("action_id", "")),
        "rule_version": ACTION_TIME_REVALIDATION_VERSION,
        "execution_verdict": verdict,
        "recommended_action": recommended_action,
        "followup_lane": followup_lane,
        "action_impact": requested_impact,
        "max_action_impact": max_action_impact,
        "risk_assessment": risk_assessment,
        "risk_exposure": risk_exposure,
        "reason_codes": reason_codes,
        "action_timing": {
            "execution_mode": "scheduled" if scheduled_for else "immediate",
            "issued_at": format_timestamp(issued_at),
            "expires_at": format_timestamp(expires_at),
            "requested_at": format_timestamp(requested_at),
            "scheduled_for": format_timestamp(scheduled_for),
            "effective_action_at": format_timestamp(effective_action_at),
        },
        "audit": {
            "input_hash": stable_hash(packet),
            "evidence_ids": evidence_ids,
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "external_services_used": False,
            "production_truth_mutation": False,
        },
    }


def revalidate_action_packets(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [revalidate_action_packet(packet) for packet in packets]


def summarize_action_revalidations(
    *,
    input_path: Path,
    output_path: Path,
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    verdict_counts = Counter(row["execution_verdict"] for row in decisions)
    action_counts = Counter(row["recommended_action"] for row in decisions)
    followup_counts = Counter(row.get("followup_lane", "unknown") for row in decisions)
    impact_counts = Counter(row.get("action_impact", "unknown") for row in decisions)
    likelihood_counts = Counter(
        row.get("risk_assessment", {}).get("likelihood_band", "unknown") for row in decisions
    )
    exposure_band_counts = Counter(row.get("risk_exposure", {}).get("band", "unknown") for row in decisions)
    risk_point_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    for row in decisions:
        reason_counts.update(row.get("reason_codes", []))
        for point in row.get("risk_assessment", {}).get("risk_points", []):
            code = point.get("code")
            if code:
                risk_point_counts[code] += 1

    unsafe_authorization_count = sum(
        1
        for row in decisions
        if row["recommended_action"] == "execute_dry_run" and row["execution_verdict"] != "action_authorized"
    )
    blocked_or_revalidation_count = sum(
        1
        for row in decisions
        if row["recommended_action"] in {"request_revalidation", "block_action", "manual_review"}
    )
    scheduled_action_count = sum(
        1 for row in decisions if row.get("action_timing", {}).get("execution_mode") == "scheduled"
    )
    new_decision_required_count = sum(
        1 for row in decisions if row.get("followup_lane") == "new_decision_required"
    )
    lease_renewal_required_count = sum(
        1 for row in decisions if row.get("followup_lane") == "lease_renewal_required"
    )
    likely_or_active_issue_count = sum(
        1
        for row in decisions
        if row.get("risk_assessment", {}).get("likelihood_band") in {"likely", "active_issue"}
    )
    max_risk_score = max((row.get("risk_assessment", {}).get("risk_score", 0) for row in decisions), default=0)
    exposure_scores = [
        float(row.get("risk_exposure", {}).get("score", 0))
        for row in decisions
        if isinstance(row.get("risk_exposure", {}).get("score", 0), (int, float))
    ]
    max_exposure_score = max(exposure_scores, default=0)
    mean_exposure_score = round(sum(exposure_scores) / len(exposure_scores), 2) if exposure_scores else 0
    material_or_above_exposure_count = sum(
        1
        for row in decisions
        if row.get("risk_exposure", {}).get("band") in {"material", "severe", "critical"}
    )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "latentatlas_action_time_revalidation",
        "rule_version": ACTION_TIME_REVALIDATION_VERSION,
        "input": str(input_path),
        "output": str(output_path),
        "decision_count": len(decisions),
        "execution_verdict_counts": dict(sorted(verdict_counts.items())),
        "recommended_action_counts": dict(sorted(action_counts.items())),
        "followup_lane_counts": dict(sorted(followup_counts.items())),
        "action_impact_counts": dict(sorted(impact_counts.items())),
        "likelihood_band_counts": dict(sorted(likelihood_counts.items())),
        "risk_exposure_model": ACTION_TIME_EXPOSURE_VERSION,
        "risk_exposure_calibration": "heuristic_relative_prior_not_empirical_probability",
        "risk_exposure_band_counts": dict(sorted(exposure_band_counts.items())),
        "risk_point_counts": dict(sorted(risk_point_counts.items())),
        "reason_code_counts": dict(sorted(reason_counts.items())),
        "unsafe_authorization_count": unsafe_authorization_count,
        "blocked_or_revalidation_count": blocked_or_revalidation_count,
        "scheduled_action_count": scheduled_action_count,
        "new_decision_required_count": new_decision_required_count,
        "lease_renewal_required_count": lease_renewal_required_count,
        "likely_or_active_issue_count": likely_or_active_issue_count,
        "max_risk_score": max_risk_score,
        "max_exposure_score": max_exposure_score,
        "mean_exposure_score": mean_exposure_score,
        "material_or_above_exposure_count": material_or_above_exposure_count,
        "external_services_used": False,
        "production_truth_mutation": False,
    }
