#!/usr/bin/env python3
"""Exact rational identities behind the sharp asymptotic coefficient."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
def clean(p):return {k:Q(v) for k,v in p.items() if v}
def add(p,q):
    out=dict(p)
    for k,v in q.items():out[k]=out.get(k,0)+v
    return clean(out)
def scale(p,s):return clean({k:s*v for k,v in p.items()})
def mul(p,q):
    out={}
    for a,x in p.items():
        for b,y in q.items():
            k=tuple(i+j for i,j in zip(a,b));out[k]=out.get(k,0)+x*y
    return clean(out)
def diff(p,j=0):return clean({tuple(e-(i==j) for i,e in enumerate(k)):v*k[j] for k,v in p.items() if k[j]})
def term(*e):return {e:Q(1)}
def integral01(p):return sum(v/Q(k[0]+1) for k,v in p.items())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    x=term(1);one=term(0)
    def T(p):return add(mul(add(scale(one,5),scale(x,-4)),p),scale(mul(x,diff(p)),4))
    P0=add(scale(x,2),scale(one,-3));P1=T(P0);P2=T(P1)
    assert P1=={(0,):Q(-15),(1,):Q(30),(2,):Q(-8)}
    assert P2=={(0,):Q(-75),(1,):Q(330),(2,):Q(-224),(3,):Q(32)}
    A=add(scale(term(3,0,0,0),8),scale(term(1,0,1,0),2))
    B=add(scale(term(2,0,0,1),4),scale(term(0,1,0,0),-1))
    phase=add(mul(A,diff(B)),scale(mul(B,diff(A)),-1))
    expected={(4,0,0,1):Q(-32),(2,0,1,1):Q(8),(2,1,0,0):Q(24),(0,1,1,0):Q(2)}
    assert phase==expected
    # Pairwise Lipschitz defect integrated against a simple crossing.
    v_one_minus_v=add(x,scale(term(2),-1));pair_loss=2*integral01(v_one_minus_v)
    assert pair_loss==Q(1,3)
    # Uniform-box smoothing of a unit step against q(x)=x.
    smoothing_linear=-integral01(v_one_minus_v);assert smoothing_linear==Q(-1,6)
    # On [-1,1], r(u)=u,w=1 and clipped-ramp sign: D=1 and
    # integral u*clip(u/a,-1,1)=2*(a^2/3+(1-a^2)/2)=1-a^2/3.
    toy_coefficient=2*(Q(1,3)-Q(1,2));assert toy_coefficient==Q(-1,3)
    # With amplitude δ and a=δ/M: f=δ-δ^3/(3M^2), so the leading
    # coefficient in δ=f+C/M^2+... is C=f^3/3, as the theorem predicts.
    out=dict(status='exact_rational_asymptotic_identities_passed',source_sha256=sha(__file__),
        identities=['first theta derivative polynomial','second theta derivative polynomial','tail phase numerator',
            'paired simple-crossing loss coefficient 1/3','unit-step moment loss coefficient -1/6','exact clipped-ramp toy moment'],
        paired_loss_coefficient=str(pair_loss),unit_step_linear_moment_coefficient=str(smoothing_linear),
        toy_moment='f=delta-delta^3/(3M^2)',
        scope='Exact finite algebra and integrals of polynomials; not a verification of the implicit-function or infinite-series analytic proof.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
