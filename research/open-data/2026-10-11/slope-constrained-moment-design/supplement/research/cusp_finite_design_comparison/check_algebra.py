#!/usr/bin/env python3
"""Exact extensions of R26 tail constants to a R29 negative-sextic arc."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def produce():
    parent=HERE.parent/'theta_global_remainder/results/algebra.json';old=json.loads(parent.read_text())
    eps=F(old['epsilon']);a0=F(old['a_max']);width=F(1,64);V=[F(5),F(4),F(180)];prior=list(map(F,old['v_absolute_bounds']))
    checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append({'name':name,'passed':True})
    ck('u5_over_exp4u',sum(F(5)**k/math.factorial(k) for k in range(8))>40*F(5,4)**5)
    potential=[F(44,50)+6*width/40,F(116+30*width,50**2),F(216+120*width,50**3),
               F(216+360*width,50**4),720*width/50**5]
    for i,b in enumerate(potential,1):ck('sextic_potential_derivative_'+str(i),0<b<1)
    pj=[list(map(F,row)) for row in old['p_derivative_constants']]
    q=[list(map(F,row)) for row in old['q_relative_constants']]
    weighted=sum(V[j]*2**j for j in range(3));vs=sum(V)
    ck('expanded_root_motion_and_kappa',weighted/F(567)<2)
    ck('expanded_raw_value',2700*(1+3*a0)**3+weighted*(1+3*a0)**2*a0<2800)
    ck('expanded_raw_derivative_perturbation',a0*a0*sum(V[j]*pj[j][1] for j in range(3))*(1+3*a0)**2<1)
    ck('inactive_leading_188',187+F(32,567)*vs/50<188)
    ck('inactive_fourth_2071000',2070000+F(16,567)*vs*vs/2500+187*vs/50<2071000)
    K=F(46);Ch=F(old['active_balance_fourth_constant'])
    Ch+=sum((V[j]-prior[j])*(q[j][1]*K+4*q[j][2]*(F(1,3)+K*K*eps*eps)) for j in range(3))/50
    ck('enlarged_balance_constant',Ch>F(old['active_balance_fourth_constant']))
    return {'status':'R30_exact_sextic_tail_extension_passed','checks':checks,'check_groups':len(checks),
       'inherited_R26_check_groups':old['check_groups'],'driver_width':str(width),'epsilon':str(eps),'a_max':str(a0),
       'v_absolute_bounds':list(map(str,V)),'potential_relative_bounds':list(map(str,potential)),
       'active_moment_constants':old['active_moment_constants'],'active_residual_sixth_constant':old['active_residual_sixth_constant'],
       'active_balance_fourth_constant':str(Ch),'active_dual_eighth_constant':str(Ch*Ch/200),
       'R26_algebra_sha256':sha(parent),'source_sha256':sha(__file__),
       'trust_boundary':'Exact added inequalities. The R26 polynomial and weighted-tail proof is inherited; nu<=0 preserves its upper density envelope.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    d=produce();args.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['check_groups'])
if __name__=='__main__':main()
