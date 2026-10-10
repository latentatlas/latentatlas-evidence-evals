#!/usr/bin/env python3
"""Separate rational reconstruction of the entire finite-window proof.

No FLINT or R10 generating module imported. Exponential-operator
coefficients are assembled by truncated polynomial convolution.
"""
import argparse,itertools,json,sys,time,hashlib
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'cusp_shape_design'
sys.path.insert(0,str(BASE))
from check_design import D,read,exact,det
if not __debug__:raise RuntimeError('Assertions required')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sym(r):return D(-r,r)
def away(v):return v.lo>0 or v.hi<0
def power(v,k):
    v=D.of(v)
    if not k:return D(1)
    if k%2:return D(v.lo**k,v.hi**k)
    return D(0 if v.lo<=0<=v.hi else min(abs(v.lo),abs(v.hi))**k,max(abs(v.lo),abs(v.hi))**k)
def inv(a):
    n=len(a);z=det(a);assert away(z)
    return [[((-1)**(i+j)*det([[a[r][c] for c in range(n) if c!=i] for r in range(n) if r!=j]))/z for j in range(n)] for i in range(n)]
def mv(a,v):return [sum((x*y for x,y in zip(r,v)),D(0)) for r in a]
def mm(a,b):return [[sum((a[i][k]*b[k][j] for k in range(len(b))),D(0)) for j in range(len(b[0]))] for i in range(len(a))]
def controls(d,orders=(0,1,2)):return [[-d[n+2]/4,d[n+4]/16,-d[n+6]/64] for n in orders]
def contractions(Y,J,f,r):
    assert away(det([[D.of(v) for v in row] for row in Y]))
    p=mm(Y,J);q=max(sum((D(i==j)-p[i][j]).abs_upper()*r[j]/r[i] for j in range(len(r))) for i in range(len(r)))
    eta=max(z.abs_upper()/v for z,v in zip(mv(Y,f),r));assert q+eta<1
    return q,eta
def dump(v):return [str(v.lo),str(v.hi)]


