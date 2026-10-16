import copy
import json
from pathlib import Path
import unittest
from verify_snapshot import coverage_check, live_headlines, package_inventory

HERE = Path(__file__).resolve().parent


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.coverage = json.loads((HERE / 'COVERAGE_MAP.json').read_text())
        self.live = json.loads((HERE / 'live-persistence/RESULTS.json').read_text())

    def test_mapping_counts(self):
        self.assertEqual(coverage_check(self.coverage)['direct_or_partial'], 68)

    def test_duplicate_identity_rejected(self):
        self.coverage['cases'][1]['case_id'] = self.coverage['cases'][0]['case_id']
        with self.assertRaises(ValueError): coverage_check(self.coverage)

    def test_case_promoted_without_acceptance_rejected(self):
        self.coverage['cases'][0]['original_registry_promotion'] = True
        with self.assertRaises(ValueError): coverage_check(self.coverage)

    def test_partial_not_added_twice(self):
        self.coverage['summary']['direct_or_partial']['cases'] = 97
        with self.assertRaises(ValueError): coverage_check(self.coverage)

    def test_live_headlines(self):
        self.assertEqual(live_headlines(self.live)['historical_requests'], 64)

    def test_control_failure_not_relabelled_success(self):
        self.live['records'][1]['old_effects_after_restart'] = 0
        with self.assertRaises(ValueError): live_headlines(self.live)

    def test_duplicate_live_arm_rejected(self):
        self.live['records'][1]['arm'] = self.live['records'][0]['arm']
        with self.assertRaises(ValueError): live_headlines(self.live)

    def test_requests_are_not_episodes(self):
        self.live['requests'] = 5
        with self.assertRaises(ValueError): live_headlines(self.live)

    def test_archive_digest_mismatch_rejected(self):
        packages = json.loads((HERE / 'PACKAGE_PROVENANCE.json').read_text())['packages']
        changed = copy.deepcopy(packages[-1:])
        name = next(iter(changed[0]['exported_hashes']))
        changed[0]['exported_hashes'][name] = '0' * 64
        with self.assertRaises(ValueError): package_inventory(HERE, changed)


if __name__ == '__main__':
    unittest.main()
