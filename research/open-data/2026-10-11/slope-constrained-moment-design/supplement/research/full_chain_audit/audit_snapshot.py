#!/usr/bin/env python3
"""Read-only evidence closure; --freeze once to seal the audit artifacts.

This checks records, counts and provenance, not the validity of an analytic
proof or the correctness of FLINT/Arb itself. No scientific result is added.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
PACKAGES = ['cusp_verified','cusp_region','cusp_connection','cusp_geometry',
 'cusp_width','cusp_literature','cusp_robustness','cusp_pinned_family',
 'cusp_shape_design','swallowtail_window','kernel_design_principle',
 'kernel_norm_threshold']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())

def inspect():
    baseline = read(HERE/'replays/inputs.json')
    assert baseline == read(HERE/'regenerations/inputs.json')
    assert len(baseline) == 449
    for path, digest in baseline.items():
        assert sha(RESEARCH/path) == digest, ('changed frozen file',path)
    package_counts = {}
    for pkg in PACKAGES:
        m = read(RESEARCH/pkg/'manifest.json')
        for entry in m['files']:
            assert sha(RESEARCH/pkg/entry['path']) == entry['sha256'], (pkg,entry['path'])
        package_counts[pkg] = len(m['files'])
    assert sum(package_counts.values()) == 437
    originals = read(RESEARCH/'cusp_verified/manifest.json')['original_files']
    assert len(originals) == 40
    for item in originals: assert sha(Path(item['path'])) == item['sha256'], item['path']

    for phase, count in [('replays',34),('regenerations',27)]:
        status = read(HERE/phase/'status.json')
        assert status['status'] == 'passed' and status['jobs'] == status['passed'] == count
        rows = read(HERE/phase/'summary.json')
        assert len(rows) == len(set(row['id'] for row in rows)) == count
        for row in rows:
            folder = HERE/phase/row['id']
            assert row == read(folder/'run.json')
            assert row['exit_code'] == 0 and (folder/'stdout.log').exists()
            assert row['source_sha256'] == sha(RESEARCH/row['package']/row['script'])
            for changed in row['changed_clone_files']:
                assert sha(folder/'generated'/changed['path']) == changed['sha256']
    comparison = read(HERE/'regeneration_comparison.json')
    assert comparison['files_compared'] == 84
    assert comparison['interval_balls_compared'] == comparison['identical_interval_balls'] == 200951
    assert all(comparison[k] == 0 for k in ('disjoint_interval_changes',
        'changed_overlapping_intervals','nonmetadata_changes'))
    for row in comparison['files']:
        assert (RESEARCH/row['input']).exists() and (HERE/row['recreated']).exists()
    precision = read(HERE/'precision_comparison.json')
    assert precision['status'] == 'precision_rerun_identical_and_root_contained'
    assert precision['identical_interval_balls'] == 72
    assert precision['higher_precision_root_box_inside_110_digit_box']
    assert precision['source_sha256'] == sha(HERE/'check_precision_replay.py')
    symbolic = read(HERE/'symbolic_checks.json')
    assert symbolic['count'] == len(symbolic['identities']) == 32
    assert symbolic['status'] == 'all_exact_symbolic_identities_passed'
    assert symbolic['source_sha256'] == sha(HERE/'check_symbolic_identities.py')
    threshold = read(HERE/'threshold_input_audit.json')
    assert threshold['status'] == 'fresh_R12_sign_envelope_integral_and_smooth_design_audit_passed'
    assert threshold['source_sha256'] == sha(HERE/'check_threshold_inputs.py')
    for key, value in {'residual_root_boxes':28,'old_sign_leaves_rechecked':113,
        'Lipschitz_cell_envelopes':2304,'Lipschitz_tail_envelopes':9,
        'step_integrals':297,'rescaled_transition_integrals':1764}.items():
        assert threshold[key] == value
    for key in ('step_moments_contained_in_old_enclosures',
        'smooth_errors_inside_old_budgets','correction_weights_contained_in_old_enclosures',
        'original_cost_upper_bound_verified','original_order_four_and_rank_three_verified'):
        assert threshold[key] is True
    diagnostic = read(HERE/'diagnostics/threshold_input_envelope_comparison.json')
    assert diagnostic['status'] == 'resolved_audit_interval_evaluation_issue'
    assert diagnostic['existing_research_certificate_failed'] is False
    assert diagnostic['existing_research_outputs_changed'] is False
    assert diagnostic['final_source_sha256'] == threshold['source_sha256']

    rows = [line for line in (HERE/'IDDIA_ENVANTERI.md').read_text().splitlines()
            if re.match(r'^\| R\d\d\.\d\d \|',line)]
    assert len(rows) == 83 and all(len(row.split('|')) == 5 for row in rows)
    ids = [row.split('|')[1].strip() for row in rows]
    assert len(set(ids)) == 83
    counts = [6,6,6,6,6,5,6,7,9,9,7,10]
    assert ids == [f'R{i:02d}.{j:02d}' for i,n in enumerate(counts,1) for j in range(1,n+1)]
    links = 0
    for p in HERE.glob('*.md'):
        for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if dest.startswith(('http://','https://','#')): continue
            target = unquote(dest.split('#',1)[0])
            assert (p.parent/target).exists(), ('broken link',p.name,target)
            links += 1
    for p in HERE.rglob('*.py'): ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))

    return dict(status='audit_evidence_and_preservation_checks_passed',
        scope='Existing R01--R12 only; no new scientific result.',
        package_scientific_file_counts=package_counts,
        frozen_scientific_files=437,frozen_manifests=12,frozen_files_unchanged=449,
        original_archive_files_unchanged=40,existing_check_jobs=34,
        existing_production_jobs=28,existing_jobs_total=62,
        json_comparisons=85,identical_dyadic_balls=201023,
        exact_symbolic_identities=32,claim_inventory_items=83,
        R12_step_integrals=297,R12_rescaled_transition_integrals=1764,
        local_links_checked=links,retained_resolved_audit_diagnostics=1,
        invalidating_mathematical_error_identified=False,
        previous_scientific_claims_retracted=False,
        previous_numerical_bounds_changed=False,
        external_mathematical_review=False,formal_proof_assistant_verification=False,
        literature_priority_established=False,new_paper_written=False,
        trust_boundary='Internal analytic review; shared FLINT/Arb backend; '
            'rational checkers trust integral inputs. Reproduction and closure '
            'are not independent mathematical proofs.',
        audit_source_sha256=sha(Path(__file__)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--freeze',action='store_true')
    args = ap.parse_args()
    report = inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists(), 'Audit already frozen'
        report['closed_utc'] = datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(report,indent=2)+'\n')
        files = [{'path':str(p.relative_to(HERE)), 'sha256':sha(p),
                  'bytes':p.stat().st_size}
                 for p in sorted(HERE.rglob('*')) if p.is_file()]
        manifest = dict(created_utc=report['closed_utc'],
            scope='Audit records only; existing scientific packages untouched.',files=files,
            coordination_documents_at_closure={
                str(p.relative_to(RESEARCH)):sha(p) for p in
                [RESEARCH/'CALISMA_DEFTERI.md',RESEARCH/'MAKALE_KAPSAMI.md']},
            coordination_note='Historical hashes only: future dated additions to these mutable documents are allowed.')
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        recorded = read(HERE/'audit_report.json')
        for k,v in report.items(): assert recorded[k] == v, ('changed closure field',k)
        manifest = read(HERE/'manifest.json')
        for entry in manifest['files']:
            assert sha(HERE/entry['path']) == entry['sha256'], entry['path']
        assert set(e['path'] for e in manifest['files']) == {
            str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p != HERE/'manifest.json'}
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
