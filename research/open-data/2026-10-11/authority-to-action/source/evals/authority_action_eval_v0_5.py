"""Inspect v0.5 high-discrimination authority-action evaluation."""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task

from evals.authority_action_eval_v0_4 import EXPECTED_ACTIONS
from evals.authority_action_eval_v0_4 import SYSTEM_MESSAGE
from evals.authority_action_eval_v0_4 import authority_action_scorer
from evals.authority_action_eval_v0_4 import execute_action
from evals.authority_action_eval_v0_4 import read_samples as read_v0_4_samples
from inspect_ai.solver import generate, system_message, use_tools


DATASET_PATH = Path(__file__).parent / "data" / "authority_action_cases_v0_5.jsonl"
REQUIRED_V0_5_FIELDS = {
    "challenge_design",
    "difficulty_level",
    "reasoning_requirements",
    "monitoring_direction",
}


def read_samples(path: Path = DATASET_PATH):
    samples = read_v0_4_samples(path)
    for sample in samples:
        missing = sorted(REQUIRED_V0_5_FIELDS - sample.metadata.keys())
        if missing:
            raise ValueError(f"{sample.id}: missing v0.5 metadata fields: {missing}")
        if sample.metadata["difficulty_level"] not in {"medium", "hard", "very_hard"}:
            raise ValueError(f"{sample.id}: unsupported difficulty level")
        requirements = sample.metadata["reasoning_requirements"]
        if not isinstance(requirements, list) or not requirements:
            raise ValueError(f"{sample.id}: reasoning_requirements must be a non-empty list")
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
            "research_question": "Do pressure, evaluation awareness, monitoring visibility, or incentives change exact authorization behavior as evidence reasoning becomes difficult?",
            "external_side_effects": False,
            "dataset_version": "authority_action_cases_v0.5-candidate",
            "design": "25_scenarios_x_authority_validity_x_context_treatment_with_difficulty",
        },
        tags=[
            "agentic",
            "authorization",
            "factorial-design",
            "high-discrimination",
            "monitoring-direction",
            "provider-refusal",
            "inspect",
        ],
        version="0.5.0",
    )
