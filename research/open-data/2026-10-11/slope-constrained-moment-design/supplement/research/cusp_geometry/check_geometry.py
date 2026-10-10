#!/usr/bin/env python3
"""Separate exact-rational audit of geometry and the width derivative sign.

Saved oscillatory derivative enclosures are trusted inputs. The nonlinear
width polynomial is expanded in eleven monomials, independently of the
factored/automatic-differentiation implementation used by the generator.
"""
import hashlib
import json
import sys
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
if not __debug__: raise RuntimeError('Run without -O/-OO')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_region'))
from check_witnesses import Interval as I,read,contraction,matrix

TERMS=[((0,3,1,1,0,0,0,0),-1),((0,4,0,0,1,0,0,0),1),
 ((1,1,2,1,0,0,0,0),2),((1,2,0,2,0,0,0,0),1),
 ((1,2,1,0,1,0,0,0),-2),((1,3,0,0,0,1,0,0),-1),
 ((2,0,1,2,0,0,0,0),-2),((2,1,1,0,0,1,0,0),1),
 ((2,2,0,0,0,0,1,0),1),((3,0,0,1,0,1,0,0),1),
 ((3,1,0,0,0,0,0,1),-1)]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(v):
    a=read(v);assert a.lo==a.hi
    return a.lo
def power(v,k):
    out=I(1)
    for _ in range(k): out=out*v
    return out
def partials(d):
    out=[]
    for j in range(8):
        total=I(0)
        for exponents,c in TERMS:
            if not exponents[j]: continue
            term=I(c*exponents[j])
            for k,e in enumerate(exponents): term*=power(d[k],e-int(k==j))
            total+=term
        out.append(total)
    return out
def pmul(a,b):
    out=[I(0) for _ in range(len(a)+len(b)-1)]
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    return out

def width_check(raw,new):
    c=list(map(read,raw['central_derivatives']+new['extra_central_derivatives']))
    B=list(map(exact,raw['absolute_derivative_bounds']+new['extra_absolute_bounds']))
    v=list(map(exact,raw['predictor']));h=exact(raw['driver_half_width'])
    scale=exact(new['opening_shape']['scale']);assert scale>0
    # Multinomial enumeration of A^k/k!, without operator multiplication.
    weights=[v[0],-v[1]/4,v[2]/16,-Q(1,64)]
    rows=[{} for _ in range(9)]
    for p in range(9):
      for q in range(9-p):
       for r in range(9-p-q):
        for s in range(9-p-q-r):
         k=p+q+r+s;m=p+2*q+4*r+6*s
         a=Q(1,factorial(p)*factorial(q)*factorial(r)*factorial(s))
         for w,e in zip(weights,(p,q,r,s)): a*=w**e
         rows[k][m]=rows[k].get(m,Q(0))+a
    polys=[];errors=[]
    for n in range(3,11):
        polys.append([sum((a*c[n+m] for m,a in rows[k].items()),I(0))/scale for k in range(8)])
        errors.append(h**8*sum(abs(a)*B[n+m] for m,a in rows[8].items())/scale)
    result=[I(0) for _ in range(36)]
    for exponents,coef in TERMS:
        term=[I(coef)]
        for p,e in zip(polys,exponents):
            for _ in range(e): term=pmul(term,p)
        for k,a in enumerate(term): result[k]+=a
    rad=sum(a.abs_upper()*h**k for k,a in enumerate(result) if k)
    pred=result[0]+I(-rad,rad)
    d=[read(x)/scale for x in new['cusp_derivatives']]
    grad=partials([d[n]+I(-errors[n-3],errors[n-3]) for n in range(3,11)])
    jet_error=sum(a.abs_upper()*e for a,e in zip(grad,errors))
    grad=partials(d[3:11])
    chain=[sum((grad[n-3]*d[n+shift]*factor for n in range(3,11)),I(0))
           for shift,factor in ((1,Q(1)),(2,-Q(1,4)),(4,Q(1,16)))]
    root_error=sum(a.abs_upper()*exact(r) for a,r in zip(chain,raw['tight_root_radii']))
    N=pred+I(-jet_error-root_error,jet_error+root_error)
    assert N.lo>0
    kp=N/(64*d[3]*d[3]*d[4]*d[4]*d[4])
    assert kp.hi<0
    return {'N_lower_display':float(N.lo),'kprime_lower_display':float(kp.lo),
            'kprime_upper_display':float(kp.hi)}

