"""Extended correlated enclosures and the fourth fold-transport derivative."""
import hashlib
import json
import sys
from math import factorial
from pathlib import Path
from flint import arb
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_geometry'))
from geometry_model import restore,serialize,upper,zero_ball,signed_powers
from width_shape import Polynomial
from bridge_taylor import operator_powers
from validated_flow import derivative,absolute_derivative_bounds

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify_inputs():
    out=[]
    for name in ('cusp_verified','cusp_region','cusp_connection','cusp_geometry'):
        base=HERE.parent/name;mp=base/'manifest.json';data=json.loads(mp.read_text())
        for entry in data['files']:
            if sha(base/entry['path'])!=entry['sha256']:
                raise ArithmeticError(f'Input changed: {name}/{entry["path"]}')
        out.append({'package':name,'manifest_sha256':sha(mp),'verified_files':len(data['files'])})
    return out

class ExtendedCell:
    """R04's correlation-preserving formula with derivative orders through 26."""
    def __init__(self,old,geometry,index):
        self.index=index;self.old=old;self.geometry=geometry
        self.x=list(map(restore,old['center']))
        self.nu=restore(old['driver_center'])
        self.v=list(map(restore,old['predictor']))
        self.h=restore(old['driver_half_width'])
        self.tight=list(map(restore,old['tight_root_radii']))
        self.allowed=list(map(restore,old['majorant_domain_half_widths']))
        self.c=list(map(restore,old['central_derivatives']+geometry['extra_central_derivatives']))
        self.B=list(map(restore,old['absolute_derivative_bounds']+geometry['extra_absolute_bounds']))
        self.K=8;self.nmax=26
        self.A=operator_powers({1:self.v[0],2:-self.v[1]/4,4:self.v[2]/16,6:-arb(1)/64},self.K)
        for n in range(57,69):
            self.c.append(derivative(self.x[0],{1:self.x[1],2:self.x[2],3:self.nu},n))
        params={1:self.x[1]+zero_ball(self.allowed[1]),
                2:self.x[2]+zero_ball(self.allowed[2]),3:self.nu+zero_ball(self.allowed[3])}
        extended=absolute_derivative_bounds(params,74)
        self.B.extend(extended[63:75])

    def enclose(self,extra=(0,0,0),upto=26):
        if len(extra)!=3 or any(not arb(v).is_finite() or not arb(v)>=0 for v in extra):
            raise ValueError('Invalid neighborhood widths')
        if not 0<=upto<=self.nmax:raise ValueError('Invalid derivative order')
        z=zero_ball(self.h)
        balls=[zero_ball(upper(r+arb(e))) for r,e in zip(self.tight,extra)]
        if any(not upper(abs(self.v[i]*z))+upper(abs(balls[i]))<self.allowed[i] for i in range(3)):
            raise ValueError('Enclosure leaves majorant domain')
        W=operator_powers({1:balls[0],2:-balls[1]/4,4:balls[2]/16},self.K)
        zp=signed_powers(z,self.K);out=[];rems=[]
        for n in range(upto+1):
            value=arb(0);rem=arb(0)
            for p in range(self.K+1):
                for q in range(self.K+1-p):
                    fac=factorial(p)*factorial(q)
                    if p+q<self.K:
                        value+=zp[p]/fac*sum((w*sum((a*self.c[n+s+r] for r,a in self.A[p].items()),arb(0))
                                              for s,w in W[q].items()),arb(0))
                    else:
                        rem+=self.h**p/fac*sum((abs(w)*sum((abs(a)*self.B[n+s+r]
                                   for r,a in self.A[p].items()),arb(0)) for s,w in W[q].items()),arb(0))
            rem=upper(rem);out.append(value+zero_ball(rem));rems.append(rem)
        return out,rems

class Dual:
    def __init__(self,value,grad=None):
        self.value=value;self.grad=list(grad) if grad is not None else [arb(0)]*9
    @staticmethod
    def of(v):return v if isinstance(v,Dual) else Dual(arb(v))
    def __add__(self,other):
        b=self.of(other);return Dual(self.value+b.value,[a+c for a,c in zip(self.grad,b.grad)])
    __radd__=__add__
    def __neg__(self):return Dual(-self.value,[-v for v in self.grad])
    def __sub__(self,other):return self+-self.of(other)
    def __rsub__(self,other):return self.of(other)+-self
    def __mul__(self,other):
        b=self.of(other);return Dual(self.value*b.value,[a*b.value+self.value*c for a,c in zip(self.grad,b.grad)])
    __rmul__=__mul__

def numerator4(ds):
    """B''''(0) = -2 N4/(D3^3 D4^4), at fixed driver on the fold."""
    a,b,c,d,e,f,g,h,i=ds
    T=a*b*f+b*c*d-b*b*e-a*d*d
    U=c*d-b*e
    P3=b*T-c*a*U+e*a*a*d-g*a*a*b
    P4=c*T-d*a*U+f*a*a*d-h*a*a*b
    P5=d*T-e*a*U+g*a*a*d-i*a*a*b
    return a*a*(b*P5-c*P4)-b*b*(a*P4-b*P3)

def partials4(ds):
    return numerator4([Dual(v,[arb(k==j) for k in range(9)]) for j,v in enumerate(ds)]).grad

def fourth_at_cusp(cell,cusp):
    scale=cell.c[3].mid()
    if not scale>0:raise ArithmeticError('Positive scale required')
    polys=[];errs=[]
    for n in range(3,12):
        polys.append(Polynomial([sum((a*cell.c[n+s] for s,a in cell.A[p].items()),arb(0))
                         /(factorial(p)*scale) for p in range(8)]))
        errs.append(upper(cell.h**8/factorial(8)*sum((abs(a)*cell.B[n+s]
                         for s,a in cell.A[8].items()),arb(0))/scale))
    polynomial=numerator4(polys)
    pred=polynomial.c[0]+zero_ball(sum((abs(a)*cell.h**k for k,a in enumerate(polynomial.c) if k),arb(0)))
    ds=[v/scale for v in cusp]
    grad=partials4([ds[n]+zero_ball(errs[n-3]) for n in range(3,12)])
    jet_error=upper(sum((abs(a)*e for a,e in zip(grad,errs)),arb(0)))
    grad=partials4(ds[3:12])
    chain=[sum((grad[n-3]*ds[n+shift]*factor for n in range(3,12)),arb(0))
           for shift,factor in ((1,arb(1)),(2,-arb(1)/4),(4,arb(1)/16))]
    root_error=upper(sum((abs(a)*r for a,r in zip(chain,cell.tight)),arb(0)))
    N=pred+zero_ball(jet_error+root_error)
    a,b=ds[3],ds[4]
    B4=-2*N/(a*a*a*b*b*b*b)
    return {'B4':B4,'N4':N,'scale':scale,'polynomial_coefficients':polynomial.c,
            'jet_remainders':errs,'jet_error':jet_error,'root_error':root_error,'spatial_gradient':chain}
