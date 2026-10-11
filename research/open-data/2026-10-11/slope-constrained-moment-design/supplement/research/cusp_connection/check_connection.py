#!/usr/bin/env python3
"""Independent exact-rational check of every continuation cell and join.

Taylor coefficients are rebuilt using multinomial formulas, rather than
the generator's differential-operator multiplication. No FLINT is imported.
The central integral enclosures and real majorants remain trusted inputs.
"""
import json
import hashlib
import sys
from fractions import Fraction as Q
from math import factorial
from pathlib import Path

if not __debug__:
    raise RuntimeError('Run without Python -O/-OO')

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'cusp_verified'
REGION=HERE.parent/'cusp_region'
sys.path.insert(0,str(REGION))
from check_witnesses import Interval as I,read


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(ball):
    a=read(ball)
    assert a.lo==a.hi
    return a.lo


def determinant(a):
    # Cyclic-column form of the ordinary 3x3 determinant.
    return sum((a[0][j]*(a[1][(j+1)%3]*a[2][(j+2)%3]
                 -a[1][(j+2)%3]*a[2][(j+1)%3])
                for j in range(3)),I(0))


def coefficients(half,v,K):
    box=[half[0],half[1]/4,half[2]/16,half[3]/64]
    pred=[v[0],-v[1]/4,v[2]/16,-Q(1,64)]
    box_rows=[{} for _ in range(K+1)]
    pred_rows=[{} for _ in range(K+1)]
    tail_abs={}
    for p in range(K+1):
        for q in range(K+1-p):
            for r in range(K+1-p-q):
                for s in range(K+1-p-q-r):
                    k=p+q+r+s
                    m=p+2*q+4*r+6*s
                    denom=factorial(p)*factorial(q)*factorial(r)*factorial(s)
                    wp=Q(1,denom)
                    wb=Q(1,denom)
                    for b,a,e in zip(box,pred,(p,q,r,s)):
                        wb*=b**e
                        wp*=a**e
                    box_rows[k][m]=box_rows[k].get(m,Q(0))+wb
                    pred_rows[k][m]=pred_rows[k].get(m,Q(0))+wp
                    if k==K:
                        tail_abs[m]=tail_abs.get(m,Q(0))+abs(wp)
    return box_rows,pred_rows,tail_abs


def check_cell(cell,index):
    nc=exact(cell['driver_center'])
    h=exact(cell['driver_half_width'])
    assert nc==-Q(2*index+1,4) and h==Q(1,4)
    assert exact(cell['driver_left'])==nc-h
    assert exact(cell['driver_right'])==nc+h
    radii=list(map(exact,cell['radii']))
    assert all(r>0 for r in radii)
    c=list(map(read,cell['central_derivatives']))
    B=list(map(exact,cell['absolute_derivative_bounds']))
    v=list(map(exact,cell['predictor']))
    half=list(map(exact,cell['taylor_box_half_widths']))
    allowed=list(map(exact,cell['majorant_domain_half_widths']))
    assert half[3]==h
    assert all(half[j]>=abs(v[j])*h+radii[j] for j in range(3))
    assert all(a>b for a,b in zip(allowed,half))
    K=cell['taylor_order']
    assert K==8 and len(c)>=51 and len(B)>=57 and min(B)>0
    Y=[list(map(read,row)) for row in cell['preconditioner']]
    assert all(a.lo==a.hi for row in Y for a in row)
    assert not determinant(Y).contains(0)
    box,pred,tail=coefficients(half,v,K)
    shifts,factors=[1,2,4],[Q(1),-Q(1,4),Q(1,16)]
    defects=[]
    for i in range(3):
        row=[]
        for j in range(3):
            combo={m:factors[j]*sum((Y[i][ell]*c[ell+shifts[j]+m]
                         for ell in range(3)),I(0)) for m in range(6*(K-1)+1)}
            center=I(i==j)-combo[0]
            rad=sum(weight*combo[m].abs_upper() for k in range(1,K)
                    for m,weight in box[k].items())
            rad+=sum(weight*sum((abs(factors[j])*Y[i][ell].abs_upper()
                                 *B[ell+shifts[j]+m] for ell in range(3)),Q(0))
                     for m,weight in box[K].items())
            row.append(center+I(-rad,rad))
        defects.append(row)
    q=max(sum(defects[i][j].abs_upper()*radii[j]/radii[i]
              for j in range(3)) for i in range(3))
    H=[]
    for n in range(3):
        rad=sum(h**k*sum((weight*c[n+m] for m,weight in pred[k].items()),I(0)).abs_upper()
                for k in range(1,K))
        rad+=h**K*sum(weight*B[n+m] for m,weight in tail.items())
        H.append(c[n]+I(-rad,rad))
    eta=max(sum((Y[i][ell]*H[ell] for ell in range(3)),I(0)).abs_upper()/radii[i]
            for i in range(3))
    assert q<1 and q+eta<1,(index,float(q),float(eta))
    assert q<Q(502,1000) and q+eta<Q(56,100)
    d=list(map(read,cell['uniform_derivatives']))
    # Rebuild ordinary derivative enclosures by the same independent
    # multinomial bounds and verify signs on the entire box.
    signs={}
    for n,sign in ((3,1),(4,-1),(6,-1)):
        rad=sum(weight*c[n+m].abs_upper() for k in range(1,K)
                for m,weight in box[k].items())
        rad+=sum(weight*B[n+m] for m,weight in box[K].items())
        enclosed=c[n]+I(-rad,rad)
        assert (enclosed*sign).lo>0
        signs[n]=enclosed
    muprime=signs[6]/(4*signs[4])
    assert muprime.lo>Q(26,100) and muprime.hi<Q(34,100)
    assert signs[3].lo>Q(8,10**14)
    tight=[eta/(1-q)*r for r in radii]
    return {'q':q,'eta':eta,'tight':tight,
            'muprime':muprime,'F3':signs[3]}


