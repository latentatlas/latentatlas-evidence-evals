#!/usr/bin/env python3
"""Rational reconstruction of narrow cusp/fold contraction inequalities."""
import argparse,json,sys,time
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_width'))
import check_width
# The point residuals are much smaller than the 192-bit absolute grid.
# Increase precision explicitly; never relax a proof inequality.
check_width.SCALE=1<<512
from check_width import D,read,exact
from check_family import sha,endpoints


def mm(a,b):return [[sum((a[i][k]*b[k][j] for k in range(len(b))),D(0)) for j in range(len(b[0]))] for i in range(len(a))]
def mv(a,b):return [sum((x*y for x,y in zip(row,b)),D(0)) for row in a]
def nm(a):return max(sum(v.abs_upper() for v in row) for row in a)
def nv(a):return max(v.abs_upper() for v in a)
def contains(a,b):return a.lo<=b.lo and a.hi>=b.hi
def sym(r):return D(-r,r)
def det3(Y):return sum((Y[0][j]*(Y[1][(j+1)%3]*Y[2][(j+2)%3]-Y[1][(j+2)%3]*Y[2][(j+1)%3]) for j in range(3)),Q(0))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();pp=HERE/'results/point_certificates.json';fp=HERE/'results/fold_samples.json'
    points=json.loads(pp.read_text());folds=json.loads(fp.read_text())
    sheet=json.loads((HERE/'results/family_certificate.json').read_text())
    old=json.loads((HERE.parent/'cusp_connection/results/connection_certificate.json').read_text())
    assert points['family_certificate_sha256']==sha(HERE/'results/family_certificate.json')
    assert folds['point_certificate_sha256']==sha(pp)
    for doc in (points,folds):
        for name,h in doc['source_sha256'].items():assert sha(HERE/name)==h
    for row in points['rows']:
        R=exact(row['radius']);r=exact(row['root_radius']);d=list(map(read,row['point_derivatives']))
        B=list(map(exact,row['absolute_bounds']));Y=[list(map(exact,line)) for line in row['preconditioner']]
        assert det3(Y)!=0
        J=[[d[n+1],-d[n+2]/4,d[n+4]/16] for n in range(3)]
        yj=mm(Y,J);q0=nm([[D(i==j)-v for j,v in enumerate(line)] for i,line in enumerate(yj)])
        assert q0<=exact(row['q0'])
        shifts=(1,2,4);factors=(Q(1),Q(1,4),Q(1,16))
        M2=max(sum(factors[i]*factors[j]*B[n+shifts[i]+shifts[j]] for i in range(3) for j in range(3)) for n in range(3))
        assert M2<=exact(row['M2'])
        yn=max(sum(map(abs,line)) for line in Y);q=q0+yn*M2*R;eta=nv(mv(Y,d[:3]))
        assert q<=exact(row['q']) and eta<=exact(row['eta']) and eta+q*R<R
        assert eta/(1-q)<=r<R
        cp=list(map(read,row['cusp_derivatives']))
        for n in range(11):assert contains(cp[n],d[n]+sym(r*(B[n+1]+B[n+2]/4+B[n+4]/16)))
        assert cp[3].lo>0 and cp[4].hi<0
        ident=row['sheet_identification'];raw=old['cells'][ident['cell']];wide=sheet['slabs'][ident['slab']]['cells'][ident['cell']]
        rho=read(ident['rho']);nu=exact(row['nu']);eps=exact(row['epsilon'])
        assert contains(rho,D(eps)/(1+read(sheet['alpha'])*eps))
        for x,a,v,u,Rbig in zip(row['center'],raw['center'],raw['predictor'],wide['rho_predictor'],raw['radii']):
            centre=exact(a)+exact(v)*(nu-exact(raw['driver_center']))+exact(u)*rho
            assert (exact(x)-centre).abs_upper()+r<exact(Rbig)
    assert len(points['rows'])==21
    count=0
    for sample in folds['samples']:
        assert 1<=sample['j']<=8 and contains(read(sample['ell']),D(Q(sample['j']**2,64000000)))
        for name,sign in (('upper',-1),('lower',1)):
            row=sample[name];r=list(map(exact,row['radii']));c=list(map(exact,row['center']))
            d=list(map(read,row['box_derivatives']));h=list(map(read,row['center_derivatives']))
            Y=[list(map(exact,line)) for line in row['preconditioner']]
            assert Y[0][0]*Y[1][1]-Y[0][1]*Y[1][0]!=0
            yj=mm(Y,[[d[1],d[4]/16],[d[2],d[5]/16]])
            q=max(sum((D(i==j)-yj[i][j]).abs_upper()*r[j]/r[i] for j in range(2)) for i in range(2))
            eta=max(v.abs_upper()/rr for v,rr in zip(mv(Y,h[:2]),r))
            assert q<=exact(row['q']) and eta<=exact(row['eta']) and q+eta<1
            tight=list(map(exact,row['tight_root_radii']))
            assert all(rr*eta/(1-q)<=t<rr for rr,t in zip(r,tight))
            for x,t,b in zip(c,tight,row['root_enclosures']):assert contains(read(b),D(x-t,x+t))
            assert sign*c[0]>r[0] and abs(c[0])+r[0]<Q(3,1000) and abs(c[1])+r[1]<Q(2,10**9)
            assert d[4].hi<0 and (sign*d[2]).lo>0;count+=1
        high=read(sample['upper']['root_enclosures'][1]);low=read(sample['lower']['root_enclosures'][1])
        assert contains(read(sample['width']),high-low) and high.lo>low.hi
    assert count==144
    for comp in folds['comparisons']:
        g=next(i for i,m in enumerate(folds['models']) if m['nu']==comp['nu'] and exact(m['epsilon'])==-Q(1,2))
        lo=next(s for s in folds['samples'] if s['model']==g and s['j']==comp['j'])
        hi=next(s for s in folds['samples'] if s['model']==g+2 and s['j']==comp['j'])
        percent=100*(read(hi['width'])/read(lo['width'])-1)
        assert contains(read(comp['W_percent_plus_half_vs_minus_half']),percent) and percent.hi<0
    report={'status':'21_cusp_and_144_fold_rational_checks_passed','cusp_points':21,'fold_points':count,
            'finite_width_comparisons':len(folds['comparisons']),
            'rounding':'Exact rational endpoint operations, outward to a 512-bit dyadic grid.',
            'trust_boundary':'Saved integral, positive majorant and local Taylor enclosures remain inputs. Narrow contraction inequalities, derivative transport bounds, sheet identification and fold widths are checked independently.',
            'input_sha256':{'point_certificates.json':sha(pp),'fold_samples.json':sha(fp)},
            'source_sha256':sha(__file__),'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(report['status'],flush=True)


if __name__=='__main__':main()
