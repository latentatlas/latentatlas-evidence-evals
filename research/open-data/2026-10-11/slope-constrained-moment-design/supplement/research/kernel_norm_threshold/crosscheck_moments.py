#!/usr/bin/env python3
"""Separate mpmath quadrature of fixed sign-template moments, not smooth spikes."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode=True
import mpmath as mp
HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def midpoint(v):
    m,e=v['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)


def numerical(c,n,dps):
    with mp.workdps(dps):
        t,lam,mu=map(midpoint,c['center'])
        ends=[mp.mpf(0)]+list(map(midpoint,c['breakpoints']))+[mp.mpf(1)]
        def fun(u):
            phi=sum((2*mp.pi**2*k**4*mp.exp(9*u)-3*mp.pi*k*k*mp.exp(5*u))*mp.exp(-mp.pi*k*k*mp.exp(4*u)) for k in range(1,13))
            phase=2*t*u+n*mp.pi/2
            return phi*mp.exp(lam*u*u+mu*u**4)*(2*u)**n*mp.cos(phase)
        values=[c['initial_sign']*(-1)**i*mp.quadgl(fun,[l,r]) for i,(l,r) in enumerate(zip(ends[:-1],ends[1:]))]
        return +mp.fsum(values)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();path=HERE/'results/threshold_certificate.json';c=json.loads(path.read_text())
    rows=[]
    for n in (0,3,4):
        a,b=numerical(c,n,50),numerical(c,n,80)
        with mp.workdps(110):
            difference=abs(a-b)
            if not difference<mp.mpf('1e-45'):raise ArithmeticError('Numerical precision agreement failed')
            v=c['step_moments_at_exact_Q'][n];mid=midpoint(v);r,e=v['rad_man_exp'];rad=mp.mpf(r)*mp.power(2,e)
            if not abs(b-mid)<=rad:raise ArithmeticError('Separate numerical value outside certified moment')
            rows.append({'order':n,'precisions':[50,80],'value':mp.nstr(b,78),'precision_difference':mp.nstr(difference,15),'inside_certified_interval':True})
        print('Separate moment',n,'passed',flush=True)
    out={'status':'three_step_moments_two_precision_independent_quadrature_passed','source_sha256':sha(__file__),
         'certificate_sha256':sha(path),'rows':rows,'elapsed_seconds':time.monotonic()-start,
         'method':'mpmath Gauss-Legendre on the 29 exact dyadic sign-template intervals; 12 theta terms, cutoff 1. The certificate uses Arb with 8 terms and analytic tails.',
         'scope':'Numerical corroboration of step moments at the dyadic center. Not an independent rigorous integration, a direct evaluation of the smoothed multiplier, or an exact pinning proof.'}
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(out['status'])


if __name__=='__main__':main()