def affine(cell,nu):
    nc=exact(cell['driver_center'])
    return [I(exact(a))+exact(b)*(nu-nc)
            for a,b in zip(cell['center'],cell['predictor'])]


def main():
    path=HERE/'results/connection_certificate.json'
    data=json.loads(path.read_text())
    for name,expected in data['source_sha256'].items():
        assert sha(HERE/name)==expected
    for directory,entry in zip((BASE,REGION),data['input_packages']):
        assert sha(directory/'manifest.json')==entry['manifest_sha256']
        manifest=json.loads((directory/'manifest.json').read_text())
        for f in manifest['files']:
            assert sha(directory/f['path'])==f['sha256']
    cells=data['cells']
    assert len(cells)==58 and len(data['seams'])==57
    checks=[]
    for i,cell in enumerate(cells):
        checks.append(check_cell(cell,i))
        if i%10==0 or i==57:
            print(f'Exact rational cell {i+1}/58 passed',flush=True)
    seam_ratios=[]
    for i,(a,b) in enumerate(zip(cells,cells[1:])):
        nu=exact(a['driver_left'])
        assert nu==exact(b['driver_right'])
        ca,cb=affine(a,I(nu)),affine(b,I(nu))
        radii=list(map(exact,b['radii']))
        for j in range(3):
            displacement=(ca[j]-cb[j]).abs_upper()+checks[i]['tight'][j]
            assert displacement<radii[j]
            assert displacement/radii[j]<Q(117,1000)
            seam_ratios.append(displacement/radii[j])
    oldq=json.loads((BASE/'results/quartic_cusp_certificate.json').read_text())
    qr=read(oldq['radius']).hi
    qc=list(map(read,oldq['center_exact_dyadic']))
    first=affine(cells[0],I(0))
    assert all((a-b).abs_upper()+qr<exact(r)
               for a,b,r in zip(qc,first,cells[0]['radii']))
    olds=json.loads((BASE/'results/sextic_cusp_certificate.json').read_text())
    ts,ls,ns=list(map(read,olds['center_exact_dyadic']))
    sr=read(olds['radius']).hi
    nu=ns+I(-sr,sr)
    matches=[i for i,c in enumerate(cells)
             if exact(c['driver_left'])<nu.lo and nu.hi<exact(c['driver_right'])]
    assert len(matches)==1
    cell=cells[matches[0]]
    sc=affine(cell,nu)
    target=[ts+I(-sr,sr),ls+I(-sr,sr),I(0)]
    assert all((a-b).abs_upper()<exact(r) for a,b,r in zip(target,sc,cell['radii']))
    report={'status':'exact_rational_connection_check_passed',
            'scope':'All 58 Taylor contractions rebuilt using multinomial coefficients, 57 root-containment joins, both original cusp identifications',
            'trust_boundary':'Central integral enclosures and uniform derivative majorants are input assumptions; does not replace an expert or formal proof review',
            'certificate_sha256':sha(path),'source_sha256':sha(Path(__file__)),
            'q_max_display':float(max(v['q'] for v in checks)),
            'eta_plus_q_max_display':float(max(v['q']+v['eta'] for v in checks)),
            'seam_containment_ratio_max_display':float(max(seam_ratios)),
            'F_ttt_min_display':float(min(v['F3'].lo for v in checks)),
            'mu_prime_range_display':[float(min(v['muprime'].lo for v in checks)),
                                      float(max(v['muprime'].hi for v in checks))],
            'per_cell_contractions':[{'q_upper':str(v['q']),'eta_upper':str(v['eta'])} for v in checks]}
    (HERE/'results/exact_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k.endswith('_display') or k=='status'},indent=2))


if __name__=='__main__':
    main()
