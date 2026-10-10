#!/usr/bin/env python3
"""R12: dual upper objective and smooth primal design from a sign template."""
import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R11=HERE.parent/'kernel_design_principle'
sys.path.insert(0,str(HERE.parent/'cusp_shape_design'))
from moment_dictionary import restore,pack,upper,zero_ball
from validated_flow import finite_kernel,series_tail,domain_tail
from flint import arb,acb,arb_mat,ctx


def need(value,message):
    if not value:raise ArithmeticError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exact_float(value):
    v=Fraction.from_float(value)
    ans=arb(v.numerator)/arb(v.denominator)
    need(ans.is_exact(),'Probe dyadic not exact')
    return ans


def interval(a,b):
    need(a.is_exact() and b.is_exact() and a<=b,'Invalid exact endpoints')
    return (a+b)/2+zero_ball((b-a)/2)


def residual(u,t,a):
    z=2*t*u;A=8*u**3+2*a[1]*u;B=4*a[2]*u*u-a[0]
    return A*z.sin()+B*z.cos()


def residual_derivative(u,t,a):
    z=2*t*u;A=8*u**3+2*a[1]*u;B=4*a[2]*u*u-a[0]
    return (24*u*u+2*a[1]-2*t*B)*z.sin()+(2*t*A+8*a[2]*u)*z.cos()


def rho_upper(l,r,params):
    pi=arb.pi();C=4*pi*pi+6*pi
    ph=upper(sum((max(upper(v*l**(2*j)),upper(v*r**(2*j))) for j,v in params.items()),arb(0)))
    return upper(C*(9*r+ph-pi*(4*l).exp()).exp())


def lipschitz_bounds(t,params,nmax=8):
    """Global sup bounds for the u derivative of rho*p_n, by positive envelopes."""
    pi=arb.pi();C0=4*pi*pi+6*pi;C1=60*pi*pi+30*pi+16*pi**3
    U=arb(2);pieces=256;M=[arb(0)]*(nmax+1);cells=[]
    for k in range(pieces):
        l,r=U*k/pieces,U*(k+1)/pieces
        ph=upper(sum((max(upper(v*l**(2*j)),upper(v*r**(2*j))) for j,v in params.items()),arb(0)))
        e=(ph-pi*(4*l).exp()).exp();rho=C0*(9*r).exp()*e
        dp=upper(sum((2*j*upper(abs(v))*r**(2*j-1) for j,v in params.items()),arb(0)))
        rhop=C1*(13*r).exp()*e+dp*rho
        row=[]
        for n in range(nmax+1):
            trig_derivative=2*upper(abs(t))*(2*r)**n
            if n:trig_derivative+=2*n*(2*r)**(n-1)
            value=upper(rhop*(2*r)**n+rho*trig_derivative)
            M[n]=max(M[n],value);row.append(value)
        cells.append({'left':l,'right':r,'bounds':row})
    # Every positive envelope term decreases on [U,infinity): the largest
    # polynomial degree is nmax+3 and the largest linear exponent is 13u.
    pp=upper(sum((2*j*max(arb(0),upper(v))*U**(2*j-1) for j,v in params.items()),arb(0)))
    c=4*pi*(4*U).exp()-13-arb(nmax+3)/U-pp
    need(c>0 and all(U>=arb(2*j-1)/4 for j,v in params.items() if v>0),'Derivative-envelope tail not decreasing')
    ph=upper(sum((max(arb(0),upper(v))*U**(2*j) for j,v in params.items()),arb(0)))
    e=(ph-pi*(4*U).exp()).exp();rho=C0*(9*U).exp()*e
    dp=upper(sum((2*j*upper(abs(v))*U**(2*j-1) for j,v in params.items()),arb(0)))
    rhop=C1*(13*U).exp()*e+dp*rho;tails=[]
    for n in range(nmax+1):
        v=rhop*(2*U)**n+rho*2*upper(abs(t))*(2*U)**n
        if n:v+=rho*2*n*(2*U)**(n-1)
        v=upper(v);tails.append(v);M[n]=max(M[n],v)
    return M,{'cutoff':U,'pieces':pieces,'cells':cells,'tail_decrease_margin':c,'tail_bounds':tails,
              'kernel_constants':[C0,C1],'formula':'|rho*p_n| derivative bounded by |rho_prime|*(2u)^n + rho*(2n*(2u)^(n-1)+2|t|*(2u)^n). Phi bound C0*exp(9u-pi*exp(4u)); |Phi_prime| bound C1*exp(13u-pi*exp(4u)).'}


def sign_cover(left,right,sign,t,a,leaves,depth=0):
    if left==right:return
    I=interval(left,right);r=residual(I,t,a)
    if sign*r>0:
        leaves.append({'left':left,'right':right,'sign':sign,'method':'range','residual':r});return
    dr=residual_derivative(I,t,a)
    ends=[residual(left,t,a),residual(right,t,a)]
    if not dr.contains(0) and all(sign*v>0 for v in ends):
        leaves.append({'left':left,'right':right,'sign':sign,'method':'monotone','derivative':dr,'endpoints':ends});return
    need(depth<60,'Sign cover failed: unaccounted zero or overly wide interval')
    mid=(left+right)/2
    sign_cover(left,mid,sign,t,a,leaves,depth+1)
    sign_cover(mid,right,sign,t,a,leaves,depth+1)


