"""Packaging/replay negative controls, not additional experimental conditions."""
import gzip
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import verify_snapshot as verify


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = verify.read_json(verify.ROOT / 'FINDINGS.json')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='stop-scope-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'snapshot'
        shutil.copytree(verify.ROOT, self.root)

    def save(self, path, value):
        path.write_text(json.dumps(value, ensure_ascii=False) + '\n')

    def test_full_offline_replay(self):
        self.assertEqual(verify.build(self.root), self.expected)

    def test_changed_evidence_rejected(self):
        path = next((self.root / 'data/live').glob('*/result.json'))
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'Manifest digest'):
            verify.verify_manifest(self.root)

    def test_unlisted_file_rejected(self):
        (self.root / 'data/unexpected.txt').write_text('synthetic')
        with self.assertRaisesRegex(ValueError, 'Unlisted'):
            verify.verify_manifest(self.root)

    def test_path_traversal_rejected(self):
        for value in ('../outside', '/absolute', 'data/../../outside'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Unsafe path'):
                verify.relative_path(value)

    def test_symlink_rejected(self):
        path = next((self.root / 'data/live').glob('*/result.json'))
        raw = path.read_bytes()
        target = Path(self.tmp.name) / 'outside.json'
        target.write_bytes(raw)
        path.unlink()
        path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'containment'):
            verify.verify_manifest(self.root)

    def test_sensitive_values_rejected(self):
        for value in ('/Users/' + 'example/private', 'Bearer ' + 'x' * 32,
                      json.dumps({'refresh_token': 'synthetic-test-value'}), 'sk-' + 'x' * 32):
            with self.subTest(value=value[:12]), self.assertRaisesRegex(ValueError, 'Sensitive'):
                verify.privacy_check(value.encode())
        verify.privacy_check(b'/workspace/stop-scope/fixture; refresh_token is a field name')

    def test_false_confirmation_cannot_be_relabelled_supported(self):
        path = self.root / 'data/confirmation/local-matrix-v01/COMPLETION.json'
        obj = verify.read_json(path)
        case = obj['conditions']['create-17-before_I_admission-false_early_confirm']
        case['outcomes']['confirmation']['claims'][0]['issued_claim_supported'] = True
        self.save(path, obj)
        with self.assertRaisesRegex(ValueError, 'Claim support'):
            verify.native_replay(self.root, 'confirmation')

    def test_drain_omission_rejected(self):
        path = self.root / 'data/confirmation/local-matrix-v01/COMPLETION.json'
        obj = verify.read_json(path)
        obj['conditions']['create-17-before_I_admission-source_drain_snapshot']['outcomes']['confirmation']['drains'] = []
        self.save(path, obj)
        with self.assertRaisesRegex(ValueError, 'counts differ|Drain cardinality'):
            verify.native_replay(self.root, 'confirmation')

    def test_cancel_target_change_rejected(self):
        path = self.root / 'data/cancellation/local-matrix-v01/COMPLETION.json'
        obj = verify.read_json(path)
        obj['conditions']['create-17-before_I_admission-source_plus_refresh_probe']['outcomes']['cancellation']['extra_target_roles'] = ['O']
        self.save(path, obj)
        with self.assertRaisesRegex(ValueError, 'Target roles'):
            verify.native_replay(self.root, 'cancellation')

    def live(self, name='initial-stop-s17'):
        workload = verify.load_module(self.root / 'source/workload.py', 'test_workload')
        reviews = {r['episode']: r for r in verify.read_json(self.root / 'data/live/AUTHOR_REVIEWS.json')}
        return self.root / 'data/live' / name, workload, reviews

    def test_review_must_match_original_response(self):
        folder, workload, reviews = self.live()
        reviews[folder.name]['text'] = 'Altered review text'
        with self.assertRaisesRegex(ValueError, 'Author review text binding'):
            verify.live_episode(folder, workload, reviews)

    def test_stop_must_reach_model_input(self):
        folder, workload, reviews = self.live()
        path = folder / 'request-03/wire_request.json'
        obj = verify.read_json(path)
        obj['input'] = json.loads(json.dumps(obj['input']).replace('Stop task incident-s17 now.', 'Continue this task.'))
        self.save(path, obj)
        with self.assertRaisesRegex(ValueError, 'Stop absent'):
            verify.live_episode(folder, workload, reviews)

    def test_live_projection_must_match_bridge(self):
        folder, workload, reviews = self.live()
        path = folder / 'request-03/projection.json'
        obj = verify.read_json(path)
        obj['envelope']['message']['content'] = 'Altered response'
        self.save(path, obj)
        with self.assertRaisesRegex(ValueError, 'Projection/bridge'):
            verify.live_episode(folder, workload, reviews)

    def test_live_file_bytes_rechecked(self):
        folder, workload, reviews = self.live()
        path = next((folder / 'files').glob('*/*partial.json'))
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'File inventory'):
            verify.live_episode(folder, workload, reviews)

    def test_event_order_rechecked(self):
        folder, _, _ = self.live()
        path = folder / 'events.jsonl.gz'
        rows = gzip.decompress(path.read_bytes()).splitlines()
        rows[2], rows[3] = rows[3], rows[2]
        path.write_bytes(gzip.compress(b'\n'.join(rows) + b'\n', mtime=0))
        with self.assertRaisesRegex(ValueError, 'Event sequence'):
            verify.events(folder)


if __name__ == '__main__':
    unittest.main()
