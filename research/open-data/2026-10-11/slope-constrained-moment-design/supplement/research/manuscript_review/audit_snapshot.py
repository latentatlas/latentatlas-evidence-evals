#!/usr/bin/env python3
"""R20 evidence/identity audit and exact diagnostics, not a formal proof."""
import sys
sys.dont_write_bytecode=True
import argparse
import ast
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def inspect():
    if not __debug__:raise RuntimeError('Do not run with -O.')
    base=read(HERE/'baseline.json');counts={}
    assert len(base['manifest_sha256'])==20
    for rel,digest in base['manifest_sha256'].items():
        path=RESEARCH/rel
        assert sha(path)==digest,rel
        rows=read(path)['files'];counts[path.parent.name]=len(rows)
        for row in rows:assert sha(path.parent/row['path'])==row['sha256'],(rel,row['path'])
    assert sum(counts.values())==base['frozen_entries']==884
    replay_script=RESEARCH/'slope_chain_review/replay_chain.py'
    spec=importlib.util.spec_from_file_location('r17_comparison',replay_script)
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
    total_balls=total_values=0
    for row in read(HERE/'base_comparison.json')['comparisons']:
        old=RESEARCH/row['original'];new=HERE/row['fresh']
        assert sha(old)==row['original_sha256'] and sha(new)==row['fresh_sha256']
        out={'dyadic_balls':0,'equal_other_values':0,'changed_metadata_paths':[]}
        replay.compare(read(old),read(new),'',out)
        assert all(out[k]==row[k] for k in out),row['original']
        total_balls+=out['dyadic_balls'];total_values+=out['equal_other_values']
    for row in read(HERE/'slope_replay/comparisons.json'):
        old=RESEARCH/row['original'];new=HERE/'slope_replay'/(row['job']+'.json')
        assert sha(old)==row['original_sha256'] and sha(new)==row['replay_sha256']
        out={'dyadic_balls':0,'equal_other_values':0,'changed_metadata_paths':[]}
        replay.compare(read(old),read(new),'',out)
        assert all(out[k]==row[k] for k in out),row['job']
        total_balls+=out['dyadic_balls'];total_values+=out['equal_other_values']
    assert (total_balls,total_values)==(7010,1157)
    replay_report=read(HERE/'slope_replay/report.json')
    assert replay_report['source_sha256']==sha(replay_script)
    assert replay_report['jobs']==11 and replay_report['mathematical_changes']==0
    runs=read(HERE/'slope_replay/runs.json')
    assert len(runs)==11 and all(r['exit_code']==0 for r in runs)
    for r in runs:
        if 'package' in r:
            assert sha(RESEARCH/r['package']/r['script'])==r['source_sha256']
            assert sha(HERE/'slope_replay'/r['output'])==r['output_sha256']
    c1=read(HERE/'base_cusp_numerical.json')
    assert c1['fresh_certificate_sha256']==sha(HERE/'base_cusp_fresh.json')
    assert c1['quadrature_source_sha256']==sha(RESEARCH/'cusp_verified/check_independent.py')
    assert c1['runner_source_sha256']==sha(HERE/'crosscheck_base_cusp.py')
    assert len(c1['rows'])==5 and all(Q(r['absolute_difference'])<Q('1e-96') for r in c1['rows'])
    c2=read(HERE/'base_norm_numerical.json')
    assert c2['certificate_sha256']==sha(RESEARCH/'kernel_norm_threshold/results/threshold_certificate.json')
    assert c2['source_sha256']==sha(RESEARCH/'kernel_norm_threshold/crosscheck_moments.py')
    assert len(c2['rows'])==3 and all(r['inside_certified_interval'] and Q(r['precision_difference'])<Q('1e-45') for r in c2['rows'])
    alg=read(HERE/'independent_algebra.json')
    assert alg['source_sha256']==sha(RESEARCH/'slope_chain_review/check_review_algebra.py')
    exact=read(HERE/'equation_checks.json')
    assert exact['source_sha256']==sha(HERE/'check_equations.py')
    with tempfile.TemporaryDirectory(prefix='r20-exact-audit-') as tmp:
        out=Path(tmp)/'exact.json'
        run=subprocess.run([sys.executable,'-B',str(HERE/'check_equations.py'),'--output',str(out)],capture_output=True,text=True)
        assert run.returncode==0,run.stdout+run.stderr
        assert read(out)==exact
    source=RESEARCH/'manuscript_core/manuscript.tex';original=source.read_text()
    revised=HERE/'revised/manuscript.tex';tex=revised.read_text()
    inv=read(HERE/'equation_inventory.json')
    assert inv['source_sha256']==sha(source) and inv['display_blocks']==54
    blocks=list(re.finditer(r'\\begin\{(equation|align)\}([\s\S]*?)\\end\{\1\}',original))
    assert len(blocks)==len(inv['rows'])==54
    for m,row in zip(blocks,inv['rows']):
        assert hashlib.sha256(m[0].encode()).hexdigest()==row['block_sha256']
        assert original[:m.start()].count('\n')+1==row['source_line'] and row['reason']
    for environment in ['theorem','proposition']:
        pattern=r'\\begin\{'+environment+r'\}[\s\S]*?\\end\{'+environment+r'\}'
        assert re.findall(pattern,original)==re.findall(pattern,tex),environment
    assert sha(HERE/'revised/certified_constants.tex')==sha(RESEARCH/'manuscript_core/certified_constants.tex')
    for p in (HERE/'revised/figures').iterdir():
        assert sha(p)==sha(RESEARCH/'manuscript_core/figures'/p.name)
    revision=read(HERE/'revised/revision.json')
    assert revision['script_sha256']==sha(HERE/'revise_manuscript.py')
    assert revision['source_tex_sha256']==sha(source) and revision['revised_tex_sha256']==sha(revised)
    labels=re.findall(r'\\label\{([^}]+)\}',tex)
    refs=re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',tex)
    bib=re.findall(r'\\bibitem\{([^}]+)\}',tex)
    cites=[key for group in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}',tex) for key in group.split(',')]
    assert len(labels)==len(set(labels)) and set(refs)<=set(labels)
    assert len(bib)==len(set(bib))==12 and set(cites)==set(bib)
    assert tex.count('\\includegraphics')==3
    # Recombine all printed threshold/error constants using exact fractions.
    c2c=read(RESEARCH/'kernel_norm_threshold/results/threshold_check.json')
    c3c=read(HERE/'slope_replay/R15_rational.json');c4c=read(HERE/'slope_replay/R16_rational.json')
    dl,du=map(Q,c2c['readable_minimum_norm_bracket']);cl,cu=map(Q,c3c['coefficient_readable_bracket'])
    km=Q(c4c['lower_remainder_constant_readable']);kp=Q(c4c['upper_remainder_constant_readable']);M=Q('0.00002')
    assert dl+cl/M**2-km/M**3==Q('0.00000000091787309568619750')
    assert du+cu/M**2+kp/M**3==Q('0.00000000091787309964331750')
    assert kp/(cl*M)<Q('0.001178')
    pdf=HERE/'revised/output/pdf/manuscript.pdf';build=read(pdf.parent/'build.json');qa=read(HERE/'pdf_qa.json')
    assert pdf.read_bytes().startswith(b'%PDF-')
    assert build['pdf_sha256']==qa['pdf_sha256']==sha(pdf) and build['tex_sha256']==sha(revised)
    assert build['layout_or_reference_errors']==[] and qa['page_count']==14
    assert len(qa['pages'])==14 and all(r['outside_page_characters']==0 for r in qa['pages'])
    assert qa['visual_review_record'].startswith('All 14 rendered pages inspected')
    extracted=(pdf.parent/'extracted_text.txt').read_text()
    for token in ['Theorem 3.1','Proposition 4.1','Theorem 5.1','0.00000000091787309568619750','0.00000000091787309964331750']:
        assert token in extracted,token
    log=(pdf.parent/'manuscript.log').read_text()
    for token in ['Overfull \\hbox','Overfull \\vbox','Missing character:','Undefined control sequence','There were undefined references','There were undefined citations']:
        assert token not in log,token
    sources=read(HERE/'sources.json')
    assert sources['primary_sources']==3 and len(sources['sources'])==3
    assert sum(len(r['versions']) for r in sources['sources'])==5
    assert len(re.findall(r'^\d+\. `',(HERE/'SEARCH_LOG.md').read_text(),re.M))==29
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            item=p.parent/target.split('#')[0]
            if item.name in ['manifest.json','audit_report.json'] and not item.exists():continue
            assert item.exists(),(p.name,target)
    return {'status':'R20_manuscript_review_evidence_and_preservation_passed',
            'prior_manifest_count':20,'prior_frozen_file_entries':884,
            'matching_ball_occurrences':7010,'matching_other_mathematical_values':1157,
            'source_display_blocks_reviewed':54,'additional_exact_check_groups':7,
            'independent_base_cusp_derivatives':5,'independent_norm_moments':3,
            'new_primary_works_reviewed':3,'new_search_queries':29,
            'main_theorem_statements_and_certified_constants_unchanged':True,
            'pdf_pages':14,'scientific_figures':3,'bibliography_entries':12,
            'tex_labels':len(labels),'tex_reference_uses':len(refs),
            'pdf_sha256':sha(pdf),'tex_sha256':sha(revised),
            'previous_frozen_packages_modified':False,'external_referee_review':False,
            'formal_proof':False,'novelty_priority_established':False,
            'new_theta_optimum_certificate':False,'public_release_or_submission':False,
            'audit_source_sha256':sha(Path(__file__)),
            'trust_boundary':'Identity, replay, exact algebra and recorded analytic/visual review. No automated decision on mathematical truth or novelty.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--preflight',action='store_true');args=ap.parse_args()
    result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],'scope':'R19 audit/exposition revision; literature review and separate finite-slope research pilot.','files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for k,v in result.items():assert recorded[k]==v,k
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {r['path'] for r in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
