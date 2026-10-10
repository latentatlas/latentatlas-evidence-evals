#!/usr/bin/env python3
"""Independent exact algebra for EXISTING R01--R12 formulas.

Does not import research generators. FLINT multivariate rational polynomials
are used only for exact coefficient arithmetic, not floating-point sampling.
"""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
from math import factorial
from pathlib import Path
from flint import fmpq, fmpq_mpoly_ctx

HERE=Path(__file__).resolve().parent
CTX=fmpq_mpoly_ctx.get([f'D{i}' for i in range(3,23)]+[f'R{i}' for i in range(9)],ordering='lex')
V=CTX.gens()

class R:
    def __init__(self,n=0,d=1):
        if isinstance(n,R): self.n,self.d=n.n,n.d;return
        self.n=CTX.constant(n) if isinstance(n,(int,fmpq)) else n
        self.d=CTX.constant(d) if isinstance(d,(int,fmpq)) else d
        assert self.d!=0
        if self.n==0:self.d=CTX.constant(1)
        else:
            g=self.n.gcd(self.d)
            self.n=self.n/g;self.d=self.d/g
    def __add__(self,b):
        b=R(b);return R(self.n*b.d+b.n*self.d,self.d*b.d)
    __radd__=__add__
    def __neg__(self):return R(-self.n,self.d)
    def __sub__(self,b):return self+-R(b)
    def __rsub__(self,b):return R(b)+-self
    def __mul__(self,b):
        b=R(b);return R(self.n*b.n,self.d*b.d)
    __rmul__=__mul__
    def __truediv__(self,b):
        b=R(b);return R(self.n*b.d,self.d*b.n)
    def __rtruediv__(self,b):return R(b)/self
    def __pow__(self,k):
        assert isinstance(k,int) and k>=0
        return R(self.n**k,self.d**k)
    def __eq__(self,b):
        b=R(b);return self.n*b.d==b.n*self.d
    def partial(self,j):
        return R(self.n.derivative(j)*self.d-self.n*self.d.derivative(j),self.d**2)
    def __str__(self):return f'({self.n}) / ({self.d})'

D=[R(0)]*3+[R(v) for v in V[:20]]
RR=[R(v) for v in V[20:]]
checks=[]
def same(name,a,b):
    assert a==b,name
    checks.append(name)

def det(a):
    if len(a)==1:return a[0][0]
    return sum(((-1)**j)*a[0][j]*det([r[:j]+r[j+1:] for r in a[1:]]) for j in range(len(a)))

a,b,c,d,e,f,g,h,i=D[3:12]
tp=None
mp=-16*RR[0]/b
lp=(4*RR[1]+c*mp/4)/a
tp=(-RR[2]+b*lp/4-d*mp/16)/a
for n in range(3):same(f'general cusp tangent equation {n}',D[n+1]*tp-D[n+2]*lp/4+D[n+4]*mp/16,-RR[n])
dot=[RR[n]+D[n+1]*tp-D[n+2]*lp/4+D[n+4]*mp/16 for n in range(6)]
kp=(a*dot[4]-dot[3]*b)/(b*b)
A3p=R(4)/3*((dot[5]*b-c*dot[4])/(b*b)-(dot[4]*a-b*dot[3])/(a*a))
U=b*RR[1]-c*RR[0]
Vv=-a*b*RR[2]+b*b*RR[1]+(a*d-b*c)*RR[0]
P3=a*a*b*RR[3]+b*Vv-a*c*U-a*a*e*RR[0]
P4=a*a*b*RR[4]+c*Vv-a*d*U-a*a*f*RR[0]
P5=a*a*b*RR[5]+d*Vv-a*e*U-a*a*g*RR[0]
same('R08 general opening polynomial',kp,(a*P4-b*P3)/(a*a*b*b*b))
N4=a*a*(b*P5-c*P4)-b*b*(a*P4-b*P3)
same('R08 general fourth transport polynomial',96*(-a/b)*A3p,-128*N4/(a**3*b**4))

