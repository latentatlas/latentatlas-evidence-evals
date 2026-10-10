#!/usr/bin/env python3
"""Independent numerical support; this is not an interval proof."""
import importlib.util
import json
import hashlib
import time
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
source=HERE.parent/'cusp_connection/check_independent.py'
spec=importlib.util.spec_from_file_location('independent_mpmath',source)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inside(x,b):return abs(x-base.point(b))<base.rad(b)


def main():
    mp.mp.dps=115;started=time.monotonic()
    p3=HERE.parent/'cusp_connection/results/connection_certificate.json'
    p5=HERE/'results/width_certificate.json'
    old=json.loads(p3.read_text());new=json.loads(p5.read_text());rows=[]
    for i in (0,28,57):
        cell=old['cells'][i]
        t,lam,mu=map(base.point,cell['center']);nu=base.point(cell['driver_center'])
        d=[mp.mpf(0)]*12
        for n in range(3,12):
            d[n]=base.derivative(t,lam,mu,nu,n)
            if not inside(d[n],cell['central_derivatives'][n]):raise ArithmeticError((i,n))
        mup=d[6]/(4*d[4]);lp=(4*d[5]*mup-d[7])/(16*d[3])
        tp=(d[8]/64+d[4]*lp/4-d[6]*mup/16)/d[3]
        g={n:d[n+1]*tp-d[n+2]*lp/4+d[n+4]*mup/16-d[n+6]/64 for n in (3,4,5)}
        k=-d[3]/d[4]
        kp=(d[3]*g[4]-g[3]*d[4])/d[4]**2
        A3p=mp.mpf(4)/3*((g[5]*d[4]-d[5]*g[4])/d[4]**2
                            -(g[4]*d[3]-d[4]*g[3])/d[3]**2)
        b3=-32*kp;b4=96*k*A3p
        if not inside(b3,new['cells'][i]['third_derivative_at_cusp']):raise ArithmeticError('B3 mismatch')
        if not inside(b4,new['cells'][i]['fourth_at_cusp']['B4']):raise ArithmeticError('B4 mismatch')
        rows.append({'cell':i,'derivative_orders':list(range(3,12)),
                     'values':[mp.nstr(v,105) for v in d[3:]],
                     'B3':mp.nstr(b3,45),'B4':mp.nstr(b4,45),'inside_enclosures':True})
        print('Independent transport derivatives cell',i+1,'passed',flush=True)
    report={'status':'independent_transport_numerical_checks_passed','is_rigorous_certificate':False,
            'method':'mpmath 115 dps, 14 terms, 16 Gauss-Legendre panels; B4 from the cusp-tangent derivative of the cubic lambda coefficient',
            'certificate_sha256':sha(p5),'connection_certificate_sha256':sha(p3),
            'source_sha256':sha(Path(__file__)),'integrator_sha256':sha(source),
            'derivative_comparisons':27,'rows':rows,'elapsed_seconds':time.monotonic()-started}
    (HERE/'results/independent_check.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