class Taylor:
    def __init__(self,data):
        jets=json.loads((BASE/'results/local_jets.json').read_text())
        design=json.loads((BASE/'results/design_certificate.json').read_text())
        assert data['input_sha256']['local_jets.json']==sha(BASE/'results/local_jets.json')
        assert data['input_sha256']['design_certificate.json']==sha(BASE/'results/design_certificate.json')
        eps=read(design['quartic_boundary']['amplitude'])
        g=[read(f)+eps*read(h) for f,h in zip(jets['F_at_exact_Q'],jets['H_at_exact_Q'])]
        assert g[4].hi<0;scale=D(24)/g[4]
        self.c=[scale*v for v in g];self.c[:4]=[D(0)]*4;self.c[4]=D(24)
        self.B=[(scale.abs_upper()*(1+eps.abs_upper())*exact(v)) for v in data['unnormalized_absolute_bounds']]
        self.domain=list(map(read,data['domain']))
    def derivatives(self,x,upto=8):
        x=list(map(D.of,x));assert len(x)==4 and upto<=12
        assert all(v.abs_upper()<=r.hi for v,r in zip(x,self.domain))
        dirs=[x[0],-x[1]/4,x[2]/16,-x[3]/64];orders=(1,2,4,6)
        poly={(0,0):D(1)}
        for u,shift in zip(dirs,orders):
            terms=[power(u,k)/factorial(k) for k in range(9)];out={}
            for (k,n),v in poly.items():
                for j in range(9-k):
                    idx=(k+j,n+j*shift);out[idx]=out.get(idx,D(0))+v*terms[j]
            poly=out
        ret=[]
        for n in range(upto+1):
            value=sum((v*self.c[n+j] for (k,j),v in poly.items() if k<8),D(0))
            rem=sum(v.abs_upper()*self.B[n+j] for (k,j),v in poly.items() if k==8)
            ret.append(value+sym(rem))
        return ret


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();mp=HERE/'results/model_v2.json';cp=HERE/'results/window_certificate.json'
    data=json.loads(mp.read_text());cert=json.loads(cp.read_text());assert cert['model_sha256']==sha(mp)
    for d in (data,cert):
        for n,h in d['source_sha256'].items():assert sha(HERE/n)==h
    m=Taylor(data);T=Q(2)**-7;P=[Q(2)**-17,Q(2)**-34,Q(2)**-34]
    assert exact(cert['global_box']['T'])==T and list(map(exact,cert['global_box']['parameter_radii']))==P
    x=[sym(T)]+[sym(v) for v in P];d=m.derivatives(x,8)
    assert d[4].lo>22 and d[4].hi<26
    for sign in (-1,1):
        side=m.derivatives([sign*T]+x[1:],4)
        assert side[0].lo>Q('1e-9') and (sign*side[1]).lo>Q('1e-6')
    R=[4*T*T,32*T**3,32*T**3];assert list(map(exact,cert['auxiliary_radii']))==R
    ad=m.derivatives([sym(T)]+[sym(v) for v in R],9)
    fy=[list(map(exact,r)) for r in cert['fold_surface']['Y']]
    fq,fe=contractions(fy,[r[1:] for r in controls(ad,(0,1))],m.derivatives([sym(T),sym(R[0]),0,0],1),R[1:])
    cy=[list(map(exact,r)) for r in cert['cusp_curve']['Y']]
    cq,ce=contractions(cy,controls(ad),m.derivatives([sym(T),0,0,0],2),R)
    ci=inv(controls(ad));v=[ci[i][2] for i in range(3)]
    slope=ad[4]-ad[3]*sum((z*u for z,u in zip(controls(ad,(3,))[0],v)),D(0))
    assert slope.lo>16 and slope.hi<32
    assert v[0].hi<Q('-.1') and v[0].lo>Q('-.24')
    growth=-v[0]*slope/2;assert growth.lo>Q('.8') and growth.hi<4
    checks=[];L=Q(2)**-24;rsmall=[L/128,L*L/256,L*L/256];rho=Q(2)**-20
    for row,(name,center,count) in zip(cert['open_witnesses'],[('zero',[-L,0,0],0),('two',[-L,-L*L,0],2),('four',[L,0,0],4)]):
        assert row['name']==name and row['count']==count and list(map(exact,row['center']))==center
        assert list(map(exact,row['radii']))==rsmall
        box=[D(v-r,v+r) for v,r in zip(center,rsmall)]
        assert all(v.abs_upper()<p for v,p in zip(box,P))
        if count in (0,2):
            strip=m.derivatives([sym(rho)]+box,4);assert strip[2].lo>0
            for sign in (-1,1):
                side=m.derivatives([sign*rho]+box,3)
                assert (sign*side[3]).lo>0 and (sign*side[1]).lo>0
            if count==0:assert strip[0].lo>0
            else:assert m.derivatives([0]+box,0)[0].hi<0
        else:
            for s,sign in zip((-3,-1,0,1,3),(1,-1,1,-1,1)):
                assert (sign*m.derivatives([s*Q(2)**-12]+box,0)[0]).lo>0
        checks.append({'name':name,'count':count,'original_control_box_checked':True})
        print('Rational open box',name,'passed',flush=True)
    out={'status':'independent_rational_finite_window_surface_cusp_and_0_2_4_boxes_passed',
        'model_sha256':sha(mp),'certificate_sha256':sha(cp),'source_sha256':sha(__file__),
        'g4_bounds':dump(d[4]),'fold_q':str(fq),'fold_eta':str(fe),'cusp_q':str(cq),'cusp_eta':str(ce),
        'cusp_g3_slope':dump(slope),'cusp_lambda_quadratic_bounds':dump(growth),'witnesses':checks,
        'method':'Rational intervals rounded outwards to a 512-bit dyadic grid. Exact derivatives and normalization rebuilt from R09 inputs. Taylor operator assembled by polynomial convolution; inverse by cofactor determinants.',
        'trust_boundary':'R09 integral enclosures and R10 unnormalized positive majorants are inputs. Every new normalized jet, spatial Taylor enclosure, contraction inequality and witness sign is rebuilt. The analytic root-count and discriminant arguments still require mathematical review.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(out['status'],flush=True)


if __name__=='__main__':main()