nu_mp=d/(4*b);nu_lp=(4*c*nu_mp-e)/(16*a)
nu_tp=(f/64+b*nu_lp/4-d*nu_mp/16)/a
ndot=[D[n+1]*nu_tp-D[n+2]*nu_lp/4+D[n+4]*nu_mp/16-D[n+6]/64 for n in range(6)]
nk=(a*ndot[4]-ndot[3]*b)/(b*b)
NN=(a*c-b*b)*(a*b*f+b*c*d-b*b*e-a*d*d)+(b*c-a*d)*(c*d-b*e)*a+(a*f-b*e)*d*a*a+(b*g-a*h)*a*a*b
same('R04 nu opening polynomial',nk,NN/(64*a*a*b*b*b))
TT=a*b*f+b*c*d-b*b*e-a*d*d;UU=c*d-b*e
NP3=b*TT-c*a*UU+e*a*a*d-g*a*a*b
NP4=c*TT-d*a*UU+f*a*a*d-h*a*a*b
NP5=d*TT-e*a*UU+g*a*a*d-i*a*a*b
for k,p in zip((3,4,5),(NP3,NP4,NP5)):same(f'R05 cusp total derivative D{k}',ndot[k],p/(64*a*a*b))
NA3p=R(4)/3*((ndot[5]*b-c*ndot[4])/(b*b)-(ndot[4]*a-b*ndot[3])/(a*a))
NN4=a*a*(b*NP5-c*NP4)-b*b*(a*NP4-b*NP3)
same('R05 fourth transport polynomial',96*(-a/b)*NA3p,-2*NN4/(a**3*b**4))

K=4
def mul(x,y):return [sum((x[j]*y[k-j] for j in range(k+1)),R(0)) for k in range(K+1)]
def powers(x):
    ans=[[R(1)]+[R(0)]*K]
    for j in range(K):ans.append(mul(ans[-1],x))
    return ans
def compose(ds,n,ls,ms):
    ll=powers([-v/4 for v in ls]);mm=powers([v/16 for v in ms]);out=[R(0)]*(K+1)
    for p in range(K+1):
        for q in range((K-p)//2+1):
            for r in range((K-p-2*q)//2+1):
                z=mul(ll[q],mm[r]);coef=ds[n+p+2*q+4*r]/(factorial(p)*factorial(q)*factorial(r))
                for k in range(p,K+1):out[k]+=coef*z[k-p]
    return out
ls=[R(0)]*(K+1);ms=[R(0)]*(K+1)
for k in range(2,K+1):
    residual0=compose(D,0,ls,ms)[k]
    residual1=compose(D,1,ls,ms)[k]
    ms[k]=-16*residual0/b
    ls[k]=(4*residual1+c*ms[k]/4)/a
same('fold lambda quadratic',ls[2],2)
same('fold mu quadratic',ms[2],0)
same('fold lambda cubic',ls[3],R(4)/3*(c/b-b/a))
same('fold mu cubic',ms[3],16*a/(3*b))
same('fold mu quartic is exactly -4',ms[4],-4)
for n in (0,1):
    series=compose(D,n,ls,ms)
    for k in range(K+1):same(f'implicit fold equation {n}, coefficient {k}',series[k],0)
gd2=compose(D,2,ls,ms);gd4=compose(D,4,ls,ms)
# Generic R jets need only eight orders here. Add one unused variable to
# retain the same complete monomial loop as the G composition.
r0=compose(RR+[R(0)]*14,0,ls,ms)
bb=[R(0)]*(K+1)
for k in range(K+1):bb[k]=(4*lp*gd2[k]-16*r0[k]-sum((gd4[j]*bb[k-j] for j in range(1,k+1)),R(0)))/gd4[0]
same('transport B(0)',bb[0],mp)
same('transport B first derivative',bb[1],0)
same('transport B second derivative',2*bb[2],0)
same('transport B third derivative',6*bb[3],-32*kp)
same('transport B fourth derivative',24*bb[4],96*(-a/b)*A3p)

same('triple-zero cusp Jacobian',det([[D[n+1],-D[n+2]/4,D[n+4]/16] for n in range(3)]),a*a*b/64)
G=[R(0)]*4+D[4:]
same('order-four three-control determinant',det([[-G[n+2]/4,G[n+4]/16,-G[n+6]/64] for n in range(3)]),b*(b*e-c*d)/4096)

out={'status':'all_exact_symbolic_identities_passed','identities':checks,
     'count':len(checks),'method':'Exact multivariate rational polynomial arithmetic; identically zero differences, not finitely many numerical test vectors.',
     'scope':'Existing R01/R04/R05/R08 cusp/fold/transport and R09--R12 rank formulas. Does not verify transcendental integrals or inequalities.',
     'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(HERE/'symbolic_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
