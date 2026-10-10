#!/usr/bin/env python3
"""Rational finite-fold contraction verification from saved Taylor enclosures."""
import argparse,json,time
from pathlib import Path
from fractions import Fraction as Q
from check_design import HERE,sha,D,read,exact
from check_local import mm,mv


def contains(a,b):return a.lo<=b.lo and a.hi>=b.hi


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();p=HERE/'results/fold_samples.json';data=json.loads(p.read_text())
    for n,h in data['source_sha256'].items():assert sha(HERE/n)==h
    assert data['jet_certificate_sha256']==sha(HERE/'results/local_jets.json')
    assert len(data['models'])==11 and len(data['samples'])==88
    count=0
    for s in data['samples']:
        assert 1<=s['j']<=8 and contains(read(s['ell']),D(Q(s['j']**2,64*10**6)))
        for name,sign in (('upper',-1),('lower',1)):
            v=s[name];c=list(map(exact,v['center']));r=list(map(exact,v['radii']))
            d=list(map(read,v['box_derivatives']));h=list(map(read,v['center_derivatives']))
            y=[list(map(exact,z)) for z in v['preconditioner']]
            assert y[0][0]*y[1][1]-y[0][1]*y[1][0]!=0
            yj=mm(y,[[d[1],d[4]/16],[d[2],d[5]/16]])
            q=max(sum((D(i==j)-yj[i][j]).abs_upper()*r[j]/r[i] for j in range(2)) for i in range(2))
            eta=max(a.abs_upper()/rr for a,rr in zip(mv(y,h[:2]),r))
            assert q<=exact(v['q']) and eta<=exact(v['eta']) and q+eta<1
            tight=list(map(exact,v['tight_root_radii']))
            assert all(rr*eta/(1-q)<=t<rr for rr,t in zip(r,tight))
            for x,t,b in zip(c,tight,v['root_enclosures']):assert contains(read(b),D(x-t,x+t))
            assert sign*c[0]>r[0] and abs(c[0])+r[0]<Q(3,1000) and abs(c[1])+r[1]<Q(2,10**9)
            assert d[4].hi<0 and (sign*d[2]).lo>0
            count+=1
        hi=read(s['upper']['root_enclosures'][1]);lo=read(s['lower']['root_enclosures'][1])
        assert contains(read(s['width']),hi-lo) and hi.lo>lo.hi
    comparisons=[]
    for row in data['comparisons']:
        minus,plus=(0,8) if row['direction']=='selected' else (9,10)
        for i,sign in ((minus,-1),(plus,1)):assert exact(data['models'][i]['epsilon'])==Q(sign,128)
        wm=read(next(s['width'] for s in data['samples'] if s['model']==minus and s['j']==row['j']))
        wp=read(next(s['width'] for s in data['samples'] if s['model']==plus and s['j']==row['j']))
        change=100*(wp/wm-1);assert change.hi<0 and contains(read(row['change_percent']),change)
        if row['j']==8:
            if row['direction']=='selected':assert change.lo>Q('-74.639525') and change.hi<Q('-74.639524')
            else:assert change.lo>Q('-0.000781') and change.hi<Q('-0.000780')
            comparisons.append({'direction':row['direction'],'change_percent':[str(change.lo),str(change.hi)]})
    report={'status':'176_rational_fold_contractions_and_16_width_comparisons_passed',
        'fold_contractions':count,'finite_width_comparisons':16,'last_offset_comparisons':comparisons,
        'certificate_sha256':sha(p),'source_sha256':sha(__file__),
        'trust_boundary':'Saved integral/local Taylor enclosures are inputs; all finite-fold contraction inequalities, signs, tight boxes and width comparisons rebuilt with rational endpoints.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],flush=True)


if __name__=='__main__':main()
