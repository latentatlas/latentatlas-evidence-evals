#!/usr/bin/env python3
"""Verify released bytes and recompute recorded results locally, without APIs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def jsonl(path: Path):
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]


def verify():
    listing = json.loads((ROOT / 'SHA256SUMS.json').read_text())['files']
    for item in listing:
        path = ROOT / item['path']
        if not path.resolve().is_relative_to(ROOT):
            raise ValueError('Unsafe manifest path')
        if not path.is_file() or sha(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('Release identity mismatch: ' + item['path'])
    declared = {r['path'] for r in listing}
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if actual - declared != {'SHA256SUMS.json'}:
        raise ValueError('Unlisted or missing release files')

    boundary = ROOT / 'relevance-is-not-authority'
    lock = boundary / 'locked'
    assert sha(lock / 'LOCK_MANIFEST.json') == '06b88b5bf5008f135fe6f361a185efdd58e78f6a9f66d4d308247b86c9a14eb5'
    original = json.loads((lock / 'LOCK_MANIFEST.json').read_text())
    assert len(original['artifacts']) == 17
    for item in original['artifacts']:
        assert sha(lock / Path(item['locked_copy']).name) == item['sha256']
    case_path = boundary / 'research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl'
    cases = jsonl(case_path)
    assert len(cases) == len({c['case_id'] for c in cases}) == 1000
    decisions_path = lock / 'outputs__latentatlas__concept_boundary_real_llm_runs__real_llm_outputs_cleaned.jsonl'
    decisions = jsonl(decisions_path)
    assert len(decisions) == len({(r['model_id'], r['case_id']) for r in decisions}) == 2990
    assert len(jsonl(lock / 'outputs__latentatlas__concept_boundary_real_llm_runs__voyage_rerank_outputs.jsonl')) == 1000
    scorer = load('open_boundary_scorer', boundary / 'research/concept_boundary_engine/score_real_llm_boundary_outputs.py')
    with tempfile.TemporaryDirectory(prefix='open-research-recompute-') as scratch:
        scored = scorer.score_outputs(decisions_path, Path(scratch), case_path)
    assert scored['failure_count'] == 0
    before = sum(r['false_authority_count'] for r in scored['model_summaries'])
    assert before == 214
    probe = load('open_boundary_guard', boundary / 'research/concept_boundary_engine/concept_boundary_probe.py')
    guard = {r['case_id']: probe.classify_boundary(r) for r in cases}
    by_case = {r['case_id']: r for r in cases}
    after = sum(guard[r['case_id']]['boundary_decision'] in probe.ALLOW_DECISIONS and by_case[r['case_id']]['expected_decision'] not in probe.ALLOW_DECISIONS for r in decisions)
    valid = sum(by_case[r['case_id']]['expected_decision'] in probe.ALLOW_DECISIONS for r in decisions)
    preserved = sum(by_case[r['case_id']]['expected_decision'] in probe.ALLOW_DECISIONS and guard[r['case_id']]['boundary_decision'] == by_case[r['case_id']]['expected_decision'] for r in decisions)
    assert after == 0 and preserved == valid == 808

    aa = ROOT / 'authority-to-action/source'
    module = load('open_authority_analysis', aa / 'latentatlas/authority_action_public_analysis.py')
    aa_result = module.verify_authority_action_public_analysis(aa / 'data/authority_action_v0_8_3_analysis', repository_root=aa)
    assert aa_result['status'] == 'pass'
    source_rows = aa / 'outputs/inspect/20260727T152524Z-full-medium-authorized/analysis/analytical_rows.jsonl'
    source_audit = aa / 'outputs/inspect/20260727T152524Z-full-medium-authorized/final_audit_summary.json'
    manifest = json.loads((aa / 'data/authority_action_v0_8_3_analysis/manifest.json').read_text())
    fingerprints = manifest['private_source_fingerprints']
    assert sha(source_rows) == fingerprints['analytical_rows_sha256']
    assert sha(source_audit) == fingerprints['final_audit_summary_sha256']
    rows = jsonl(source_rows)
    assert len(rows) == 600
    logs = {}
    samples = 0
    for p in (aa / 'outputs/inspect/20260727T152524Z-full-medium-authorized').rglob('*.json'):
        obj = json.loads(p.read_text())
        if isinstance(obj, dict) and isinstance(obj.get('samples'), list):
            logs[sha(p)] = {str(r.get('uuid')) for r in obj['samples']}
            samples += len(obj['samples'])
    assert samples == 603
    assert all(r['source_log_sha256'] in logs and str(r['source_sample_uuid']) in logs[r['source_log_sha256']] for r in rows)

    leases = ROOT / 'authority-leases/outputs/latentatlas'
    frozen_path = leases / 'action_time_p0_review_freeze_v1/action_time_p0_review_freeze_rows.csv'
    frozen = list(csv.DictReader(frozen_path.open()))
    outcomes = dict(Counter(r['reviewed_outcome'] for r in frozen))
    assert len(frozen) == 146
    assert outcomes == {'correct_block': 99, 'false_block': 22, 'needs_more_evidence': 25}
    adapter = leases / 'action_time_masked_evidence_adapter_p0_full'
    cohort = list(csv.DictReader((adapter / 'action_time_masked_evidence_reviewer_sheet.csv').open()))
    high_priority = list(csv.DictReader((adapter / 'action_time_masked_evidence_reviewer_sheet_p0.csv').open()))
    cohort_ids = {r['queue_id'] for r in cohort}
    high_ids = {r['queue_id'] for r in high_priority}
    frozen_ids = {r['queue_id'] for r in frozen}
    assert len(cohort) == len(cohort_ids) == 2614
    assert len(high_priority) == len(high_ids) == 151
    assert len(frozen_ids) == 146 and frozen_ids <= high_ids <= cohort_ids
    excluded = [r for r in high_priority if r['queue_id'] not in frozen_ids]
    assert len(excluded) == 5
    assert all(r['packet_sufficiency_label'] == 'insufficient_for_outcome_adjudication' and r['outcome_adjudication_allowed'] == 'False' for r in excluded)
    closure = json.loads((leases / 'concurrency_closure_pack_20260718/concurrency_closure_summary.json').read_text())
    assert sha(frozen_path) == closure['artifact_integrity']['freeze_rows_sha256']
    assert closure['negative_fixture_count'] == 12 and closure['negative_assertion_fail_count'] == 0

    upstream = ROOT / 're-bench-systems-benchmark/upstream/RE-Bench'
    upstream_hashes = {
        'ai_rd_small_scaling_law/ai_rd_small_scaling_law.py': 'bfee000890adb8c1b9097e41aa0cde6535d8a8d21e2eb19bd9b6ea371f1b5f73',
        'ai_rd_triton_cumsum/ai_rd_triton_cumsum.py': '50ae825d7f3390eceac2dad25b4594b5c1ccd1bc493f578e33da6307412c82b5',
        'ai_rd_optimize_llm_foundry/ai_rd_optimize_llm_foundry.py': 'f87048633f30fd10b3af7243160b00e554d3e434e4d18b14bde8d91ebb8dc900',
        'ai_rd_optimize_llm_foundry/assets/score.py': '27803f2c25bdf34287f04189e0a4930b93db412eafcf1ee09129834a225ffa17',
    }
    assert all(sha(upstream / path) == expected for path, expected in upstream_hashes.items())

    math = ROOT / 'slope-constrained-moment-design/supplement'
    math_files = json.loads((math / 'SHA256SUMS.json').read_text())['files']
    assert all(sha(math / f['path']) == f['sha256'] for f in math_files)
    assert len([p for p in math.rglob('*') if p.is_file() and '__pycache__' not in p.parts]) == 1404
    return {
        'status': 'pass', 'released_files_verified': len(listing),
        'boundary': {'sealed_files': 17, 'cases': 1000, 'decisions': 2990, 'voyage_results': 1000, 'false_authority_before': before, 'false_authority_after_guard': after, 'valid_allows_preserved': preserved, 'scope': 'Recorded synthetic benchmark and attribute-based guard; not independent adjudication.'},
        'authority_to_action': {'public_analysis': aa_result, 'analytical_rows': 600, 'gross_log_samples': samples, 'all_analytical_rows_link_to_original_logs': True},
        'authority_leases': {'masked_input_cohort': len(cohort), 'high_priority_packets': len(high_priority), 'pre_review_exclusions': len(excluded), 'reviewed_rows': 146, 'outcomes': outcomes, 'synthetic_fixtures': 12},
        're_bench': {'audited_upstream_commit': '93b98062e55f6945d4a7e213a3226dd419896170', 'upstream_source_hashes_verified': len(upstream_hashes), 'historical_benchmark_rerun': False},
        'mathematics': {'release_files': 1404, 'inner_hashes_verified': len(math_files), 'mathematical_proof_verified': False},
        'external_api_calls': 0, 'new_model_experiments': 0,
        'scope': 'Artifact integrity and recorded-result recomputation; not peer review, production effectiveness or independent experiment replication.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = verify()
    if args.report:
        path = args.report.resolve()
        if path.is_relative_to(ROOT) or path.exists():
            raise ValueError('Use a new report path outside the immutable release')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
