#!/usr/bin/env python3
"""Numerical branch discovery in the three-control family; not a path proof."""
import json
import hashlib
import sys
import time
from fractions import Fraction
from pathlib import Path
from flint import arb,ctx

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'cusp_verified'
REGION=HERE.parent/'cusp_region'
sys.path.insert(0,str(BASE))
from validated_flow import (cache,jacobian,midpoint_inverse,matvec,
                            norm_vec,serialize)
from local_roots import restore


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_inputs():
    records=[]
    for directory in (BASE,REGION):
        manifest=json.loads((directory/'manifest.json').read_text())
        for entry in manifest['files']:
            if sha(directory/entry['path'])!=entry['sha256']:
                raise ArithmeticError(f'Input package changed: {directory.name}/{entry["path"]}')
        records.append({'package':directory.name,'manifest_sha256':sha(directory/'manifest.json'),
                        'file_count':len(manifest['files'])})
    return records


def J(c):
    return jacobian(c,[0,1,2],[1,2,4],[arb(1),-arb(1)/4,arb(1)/16])


def point_cache(x,nu,nmax=8,**kw):
    settings=dict(N=16,U=2,pieces=8,abs_tol='1e-98',rel_tol='1e-98')
    settings.update(kw)
    return cache(x[0],{1:x[1],2:x[2],3:nu},nmax,**settings)


def refine(x,nu):
    x=[arb(v).mid() for v in x]
    last=None
    for iteration in range(12):
        c=point_cache(x,nu)
        Y=midpoint_inverse(J(c))
        change=matvec(Y,c[:3])
        last=norm_vec(change)
        if last<arb('1e-65'):
            return x,c,Y,last,iteration
        if not last.is_finite() or last>100:
            raise ArithmeticError('Newton candidate left the intended local range')
        x=[(a-b).mid() for a,b in zip(x,change)]
    raise ArithmeticError(f'Candidate did not converge: {last}')


def tangent(c,Y):
    return [v.mid() for v in matvec(Y,[v/64 for v in c[6:9]])]


def trace(seed,start_nu,targets):
    out=[]
    x,c,Y,error,_=refine(seed,start_nu)
    nu=start_nu
    for index,target in enumerate(targets):
        v=tangent(c,Y)
        guess=[(a+b*(target-nu)).mid() for a,b in zip(x,v)]
        x,c,Y,error,steps=refine(guess,target)
        nu=target
        out.append({'nu':serialize(nu),'point':[serialize(a) for a in x],
                    'tangent':[serialize(a) for a in tangent(c,Y)],
                    'F_ttt':serialize(c[3]),'F_tttt':serialize(c[4]),
                    'newton_correction_bound':serialize(error),'newton_steps':steps})
        if index%5==0 or index+1==len(targets):
            print('nu',nu.str(8),'point',[a.str(12) for a in x],flush=True)
    return out


def main():
    ctx.dps=110
    started=time.monotonic()
    inputs=verify_inputs()
    q=json.loads((BASE/'results/quartic_cusp_certificate.json').read_text())
    s=json.loads((BASE/'results/sextic_cusp_certificate.json').read_text())
    xq=list(map(restore,q['center_exact_dyadic']))
    ts,ls,ns=list(map(restore,s['center_exact_dyadic']))
    print('Forward discovery from quartic point',flush=True)
    forward=trace(xq,arb(0),[arb(-k) for k in range(30)])
    print('Reverse discovery from sextic point',flush=True)
    backward=trace([ts,ls,arb(0)],ns,[arb(-k) for k in range(28,-1,-1)])
    differences=[]
    for row in backward:
        man,exp=row['nu']['mid_man_exp']
        exact_nu=Fraction(man)*Fraction(2)**exp
        if exact_nu.denominator!=1 or row['nu']['rad_man_exp'][0]!=0:
            raise ArithmeticError('Shared-node driver must be an exact integer')
        nu=exact_nu.numerator
        other=forward[-nu]
        a=list(map(restore,row['point']))
        b=list(map(restore,other['point']))
        difference=norm_vec([u-v for u,v in zip(a,b)])
        if not difference<arb('1e-55'):
            raise ArithmeticError('Opposite continuation directions disagree')
        differences.append(serialize(difference))
    at_sextic,_,_,error,_=refine(list(map(restore,forward[29]['point'])),ns)
    report={'status':'two_direction_numerical_connection_candidate',
            'is_continuum_certificate':False,
            'scope':'G=(F,F_t,F_tt)=0, unknowns (t,lambda,mu), driver nu from 0 to -29',
            'input_packages':inputs,'forward':forward,'backward':backward,
            'shared_node_differences':differences,
            'sextic_slice_driver':serialize(ns),
            'point_at_sextic_driver':[serialize(v) for v in at_sextic],
            'distance_to_sextic_center':serialize(norm_vec([at_sextic[0]-ts,at_sextic[1]-ls,at_sextic[2]])),
            'source_sha256':sha(Path(__file__)),
            'elapsed_seconds':time.monotonic()-started}
    (HERE/'results').mkdir(exist_ok=True)
    (HERE/'results/exploration.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Candidate found; independent path certification is still required.',flush=True)
    print('Distance at sextic driver:',report['distance_to_sextic_center']['enclosure'],flush=True)


if __name__=='__main__':
    main()
