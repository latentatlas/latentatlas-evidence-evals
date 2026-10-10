#!/usr/bin/env python3
"""Separate rational cofactor/dual proof and exact quartic-root rank check."""
import argparse,itertools,json,sys,time
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_width'))
import check_width
check_width.SCALE=1<<512
from check_width import D,read,exact
sys.path.insert(0,str(HERE.parent/'cusp_robustness'))
from check_pinned import exact_identity
import hashlib
if not __debug__:raise RuntimeError('Assertions required')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def det(a):
    n=len(a);total=D(0)
    for p in itertools.permutations(range(n)):
        sign=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        term=D(sign)
        for i in range(n):term*=a[i][p[i]]
        total+=term
    return total
def away(v):return v.lo>0 or v.hi<0
def sym(r):return D(-r,r)
def rowinterval(v):return [str(v.lo),str(v.hi)]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();path=HERE/'results/design_certificate.json';cert=json.loads(path.read_text())
    dp=HERE/'results/dictionary_16.json';raw=json.loads(dp.read_text())
    qp=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';q=json.loads(qp.read_text())
    assert sha(dp)==cert['dictionary_sha256'] and sha(qp)==cert['quartic_certificate_sha256']
    assert sha(HERE/'certify_design.py')==cert['source_sha256']
    assert sha(HERE/'moment_dictionary.py')==raw['source_sha256']
    M=[[read(row['moments'][n]) for row in raw['rows']] for n in range(9)]
    inds=[j-1 for j in cert['frequencies']];assert inds==[9,12,14,15]
    cof=[(-1)**j*det([[M[n][inds[k]] for k in range(4) if k!=j] for n in range(3)]) for j in range(4)]
    assert all(away(v) for v in cof)
    norm=sum((v if v.lo>0 else -v for v in cof),D(0))
    w=[cert['orientation']*v/norm for v in cof];signs=[1 if v.lo>0 else -1 for v in w]
    assert norm.lo>0
    force=[sum((v*M[n][j] for v,j in zip(w,inds)),D(0)) for n in range(9)]
    for v in force[:3]:assert v.lo<=0<=v.hi
    f=list(map(read,q['root_derivative_enclosures']))
    a,b=force[3]/f[3],force[4]/f[4];score=b-a
    assert score.lo>Q('83.76697') and score.hi<Q('83.76698')
    A=[[v/exact(s) for v in row] for row,s in zip(M[:3],cert['optimization']['row_scales'])]
    d=[M[4][j]/f[4]-M[3][j]/f[3] for j in range(16)]
    L=[[A[n][j] for n in range(3)]+[D(s)] for j,s in zip(inds,signs)]
    denom=det(L);assert away(denom);rhs=[d[j] for j in inds];dual=[]
    for col in range(4):
        alt=[[rhs[i] if j==col else L[i][j] for j in range(4)] for i in range(4)]
        dual.append(det(alt)/denom)
    y,z=dual[:3],dual[3];assert z.lo>0 and (z-score).lo<=0<=(z-score).hi
    reduced=[d[j]-sum((A[n][j]*y[n] for n in range(3)),D(0)) for j in range(16)]
    margins=[z.lo-reduced[j].abs_upper() for j in range(16) if j not in inds]
    assert min(margins)>0
    # Support equalities are EXACT by the definition of the exact linear
    # system, not inferred from a small interval residual. The cofactor
    # vector is feasible exactly by the symbolic identity.
    identity=exact_identity()
    tau=Q(1,128)
    assert (1+sym(tau*a.abs_upper())).lo>Q('0.58')
    assert (1+sym(tau*b.abs_upper())).lo>Q('0.76')
    ratio=((1+tau*a)*(1-tau*b))/((1+tau*b)*(1-tau*a))
    assert ratio.lo>Q('0.2536045') and ratio.hi<Q('0.2536046')
    crit=-D(1)/a;assert crit.lo>Q('0.0187691205') and crit.hi<Q('0.0187691206')
    ds=[f[n]+crit*force[n] for n in range(9)];ds[:4]=[D(0)]*4
    assert ds[4].hi<0 and crit.hi<1
    controls=[[-ds[n+2]/4,ds[n+4]/16,-ds[n+6]/64] for n in range(3)]
    rank=det(controls);assert rank.hi<0
    # Sparse determinant identity at a quartic zero:
    # det = G4*(G4*G7-G5*G6)/4096.
    factorized=ds[4]*(ds[4]*ds[7]-ds[5]*ds[6])/4096
    assert (factorized-rank).lo<=0<=(factorized-rank).hi
    report={'status':'rational_exact_pinning_dual_optimality_and_quartic_rank_passed',
        'certificate_sha256':sha(path),'dictionary_sha256':sha(dp),'source_sha256':sha(__file__),
        'cofactor_identities':identity,'finite_class_optimum':rowinterval(score),'dual_bound':rowinterval(z),
        'smallest_inactive_dual_margin':str(min(margins)),'a':rowinterval(a),'b':rowinterval(b),
        'safe_C_ratio':rowinterval(ratio),'quartic_amplitude':rowinterval(crit),
        'quartic_fourth_derivative':rowinterval(ds[4]),'quartic_control_determinant':rowinterval(rank),
        'rounding':'Independent rational endpoint arithmetic, outward to a 512-bit dyadic grid. Determinants expanded by permutations; dual system solved by Cramer determinants.',
        'trust_boundary':'Saved rigorous integral enclosures at the exact Q are inputs. No FLINT or R09 generating module imported. Exact moment cancellation and active dual equalities follow from their algebraic definitions, not numerical residuals.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as fp:json.dump(report,fp,indent=2);fp.write('\n')
    print(report['status'],'dual margin',float(min(margins)),'quartic amplitude',float(crit.lo),flush=True)


if __name__=='__main__':main()
