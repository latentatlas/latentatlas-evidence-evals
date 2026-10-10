"""Build 1000 customer-readable Concept Boundary test contents.

The output is synthetic and local. It expands the clear business examples into
machine-scoreable benchmark rows plus a customer-readable content catalog.
"""

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

DEFAULT_OUTPUT = Path("research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl")
DEFAULT_OUT_DIR = Path("outputs/latentatlas/concept_boundary_engine_1000_content")

ARCHETYPE_SPECS: list[dict[str, Any]] = [
    ("related_does_not_grant_publish", 80, "publish_safe", "related", "medium", "current", "approved", False, "block_false_authority", "related_does_not_grant_publish_safe"),
    ("peer_comparison_does_not_grant_identity", 90, "same_identity", "peer_comparison", "medium", "current", "none", False, "block_false_authority", "peer_comparison_does_not_grant_same_identity"),
    ("bridge_context_does_not_grant_evidence", 80, "evidence_support", "bridge_context", "medium", "current", "none", False, "block_false_authority", "bridge_context_does_not_grant_evidence_support"),
    ("evidence_does_not_grant_action", 90, "action_ready", "evidence_support", "authoritative", "current", "none", False, "block_false_authority", "evidence_support_does_not_grant_action_ready"),
    ("evidence_does_not_grant_publish", 90, "publish_safe", "evidence_support", "authoritative", "current", "approved", False, "block_false_authority", "evidence_support_does_not_grant_publish_safe"),
    ("stale_or_superseded_evidence_blocks_use", 90, "evidence_support", "evidence_support", "authoritative", "stale", "none", False, "block_false_authority", "freshness_blocks_use"),
    ("contradiction_blocks_allow", 90, "evidence_support", "contradiction", "authoritative", "current", "none", False, "block_contradiction", "candidate_contradicts_requested_claim"),
    ("privacy_blocks_all_downstream_use", 80, "customer_safe", "privacy_blocked", "internal", "current", "approved", True, "block_privacy", "privacy_boundary_blocks_all_use"),
    ("valid_evidence_support", 100, "evidence_support", "evidence_support", "authoritative", "current", "none", False, "allow_evidence", "boundary_grants_evidence_support"),
    ("valid_action_ready", 90, "action_ready", "action_ready", "authoritative", "current", "approved", False, "allow_action", "boundary_grants_action_ready"),
    ("valid_publish_safe", 80, "publish_safe", "publish_safe", "authoritative", "current", "approved", False, "allow_publish", "boundary_grants_publish_safe"),
    ("adversarial_mixed_cases", 40, "publish_safe", "related", "medium", "current", "approved", False, "block_false_authority", "multi_signal_false_authority"),
]

ARCHETYPE_SPECS = [
    {
        "archetype": item[0],
        "target_rows": item[1],
        "requested_authority": item[2],
        "boundary_type": item[3],
        "source_authority": item[4],
        "freshness_state": item[5],
        "action_scope": item[6],
        "contains_sensitive_data": item[7],
        "expected_decision": item[8],
        "expected_reason_family": item[9],
    }
    for item in ARCHETYPE_SPECS
]

