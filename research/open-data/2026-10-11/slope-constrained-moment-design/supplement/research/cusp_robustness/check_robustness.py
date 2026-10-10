#!/usr/bin/env python3
"""Separate rational audit, no FLINT or R07 generating module imported.

Rebuilds enlarged-tube Taylor enclosures by multinomial coefficients,
both nonlinear cusp polynomials by expanded monomials, local geometry,
and the fifth transport derivative by its ODE. Frozen integral jets,
majorants and R03 contraction bounds remain trusted numerical inputs.
"""
import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Run without -O/-OO')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_width'))
from check_width import D,read,exact,powi,mul,TERMS as TERMS4,fifth_from_ode
sys.path.insert(0,str(HERE.parent/'cusp_geometry'))
from check_geometry import TERMS as TERMS3


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sym(r):return D(-r,r)
def upper(x):return D.of(x).hi
def determinant(Y):
    return sum((Y[0][j]*(Y[1][(j+1)%3]*Y[2][(j+2)%3]-Y[1][(j+2)%3]*Y[2][(j+1)%3]) for j in range(3)),D(0))
def away0(x):return x.lo>0 or x.hi<0


def multinomial_rows(weights,shifts,K=8):
    rows=[{} for _ in range(K+1)]
    def visit(j,k,s,value):
        if j==len(weights):
            rows[k][s]=rows[k].get(s,Q(0))+value
            return
        for e in range(K-k+1):
            visit(j+1,k+e,s+shifts[j]*e,value*weights[j]**e/factorial(e))
    visit(0,0,0,Q(1))
    return rows


class Taylor:
    def __init__(self,raw,geo,width,radii):
        self.c=list(map(read,raw['central_derivatives']+geo['extra_central_derivatives']+width['extra_central_derivatives']))
        self.B=list(map(exact,raw['absolute_derivative_bounds']+geo['extra_absolute_bounds']+width['extra_absolute_bounds']))
        self.v=list(map(exact,raw['predictor']));self.h=exact(raw['driver_half_width'])
        self.r=list(radii);self.allowed=list(map(exact,raw['majorant_domain_half_widths']))
        self.A=multinomial_rows((self.v[0],-self.v[1]/4,self.v[2]/16,-Q(1,64)),(1,2,4,6))
        self.cache={};self.tailcache={}
    def combo(self,n,p):
        key=(n,p)
        if key not in self.cache:self.cache[key]=sum((v*self.c[n+s] for s,v in self.A[p].items()),D(0))
        return self.cache[key]
    def tail(self,n,p):
        key=(n,p)
        if key not in self.tailcache:self.tailcache[key]=sum(abs(v)*self.B[n+s] for s,v in self.A[p].items())
        return self.tailcache[key]
    def enclose(self,extra,upto):
        r=[a+b for a,b in zip(self.r,extra)]
        assert all(abs(v)*self.h+x<allowed for v,x,allowed in zip(self.v,r,self.allowed))
        assert self.h<=self.allowed[3]
        W=multinomial_rows((r[0],r[1]/4,r[2]/16),(1,2,4))
        out=[]
        for n in range(upto+1):
            radius=Q(0)
            for p in range(9):
                for q in range(9-p):
                    if p==q==0:continue
                    radius+=self.h**p*sum(w*(self.combo(n+s,p).abs_upper() if p+q<8 else self.tail(n+s,p)) for s,w in W[q].items())
            out.append(self.c[n]+sym(radius))
        return out


def grad(terms,ds):
    out=[]
    for j in range(len(ds)):
        total=D(0)
        for exps,coef in terms:
            if not exps[j]:continue
            term=D(coef*exps[j])
            for i,e in enumerate(exps):term*=powi(ds[i],e-int(i==j))
            total+=term
        out.append(total)
    return out


