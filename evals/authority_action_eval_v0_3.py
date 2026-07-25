"""Paired-prompt extension of the authority-to-action Inspect evaluation."""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.solver import generate, system_message, use_tools

from evals.authority_action_eval_v0_2 import EXPECTED_ACTIONS
from evals.authority_action_eval_v0_2 import SYSTEM_MESSAGE
from evals.authority_action_eval_v0_2 import authority_action_scorer
from evals.authority_action_eval_v0_2 import execute_action
from evals.authority_action_eval_v0_2 import read_samples as read_v0_2_samples


BASE_DATASET_PATH = Path(__file__).parent / "data" / "authority_action_cases.jsonl"
PAIR_DATASET_PATH = (
    Path(__file__).parent / "data" / "authority_action_prompt_pairs_v0_3.jsonl"
)
PAIR_ID = "similarity_without_authority_v7"
PRESSURE_SAMPLE_ID = "withhold_similarity_pressure"


def read_samples() -> list[Sample]:
    """Load the frozen v0.2 set plus the v0.3 neutral paired control."""

    base_samples = read_v0_2_samples(BASE_DATASET_PATH)
    pair_samples = read_v0_2_samples(PAIR_DATASET_PATH)
    combined = [*base_samples, *pair_samples]
    ids = [str(sample.id) for sample in combined]
    if len(ids) != len(set(ids)):
        raise ValueError("v0.3 combined dataset contains duplicate sample IDs")

    samples: list[Sample] = []
    for sample in combined:
        metadata = dict(sample.metadata or {})
        if str(sample.id) == PRESSURE_SAMPLE_ID:
            metadata.update(
                {
                    "pair_id": PAIR_ID,
                    "prompt_variant": "pressure",
                }
            )
        samples.append(
            Sample(
                id=sample.id,
                input=sample.input,
                target=sample.target,
                metadata=metadata,
            )
        )
    return samples


@task
def authority_action_eval(case_type: str = "all") -> Task:
    """Evaluate authorization behavior with a paired prompt diagnostic."""

    if case_type not in {"all", *EXPECTED_ACTIONS}:
        raise ValueError("case_type must be all, execute, or withhold")
    samples = read_samples()
    if case_type != "all":
        samples = [
            sample
            for sample in samples
            if sample.metadata["expected_action"] == case_type
        ]
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
            "research_question": "Does prompt pressure change authorization behavior or provider refusal?",
            "external_side_effects": False,
            "dataset_version": "authority_action_cases_v0.2-paired",
            "paired_diagnostic": PAIR_ID,
        },
        tags=[
            "agentic",
            "authorization",
            "negative-controls",
            "paired-prompts",
            "inspect",
        ],
        version="0.3.1",
    )
