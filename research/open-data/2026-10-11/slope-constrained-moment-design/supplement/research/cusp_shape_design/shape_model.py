"""R09 direct kernel integrals and local Taylor bounds at the exact pinned Q."""
import json,sys
from math import factorial
from flint import arb,acb
sys.dont_write_bytecode=True
from moment_dictionary import HERE,restore,pack,upper,zero_ball,sha
from pinned_model import Kernel as OldKernel
from validated_flow import finite_kernel,series_tail,domain_tail,absolute_derivative_bounds
from certify_design import need


class Kernel(OldKernel):
    def __init__(self):
        self.design_path=HERE/'results/design_certificate.json';self.design=json.loads(self.design_path.read_text())
        self.weights=list(map(restore,self.design['weights']));self.freq=self.design['frequencies']
        self.q=json.loads((HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json').read_text())
    def derivative(self,x,nu,n,eps=None,*,kind='G',tol='1e-83',N=16,U=2,pieces=16):
        need(kind in ('F','H','G'),'Unknown integral kind')
        t,lam,mu=map(arb,x);nu=arb(nu);eps=arb(0) if eps is None else arb(eps);cut=arb(U)
        params={1:lam,2:mu,3:nu};factor=1+upper(abs(eps)) if kind=='G' else arb(1)
        tail=upper(factor*(series_tail(params,n,cut,N)+domain_tail(params,n,cut)))
        def fun(u,analytic):
            if not (4*u).exp().real>0:return acb('nan','nan')
            h=sum((acb(w)*(2*j*u).cos() for j,w in zip(self.freq,self.weights)),acb(0)) if kind!='F' else acb(0)
            mult=acb(1) if kind=='F' else h if kind=='H' else 1+acb(eps)*h
            z=2*acb(t)*u;trig=(z.cos(),-z.sin(),-z.cos(),z.sin())[n%4]
            return finite_kernel(u,N)*(acb(lam)*u*u+acb(mu)*u**4+acb(nu)*u**6).exp()*(2*u)**n*trig*mult
        total=acb(0)
        for j in range(pieces):
            total+=acb.integral(fun,acb(cut*j/pieces),acb(cut*(j+1)/pieces),
                abs_tol=arb(tol)/pieces,rel_tol=arb(tol),eval_limit=100000)
        need(total.is_finite(),'Nonfinite integral')
        return total.real+zero_ball(tail)


class LocalTaylor:
    def __init__(self,data,amplitude):
        self.F=list(map(restore,data['F_at_exact_Q']));self.H=list(map(restore,data['H_at_exact_Q']))
        self.B=list(map(restore,data['absolute_F_bounds']));self.eps=arb(amplitude)
        self.c=[f+self.eps*h for f,h in zip(self.F,self.H)]
        self.mult=1+upper(abs(self.eps));self.terms=[]
        self.domain=list(map(restore,data['local_majorant_domain']))
        for a in range(9):
            for b in range(9-a):
                for c in range(9-a-b):
                    self.terms.append((a,b,c,a+2*b+4*c,arb(1)/(factorial(a)*factorial(b)*factorial(c))))
    def enclose(self,extra,upto):
        rt,rl,rm=map(arb,extra)
        need(rl<self.domain[1] and rm<self.domain[2],'Local box outside majorant domain')
        g=[];h=[]
        for n in range(upto+1):
            rg,rh=arb(0),arb(0)
            for a,b,c,j,f in self.terms:
                order=a+b+c
                if not order:continue
                coeff=rt**a*(rl/4)**b*(rm/16)**c*f
                if order<8:
                    rg+=coeff*abs(self.c[n+j]);rh+=coeff*abs(self.H[n+j])
                else:
                    rg+=coeff*self.mult*self.B[n+j];rh+=coeff*self.B[n+j]
            g.append(self.c[n]+zero_ball(rg));h.append(self.H[n]+zero_ball(rh))
        return g,h