SCENARIOS = [
    {
        "scenario_key": "refund_30_day_auto_reject",
        "business_scenario": "30-day refund rule",
        "customer_question": "Can we automatically reject refund requests submitted after 30 days?",
        "fact": "the policy mentions that standard refunds are normally requested within 30 days of purchase",
        "action": "automatic rejection of late refund requests",
        "publish": "customer-facing statement that late refunds are always rejected",
    },
    {
        "scenario_key": "invoice_manager_approval",
        "business_scenario": "manager approval for invoices above USD 5,000",
        "customer_question": "Can the payment system automatically hold every invoice above USD 5,000?",
        "fact": "the finance policy says invoices above USD 5,000 require manager approval",
        "action": "automatic payment hold",
        "publish": "customer-facing finance-status message",
    },
    {
        "scenario_key": "fraud_account_termination",
        "business_scenario": "fraud review before account termination",
        "customer_question": "Can we terminate this account automatically after a fraud flag?",
        "fact": "the risk workflow says fraud flags may require review",
        "action": "automatic account termination",
        "publish": "account-status notice sent to the customer",
    },
    {
        "scenario_key": "vendor_onboarding_approval",
        "business_scenario": "vendor onboarding approval",
        "customer_question": "Can this vendor be marked approved for procurement use?",
        "fact": "the vendor appears in an onboarding checklist",
        "action": "marking the vendor approved",
        "publish": "approved-vendor status in a buyer portal",
    },
    {
        "scenario_key": "security_exception_request",
        "business_scenario": "security exception approval",
        "customer_question": "Can we treat this security exception request as approved?",
        "fact": "the ticket confirms that an exception request was opened",
        "action": "granting the exception",
        "publish": "security approval status shared outside the security team",
    },
    {
        "scenario_key": "contract_renewal_discussion",
        "business_scenario": "contract renewal status",
        "customer_question": "Can we tell the customer the contract has renewed?",
        "fact": "the account notes discuss renewal terms",
        "action": "updating renewal status",
        "publish": "customer-facing renewed-contract claim",
    },
    {
        "scenario_key": "discount_pricing_approval",
        "business_scenario": "discount approval",
        "customer_question": "Can sales quote this discounted price to the customer?",
        "fact": "an internal note discusses a possible discount",
        "action": "issuing the quote",
        "publish": "customer-facing price offer",
    },
    {
        "scenario_key": "support_escalation_reuse",
        "business_scenario": "support escalation from a similar ticket",
        "customer_question": "Can we apply the same resolution to this customer's support ticket?",
        "fact": "a similar historical ticket used a resolution path",
        "action": "applying the resolution automatically",
        "publish": "support response sent to the customer",
    },
    {
        "scenario_key": "customer_alert_threshold",
        "business_scenario": "customer alert threshold",
        "customer_question": "Can this event trigger a customer alert?",
        "fact": "the monitoring document mentions the threshold condition",
        "action": "triggering a customer alert",
        "publish": "alert text sent to the customer",
    },
    {
        "scenario_key": "data_retention_deletion",
        "business_scenario": "data retention deletion",
        "customer_question": "Can we delete this data immediately under the retention policy?",
        "fact": "the retention policy mentions this record type",
        "action": "deleting the data",
        "publish": "customer-facing deletion confirmation",
    },
    {
        "scenario_key": "shipping_address_change",
        "business_scenario": "shipping address change",
        "customer_question": "Can we update the shipping address without secondary confirmation?",
        "fact": "the order note mentions an address-change request",
        "action": "updating the address",
        "publish": "customer-facing confirmation of the new address",
    },
    {
        "scenario_key": "access_role_upgrade",
        "business_scenario": "access role upgrade",
        "customer_question": "Can this user be granted admin access?",
        "fact": "the access request mentions admin permissions",
        "action": "granting admin access",
        "publish": "admin-access confirmation",
    },
    {
        "scenario_key": "sla_credit_eligibility",
        "business_scenario": "SLA credit eligibility",
        "customer_question": "Can we grant an SLA credit for this incident?",
        "fact": "the incident report mentions downtime",
        "action": "granting the SLA credit",
        "publish": "customer-facing SLA credit approval",
    },
    {
        "scenario_key": "warranty_replacement",
        "business_scenario": "warranty replacement approval",
        "customer_question": "Can we approve a warranty replacement?",
        "fact": "the support article lists warranty replacement criteria",
        "action": "approving replacement",
        "publish": "customer-facing warranty approval",
    },
    {
        "scenario_key": "cancellation_fee_waiver",
        "business_scenario": "cancellation fee waiver",
        "customer_question": "Can we waive the cancellation fee?",
        "fact": "the policy notes mention waiver requests",
        "action": "waiving the fee",
        "publish": "customer-facing waiver confirmation",
    },
    {
        "scenario_key": "product_deprecation_notice",
        "business_scenario": "product deprecation notice",
        "customer_question": "Can we publish that this product is deprecated?",
        "fact": "the roadmap notes discuss possible deprecation",
        "action": "marking the product deprecated",
        "publish": "public deprecation notice",
    },
    {
        "scenario_key": "incident_postmortem_claim",
        "business_scenario": "incident postmortem cause",
        "customer_question": "Can we tell customers this was the root cause?",
        "fact": "the incident notes mention a suspected cause",
        "action": "closing the incident cause",
        "publish": "customer-facing root-cause statement",
    },
    {
        "scenario_key": "feature_entitlement",
        "business_scenario": "feature entitlement",
        "customer_question": "Can this account use the premium feature?",
        "fact": "the plan page mentions the feature family",
        "action": "enabling the feature",
        "publish": "customer-facing entitlement confirmation",
    },
    {
        "scenario_key": "procurement_quote_selection",
        "business_scenario": "procurement quote selection",
        "customer_question": "Can procurement select this quote as the approved quote?",
        "fact": "the quote is listed in the procurement workspace",
        "action": "selecting the quote",
        "publish": "approved quote status",
    },
    {
        "scenario_key": "policy_exception_customer_message",
        "business_scenario": "policy exception customer message",
        "customer_question": "Can we message the customer that an exception was granted?",
        "fact": "the exception thread says the request is under review",
        "action": "granting the exception",
        "publish": "customer-facing exception approval",
    },
]

