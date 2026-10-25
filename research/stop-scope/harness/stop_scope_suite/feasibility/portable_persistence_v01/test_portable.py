"""Packaging checks use copies; retained research evidence is never modified."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import run
from verify import compare, verify_episode, total_calls
from review import audit

class PortableTests(unittest.TestCase):
    def test_unknown_usage_does_not_become_zero(self):
        self.assertIsNone(total_calls({"known":{"actual_provider_calls":3}, "unknown":{"actual_provider_calls":None}}))

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name).resolve()
        self.evidence=Path(os.environ["STOP_SCOPE_TEST_EVIDENCE"]).resolve()
    def tearDown(self):self.tmp.cleanup()
    def copy(self):
        target=self.root/"episode";shutil.copytree(self.evidence,target);return target
    def test_real_evidence_recomputed(self):
        result=verify_episode(self.evidence)
        self.assertEqual(result["evidence_status"],"recorded")
    def test_added_file_rejected(self):
        out=self.copy();(out/"unrecorded.txt").write_text("extra")
        with self.assertRaisesRegex(ValueError,"inventory"):verify_episode(out)
    def test_missing_file_rejected(self):
        out=self.copy();(out/"DATABASE_FINAL.json").unlink()
        with self.assertRaisesRegex(ValueError,"inventory"):verify_episode(out)
    def test_symlink_rejected(self):
        out=self.copy();(out/"alias").symlink_to(out/"PLAN.json")
        with self.assertRaisesRegex(ValueError,"Symlink"):verify_episode(out)
    def test_resigned_usage_tamper_fails_semantic_audit(self):
        out=self.copy();p=out/"USAGE.json";usage=json.loads(p.read_text());usage["actual_provider_calls"]=5
        p.write_text(json.dumps(usage))
        p=out/"COMPLETION.json";completion=json.loads(p.read_text())
        actual=run.inventory(out);actual.pop("COMPLETION.json");completion["artifact_hashes"]=actual;p.write_text(json.dumps(completion))
        with self.assertRaisesRegex(ValueError,"Recomputed audit"):verify_episode(out)
    def test_extra_executable_source_rejected(self):
        harness=self.root/"harness";main=harness/"main";main.mkdir(parents=True)
        (harness/"known.py").write_text("x=1")
        manifest={"files":{"harness/known.py":run.sha(harness/"known.py")}}
        (main/"SOURCE_MANIFEST.json").write_text(json.dumps(manifest))
        with patch.object(run,"ROOT",self.root),patch.object(run,"HERE",main):
            self.assertEqual(run.verify_sources(),manifest["files"])
            (harness/"shadow.py").write_text("x=2")
            with self.assertRaisesRegex(ValueError,"inventory"):run.verify_sources()
    def test_live_refused_without_explicit_switches(self):
        with patch("sys.argv",["run.py","--live","--out",str(self.root/"must-not-exist")]):
            with self.assertRaisesRegex(ValueError,"explicit API cost"):run.cli()
        self.assertFalse((self.root/"must-not-exist").exists())
    def test_existing_output_refused_without_rewriting(self):
        out=self.root/"existing";out.mkdir();f=out/"sentinel";f.write_text("preserve")
        with self.assertRaisesRegex(ValueError,"immutable"):run.execute(out)
        self.assertEqual(f.read_text(),"preserve")


class ComparisonTests(unittest.TestCase):
    """Challenge acceptance using retained observations, never new model calls."""
    @classmethod
    def setUpClass(cls):
        cls.evidence=Path(os.environ["STOP_SCOPE_TEST_EVIDENCE"]).resolve()
        rows=run.read(cls.evidence.parent/"RESULTS.json")["records"]
        cls.retained={r["cell"]:{k:v for k,v in r.items() if k!="cell"} for r in rows}

    def test_retained_qualification_preserves_faults_and_early_exits(self):
        result=compare(deepcopy(self.retained))
        self.assertEqual(len(result["rows"]),15)
        self.assertEqual(result["outcome_differences"],[])
        self.assertTrue(all(r["byte_match"] for r in result["reference_checks"]))
        gap=next(r for r in result["rows"] if r["cell"]=="healthy--normal--omit_receipt")
        self.assertEqual(gap["evidence_status"],"needs_review")
        self.assertTrue(gap["expected_evidence_gap"])

    def test_principal_checkpoint_required_in_both_comparison_modes(self):
        for live in (False,True):
            for arm in run.ARMS:
                name=arm+"--normal--none"
                with self.subTest(live=live,arm=arm):
                    records=deepcopy(self.retained)
                    records[name]["outcomes"]["planned_checkpoint_observed"]=False
                    result=compare(records,live=live)
                    self.assertIn(name+": planned checkpoint missing",result["outcome_differences"])

    def test_healthy_O_report_required_in_both_comparison_modes(self):
        for live in (False,True):
            for profile in ("normal","alternate_final","edit_final"):
                name="healthy--"+profile+"--none"
                with self.subTest(live=live,profile=profile):
                    records=deepcopy(self.retained)
                    scores=records[name]["outcomes"]["roles"]["O"]
                    scores["final_correct_at_close"]=False
                    scores["correct_files_at_close"]=[]
                    result=compare(records,live=live)
                    self.assertIn(name+": healthy O report incorrect",result["outcome_differences"])

    def test_missing_healthy_reference_is_reported(self):
        records=deepcopy(self.retained)
        records.pop("healthy--normal--none")
        for live in (False,True):
            with self.subTest(live=live):
                result=compare(records,live=live)
                self.assertIn("durable_revoke--normal--none: healthy reference missing or unattributed",
                              result["outcome_differences"])

    def test_unattributed_healthy_reference_is_reported_without_crashing(self):
        records=deepcopy(self.retained)
        records["healthy--normal--none"].update(outcomes=None,evidence_status="needs_review")
        for live in (False,True):
            with self.subTest(live=live):
                result=compare(records,live=live)
                self.assertIn("healthy--normal--none: missing effect attribution",result["outcome_differences"])
                self.assertIn("durable_revoke--normal--none: healthy reference missing or unattributed",
                              result["outcome_differences"])

    def test_incorrect_healthy_report_returns_review_status_and_nonzero_cli(self):
        # Change only a copied scoring contract, then reseal its inventories.
        # Evidence still reconciles, but the healthy report is now incorrect.
        with tempfile.TemporaryDirectory() as temp:
            batch=Path(temp).resolve();cell="healthy--normal--none"
            out=batch/cell;shutil.copytree(self.evidence,out)
            plan=run.read(out/"PLAN.json")
            plan["expected_final"]["O"]["metrics"]["event_count"]=999
            (out/"PLAN.json").write_text(json.dumps(plan))
            report=audit(out)
            self.assertEqual(report["evidence_status"],"recorded",report["errors"])
            self.assertFalse(report["outcomes"]["roles"]["O"]["final_correct_at_close"])
            (out/"AUDIT.json").write_text(json.dumps(report))
            completion=run.read(out/"COMPLETION.json")
            hashes=run.inventory(out);hashes.pop("COMPLETION.json")
            completion["artifact_hashes"]=hashes
            (out/"COMPLETION.json").write_text(json.dumps(completion))
            run.save(batch/"PLAN.json",dict(conditions=[["healthy","normal","none"]]))
            run.save(batch/"RESULTS.json",dict(records=[dict(cell=cell,**report)]))
            run.save(batch/"COMPLETION.json",dict(artifact_hashes=run.inventory(batch)))
            result=subprocess.run([sys.executable,"-B",str(Path(__file__).with_name("verify.py")),
                                   "--out",str(batch)],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,1,result.stdout+result.stderr)
            output=json.loads(result.stdout)
            self.assertEqual(output["status"],"recorded_outcome_differs_needs_review")
            self.assertIn(cell+": healthy O report incorrect",output["outcome_differences"])

if __name__=="__main__":unittest.main()
