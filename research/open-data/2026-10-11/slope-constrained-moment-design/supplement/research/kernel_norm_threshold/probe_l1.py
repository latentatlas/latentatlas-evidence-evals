#!/usr/bin/env python3
"""Exploratory floating-point L1 optimization. No certification claims."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode=True
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE=Path(__file__).resolve().parent
QP=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json'


def midpoint(v):
    m,e=v['mid_man_exp'];return float(m*2.0**e)


class Model:
    def __init__(self):
        self.q=json.loads(QP.read_text())
        self.t,self.lam,self.mu=map(midpoint,self.q['center_exact_dyadic'])
        self.x,self.w=leggauss(48)
        self.grid=np.linspace(0,2,32769)

    def rho(self,u):
        u=np.asarray(u);e4=np.exp(4*u)
        phi=sum((2*np.pi**2*k**4*np.exp(9*u)-3*np.pi*k*k*np.exp(5*u))*np.exp(-np.pi*k*k*e4) for k in range(1,9))
        return phi*np.exp(self.lam*u*u+self.mu*u**4)

    def p(self,u,nmax=3):
        u=np.asarray(u);z=2*self.t*u
        c,s=np.cos(z),np.sin(z);trig=(c,-s,-c,s)
        return np.array([(2*u)**j*trig[j%4] for j in range(nmax+1)])

    def residual(self,u,a):
        p=self.p(u);return p[3]-np.einsum('i,i...->...',a,p[:3])

    def dr(self,u,a):
        u=np.asarray(u);z=2*self.t*u
        A=8*u**3+2*a[1]*u;B=4*a[2]*u*u-a[0]
        return (24*u*u+2*a[1]-2*self.t*B)*np.sin(z)+(2*self.t*A+8*a[2]*u)*np.cos(z)

    def roots(self,a):
        r=self.residual(self.grid,a)
        idx=np.where(r[:-1]*r[1:]<0)[0]
        lo,hi=self.grid[idx].copy(),self.grid[idx+1].copy()
        sign=np.sign(r[idx])
        for _ in range(45):
            mid=(lo+hi)/2;test=np.sign(self.residual(mid,a))==sign
            lo=np.where(test,mid,lo);hi=np.where(test,hi,mid)
        return (lo+hi)/2

    def evaluate(self,a):
        roots=self.roots(a);ends=np.r_[0,roots,2]
        lo,hi=ends[:-1],ends[1:]
        u=(lo[:,None]+hi[:,None])/2+(hi-lo)[:,None]*self.x/2
        w=self.w[None,:]*(hi-lo)[:,None]/2*self.rho(u)
        p=self.p(u,8);sgn=np.sign(self.residual((lo+hi)/2,a))
        S=np.einsum('kij,ij,i->k',p,w,sgn)
        D=S[3]-a@S[:3]
        pr=self.p(roots);weights=2*self.rho(roots)/np.abs(self.dr(roots,a))
        H=np.einsum('ik,jk,k->ij',pr[:3],pr[:3],weights)
        return {'a':a,'roots':roots,'D':D,'S':S,'H':H}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    m=Model()
    u=(m.x+1)/2;w=m.w/2*m.rho(u);p=m.p(u)
    A=np.einsum('ik,jk,k->ij',p[:3],p[:3],w);b=np.einsum('ik,k,k->i',p[:3],p[3],w)
    a=np.linalg.solve(A,b)
    history=[]
    for iteration in range(60):
        e=m.evaluate(a);norm=float(np.max(np.abs(e['S'][:3])))
        history.append({'iteration':iteration,'a':a.tolist(),'D':float(e['D']),'moment_residual':norm,'roots':len(e['roots'])})
        if norm<1e-15:break
        step=np.linalg.solve(e['H'],e['S'][:3])
        old=e['D'];scale=1.0
        while scale>2**-35:
            trial=a+scale*step;n=m.evaluate(trial)
            if n['D']<=old-1e-5*scale*(e['S'][:3]@step) or np.max(np.abs(n['S'][:3]))<norm/2:
                a=trial;break
            scale/=2
        else:raise ArithmeticError('Probe line search failed')
    e=m.evaluate(a)
    jp=HERE.parent/'cusp_shape_design/results/local_jets.json';f=json.loads(jp.read_text())
    F3=midpoint(f['F_at_exact_Q'][3]);delta=F3/e['D']
    out={'status':'floating_point_exploration_only','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'Q_certificate_sha256':hashlib.sha256(QP.read_bytes()).hexdigest(),
         'center':[m.t,m.lam,m.mu],'a':a.tolist(),'D':float(e['D']),'norm_estimate':float(delta),
         'S':e['S'].tolist(),'roots_0_2':e['roots'].tolist(),'hessian':e['H'].tolist(),'history':history,
         'scope':'Numpy quadrature and sign-change root search only. This is neither a root completeness proof nor a norm certificate.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:out[k] for k in ('status','a','D','norm_estimate','S')},indent=2))


if __name__=='__main__':main()
