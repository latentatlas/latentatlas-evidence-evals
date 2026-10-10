#!/usr/bin/env python3
"""Rational reconstruction of the dual/primal certificate; no FLINT import."""
import argparse
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R11=HERE.parent/'kernel_design_principle'
spec=importlib.util.spec_from_file_location('r11_rational',R11/'check_candidate.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
I,restore,determinant,sha,decimal,need=prior.I,prior.restore,prior.determinant,prior.sha,prior.decimal,prior.need


def point(v):
    m,e=v['mid_man_exp'];r,_=v['rad_man_exp']
    need(r==0,'Expected exact dyadic')
    return Q(m)*Q(2)**e


def overlaps(a,b):
    return max(a.lo,b.lo)<=min(a.hi,b.hi)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    need(not args.output.exists(),'Refuse to replace a recorded check')
    cp=HERE/'results/threshold_certificate.json';c=json.loads(cp.read_text())
    op=R11/'results/candidate_certificate.json';old=json.loads(op.read_text())
    jp=HERE.parent/'cusp_shape_design/results/local_jets.json';jets=json.loads(jp.read_text())
    need(c['input_sha256']['R11_candidate']==sha(op) and c['input_sha256']['R09_jets']==sha(jp),'Changed arithmetic input')
    f=list(map(restore,jets['F_at_exact_Q'][:9]));f[:3]=[I(0)]*3
    need(f[3].lo>0,'Base cusp derivative')
    a=list(map(restore,c['a']));alpha=restore(c['alpha']);eta=point(c['smoothing_width'])
    beta=point(c['zero_box_radius']);breaks=list(map(point,c['breakpoints']));N=len(breaks)
    need(N==28 and eta==Q(2)**-32 and beta==Q(2)**-36,'Template identity')
    need(c['initial_sign']==1 and point(c['cutoff'])==1,'Sign and integration domain')

    pieces=[];wrong=I(0)
    for j,(b,row) in enumerate(zip(breaks,c['root_boxes'])):
        left,right=point(row['left']),point(row['right']);s=(-1)**j
        need(point(row['center'])==b and left==b-beta and right==b+beta and row['sign_before']==s,'Root box identity')
        ends=list(map(restore,row['endpoints']));dr=restore(row['derivative'])
        need((s*ends[0]).lo>0 and (s*ends[1]).hi<0 and dr.nonzero(),'Unique root crossing inequalities')
        rho=restore(row['rho_upper']);rp=restore(row['residual_abs_upper'])
        need(rho.lo>0 and rp.lo>0,'Positive root error inputs')
        error=4*beta*point(row['rho_upper'])*point(row['residual_abs_upper'])
        need(error<=point(row['objective_error_upper']),'Wrong-sign bound rounded outwards')
        wrong=wrong+I(error)
        pieces.append((left,right,'root',s))
    for row in c['sign_cover']:
        left,right=point(row['left']),point(row['right']);s=row['sign']
        need(s in (-1,1) and left<right,'Sign leaf identity')
        if row['method']=='range':
            need((s*restore(row['residual'])).lo>0,'Range sign inequality')
        elif row['method']=='monotone':
            need(restore(row['derivative']).nonzero(),'Monotonicity inequality')
            need(all((s*restore(v)).lo>0 for v in row['endpoints']),'Monotone endpoint sign')
        else:raise ArithmeticError('Unknown sign proof')
        pieces.append((left,right,'sign',s))
    pieces.sort();cursor=Q(0);sign=1
    for left,right,kind,s in pieces:
        need(left==cursor and s==sign,'Incomplete or inconsistent sign partition')
        cursor=right
        if kind=='root':sign=-sign
    need(cursor==1,'Sign proof does not cover [0,1]')
    need(wrong.hi<=point(c['wrong_sign_error']),'Wrong-sign sum upper bound')

    lip=list(map(restore,c['lipschitz_bounds']));majorants=c['derivative_majorants']
    need(len(lip)==9 and len(majorants['cells'])==256,'Lipschitz majorant count')
    cursor=Q(0)
    for row in majorants['cells']:
        need(point(row['left'])==cursor and point(row['right'])-cursor==Q(1,128),'Lipschitz cell partition')
        cursor=point(row['right'])
        need(all(0<point(v)<=lip[n].lo for n,v in enumerate(row['bounds'])),'Cell derivative envelope dominated')
    need(cursor==2 and restore(majorants['tail_decrease_margin']).lo>0,'Lipschitz tail domain')
    need(all(restore(v).hi<=lip[n].lo for n,v in enumerate(majorants['tail_bounds'])),'Tail derivative envelope dominated')
    smooth_error=[N*v*eta*eta for v in lip]
    need(all(v.hi<=point(c['smooth_moment_errors'][n]) for n,v in enumerate(smooth_error)),'Smoothing errors rounded outward')

    S=[I(0)]*9;ends=[Q(0)]+breaks+[Q(1)]
    need(len(c['segments'])==29,'Quadrature segment count')
    for j,row in enumerate(c['segments']):
        need(point(row['left'])==ends[j] and point(row['right'])==ends[j+1] and row['sign']==(-1)**j,'Quadrature interval identity')
        values=list(map(restore,row['finite_integrals']));need(len(values)==9,'Quadrature orders')
        S=[S[n]+row['sign']*values[n] for n in range(9)]
    for n in range(9):
        er=c['step_moment_errors'][n];radius=restore(er['truncation']).hi+restore(er['Q_displacement']).hi
        need(radius>=0,'Negative step moment error')
        S[n]=S[n]+I(-radius,radius)
        need(overlaps(S[n],restore(c['step_moments_at_exact_Q'][n])),'Signed integral aggregation mismatch')
    Z=S[3]-sum((a[i]*S[i] for i in range(3)),I(0))
    tail=restore(c['wrong_sign_tail_error']);need(tail.lo>=0,'Negative tail error')
    Dcap=Z.hi+wrong.hi+tail.hi
    need(Dcap>0,'Dual objective bound sign')
    lower=f[3]/I(Dcap)
    # Exact point coefficients of the adjugate are computed before multiplying
    # the uncertain right-hand side. This avoids spurious dependency inflation.
    A=[[restore(v) for v in row] for row in old['design_matrix']]
    det=determinant(A);need(det.nonzero(),'Correction matrix determinant')
    adj=[]
    for j in range(4):
        row=[]
        for i in range(4):
            minor=[[A[r][s] for s in range(4) if s!=j] for r in range(4) if r!=i]
            row.append(((-1)**(i+j))*determinant(minor)/det)
        adj.append(row)
    smooth=[S[n]+I(-smooth_error[n].hi,smooth_error[n].hi) for n in range(9)]
    target=[I(0),I(0),I(0),-f[3]];rhs=[target[n]+alpha*smooth[n] for n in range(4)]
    w=[sum((adj[j][i]*rhs[i] for i in range(4)),I(0)) for j in range(4)]
    need(all(overlaps(v,restore(s)) for v,s in zip(w,c['correction_weights'])),'Independent correction weights')
    dictionary=[[restore(row['moments'][n]) for row in old['dictionary']] for n in range(9)]
    g=[f[n]-alpha*smooth[n]+sum((dictionary[n][j]*w[j] for j in range(4)),I(0)) for n in range(9)]
    need(all(v.lo<=0<=v.hi for v in g[:4]),'Exact moment system inconsistent')
    g[:4]=[I(0)]*4
    need(g[4].hi<0,'Order exactly four')
    J=[[-g[n+2]/4,g[n+4]/16,-g[n+6]/64] for n in range(3)]
    rank=determinant(J);reduced=g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    need(rank.hi<0 and reduced.hi<0 and overlaps(rank,reduced),'Rank-three unfolding')
    own_cost=alpha.hi+sum(v.absolute().hi for v in w)
    # Publish a common outer bracket valid for both arithmetic reconstructions.
    low=min(lower.lo,restore(c['minimum_norm_lower_bound']).lo)
    high=max(own_cost,point(c['feasible_norm_upper_enclosure']))
    need(0<low<high<1,'Common positive norm bracket')
    gap=high/low-1
    need(gap<Q('5e-11'),'Targeted near-optimal relative gap not achieved')
    readable=[decimal(low,23),decimal(high,23,True)]
    need(Q(readable[1])/Q(readable[0])-1<Q('5e-11'),'Readable rounding loses target')
    out={'status':'rational_dual_primal_near_minimum_certificate_passed',
         'source_sha256':{'check_threshold.py':sha(__file__),'../kernel_design_principle/check_candidate.py':sha(R11/'check_candidate.py')},
         'certificate_sha256':sha(cp),'R11_candidate_sha256':sha(op),'R09_jets_sha256':sha(jp),
         'sign_partition_pieces':len(pieces),'root_boxes':N,'sign_leaves':len(c['sign_cover']),
         'reconstructed_step_moments':[v.pair() for v in S],'dual_objective_upper':str(Dcap),
         'independent_norm_lower_bound':lower.pair(),'correction_weights':[v.pair() for v in w],
         'modified_derivatives':[v.pair() for v in g],'control_determinant':rank.pair(),
         'independent_feasible_norm_upper':str(own_cost),'common_minimum_norm_bracket':[str(low),str(high)],
         'readable_minimum_norm_bracket':readable,'relative_gap_upper':str(gap),
         'relative_gap_readable_upper':'0.00000000005',
         'fourth_derivative_times_1e13':[decimal(g[4].lo*10**13,9),decimal(g[4].hi*10**13,9,True)],
         'control_determinant_times_1e40':[decimal(rank.lo*10**40,9),decimal(rank.hi*10**40,9,True)],
         'method':'Rational interval arithmetic at 512 bits, signed integral aggregation, sign-partition continuity, smoothing-error arithmetic, adjugate solve, full 3x3 control determinant and norm upper endpoints.',
         'trust_boundary':'Arb segment integrals, trigonometric interval evaluations, positive derivative envelopes, exact Q and analytic tail bounds are inputs. This checker proves their algebraic consequences; it does not independently validate the quadrature or the analytic smoothing lemma.'}
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:out[k] for k in ('status','readable_minimum_norm_bracket','relative_gap_readable_upper','fourth_derivative_times_1e13','control_determinant_times_1e40')},indent=2))


if __name__=='__main__':main()
