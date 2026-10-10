#!/usr/bin/env python3
"""Exact cofactor identity, rational finite-amplitude check, direct numerics."""
import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
import mpmath as mp
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Run without -O/-OO')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_width'))
from check_width import D,read


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def det(a):return sum((a[0][j]*(a[1][(j+1)%3]*a[2][(j+2)%3]-a[1][(j+2)%3]*a[2][(j+1)%3]) for j in range(3)),D(0))
def point(v):
    a,e=v['mid_man_exp'];return mp.mpf(a)*mp.power(2,e)
def sign(p):return (-1)**sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))


def exact_identity():
    for row in range(3):
        terms={}
        for omit in range(4):
            cols=[j for j in range(4) if j!=omit]
            for p in itertools.permutations(range(3)):
                monomial=tuple(sorted([4*row+omit]+[4*i+cols[p[i]] for i in range(3)]))
                terms[monomial]=terms.get(monomial,0)+(-1)**omit*sign(p)
        assert all(v==0 for v in terms.values())
    return 'All three degree-four cofactor identities vanish by exact integer monomial cancellation.'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();mp.mp.dps=105
    path=HERE/'results/pinned_cusp_certificate.json';cert=json.loads(path.read_text())
    oldpath=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';old=json.loads(oldpath.read_text())
    assert sha(oldpath)==cert['quartic_certificate_sha256']
    for name,h in cert['source_sha256'].items():assert sha(HERE/name)==h
    identity=exact_identity()
    M=[[read(v) for v in row] for row in cert['moments']]
    alpha=[(-1)**j*det([[M[n][k] for k in range(4) if k!=j] for n in range(3)]) for j in range(4)]
    assert all(a.hi<0 if j%2==0 else a.lo>0 for j,a in enumerate(alpha))
    norm=sum(((-a if j%2==0 else a) for j,a in enumerate(alpha)),D(0));assert norm.lo>0
    weights=[a/norm for a in alpha]
    force=[sum((w*v for w,v in zip(weights,row)),D(0)) for row in M]
    d=list(map(read,old['root_derivative_enclosures']))
    for value in force[:3]:assert value.lo<=0<=value.hi
    ratio=[(force[n]/d[n]).abs_upper() for n in (3,4)]
    assert all(v<D.of('0.401').lo for v in ratio)
    assert (d[3]+D(-force[3].abs_upper()/2,force[3].abs_upper()/2)).lo>0
    assert (d[4]+D(-force[4].abs_upper()/2,force[4].abs_upper()/2)).hi<0
    # At u=pi/2, cos(2*j*u)=(-1)^j has the cofactor signs:
    # hence h(pi/2)=sum |w|=1 exactly, so the L-infinity norm is one.
    t,lam,mu=map(point,old['center_exact_dyadic']);w=list(map(point,cert['weights']));pi=mp.pi
    rows=[]
    for n in range(5):
        def f(u):
            phi=mp.fsum((2*pi*pi*k**4*mp.exp(9*u)-3*pi*k*k*mp.exp(5*u))*mp.exp(-pi*k*k*mp.exp(4*u)) for k in range(1,13))
            h=mp.fsum(wj*mp.cos(2*j*u) for j,wj in enumerate(w,1))
            return phi*mp.exp(lam*u*u+mu*u**4)*h*(2*u)**n*mp.cos(2*t*u+n*pi/2)
        value=mp.quad(f,[mp.mpf(k)/16 for k in range(33)],method='gauss-legendre')
        error=abs(value-point(cert['moment_response'][n]))
        assert error<mp.mpf('1e-75')
        if n<3:assert abs(value)<mp.mpf('1e-75')
        rows.append({'order':n,'direct_moment':mp.nstr(value,90),'difference':mp.nstr(error,10)})
        print('Pinned direction direct moment',n,'passed',flush=True)
    result={'status':'exact_identity_rational_bounds_and_numerical_check_passed',
        'certificate_sha256':sha(path),'source_sha256':sha(Path(__file__)),
        'exact_symbolic_identity':identity,'h_sup_norm':'exactly 1; attained at u=pi/2',
        'amplitude_interval':['-1/2','1/2'],'readable_response_ratio_upper':'0.401 for both D3 and D4',
        'readable_nondegeneracy_factor':'D3_epsilon >= 0.7995 D3_original > 0; |D4_epsilon| >= 0.7995 |D4_original| > 0',
        'rows':rows,'numerical_method':'mpmath 105 dps; 12 terms, [0,2], 32 Gauss-Legendre panels; numerical support, not a second interval proof.',
        'trust_boundary':'Saved original and shifted-frequency Arb integral enclosures are inputs; cofactor signs, nonlinear normalization and finite-amplitude inequalities are separately checked with rational intervals.',
        'scope':'One explicit direction; one fixed cusp Q in nu=0. No large-amplitude assertion for the whole arc, fold transport or the full finite root window.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')


if __name__=='__main__':main()
