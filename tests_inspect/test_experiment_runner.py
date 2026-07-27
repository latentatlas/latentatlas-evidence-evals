from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.run_authority_action_experiment import REPO_ROOT
from scripts.run_authority_action_experiment import audit_provider_logs
from scripts.run_authority_action_experiment import build_command
from scripts.run_authority_action_experiment import subprocess_environment
from evals.experiment_control import V0_6_1_MANIFEST
from evals.experiment_control import load_manifest


class ExperimentRunnerTests(unittest.TestCase):
    def test_cost_calibrated_manifest_builds_provider_specific_caps(self) -> None:
        manifest = load_manifest(V0_6_1_MANIFEST)
        for provider, expected in (("anthropic", "0.04"), ("openai", "0.02")):
            command = build_command(
                manifest,
                provider,
                "pilot",
                Path("/tmp/latentatlas-test-log"),
                "0" * 64,
            )
            limit_index = command.index("--cost-limit")
            self.assertEqual(command[limit_index + 1], expected)

    def test_provider_audit_marks_sample_limits_needs_review(self) -> None:
        events = [
            [SimpleNamespace(event="sample_limit", type="cost")],
            [SimpleNamespace(event="sample_limit", type="token")],
            [],
        ]
        fake_log = SimpleNamespace(
            status="success",
            samples=[SimpleNamespace(events=value) for value in events],
            stats=SimpleNamespace(
                model_usage={
                    "test/model": SimpleNamespace(total_cost=0.1234567894)
                }
            ),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "run.json"
            log_path.write_text("{}\n", encoding="utf-8")
            with patch(
                "scripts.run_authority_action_experiment.read_eval_log",
                return_value=fake_log,
            ):
                audit = audit_provider_logs(Path(temp_dir))

        self.assertEqual(audit["status"], "needs_review")
        self.assertEqual(audit["sample_runs"], 3)
        self.assertEqual(audit["protocol_complete_runs"], 1)
        self.assertEqual(audit["cost_limit_exceeded"], 1)
        self.assertEqual(audit["token_limit_exceeded"], 1)
        self.assertEqual(audit["calculated_total_cost_usd"], 0.123456789)

    def test_provider_audit_rejects_incomplete_log(self) -> None:
        fake_log = SimpleNamespace(status="error", samples=None)

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "run.json"
            log_path.write_text("{}\n", encoding="utf-8")
            with patch(
                "scripts.run_authority_action_experiment.read_eval_log",
                return_value=fake_log,
            ):
                with self.assertRaisesRegex(ValueError, "incomplete"):
                    audit_provider_logs(Path(temp_dir))

    def test_subprocess_environment_preserves_existing_entries_after_repo(self) -> None:
        existing = os.pathsep.join(("/tmp/example-one", "/tmp/example-two"))

        with patch.dict(os.environ, {"PYTHONPATH": existing}, clear=False):
            environment = subprocess_environment()

        self.assertEqual(
            environment["PYTHONPATH"].split(os.pathsep),
            [str(REPO_ROOT), "/tmp/example-one", "/tmp/example-two"],
        )

    def test_inspect_cli_can_load_v0_3_task_from_runner_environment(self) -> None:
        inspect_binary = shutil.which("inspect")
        if inspect_binary is None:
            candidate = Path(os.sys.executable).with_name("inspect")
            self.assertTrue(candidate.is_file(), "Inspect CLI is unavailable")
            inspect_binary = str(candidate)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    inspect_binary,
                    "eval",
                    "evals/authority_action_eval_v0_3.py",
                    "--model",
                    "mockllm/model",
                    "-T",
                    "case_type=all",
                    "--sample-id",
                    "withhold_similarity_neutral",
                    "--epochs",
                    "1",
                    "--display",
                    "none",
                    "--log-format",
                    "json",
                    "--log-dir",
                    str(Path(temp_dir) / "logs"),
                ],
                cwd=REPO_ROOT,
                env=subprocess_environment(),
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_inspect_cli_can_load_v0_4_structured_task(self) -> None:
        inspect_binary = shutil.which("inspect")
        if inspect_binary is None:
            candidate = Path(os.sys.executable).with_name("inspect")
            self.assertTrue(candidate.is_file(), "Inspect CLI is unavailable")
            inspect_binary = str(candidate)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    inspect_binary,
                    "eval",
                    "evals/authority_action_eval_v0_4.py",
                    "--model",
                    "mockllm/model",
                    "-T",
                    "case_type=all",
                    "--sample-id",
                    "pressure_incident_publication__invalid_treatment",
                    "--epochs",
                    "1",
                    "--display",
                    "none",
                    "--log-format",
                    "json",
                    "--log-dir",
                    str(Path(temp_dir) / "logs"),
                ],
                cwd=REPO_ROOT,
                env=subprocess_environment(),
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_inspect_cli_can_load_v0_5_high_discrimination_task(self) -> None:
        inspect_binary = shutil.which("inspect")
        if inspect_binary is None:
            candidate = Path(os.sys.executable).with_name("inspect")
            self.assertTrue(candidate.is_file(), "Inspect CLI is unavailable")
            inspect_binary = str(candidate)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    inspect_binary,
                    "eval",
                    "evals/authority_action_eval_v0_5.py",
                    "--model",
                    "mockllm/model",
                    "-T",
                    "case_type=all",
                    "--sample-id",
                    "monitoring_sandbox_credential__invalid_treatment",
                    "--epochs",
                    "1",
                    "--display",
                    "none",
                    "--log-format",
                    "json",
                    "--log-dir",
                    str(Path(temp_dir) / "logs"),
                ],
                cwd=REPO_ROOT,
                env=subprocess_environment(),
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_inspect_cli_can_load_v0_6_proof_contract_task(self) -> None:
        inspect_binary = shutil.which("inspect")
        if inspect_binary is None:
            candidate = Path(os.sys.executable).with_name("inspect")
            self.assertTrue(candidate.is_file(), "Inspect CLI is unavailable")
            inspect_binary = str(candidate)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    inspect_binary,
                    "eval",
                    "evals/authority_action_eval_v0_6.py",
                    "--model",
                    "mockllm/model",
                    "-T",
                    "case_type=all",
                    "--sample-id",
                    "pressure_trial_vendor__valid_neutral",
                    "--epochs",
                    "1",
                    "--display",
                    "none",
                    "--log-format",
                    "json",
                    "--log-dir",
                    str(Path(temp_dir) / "logs"),
                ],
                cwd=REPO_ROOT,
                env=subprocess_environment(),
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
