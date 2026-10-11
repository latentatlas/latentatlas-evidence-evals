#!/usr/bin/env python3
"""R26 independent rational reconstruction of all new global constants."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'theta_fourth_order'))
from rational_intervals import RI,restore,BITS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def U(x):return RI(x).hi
def sm(xs):return sum(xs,RI(0))
def au(x):return RI(x).abs_upper()
def run(new,old,alg):
    eps=RI(F(alg['epsilon']));a0=RI(F(alg['a_max']));V=list(map(F,alg['v_absolute_bounds']))
    co={k:restore(x) for k,x in old['coefficient_inputs'].items()};checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append(name)
    ck('tail_gap_sign',restore(new['tail_gap_raw_residual']).lo>0)
    for j,bound in enumerate([F('.001'),F('.1'),F('.005')]):
        ck('expanded_coefficient_'+str(j),au(restore(old['expanded_trial_dual_box'][j]))<bound)
        ck('v_component_'+str(j),au(restore(old['v_enclosure'][j]))<V[j])
    S={d:restore(new['weighted_tail_bounds'][str(d)]['root_sum']) for d in [12,16,24]}
    I={d:restore(new['weighted_tail_bounds'][str(d)]['integral']) for d in [12,16,24]}
    Hc=list(map(F,alg['active_moment_constants']));Cs=F(alg['active_residual_sixth_constant']);C8=F(alg['active_dual_eighth_constant'])
    hm=[U(Hc[j]*S[12]) for j in range(3)]
    hl=U(188/eps**2*S[12]);hI=[U(2**(j+1)/eps**4/(1-48*a0)*I[16]) for j in range(3)]
    htail=[U(RI(hm[j])+hl+hI[j]) for j in range(3)]
    active=U(Cs*S[16]+sm(V[j]*RI(hm[j]) for j in range(3)))
    gamma=U(300/eps**4*S[16]);Xi=U(2071000/eps**2*S[16]);objective=U(18/eps**6/(1-72*a0)*I[24])
    tail=U(RI(active)+gamma+Xi+objective);d8=U(C8*S[24])
    ck('global_target_tail_small',0<tail<F('8.411e-35'))
    ck('global_support_tail_small',0<d8<F('3.366e-40'))
    H=[U(restore(old['moment_fourth_bounds_finite'][j])+htail[j]) for j in range(3)]
    C=[[restore(x) for x in row] for row in old['moment_preconditioner']];W=list(map(restore,old['repair_scaled_box']))
    contraction=list(map(restore,old['repair_contraction']))
    forcing=[U(sm(au(C[i][j])*RI(H[j]) for j in range(3))/W[i]) for i in range(3)]
    for i in range(3):ck('global_moment_repair_'+str(i),contraction[i].hi+forcing[i]<1)
    K6=U(restore(old['K6_finite'])+tail)
    Kd=U(K6+a0**2*(restore(old['K8dual'])+d8));Kp=U(K6+a0**2*restore(old['K8primal']))
    f,delta,D,Gamma,Xi=[co[k] for k in ['f','delta0','D','Gamma','Xi']]
    M=RI(F('2e-5'));amp=restore(old['amplitude_upper'])
    low=(Gamma/3-Xi*delta**2/M**2).lo
    high=(amp-delta-Gamma*amp**3/(3*D*M**2)-Kp*amp**7/(D*M**6)).lo
    gd=(D-Gamma*amp**2/M**2-7*Kp*amp**6/M**6).lo
    fd=(D-Gamma*amp**2/M**2).lo
    ck('lower_scalar_endpoint',low>0)
    ck('upper_scalar_endpoint_all_M',high>0)
    ck('auxiliary_scalar_monotonicity',gd>0)
    ck('inverse_monotonicity',fd>0)
    ck('width_valid_for_all_M',U(amp/M)<a0.lo)
    ck('positive_kernel',amp.hi<1)
    ck('approximation_within_amplitude_interval',U(delta+co['C2']/M**2+co['C4']/M**4)<amp.lo)
    km=U((restore(old['Kpoly'])+Kd*amp**7)/fd);kp=U((restore(old['Kpoly'])+Kp*amp**7)/fd)
    ck('published_global_lower_bound',0<km<F('9.593e-54'))
    ck('published_global_upper_bound',0<kp<F('1.488e-53'))
    ck('explicit_positive_correction_onset',(co['C4']-RI(F('9.593e-54'))/M**2).lo>0)
    return {'status':'R26_rational_global_inequalities_passed','rounding_bits':BITS,'checks':checks,'check_count':len(checks),
       'target_sixth_tail_upper':str(tail),'dual_eighth_tail_upper':str(d8),
       'moment_tail_uppers':list(map(str,htail)),'repair_forcing_uppers':list(map(str,forcing)),
       'Kminus_upper':str(km),'Kplus_upper':str(kp),'upper_scalar_endpoint_margin':str(high),
       'source_sha256':sha(__file__),'rational_helper_sha256':sha(HERE.parent/'theta_fourth_order/rational_intervals.py'),
       'trust_boundary':'Independent rational reconstruction of the new weighted-tail combination, contraction and scalar inequalities. Transcendental weighted-tail bounds and inherited finite-root bounds are accepted as explicit inputs; the analytic adaptive-prefix proof is not mechanically verified.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    op=HERE.parent/'theta_effective_remainder/results/certificate.json';alg=HERE/'results/algebra.json'
    d=run(json.loads(a.certificate.read_text()),json.loads(op.read_text()),json.loads(alg.read_text()))
    d['certificate_sha256']=sha(a.certificate);d['R25_certificate_sha256']=sha(op);d['algebra_sha256']=sha(alg)
    a.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['check_count'])
    print('target tail',float(F(d['target_sixth_tail_upper'])),'Kminus',float(F(d['Kminus_upper'])),'Kplus',float(F(d['Kplus_upper'])))
if __name__=='__main__':main()
