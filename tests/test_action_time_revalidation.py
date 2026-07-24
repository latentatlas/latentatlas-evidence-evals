import copy
import json
from pathlib import Path
import unittest

from latentatlas.action_time_revalidation import revalidate_action_packet


EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "examples" / "action_packets.jsonl"


def load_examples():
    return [json.loads(line) for line in EXAMPLE_PATH.read_text(encoding="utf-8").splitlines() if line]


class ActionTimeRevalidationTests(unittest.TestCase):
    def test_valid_lease_authorizes_only_the_dry_run(self):
        decision = revalidate_action_packet(load_examples()[0])
        self.assertEqual(decision["execution_verdict"], "action_authorized")
        self.assertEqual(decision["recommended_action"], "execute_dry_run")
        self.assertFalse(decision["audit"]["external_services_used"])
        self.assertFalse(decision["audit"]["production_truth_mutation"])

    def test_permission_change_blocks_action(self):
        decision = revalidate_action_packet(load_examples()[1])
        self.assertEqual(decision["execution_verdict"], "blocked_permission_changed")
        self.assertEqual(decision["recommended_action"], "block_action")

    def test_expired_lease_requires_revalidation(self):
        decision = revalidate_action_packet(load_examples()[2])
        self.assertEqual(decision["execution_verdict"], "blocked_authority_expired")
        self.assertEqual(decision["recommended_action"], "request_revalidation")

    def test_live_execution_is_never_authorized_by_this_reference_layer(self):
        packet = copy.deepcopy(load_examples()[0])
        packet["action_request"]["dry_run"] = False
        decision = revalidate_action_packet(packet)
        self.assertEqual(decision["execution_verdict"], "blocked_non_dry_run")
        self.assertEqual(decision["recommended_action"], "block_action")


if __name__ == "__main__":
    unittest.main()
