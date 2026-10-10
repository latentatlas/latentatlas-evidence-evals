#!/usr/bin/env python3
"""Independent mpmath checks of selected direct oscillatory integrals.

No FLINT or generating implementation is imported. These are numerical
precision checks, not rigorous quadrature or a replacement for the proof.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
import mpmath as mp
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def midpoint(v):
    a,e=v['mid_man_exp'];return mp.mpf(a)*mp.power(2,e)
def endpoints(v):
    r,e=v['rad_man_exp'];r=mp.mpf(r)*mp.power(2,e);m=midpoint(v)
    return m-r,m+r


def direct(data,design,n,dps):
    with mp.workdps(dps):
        t,lam,mu=map(midpoint,data['center'])
        ws=list(map(midpoint,design['weights']));frequencies=design['frequencies']
        p=mp.pi
        def integrand(u):
            e4,e5,e9=mp.exp(4*u),mp.exp(5*u),mp.exp(9*u)
            phi=mp.fsum((2*p*p*k**4*e9-3*p*k*k*e5)*mp.exp(-p*k*k*e4) for k in range(1,17))
            h=mp.fsum(w*mp.cos(2*j*u) for j,w in zip(frequencies,ws))
            phase=2*t*u
            trig=(mp.cos(phase),-mp.sin(phase),-mp.cos(phase),mp.sin(phase))[n%4]
            return phi*mp.exp(lam*u*u+mu*u**4)*h*(2*u)**n*trig
        return mp.quad(integrand,[mp.mpf(j)/8 for j in range(17)])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    mp.mp.dps=125;start=time.monotonic()
    jp=HERE/'results/local_jets.json';dp=HERE/'results/design_certificate.json'
    data=json.loads(jp.read_text());design=json.loads(dp.read_text());rows=[]
    for n in range(9):
        a=direct(data,design,n,90);b=direct(data,design,n,115)
        lo,hi=endpoints(data['H_at_center'][n]);difference=abs(a-b)
        if not (lo<b<hi and difference<mp.mpf('1e-80')):
            raise ArithmeticError('Independent integral disagreement at order '+str(n))
        rows.append({'order':n,'dps':[90,115],'value':mp.nstr(b,108),
                     'precision_difference':mp.nstr(difference,15),'inside_rigorous_center_ball':True})
        print('Separate direct moment',n,'passed',flush=True)
    result={'status':'9_independent_direct_moments_at_two_precisions_passed',
        'rows':rows,'input_sha256':{'local_jets.json':sha(jp),'design_certificate.json':sha(dp)},
        'source_sha256':sha(__file__),
        'trust_boundary':'Numerical midpoint checks, with the same N=16 finite series and U=2 cutoff. No rigorous mpmath remainder claim. The primary Arb moment enclosures include truncation tails, exact weight uncertainty and exact-Q uncertainty where indicated.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')


if __name__=='__main__':main()
