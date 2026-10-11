#!/usr/bin/env python3
"""Exact identities behind the finite-window error bounds; no numerical fitting."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'finite_slope_fourth_order'))
from check_fourth_order import P,var
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
    checks=[]
    def ck(name,value):
        assert value,name
        checks.append({'name':name,'passed':True})
    a,k,y,r,t,u,v,Q,dp=[var(i) for i in range(9)];h=k*a*a+a*y
    for n in range(1,7):
        expected=sum((F(math.comb(n,j),j+1)*k**(n-j)*a**(2*n-j) for j in range(0,n+1,2)),P(0))
        ck('symmetric_averaged_power_'+str(n),(h**n).average(2)==expected)
    fourth=var(7)
    local=(-r*h**2-t*h**3/3-u*h**4/12-fourth*h**5/60).average(2)
    leading=-r*a*a/3-a**4*(r*k*k+t*k/3+u/60)
    rest=-t*k**3*a**6/3-u*(2*k*k*a**6+k**4*a**8)/12-fourth*(k*a**6+F(10,3)*k**3*a**8+k**5*a**10)/60
    ck('residual_primitive_remainder_powers',local==leading+rest)
    kap=(Q*v-t/6)/r
    ck('trial_balance_quadratic_cancellation',r*kap+t/6-Q*v==0)
    for sig in [-1,1]:
        L=-2*sig*Q*kap-sig*dp/3
        GG=2*Q**2/(sig*r);BB=sig*(Q*t/r-dp)/3
        RR=t*t/(36*sig*r)-sig*u/60
        A4=-sig*(r*kap*kap+t*kap/3+u/60)
        ck('finite_trial_fourth_identity_'+str(sig),A4-v*L==RR+GG*v*v/2-BB*v)
    x,tt,ee=[var(i) for i in range(3)];p=1+tt*x+(3*tt*tt-ee)*x*x
    inv=p-tt*x*p**3+ee*x*x*p**5-1
    ck('amplitude_residual_starts_at_cube',inv.trunc(0,2)==0)
    wrong=1+tt*x+(tt*tt-ee)*x*x
    ck('missing_feedback_negative_control',(wrong-tt*x*wrong**3+ee*x*x*wrong**5-1).trunc(0,2)!=0)
    d,g,m=var(0),var(1),var(2)
    ck('support_gap_completed_square',g*d-m*d*d==g*g/(4*m)-m*(d-g/(2*m))**2)
    ck('fifth_derivative_theta_series_ratio',F(14,13)**14/F(2)**81<F(1,2))
    ck('integrated_tail_decay',600-(3+9+36)>540)
    return {'status':'R25_exact_remainder_identities_passed','source_sha256':sha(__file__),
      'helper_sha256':sha(HERE.parent/'finite_slope_fourth_order/check_fourth_order.py'),
      'check_groups':len(checks),'checks':checks,'formal_proof':False}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    data=run();a.output.write_text(json.dumps(data,indent=2)+'\n');print(data['status'],data['check_groups'])
if __name__=='__main__':main()
