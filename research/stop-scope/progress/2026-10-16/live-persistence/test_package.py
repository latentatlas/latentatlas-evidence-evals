"""Negative controls for the portable evidence reader; no new experiment."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import audit_native as native
import offline_codec as codec
import verify
import privacy

ROOT = Path(__file__).resolve().parent


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = ROOT/'records/healthy'
        cls.logs = {n: native.journal(cls.folder/(n+'.jsonl')) for n in
                    ('source', 'supervisor', 'receiver-1', 'receiver-2', 'observer')}
        cls.stream = native.selected(cls.logs['source'], 'bridge_wire_exchange')[0]['events']

    def test_all_archived_conditions_recompute(self):
        self.assertEqual(verify.compute(ROOT), verify.read(ROOT/'RESULTS.json'))

    def test_all_sealed_files(self):
        self.assertGreater(verify.integrity(ROOT), 300)

    def test_missing_receiver_receipt_is_not_a_zero_effect(self):
        logs = deepcopy(self.logs)
        target = next(e for e in logs['receiver-2'] if e['kind'] == 'native_effect_result')
        logs['receiver-2'].remove(target)
        self.assertEqual(native.audit(self.folder, logs)['evidence_status'], 'needs_review')

    def test_changed_authority_is_rejected(self):
        logs = deepcopy(self.logs)
        native.selected(logs['source'], 'authority_declared')[0]['origin_key'] = 'mismatched-origin'
        self.assertEqual(native.audit(self.folder, logs)['evidence_status'], 'needs_review')

    def test_changed_disk_content_is_rejected(self):
        files = native.files(self.folder/'files')
        files[next(iter(files))]['content'] += 'changed'
        with patch.object(native, 'files', return_value=files):
            self.assertEqual(native.audit(self.folder)['evidence_status'], 'needs_review')

    def test_missing_database_is_rejected(self):
        with patch.object(native, 'database', side_effect=FileNotFoundError('missing SQLite')):
            self.assertEqual(native.audit(self.folder)['evidence_status'], 'needs_review')

    def test_incomplete_stream_is_not_a_stop_success(self):
        with self.assertRaises(ValueError): codec.reconcile(self.stream[:-1])

    def test_changed_stream_arguments_are_rejected(self):
        events = deepcopy(self.stream)
        event = next(e for e in events if e['type'] == 'response.function_call_arguments.delta')
        event['delta'] += 'changed'
        with self.assertRaises(ValueError): codec.reconcile(events)

    def test_changed_native_projection_is_rejected(self):
        rows = deepcopy(self.logs['source'])
        native.selected(rows, 'bridge_wire_exchange')[0]['projection']['message']['content'] = 'changed'
        with self.assertRaises(ValueError): verify.transport(self.folder, rows)

    def test_author_review_binds_exact_text(self):
        author = verify.read(ROOT/'AUTHOR_REVIEWS.json')
        author['entries'][0]['raw_text'] += 'changed'
        arm = author['entries'][0]['arm']
        with self.assertRaises(ValueError):
            verify.summary_review(arm, native.journal(ROOT/'records'/arm/'source.jsonl'), author)

    def test_summary_delivery_must_come_from_provider_call(self):
        author = verify.read(ROOT/'AUTHOR_REVIEWS.json')
        arm = author['entries'][0]['arm']
        rows = native.journal(ROOT/'records'/arm/'source.jsonl')
        native.one(rows, 'summary_local_delivery')['call']['id'] = 'not-the-provider-call'
        with self.assertRaises(ValueError): verify.summary_review(arm, rows, author)

    def test_manifest_rejects_extra_file(self):
        with tempfile.TemporaryDirectory(prefix='stop-scope-inventory-test-') as directory:
            root = Path(directory)
            (root/'MANIFEST.json').write_text(json.dumps({'artifact_hashes': {}}))
            (root/'unlisted.txt').write_text('unexpected')
            with self.assertRaises(ValueError): verify.integrity(root)

    def test_nested_manifest_cannot_hide_an_unlisted_file(self):
        with tempfile.TemporaryDirectory(prefix='stop-scope-manifest-test-') as directory:
            root = Path(directory)
            (root/'MANIFEST.json').write_text(json.dumps({'artifact_hashes': {}}))
            (root/'nested').mkdir()
            (root/'nested/MANIFEST.json').write_text('{}')
            with self.assertRaises(ValueError): verify.integrity(root)

    def test_account_fields_and_original_replay_are_rejected(self):
        self.assertTrue(privacy.object_issues({'safety_identifier': 'private-value'}))
        self.assertTrue(privacy.object_issues({'prompt_cache_key': 'private-value'}))
        self.assertTrue(privacy.object_issues({'encrypted_content': 'original-opaque-data'}))
        self.assertFalse(privacy.object_issues({'encrypted_content': '[opaque-replay-sha256:'+'0'*64+']'}))

    def test_export_privacy_allowlist(self):
        self.assertEqual(privacy.check_tree(ROOT)['status'], 'passed_selected_patterns_and_fields')

    def test_offline_guard(self):
        for event in ('socket.connect', 'subprocess.Popen', 'os.system'):
            with self.assertRaises(RuntimeError): verify.deny_network(event, ())

    def test_readme_table_matches_saved_results(self):
        text = (ROOT/'README.md').read_text()
        for row in verify.read(ROOT/'RESULTS.json')['records']:
            self.assertIn('| '+row['arm']+' | '+str(row['old_effects_after_restart'])+' | '+
                          str(row['continuation_effects_after_restart'])+' |', text)


if __name__ == '__main__': unittest.main()
