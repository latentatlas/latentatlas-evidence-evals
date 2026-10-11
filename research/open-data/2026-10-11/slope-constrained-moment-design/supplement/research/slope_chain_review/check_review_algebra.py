#!/usr/bin/env python3
"""R17 targeted checks independent of the R15/R16 interval helper.

Exact differentiation of polynomial/trigonometric density jets, direct
piecewise step integrals, absorption algebra, and dyadic B nonsingularity.
These finite checks do not formalize the analytic infinite-switch proof.
"""
import sys
sys.dont_write_bytecode = True
import argparse, hashlib, json
from fractions import Fraction as Q
from pathlib import Path
HERE = Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(*polys):
    out = {}
    for p in polys:
        for k, v in p.items(): out[k] = out.get(k, Q(0)) + v
    return {k: v for k, v in out.items() if v}
def scale(p, s): return {k: s*v for k, v in p.items() if s*v}
def mul(p, q):
    out = {}
    for x, a in p.items():
        for y, b in q.items():
            k = tuple(i+j for i, j in zip(x, y))
            out[k] = out.get(k, Q(0)) + a*b
    return {k: v for k, v in out.items() if v}
def derivative(p):
    # Keys: u power, frequency power, derivative order of density, cos/sin.
    terms = []
    for (u, k, w, trig), c in p.items():
        if u: terms.append({(u-1,k,w,trig):c*u})
        terms.append({(u,k,w+1,trig):c})
        terms.append({(u,k+1,w,1-trig):c*(-1 if trig==0 else 1)})
    return add(*terms)
def integral(p, left, right):
    return sum(c*(right**(n+1)-left**(n+1))/Q(n+1) for (n,),c in p.items())
def exact_ball(v):
    m,e=v['mid_man_exp'];r,_=v['rad_man_exp'];assert r==0
    return Q(m)*Q(2)**e

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not sys.flags.optimize and not args.output.exists()
    checks=[]
    # Treat phase offset as constant: the formulas hold for every j*pi/2.
    for n in range(4):
        q={(n,0,0,0):Q(2**n)}
        first={(n,0,1,0):Q(2**n),(n,1,0,1):Q(-2**n)}
        second={(n,0,2,0):Q(2**n),(n,1,1,1):Q(-2**(n+1)),(n,2,0,0):Q(-2**n)}
        if n:
            first[(n-1,0,0,0)]=Q(n*2**n)
            second[(n-1,0,1,0)]=Q(2*n*2**n)
            second[(n-1,1,0,1)]=Q(-2*n*2**n)
        if n>=2: second[(n-2,0,0,0)]=Q(n*(n-1)*2**n)
        assert derivative(q)==first
        assert derivative(derivative(q))==second
        checks.extend([f'q_{n} first derivative',f'q_{n} second derivative'])
    # Integrate actual ramp minus unit step on both half intervals.
    piecewise=[]
    for n in range(7):
        left={(n+1,):Q(1,2),(n,):Q(1,2)}
        right={(n+1,):Q(1,2),(n,):Q(-1,2)}
        value=integral(left,Q(-1),Q(0))+integral(right,Q(0),Q(1))
        expected=Q(0) if n%2==0 else -Q(1,(n+1)*(n+2))
        assert value==expected
        piecewise.append(str(value));checks.append(f'direct piecewise step moment degree {n}')
    assert piecewise[1]=='-1/6'
    # Independent polynomial identity for the absorption of e=alpha-delta.
    # Symbols: D, delta, Gamma, U, x=1/M, A3, A4.
    def t(i): return {tuple(int(j==i) for j in range(7)):Q(1)}
    one={(0,)*7:Q(1)}
    D,d,G,U,x,A3,A4=[t(i) for i in range(7)]
    def power(p,n):
        ans=one
        for _ in range(n):ans=mul(ans,p)
        return ans
    denominator=add(D,scale(mul(G,mul(power(U,2),power(x,2))),-1))
    numerator=add(scale(mul(G,mul(power(d,3),power(x,2))),Q(1,3)),
        mul(A3,mul(power(U,4),power(x,3))),mul(A4,mul(power(U,5),power(x,4))))
    after=add(mul(D,numerator),scale(mul(scale(mul(G,power(d,3)),Q(1,3)),mul(power(x,2),denominator)),-1))
    claimed=add(mul(D,mul(A3,mul(power(U,4),power(x,3)))),
        mul(D,mul(A4,mul(power(U,5),power(x,4)))),
        scale(mul(power(G,2),mul(power(U,2),mul(power(d,3),power(x,4)))),Q(1,3)))
    assert after==claimed;checks.append('upper remainder absorption identity')
    # Pair integration in normalized v in [0,1].
    assert integral({(1,):Q(2),(2,):Q(-2)},Q(0),Q(1))==Q(1,3)
    assert integral({(2,):Q(-1),(3,):Q(1)},Q(0),Q(1))==-Q(1,12)
    checks.extend(['lower leading pair coefficient','lower Taylor-error pair coefficient'])
    cp=HERE.parent/'kernel_slope_remainder/results/remainder_certificate.json'
    c=json.loads(cp.read_text());B=[list(map(exact_ball,row)) for row in c['preconditioner']]
    det=sum((1 if (i,j,k) in [(0,1,2),(1,2,0),(2,0,1)] else -1)*B[0][i]*B[1][j]*B[2][k]
        for i in range(3) for j in range(3) for k in range(3) if len({i,j,k})==3)
    assert det!=0;checks.append('exact dyadic preconditioner nonsingularity')
    out=dict(status='targeted_independent_exact_review_passed',source_sha256=sha(__file__),
        certificate_sha256=sha(cp),check_count=len(checks),checks=checks,
        unit_step_monomial_integrals=piecewise,preconditioner_determinant_sign=1 if det>0 else -1,
        preconditioner_determinant_numerator_sha256=hashlib.sha256(str(det.numerator).encode()).hexdigest(),
        scope='Finite derivative, factor and algebra checks. No new research theorem or coefficient; '
        'no formal verification of regularity, infinite tails, IFT or Banach arguments.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
