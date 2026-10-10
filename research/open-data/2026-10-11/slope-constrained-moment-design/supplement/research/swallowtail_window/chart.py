"""An explicit affine plotting chart in the original mu/nu control plane.

Not a Weierstrass coordinate change. Linear directions are exact dyadics;
their leading contributions are combined before interval evaluation.
"""
from model_v2 import *


class Chart:
    def __init__(self,data,cert):
        self.model=Model(data);self.L=arb(2)**-24;self.r=arb(2)**-12
        self.E=[[restore(v) for v in row] for row in cert['fold_surface']['Y']]
        self.alpha=arb(-4).union(arb(4));self.beta=(-arb(3)/2).union(arb(11)/2)
        self.cache={};p=self.parameters(self.alpha,self.beta);self.maxp=[upper(abs(v)) for v in p]
        need(all(v<arb(2)**-34 for v in self.maxp),'Chart leaves physical control box')
        self.bounds=self.model.derivatives([zero_ball(3*self.r),self.L]+[zero_ball(v) for v in self.maxp],12)
        for n in (13,14):
            rad=3*self.r*self.model.B[n+1]+self.L*self.model.B[n+2]/4+self.maxp[0]*self.model.B[n+4]/16+self.maxp[1]*self.model.B[n+6]/64
            self.bounds.append(self.model.c[n]+zero_ball(rad))
    def parameters(self,alpha,beta):
        v=[self.L*self.L*(beta-arb(3)/4),self.r**3*alpha]
        return matvec(self.E,v)
    def axis(self,s):
        key=(s.mid().man_exp(),s.rad().man_exp())
        if key not in self.cache:self.cache[key]=self.model.derivatives([s,self.L,0,0],8)
        return self.cache[key]
    def value(self,s,alpha,beta,n=0):
        need(n<=2,'Chart derivative order')
        s,alpha,beta=map(arb,(s,alpha,beta));need(abs(s)<=3*self.r,'Chart s range')
        axis=self.axis(s)
        sa=self.r**3*(self.E[0][1]*axis[n+4]/16-self.E[1][1]*axis[n+6]/64)
        sb=self.L*self.L*(self.E[0][0]*axis[n+4]/16-self.E[1][0]*axis[n+6]/64)
        value=axis[n]+sa*alpha+sb*(beta-arb(3)/4)
        p=self.parameters(alpha,beta);u=upper(abs(p[0]))/16;v=upper(abs(p[1]))/64
        rem=(u*u*abs(self.bounds[n+8])+2*u*v*abs(self.bounds[n+10])+v*v*abs(self.bounds[n+12]))/2
        return value+zero_ball(rem)
