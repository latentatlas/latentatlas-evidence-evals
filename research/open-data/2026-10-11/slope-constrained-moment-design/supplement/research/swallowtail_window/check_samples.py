#!/usr/bin/env python3
"""Rational re-evaluation and contraction checks for geometric samples."""
import argparse,json,time
from pathlib import Path
from check_window import *


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();mp=HERE/'results/model_v2.json';cp=HERE/'results/sample_certificate.json'
    cert=json.loads(cp.read_text());m=Taylor(json.loads(mp.read_text()))
    for n,h in cert['source_sha256'].items():assert sha(HERE/n)==h
    assert cert['model_sha256']==sha(mp) and cert['window_certificate_sha256']==sha(HERE/'results/window_certificate.json')
    L=Q(2)**-24;assert exact(cert['lambda_section'])==L
    records=[]
    def check(row,fun,name):
        center=list(map(exact,row['center']));r=list(map(exact,row['radii']));Y=[list(map(exact,z)) for z in row['preconditioner']]
        f,_=fun(list(map(D.of,center)));box=[D(x-rr,x+rr) for x,rr in zip(center,r)];_,jb=fun(box)
        q,eta=contractions(Y,jb,f,r)
        # Independently proved root enclosures can differ slightly from
        # the generator's tighter balls. Both lie in the common uniqueness box.
        tight=[rr*eta/(1-q) for rr in r]
        roots=[D(x-rr,x+rr) for x,rr in zip(center,tight)]
        assert all(rr<old for rr,old in zip(tight,r))
        records.append({'name':name,'q':str(q),'eta':str(eta),'root_enclosures':list(map(dump,roots))})
        return roots
    for row in cert['cusps']:
        def fun(x):
            s,mu,nu=x;d=m.derivatives([s,L,mu,nu],8)
            return d[:3],[[d[n+1],d[n+4]/16,-d[n+6]/64] for n in range(3)]
        x=check(row,fun,'cusp_'+str(row['branch']))
        assert (row['branch']*m.derivatives([x[0],L,x[1],x[2]],3)[3]).lo>0
        assert x[0].abs_upper()<Q(2)**-7 and all(v.abs_upper()<Q(2)**-34 for v in x[1:])
    def dfun(x):
        s1,s2,mu,nu=x;d1=m.derivatives([s1,L,mu,nu],7);d2=m.derivatives([s2,L,mu,nu],7)
        return [d1[0],d1[1],d2[0],d2[1]],[
            [d1[1],D(0),d1[4]/16,-d1[6]/64],
            [d1[2],D(0),d1[5]/16,-d1[7]/64],
            [D(0),d2[1],d2[4]/16,-d2[6]/64],
            [D(0),d2[2],d2[5]/16,-d2[7]/64]]
    z=check(cert['double_fold'],dfun,'two_double_roots');assert z[0].hi<z[1].lo
    assert all(m.derivatives([s,L,z[2],z[3]],2)[2].lo>0 for s in z[:2])
    assert all(v.abs_upper()<Q(2)**-34 for v in z[2:])
    for i,row in enumerate(cert['fold_samples']):
        s=read(row['s']);target=Q(2)**-12*Q(i-40,25);assert s.lo<=target<=s.hi
        def fun(x):
            d=m.derivatives([s,L,x[0],x[1]],7)
            return d[:2],[[d[n+4]/16,-d[n+6]/64] for n in range(2)]
        x=check(row,fun,'fold_'+str(i));assert all(v.abs_upper()<Q(2)**-34 for v in x)
    for group in cert['simple_roots']:
        p=list(map(exact,group['controls']));prev=None
        for i,row in enumerate(group['roots']):
            def fun(x):
                d=m.derivatives([x[0]]+p,1);return [d[0]],[[d[1]]]
            x=check(row,fun,group['name']+'_root_'+str(i))[0]
            assert x.abs_upper()<Q(2)**-7
            assert away(m.derivatives([x]+p,1)[1])
            if prev is not None:assert prev<x.lo
            prev=x.hi
    assert len(records)==90
    out={'status':'independent_rational_90_geometric_sample_contractions_passed',
        'certificate_sha256':sha(cp),'model_sha256':sha(mp),'source_sha256':sha(__file__),
        'cusps':2,'double_fold_intersections':1,'fold_curve_points':81,'simple_roots':6,'records':records,
        'trust_boundary':'R09 integral balls and R10 unnormalized majorants are inputs. All sample residuals, Jacobians and contraction inequalities are reconstructed by the separate rational Taylor implementation. Recorded rational tight boxes are separate from the generator boxes and share their full uniqueness boxes.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(out['status'],flush=True)


if __name__=='__main__':main()
