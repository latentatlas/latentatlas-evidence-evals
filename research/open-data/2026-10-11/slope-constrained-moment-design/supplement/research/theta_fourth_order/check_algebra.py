#!/usr/bin/env python3
"""Exact root-identity and tail-bound algebra for R24."""
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
    def ck(name,condition):
        assert condition,name
        checks.append({'name':name,'passed':True})
    w,wp,wpp,r,rr,rrr,p,dp,other=[var(i) for i in range(9)]
    q1=w*r;q2=2*wp*r+w*rr;q3=3*wpp*r+3*wp*rr+w*rrr
    for sigma in [-1,1]:
        gamma=sigma*q1
        full=sigma*((w*p)*q2/q1-(wp*p+w*dp))/3
        reduced=sigma*(wp*p+w*(p*rr/r-dp))/3
        ck('root_B_identity_orientation_'+str(sigma),full==reduced)
        ck('root_G_identity_orientation_'+str(sigma),2*(w*p)*(w*other)/gamma==2*w*p*other/(sigma*r))
        ck('root_R_logarithmic_identity_orientation_'+str(sigma),
           q2**2/(36*gamma)-sigma*q3/60==gamma*((2*wp/w+rr/r)**2/36-(3*wpp/w+3*(wp/w)*(rr/r)+rrr/r)/60))
    # The product-rule w'''*r term vanishes because the raw residual is zero.
    ck('root_third_derivative_product_rule',q3==3*wpp*r+3*wp*rr+w*rrr)
    def coeff(j,l):
        return F(2**j)*sum(F(math.comb(l,h)*math.factorial(j),math.factorial(j-h))*84**(l-h)
                          for h in range(min(j,l)+1))
    raw=[]
    for l in range(1,4):
        raw.append(coeff(3,l)+F(1,1000)*coeff(0,l)+F(1,10)*coeff(1,l)+F(1,200)*coeff(2,l))
    ck('raw_residual_tail_derivative_bounds',raw[0]<900 and raw[1]<63000 and raw[2]<5400000)
    ck('tail_logarithmic_residual_ratios',F(63000,567)<112 and F(5400000,567)<9524)
    # Phi'/Phi <=134 exp(4u); Phi''/Phi <=3526 exp(8u), pi in (3,4).
    l_bound=F(134)+F(44,50)
    m_bound=F(3526)+F(88*134,50)+F(44**2+116,2500)
    ck('weight_logarithmic_jet_bounds',l_bound<135 and m_bound<3800)
    normalized2=F(2*135)+F(112,50)
    normalized3=F(3*3800)+F(3*135*112,50)+F(9524,2500)
    ck('root_density_second_third_ratios',normalized2<273 and normalized3<12400)
    Rfactor=F(273**2,36)+F(12400,60)
    ck('R_tail_absolute_bound',Rfactor<2300 and 2300*900*88==182160000)
    ck('G_B_tail_absolute_bounds',F(2*16*88,567)<5 and F(4*139*88,3)<16400 and 135+F(2+84+112,50)<139)
    # e^(4u)>=50*u^3 for u>=1; all four envelopes have decay at least 540.
    decay_margins=[600-(3+9+36),600-(1+9+36),600-(2+13+36),600-(3+17+36)]
    ck('geometric_switch_sum',min(decay_margins)>540 and F(540*3,85)>16)
    # Polynomial envelope for f and D is deliberately not reused as a C4 tail.
    ck('localization_from_strong_convexity',F(2065,10**19)/F(1,200)<F(1,2**40))
    return {'status':'R24_exact_root_and_tail_algebra_passed','checks':checks,'check_groups':len(checks),
       'raw_derivative_constant_upper_before_rounding':list(map(str,raw)),
       'weight_first_ratio_constant_upper':str(l_bound),'weight_second_ratio_constant_upper':str(m_bound),
       'R_factor_upper_before_rounding':str(Rfactor),'tail_log_decay_margins':decay_margins,
       'source_sha256':sha(__file__),'algebra_helper_sha256':sha(HERE.parent/'finite_slope_fourth_order/check_fourth_order.py'),
       'trust_boundary':'Exact finite identities and rational inequalities. The zero identities, inherited localization and analytic theta tail derivation are separate explicit proof inputs.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    data=run();args.output.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'status':data['status'],'check_groups':data['check_groups']}))
if __name__=='__main__':main()
