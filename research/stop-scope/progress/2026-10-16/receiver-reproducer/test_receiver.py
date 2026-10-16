from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from common import Journal
from audit import audit,inspect_data,rows

HERE=Path(__file__).resolve().parent
SMOKE=HERE/'example-evidence'/'claimed_before_effect--source_stop--none'


class JournalTests(unittest.TestCase):
    def test_missing_journal_retains_direct_disk_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp); (path/'store').mkdir()
            (path/'store'/'O-final.json').write_text('synthetic')
            r=audit(path)
            self.assertEqual(r['status'],'needs_review')
            self.assertIsNone(r['outcomes'])
            self.assertTrue(r['raw_disk_by_declared_name']['O-final.json']['present'])
            self.assertFalse(r['raw_disk_is_trusted_origin_attribution'])

    def test_subject_pid_does_not_overwrite_emitter(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp)/'events','test')
            r=j.emit('stopped',source_pid=123); j.close()
            self.assertEqual(r['source_pid'],123)
            self.assertNotEqual(r['pid'],123)

    def test_reserved_fields_fail_without_sequence_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp)/'events','test')
            with self.assertRaises(ValueError): j.emit('bad',pid=123)
            r=j.emit('good'); j.close()
            self.assertEqual(r['seq'],1)


class AuditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((SMOKE/'PLAN.json').read_text())
        cls.process=json.loads((SMOKE/'PROCESS.json').read_text())
        cls.logs={k:rows(SMOKE/(k+'.jsonl')) for k in ('coordinator','source','receiver','observer')}
        final=next(r for r in cls.logs['observer'] if r['kind']=='snapshot' and r['label']=='final')
        cls.disk={f['path']:f for f in final['files']}

    def read(self,logs=None,plan=None,disk=None):
        d=logs or self.logs
        return inspect_data(plan or self.plan,self.process,d['coordinator'],d['source'],d['receiver'],d['observer'],self.disk if disk is None else disk)

    def test_real_smoke_has_effect_after_source_ended(self):
        r=self.read()
        self.assertTrue(r['evidence_valid'])
        self.assertEqual(r['outcomes']['O_receipts_after_boundary'],1)
        self.assertTrue(r['outcomes']['source_terminal_while_receiver_O_pending'])

    def test_arm_name_does_not_determine_effect(self):
        p=deepcopy(self.plan); p['condition']['arm']='receiver_revoke'
        self.assertEqual(self.read()['outcomes'],self.read(plan=p)['outcomes'])

    def test_missing_receipt_keeps_disk_signal_not_zero(self):
        logs=deepcopy(self.logs)
        oid=next(r['op']['operation_id'] for r in logs['receiver'] if r['kind']=='job_accepted' and r['op']['role']=='O')
        logs['receiver']=[r for r in logs['receiver'] if not(r['kind']=='native_write_receipt' and r['operation_id']==oid)]
        r=self.read(logs=logs)
        self.assertFalse(r['evidence_valid'])
        self.assertTrue(r['outcomes']['final_files_observed']['O'])
        self.assertIsNone(r['outcomes']['O_receipts_after_boundary'])

    def test_duplicate_receipt_is_not_extra_valid_effect(self):
        logs=deepcopy(self.logs)
        logs['receiver'].append(deepcopy(next(r for r in logs['receiver'] if r['kind']=='native_write_receipt')))
        self.assertFalse(self.read(logs=logs)['evidence_valid'])

    def test_observer_content_corruption_is_detected(self):
        logs=deepcopy(self.logs)
        final=next(r for r in logs['observer'] if r['kind']=='snapshot' and r['label']=='final')
        final['files'][0]['content']='changed'
        self.assertFalse(self.read(logs=logs)['evidence_valid'])

    def test_real_disk_is_not_replaced_by_receiver_claim(self):
        disk=deepcopy(self.disk); del disk['O-final.json']
        self.assertFalse(self.read(disk=disk)['evidence_valid'])

    def test_foreign_receipt_identity_is_detected(self):
        logs=deepcopy(self.logs)
        rec=next(r for r in logs['receiver'] if r['kind']=='native_write_receipt')
        rec['operation_id']='unbound'
        r=self.read(logs=logs)
        self.assertFalse(r['evidence_valid'])
        self.assertTrue(r['outcomes']['final_files_observed']['O'])

    def test_rpc_reply_cannot_be_swapped(self):
        logs=deepcopy(self.logs)
        r=next(r for r in logs['source'] if r['kind']=='rpc_returned')
        r['reply']['payload_sha256']='wrong'
        self.assertFalse(self.read(logs=logs)['evidence_valid'])

    def test_absent_final_snapshot_is_unknown(self):
        logs=deepcopy(self.logs)
        logs['observer']=[r for r in logs['observer'] if not(r['kind']=='snapshot' and r['label']=='final')]
        r=self.read(logs=logs)
        self.assertFalse(r['evidence_valid'])
        self.assertIsNone(r['outcomes']['final_files_observed']['O'])


if __name__=='__main__': unittest.main()
