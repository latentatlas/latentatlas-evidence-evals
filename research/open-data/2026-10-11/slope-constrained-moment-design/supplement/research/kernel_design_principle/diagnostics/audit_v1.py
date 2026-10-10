#!/usr/bin/env python3
"""R11 recorded-evidence audit. Does not replace analytic or arithmetic review."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
from xml.etree import ElementTree

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R10 = HERE.parent/'swallowtail_window'
R10_HASH = '72fbd3c96d0a6955cf8ceb5d776c70349b8267c7e8dae515057c766d5debe2e1'


def need(condition,message):
    if not condition:
        raise ArithmeticError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads((HERE/path).read_text())


def bounds(v):
    m,e=v['mid_man_exp'];r,f=v['rad_man_exp']
    need(all(isinstance(x,int) for x in (m,e,r,f)), 'Invalid interval encoding')
    mid,rad=Q(m)*Q(2)**e,Q(r)*Q(2)**f
    need(rad>=0,'Negative radius')
    return mid-rad,mid+rad


def overlaps(a,b):
    return max(a[0],b[0])<=min(a[1],b[1])


def nonzero(a):
    return a[0]>0 or a[1]<0


def sources(record,scalar_name=None):
    entries=record['source_sha256']
    if not isinstance(entries,dict):
        need(scalar_name is not None,'Missing scalar source path')
        entries={scalar_name:entries}
    for path,digest in entries.items():
        need(sha(HERE/path)==digest,'Changed source '+path)


def own_files():
    return [p for p in sorted(HERE.rglob('*')) if p.is_file()
            and p.name!='manifest.json' and '__pycache__' not in p.parts]


def audit():
    need(sha(R10/'manifest.json')==R10_HASH,'Changed R10 manifest')
    prior_manifest=json.loads((R10/'manifest.json').read_text())
    for row in prior_manifest['files']:
        need(sha(R10/row['path'])==row['sha256'],'Changed R10 file '+row['path'])
    prior_run=subprocess.run([sys.executable,str(R10/'audit_snapshot.py')],
                             check=True,capture_output=True,text=True)
    previous=json.loads(prior_run.stdout)
    need(previous['status']=='r10_evidence_links_and_preservation_checks_passed','Previous audit chain')
    packages=previous['preserved_packages']+[
        {'package':'swallowtail_window','files':len(prior_manifest['files']),'manifest_sha256':R10_HASH}]
    need(len(packages)==10 and sum(v['files'] for v in packages)==386,'Frozen package count')
    need(previous['preserved_original_files']==40,'Original file count')

    cp=HERE/'results/candidate_certificate.json'
    jp=HERE.parent/'cusp_shape_design/results/local_jets.json'
    qp=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json'
    c=read('results/candidate_certificate.json')
    jets=json.loads(jp.read_text());q=json.loads(qp.read_text())
    sources(c)
    need(c['frozen_R10_manifest_sha256']==R10_HASH,'Candidate baseline identity')
    need(c['input_sha256']=={'R01_quartic_certificate':sha(qp),'R09_local_jets':sha(jp)},'Candidate inputs')
    need(c['status']=='exact_smooth_pinned_order_four_design_and_universal_norm_bracket_passed','Candidate status')
    need(c['frequencies']==[40,41,42,43],'New candidate identity')
    need(c['center']==q['center_exact_dyadic']==jets['center'],'Exact Q center identity')
    need(c['Q_radius']==q['root_radius']==jets['root_radius'],'Exact Q enclosure identity')
    need(c['quadrature']=={'dps':110,'terms':16,'cutoff':2,'panels':8,'tolerance':'1e-93'},'Quadrature identity')
    need(len(c['dictionary'])==4,'Dictionary modes')
    for j,row in zip(c['frequencies'],c['dictionary']):
        need(row['frequency']==j and len(row['moments'])==9 and len(row['shifted_integrals'])==9,'Dictionary size')
        need(all(len(pair)==2 for pair in row['shifted_integrals']),'Shifted integral count')
    M=[[row['moments'][n] for row in c['dictionary']] for n in range(9)]
    need(c['design_matrix']==M[:4],'Design matrix identity')
    need(len(c['weights'])==4 and len(c['base_derivatives'])==9,'Jet/weight counts')
    need(c['base_derivatives'][3:]==jets['F_at_exact_Q'][3:9],'Reused derivative identity')
    need(all(bounds(v)==(0,0) for v in c['base_derivatives'][:3]),'Original exact zero identities')
    need(bounds(c['base_derivatives'][3])[0]>0,'Original derivative sign')
    need(nonzero(bounds(c['design_matrix_determinant'])),'Nonsingular moment design')
    need(len(c['modified_derivatives'])==9 and all(bounds(v)==(0,0) for v in c['modified_derivatives'][:4]),'Pinned exact identities')
    need(bounds(c['modified_derivatives'][4])[1]<0 and bounds(c['three_control_determinant'])[1]<0,'Candidate nondegeneracy')
    need(0<bounds(c['positive_moment_3_at_exact_Q'])[0],'Positive moment')
    need(0<bounds(c['feasible_coefficient_l1_cost'])[0]<=bounds(c['feasible_coefficient_l1_cost'])[1]<Q('2.381e-7'),'Candidate norm bound')
    need(bounds(c['kernel_multiplier_lower_bound'])[0]>1-Q('2.381e-7'),'Uniform positivity factor')

    rat=read('results/candidate_check.json');sources(rat,'check_candidate.py')
    need(rat['certificate_sha256']==sha(cp) and rat['R09_jets_sha256']==sha(jp),'Rational input identities')
    need(rat['status']=='independent_rational_pinned_design_rank_and_norm_bracket_passed','Rational checker status')
    for key,stored_key in [('matrix_determinant','design_matrix_determinant'),('three_control_determinant','three_control_determinant')]:
        interval=tuple(map(Q,rat[key]))
        need(nonzero(interval) and overlaps(interval,bounds(c[stored_key])),'Independent determinant consistency')
    for key in ('weights','modified_derivatives'):
        need(len(rat[key])==len(c[key]),'Independent vector length')
        need(all(overlaps(tuple(map(Q,v)),bounds(w)) for v,w in zip(rat[key],c[key])),'Independent interval consistency '+key)
    lower=tuple(map(Q,rat['universal_lower_bound_interval']))
    cost=tuple(map(Q,rat['feasible_l1_cost_interval']))
    need(Q('3.96e-10')<lower[0]<=lower[1]<cost[0]<=cost[1]<Q('2.381e-7'),'Rational norm bracket')
    lo,hi=map(Q,rat['readable_minimum_norm_bracket'])
    need(lo<=lower[0] and cost[1]<=hi,'Outward decimal endpoints')
    need(overlaps(lower,bounds(c['universal_norm_lower_bound'])) and overlaps(cost,bounds(c['feasible_coefficient_l1_cost'])),'Two arithmetic norm checks')
    need(all(tuple(map(Q,v))==(0,0) for v in rat['modified_derivatives'][:4]),'Independent exact zero identities')
    for key,index,scale in [('fourth_derivative_times_1e13',4,10**13)]:
        a,b=map(Q,rat[key]);v,w=map(Q,rat['modified_derivatives'][index])
        need(a<=v*scale<=w*scale<=b<0,'Copied derivative decimal enclosure')
    a,b=map(Q,rat['control_determinant_times_1e40']);v,w=map(Q,rat['three_control_determinant'])
    need(a<=v*10**40<=w*10**40<=b<0,'Copied determinant decimal enclosure')

    cross=read('results/integral_crosscheck.json');sources(cross)
    need(cross['certificate_sha256']==sha(cp) and cross['R01_certificate_sha256']==sha(qp),'Integral crosscheck inputs')
    need(cross['status']=='9_direct_product_integrals_and_3_two_precision_numerical_checks_passed','Integral crosscheck status')
    need([v['order'] for v in cross['rows']]==list(range(9)),'Direct integral orders')
    for row in cross['rows']:
        n=row['order']
        need(row['spectral_design_value']==c['modified_derivatives'][n],'Direct comparison identity')
        need(overlaps(bounds(row['direct_at_exact_Q']),bounds(row['spectral_design_value'])),'Direct spectral comparison')
    numerical=[v for v in cross['rows'] if 'mpmath' in v]
    need([v['order'] for v in numerical]==[0,3,4],'Numerical midpoint check identity')
    for row in numerical:
        entry=row['mpmath'];low,high=bounds(row['direct_at_center'])
        need(entry['precisions']==[90,115] and entry['inside_direct_interval'],'Separate numerical precision/containment')
        need(Q(entry['precision_difference'])<Q('1e-78') and low<=Q(entry['value'])<=high,'Recorded numerical agreement')

    plot=read('figures/metadata.json');sources(plot,'plot_results.py')
    need(plot['status']=='scientific_budget_bracket_from_certified_endpoints','Figure role')
    need(plot['input_sha256']=={'candidate_check.json':sha(HERE/'results/candidate_check.json')},'Figure input')
    need(plot['readable_minimum_norm_bracket']==rat['readable_minimum_norm_bracket'],'Figure endpoint identity')
    for name,digest in plot['files'].items():
        need(sha(HERE/'figures'/name)==digest,'Figure changed '+name)
    png=HERE/'figures/minimum_relative_change.png'
    need(plot['png_dimensions']==list(struct.unpack('>II',png.read_bytes()[16:24]))==[2140,840],'PNG dimensions')
    need(ElementTree.parse(HERE/'figures/minimum_relative_change.svg').getroot().tag.endswith('svg'),'SVG structure')
    visual=read('figures/visual_review.json')
    need(visual['status']=='visually_reviewed' and visual['external_review'] is False,'Visual inspection scope')
    need(visual['files']=={png.name:sha(png)},'Visual inspection identity')

    texts=[(HERE/name).read_text() for name in ('PROOF.md','ARASTIRMA_NOTU.md','THEOREM_APPENDIX.tex')]
    for key in ('readable_minimum_norm_bracket','fourth_derivative_times_1e13','control_determinant_times_1e40'):
        for number in rat[key]:
            need(all(number in text for text in texts),'Copied result missing or inconsistent '+number)
    links=0
    for path in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^\n]+?)\)',path.read_text()):
            if target.startswith(('http://','https://','#')):
                continue
            linked=path.parent/target.split('#',1)[0]
            need(linked.exists() or linked in (HERE/'manifest.json',HERE/'audit_report.json'),'Broken local link '+str(linked))
            links+=1
    for path in HERE.glob('*.tex'):
        depth=0
        for char in path.read_text():
            depth+=(char=='{')-(char=='}')
            need(depth>=0,'TeX brace order '+path.name)
        need(depth==0,'TeX brace balance '+path.name)
    for path in HERE.glob('*.py'):
        compile(path.read_text(),str(path),'exec')
    need(not list(HERE.rglob('__pycache__')),'Unexpected Python cache')
    runtime=read('runtime.json')
    need(runtime['assertions_enabled'] and runtime['bytecode_disabled'],'Runtime controls')

    return {
        'status':'r11_evidence_links_and_preservation_checks_passed',
        'preserved_packages':packages,'preserved_scientific_files':386,'preserved_original_files':40,
        'previous_chain_audit':'passed','new_shifted_integrals':72,'new_positive_moments':1,
        'new_direct_product_integrals':9,'total_new_rigorous_integral_evaluations':82,
        'separate_mpmath_values_two_precisions':3,'rational_checker_reports':1,
        'readable_minimum_norm_bracket':rat['readable_minimum_norm_bracket'],
        'figures_visually_reviewed':1,'local_links_checked':links,
        'latex_compiled':False,'external_mathematical_review':False,
        'literature_priority_established':False,'sharp_norm_minimum_computed':False,
        'R10_finite_window_transferred':False,
        'scope':'General sufficient moment-control assumptions; analytic L1/L-infinity minimum-norm reduction and smooth nondegenerate infimum; first certified universal bracket and a new four-cosine positive order-four design at the original exact Q.',
        'trust_boundary':'This audit checks recorded evidence and provenance. The rational checker trusts integral enclosures, exact Q and the positive moment. Direct integral crosschecks share analytic tail tools. The general proofs are self-contained drafts, not formally verified or externally reviewed.',
        'audit_source_sha256':sha(__file__),
    }


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--freeze',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    args=parser.parse_args()
    need(not(args.freeze and args.preflight),'Choose freeze or preflight')
    manifest=HERE/'manifest.json'
    if args.freeze:
        need(not manifest.exists() and not (HERE/'audit_report.json').exists(),'R11 already frozen or partially recorded')
    report=audit()
    if args.freeze:
        with (HERE/'audit_report.json').open('x') as stream:
            json.dump(report,stream,indent=2);stream.write('\n')
        record={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':report['scope'],
                'audit':report,'files':[{'path':str(p.relative_to(HERE)),'sha256':sha(p)} for p in own_files()]}
        with manifest.open('x') as stream:
            json.dump(record,stream,indent=2);stream.write('\n')
    elif not args.preflight:
        record=json.loads(manifest.read_text())
        need(record['audit']==report==read('audit_report.json'),'Audit report changed')
        expected={v['path']:v['sha256'] for v in record['files']}
        need(len(expected)==len(record['files']),'Duplicate manifest path')
        need(expected=={str(p.relative_to(HERE)):sha(p) for p in own_files()},'Changed or unrecorded R11 file')
    print(json.dumps(report,indent=2))
