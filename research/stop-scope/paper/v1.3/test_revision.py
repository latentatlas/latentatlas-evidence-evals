"""Publication regression checks; no model or experiment execution."""
import copy
import json
from pathlib import Path
import unittest

from verify_revision import HERE, SNAPSHOT, check_artifacts, compare_fault_table, compare_live_table


class RevisionTests(unittest.TestCase):
    def setUp(self):
        self.text = (HERE / 'MANUSCRIPT.md').read_text()
        self.live = json.loads((SNAPSHOT / 'live-persistence' / 'RESULTS.json').read_text())
        self.receiver = json.loads((SNAPSHOT / 'receiver-reproducer' / 'example-evidence' / 'RESULTS.json').read_text())

    def test_tables_match_retained_results(self):
        self.assertEqual(compare_live_table(self.text, self.live), 5)
        self.assertEqual(compare_fault_table(self.text, self.receiver), 4)

    def test_reject_changed_effect_count(self):
        with self.assertRaises(ValueError):
            compare_live_table(self.text.replace('| Source stop | 1 | 2 |', '| Source stop | 0 | 2 |'), self.live)

    def test_reject_missing_table_row(self):
        with self.assertRaises(ValueError):
            compare_live_table(self.text.replace('| Source stop | 1 | 2 | Match / match |\n', ''), self.live)

    def test_reject_legitimate_output_mismatch(self):
        data = copy.deepcopy(self.live)
        data['records'][1]['legitimate_final_files']['N'] = '0' * 64
        with self.assertRaises(ValueError):
            compare_live_table(self.text, data)

    def test_reject_promoted_missing_receipt(self):
        data = copy.deepcopy(self.receiver)
        row = next(r for r in data['records'] if r['cell'].endswith('--omit_receipt'))
        row['status'] = 'recorded'
        with self.assertRaises(ValueError):
            compare_fault_table(self.text, data)

    def test_reject_false_fault_table_interpretation(self):
        with self.assertRaises(ValueError):
            compare_fault_table(self.text.replace('Recorded collateral damage', 'Successful preservation'), self.receiver)

    def test_reject_unsafe_manifest_path(self):
        with self.assertRaises(ValueError):
            check_artifacts(HERE, {'artifact_hashes': {'../v1.2/MANUSCRIPT.md': '0' * 64}})

    def test_reject_changed_artifact_digest(self):
        with self.assertRaises(ValueError):
            check_artifacts(HERE, {'artifact_hashes': {'MANUSCRIPT.md': '0' * 64}})


if __name__ == '__main__':
    unittest.main()