def correlated_numerator(model,cp0,cp,epsilon,terms,degree,nlast,scale):
    assert scale>0
    polys=[[model.combo(n,p)/scale for p in range(8)] for n in range(3,nlast+1)]
    errors=[model.h**8*model.tail(n,8)/scale for n in range(3,nlast+1)]
    cached=[]
    for p in polys:
        powers=[[D(1)]]
        for k in range(1,degree+1):powers.append(mul(powers[-1],p,7*k))
        cached.append(powers)
    coeff=[D(0) for _ in range(7*degree+1)]
    for exps,c in terms:
        p=[D(c)]
        for j,e in enumerate(exps):
            if e:p=mul(p,cached[j][e],len(p)+7*e-1)
        for k,value in enumerate(p):coeff[k]+=value
    pred=coeff[0]+sym(sum(v.abs_upper()*model.h**k for k,v in enumerate(coeff) if k))
    ds=[v/scale for v in cp0]
    g=grad(terms,[ds[n]+sym(errors[n-3]) for n in range(3,nlast+1)])
    jeterr=sum(a.abs_upper()*e for a,e in zip(g,errors))
    g=grad(terms,ds[3:nlast+1])
    spatial=[sum((g[n-3]*ds[n+shift]*factor for n in range(3,nlast+1)),D(0)) for shift,factor in ((1,Q(1)),(2,-Q(1,4)),(4,Q(1,16)))]
    rooterr=sum(a.abs_upper()*r for a,r in zip(spatial,model.r))
    gp=grad(terms,[v/scale for v in cp[3:nlast+1]])
    kernelerr=epsilon/scale*sum(a.abs_upper()*model.B[n] for n,a in zip(range(3,nlast+1),gp))
    return pred+sym(jeterr+rooterr+kernelerr)


class Local:
    def __init__(self,c,b):self.c=list(c);self.c[:3]=[D(0)]*3;self.b=b
    def axis(self,n,s):
        return sum((powi(s,k)*self.c[n+k]/factorial(k) for k in range(6-n)),D(0))+powi(s,6-n)*self.b[6]/factorial(6-n)
    def evaluate(self,n,s,l,m):
        s,l,m=map(D.of,(s,l,m))
        if n<2:
            val=self.axis(n,s)-l/4*self.axis(n+2,s)+m/16*self.axis(n+4,s)
            al,am=l.abs_upper()/4,m.abs_upper()/16
            rem=(al*al*self.b[n+4].abs_upper()+2*al*am*self.b[n+6].abs_upper()+am*am*self.b[n+8].abs_upper())/2
            return val+sym(rem)
        if n==2:return s*self.b[3]-l/4*self.b[4]+m/16*self.b[6]
        return self.b[n]


def check_geometry(cp,b,Y):
    T,L,M=Q(3,1000),Q(1,10**6),Q(2,10**9)
    r=(Q(2)**-13,Q(2)**-20);local=Local(cp,b)
    d=[local.evaluate(n,sym(T),sym(r[0]),sym(r[1])) for n in range(7)]
    assert away0(Y[0][0]*Y[1][1]-Y[0][1]*Y[1][0])
    J=[[-d[2]/4,d[4]/16],[-d[3]/4,d[5]/16]]
    q=max(sum((D(i==j)-sum((Y[i][k]*J[k][j] for k in range(2)),D(0))).abs_upper()*r[j]/r[i] for j in range(2)) for i in range(2))
    H=[local.evaluate(n,sym(T),D(0),D(0)) for n in range(2)]
    eta=max(sum((Y[i][k]*H[k] for k in range(2)),D(0)).abs_upper()/r[i] for i in range(2))
    assert q+eta<1
    delta=d[3]*d[4]-d[2]*d[5]
    assert d[3].lo>0 and d[4].hi<0 and delta.hi<0
    lp,mp=4*d[2]*d[4]/delta,16*d[2]*d[2]/delta
    wp=d[3]-d[4]*lp/4+d[6]*mp/16
    quad=4*d[4]/delta*wp/2;cubic=D(-16)/delta*wp*wp/3
    assert wp.lo>0 and quad.lo>Q(180,100) and quad.hi<Q(221,100)
    assert cubic.lo>Q(161,100) and cubic.hi<Q(209,100)
    assert cubic.lo**2>Q(49,100)**2*quad.hi**3
    assert cubic.hi**2<Q(86,100)**2*quad.lo**3
    assert Q(180,100)*T*T>L and Q(86,100)**2*L**3<M*M
    for sign in (-1,1):
        assert (sign*local.evaluate(0,sign*T,sym(L),sym(M))).lo>0
        assert (sign*local.evaluate(2,sign*T,sym(r[0]),sym(r[1]))).lo>0
    for s,sign in zip((-Q(3,2000),-Q(3,10000),Q(3,10000),Q(3,2000)),(-1,1,-1,1)):
        assert (sign*local.evaluate(0,s,L/2,0)).lo>0
    for k in range(32):assert local.evaluate(1,D(-T+2*T*k/32,-T+2*T*(k+1)/32),-L/2,0).lo>0
    return wp,{'q':str(q),'eta':str(eta)}