def finite_segment(x,n,left,right,N=8):
    t,lam,mu=x
    def fun(u,analytic):
        if not (4*u).exp().real>0:return acb('nan','nan')
        z=2*acb(t)*u;trig=(z.cos(),-z.sin(),-z.cos(),z.sin())[n%4]
        return finite_kernel(u,N)*(acb(lam)*u*u+acb(mu)*u**4).exp()*(2*u)**n*trig
    value=acb.integral(fun,acb(left),acb(right),abs_tol=arb('1e-60'),rel_tol=arb('1e-60'),eval_limit=100000)
    need(value.is_finite(),'Segment quadrature did not converge')
    return value.real


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    need(not args.output.exists(),'Refuse to replace a recorded certificate')
    start=time.monotonic();ctx.dps=110
    pp=HERE/'diagnostics/l1_probe.json';probe=json.loads(pp.read_text())
    qp=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';q=json.loads(qp.read_text())
    jp=HERE.parent/'cusp_shape_design/results/local_jets.json';jets=json.loads(jp.read_text())
    cp=R11/'results/candidate_certificate.json';old=json.loads(cp.read_text())
    x=list(map(restore,q['center_exact_dyadic']));rQ=restore(q['root_radius'])
    need(all(v.is_exact() for v in x),'Exact dyadic Q center lost')
    Qbox=[v+zero_ball(upper(rQ)) for v in x]
    params={1:Qbox[1],2:Qbox[2],3:arb(0)}
    center_params={1:x[1],2:x[2],3:arb(0)}
    B=list(map(restore,q['absolute_derivative_bounds']))
    f=list(map(restore,jets['F_at_exact_Q']))[:9];f[:3]=[arb(0)]*3
    a=list(map(exact_float,probe['a']))
    alpha=exact_float(probe['norm_estimate'])
    breaks=[exact_float(v) for v in probe['roots_0_2'] if 0<v<1]
    U=arb(1);N=8;beta=arb(2)**-36;eta=arb(2)**-32
    need(breaks and all(v>beta and v<U-beta for v in breaks),'Invalid sign-template knots')
    need(all(breaks[i+1]-breaks[i]>2*beta for i in range(len(breaks)-1)),'Overlapping zero boxes')
    initial=1 if residual(arb(0),Qbox[0],a)>0 else -1
    need(initial*residual(arb(0),Qbox[0],a)>0,'Initial sign unresolved')
    boxes=[];leaves=[];left=arb(0);sign=initial;wrong=arb(0)
    for b in breaks:
        lo,hi=b-beta,b+beta;I=interval(lo,hi)
        ends=[residual(lo,Qbox[0],a),residual(hi,Qbox[0],a)]
        dr=residual_derivative(I,Qbox[0],a)
        need(sign*ends[0]>0 and sign*ends[1]<0 and not dr.contains(0),'Zero box does not isolate a unique crossing')
        sign_cover(left,lo,sign,Qbox[0],a,leaves)
        rp=upper(abs(residual(b,Qbox[0],a))+beta*upper(abs(dr)))
        rh=rho_upper(lo,hi,params);err=upper(4*beta*rh*rp)
        wrong+=err
        boxes.append({'center':b,'left':lo,'right':hi,'sign_before':sign,'endpoints':ends,
                      'derivative':dr,'residual_abs_upper':rp,'rho_upper':rh,'objective_error_upper':err})
        left=hi;sign=-sign
    sign_cover(left,U,sign,Qbox[0],a,leaves)
    T=[domain_tail(params,n,U) for n in range(9)]
    wrong_tail=upper(2*(T[3]+sum((abs(a[i])*T[i] for i in range(3)),arb(0))))
    print('Sign proof:',len(boxes),'crossings,',len(leaves),'sign leaves',flush=True)
    M,majorants=lipschitz_bounds(Qbox[0],params)
    smooth_errors=[upper(len(breaks)*v*eta*eta) for v in M]
    print('Smooth moment error bounds:',[str(v) for v in smooth_errors[:4]],flush=True)
    ends=[arb(0)]+breaks+[U];segments=[];S=[arb(0)]*9
    for k,(lo,hi) in enumerate(zip(ends[:-1],ends[1:])):
        s=initial*(-1)**k
        values=[finite_segment(x,n,lo,hi,N) for n in range(9)]
        for n in range(9):S[n]+=s*values[n]
        segments.append({'left':lo,'right':hi,'sign':s,'finite_integrals':values})
        print('Integrated segment',k+1,'/',len(ends)-1,flush=True)
    errors=[]
    for n in range(9):
        truncation=upper(series_tail(center_params,n,U,N)+domain_tail(center_params,n,U))
        displacement=upper(rQ*(B[n+1]+B[n+2]/4+B[n+4]/16))
        err=upper(truncation+displacement);errors.append({'truncation':truncation,'Q_displacement':displacement})
        S[n]+=zero_ball(err)
    Z=S[3]-sum((a[i]*S[i] for i in range(3)),arb(0))
    Dupper=upper(Z+wrong+wrong_tail)
    need(Dupper>0,'Dual objective upper bound nonpositive')
    lower=f[3]/Dupper
    Arows=[[restore(v) for v in row] for row in old['design_matrix']]
    A=arb_mat(Arows);det=A.det();need(not det.contains(0),'Correction matrix unresolved')
    dictionary=[[restore(row['moments'][n]) for row in old['dictionary']] for n in range(9)]
    smooth=[S[n]+zero_ball(smooth_errors[n]) for n in range(9)]
    target=[arb(0),arb(0),arb(0),-f[3]]
    rhs=[target[n]+alpha*smooth[n] for n in range(4)]
    sol=A.solve(arb_mat([[v] for v in rhs]));w=[sol[i,0] for i in range(4)]
    response=[-alpha*smooth[n]+sum((dictionary[n][j]*w[j] for j in range(4)),arb(0)) for n in range(9)]
    g=[f[n]+response[n] for n in range(9)]
    need(all(v.contains(0) for v in g[:4]),'Exact defining system inconsistent')
    g[:4]=[arb(0)]*4
    cost_ball=alpha+sum((abs(v) for v in w),arb(0))
    # Only an outward upper endpoint is a certified feasible budget.
    # The lower end of a wide ball for an absolute value may be negative.
    cost=upper(cost_ball)
    rank=g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    need(cost<1 and g[4]<0 and rank<0,'Smooth nondegenerate positive design unresolved')
    need(lower>0 and lower<cost,'Norm bracket inconsistent')
    out={
        'status':'certified_dual_bound_and_smooth_near_minimum_pinned_design',
        'source_sha256':{'certify_threshold.py':sha(__file__),'../cusp_verified/validated_flow.py':sha(HERE.parent/'cusp_verified/validated_flow.py')},
        'input_sha256':{'probe':sha(pp),'R01_Q':sha(qp),'R09_jets':sha(jp),'R11_candidate':sha(cp)},
        'frozen_R11_manifest_sha256':sha(R11/'manifest.json'),
        'center':x,'Q_radius':rQ,'a':a,'alpha':alpha,'cutoff':U,'kernel_terms':N,
        'quadrature':{'dps':110,'abs_tol':'1e-60','rel_tol':'1e-60','pieces':len(segments)},
        'breakpoints':breaks,'initial_sign':initial,'zero_box_radius':beta,'smoothing_width':eta,
        'root_boxes':boxes,'sign_cover':leaves,'derivative_majorants':majorants,'lipschitz_bounds':M,
        'smooth_moment_errors':smooth_errors,'segments':segments,'step_moment_errors':errors,
        'step_moments_at_exact_Q':S,'signed_residual_integral':Z,
        'wrong_sign_error':upper(wrong),'wrong_sign_tail_error':wrong_tail,'dual_objective_upper':Dupper,
        'minimum_norm_lower_bound':lower,'smooth_moments_at_exact_Q':smooth,
        'correction_frequencies':old['frequencies'],'correction_matrix_determinant':det,
        'correction_rhs':rhs,'correction_weights':w,'modified_derivatives':g,
        'three_control_determinant':rank,'coefficient_cost_enclosure':cost_ball,
        'feasible_norm_upper_enclosure':cost,
        'bracket_ratio_enclosure':cost/lower,'relative_gap_enclosure':cost/lower-1,
        'smooth_definition':'Even step template s0 with knots +/-b and alternating signs, convolved on R with sech^2(v/eta)/(2 eta). Thus |s_eta|<=1 and s_eta is smooth. Set h=-alpha*s_eta+sum w_j*cos(2j*u). Define w exactly by A*w=(0,0,0,-F3)+alpha*(S_eta,0..3).',
        'smoothing_lemma':'For q_n(u)=rho(u)*p_n(u), even extension is globally Lipschitz with constant M_n. For N positive knots, |integral_0^infty q_n*(s_eta-s0)| <= N*M_n*eta^2. Odd smoothing error cancels the constant term; logistic tails bounded by exp(-2|v|/eta).',
        'scope':'Fixed original Q, relative L-infinity norm, no frequency or derivative constraint. Feasible design is real analytic, positive and exactly order four with rank-three controls. R10 finite root regions are not transferred.',
        'trust_boundary':'New Arb interval sign cover, positive derivative envelopes and segment quadrature. Smoothing errors are analytic bounds, not numerical evaluations of the narrow transitions. Exact pinning is supplied by a defining moment system, not a residual tolerance.',
        'elapsed_seconds':time.monotonic()-start,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as stream:json.dump(pack(out),stream,indent=2);stream.write('\n')
    print('Minimum norm lower:',lower)
    print('Smooth feasible upper:',cost)
    print('Relative gap:',cost/lower-1)
    print('Fourth derivative:',g[4]);print('Control determinant:',rank)


if __name__=='__main__':main()