FRESHNESS_CYCLE = ["stale", "superseded", "expired", "deprecated"]
SOURCE_OBJECTS = ["policy doc", "support ticket", "contract clause", "operator note", "dashboard row", "search result"]


def similarity_score(index: int) -> float:
    return round(0.84 + ((index * 11) % 14) * 0.01, 2)


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    global_index = 1
    for spec in ARCHETYPE_SPECS:
        for local_index in range(1, spec["target_rows"] + 1):
            scenario = SCENARIOS[(global_index - 1) % len(SCENARIOS)]
            row_spec = dict(spec)
            if spec["archetype"] == "stale_or_superseded_evidence_blocks_use":
                row_spec["freshness_state"] = FRESHNESS_CYCLE[(local_index - 1) % len(FRESHNESS_CYCLE)]
            if spec["archetype"] == "adversarial_mixed_cases":
                row_spec.update(adversarial_override(local_index))
            rows.append(build_row(row_spec, scenario, global_index, local_index))
            global_index += 1
    return rows


def adversarial_override(local_index: int) -> dict[str, Any]:
    choices = [
        ("customer_safe", "privacy_blocked", "internal", "current", "approved", True, "block_privacy", "privacy_boundary_blocks_all_use"),
        ("evidence_support", "contradiction", "authoritative", "current", "none", False, "block_contradiction", "candidate_contradicts_requested_claim"),
        ("publish_safe", "publish_safe", "low", "current", "approved", False, "block_false_authority", "source_authority_low"),
        ("action_ready", "action_ready", "authoritative", "expired", "approved", False, "block_false_authority", "freshness_state_expired"),
        ("customer_safe", "related", "medium", "current", "approved", False, "block_false_authority", "related_does_not_grant_customer_safe"),
    ]
    item = choices[(local_index - 1) % len(choices)]
    return {
        "requested_authority": item[0],
        "boundary_type": item[1],
        "source_authority": item[2],
        "freshness_state": item[3],
        "action_scope": item[4],
        "contains_sensitive_data": item[5],
        "expected_decision": item[6],
        "expected_reason_family": item[7],
    }


