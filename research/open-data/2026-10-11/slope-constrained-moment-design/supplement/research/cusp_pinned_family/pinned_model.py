"""R08 exact R07 kernel direction. New outputs only, frozen inputs read-only."""
from pathlib import Path
import hashlib
import json
import sys
sys.dont_write_bytecode=True
from flint import arb,acb,arb_mat
HERE=Path(__file__).resolve().parent
for name in ('cusp_verified','cusp_connection','cusp_geometry','cusp_width'):
    sys.path.insert(0,str(HERE.parent/name))
from validated_flow import (finite_kernel,series_tail,domain_tail,absolute_derivative_bounds,
                            upper,zero_ball,serialize,midpoint_inverse,matvec,norm_vec,norm_mat,matmul)
from explore import restore,J
from certify_connection import cusp_tangent
from width_shape import numerator


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pack(v):
    if isinstance(v,arb):return serialize(v)
    if isinstance(v,list):return [pack(x) for x in v]
    if isinstance(v,dict):return {k:pack(x) for k,x in v.items()}
    return v
def verify_inputs():
    out=[]
    for name in ('cusp_verified','cusp_region','cusp_connection','cusp_geometry','cusp_width','cusp_literature','cusp_robustness'):
        base=HERE.parent/name;m=json.loads((base/'manifest.json').read_text())
        for r in m['files']:
            if sha(base/r['path'])!=r['sha256']:raise ArithmeticError('Frozen input changed: '+name+'/'+r['path'])
        out.append({'package':name,'files':len(m['files']),'manifest_sha256':sha(base/'manifest.json')})
    return out


class Kernel:
    def __init__(self):
        self.pinned_path=HERE.parent/'cusp_robustness/results/pinned_cusp_certificate.json'
        self.pinned=json.loads(self.pinned_path.read_text())
        self.weights=list(map(restore,self.pinned['weights']))
        self.q=json.loads((HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json').read_text())
    def derivative(self,x,nu,n,eps=None,*,kind='G',tol='1e-70',N=16,U=2,pieces=8):
        if kind not in ('F','H','G'):raise ValueError('Invalid derivative kind')
        if kind=='G' and eps is None:raise ValueError('G requires epsilon')
        t,lam,mu=map(arb,x);nu=arb(nu);eps=arb(eps or 0)
        params={1:lam,2:mu,3:nu};cut=arb(U)
        factor=arb(1) if kind in ('F','H') else 1+upper(abs(eps))
        tail=upper(factor*(series_tail(params,n,cut,N)+domain_tail(params,n,cut)))
        def f(u,analytic):
            if not (4*u).exp().real>0:return acb('nan','nan')
            P=acb(lam)*u*u+acb(mu)*u**4+acb(nu)*u**6
            h=sum((acb(w)*(2*j*u).cos() for j,w in enumerate(self.weights,1)),acb(0)) if kind!='F' else acb(0)
            mult=acb(1) if kind=='F' else h if kind=='H' else 1+acb(eps)*h
            z=2*acb(t)*u;trig=(z.cos(),-z.sin(),-z.cos(),z.sin())[n%4]
            return finite_kernel(u,N)*P.exp()*(2*u)**n*trig*mult
        value=acb(0)
        for k in range(pieces):
            value+=acb.integral(f,acb(cut*k/pieces),acb(cut*(k+1)/pieces),
                               abs_tol=arb(tol)/pieces,rel_tol=arb(tol),eval_limit=100000)
        if not value.is_finite():raise ArithmeticError('Nonfinite rigorous integral')
        return value.real+zero_ball(tail)
    def cache(self,x,nu,nmax,eps=None,**kw):
        return [self.derivative(x,nu,n,eps,**kw) for n in range(nmax+1)]
    def refine(self,seed,nu,eps,target='1e-48'):
        x=[arb(v).mid() for v in seed]
        for k in range(12):
            d=self.cache(x,nu,6,eps);Y=midpoint_inverse(J(d));change=matvec(Y,d[:3]);error=norm_vec(change)
            if error<arb(target):
                d.extend(self.derivative(x,nu,n,eps) for n in range(7,11))
                return x,d,Y,error,k
            if not error.is_finite() or error>2:raise ArithmeticError('Newton correction outside diagnostic range')
            x=[(a-b).mid() for a,b in zip(x,change)]
        raise ArithmeticError('Newton diagnostic did not converge')


def opening(d):
    a,b=d[3],d[4];scale=a.mid();s=[v/scale for v in d]
    kp=numerator(s[3:11])/(64*s[3]*s[3]*s[4]*s[4]*s[4])
    return -8*arb(2).sqrt()*a/(3*b),8*arb(2).sqrt()*kp/3
