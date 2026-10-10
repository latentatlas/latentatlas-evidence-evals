#!/usr/bin/env python3
"""R09: rigorous finite cosine dictionary at the exact frozen quartic Q."""
import argparse,json,sys,time,hashlib
from pathlib import Path
from flint import arb,ctx
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_pinned_family'))
from pinned_model import restore,pack,upper,zero_ball,sha
from validated_flow import derivative,absolute_derivative_bounds


def verify():
    out=[]
    for name in ('cusp_verified','cusp_region','cusp_connection','cusp_geometry','cusp_width','cusp_literature','cusp_robustness','cusp_pinned_family'):
        base=HERE.parent/name;p=base/'manifest.json';m=json.loads(p.read_text())
        for row in m['files']:
            if sha(base/row['path'])!=row['sha256']:raise ArithmeticError('Frozen input changed '+name+'/'+row['path'])
        out.append({'package':name,'manifest_sha256':sha(p),'files':len(m['files'])})
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--max-frequency',type=int,default=16)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    if not 4<=args.max_frequency<=64:raise ValueError('Dictionary outside declared budget')
    ctx.dps=110;start=time.monotonic();inputs=verify()
    qp=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';q=json.loads(qp.read_text())
    x=list(map(restore,q['center_exact_dyadic']));r=restore(q['root_radius']);ds=list(map(restore,q['root_derivative_enclosures']))
    B=list(map(restore,q['absolute_derivative_bounds']));rows=[]
    for j in range(1,args.max_frequency+1):
        values=[];pairs=[]
        for n in range(9):
            pair=[derivative(x[0]+sign*j,{1:x[1],2:x[2],3:arb(0)},n,
                             N=16,U=2,pieces=8,abs_tol='1e-93',rel_tol='1e-93') for sign in (-1,1)]
            err=upper(r*(B[n+1]+B[n+2]/4+B[n+4]/16))
            values.append(sum(pair,arb(0))/2+zero_ball(err));pairs.append(pair)
        rows.append(pack({'frequency':j,'moments':values,'shifted_integrals':pairs}))
        print('Dictionary frequency',j,'of',args.max_frequency,'done',flush=True)
    report={'status':'rigorous_Q_cosine_moment_dictionary','max_frequency':args.max_frequency,
            'orders':list(range(9)),'rows':rows,'input_packages':inputs,'quartic_certificate_sha256':sha(qp),
            'source_sha256':sha(__file__),'quadrature':{'dps':110,'tolerance':'1e-93','terms':16,'panels':8,'cutoff':2},
            'scope':'Exact Q uncertainty and analytic series/infinite-domain tails included. All weights are later defined through these exact moments, not decimal midpoints.',
            'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')


if __name__=='__main__':main()
