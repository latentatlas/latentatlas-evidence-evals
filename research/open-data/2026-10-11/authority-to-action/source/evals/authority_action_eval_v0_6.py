"""Inspect v0.6 authority-action evaluation with explicit proof contracts."""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message, use_tools

from evals.authority_action_eval_v0_4 import EXPECTED_ACTIONS
from evals.authority_action_eval_v0_4 import SYSTEM_MESSAGE
from evals.authority_action_eval_v0_4 import authority_action_scorer
from evals.authority_action_eval_v0_4 import execute_action
from evals.authority_action_eval_v0_5 import read_samples as read_v0_5_samples


DATASET_PATH = Path(__file__).parent / "data" / "authority_action_cases_v0_6.jsonl"
REQUIRED_V0_6_FIELDS = {
    "proof_contract_version",
    "proof_contract_state",
    "proof_candidate_authorization_id",
    "proof_source_record_id",
    "proof_source_digest",
    "proof_record_ids",
}


def read_samples(path: Path = DATASET_PATH):
    samples = read_v0_5_samples(path)
    for sample in samples:
        missing = sorted(REQUIRED_V0_6_FIELDS - sample.metadata.keys())
        if missing:
            raise ValueError(f"{sample.id}: missing v0.6 metadata fields: {missing}")
        if sample.metadata["proof_contract_version"] != "canonical_registry_signature_finality_v1":
            raise ValueError(f"{sample.id}: unsupported proof contract version")
        if sample.metadata["proof_contract_state"] not in {
            "verified_final",
            "not_final",
            "unverified",
        }:
            raise ValueError(f"{sample.id}: unsupported proof contract state")
        proof_ids = sample.metadata["proof_record_ids"]
        if not isinstance(proof_ids, list) or len(proof_ids) != 4:
            raise ValueError(f"{sample.id}: proof_record_ids must contain four IDs")
    return samples


@task
def authority_action_eval(case_type: str = "all") -> Task:
    if case_type not in {"all", *EXPECTED_ACTIONS}:
        raise ValueError("case_type must be all, execute, or withhold")
    samples = read_samples()
    if case_type != "all":
        samples = [sample for sample in samples if sample.metadata["expected_action"] == case_type]
    return Task(
        dataset=samples,
        solver=[
            system_message(SYSTEM_MESSAGE),
            use_tools(execute_action()),
            generate(tool_calls="loop"),
        ],
        scorer=authority_action_scorer(),
        message_limit=6,
        metadata={
            "research_question": "Do frontier systems execute only when a multi-record proof path establishes current, final, verified, exact authority under contextual pressure?",
            "external_side_effects": False,
            "dataset_version": "authority_action_cases_v0.6-candidate",
            "design": "v0.5_high_discrimination_plus_machine_resolvable_proof_contract",
        },
        tags=[
            "agentic",
            "authorization",
            "factorial-design",
            "high-discrimination",
            "proof-contract",
            "provider-refusal",
            "inspect",
        ],
        version="0.6.0",
    )
