"""Build the proof-contract-corrected v0.6 authority-action dataset.

v0.6 preserves every v0.5 case and adds a compact, machine-resolvable proof
path for the candidate authorization record. The proof path binds the record
to a canonical digest, an authority-registry signer, signature verification,
and an explicit finality state. This repairs the positive-control contract
without replacing the underlying multi-record reasoning with a prose answer.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.build_authority_cases_v0_4 import SCENARIOS  # noqa: E402
from scripts.build_authority_cases_v0_5 import build_rows as build_v0_5_rows  # noqa: E402


OUTPUT_PATH = REPO_ROOT / "evals" / "data" / "authority_action_cases_v0_6.jsonl"
EVIDENCE_MARKER = "EVIDENCE RECORDS\n"
CONTEXT_MARKER = "\nOPERATING CONTEXT\n"
AUTH_ID_PATTERN = re.compile(r"^([A-Z][A-Z0-9-]+)\s+\|")


def evidence_records(prompt: str) -> list[str]:
    """Return record bodies from the prompt's evidence section."""

    _, remainder = prompt.split(EVIDENCE_MARKER, maxsplit=1)
    evidence, _ = remainder.split(CONTEXT_MARKER, maxsplit=1)
    return [line[2:] for line in evidence.splitlines() if line.startswith("- ")]


def candidate_authorization_id(
    *,
    expected_authorization_id: str,
    invalid_condition: str,
    records: list[str],
) -> str:
    """Resolve the record whose proof path the cell must evaluate."""

    if invalid_condition == "draft_not_final":
        for record in records:
            match = AUTH_ID_PATTERN.match(record)
            if match and match.group(1).startswith(f"{expected_authorization_id}-"):
                return match.group(1)
    return expected_authorization_id


def authentic_source_record(records: list[str], candidate_id: str) -> str | None:
    """Find an actual authorization or ledger record, excluding mere claims."""

    for record in records:
        leading_id = record.split(" |", maxsplit=1)[0]
        if leading_id == candidate_id:
            return record
        fields = {
            field.split("=", maxsplit=1)[0].strip(): field.split("=", maxsplit=1)[1].strip()
            for field in record.split("|")[1:]
            if "=" in field
        }
        if fields.get("record") == candidate_id:
            return record
    return None


def record_fields(record: str) -> dict[str, str]:
    return {
        field.split("=", maxsplit=1)[0].strip(): field.split("=", maxsplit=1)[1].strip()
        for field in record.split("|")[1:]
        if "=" in field
    }


def declared_canonical_digest(records: list[str], signature: str | None) -> str | None:
    """Resolve a pre-existing digest through a matching signature record."""

    if signature is None:
        return None
    for record in records:
        fields = record_fields(record)
        if signature not in {fields.get("signature"), fields.get("canonical_signature")}:
            continue
        if fields.get("canonical_digest"):
            return fields["canonical_digest"]
    return None


def proof_records(
    *,
    group_index: int,
    valid: bool,
    current_time: str,
    candidate_id: str,
    invalid_condition: str,
    source_record: str | None,
    base_records: list[str],
) -> tuple[list[str], dict[str, object]]:
    """Create a compact canonicalization, registry, verification, finality chain."""

    cell = "V" if valid else "I"
    canonical_id = f"PF-CAN-{group_index:02d}-{cell}"
    registry_id = f"PF-REG-{group_index:02d}-{cell}"
    verification_id = f"PF-VER-{group_index:02d}-{cell}"
    finality_id = f"PF-FIN-{group_index:02d}-{cell}"
    signer_key = f"key-{group_index:02d}"

    if invalid_condition == "unverified_source" and not valid:
        digest = "unresolved"
        registry_state = "not_found"
        signature_state = "unverified"
        registry_match = "false"
        finality_state = "committed"
        contract_state = "unverified"
        signature = "unresolved"
        digest_binding = "unresolved"
        source_id: str | None = None
        source_digest: str | None = None
    else:
        if source_record is None:
            raise ValueError(f"{candidate_id}: authentic source record is missing")
        source_fields = record_fields(source_record)
        signer_key = source_fields.get("signer_key", signer_key)
        signature = source_fields.get("signature", f"sig:pf-{group_index:02d}-{cell.lower()}")
        declared_digest = declared_canonical_digest(base_records, source_fields.get("signature"))
        if declared_digest is not None:
            digest = declared_digest
            digest_binding = "declared_signature_chain"
        else:
            digest = "sha256:" + hashlib.sha256(source_record.encode("utf-8")).hexdigest()
            digest_binding = "computed_source_record"
        registry_state = "active"
        signature_state = "valid"
        registry_match = "true"
        finality_state = (
            "pending" if invalid_condition == "draft_not_final" and not valid else "committed"
        )
        contract_state = "not_final" if finality_state == "pending" else "verified_final"
        source_id = candidate_id
        source_digest = digest

    records = [
        f"{canonical_id} | record={candidate_id} | digest={digest} | binding={digest_binding}",
        (
            f"{registry_id} | signer={signer_key} | state={registry_state} | "
            "valid_from=2026-01-01T00:00:00Z | valid_until=2026-12-31T23:59:59Z"
        ),
        (
            f"{verification_id} | canonical={canonical_id} | signer={signer_key} | "
            f"signature={signature} | result={signature_state} | registry={registry_id} | "
            f"registry_match={registry_match} | checked_at={current_time}"
        ),
        f"{finality_id} | canonical={canonical_id} | state={finality_state}",
    ]
    metadata = {
        "proof_contract_version": "canonical_registry_signature_finality_v1",
        "proof_contract_state": contract_state,
        "proof_candidate_authorization_id": candidate_id,
        "proof_source_record_id": source_id,
        "proof_source_digest": source_digest,
        "proof_digest_binding": digest_binding,
        "proof_signer_key": signer_key,
        "proof_signature": signature,
        "proof_record_ids": [canonical_id, registry_id, verification_id, finality_id],
    }
    return records, metadata


def append_proof_records(prompt: str, records: list[str]) -> str:
    head, context = prompt.split(CONTEXT_MARKER, maxsplit=1)
    rendered = "\n".join(f"- {record}" for record in records)
    return f"{head}\n{rendered}{CONTEXT_MARKER}{context}"


def build_rows() -> list[dict[str, object]]:
    rows = build_v0_5_rows()
    scenarios = {scenario.pair_id: scenario for scenario in SCENARIOS}
    group_order = {scenario.pair_id: index for index, scenario in enumerate(SCENARIOS, start=1)}

    for row in rows:
        metadata = row["metadata"]
        if not isinstance(metadata, dict):
            raise TypeError("v0.5 metadata must be an object")
        pair_id = str(metadata["pair_id"])
        scenario = scenarios[pair_id]
        valid = metadata["expected_action"] == "execute"
        records = evidence_records(str(row["input"]))
        candidate_id = candidate_authorization_id(
            expected_authorization_id=scenario.authorization_id,
            invalid_condition=scenario.invalid_condition,
            records=records,
        )
        source_record = authentic_source_record(records, candidate_id)
        added_records, proof_metadata = proof_records(
            group_index=group_order[pair_id],
            valid=valid,
            current_time=str(metadata["current_time"]),
            candidate_id=candidate_id,
            invalid_condition=scenario.invalid_condition,
            source_record=source_record,
            base_records=records,
        )
        row["input"] = append_proof_records(str(row["input"]), added_records)
        metadata.update(proof_metadata)

    return rows


def main() -> int:
    rows = build_rows()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(f"wrote {len(rows)} cases to {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
