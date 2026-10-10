#!/usr/bin/env python3
"""Independent outward rational arithmetic and a fold-ODE jet check.

The generator solves implicit power-series coefficients. This checker
differentiates the fold ODE recursively. No FLINT or generating code is
imported. Integral/correlated derivative enclosures remain trusted inputs.
"""
import hashlib
import json
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
if not __debug__:raise RuntimeError('Run without -O/-OO')
HERE=Path(__file__).resolve().parent
BITS=192
SCALE=1<<BITS

class D:
    def __init__(self,lo,hi=None):
        lo=Q(lo);hi=lo if hi is None else Q(hi)
        if lo>hi:raise ValueError('Reversed interval')
        self.lo=Q((lo.numerator*SCALE)//lo.denominator,SCALE)
        self.hi=Q(-((-hi.numerator*SCALE)//hi.denominator),SCALE)
    @staticmethod
    def of(x):return x if isinstance(x,D) else D(x)
    def __add__(self,x):
        x=self.of(x);return D(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return D(-self.hi,-self.lo)
    def __sub__(self,x):return self+-self.of(x)
    def __rsub__(self,x):return self.of(x)+-self
    def __mul__(self,x):
        x=self.of(x);p=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)]
        return D(min(p),max(p))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=self.of(x)
        if x.lo<=0<=x.hi:raise ZeroDivisionError('Zero divisor')
        return self*D(1/x.hi,1/x.lo)
    def abs_upper(self):return max(abs(self.lo),abs(self.hi))

def exact(v):
    a,e=v['mid_man_exp'];r,f=v['rad_man_exp'];assert r==0
    return Q(a)*Q(2)**e
def read(v):
    a,e=v['mid_man_exp'];r,f=v['rad_man_exp'];assert r>=0
    m=Q(a)*Q(2)**e;b=Q(r)*Q(2)**f
    return D(m-b,m+b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mul(a,b,K):
    out=[D(0) for _ in range(K+1)]
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            if i+j<=K:out[i+j]+=x*y
    return out
def divide(a,b,K):
    out=[D(0) for _ in range(K+1)]
    for k in range(K+1):out[k]=(a[k]-sum((b[j]*out[k-j] for j in range(1,k+1)),D(0)))/b[0]
    return out
def powi(a,k):
    v=D(1)
    for _ in range(k):v*=a
    return v

TERMS=[
((0,5,1,1,0,0,0,0,0),1),((0,6,0,0,1,0,0,0,0),-1),
((1,3,2,1,0,0,0,0,0),-2),((1,4,0,2,0,0,0,0,0),-1),
((1,4,1,0,1,0,0,0,0),2),((1,5,0,0,0,1,0,0,0),1),
((2,1,3,1,0,0,0,0,0),-1),((2,2,1,2,0,0,0,0,0),3),
((2,2,2,0,1,0,0,0,0),1),((2,3,0,1,1,0,0,0,0),-1),
((2,3,1,0,0,1,0,0,0),-1),((2,4,0,0,0,0,1,0,0),-1),
((3,0,2,2,0,0,0,0,0),2),((3,1,0,3,0,0,0,0,0),-1),
((3,1,1,1,1,0,0,0,0),-2),((3,1,2,0,0,1,0,0,0),-1),
((3,2,0,0,2,0,0,0,0),1),((3,3,0,0,0,0,0,1,0),1),
((4,0,1,1,0,1,0,0,0),-1),((4,1,0,1,0,0,1,0,0),1),
((4,1,1,0,0,0,0,1,0),1),((4,2,0,0,0,0,0,0,1),-1)]

def grad(ds):
    out=[]
    for j in range(9):
        value=D(0)
        for exps,coef in TERMS:
            if not exps[j]:continue
            term=D(coef*exps[j])
            for i,e in enumerate(exps):term*=powi(ds[i],e-int(i==j))
            value+=term
        out.append(value)
    return out

def fourth_bound(old,geo,new):
    centers=list(map(read,old['central_derivatives']+geo['extra_central_derivatives']+new['extra_central_derivatives']))
    B=list(map(exact,old['absolute_derivative_bounds']+geo['extra_absolute_bounds']+new['extra_absolute_bounds']))
    v=list(map(exact,old['predictor']));h=exact(old['driver_half_width'])
    scale=exact(new['fourth_at_cusp']['scale'])
    rows=[{} for _ in range(9)]
    weights=(v[0],-v[1]/4,v[2]/16,-Q(1,64))
    for a in range(9):
      for b in range(9-a):
       for c in range(9-a-b):
        for d in range(9-a-b-c):
         k=a+b+c+d;s=a+2*b+4*c+6*d
         z=Q(1,factorial(a)*factorial(b)*factorial(c)*factorial(d))
         for x,e in zip(weights,(a,b,c,d)):z*=x**e
         rows[k][s]=rows[k].get(s,Q(0))+z
    polynomials=[];errors=[]
    for n in range(3,12):
        polynomials.append([sum((w*centers[n+s] for s,w in rows[k].items()),D(0))/scale for k in range(8)])
        errors.append(h**8*sum(abs(w)*B[n+s] for s,w in rows[8].items())/scale)
    # Ordinary expanded monomials, distinct from the generator's factorization.
    cached=[]
    for p in polynomials:
        powers=[[D(1)]]
        for k in range(1,7):powers.append(mul(powers[-1],p,7*k))
        cached.append(powers)
    coefficients=[D(0) for _ in range(50)]
    for exps,c in TERMS:
        p=[D(c)]
        for i,e in enumerate(exps):
            if e:p=mul(p,cached[i][e],len(p)+7*e-1)
        for j,z in enumerate(p):coefficients[j]+=z
    radius=sum(z.abs_upper()*h**k for k,z in enumerate(coefficients) if k)
    pred=coefficients[0]+D(-radius,radius)
    ds=[read(v)/scale for v in new['cusp_derivatives']]
    g=grad([ds[n]+D(-errors[n-3],errors[n-3]) for n in range(3,12)])
    ejet=sum(a.abs_upper()*b for a,b in zip(g,errors))
    g=grad(ds[3:12])
    spatial=[sum((g[n-3]*ds[n+shift]*factor for n in range(3,12)),D(0))
             for shift,factor in ((1,Q(1)),(2,-Q(1,4)),(4,Q(1,16)))]
    eroot=sum(a.abs_upper()*exact(r) for a,r in zip(spatial,old['tight_root_radii']))
    N=pred+D(-ejet-eroot,ejet+eroot)
    a,b=ds[3],ds[4]
    return (-2*N/(a*a*a*b*b*b*b)).abs_upper()

def fifth_from_ode(ds,lp):
    K=5
    jets=[[v]+[D(0) for _ in range(K)] for v in ds]
    for k in range(1,K+1):
        w,d3,d4,d5=[row[:k] for row in (jets[2],jets[3],jets[4],jets[5])]
        delta=[a-b for a,b in zip(mul(d3,d4,k-1),mul(w,d5,k-1))]
        lprime=divide([4*a for a in mul(w,d4,k-1)],delta,k-1)
        mprime=divide([16*a for a in mul(w,w,k-1)],delta,k-1)
        for n in range(27-4*k):
            rhs=jets[n+1][k-1]-mul(lprime,jets[n+2][:k],k-1)[k-1]/4+mul(mprime,jets[n+4][:k],k-1)[k-1]/16
            jets[n][k]=rhs/k
    u=[4*lp*a+b/4 for a,b in zip(jets[2],jets[6])]
    result=divide(u,jets[4],K)
    return 120*result[5].abs_upper()

def main():
    path=HERE/'results/width_certificate.json';data=json.loads(path.read_text())
    for n,h in data['source_sha256'].items():assert sha(HERE/n)==h
    for entry in data['input_packages']:
        base=HERE.parent/entry['package'];p=base/'manifest.json'
        assert sha(p)==entry['manifest_sha256']
        for e in json.loads(p.read_text())['files']:assert sha(base/e['path'])==e['sha256']
    p3=HERE.parent/'cusp_connection/results/connection_certificate.json'
    p4=HERE.parent/'cusp_geometry/results/geometry_certificate.json'
    assert sha(p3)==data['connection_certificate_sha256'] and sha(p4)==data['geometry_certificate_sha256']
    old=json.loads(p3.read_text());geo=json.loads(p4.read_text())
    assert len(data['cells'])==58
    S=Q(3,4000);assert Q(180,100)*S*S>Q(1,1000000)
    checks=[]
    for i,row in enumerate(data['cells']):
        assert row['index']==i and row['driver_center']==old['cells'][i]['driver_center']
        scale=exact(row['fourth_at_cusp']['scale']);assert scale>0
        ds=[read(v)/scale for v in row['fold_derivatives']]
        assert ds[0].lo==ds[0].hi==ds[1].lo==ds[1].hi==0
        cp=[read(v)/scale for v in row['cusp_derivatives']]
        mup=cp[6]/(4*cp[4]);lp=(4*cp[5]*mup-cp[7])/(16*cp[3])
        fourth=fourth_bound(old['cells'][i],geo['cells'][i],row)
        fifth=fifth_from_ode(ds,lp)
        at0=-32*read(geo['cells'][i]['opening_shape']['kprime'])
        error=fourth*S+fifth*S*S/2
        low=at0.lo-error;high=at0.hi+error
        assert low>0,(i,float(low),float(fourth),float(fifth))
        # Conservative readable rate constants without irrational arithmetic.
        assert low**2>(3*Q(3,10000))**2*Q(221,100)**3
        assert high**2<(3*Q(3,1000))**2*Q(180,100)**3
        checks.append({'third_lower':str(low),'third_upper':str(high),
                       'fourth_abs':str(fourth),'fifth_abs':str(fifth)})
        if i%10==0 or i==57:print('rational ODE check',i+1,'passed; lower',float(low),flush=True)
    report={'status':'rational_ode_and_finite_width_checks_passed','cells_checked':58,
        'certificate_sha256':sha(path),'source_sha256':sha(Path(__file__)),
        'rounding':'Exact Fraction endpoint operations, outward to a fixed 192-bit dyadic grid after each operation; no binary floating point in proof comparisons',
        'trust_boundary':'Saved integral and correlated derivative enclosures are input assumptions. Rebuilds the fourth-derivative numerator from 22 monomials and the fifth derivative from the fold ODE.',
        'independently_verified_normalized_rate_bounds':['0.0003','0.003'],
        'third_lower_min_display':float(min(Q(v['third_lower']) for v in checks)),
        'third_upper_max_display':float(max(Q(v['third_upper']) for v in checks)),
        'per_cell':checks}
    (HERE/'results/rational_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='per_cell'},indent=2))

if __name__=='__main__':main()
