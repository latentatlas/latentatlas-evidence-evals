#!/usr/bin/env python3
"""Independent rational reconstruction of R13 budget inequalities.

No FLINT, generating-module import, or assumption that a plotted curve is optimal.
The local transcendental enclosures and integral segments remain trusted inputs.
"""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'kernel_design_principle'))
from check_candidate import I,restore,decimal

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(v):
    m,e=v['mid_man_exp'];r,f=v['rad_man_exp']
    assert r==0
    return Q(m)*Q(2)**e
def absup(v):return max(abs(v.lo),abs(v.hi))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists()
    cp=HERE/'results/budget_certificate.json';c=json.loads(cp.read_text())
    paths={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
           'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
           'R11':HERE.parent/'kernel_design_principle/results/candidate_certificate.json',
           'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json'}
    for k,p in paths.items():assert c['input_sha256'][k]==sha(p)
    for k,h in c['source_sha256'].items():assert sha(HERE/k)==h
    d={k:json.loads(p.read_text()) for k,p in paths.items()};a,b=d['R11'],d['R12']
    j1=a['frequencies'];j2=b['correction_frequencies']
    w1=list(map(restore,a['weights']));w2=list(map(restore,b['correction_weights']))
    eta=exact(b['smoothing_width']);alpha=exact(b['alpha']);knots=list(map(exact,b['breakpoints']))
    spacing=min([2*knots[0]]+[y-x for x,y in zip(knots[:-1],knots[1:])])
    assert spacing>=32*eta and len(knots)==28
    assert sum(Q(4**k,factorial(k)) for k in range(8))>50
    exp_bound=Q(1,50**8)
    n1=sum(absup(w) for w in w1);s1=sum(2*j*absup(w) for j,w in zip(j1,w1))
    n2=alpha+sum(absup(w) for w in w2)
    s2=alpha/eta*(1+4*(2*len(knots)-1)*exp_bound)+sum(2*j*absup(w) for j,w in zip(j2,w2))
    M1=Q('0.00002');M2=Q(4);U1=Q('0.00000023803280902557')
    L,U2=map(Q,c['unconstrained_readable_bracket'])
    assert n1<U1 and s1<M1 and n2<U2 and s2<M2
    g1=list(map(restore,a['modified_derivatives']));g2=list(map(restore,b['modified_derivatives']))
    bern=[g1[4]*g1[7]-g1[5]*g1[6],
          (g1[4]*g2[7]+g2[4]*g1[7]-g1[5]*g2[6]-g2[5]*g1[6])/2,
          g2[4]*g2[7]-g2[5]*g2[6]]
    assert g1[4].hi<0 and g2[4].hi<0 and all(v.lo>0 for v in bern)
    f3=restore(d['jets']['F_at_exact_Q'][3]);D=exact(b['dual_objective_upper'])
    assert f3.lo/D>L
    assert c['local_root_box']==b['root_boxes'][0] and c['selected_root_index']==0
    radius=exact(c['local_radius']);beta=exact(b['zero_box_radius']);box=restore(c['local_interval'])
    assert radius==Q(2)**-12 and box.lo<=knots[0]-beta-radius
    assert box.hi>=knots[0]+beta+radius and box.lo>0
    density=restore(c['local_density_first_term_enclosure'])
    dr=restore(c['local_residual_derivative_enclosure'])
    assert density.lo>0 and dr.nonzero()
    slope_min=min(abs(dr.lo),abs(dr.hi));coef=density.lo*slope_min
    A4=sum((restore(v) for v in c['positive_moment_4_integrals']),I(0))
    error=absup(restore(c['positive_moment_4_tail']))+absup(restore(c['positive_moment_4_Q_displacement']))
    A4=A4+I(-error,error)
    K=Q(476270901)
    assert A4.lo>0 and A4.hi/(2*f3.lo)<K
    other=restore(c['positive_moment_4_high_precision'])
    assert max(A4.lo,other.lo)<=min(A4.hi,other.hi)
    def lower(M):
        if M==0:return Q(1)
        ell=min(radius,L/M)
        assert M*ell<=L
        penalty=coef*(L*ell**2-Q(2,3)*M*ell**3)
        assert penalty>0
        return max(L,1-K*M,(f3.lo+penalty)/D)
    def upper(M):
        if M<=M1:return 1-M/M1*(1-U1)
        if M<=M2:return U1+(M-M1)/(M2-M1)*(U2-U1)
        return U2
    readable=Q(c['witness_readable_norm_lower'])
    assert lower(M1)>readable>U2
    ms=sorted(set([Q(0),M1,M2]+[Q(10)**j for j in range(-12,2)]))
    samples=[]
    for M in ms:
        lo,hi=lower(M),upper(M);assert lo<=hi
        samples.append(dict(M=str(M),certified_lower=decimal(lo,28),
                            feasible_upper=decimal(hi,28,True)))
    out=dict(status='independent_rational_slope_budget_checks_passed',
        certificate_sha256=sha(cp),source_sha256=sha(__file__),
        slope_upper_bounds=[decimal(s1,24,True),decimal(s2,24,True)],
        norm_upper_bounds=[decimal(n1,28,True),decimal(n2,28,True)],
        mixture_rank_bernstein_positive=True,
        local_loss_coefficient_lower=decimal(coef,28),
        small_slope_kappa_upper=str(K),
        M_2e_minus5_lower=decimal(lower(M1),28),
        readable_M_2e_minus5_bracket=[c['witness_readable_norm_lower'],str(float(U1))],
        strict_separation_from_unconstrained_upper=True,
        samples=samples,
        plotting_parameters=dict(L=str(L),U2=str(U2),U1=str(U1),M1=str(M1),M2=str(M2),
                                 radius=str(radius),loss_coefficient=str(coef),f3_lower=str(f3.lo),
                                 dual_upper=str(D),kappa=str(K)),
        trust_boundary='Accepts local transcendental interval enclosures and positive-moment integral inputs. '
                       'Reconstructs algebra and outward displayed bounds with rational arithmetic. '
                       'Does not prove compactness or evaluate the exact finite-budget optimum.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status']);print('slope bounds',out['slope_upper_bounds'])
    print('delta(2e-5) lower',out['M_2e_minus5_lower'])

if __name__=='__main__':main()