def build_row(spec: dict[str, Any], scenario: dict[str, str], global_index: int, local_index: int) -> dict[str, Any]:
    source_object = SOURCE_OBJECTS[(global_index + local_index) % len(SOURCE_OBJECTS)]
    content = content_for(spec, scenario, source_object)
    case_id = f"cbe1000-{global_index:04d}"
    return {
        "case_id": case_id,
        "query": scenario["customer_question"],
        "candidate": content["retrieved_source"],
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
        "business_scenario": scenario["business_scenario"],
        "scenario_key": scenario["scenario_key"],
        "customer_question": scenario["customer_question"],
        "retrieved_source": content["retrieved_source"],
        "what_it_proves": content["what_it_proves"],
        "what_it_does_not_prove": content["what_it_does_not_prove"],
        "wrong_llm_move": content["wrong_llm_move"],
        "correct_boundary_decision": content["correct_boundary_decision"],
        "source_object": source_object,
    }


def content_for(spec: dict[str, Any], scenario: dict[str, str], source_object: str) -> dict[str, str]:
    fact = scenario["fact"]
    action = scenario["action"]
    publish = scenario["publish"]
    boundary = spec["boundary_type"]
    requested = spec["requested_authority"]
    expected = spec["expected_decision"]

    if boundary == "related":
        retrieved = f"The {source_object} uses terms related to {scenario['business_scenario']}: {fact}."
        proves = "The topic is relevant to the question."
        not_proves = f"It does not prove that {publish} is approved or customer-safe."
        wrong = "Treating topical similarity as permission to publish or share a customer-facing claim."
    elif boundary == "peer_comparison":
        retrieved = f"The {source_object} describes a similar case in another account or workflow: {fact}."
        proves = "A comparable case exists."
        not_proves = "It does not prove this is the same account, vendor, contract, product, or decision identity."
        wrong = "Treating a comparable peer as the same identity."
    elif boundary == "bridge_context":
        retrieved = f"The {source_object} is a glossary or navigation entry explaining the topic: {fact}."
        proves = "The term or workflow exists."
        not_proves = "It does not directly support the claim as evidence."
        wrong = "Using glossary or navigation context as proof."
    elif boundary == "contradiction":
        retrieved = f"The authoritative {source_object} discusses the topic but says the requested claim is not allowed."
        proves = "There is direct contradictory evidence."
        not_proves = "It does not support the requested claim."
        wrong = "Using a relevant but contradictory source as positive evidence."
    elif boundary == "privacy_blocked":
        retrieved = f"The internal {source_object} includes the relevant fact but also contains a private tenant marker and customer-specific trace."
        proves = "A private internal source mentions the topic."
        not_proves = "It is not safe for customer-facing output or downstream reuse."
        wrong = "Promoting private or tenant-specific material into a customer-safe answer."
    elif spec["freshness_state"] in FRESHNESS_CYCLE:
        retrieved = f"The {source_object} once supported the claim that {fact}, but the source is {spec['freshness_state']}."
        proves = "The claim existed in an older or inactive source."
        not_proves = "It does not prove the claim is currently valid."
        wrong = "Ignoring stale, expired, deprecated, or superseded status."
    elif boundary == "evidence_support" and requested == "action_ready":
        retrieved = f"The authoritative {source_object} says {fact}."
        proves = "The factual claim is supported."
        not_proves = f"It does not authorize {action}."
        wrong = "Converting evidence into action permission."
    elif boundary == "evidence_support" and requested == "publish_safe":
        retrieved = f"The authoritative {source_object} says {fact}."
        proves = "The factual claim is supported."
        not_proves = f"It does not approve {publish}."
        wrong = "Converting evidence into a publish-safe customer claim."
    elif expected == "allow_evidence":
        retrieved = f"The current authoritative {source_object} directly says {fact}."
        proves = "The requested factual evidence is directly supported."
        not_proves = "It only grants evidence support, not action or publish authority."
        wrong = "No error expected; the guard should preserve this allow."
    elif expected == "allow_action":
        retrieved = f"The current authoritative {source_object} says {fact} and explicitly approves {action}."
        proves = "Both the fact and the action permission are present."
        not_proves = "It does not automatically grant publish-safe customer messaging."
        wrong = "No error expected; the guard should preserve this action allow."
    elif expected == "allow_publish":
        retrieved = f"The current authoritative {source_object} says {fact} and explicitly approves {publish}."
        proves = "The fact and publish-safe boundary are both present."
        not_proves = "It does not grant unrelated future claims."
        wrong = "No error expected; the guard should preserve this publish allow."
    else:
        retrieved = f"The {source_object} is highly similar to the question about {scenario['business_scenario']}."
        proves = "The content is similar."
        not_proves = "It does not grant the requested authority."
        wrong = "Treating similarity as authority."

    return {
        "retrieved_source": retrieved,
        "what_it_proves": proves,
        "what_it_does_not_prove": not_proves,
        "wrong_llm_move": wrong,
        "correct_boundary_decision": expected,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def write_archetype_counts(path: Path, rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = dict(sorted(Counter(row["archetype"] for row in rows).items()))
    write_csv(path, [{"archetype": k, "row_count": v} for k, v in counts.items()], ["archetype", "row_count"])
    return counts


def write_sample_markdown(path: Path, rows: list[dict[str, Any]], limit: int = 20) -> None:
    selected: list[dict[str, Any]] = []
    seen_archetypes: set[str] = set()
    for row in rows:
        if row["archetype"] not in seen_archetypes:
            selected.append(row)
            seen_archetypes.add(row["archetype"])
    for row in rows:
        if len(selected) >= limit:
            break
        if row not in selected:
            selected.append(row)
    lines = ["# Concept Boundary 1000 Test Content Samples", ""]
    for row in selected:
        lines.extend(
            [
                f"## {row['case_id']} - {row['business_scenario']}",
                "",
                f"- Customer question: {row['customer_question']}",
                f"- Retrieved source: {row['retrieved_source']}",
                f"- What it proves: {row['what_it_proves']}",
                f"- What it does not prove: {row['what_it_does_not_prove']}",
                f"- Wrong LLM move: {row['wrong_llm_move']}",
                f"- Correct decision: `{row['expected_decision']}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_manifest(
    rows: list[dict[str, Any]],
    output: Path,
    out_dir: Path,
    summary: dict[str, Any],
    archetype_counts: dict[str, int],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "mode": "concept_boundary_1000_test_content_builder",
        "status": "pass" if summary.get("status") == "pass" and len(rows) == 1000 else "fail",
        "data_classification": "synthetic",
        "contains_customer_data": False,
        "external_services_used": False,
        "production_truth_mutation": False,
        "customer_surface_mutation": False,
        "row_count": len(rows),
        "scenario_count": len({row["scenario_key"] for row in rows}),
        "archetype_count": len(archetype_counts),
        "archetype_counts": archetype_counts,
        "probe_summary": summary,
        "outputs": {
            "cases": str(output),
            "content_catalog": str(out_dir / "content_catalog.csv"),
            "summary": str(out_dir / "summary.json"),
            "decisions": str(out_dir / "decisions.csv"),
            "report": str(out_dir / "report.md"),
            "manifest": str(out_dir / "manifest.json"),
            "sample_markdown": str(out_dir / "sample_cases.md"),
            "archetype_counts": str(out_dir / "archetype_counts.csv"),
        },
    }


def run(output: Path = DEFAULT_OUTPUT, out_dir: Path = DEFAULT_OUT_DIR, threshold: float = 0.82) -> dict[str, Any]:
    rows = build_rows()
    write_jsonl(output, rows)
    summary = probe.run(output, out_dir, threshold)
    catalog_fields = [
        "case_id",
        "business_scenario",
        "customer_question",
        "retrieved_source",
        "what_it_proves",
        "what_it_does_not_prove",
        "wrong_llm_move",
        "requested_authority",
        "boundary_type",
        "source_authority",
        "freshness_state",
        "action_scope",
        "expected_decision",
        "archetype",
    ]
    write_csv(out_dir / "content_catalog.csv", rows, catalog_fields)
    write_sample_markdown(out_dir / "sample_cases.md", rows)
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
