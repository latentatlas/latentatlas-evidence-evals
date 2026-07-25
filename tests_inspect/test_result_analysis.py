from __future__ import annotations

import unittest

from evals.analyze_authority_results import ResultRow
from evals.analyze_authority_results import aggregate_rows
from evals.analyze_authority_results import render_markdown


def result_row(
    *,
    sample_id: str,
    expected_action: str,
    authority_condition: str,
    correct_decision: float,
    unsafe_action: float,
    unnecessary_withhold: float,
    model_refusal: float = 0.0,
    pair_id: str | None = None,
    prompt_variant: str | None = None,
) -> ResultRow:
    return ResultRow(
        model="test/model",
        sample_id=sample_id,
        expected_action=expected_action,
        authority_condition=authority_condition,
        control_type="test_control",
        metrics={
            "correct_decision": correct_decision,
            "usable_decision": correct_decision * (1.0 - model_refusal),
            "explicit_withhold": float(
                expected_action == "withhold"
                and correct_decision == 1.0
                and model_refusal == 0.0
            ),
            "unsafe_action": unsafe_action,
            "unnecessary_withhold": unnecessary_withhold,
            "malformed_or_duplicate_action": 0.0,
            "action_attempted": unsafe_action,
            "model_refusal": model_refusal,
        },
        pair_id=pair_id,
        prompt_variant=prompt_variant,
    )


class AuthorityResultAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            result_row(
                sample_id="allowed",
                expected_action="execute",
                authority_condition="current_explicit_exact_scope",
                correct_decision=1.0,
                unsafe_action=0.0,
                unnecessary_withhold=0.0,
            ),
            result_row(
                sample_id="expired",
                expected_action="withhold",
                authority_condition="expired_permission",
                correct_decision=0.0,
                unsafe_action=1.0,
                unnecessary_withhold=0.0,
            ),
        ]

    def test_aggregate_reports_overall_and_condition_metrics(self) -> None:
        summary = aggregate_rows(self.rows)
        model = summary["models"]["test/model"]

        self.assertEqual(summary["sample_runs"], 2)
        self.assertEqual(model["overall"]["correct_decision"]["mean"], 0.5)
        self.assertEqual(model["overall"]["correct_decision"]["stderr"], 0.5)
        self.assertEqual(
            model["by_authority_condition"]["expired_permission"]["metrics"][
                "unsafe_action"
            ]["mean"],
            1.0,
        )

    def test_markdown_report_contains_no_prompts_or_completions(self) -> None:
        report = render_markdown(aggregate_rows(self.rows))

        self.assertIn("test/model", report)
        self.assertIn("expired_permission", report)
        self.assertIn("Unsafe action", report)
        self.assertIn("Usable decision", report)
        self.assertIn("By expected action", report)
        self.assertIn("Model-refusal rate", report)
        self.assertNotIn("prompt", report.lower())
        self.assertNotIn("completion", report.lower())

    def test_markdown_report_can_include_aggregate_usage(self) -> None:
        summary = aggregate_rows(self.rows)
        summary["usage"] = {
            "test/model": {
                "input_tokens": 100,
                "output_tokens": 20,
                "total_tokens": 120,
                "input_tokens_cache_write": 0,
                "input_tokens_cache_read": 0,
                "reasoning_tokens": 5,
                "total_cost_usd": 0.012,
            }
        }

        report = render_markdown(summary)

        self.assertIn("Token use and calculated cost", report)
        self.assertIn("0.006000", report)

    def test_prompt_pair_is_aggregated_without_exporting_content(self) -> None:
        pair_rows = [
            result_row(
                sample_id="pressure",
                expected_action="withhold",
                authority_condition="similarity_without_authority",
                correct_decision=1.0,
                unsafe_action=0.0,
                unnecessary_withhold=0.0,
                model_refusal=1.0,
                pair_id="similarity-v7",
                prompt_variant="pressure",
            ),
            result_row(
                sample_id="neutral",
                expected_action="withhold",
                authority_condition="similarity_without_authority",
                correct_decision=1.0,
                unsafe_action=0.0,
                unnecessary_withhold=0.0,
                pair_id="similarity-v7",
                prompt_variant="neutral",
            ),
        ]

        summary = aggregate_rows(pair_rows)
        variants = summary["models"]["test/model"]["by_prompt_pair"][
            "similarity-v7"
        ]["variants"]
        self.assertEqual(variants["pressure"]["metrics"]["model_refusal"]["mean"], 1.0)
        self.assertEqual(variants["neutral"]["metrics"]["model_refusal"]["mean"], 0.0)

        report = render_markdown(summary)
        self.assertIn("Paired prompt diagnostics", report)
        self.assertIn("similarity-v7", report)
        self.assertNotIn("prompt text", report.lower())

    def test_empty_result_set_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty result set"):
            aggregate_rows([])


if __name__ == "__main__":
    unittest.main()
