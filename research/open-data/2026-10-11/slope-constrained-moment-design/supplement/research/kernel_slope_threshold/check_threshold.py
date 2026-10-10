#!/usr/bin/env python3
"""R14 independent rational reconstruction; no FLINT or producer import."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'kernel_design_principle'))
from check_candidate import I,restore,determinant,decimal
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(v):
    m,e=v['mid_man_exp'];r,f=v['rad_man_exp'];assert r==0
    return Q(m)*Q(2)**e
def absup(v):return max(abs(v.lo),abs(v.hi))
def overlap(a,b):return max(a.lo,b.lo)<=min(a.hi,b.hi)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists()
    cp=HERE/'results/slope_threshold_certificate.json';c=json.loads(cp.read_text())
    paths={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
           'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
           'R11':HERE.parent/'kernel_design_principle/results/candidate_certificate.json',
           'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
           'R13':HERE.parent/'kernel_slope_budget/results/budget_certificate.json',
           'probe':HERE/'diagnostics/candidate_probe.json'}
    for k,p in paths.items():assert c['input_sha256'][k]==sha(p),k
    for k,digest in c['source_sha256'].items():assert sha(HERE/k)==digest,k
    data={k:json.loads(p.read_text()) for k,p in paths.items()};old=data['R12'];probe=data['probe'];r11=data['R11']
    knots=list(map(exact,c['breakpoints']));oldknots=list(map(exact,old['breakpoints']))
    assert knots[:3]==[Q(a,b) for a,b in probe['first_three_knots_dyadic']]
    assert knots[3:]==oldknots[3:] and len(knots)==28
    eta=exact(c['smoothing_width']);alpha=exact(c['alpha']);V=exact(c['transition_cutoff'])
    assert eta==Q(49500,2**30) and alpha==Q(*probe['alpha_dyadic']) and V==32
    spacing=min([2*knots[0]]+[b-a for a,b in zip(knots[:-1],knots[1:])])
    assert spacing>2*V*eta and knots[-1]+V*eta<1 and spacing>=32*eta
    assert len(c['shift_integrals'])==3 and len(c['transition_integrals'])==28
    S=list(map(restore,old['step_moments_at_exact_Q']))
    for k,row in enumerate(c['shift_integrals']):
        assert row['index']==k and exact(row['old'])==oldknots[k] and exact(row['new'])==knots[k]
        assert row['jump']==-2*(-1)**k and len(row['oriented_integrals'])==9
        for n,v in enumerate(row['oriented_integrals']):S[n]=S[n]-row['jump']*restore(v)
    for k,row in enumerate(c['transition_integrals']):
        assert row['index']==k and exact(row['knot'])==knots[k] and row['jump']==-2*(-1)**k
        assert len(row['rescaled_integrals'])==9
        for n,v in enumerate(row['rescaled_integrals']):S[n]=S[n]+row['jump']*restore(v)
    assert sum(Q(4**k,factorial(k)) for k in range(8))>50
    # Independent, slightly larger rational e^-64 bound for all smoothing tails.
    errors=[]
    for n,row in enumerate(c['moment_error_bounds']):
        majorant=absup(restore(old['lipschitz_bounds'][n]))
        tail=2*28*majorant*eta**2*(V+Q(1,2))*Q(1,50**16)
        error=absup(restore(row['series']))+tail;errors.append(error)
        S[n]=S[n]+I(-error,error)
        assert overlap(S[n],restore(c['smoothed_moments_at_exact_Q'][n]))
    f=list(map(restore,data['jets']['F_at_exact_Q']))[:9];f[:3]=[I(0)]*3
    A=[[restore(v) for v in row] for row in r11['design_matrix']]
    dictionary=[[restore(row['moments'][n]) for row in r11['dictionary']] for n in range(9)]
    assert all(overlap(A[n][k],dictionary[n][k]) for n in range(4) for k in range(4))
    det=determinant(A);assert det.nonzero();rhs=[alpha*S[n]-(f[3] if n==3 else I(0)) for n in range(4)]
    weights=[]
    for j in range(4):
        Aj=[[rhs[n] if k==j else A[n][k] for k in range(4)] for n in range(4)]
        weights.append(determinant(Aj)/det)
    for x,y in zip(weights,c['correction_weights']):assert overlap(x,restore(y))
    g=[f[n]-alpha*S[n]+sum((dictionary[n][j]*weights[j] for j in range(4)),I(0)) for n in range(9)]
    assert all(v.lo<=0<=v.hi for v in g[:4]);g[:4]=[I(0)]*4
    J=[[-g[n+2]/4,g[n+4]/16,-g[n+6]/64] for n in range(3)]
    rank=determinant(J);reduced=g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    assert rank.hi<0 and reduced.hi<0 and overlap(rank,reduced) and g[4].hi<0
    norm=alpha+sum(absup(v) for v in weights)
    assert c['correction_frequencies']==r11['frequencies']==[40,41,42,43]
    slope=alpha/eta*(1+4*(2*28-1)*Q(1,50**8))+sum(2*j*absup(v) for j,v in zip([40,41,42,43],weights))
    M=Q('0.00002');mb=restore(c['slope_budget']);assert mb.lo<=M<=mb.hi and slope<M and norm<1
    radius=exact(c['lower_local_radius']);beta=exact(old['zero_box_radius'])
    assert radius==Q(2)**-14 and exact(c['lower_root_box_radius'])==beta
    L=Q('0.00000000091787079603827');oldU=Q('0.00000000091787079608363');ell=L/M
    assert ell<radius and all(b-a>2*(radius+beta) for a,b in zip(oldknots[:-1],oldknots[1:]))
    assert len(c['lower_crossings'])==28;coefficient=Q(0)
    for k,row in enumerate(c['lower_crossings']):
        assert row['index']==k and exact(row['center'])==oldknots[k]
        box=restore(row['interval']);assert 0<box.lo<=oldknots[k]-beta-radius and box.hi>=oldknots[k]+beta+radius
        density=restore(row['density_first_term']);derivative=restore(row['residual_derivative'])
        assert density.lo>0 and derivative.nonzero()
        coefficient+=density.lo*min(abs(derivative.lo),abs(derivative.hi))
    penalty=coefficient*L**3/(3*M*M);D=exact(old['dual_objective_upper']);lower=(f[3].lo+penalty)/D
    display=list(map(Q,c['readable_bracket']))
    assert oldU<display[0]<lower<norm<display[1]<Q('0.00000023803280902557')
    gap=display[1]/display[0]-1;relative=[display[0]/oldU-1,display[1]/L-1]
    assert gap<Q('0.00000376') and relative[0]>Q('0.00000248') and relative[1]<Q('0.00000625')
    out=dict(status='independent_rational_finite_slope_threshold_passed',certificate_sha256=sha(cp),source_sha256=sha(__file__),
        readable_bracket=c['readable_bracket'],reconstructed_lower=decimal(lower,30),reconstructed_upper=decimal(norm,30,True),
        feasible_slope_upper=decimal(slope,30,True),relative_bracket_gap_upper=decimal(gap,20,True),
        relative_increase_over_unconstrained=[decimal(relative[0],20),decimal(relative[1],20,True)],
        shift_integral_count=27,transition_integral_count=252,disjoint_loss_neighborhoods=28,
        weights=[v.pair() for v in weights],modified_derivatives=[v.pair() for v in g],control_determinant=rank.pair(),
        loss_coefficient_lower=decimal(coefficient,30),moment_error_upper=[decimal(v,80,True) for v in errors],
        trust_boundary='Integral and local transcendental balls and series tails accepted as inputs. Exact rational reconstruction uses independent Cramer determinants, a larger rational exponential tail, global slope and 28 disjoint loss estimates. No exact optimizer claim.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status']);print('bracket',out['readable_bracket']);print('relative increase',out['relative_increase_over_unconstrained'])
if __name__=='__main__':main()
