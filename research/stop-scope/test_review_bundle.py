"""Negative controls for the packaging layer; not new agent experiments."""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

import review_bundle as review


class ExportTests(unittest.TestCase):
    def test_real_export_is_bound_to_frozen_sources(self):
        result = review.check_export(review.ROOT)
        self.assertEqual(result['frozen_harness_source_files_verified'], 14)
        self.assertFalse(result['raw_evidence_reaudited'])
        self.assertEqual(result['new_experiments_run'], 0)

    def test_missing_changed_extra_and_symlinked_files_fail(self):
        with tempfile.TemporaryDirectory(prefix='stop-scope-package-test-') as temporary:
            root = Path(temporary)
            path = root / 'record.json'
            path.write_bytes(b'original')
            expected = {'record.json': hashlib.sha256(b'original').hexdigest()}
            review.verify_files(root, expected, exact=True)
            path.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                review.verify_files(root, expected)
            path.unlink()
            with self.assertRaises(ValueError):
                review.verify_files(root, expected)
            target = root / 'target.json'
            target.write_bytes(b'original')
            path.symlink_to(target)
            with self.assertRaises(ValueError):
                review.verify_files(root, expected)
            path.unlink()
            path.write_bytes(b'original')
            with self.assertRaises(ValueError):
                review.verify_files(root, expected, exact=True)

    def test_traversal_and_symlinked_parent_fail(self):
        with tempfile.TemporaryDirectory(prefix='stop-scope-path-test-') as temporary:
            root = Path(temporary)
            directory = root / 'real'
            directory.mkdir()
            (directory / 'a').write_text('data')
            (root / 'alias').symlink_to(directory, target_is_directory=True)
            for path in ('../escape', '/absolute', './real/a', 'real//a', 'alias/a'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    review.safe_file(root, path)


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.rows = [({'schedule': 'held', 'arm': 'cancel'},
                      {'evidence_valid': True, 'counts': {'writes': 1},
                       'outcomes': {'R': {'status': 'fail'}}})]
        self.summary = {'all_evidence_valid': True, 'totals': {'writes': 1},
                        'groups': [{'schedule': 'held', 'arm': 'cancel', 'cells': 1,
                                    'outcomes': {'R': {'fail': 1}}}]}

    def test_valid_failed_control_is_not_corrupt_evidence(self):
        self.assertEqual(review.check_summary(self.summary, self.rows), {'writes': 1})

    def test_flipped_failure_is_rejected(self):
        self.summary['groups'][0]['outcomes']['R'] = {'pass': 1}
        with self.assertRaises(ValueError):
            review.check_summary(self.summary, self.rows)

    def test_count_change_is_rejected(self):
        self.summary['totals']['writes'] = 0
        with self.assertRaises(ValueError):
            review.check_summary(self.summary, self.rows)

    def test_missing_and_duplicate_groups_are_rejected(self):
        for groups in ([], self.summary['groups'] * 2):
            altered = deepcopy(self.summary)
            altered['groups'] = groups
            with self.subTest(groups=groups), self.assertRaises(ValueError):
                review.check_summary(altered, self.rows)

    def test_invalid_evidence_cannot_be_counted(self):
        self.rows[0][1]['evidence_valid'] = False
        with self.assertRaises(ValueError):
            review.check_summary(self.summary, self.rows)


if __name__ == '__main__':
    unittest.main(verbosity=2)