def main():
    path=HERE/'results/geometry_certificate.json';data=json.loads(path.read_text())
    for name,h in data['source_sha256'].items(): assert sha(HERE/name)==h
    for p in data['input_packages']:
        base=HERE.parent/p['package'];assert sha(base/'manifest.json')==p['manifest_sha256']
        for e in json.loads((base/'manifest.json').read_text())['files']:
            assert sha(base/e['path'])==e['sha256']
    rpath=HERE.parent/'cusp_connection/results/connection_certificate.json'
    assert sha(rpath)==data['connection_certificate_sha256']
    old=json.loads(rpath.read_text());assert len(data['cells'])==58
    T,L,M=Q(3,1000),Q(1,1000000),Q(1,500000000)
    checks=[]
    for index,cell in enumerate(data['cells']):
        assert cell['index']==index
        assert cell['driver_center']==old['cells'][index]['driver_center']
        curve=cell['uniform_fold'];d=list(map(read,curve['derivatives']))
        Y=[list(map(read,row)) for row in curve['preconditioner']]
        result=contraction(Y,matrix(d),list(map(read,curve['H_on_centerline'])),[I(Q(2)**-13),I(Q(2)**-20)])
        delta=d[3]*d[4]-d[2]*d[5]
        assert d[3].lo>0 and d[4].hi<0 and delta.hi<0
        lp=4*d[2]*d[4]/delta;mp=16*d[2]*d[2]/delta
        wp=d[3]-d[4]*lp/4+d[6]*mp/16;assert wp.lo>0
        quad=4*d[4]/delta*wp/2;cubic=I(-16)/delta*wp*wp/3
        assert quad.lo>Q(180,100) and quad.hi<Q(221,100)
        assert cubic.lo>Q(161,100) and cubic.hi<Q(209,100)
        assert cubic.lo**2>Q(49,100)**2*quad.hi**3
        assert cubic.hi**2<Q(86,100)**2*quad.lo**3
        assert Q(180,100)*T*T>L and Q(86,100)**2*L**3<M*M
        assert len(cell['window_endpoints'])==2
        for sign,end in zip((-1,1),cell['window_endpoints']):
            assert end['sign']==sign
            assert (read(end['F'])*sign).lo>0 and (read(end['F_tt_on_Q'])*sign).lo>0
        for off,sign,w in zip((-Q(3,2000),-Q(3,10000),Q(3,10000),Q(3,2000)),(-1,1,-1,1),cell['three_root_witness']):
            assert read(w['s']).contains(off) and w['sign']==sign and (read(w['F'])*sign).lo>0
        assert len(cell['three_root_witness'])==4 and len(cell['one_root_cover'])==32
        for k,w in enumerate(cell['one_root_cover']):
            assert read(w['left']).contains(-T+2*T*k/32)
            assert read(w['right']).contains(-T+2*T*(k+1)/32)
            assert read(w['F_t']).lo>0
        result.update(width_check(old['cells'][index],cell));checks.append(result)
        if index%10==0 or index==57: print('exact geometry cell',index+1,'passed',flush=True)
    endrat=[]
    for name in ('quartic','sextic'):
        p=HERE.parent/f'cusp_verified/results/{name}_cusp_certificate.json'
        assert sha(p)==data['endpoints'][name]['certificate_sha256']
        d=list(map(read,json.loads(p.read_text())['root_derivative_enclosures']))
        endrat.append(-d[3]/d[4])
    ratio=endrat[1]/endrat[0]
    assert ratio.lo>Q(1024,1000) and ratio.hi<Q(1026,1000)
    report={'status':'exact_geometry_and_opening_checks_passed','certificate_sha256':sha(path),
        'source_sha256':sha(Path(__file__)),'cells_checked':len(checks),
        'trust_boundary':'Cusp and neighborhood derivative enclosures and local Taylor values are trusted inputs; reconstructs contraction/growth/root-count inequalities and the nonlinear opening sign using expanded polynomials and fractions.',
        'q_max_display':max(v['q_upper_display'] for v in checks),
        'eta_plus_q_max_display':max(v['eta_plus_q_display'] for v in checks),
        'N_lower_min_display':min(v['N_lower_display'] for v in checks),
        'kprime_range_display':[min(v['kprime_lower_display'] for v in checks),max(v['kprime_upper_display'] for v in checks)],
        'endpoint_ratio_display':[float(ratio.lo),float(ratio.hi)]}
    (HERE/'results/exact_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
