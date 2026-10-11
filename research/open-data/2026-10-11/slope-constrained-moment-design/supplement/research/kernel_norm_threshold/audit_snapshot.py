#!/usr/bin/env python3
"""R12 evidence/provenance closure, distinct from the mathematical checks."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
from xml.etree import ElementTree

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R11=HERE.parent/'kernel_design_principle'
R11_HASH='c48a51b15d4eb109a7f788eab7aa3e47edb78ef21ac935c34e624782431bedca'


def need(v,message):
    if not v:raise ArithmeticError(message)


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):return json.loads((HERE/p).read_text())


def bounds(v):
    m,e=v['mid_man_exp'];r,f=v['rad_man_exp']
    need(all(isinstance(x,int) for x in (m,e,r,f)) and r>=0,'Invalid dyadic ball')
    mid,rad=Q(m)*Q(2)**e,Q(r)*Q(2)**f
    return mid-rad,mid+rad


def point(v):
    low,high=bounds(v);need(low==high,'Expected exact dyadic point');return low


def overlaps(a,b):return max(a[0],b[0])<=min(a[1],b[1])


def sources(data,name=None):
    items=data['source_sha256']
    if not isinstance(items,dict):
        need(name is not None,'Missing scalar source path');items={name:items}
    for path,digest in items.items():need(sha(HERE/path)==digest,'Changed source '+path)


def own_files():
    return [p for p in sorted(HERE.rglob('*')) if p.is_file()
            and p.name!='manifest.json' and '__pycache__' not in p.parts]


def audit():
    need(sha(R11/'manifest.json')==R11_HASH,'Changed R11 manifest')
    manifest=json.loads((R11/'manifest.json').read_text())
    for row in manifest['files']:
        need(sha(R11/row['path'])==row['sha256'],'Changed R11 input '+row['path'])
    prior=subprocess.run([sys.executable,str(R11/'audit_snapshot.py')],capture_output=True,text=True,check=True)
    previous=json.loads(prior.stdout)
    need(previous['status']=='r11_evidence_links_and_preservation_checks_passed','Previous audit chain')
    packages=previous['preserved_packages']+[{'package':'kernel_design_principle','files':len(manifest['files']),'manifest_sha256':R11_HASH}]
    need(len(packages)==11 and sum(v['files'] for v in packages)==409,'Prior scientific file count')
    need(previous['preserved_original_files']==40,'Original file count')
    qp=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json'
    jp=HERE.parent/'cusp_shape_design/results/local_jets.json'
    op=R11/'results/candidate_certificate.json'
    pp=HERE/'diagnostics/l1_probe.json'
    cp=HERE/'results/threshold_certificate.json';rp=HERE/'results/threshold_check.json'
    c=read('results/threshold_certificate.json');rat=read('results/threshold_check.json')
    q=json.loads(qp.read_text());old=json.loads(op.read_text())
    probe=read('diagnostics/l1_probe.json');sources(probe,'probe_l1.py')
    need(probe['status']=='floating_point_exploration_only' and probe['Q_certificate_sha256']==sha(qp),'Probe scope/input')
    sources(c)
    need(c['status']=='certified_dual_bound_and_smooth_near_minimum_pinned_design','Generator status')
    need(c['frozen_R11_manifest_sha256']==R11_HASH,'Generator baseline identity')
    need(c['input_sha256']=={'probe':sha(pp),'R01_Q':sha(qp),'R09_jets':sha(jp),'R11_candidate':sha(op)},'Generator input identities')
    need(list(map(point,c['center']))==list(map(point,q['center_exact_dyadic'])),'Exact Q center')
    need(bounds(c['Q_radius'])==bounds(q['root_radius']),'Exact Q radius')
    need(list(map(point,c['a']))==[Q.from_float(v) for v in probe['a']],'Fixed rational residual coefficients')
    need(point(c['alpha'])==Q.from_float(probe['norm_estimate']),'Fixed rational design amplitude')
    breaks=list(map(point,c['breakpoints']))
    need(breaks==[Q.from_float(v) for v in probe['roots_0_2'] if 0<v<1],'Fixed rational knots')
    need(len(breaks)==28 and c['initial_sign']==1,'Sign template identity')
    need(point(c['smoothing_width'])==Q(2)**-32 and point(c['zero_box_radius'])==Q(2)**-36,'Smoothing/root scales')
    need(point(c['cutoff'])==1 and c['kernel_terms']==8,'Quadrature truncation identity')
    need(c['quadrature']=={'dps':110,'abs_tol':'1e-60','rel_tol':'1e-60','pieces':29},'Quadrature precision identity')
    need(len(c['root_boxes'])==28 and len(c['sign_cover'])==113,'Sign proof counts')
    need(len(c['segments'])==29 and all(len(v['finite_integrals'])==9 for v in c['segments']),'261 integral records')
    need(len(c['derivative_majorants']['cells'])==256 and len(c['lipschitz_bounds'])==9,'Derivative envelopes')
    need(bounds(c['derivative_majorants']['tail_decrease_margin'])[0]>0,'Global tail monotonicity')
    need(all(point(v)>0 for v in c['lipschitz_bounds']),'Positive Lipschitz bounds')
    for M,E in zip(c['lipschitz_bounds'],c['smooth_moment_errors']):
        need(28*point(M)*Q(2)**-64<=point(E),'Analytic smoothing error arithmetic')
    need(c['correction_frequencies']==old['frequencies']==[40,41,42,43],'Correction subspace identity')
    need(all(bounds(v)==(0,0) for v in c['modified_derivatives'][:4]),'Exact pinned identities')
    need(bounds(c['modified_derivatives'][4])[1]<0 and bounds(c['three_control_determinant'])[1]<0,'Generator nondegeneracy')
    need(point(c['feasible_norm_upper_enclosure'])>=bounds(c['coefficient_cost_enclosure'])[1],'Correct outward norm budget')

    sources(rat)
    need(rat['status']=='rational_dual_primal_near_minimum_certificate_passed','Rational checker status')
    need(rat['certificate_sha256']==sha(cp) and rat['R11_candidate_sha256']==sha(op) and rat['R09_jets_sha256']==sha(jp),'Rational input identities')
    need(rat['sign_partition_pieces']==141 and rat['root_boxes']==28 and rat['sign_leaves']==113,'Rational sign cover counts')
    need(all(overlaps(bounds(v),tuple(map(Q,w))) for v,w in zip(c['step_moments_at_exact_Q'],rat['reconstructed_step_moments'])),'Independent step moment consistency')
    need(all(overlaps(bounds(v),tuple(map(Q,w))) for v,w in zip(c['correction_weights'],rat['correction_weights'])),'Independent correction consistency')
    need(all(overlaps(bounds(v),tuple(map(Q,w))) for v,w in zip(c['modified_derivatives'],rat['modified_derivatives'])),'Independent jet consistency')
    lo,hi=map(Q,rat['common_minimum_norm_bracket']);L,U=map(Q,rat['readable_minimum_norm_bracket'])
    need(0<L<lo<hi<U<1,'Strict common outward bracket and positivity')
    need(lo<=bounds(c['minimum_norm_lower_bound'])[0] and hi>=point(c['feasible_norm_upper_enclosure']),'Common bracket covers generator')
    need(lo<=Q(rat['independent_norm_lower_bound'][0]) and hi>=Q(rat['independent_feasible_norm_upper']),'Common bracket covers rational checker')
    need(Q(rat['relative_gap_upper'])==hi/lo-1 and U/L-1<Q('5e-11'),'Relative near-minimum gap')
    need(rat['relative_gap_readable_upper']=='0.00000000005','Copied gap statement')
    need(all(tuple(map(Q,v))==(0,0) for v in rat['modified_derivatives'][:4]),'Independent exact identities')
    need(Q(rat['modified_derivatives'][4][1])<0 and Q(rat['control_determinant'][1])<0,'Independent nondegeneracy')
    dL,dU=map(Q,rat['fourth_derivative_times_1e13']);dl,du=map(Q,rat['modified_derivatives'][4])
    need(dL<=dl*10**13<=du*10**13<=dU<0,'Readable fourth derivative enclosure')
    dL,dU=map(Q,rat['control_determinant_times_1e40']);dl,du=map(Q,rat['control_determinant'])
    need(dL<=dl*10**40<=du*10**40<=dU<0,'Readable control determinant enclosure')

    cross=read('results/moment_crosscheck.json');sources(cross,'crosscheck_moments.py')
    need(cross['certificate_sha256']==sha(cp),'Numerical crosscheck input')
    need(cross['status']=='three_step_moments_two_precision_independent_quadrature_passed','Numerical crosscheck status')
    need([v['order'] for v in cross['rows']]==[0,3,4],'Separate check orders')
    for row in cross['rows']:
        low,high=bounds(c['step_moments_at_exact_Q'][row['order']])
        need(row['precisions']==[50,80] and row['inside_certified_interval'],'Separate precision identity')
        need(Q(row['precision_difference'])<Q('1e-45') and low<=Q(row['value'])<=high,'Separate numerical agreement')

    guard=read('diagnostics/interval_cost_guard.json');decode=read('diagnostics/rational_point_decode.json')
    need(guard['status']=='failed_before_certificate_interval_comparison_too_strong','Cost guard history')
    need(guard['prior_source_sha256']==sha(HERE/'diagnostics/certify_threshold_v1.py'),'Cost guard source identity')
    need(overlaps(bounds(guard['lower']),bounds(guard['raw_cost_ball'])),'Recorded cost-ball comparison issue')
    need(point(guard['usable_cost_upper_endpoint'])>bounds(guard['lower'])[1],'Recorded usable upper budget')
    need(decode['status']=='rational_checker_exact_dyadic_decode_corrected','Exact-point decoder history')
    need(decode['prior_source_sha256']==sha(HERE/'diagnostics/check_threshold_v1.py'),'Exact-point decoder source identity')

    plot=read('figures/metadata.json');sources(plot,'plot_results.py')
    need(plot['status']=='scientific_figures_from_certified_bracket_and_exact_design_formula','Figure role')
    need(plot['input_sha256']=={'threshold_certificate.json':sha(cp),'threshold_check.json':sha(rp),'R11_candidate_check.json':sha(R11/'results/candidate_check.json')},'Plot source identities')
    need(plot['readable_bracket']==rat['readable_minimum_norm_bracket'],'Plot bracket identity')
    visual=read('figures/visual_review.json')
    need(visual['status']=='visually_reviewed' and visual['external_review'] is False,'Visual review role')
    dims={'threshold_contraction':[2100,1220],'smooth_near_minimum_design':[2100,760]}
    need(plot['png_dimensions']==dims,'Plot dimensions recorded')
    for name,digest in plot['files'].items():need(sha(HERE/'figures'/name)==digest,'Changed plot '+name)
    for name,size in dims.items():
        png=HERE/'figures'/(name+'.png')
        need(list(struct.unpack('>II',png.read_bytes()[16:24]))==size,'PNG size')
        need(ElementTree.parse(HERE/'figures'/(name+'.svg')).getroot().tag.endswith('svg'),'SVG format')
        need(visual['files'][png.name]==sha(png),'Visual inspection hash')

    texts=[(HERE/name).read_text() for name in ('PROOF.md','ARASTIRMA_NOTU.md','THEOREM_APPENDIX.tex')]
    for key in ('readable_minimum_norm_bracket','fourth_derivative_times_1e13','control_determinant_times_1e40'):
        for number in rat[key]:need(all(number in text for text in texts),'Copied numerical result '+number)
    links=0
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^\n]+?)\)',p.read_text()):
            if target.startswith(('https://','http://','#')):continue
            linked=p.parent/target.split('#',1)[0]
            need(linked.exists() or linked in (HERE/'manifest.json',HERE/'audit_report.json'),'Broken link '+str(linked));links+=1
    for p in HERE.rglob('*.py'):compile(p.read_text(),str(p),'exec')
    for p in HERE.glob('*.tex'):
        depth=0
        for ch in p.read_text():
            depth+=(ch=='{')-(ch=='}');need(depth>=0,'TeX brace order '+p.name)
        need(depth==0,'TeX brace balance '+p.name)
    need(not list(HERE.rglob('__pycache__')),'Unexpected Python cache')
    runtime=read('runtime.json')
    need(runtime['assertions_enabled'] and runtime['bytecode_disabled'],'Runtime controls')

    return {'status':'r12_evidence_links_and_preservation_checks_passed',
            'preserved_packages':packages,'preserved_scientific_files':409,'preserved_original_files':40,
            'previous_chain_audit':'passed','new_arb_segment_integrals':261,'residual_root_boxes':28,
            'sign_leaves':113,'complete_sign_partition_pieces':141,'positive_derivative_envelope_cells':256,
            'rational_checker_reports':1,'separate_numerical_moments_two_precisions':3,
            'readable_minimum_norm_bracket':rat['readable_minimum_norm_bracket'],
            'relative_gap_upper_bound':'5e-11','figures_visually_reviewed':2,'local_links_checked':links,
            'retained_implementation_diagnostics':2,'latex_compiled':False,'external_mathematical_review':False,
            'literature_priority_established':False,'exact_optimal_coefficients_certified':False,
            'R10_finite_window_transferred':False,'frequency_or_derivative_budget_imposed':False,
            'smooth_nonattainment_status':'Analytic consequence of R11 dual equality and full positive support; not an arithmetic-only finding.',
            'scope':'Universal lower bound and explicit real-analytic positive nondegenerate upper design at the original exact Q, within relative 5e-11 of the minimum L-infinity amplitude; no frequency/derivative budget.',
            'trust_boundary':'Provenance closure checks recorded artifacts and their source identities. Rational arithmetic trusts segment integral enclosures, trigonometric bounds, positive envelopes and analytic tails. Smooth-transition errors are bounded analytically; no claim of a separate direct integration of those transitions or external review.',
            'audit_source_sha256':sha(__file__)}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--preflight',action='store_true');ap.add_argument('--freeze',action='store_true');args=ap.parse_args()
    need(not(args.preflight and args.freeze),'Choose preflight or freeze')
    mp=HERE/'manifest.json'
    if args.freeze:need(not mp.exists() and not(HERE/'audit_report.json').exists(),'Already frozen or partly recorded')
    report=audit()
    if args.freeze:
        with (HERE/'audit_report.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
        record={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':report['scope'],'audit':report,
                'files':[{'path':str(p.relative_to(HERE)),'sha256':sha(p)} for p in own_files()]}
        with mp.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    elif not args.preflight:
        record=json.loads(mp.read_text());need(record['audit']==report==read('audit_report.json'),'Audit record changed')
        expected={v['path']:v['sha256'] for v in record['files']}
        need(len(expected)==len(record['files']),'Duplicate manifest path')
        need(expected=={str(p.relative_to(HERE)):sha(p) for p in own_files()},'Changed or unrecorded R12 files')
    print(json.dumps(report,indent=2))
