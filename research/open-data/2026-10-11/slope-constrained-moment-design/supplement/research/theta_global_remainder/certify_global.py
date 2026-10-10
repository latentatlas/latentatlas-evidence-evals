#!/usr/bin/env python3
"""R26: validated global constants with a width-dependent finite prefix."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
from flint import arb,arb_mat,ctx
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'theta_effective_remainder'))
from jets import restore,pack,rational,upper,absup,zero_ball,sm,pjets
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def matrix(x):return arb_mat([list(map(restore,row)) for row in x])
def produce():
    assert __debug__;ctx.dps=120
    op=HERE.parent/'theta_effective_remainder/results/certificate.json';ap=HERE/'results/algebra.json'
    old=json.loads(op.read_text());alg=json.loads(ap.read_text())
    assert alg['source_sha256']==sha(HERE/'check_algebra.py')
    eps=rational(alg['epsilon']);a0=rational(alg['a_max']);V=list(map(rational,alg['v_absolute_bounds']))
    params=list(map(restore,old['Q_box']));b=list(map(restore,old['expanded_trial_dual_box']));v=list(map(restore,old['v_enclosure']))
    assert all(absup(v[j])<V[j] for j in range(3))
    assert all(absup(b[j])<rational(s) for j,s in enumerate(['.001','.1','.005']))
    assert 41<params[0] and params[0]<42 and -4<params[1] and params[1]<0 and 0<params[2] and params[2]<9
    gap=rational('1.0005')+zero_ball(rational('.0005'));p=pjets(gap,params[0],0)
    rawgap=p[3][0]-sm(b[j]*p[j][0] for j in range(3));assert rawgap>0
    denom=1-arb(1)/50**4;pi=arb.pi();e4=arb(4).exp();assert 3<pi and pi<4 and e4>50
    weighted={}
    for d in [12,16,24]:
        value=88*(18+d-pi*e4).exp()
        weighted[str(d)]={'root_sum':upper(value/denom),'integral':upper(value/500)}
    S12,S16,S24=[weighted[str(d)]['root_sum'] for d in [12,16,24]]
    I16,I24=[weighted[str(d)]['integral'] for d in [16,24]]
    Hj=list(map(rational,alg['active_moment_constants']));Cs=rational(alg['active_residual_sixth_constant'])
    Ch=rational(alg['active_balance_fourth_constant']);C8=rational(alg['active_dual_eighth_constant'])
    fac4=1/(1-48*a0);fac6=1/(1-72*a0)
    active_moment=[upper(Hj[j]*S12) for j in range(3)]
    inactive_moment_leading=upper(188*eps**-2*S12)
    inactive_moment_integral=[upper(2**(j+1)*eps**-4*fac4*I16) for j in range(3)]
    moment_tail=[upper(active_moment[j]+inactive_moment_leading+inactive_moment_integral[j]) for j in range(3)]
    active_target=upper(Cs*S16+sm(V[j]*active_moment[j] for j in range(3)))
    inactive_gamma=upper(300*eps**-4*S16);inactive_Xi=upper(2071000*eps**-2*S16)
    inactive_objective=upper(18*eps**-6*fac6*I24)
    target_tail=upper(active_target+inactive_gamma+inactive_Xi+inactive_objective)
    dual8_tail=upper(C8*S24)
    # Only the finite-root constants of R25 are inherited; its a_min-dependent tail terms are not reused.
    Hfinite=list(map(restore,old['moment_fourth_bounds_finite']));H=[upper(Hfinite[j]+moment_tail[j]) for j in range(3)]
    C=matrix(old['moment_preconditioner']);W=list(map(restore,old['repair_scaled_box']))
    contraction=list(map(restore,old['repair_contraction']))
    forcing=[upper(sm(absup(C[i,j])*H[j] for j in range(3))/W[i]) for i in range(3)]
    assert all(contraction[i]+forcing[i]<1 for i in range(3))
    K6=upper(restore(old['K6_finite'])+target_tail)
    Kdual=upper(K6+a0**2*(restore(old['K8dual'])+dual8_tail))
    Kprimal=upper(K6+a0**2*restore(old['K8primal']))
    co={k:restore(x) for k,x in old['coefficient_inputs'].items()}
    f,delta,D,Gamma,Xi=[co[k] for k in ['f','delta0','D','Gamma','Xi']]
    M0=rational('2e-5');U=restore(old['amplitude_upper'])
    assert Xi>0 and U<1 and U/M0<a0
    # Auxiliary scalar G_M(A)=F_M(A)-Kprimal*A^7/M^6. Its root yields a feasible amplitude.
    lower_endpoint_coefficient=(Gamma/3-Xi*delta**2/M0**2).lower();assert lower_endpoint_coefficient>0
    upper_endpoint_margin=(U-delta-Gamma*U**3/(3*D*M0**2)-Kprimal*U**7/(D*M0**6)).lower();assert upper_endpoint_margin>0
    auxiliary_derivative_lower=(D-Gamma*U**2/M0**2-7*Kprimal*U**6/M0**6).lower();assert auxiliary_derivative_lower>0
    Fderivative=(D-Gamma*U**2/M0**2).lower();assert Fderivative>0
    assert delta+co['C2']/M0**2+co['C4']/M0**4<U
    Kpoly=restore(old['Kpoly'])
    Kminus=upper((Kpoly+Kdual*U**7)/Fderivative)
    Kplus=upper((Kpoly+Kprimal*U**7)/Fderivative)
    assert Kminus<rational('9.593e-54') and Kplus<rational('1.488e-53')
    # The positive C4 dominates the whole remainder from this explicit onset onward.
    dominance=(co['C4']-rational('9.593e-54')/M0**2).lower();assert dominance>0
    return pack({'status':'R26_uniform_all_large_M_fourth_order_remainder','dps':120,
       'source_sha256':sha(__file__),'algebra_sha256':sha(ap),'R25_certificate_sha256':sha(op),
       'epsilon':eps,'maximum_half_width':a0,'minimum_slope_budget':M0,'v_absolute_bounds':V,
       'expanded_trial_dual_box':b,'tail_initial_gap':gap,'tail_gap_raw_residual':rawgap,
       'weighted_tail_decay_lower':500,'weighted_root_spacing_lower':'3/85','weighted_tail_bounds':weighted,
       'active_moment_tail_bounds':active_moment,'inactive_moment_leading_bound':inactive_moment_leading,
       'inactive_moment_integral_bounds':inactive_moment_integral,'moment_tail_bounds':moment_tail,
       'active_target_sixth_tail':active_target,'inactive_Gamma_sixth_tail':inactive_gamma,
       'inactive_Xi_sixth_tail':inactive_Xi,'inactive_objective_sixth_tail':inactive_objective,
       'target_sixth_tail':target_tail,'dual_eighth_tail':dual8_tail,
       'moment_fourth_bounds':H,'repair_contraction':contraction,'repair_forcing':forcing,
       'K6_global':K6,'Kdual6':Kdual,'Kprimal6':Kprimal,'amplitude_upper':U,
       'lower_endpoint_coefficient':lower_endpoint_coefficient,'upper_endpoint_margin':upper_endpoint_margin,
       'auxiliary_derivative_lower':auxiliary_derivative_lower,'inversion_derivative_lower':Fderivative,
       'Kpoly':Kpoly,'Kminus':Kminus,'Kplus':Kplus,'positive_quartic_dominance_margin':dominance,
       'published_constants':['9.593e-54','1.488e-53'],
       'scope':'For every M>=2e-5 at fixed exact Q: -9.593e-54/M^6 < delta(M)-delta0-C2/M^2-C4/M^4 < 1.488e-53/M^6. Adaptive finite prefixes with uniform active/inactive weighted tails. No C6 limit, exact finite-M optimizer or cusp-uniform result claimed.'})
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    d=produce();a.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'])
    for k in ['target_sixth_tail','dual_eighth_tail','Kdual6','Kprimal6','upper_endpoint_margin','Kminus','Kplus']:print(k,d[k]['enclosure'])
if __name__=='__main__':main()