def check_cell(raw,geo,width,row,epsilon):
    R=list(map(exact,raw['radii']));Y=[list(map(read,v)) for v in raw['preconditioner']]
    # E and Q must use the exact dyadic preconditioner, not its 192-bit
    # interval copy. Otherwise artificial widening can exceed the much
    # finer generator radius by ~10^-70 and invalidate containment checks.
    Ye=[list(map(exact,v)) for v in raw['preconditioner']]
    assert away0(determinant(Y))
    B=list(map(exact,raw['absolute_derivative_bounds']))
    E=max(sum(abs(Ye[i][n])*B[n] for n in range(3))/R[i] for i in range(3))
    Qerr=max(sum(sum(abs(Ye[i][n])*B[n+shifts] for n in range(3))*f*R[j]/R[i] for j,(shifts,f) in enumerate(((1,Q(1)),(2,Q(1,4)),(4,Q(1,16))))) for i in range(3))
    q=exact(raw['q'])+epsilon*Qerr;eta=exact(raw['eta'])+epsilon*E
    assert q+eta<1
    displacement=[r*epsilon*E/(1-q) for r in R]
    tight=list(map(exact,row['contraction']['tight']))
    required=[min(r*eta/(1-q),exact(old)+d) for r,old,d in zip(R,raw['tight_root_radii'],displacement)]
    assert all(need<=used<Ri for need,used,Ri in zip(required,tight,R))
    assert max(displacement)<Q(4,10**5)
    model=Taylor(raw,geo,width,tight)
    cp0=model.enclose((Q(0),)*3,15)
    perturb=lambda ds:[v+sym(epsilon*model.B[n]) for n,v in enumerate(ds)]
    cp=perturb(cp0)
    assert cp[3].lo>0 and cp[4].hi<0 and cp[6].hi<0
    mup=cp[6]/(4*cp[4]);lp=(4*cp[5]*mup-cp[7])/(16*cp[3])
    assert mup.lo>Q(26,100) and mup.hi<Q(34,100)
    scale=exact(row['opening_original']['scale'])
    assert scale==exact(row['fourth_original']['scale'])
    N=correlated_numerator(model,cp0,cp,epsilon,TERMS3,5,10,scale)
    ds=[v/scale for v in cp]
    kp=N/(64*ds[3]*ds[3]*ds[4]*ds[4]*ds[4]);assert N.lo>0 and kp.hi<0
    limits=(Q(2)**-8,Q(2)**-12,Q(2)**-19)
    b=perturb(model.enclose(limits,10))
    wp,geometry=check_geometry(cp,b,[list(map(read,v)) for v in row['geometry']['preconditioner']])
    N4=correlated_numerator(model,cp0,cp,epsilon,TERMS4,7,11,scale)
    fourth=(-2*N4/(ds[3]*ds[3]*ds[3]*ds[4]*ds[4]*ds[4]*ds[4])).abs_upper()
    S=Q(3,4000);extra=(2*S,Q(222,100)*S*S,Q(210,100)*S*S*S)
    fd=perturb(model.enclose(extra,26));fd[0]=fd[1]=D(0);fd[2]=sym(wp.hi*S)
    fifth=fifth_from_ode([v/scale for v in fd],lp)
    third=-32*kp+sym(fourth*S+fifth*S*S/2)
    assert third.lo>0
    assert Q(180,100)*S*S>Q(1,10**6)
    assert third.lo**2>(3*Q(3,10000))**2*Q(221,100)**3
    assert third.hi**2<(3*Q(3,1000))**2*Q(180,100)**3
    return {'index':row['index'],'q':str(q),'eta':str(eta),'tight':[str(x) for x in tight],
            'displacement':[str(x) for x in displacement], 'kprime':[str(kp.lo),str(kp.hi)],
            'third':[str(third.lo),str(third.hi)],'fourth_abs':str(fourth),'fifth_abs':str(fifth),
            'geometry':geometry}


