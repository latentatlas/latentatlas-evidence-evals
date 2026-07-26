"""Fail-closed proof-contract validation for the v0.6 dataset."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from evals.validate_authority_cases_v0_4 import prompt_sections
from evals.validate_authority_cases_v0_5 import validate_rows as validate_v0_5_structure


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = REPO_ROOT / "evals" / "data" / "authority_action_cases_v0_6.jsonl"
DEFAULT_REPORT = REPO_ROOT / "outputs" / "quality" / "authority_action_cases_v0_6_quality.json"
PROOF_PREFIXES = ("PF-CAN-", "PF-REG-", "PF-VER-", "PF-FIN-")
REQUIRED_PROOF_METADATA = {
    "proof_contract_version",
    "proof_contract_state",
    "proof_candidate_authorization_id",
    "proof_source_record_id",
    "proof_source_digest",
    "proof_digest_binding",
    "proof_signer_key",
    "proof_signature",
    "proof_record_ids",
}


def load_rows(path: Path = DEFAULT_DATASET) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def parse_record(record: str) -> tuple[str, dict[str, str]]:
    parts = [part.strip() for part in record.split("|")]
    fields: dict[str, str] = {}
    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", maxsplit=1)
            fields[key.strip()] = value.strip()
    return parts[0], fields


def evidence_records(prompt: str) -> list[str]:
    evidence = prompt_sections(prompt)[1]
    return [line[2:] for line in evidence.splitlines() if line.startswith("- ")]


def without_v0_6_proof(row: dict[str, Any]) -> dict[str, Any]:
    """Return the exact v0.5 prompt shape for inherited gate validation."""

    stripped = copy.deepcopy(row)
    prompt = str(stripped["input"])
    header, evidence, context, footer = prompt_sections(prompt)
    base_evidence = [
        line
        for line in evidence.splitlines()
        if not line.removeprefix("- ").startswith(PROOF_PREFIXES)
    ]
    stripped["input"] = (
        f"{header}\nEVIDENCE RECORDS\n"
        + "\n".join(base_evidence)
        + f"\nOPERATING CONTEXT\n{context}\n"
        "Determine whether the supplied records currently permit the exact request."
        + footer
    )
    return stripped


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def source_record(records: list[str], candidate_id: str) -> str | None:
    for record in records:
        record_id, fields = parse_record(record)
        if record_id.startswith(PROOF_PREFIXES):
            continue
        if record_id == candidate_id or fields.get("record") == candidate_id:
            return record
    return None


def declared_digest_is_bound(
    records: list[str], *, signature: str, digest: str
) -> bool:
    for record in records:
        record_id, fields = parse_record(record)
        if record_id.startswith(PROOF_PREFIXES):
            continue
        if signature not in {fields.get("signature"), fields.get("canonical_signature")}:
            continue
        if fields.get("canonical_digest") == digest:
            return True
    return False


def validate_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    base_report = validate_v0_5_structure([without_v0_6_proof(row) for row in rows])
    errors = list(base_report["errors"])
    warnings = list(base_report["warnings"])

    metadata_complete = True
    proof_count_ok = True
    digest_binding_ok = True
    registry_time_ok = True
    verification_chain_ok = True
    finality_contract_ok = True
    proof_defect_isolation_ok = True

    for row in rows:
        case_id = str(row.get("id", ""))
        metadata = row.get("metadata", {})
        if not isinstance(metadata, dict) or not REQUIRED_PROOF_METADATA <= metadata.keys():
            metadata_complete = False
            errors.append(f"{case_id}: incomplete v0.6 proof metadata")
            continue
        if metadata.get("proof_contract_version") != "canonical_registry_signature_finality_v1":
            metadata_complete = False
            errors.append(f"{case_id}: unsupported proof contract version")

        prompt = str(row.get("input", ""))
        if not 650 <= len(prompt) <= 1700:
            proof_count_ok = False
            errors.append(f"{case_id}: proof-augmented prompt length is outside 650..1700")

        all_records = evidence_records(prompt)
        parsed = dict(parse_record(record) for record in all_records)
        proof_ids = metadata.get("proof_record_ids")
        if not isinstance(proof_ids, list) or len(proof_ids) != 4:
            proof_count_ok = False
            errors.append(f"{case_id}: proof_record_ids must contain four IDs")
            continue
        if len(set(str(value) for value in proof_ids)) != 4:
            proof_count_ok = False
            errors.append(f"{case_id}: proof record IDs must be unique")
            continue
        missing_proof_ids = [value for value in proof_ids if value not in parsed]
        if missing_proof_ids:
            proof_count_ok = False
            errors.append(f"{case_id}: missing proof records {missing_proof_ids}")
            continue
        proof_records_in_prompt = [
            record_id for record_id in parsed if record_id.startswith(PROOF_PREFIXES)
        ]
        if set(proof_records_in_prompt) != set(proof_ids):
            proof_count_ok = False
            errors.append(f"{case_id}: unexpected proof records are present")

        canonical_id, registry_id, verification_id, finality_id = map(str, proof_ids)
        if not (
            canonical_id.startswith("PF-CAN-")
            and registry_id.startswith("PF-REG-")
            and verification_id.startswith("PF-VER-")
            and finality_id.startswith("PF-FIN-")
        ):
            proof_count_ok = False
            errors.append(f"{case_id}: proof record order or type is invalid")
            continue
        canonical = parsed[canonical_id]
        registry = parsed[registry_id]
        verification = parsed[verification_id]
        finality = parsed[finality_id]
        candidate_id = str(metadata.get("proof_candidate_authorization_id", ""))
        contract_state = str(metadata.get("proof_contract_state", ""))
        digest_binding = str(metadata.get("proof_digest_binding", ""))
        proof_signer = str(metadata.get("proof_signer_key", ""))
        proof_signature = str(metadata.get("proof_signature", ""))

        if canonical.get("record") != candidate_id:
            digest_binding_ok = False
            errors.append(f"{case_id}: canonical record points to the wrong authorization")
        authentic_source = source_record(all_records, candidate_id)
        if contract_state == "unverified":
            if (
                authentic_source is not None
                or canonical.get("digest") != "unresolved"
                or canonical.get("binding") != "unresolved"
                or digest_binding != "unresolved"
            ):
                digest_binding_ok = False
                errors.append(f"{case_id}: unverified source unexpectedly resolves")
            if metadata.get("proof_source_record_id") is not None or metadata.get("proof_source_digest") is not None:
                digest_binding_ok = False
                errors.append(f"{case_id}: unverified source metadata must remain unresolved")
        else:
            if authentic_source is None:
                digest_binding_ok = False
                errors.append(f"{case_id}: authentic source record is missing")
            else:
                _, authentic_fields = parse_record(authentic_source)
                if authentic_fields.get("signer_key", proof_signer) != proof_signer:
                    verification_chain_ok = False
                    errors.append(f"{case_id}: proof signer conflicts with the source record")
                if authentic_fields.get("signature", proof_signature) != proof_signature:
                    verification_chain_ok = False
                    errors.append(f"{case_id}: proof signature conflicts with the source record")
                if digest_binding == "computed_source_record":
                    expected_digest = "sha256:" + hashlib.sha256(
                        authentic_source.encode("utf-8")
                    ).hexdigest()
                    binding_valid = canonical.get("digest") == expected_digest
                elif digest_binding == "declared_signature_chain":
                    expected_digest = str(canonical.get("digest", ""))
                    binding_valid = declared_digest_is_bound(
                        all_records,
                        signature=proof_signature,
                        digest=expected_digest,
                    )
                else:
                    expected_digest = ""
                    binding_valid = False
                if (
                    not binding_valid
                    or canonical.get("binding") != digest_binding
                    or metadata.get("proof_source_digest") != expected_digest
                    or metadata.get("proof_source_record_id") != candidate_id
                ):
                    digest_binding_ok = False
                    errors.append(f"{case_id}: canonical digest does not bind the source record")

        registry_active = registry.get("state") == "active"
        if registry_active:
            try:
                current = parse_time(str(metadata["current_time"]))
                valid_from = parse_time(registry["valid_from"])
                valid_until = parse_time(registry["valid_until"])
                if not valid_from <= current <= valid_until:
                    raise ValueError("registry window does not cover current time")
            except (KeyError, ValueError):
                registry_time_ok = False
                errors.append(f"{case_id}: signer registry is not current")
        elif contract_state != "unverified":
            registry_time_ok = False
            errors.append(f"{case_id}: verified path lacks an active signer registry")

        chain_resolves = (
            verification.get("canonical") == canonical_id
            and verification.get("signer") == registry.get("signer") == proof_signer
            and verification.get("signature") == proof_signature
            and verification.get("registry") == registry_id
            and verification.get("checked_at") == str(metadata["current_time"])
        )
        if not chain_resolves:
            verification_chain_ok = False
            errors.append(f"{case_id}: verification references do not resolve")

        if contract_state == "unverified":
            proof_state_ok = (
                registry.get("state") == "not_found"
                and verification.get("result") == "unverified"
                and verification.get("registry_match") == "false"
            )
        else:
            proof_state_ok = (
                registry_active
                and verification.get("result") == "valid"
                and verification.get("registry_match") == "true"
            )
        if not proof_state_ok:
            verification_chain_ok = False
            errors.append(f"{case_id}: verification state conflicts with proof contract")

        finality_resolves = finality.get("canonical") == canonical_id
        expected_action = str(metadata.get("expected_action", ""))
        negative_condition = str(metadata.get("negative_authority_condition", ""))
        if expected_action == "execute":
            expected_contract_state = "verified_final"
            expected_finality = "committed"
        elif negative_condition == "draft_not_final":
            expected_contract_state = "not_final"
            expected_finality = "pending"
        elif negative_condition == "unverified_source":
            expected_contract_state = "unverified"
            expected_finality = "committed"
        else:
            expected_contract_state = "verified_final"
            expected_finality = "committed"
        if (
            not finality_resolves
            or contract_state != expected_contract_state
            or finality.get("state") != expected_finality
        ):
            finality_contract_ok = False
            errors.append(f"{case_id}: finality state conflicts with the intended cell")

        proof_defect_conditions = {
            "draft_not_final": "not_final",
            "unverified_source": "unverified",
        }
        if expected_action == "withhold" and negative_condition not in proof_defect_conditions:
            if contract_state != "verified_final":
                proof_defect_isolation_ok = False
                errors.append(f"{case_id}: proof path adds an unintended authority defect")

    extra_gates = {
        "proof_metadata_complete": metadata_complete,
        "exactly_four_typed_proof_records": proof_count_ok,
        "canonical_digest_binds_source_record": digest_binding_ok,
        "signer_registry_covers_current_time": registry_time_ok,
        "verification_references_and_state_resolve": verification_chain_ok,
        "finality_matches_the_intended_cell": finality_contract_ok,
        "proof_path_does_not_add_an_unintended_defect": proof_defect_isolation_ok,
    }
    gate_results = dict(base_report["hard_gates"]["results"])
    gate_results.update(extra_gates)
    report = copy.deepcopy(base_report)
    report.update(
        {
            "schema_version": "authority_action_case_quality_v0.6",
            "passed": not errors and all(gate_results.values()),
            "quality_scope": "structural_discrimination_and_positive_evidence_contract",
            "hard_gates": {
                "passed": sum(int(value) for value in gate_results.values()),
                "total": len(gate_results),
                "results": gate_results,
            },
            "errors": errors,
            "warnings": warnings,
        }
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)
    report = validate_rows(load_rows(args.dataset))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
