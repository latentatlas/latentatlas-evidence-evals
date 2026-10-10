#!/usr/bin/env python3
"""Exact rational guards for the larger negative-sextic domain and cover."""
import sys
sys.dont_write_bytecode=True
import argparse,json,hashlib,math
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def produce():
    checks=[]
    def ck(name,value):
        assert value,name
        checks.append({'name':name,'passed':True})
    H=F(1,64);h=F(1,4096)
    ck('exact_cover_length',32*2*h==H)
    ck('enlargement_factor',H/F(1,65536)==1024)
    ck('coarse_attempt_is_covered',F(1,512)<H)
    ck('u5_over_exp4u',sum(F(5)**k/math.factorial(k) for k in range(8))>40*F(5,4)**5)
    p=[F(44,50)+6*H/40,F(116+30*H,50**2),F(216+120*H,50**3),F(216+360*H,50**4),720*H/50**5]
    for i,x in enumerate(p,1):ck('sextic_potential_derivative_'+str(i),0<x<1)
    rho=F(1,1000);c=3*(1-4*rho)-2/(1-4*rho)
    ck('weighted_asymptotic_coercivity',c>F(97,100))
    ck('new_weighted_polynomial_degree',3*18==54)
    lo,hi=F('1.9e-40'),F('5.3e-40')
    ck('anchored_coefficient_lower',F('2.49203004e-39')-H*hi==F('2.48374879e-39'))
    ck('endpoint_gain_lower',H*lo==F('2.96875e-42'))
    ck('endpoint_gain_upper',H*hi==F('8.28125e-42'))
    return {'status':'R29_exact_domain_and_scope_checks_passed','checks':checks,'check_count':len(checks),
      'potential_relative_bounds':list(map(str,p)),'weighted_decay_factor_lower':str(c),
      'driver_interval':['-1/64','0'],'enlargement_factor':1024,
      'endpoint_gain_bounds':['2.96875e-42','8.28125e-42'],
      'source_sha256':sha(__file__),
      'R28_derivative_algebra_sha256':sha(HERE.parent/'cusp_coefficient_motion/results/algebra.json'),
      'scope':'R28 derivative identities and envelopes inherited unchanged; potential derivative bounds extended to |nu|<=1/64. No finite-M remainder constant is extended.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
    d=produce();a.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['check_count'])
if __name__=='__main__':main()
