#!/usr/bin/env python3
"""R13: certified slope budgets and a finite-budget dual loss bound."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,time
from fractions import Fraction
from math import factorial
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'kernel_norm_threshold'))
from certify_threshold import restore,pack,upper,zero_ball,residual_derivative
from validated_flow import finite_kernel,series_tail,domain_tail
from flint import arb,acb,ctx

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,msg):
    if not v:raise ArithmeticError(msg)

def positive_four(x,N,panels,dps):
    ctx.dps=dps;t,lam,mu=x
    def fun(u,analytic):
        if not (4*u).exp().real>0:return acb('nan','nan')
        return finite_kernel(u,N)*(acb(lam)*u*u+acb(mu)*u**4).exp()*(2*u)**4
    total=acb(0);parts=[]
    for k in range(panels):
        v=acb.integral(fun,acb(arb(2)*k/panels),acb(arb(2)*(k+1)/panels),
            abs_tol=arb('1e-'+str(dps-20))/panels,rel_tol=arb('1e-'+str(dps-20)),eval_limit=100000)
        need(v.is_finite(),'Positive moment integral failed');parts.append(v.real);total+=v
    params={1:lam,2:mu,3:arb(0)}
    tail=upper(series_tail(params,4,arb(2),N)+domain_tail(params,4,arb(2)))
    return total.real+zero_ball(tail),parts,tail

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    need(not args.output.exists(),'Refuse overwrite');start=time.monotonic();ctx.dps=110
    paths={
      'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
      'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
      'R11':HERE.parent/'kernel_design_principle/results/candidate_certificate.json',
      'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json'}
    d={k:json.loads(p.read_text()) for k,p in paths.items()}
    q,x11,x12=d['Q'],d['R11'],d['R12']
    x=list(map(restore,q['center_exact_dyadic']));rQ=restore(q['root_radius'])
    qb=[v+zero_ball(rQ) for v in x];B=list(map(restore,q['absolute_derivative_bounds']))
    f3=restore(d['jets']['F_at_exact_Q'][3]);need(f3>0,'f3 positive')
    w1=list(map(restore,x11['weights']));j1=x11['frequencies']
    norm1=sum((abs(v) for v in w1),arb(0))
    slope1=sum((2*j*abs(v) for j,v in zip(j1,w1)),arb(0))
    knots=list(map(restore,x12['breakpoints']));eta=restore(x12['smoothing_width']);alpha=restore(x12['alpha'])
    spacing=min([2*knots[0]]+[b-a for a,b in zip(knots[:-1],knots[1:])])
    need(spacing>=32*eta,'Transition separation insufficient')
    # e^4 > sum_{k=0}^7 4^k/k! > 50, hence exp(-32) < 50^-8.
    exp_partial=sum(Fraction(4**k,factorial(k)) for k in range(8))
    need(exp_partial>50,'Rational exponential inequality')
    ebound=arb(1)/50**8
    w2=list(map(restore,x12['correction_weights']));j2=x12['correction_frequencies']
    norm2=alpha+sum((abs(v) for v in w2),arb(0))
    transition_slope=(1+4*(2*len(knots)-1)*ebound)/eta
    slope2=alpha*transition_slope+sum((2*j*abs(v) for j,v in zip(j2,w2)),arb(0))
    M1=arb('0.00002');U1=arb('0.00000023803280902557')
    M2=arb(4);U2=arb('0.00000000091787079608363');L=arb('0.00000000091787079603827')
    need(norm1<U1 and slope1<M1 and norm2<U2 and slope2<M2,'Anchor budget failed')
    g1=list(map(restore,x11['modified_derivatives']));g2=list(map(restore,x12['modified_derivatives']))
    bern=[g1[4]*g1[7]-g1[5]*g1[6],
          (g1[4]*g2[7]+g2[4]*g1[7]-g1[5]*g2[6]-g2[5]*g1[6])/2,
          g2[4]*g2[7]-g2[5]*g2[6]]
    need(g1[4]<0 and g2[4]<0 and all(v>0 for v in bern),'Mixture rank failed')
    a=list(map(restore,x12['a']));b=knots[0];beta=restore(x12['zero_box_radius']);radius=arb(2)**-12
    I=b+zero_ball(upper(beta+radius));pi=arb.pi();z=(4*I).exp()
    rho1=pi*(5*I).exp()*(2*pi*z-3)*(-pi*z+qb[1]*I*I+qb[2]*I**4).exp()
    derivative=residual_derivative(I,qb[0],a)
    need(rho1>0 and not derivative.contains(0) and I>0,'Local dual-loss bounds failed')
    c=rho1.lower()*abs(derivative).lower()
    D=restore(x12['dual_objective_upper']);need(f3/D>L,'Base lower bound unavailable')
    A4,parts,tail=positive_four(x,16,8,110)
    displacement=upper(rQ*(B[6]/4+B[8]/16));A4+=zero_ball(displacement)
    other,parts2,tail2=positive_four(x,24,12,135);other+=zero_ball(displacement)
    need(A4.overlaps(other),'Higher-precision positive moment disagreement');ctx.dps=110
    kappa=upper(A4/(2*f3));ell=L/M1
    need(ell<radius,'Witness loss radius exceeds certified neighborhood')
    penalty=c*(L*ell**2-arb(2)/3*M1*ell**3)
    budget_lower=(f3+penalty)/D
    readable_lower=arb('0.000000000917870847')
    need(budget_lower>readable_lower and readable_lower>U2,'Finite slope separation not established')
    out=dict(status='slope_anchors_and_finite_budget_separation_passed',
        input_sha256={k:sha(p) for k,p in paths.items()},source_sha256={
          'certify_budget.py':sha(__file__),
          '../cusp_verified/validated_flow.py':sha(HERE.parent/'cusp_verified/validated_flow.py'),
          '../kernel_norm_threshold/certify_threshold.py':sha(HERE.parent/'kernel_norm_threshold/certify_threshold.py')},
        unconstrained_readable_bracket=['0.00000000091787079603827','0.00000000091787079608363'],
        anchors=[dict(name='R11_four_cosines',slope_budget='0.00002',norm_budget='0.00000023803280902557',
                      computed_norm=norm1,computed_slope=slope1),
                 dict(name='R12_smooth_near_minimum',slope_budget='4',norm_budget='0.00000000091787079608363',
                      computed_norm=norm2,computed_slope=slope2)],
        transition_min_spacing=spacing,transition_width=eta,exp_minus_32_upper=ebound,
        exp4_partial_sum=[exp_partial.numerator,exp_partial.denominator],
        transition_slope_upper=transition_slope,mixture_rank_bernstein=bern,
        selected_root_index=0,local_root_box=x12['root_boxes'][0],local_radius=radius,
        local_interval=I,local_density_first_term_enclosure=rho1,
        local_residual_derivative_enclosure=derivative,loss_coefficient_lower=c,
        positive_moment_4_at_exact_Q=A4,positive_moment_4_Q_displacement=displacement,
        positive_moment_4_integrals=parts,positive_moment_4_tail=tail,
        positive_moment_4_high_precision=other,positive_moment_4_high_precision_integrals=parts2,
        positive_moment_4_high_precision_tail=tail2,small_slope_kappa_upper=kappa,
        witness_slope_budget=M1,witness_pair_radius=ell,witness_dual_loss_lower=penalty,
        witness_norm_lower=budget_lower,witness_readable_norm_lower='0.000000000917870847',
        witness_exceeds_unconstrained_upper=budget_lower-U2,
        scope='Fixed exact Q; bounded Lipschitz h in original u coordinate. No mass normalization. '
              'Bounds and feasible witnesses, not an evaluated complete optimal value curve.',
        trust_boundary='Analytic compactness and dual-loss proofs separate from arithmetic. '
              'New Arb local enclosures and one positive moment, with a higher-precision repeat; '
              'old exact moment identities and input certificates retained.',
        elapsed_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(pack(out),indent=2)+'\n')
    print('status',out['status']);print('anchor slopes',slope1,slope2)
    print('A4',A4,'kappa',kappa);print('finite budget lower',budget_lower)
    print('gap above old upper',budget_lower-U2)

if __name__=='__main__':main()
