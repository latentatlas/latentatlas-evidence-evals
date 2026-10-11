"""Bounded executable checks for pinned RE-Bench source-contract findings.

These checks do not run RE-Bench, execute a participant submission, reproduce
a paper result, or require benchmark hardware. They load selected hash-pinned
public task wrappers with a minimal ``metr.task_protected_scoring`` stub and
verify only the source behaviors named in the accompanying review.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import sys
import types
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest import mock


EXPECTED_SOURCE_SHA256 = {
    "ai_rd_small_scaling_law/ai_rd_small_scaling_law.py":
        "bfee000890adb8c1b9097e41aa0cde6535d8a8d21e2eb19bd9b6ea371f1b5f73",
    "ai_rd_triton_cumsum/ai_rd_triton_cumsum.py":
        "50ae825d7f3390eceac2dad25b4594b5c1ccd1bc493f578e33da6307412c82b5",
    "ai_rd_optimize_llm_foundry/ai_rd_optimize_llm_foundry.py":
        "f87048633f30fd10b3af7243160b00e554d3e434e4d18b14bde8d91ebb8dc900",
    "ai_rd_optimize_llm_foundry/assets/score.py":
        "27803f2c25bdf34287f04189e0a4930b93db412eafcf1ee09129834a225ffa17",
}


@dataclass(frozen=True)
class SourceBundle:
    root: Path

    @property
    def scaling(self) -> Path:
        return self.root / "ai_rd_small_scaling_law" / "ai_rd_small_scaling_law.py"

    @property
    def kernel_wrapper(self) -> Path:
        return self.root / "ai_rd_triton_cumsum" / "ai_rd_triton_cumsum.py"

    @property
    def foundry_wrapper(self) -> Path:
        return self.root / "ai_rd_optimize_llm_foundry" / "ai_rd_optimize_llm_foundry.py"

    @property
    def foundry_scorer(self) -> Path:
        return self.root / "ai_rd_optimize_llm_foundry" / "assets" / "score.py"


BUNDLE: SourceBundle | None = None


def _bundle() -> SourceBundle:
    if BUNDLE is None:
        raise RuntimeError("Source bundle has not been configured")
    return BUNDLE


def _load_task_module(name: str, path: Path) -> tuple[types.ModuleType, types.ModuleType]:
    """Load a task wrapper without installing or invoking METR infrastructure."""

    scoring = types.ModuleType("metr.task_protected_scoring")
    scoring.SCORING_INSTRUCTIONS = "stub scoring instructions"
    scoring.SCORING_SCRIPT_PATH = "/nonexistent/stub-score.py"
    scoring.get_timestamp = lambda: 0
    scoring.log_score = lambda *args, **kwargs: None
    scoring.IntermediateScoreResult = lambda **kwargs: kwargs
    scoring.get_best_score = lambda **kwargs: float("nan")

    metr = types.ModuleType("metr")
    metr.__path__ = []
    metr.task_protected_scoring = scoring

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module specification for {path}")
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(
        sys.modules,
        {"metr": metr, "metr.task_protected_scoring": scoring},
    ):
        spec.loader.exec_module(module)
    return module, scoring


def _duplicate_string_keys(path: Path) -> list[str]:
    """Return repeated literal-string keys found within individual dict nodes."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    duplicates: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        seen: set[str] = set()
        for key_node in node.keys:
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                continue
            key = key_node.value
            if key in seen:
                duplicates.append(key)
            seen.add(key)
    return duplicates


class PinnedSourceIntegrityTests(unittest.TestCase):
    def test_audited_source_hashes_match_the_frozen_snapshot(self) -> None:
        bundle = _bundle()
        for relative, expected in EXPECTED_SOURCE_SHA256.items():
            path = bundle.root / relative
            with self.subTest(path=path):
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(actual, expected)


class ScalingLawContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module, _ = _load_task_module("rebench_scaling_contract", _bundle().scaling)

    def test_interpolated_loss_is_independent_of_n_embd(self) -> None:
        loss_at_width_8 = self.module.ground_truth_loss_equation(
            n_embd=8,
            max_iters=88_914,
        )
        loss_at_declared_optimum_width = self.module.ground_truth_loss_equation(
            n_embd=554,
            max_iters=88_914,
        )
        self.assertEqual(loss_at_width_8, loss_at_declared_optimum_width)

    def test_low_compute_pair_can_receive_the_maximum_implemented_score(self) -> None:
        task = self.module.TaskFamily.get_tasks()["main"]
        loss_prediction = float(
            self.module.ground_truth_loss_equation(n_embd=8, max_iters=88_914)
        )
        answer = json.dumps(
            {
                "n_embd": 8,
                "max_iters": 88_914,
                "loss_prediction": loss_prediction,
            }
        )

        with mock.patch("builtins.open", mock.mock_open(read_data=answer)):
            with contextlib.redirect_stdout(io.StringIO()):
                result = self.module.TaskFamily.intermediate_score(task)

        self.assertTrue(result["message"]["is_valid"])
        self.assertAlmostEqual(result["score"], 1.0, places=12)
        self.assertLess(result["details"]["frac_flops_used"], 0.001)
        self.assertNotEqual(result["details"]["n_embd"], task["ground_truth_n_embd"])


class KernelAggregationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module, cls.scoring = _load_task_module(
            "rebench_kernel_aggregation_contract",
            _bundle().kernel_wrapper,
        )
        cls.task = cls.module.TaskFamily.get_tasks()["main"]

    def test_all_invalid_nan_aggregate_is_converted_to_zero(self) -> None:
        self.scoring.get_best_score = lambda **kwargs: float("nan")
        aggregate = self.module.TaskFamily.aggregate_scores(self.task, [])
        self.assertEqual(aggregate, 0)

    def test_valid_aggregate_is_preserved(self) -> None:
        self.scoring.get_best_score = lambda **kwargs: 1.234
        aggregate = self.module.TaskFamily.aggregate_scores(self.task, [])
        self.assertEqual(aggregate, 1.234)
        self.assertFalse(math.isnan(aggregate))


class LLMFoundryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module, _ = _load_task_module(
            "rebench_foundry_task_contract",
            _bundle().foundry_wrapper,
        )

    def test_hidden_score_key_is_duplicated_in_the_literal(self) -> None:
        self.assertIn("hidden_score", _duplicate_string_keys(_bundle().foundry_wrapper))

    def test_runtime_hidden_score_variant_is_the_second_literal_value(self) -> None:
        hidden = self.module.TaskFamily.get_tasks()["hidden_score"]
        self.assertTrue(hidden["allow_download_software"])
        self.assertFalse(hidden["strip_score_information"])

    def test_scorer_implements_per_tensor_torch_norm_but_labels_it_l1(self) -> None:
        source = _bundle().foundry_scorer.read_text(encoding="utf-8")
        self.assertIn("diff_norm += torch.norm(diff).item()", source)
        self.assertIn("L1 norm difference between model and reference", source)
        self.assertNotIn("diff_norm += torch.sum(torch.abs(diff)).item()", source)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Clean METR/RE-Bench checkout at commit 93b98062…",
    )
    args = parser.parse_args()

    if importlib.util.find_spec("numpy") is None:
        parser.error(
            "NumPy is required for the Scaling Law checks. Install the "
            "audit-only pin from docs/re-bench/requirements-audit.txt."
        )

    global BUNDLE
    BUNDLE = SourceBundle(args.source_root.resolve())

    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
