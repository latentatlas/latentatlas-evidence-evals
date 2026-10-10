#!/usr/bin/env python3
"""Rational verification of all endpoint plotting contraction witnesses.

Assumes the saved Taylor/integral enclosures, then independently checks
Banach contraction inequalities, signs, refined root bounds and widths.
"""
import json
from fractions import Fraction as Q
from pathlib import Path
from check_width import D,read,exact,sha
HERE=Path(__file__).resolve().parent


def mv(a,v):return [sum((x*y for x,y in zip(row,v)),D(0)) for row in a]
def mm(a,b):return [[sum((a[i][k]*b[k][j] for k in range(2)),D(0)) for j in range(2)] for i in range(2)]
def contains(a,b):return a.lo<=b.lo and a.hi>=b.hi


def main():
    path=HERE/'results/endpoint_folds.json';data=json.loads(path.read_text())
    assert data['source_sha256']==sha(HERE/'endpoint_folds.py')
    for entry in data['input_packages']:
        base=HERE.parent/entry['package'];mp=base/'manifest.json'
        assert sha(mp)==entry['manifest_sha256']
        for row in json.loads(mp.read_text())['files']:assert sha(base/row['path'])==row['sha256']
    assert len(data['samples'])==32
    checks=[]
    for k,row in enumerate(data['samples'],1):
        ell=Q(k*k,1000000*32*32)
        assert contains(read(row['ell']),D(ell)) and 0<ell<=Q(1,1000000)
        for name,endpoint in row['endpoints'].items():
            assert name in ('quartic','sextic')
            for branch,sign in (('upper',-1),('lower',1)):
                v=endpoint[branch]
                c=list(map(exact,v['center']));r=list(map(exact,v['radii']))
                d=list(map(read,v['box_derivatives']));h=list(map(read,v['center_derivatives']))
                Y=[list(map(exact,line)) for line in v['preconditioner']]
                assert Y[0][0]*Y[1][1]-Y[0][1]*Y[1][0]!=0
                J=[[d[1],d[4]/16],[d[2],d[5]/16]]
                YJ=mm(Y,J)
                q=max(sum(((D(i==j)-YJ[i][j])*r[j]/r[i]).abs_upper() for j in range(2)) for i in range(2))
                eta=max(z.abs_upper()/rr for z,rr in zip(mv(Y,h[:2]),r))
                assert q<1 and eta+q<1
                assert sign*c[0]>r[0] and abs(c[0])+r[0]<Q(3,1000)
                assert abs(c[1])+r[1]<Q(2,10**9)
                assert d[4].hi<0 and (sign*d[2]).lo>0
                # Refined root bounds are checked with the independently
                # recomputed inequality. Outward rounding may make a fresh
                # rational bound microscopically larger; use the original
                # contraction bound only if it dominates this calculation.
                saved_q=exact(v['q']);saved_eta=exact(v['eta'])
                assert q<=saved_q and eta<=saved_eta
                tr=list(map(exact,v['tight_root_radii']))
                assert all(t>=rr*saved_eta/(1-saved_q) for t,rr in zip(tr,r))
                for center,t,ball in zip(c,tr,v['root_enclosures']):
                    assert contains(read(ball),D(center-t,center+t))
                checks.append({'sample':k,'endpoint':name,'branch':branch,
                               'q_upper':str(q),'eta_upper':str(eta)})
            high=read(endpoint['upper']['root_enclosures'][1])
            low=read(endpoint['lower']['root_enclosures'][1])
            assert contains(read(endpoint['width']),high-low)
        ws=read(row['endpoints']['sextic']['width']);wq=read(row['endpoints']['quartic']['width'])
        assert wq.lo>0 and ws.lo>wq.hi
        assert contains(read(row['ratio']),ws/wq)
    report={'status':'128_endpoint_rational_contraction_checks_passed',
            'trust_boundary':'Saved integral/Taylor enclosures are inputs, not independently reintegrated here.',
            'certificate_sha256':sha(path),'source_sha256':sha(Path(__file__)),
            'interval_arithmetic_sha256':sha(HERE/'check_width.py'),'checks':checks}
    (HERE/'results/endpoint_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'])


if __name__=='__main__':main()