def affine(raw,nu):return [exact(x)+exact(v)*(nu-exact(raw['driver_center'])) for x,v in zip(raw['center'],raw['predictor'])]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,default=HERE/'results/robustness_certificate.json')
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--sample',action='store_true');args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();cert=json.loads(args.certificate.read_text())
    for name,h in cert['source_sha256'].items():assert sha(HERE/name)==h
    for entry in cert['input_packages']:
        base=HERE.parent/entry['package'];assert sha(base/'manifest.json')==entry['manifest_sha256']
        for row in json.loads((base/'manifest.json').read_text())['files']:assert sha(base/row['path'])==row['sha256']
    paths=[HERE.parent/p/'results'/name for p,name in (('cusp_connection','connection_certificate.json'),('cusp_geometry','geometry_certificate.json'),('cusp_width','width_certificate.json'))]
    for p in paths:assert sha(p)==cert['input_certificates'][str(p.relative_to(HERE.parent))]
    old,geo,width=[json.loads(p.read_text()) for p in paths]
    assert len(cert['cells'])==58 and len(cert['seams'])==57
    epsilon=exact(cert['epsilon_proof_upper'])
    assert 0<Q(cert['epsilon_requested_rational'])<=epsilon<1
    checks=[]
    for i in ((0,28,57) if args.sample else range(58)):
        raw=old['cells'][i];row=cert['cells'][i]
        assert row['index']==i and exact(raw['driver_center'])==-Q(2*i+1,4) and exact(raw['driver_half_width'])==Q(1,4)
        checks.append(check_cell(raw,geo['cells'][i],width['cells'][i],row,epsilon))
        if i%10==0 or i in (28,57):print('R07 independent rational cell',i+1,'passed',flush=True)
    joins=[]
    if not args.sample:
        for i in range(57):
            a,b=old['cells'][i:i+2];nu=exact(a['driver_left']);assert nu==exact(b['driver_right'])
            aa,bb=affine(a,nu),affine(b,nu)
            ratios=[(abs(x-y)+Q(r))/exact(R) for x,y,r,R in zip(aa,bb,checks[i]['tight'],b['radii'])]
            assert max(ratios)<1;joins+=ratios
        startmu=affine(old['cells'][0],Q(0))[2]-Q(checks[0]['tight'][2])
        endmu=affine(old['cells'][57],Q(-29))[2]+Q(checks[57]['tight'][2])
        assert startmu>0 and endmu<0
        assert Q(4,10**5)/Q(26,100)<Q(2,10**4)
    report={'status':'sample_checks_passed' if args.sample else 'independent_rational_robustness_checks_passed',
        'cells_checked':len(checks),'joins_checked':len(joins)//3,
        'certificate_sha256':sha(args.certificate),'source_sha256':sha(Path(__file__)),
        'trust_boundary':'Frozen original-kernel central integral enclosures, positive majorants and original R03 contraction/tight-root bounds are assumed valid. All NEW Taylor enclosures, perturbation inequalities, nonlinear polynomials, geometry and transport bounds are rebuilt without FLINT or the R07 generator.',
        'rounding':'Fraction endpoint arithmetic with outward rounding to a 192-bit dyadic grid; proof comparisons use rational numbers only.',
        'readable_rate_bounds':['0.0003','0.003'],
        'max_displacement_display':float(max(Q(d) for c in checks for d in c['displacement'])),
        'seam_max_ratio_display':float(max(joins)) if joins else None,
        'third_range_display':[float(min(Q(c['third'][0]) for c in checks)),float(max(Q(c['third'][1]) for c in checks))],
        'checks':checks,'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','trust_boundary','rounding')}),flush=True)


if __name__=='__main__':main()
