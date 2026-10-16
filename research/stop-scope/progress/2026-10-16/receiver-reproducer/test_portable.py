"""Packaging checks supplement (not replace) the preserved auditor tests."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import verify

HERE = Path(__file__).resolve().parent


class PortableTests(unittest.TestCase):
    def test_release_inventory(self):
        self.assertEqual(verify.package_check()['status'], 'passed')

    def test_saved_evidence_recomputes(self):
        r = verify.verify_run(HERE / 'example-evidence')
        self.assertEqual(r['status'], 'passed')
        self.assertEqual(r['conditions'], 16)
        self.assertEqual(r['evidence_statuses'], {'recorded': 15, 'needs_review': 1})
        self.assertEqual(r['legitimate_reference_matches'], 18)

    def test_bad_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'x'; path.write_text('synthetic')
            with self.assertRaises(ValueError):
                verify.verify_hashes(Path(d), {'x': '0' * 64})

    def test_escaping_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ('../outside', '/absolute'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    verify.safe_path(Path(d), name)

    def test_symlink_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / 'real').write_text('synthetic')
            (root / 'link').symlink_to(root / 'real')
            with self.assertRaises(ValueError):
                verify.safe_path(root, 'link')

    def test_unlisted_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'COMPLETION.json').write_text(json.dumps({'artifact_hashes': {}}))
            (root / 'extra').write_text('unlisted')
            with self.assertRaises(ValueError):
                verify.completion_check(root)

    def test_expectation_is_not_evidence_validity(self):
        rows = json.loads((HERE / 'example-evidence/RESULTS.json').read_text())['records']
        expected = json.loads((HERE / 'EXPECTED_MECHANISM_OUTCOMES.json').read_text())
        expected = deepcopy(expected)
        expected[rows[0]['cell']]['outcomes']['final_files_observed']['O'] = False
        self.assertEqual(verify.compare_expectations(rows, expected), [rows[0]['cell']])
        self.assertTrue(rows[0]['evidence_valid'])

    def test_core_mechanism_is_unchanged(self):
        provenance = json.loads((HERE / 'PROVENANCE.json').read_text())
        for name in ('common.py', 'receiver.py', 'source.py', 'observer.py', 'audit.py', 'PROTOCOL.md'):
            self.assertEqual(verify.sha(HERE / name), provenance['original_source_hashes'][name])


if __name__ == '__main__':
    unittest.main()
