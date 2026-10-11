#!/usr/bin/env python3
"""Independent real-axis perturbation integral and rational sensitivity check.

The mpmath calculation is numerical support, not a rigorous enclosure.
The sensitivity bounds are checked separately with rational intervals.
"""
import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction as Q
from pathlib import Path
import mpmath as mp
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_width'))
from check_width import D,read


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def point(v):
    a,e=v['mid_man_exp'];return mp.mpf(a)*mp.power(2,e)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    if not __debug__:raise RuntimeError('Run without -O/-OO')
    start=time.monotonic();mp.mp.dps=105
    path=HERE/'results/condition_witness.json';cert=json.loads(path.read_text())
    oldpath=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';old=json.loads(oldpath.read_text())
    assert sha(oldpath)==cert['quartic_certificate_sha256']
    for name,h in cert['source_sha256'].items():assert sha(HERE/name)==h
    a,lam,mu=map(point,old['center_exact_dyadic']);pi=mp.pi
    def moment(n):
        def integrand(u):
            phi=mp.fsum((2*pi*pi*k**4*mp.exp(9*u)-3*pi*k*k*mp.exp(5*u))*mp.exp(-pi*k*k*mp.exp(4*u)) for k in range(1,13))
            return phi*mp.exp(lam*u*u+mu*u**4)*mp.cos(2*a*u)*(2*u)**n*mp.cos(2*a*u+n*pi/2)
        return mp.quad(integrand,[mp.mpf(k)/16 for k in range(33)],method='gauss-legendre')
    rows=[]
    for n in range(3):
        value=moment(n);expected=point(cert['forcing_at_cusp'][n]);error=abs(value-expected)
        assert error<mp.mpf('1e-80'),(n,mp.nstr(error))
        rows.append({'order':n,'direct_perturbation_integral':mp.nstr(value,92),'difference_to_shifted_arb_midpoint':mp.nstr(error,10)})
        print('Direct mpmath perturbation moment',n,'agrees within 1e-80',flush=True)
    d=list(map(read,old['root_derivative_enclosures']));r=list(map(read,cert['forcing_at_cusp']))
    mp1=-16*r[0]/d[4];lp1=(4*r[1]+d[5]*mp1/4)/d[3]
    tp1=(-r[2]+d[4]*lp1/4-d[6]*mp1/16)/d[3]
    readable=((-Q(27775)*10**7,-Q(27773)*10**7),(Q(53155)*10**7,Q(53157)*10**7),(Q(49259)*10**7,Q(49261)*10**7))
    for v,(lo,hi) in zip((tp1,lp1,mp1),readable):assert lo<v.lo<=v.hi<hi
    # The frequency identity is the exact product-to-sum cosine identity.
    # For constant h, the perturbation forcing at a cusp is identically zero.
    const_mu=D(0)/d[4];const_lam=(D(0)+d[5]*const_mu/4)/d[3]
    const_t=(D(0)+d[4]*const_lam/4-d[6]*const_mu/16)/d[3]
    assert all(v.lo==v.hi==0 for v in (const_t,const_lam,const_mu))
    result={'status':'rational_sensitivity_and_independent_numerical_agreement',
        'condition_certificate_sha256':sha(path),'source_sha256':sha(Path(__file__)),
        'method':'mpmath 105 decimal digits; direct cos-modulated kernel, 12 kernel terms on [0,2], 32 Gauss-Legendre panels. Numerical check only; original Arb certificate handles all tails.',
        'rows':rows,'readable_derivative_bounds':[[str(x),str(y)] for x,y in readable],
        'constant_kernel_multiplier_invariance':'zero cusp derivative checked with rational intervals',
        'scope':'Infinitesimal direction at epsilon=0; no claim of a finite breakdown threshold.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')


if __name__=='__main__':main()
