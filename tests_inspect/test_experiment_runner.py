from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_authority_action_experiment import REPO_ROOT
from scripts.run_authority_action_experiment import subprocess_environment


class ExperimentRunnerTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
