#!/usr/bin/env python3
"""Audit manuscript provenance and checks; not a formal mathematical proof."""
import sys
sys.dont_write_bytecode = True
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def inspect():
    if not __debug__:
        raise RuntimeError('Do not use Python -O for audit checks.')
    inputs = read(HERE/'inputs.json')
    counts = {}
    assert len(inputs['prior_manifest_sha256']) == 19
    for rel, digest in inputs['prior_manifest_sha256'].items():
        p = HERE.parent/rel
        assert sha(p) == digest, rel
        data = read(p)
        for row in data['files']:
            assert sha(p.parent/row['path']) == row['sha256'], (rel,row['path'])
        counts[p.parent.name] = len(data['files'])
    assert sum(counts.values()) == inputs['prior_frozen_entries'] == 859
    for rel,digest in inputs['source_sha256'].items():
        assert sha(HERE.parent/rel) == digest, rel
    for name,rel in inputs['figures_copied_unchanged'].items():
        assert sha(HERE/'figures'/name) == sha(HERE.parent/rel), name
    checks = {
        'asymptotic_check.json': 'kernel_slope_asymptotics/results/asymptotic_check.json',
        'remainder_check.json': 'kernel_slope_remainder/results/remainder_check.json',
        'normalization_checks.json': 'slope_equivalence_review/results/normalization_checks.json',
    }
    for name,rel in checks.items():
        assert read(HERE/'verification'/name) == read(HERE.parent/rel), name
    dc = read(HERE/'data_checks.json')
    assert dc['producer_sha256'] == sha(HERE/'prepare_inputs.py')
    assert dc['status'] == 'source_constants_and_exact_endpoint_arithmetic_passed'
    c2 = read(HERE.parent/'kernel_norm_threshold/results/threshold_check.json')
    c3 = read(HERE/'verification/asymptotic_check.json')
    c4 = read(HERE/'verification/remainder_check.json')
    dl,du = map(Q,c2['readable_minimum_norm_bracket'])
    cl,cu = map(Q,c3['coefficient_readable_bracket'])
    km,kp = Q(c4['lower_remainder_constant_readable']),Q(c4['upper_remainder_constant_readable'])
    M = Q('0.00002')
    assert dl+cl/M**2-km/M**3 == Q(dc['threshold_lower_exact'])
    assert du+cu/M**2+kp/M**3 == Q(dc['threshold_upper_exact'])
    assert kp/(cl*M) == Q(dc['relative_excess_error_upper_exact']) < Q('0.001178')
    assert Q(dc['macros']['DeltaLower'])*Q('1e-10') == dl
    assert Q(dc['macros']['DeltaUpper'])*Q('1e-10') == du
    assert Q(dc['macros']['CLower'])*Q('1e-25') == cl
    assert Q(dc['macros']['CUpper'])*Q('1e-25') == cu
    macro_text = (HERE/'certified_constants.tex').read_text()
    for k,v in dc['macros'].items():
        assert '\\newcommand{\\'+k+'}{'+v+'}' in macro_text,k
    tex = (HERE/'manuscript.tex').read_text()
    labels = re.findall(r'\\label\{([^}]+)\}',tex)
    assert len(labels) == len(set(labels))
    refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',tex)
    assert set(refs) <= set(labels)
    bib = re.findall(r'\\bibitem\{([^}]+)\}',tex)
    cites = [key for group in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}',tex) for key in group.split(',')]
    assert len(bib) == len(set(bib)) == 10
    assert set(cites) == set(bib)
    assert tex.count('\\includegraphics') == 3
    for name in ['asymptotic','remainder']:
        assert 'thm:'+name in labels
    assert 'prop:smooth' in labels
    build = read(HERE/'output/pdf/build.json')
    pdf = HERE/'output/pdf/manuscript.pdf'
    assert pdf.read_bytes().startswith(b'%PDF-')
    assert build['tex_sha256'] == sha(HERE/'manuscript.tex')
    assert build['pdf_sha256'] == sha(pdf)
    assert build['layout_or_reference_errors'] == []
    log = (HERE/'output/pdf/manuscript.log').read_text()
    for forbidden in ['Overfull \\hbox','Overfull \\vbox','Missing character:',
                      'There were undefined references','There were undefined citations',
                      'Undefined control sequence']:
        assert forbidden not in log,forbidden
    qa = read(HERE/'pdf_qa.json')
    assert qa['pdf_sha256'] == sha(pdf) and qa['page_count'] == 13
    assert len(qa['pages']) == 13 and all(row['outside_page_characters']==0 for row in qa['pages'])
    extracted = (HERE/'output/pdf/extracted_text.txt').read_text()
    for token in ['Theorem 3.1','Proposition 4.1','Theorem 5.1',
                  '0.00000000091787309568619750','0.00000000091787309964331750']:
        assert token in extracted,token
    assert 'Every rendered page\n   was inspected visually' in (HERE/'REVIEW_NOTES.md').read_text()
    for p in HERE.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    assert not list(HERE.rglob('__pycache__')) and not list(HERE.rglob('*.pyc'))
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):
                continue
            item = p.parent/target.split('#')[0]
            if item.name in ['manifest.json','audit_report.json'] and not item.exists():
                continue
            assert item.exists(),(p.name,target)
    return {
        'status':'R19_manuscript_evidence_and_preservation_checks_passed',
        'prior_manifest_count':19,'prior_frozen_file_entries':859,
        'prior_package_file_counts':counts,
        'pdf_pages':13,'scientific_figures':3,'bibliography_entries':10,
        'unique_tex_labels':len(labels),'resolved_tex_reference_uses':len(refs),
        'fresh_rational_check_outputs_identical_to_frozen':list(checks),
        'source_constant_transfer_and_exact_endpoint_arithmetic':True,
        'visual_review_recorded_for_all_pages':True,
        'pdf_sha256':sha(pdf),'manuscript_sha256':sha(HERE/'manuscript.tex'),
        'scientific_results_changed':False,'previous_frozen_packages_modified':False,
        'new_interval_producer_run':False,'external_review':False,
        'formal_proof':False,'literature_priority_established':False,
        'public_submission_or_release':False,
        'trust_boundary':'Editorial and evidence-chain audit. Analytic proofs, inherited validated enclosures and software correctness remain separate responsibilities.',
        'audit_source_sha256':sha(Path(__file__)),
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');args=ap.parse_args()
    result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists(), 'Already frozen'
        result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size}
               for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({
            'created_utc':result['closed_utc'],
            'scope':'New manuscript core from existing validated research; no scientific extension.',
            'files':files,'audit':result},indent=2)+'\n')
    else:
        old=read(HERE/'audit_report.json')
        for k,v in result.items():
            assert old[k]==v,k
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:
            assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {row['path'] for row in manifest['files']} == {
            str(p.relative_to(HERE)) for p in HERE.rglob('*')
            if p.is_file() and p != HERE/'manifest.json'}
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
