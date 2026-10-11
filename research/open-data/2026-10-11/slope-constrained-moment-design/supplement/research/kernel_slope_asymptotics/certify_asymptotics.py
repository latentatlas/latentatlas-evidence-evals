#!/usr/bin/env python3
"""R15: certify hypotheses and coefficient of the sharp large-slope law."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,time
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'kernel_norm_threshold'))
from certify_threshold import restore,pack,upper,zero_ball,residual,residual_derivative,sign_cover
from validated_flow import finite_kernel,domain_tail
from flint import arb,acb,arb_mat,ctx
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,msg):
    if not v:raise ArithmeticError(msg)
def rational(s):
    v=Fraction(s);return arb(v.numerator)/arb(v.denominator)
def bracket(left,right):
    a,b=Fraction(left),Fraction(right)
    m=(a+b)/2;r=(b-a)/2
    return arb(m.numerator)/arb(m.denominator)+zero_ball(upper(arb(r.numerator)/arb(r.denominator)))
def pvector(u,t,nmax):
    z=2*t*u;trig=[z.cos(),-z.sin(),-z.cos(),z.sin()]
    return [(2*u)**n*trig[n%4] for n in range(nmax+1)]
def rho_first(u,x):
    pi=arb.pi();z=(4*u).exp()
    return pi*(5*u).exp()*(2*pi*z-3)*(-pi*z+x[1]*u**2+x[2]*u**4).exp()
def rho_full(u,x,N=12):
    value=(finite_kernel(acb(u),N)*(acb(x[1])*acb(u)**2+acb(x[2])*acb(u)**4).exp()).real
    l,r=u.lower(),u.upper();pi=arb.pi();k=N+1
    ph=upper(max(x[1]*l*l,x[1]*r*r)+max(x[2]*l**4,x[2]*r**4))
    tail=upper(2*(2*pi*pi*k**4*(9*r).exp()+3*pi*k*k*(5*r).exp())*(-pi*k*k*(4*l).exp()+ph).exp())
    return value+zero_ball(tail),tail

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    need(not args.output.exists(),'Refuse overwrite');start=time.monotonic();ctx.dps=110
    paths={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
        'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
        'R14':HERE.parent/'kernel_slope_threshold/results/slope_threshold_certificate.json'}
    d={k:json.loads(p.read_text()) for k,p in paths.items()};old=d['R12'];q=d['Q']
    center=list(map(restore,q['center_exact_dyadic']));qr=restore(q['root_radius'])
    x=[v+zero_ball(upper(qr)) for v in center];params={1:x[1],2:x[2],3:arb(0)}
    a0=list(map(restore,old['a']));R=arb(2)**-40;aa=[v+zero_ball(R) for v in a0]
    knots=list(map(restore,old['breakpoints']));beta=restore(old['zero_box_radius']);beta_family=arb(2)**-24
    need(len(knots)==28 and old['initial_sign']==1,'Reference identity')
    f=list(map(restore,d['jets']['F_at_exact_Q']))[:9];f[:3]=[arb(0)]*3
    # Gradient at the fixed central a0, using narrower interval-Newton root images.
    central=[];displacements=[]
    for k,b in enumerate(knots):
        I=b+zero_ball(beta);rb=residual(b,x[0],a0);dr=residual_derivative(I,x[0],a0)
        need(not dr.contains(0),'Central derivative unresolved')
        image=b-rb/dr;dist=upper(abs(image-b));need(dist<beta,'Central root contraction escaped')
        central.append(dict(index=k,residual_at_old_knot=rb,derivative_on_old_box=dr,newton_image=image,displacement_upper=dist))
        displacements.append(dist)
    gradient=[];gradient_rows=[]
    for n in range(3):
        errors=[upper(2*displacements[k]*restore(old['root_boxes'][k]['rho_upper'])*(2*(knots[k]+beta))**n) for k in range(28)]
        tail=upper(2*domain_tail(params,n,arb(1)))
        bound=upper(abs(restore(old['step_moments_at_exact_Q'][n]))+sum(errors,arb(0))+tail)
        gradient.append(bound);gradient_rows.append(dict(order=n,root_errors=errors,tail_error=tail,absolute_gradient_upper=bound))
    gradnorm=upper(sum(gradient,arb(0)));m=arb(1)/200
    # Complete finite-domain sign cover, uniformly for the entire coefficient box.
    rows=[];leaves=[];left=arb(0);sign=1;H=[[arb(0) for j in range(3)] for i in range(3)]
    gamma=arb(0);p_first=[];loss=arb(0);expanded=[]
    need(residual(arb(0),x[0],aa)>0,'Boundary zero/sign unresolved')
    for k,b in enumerate(knots):
        lo,hi=b-beta_family,b+beta_family;I=b+zero_ball(beta_family)
        ends=[residual(lo,x[0],aa),residual(hi,x[0],aa)];der=residual_derivative(I,x[0],aa)
        need(sign*ends[0]>0 and sign*ends[1]<0 and not der.contains(0),'Uniform root isolation failed')
        sign_cover(left,lo,sign,x[0],aa,leaves)
        contractions=[];radius=beta_family;stopped_proposal=None
        for iteration in range(3):
            rb=residual(b,x[0],aa);dr=residual_derivative(I,x[0],aa)
            need(not dr.contains(0),'Uniform Newton denominator')
            newrad=upper(abs(rb/dr))
            if not newrad<radius:
                # Interval radii have finite precision. A non-improving proposal
                # is discarded; the last proved root enclosure remains valid.
                stopped_proposal=dict(iteration=iteration,input_radius=radius,proposed_radius=newrad)
                break
            contractions.append(dict(input_radius=radius,residual_at_center=rb,derivative=dr,output_radius=newrad))
            radius=newrad;I=b+zero_ball(radius)
        need(len(contractions)>=1,'No accepted uniform root contraction')
        derivative=residual_derivative(I,x[0],aa);first=rho_first(I,x);density,series=rho_full(I,x)
        need(first>0 and density>0 and not derivative.contains(0),'Root weights unresolved')
        p=pvector(I,x[0],8)
        for i in range(3):
            for j in range(3):H[i][j]+=2*first*p[i]*p[j]/abs(derivative)
        contribution=density*abs(derivative);gamma+=contribution
        if k<3:p_first.append(p[:3])
        J=b+zero_ball(upper(radius+arb(2)**-14));df=residual_derivative(J,x[0],aa);density_lower=rho_first(J,x)
        need(density_lower>0 and not df.contains(0),'Expanded exact-optimum loss neighborhood')
        ck=density_lower.lower()*abs(df).lower();loss+=ck;expanded.append(J)
        rows.append(dict(index=k,old_knot=b,coarse_left=lo,coarse_right=hi,coarse_endpoints=ends,
            coarse_derivative=der,sign_before=sign,contractions=contractions,stopped_proposal=stopped_proposal,root_interval=I,root_radius=radius,
            residual_derivative=derivative,first_density=first,full_density=density,density_series_error=series,
            p_values=p,gamma_contribution=contribution,expanded_interval=J,expanded_density=density_lower,
            expanded_derivative=df,loss_coefficient_lower=ck))
        left=hi;sign=-sign
    sign_cover(left,arb(1),sign,x[0],aa,leaves)
    B=[[H[i][j]-(m if i==j else 0) for j in range(3)] for i in range(3)]
    minors=[arb_mat([row[:n] for row in B[:n]]).det() for n in [1,2,3]]
    need(all(v>0 for v in minors),'Strong convexity Sylvester check failed')
    need(m*R>2*gradnorm,'Gradient/curvature localization inequality failed')
    det_p=arb_mat(p_first).det();need(not det_p.contains(0),'Three-switch moment Jacobian singular')
    # Tail phase: A>7u^3, |theta_prime| <= 1/(200 u^2), u>=1.
    need(x[0]>41 and x[0]<42,'Tail frequency range')
    need(abs(aa[0])<arb(1)/1000 and abs(aa[1])<arb(1)/10 and abs(aa[2])<arb(1)/200,'Tail coefficient range')
    phase_numerator=32*arb(1)/200+8*arb(1)/10/200+24*arb(1)/1000+2*arb(1)/1000/10
    need(phase_numerator/49<arb(1)/200,'Phase derivative inequality')
    d0=arb(1)/200
    need(2*rows[0]['root_interval'].lower()>d0 and all(rows[k+1]['root_interval'].lower()-rows[k]['root_interval'].upper()>d0 for k in range(27)),'Finite signed-root separation')
    need(1-rows[-1]['root_interval'].upper()>d0 and arb(3)/85>d0,'Tail junction separation')
    pi=arb.pi();muplus=upper(x[2]);C0=4*pi*pi+6*pi
    W1=upper(900*C0*(9+muplus-pi*arb(4).exp()).exp())
    margin=4*pi*arb(4).exp()-12-4*muplus
    need(margin>0 and margin*3/85>16,'Weighted root-sum tail decrease')
    gamma_tail=upper(W1/(1-arb(1)/50**4))
    gamma_total=gamma+zero_ball(gamma_tail)
    lower='0.00000000091787079603827';upper_delta='0.00000000091787079608363'
    delta=bracket(lower,upper_delta);coefficient=delta**4*gamma_total/(3*f[3]);relative=delta**3*gamma_total/(3*f[3])
    need(coefficient>0,'Leading coefficient not positive')
    # Limiting discontinuous minimizer's jets: not finite-M minimizer claims.
    sign_moments=[];sign_errors=[]
    for n in range(9):
        err=arb(0)
        for k,row in enumerate(rows):
            b=knots[k];rr=row['root_radius'];oldroot=old['root_boxes'][k]
            # Fresh coarse density bound on a box containing old and new signs.
            u=b+zero_ball(rr);_,series=rho_full(u,x)
            dens,_=rho_full(u,x)
            err+=2*rr*upper(abs(dens))*(2*u.upper())**n
        err=upper(err+2*domain_tail(params,n,arb(1)))
        sign_errors.append(err);sign_moments.append(restore(old['step_moments_at_exact_Q'][n])+zero_ball(err))
    g=[f[n]-delta*sign_moments[n] for n in range(9)]
    need(all(v.contains(0) for v in g[:4]),'Optimal sign constraints inconsistent with localization');g[:4]=[arb(0)]*4
    rank=g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    need(g[4]<0 and rank<0,'Limiting geometric nondegeneracy unresolved')
    L=rational(lower);finite_rel=loss*L**3/(3*f[3]);finite_abs=finite_rel*L
    need(L/rational('0.00002')<arb(2)**-14 and all(expanded[k].upper()<expanded[k+1].lower() for k in range(27)),'Uniform finite-budget lower domain')
    out=dict(status='asymptotic_hypotheses_and_leading_coefficient_certified',
        input_sha256={k:sha(p) for k,p in paths.items()},source_sha256={'certify_asymptotics.py':sha(__file__),
            '../kernel_norm_threshold/certify_threshold.py':sha(HERE.parent/'kernel_norm_threshold/certify_threshold.py'),
            '../cusp_verified/validated_flow.py':sha(HERE.parent/'cusp_verified/validated_flow.py')},
        dps=110,center=center,Q_box=x,Q_radius=qr,dual_center=a0,dual_localization_radius=R,dual_coefficient_box=aa,
        central_root_contractions=central,gradient_rows=gradient_rows,gradient_l1_upper=gradnorm,
        strong_convexity_constant=m,hessian_first_density=H,hessian_shifted_principal_minors=minors,
        localization_margin=m*R-2*gradnorm,coarse_root_box_radius=beta_family,uniform_roots=rows,
        uniform_sign_cover=leaves,first_three_evaluation_determinant=det_p,
        tail_phase_derivative_numerator_bound=phase_numerator,tail_phase_derivative_range=[81,85],
        signed_root_separation_lower=d0,tail_root_spacing_lower=arb(3)/85,
        tail_weight_at_one_upper=W1,tail_weight_decay_lower=margin,weighted_root_sum_finite=gamma,
        weighted_root_sum_tail_upper=gamma_tail,weighted_root_sum=gamma_total,delta_star_enclosure=delta,
        leading_coefficient=coefficient,relative_leading_coefficient=relative,
        limiting_sign_moment_errors=sign_errors,limiting_sign_moments=sign_moments,
        limiting_modified_derivatives=g,limiting_control_determinant=rank,
        finite_budget_loss_coefficient=loss,finite_budget_absolute_constant_lower=finite_abs,
        finite_budget_relative_constant_lower=finite_rel,finite_budget_lower_valid_for_M_at_least='0.00002',
        scope='Sharp large-M law delta(M)=delta_star+C/M^2+o(M^-2), conditional on the separate analytic proof. Validates a unique exact dual minimizer neighborhood, all positive residual zeros via finite cover plus monotone tail phase, summability, switch rank and C. No finite-M remainder, exact finite-M optimizer or new physical claim.',
        trust_boundary='Analytic lower/upper asymptotic argument and implicit-function construction are separate. Arb enclosures and prior certificates supply their numerical hypotheses; independent rational and mpmath checks cover stated parts.',elapsed_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(pack(out),indent=2)+'\n')
    print(out['status']);print('localization margin',out['localization_margin']);print('sign leaves',len(leaves))
    print('Gamma',gamma_total,'tail',gamma_tail);print('C',coefficient,'relative C',relative)
    print('switch determinant',det_p,'limiting rank',rank);print('uniform lower C',finite_abs)
if __name__=='__main__':main()
