"""Cusp-centered local bounds built on the frozen R03 continuation."""
import hashlib
import json
import sys
from math import factorial
from pathlib import Path
from flint import arb,ctx

HERE=Path(__file__).resolve().parent
CONNECTION=HERE.parent/'cusp_connection'
BASE=HERE.parent/'cusp_verified'
sys.path.insert(0,str(CONNECTION))
from explore import restore,point_cache
from bridge_taylor import operator_powers
from validated_flow import (upper,zero_ball,serialize,derivative,
                            absolute_derivative_bounds)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify_inputs():
    out=[]
    for name in ('cusp_verified','cusp_region','cusp_connection'):
        directory=HERE.parent/name
        manifest=json.loads((directory/'manifest.json').read_text())
        for entry in manifest['files']:
            if sha(directory/entry['path'])!=entry['sha256']:
                raise ArithmeticError(f'Input changed: {name}/{entry["path"]}')
        out.append({'package':name,'manifest_sha256':sha(directory/'manifest.json'),
                    'verified_files':len(manifest['files'])})
    return out


def signed_powers(x,K):
    row=[arb(1)]
    for _ in range(K): row.append(row[-1]*x)
    return row


class CorrelatedCell:
    """For delta=(v*z+w,z), keep z correlation before interval bounds.

    Powers use exp(z*A+W) through total degree K-1. The Kth directional
    remainder is bounded on the original larger R03 majorant domain.
    """
    def __init__(self,cell,index):
        self.cell,self.index=cell,index
        self.c=list(map(restore,cell['central_derivatives']))
        self.B=list(map(restore,cell['absolute_derivative_bounds']))
        self.x=list(map(restore,cell['center']))
        self.nu=restore(cell['driver_center'])
        self.v=list(map(restore,cell['predictor']))
        self.h=restore(cell['driver_half_width'])
        self.tight=list(map(restore,cell['tight_root_radii']))
        self.allowed=list(map(restore,cell['majorant_domain_half_widths']))
        self.K=8
        self.A=operator_powers({1:self.v[0],2:-self.v[1]/4,
                               4:self.v[2]/16,6:-arb(1)/64},self.K)
        # Six extra integral orders suffice for derivatives through D14.
        for n in range(51,57):
            self.c.append(derivative(self.x[0],{1:self.x[1],2:self.x[2],3:self.nu},n))
        params={1:self.x[1]+zero_ball(self.allowed[1]),
                2:self.x[2]+zero_ball(self.allowed[2]),
                3:self.nu+zero_ball(self.allowed[3])}
        extended=absolute_derivative_bounds(params,62)
        self.B.extend(extended[57:63])

    def enclose(self,extra=(0,0,0),upto=10,z=None):
        z=zero_ball(self.h) if z is None else arb(z)
        if not z.is_finite() or not upper(abs(z))<=self.allowed[3]:
            raise ValueError('Driver leaves majorant domain')
        if not 0<=upto<=14: raise ValueError('Derivative order outside model')
        radii=[upper(a+arb(b)) for a,b in zip(self.tight,extra)]
        if len(radii)!=3 or any(not r>0 for r in radii):
            raise ValueError('Invalid local radii')
        balls=[zero_ball(r) for r in radii]
        if any(not upper(abs(self.v[i]*z))+upper(abs(balls[i]))<self.allowed[i] for i in range(3)):
            raise ValueError('Local box leaves majorant domain')
        W=operator_powers({1:balls[0],2:-balls[1]/4,4:balls[2]/16},self.K)
        zp=signed_powers(z,self.K)
        # For each p,q group combine the exact predictor coefficients
        # against central derivative balls BEFORE applying W and z.
        out=[];rems=[]
        for n in range(upto+1):
            value=arb(0);rem=arb(0)
            for p in range(self.K+1):
                for q in range(self.K+1-p):
                    fac=factorial(p)*factorial(q)
                    if p+q<self.K:
                        value+=zp[p]/fac*sum((w*sum((a*self.c[n+s+r]
                            for r,a in self.A[p].items()),arb(0))
                            for s,w in W[q].items()),arb(0))
                    else:
                        rem+=upper(abs(z))**p/fac*sum((abs(w)*sum((abs(a)*self.B[n+s+r]
                            for r,a in self.A[p].items()),arb(0))
                            for s,w in W[q].items()),arb(0))
            rem=upper(rem)
            out.append(value+zero_ball(rem));rems.append(rem)
        return out,rems


class LocalCusp:
    """Bounds relative to the exact cusp, at fixed nu.

    c[0:3] are zero by the R03 theorem. b[n] enclose D_n in the
    entire local box. Taylor in t, followed by second-order parameter
    remainder, avoids any approximate substitution for the exact cusp.
    """
    def __init__(self,c,b,limits):
        self.c=list(c);self.c[:3]=[arb(0)]*3
        self.b=list(b);self.limits=list(map(arb,limits))

    def axis(self,n,s):
        # Taylor through derivative 5, with sixth derivative remainder.
        if not 0<=n<=5: raise ValueError('Axis order unsupported')
        sp=signed_powers(s,6-n)
        val=sum((sp[k]*self.c[n+k]/factorial(k) for k in range(6-n)),arb(0))
        # Integral remainder preserves sign if s is an exact signed point.
        return val+sp[6-n]*self.b[6]/factorial(6-n)

    def evaluate(self,n,s,l,m):
        s,l,m=map(arb,(s,l,m))
        if any(not v.is_finite() or not upper(abs(v))<=a
               for v,a in zip((s,l,m),self.limits)):
            raise ValueError('Request leaves cusp-centered box')
        if n in (0,1):
            value=self.axis(n,s)-l/4*self.axis(n+2,s)+m/16*self.axis(n+4,s)
            # Ordinary two-parameter Taylor remainder along the segment.
            al,am=upper(abs(l))/4,upper(abs(m))/16
            rem=upper((al*al*abs(self.b[n+4])
                +2*al*am*abs(self.b[n+6])
                +am*am*abs(self.b[n+8]))/2)
            return value+zero_ball(rem)
        if n==2:
            return s*self.b[3]-l/4*self.b[4]+m/16*self.b[6]
        return self.b[n]

    def derivatives(self,s,l,m,upto=6):
        return [self.evaluate(n,s,l,m) for n in range(upto+1)]
