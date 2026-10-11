#!/usr/bin/env python3
"""Independent rational Taylor reconstruction, geometry and fold-ODE proof."""
import argparse,json,sys,time
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
sys.dont_write_bytecode=True
from check_design import HERE,sha,D,read,exact,sym,away
sys.path.insert(0,str(HERE.parent/'cusp_robustness'))
from check_robustness import Local
sys.path.insert(0,str(HERE.parent/'cusp_pinned_family'))
from check_family import joint_ode
if not __debug__:raise RuntimeError('Assertions required')


def mv(a,v):return [sum((x*y for x,y in zip(row,v)),D(0)) for row in a]
def mm(a,b):return [[sum((a[i][k]*b[k][j] for k in range(len(b))),D(0)) for j in range(len(b[0]))] for i in range(len(a))]


class Taylor:
    def __init__(self,data,eps):
        self.f=list(map(read,data['F_at_exact_Q']));self.h=list(map(read,data['H_at_exact_Q']))
        self.b=list(map(exact,data['absolute_F_bounds']));self.domain=list(map(exact,data['local_majorant_domain']))
        self.eps=eps;self.c=[f+eps*h for f,h in zip(self.f,self.h)];self.mult=1+eps.abs_upper()
    def enclose(self,r,upto):
        assert r[1]<self.domain[1] and r[2]<self.domain[2]
        coefficients=[{} for _ in range(9)]
        for a in range(9):
            for b in range(9-a):
                for c in range(9-a-b):
                    k=a+b+c;s=a+2*b+4*c
                    v=r[0]**a*(r[1]/4)**b*(r[2]/16)**c/Q(factorial(a)*factorial(b)*factorial(c))
                    coefficients[k][s]=coefficients[k].get(s,Q(0))+v
        g=[];h=[]
        for n in range(upto+1):
            rg=sum(v*self.c[n+s].abs_upper() for k in range(1,8) for s,v in coefficients[k].items())
            rh=sum(v*self.h[n+s].abs_upper() for k in range(1,8) for s,v in coefficients[k].items())
            tail=sum(v*self.b[n+s] for s,v in coefficients[8].items())
            g.append(self.c[n]+sym(rg+self.mult*tail));h.append(self.h[n]+sym(rh+tail))
        return g,h


def check_geometry(c,b,Y):
    T,L,M=Q(3,1000),Q(1,10**6),Q(2,10**9);r=(Q(2)**-13,Q(2)**-19)
    local=Local(c,b);ds=[local.evaluate(n,sym(T),sym(r[0]),sym(r[1])) for n in range(7)]
    assert away(D(Y[0][0]*Y[1][1]-Y[0][1]*Y[1][0]))
    j=[[-ds[2]/4,ds[4]/16],[-ds[3]/4,ds[5]/16]];yj=mm(Y,j)
    q=max(sum((D(i==j)-yj[i][j]).abs_upper()*r[j]/r[i] for j in range(2)) for i in range(2))
    h=[local.evaluate(n,sym(T),D(0),D(0)) for n in range(2)]
    eta=max(v.abs_upper()/rr for v,rr in zip(mv(Y,h),r));assert q+eta<1
    delta=ds[3]*ds[4]-ds[2]*ds[5]
    assert ds[3].lo>0 and ds[4].hi<0 and delta.hi<0
    lp,mp=4*ds[2]*ds[4]/delta,16*ds[2]*ds[2]/delta
    wp=ds[3]-ds[4]*lp/4+ds[6]*mp/16;assert wp.lo>0
    quad=4*ds[4]/delta*wp/2;cubic=D(-16)/delta*wp*wp/3
    assert quad.lo>0 and cubic.lo>0
    assert quad.lo*T*T>L and cubic.hi**2*L**3<M*M*quad.lo**3
    for sign in (-1,1):
        assert (sign*local.evaluate(0,sign*T,sym(L),sym(M))).lo>0
        assert (sign*local.evaluate(2,sign*T,sym(r[0]),sym(r[1]))).lo>0
    for s,sign in zip((-Q(3,2000),-Q(3,10000),Q(3,10000),Q(3,2000)),(-1,1,-1,1)):
        assert (sign*local.evaluate(0,s,L/2,0)).lo>0
    for j in range(32):assert local.evaluate(1,D(-T+2*T*j/32,-T+2*T*(j+1)/32),-L/2,0).lo>0
    return quad,cubic,wp,q,eta


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();path=HERE/'results/local_certificate.json';cert=json.loads(path.read_text())
    jp=HERE/'results/local_jets.json';data=json.loads(jp.read_text())
    assert sha(jp)==cert['jet_certificate_sha256'] and len(cert['cells'])==16
    for d in (cert,data):
        for n,h in d['source_sha256'].items():assert sha(HERE/n)==h
    checks=[]
    for i,row in enumerate(cert['cells']):
        assert row['index']==i and exact(row['left'])==-Q(1,128)+Q(i,1024)
        assert exact(row['right'])==exact(row['left'])+Q(1,1024)
        if i:assert row['left']==cert['cells'][i-1]['right']
        eps=read(row['epsilon']);assert eps.lo<=exact(row['left']) and eps.hi>=exact(row['right'])
        model=Taylor(data,eps);c=model.c
        assert c[3].lo>0 and c[4].hi<0
        b,_=model.enclose((Q(2)**-8,Q(2)**-12,Q(2)**-18),10)
        quad,cubic,wp,q,eta=check_geometry(c,b,[list(map(exact,r)) for r in row['geometry']['preconditioner']])
        a,bb,cc=c[3:6];h3,h4,h5=model.h[3:6]
        kp=(model.f[3]*h4-model.f[4]*h3)/(bb*bb);assert kp.hi<0
        A3p=Q(4,3)*((h5*bb-cc*h4)/(bb*bb)-(h4*a-bb*h3)/(a*a))
        M4=(96*(-a/bb)*A3p).abs_upper();S=Q(1,1000);assert quad.lo*S*S>Q(1,10**6)
        extra=(2*S,quad.hi*S*S,cubic.hi*S**3)
        fd,fh=model.enclose(extra,26);fd[0]=fd[1]=D(0);fd[2]=sym(wp.hi*S)
        scale=read(data['F_at_exact_Q'][3]);scale=(scale.lo+scale.hi)/2
        M5=joint_ode([v/scale for v in fd],[v/scale for v in fh],D(0))
        third=-32*kp+sym(M4*S+M5*S*S/2);assert third.lo>0
        assert third.lo**2>(3*10)**2*quad.hi**3
        assert third.hi**2<(3*500)**2*quad.lo**3
        checks.append({'index':i,'q':str(q),'eta':str(eta),'quadratic':[str(quad.lo),str(quad.hi)],
                       'third':[str(third.lo),str(third.hi)],'M4':str(M4),'M5':str(M5)})
        print('Rebuilt rational local cell',i,'passed',flush=True)
    report={'status':'rational_Taylor_geometry_and_finite_transport_passed','cells':16,'adjacent_joins':15,
            'certificate_sha256':sha(path),'jet_certificate_sha256':sha(jp),'source_sha256':sha(__file__),
            'rate_bounds':['10','500'],'checks':checks,
            'trust_boundary':'Exact-Q F/H integral enclosures and positive majorants are input assumptions. All new spatial Taylor bounds, geometry inequalities and fifth derivative transport bounds are rebuilt without FLINT or R09 generating modules. The fifth derivative is obtained from the fold ODE rather than implicit-series elimination.',
            'rounding':'Rational endpoints, outward 512-bit dyadic grid.','elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],flush=True)


if __name__=='__main__':main()
