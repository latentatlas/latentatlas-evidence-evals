#!/usr/bin/env python3
"""Independent mpmath support for the opening-coefficient derivative."""
import hashlib
import importlib.util
import json
import time
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
R03=HERE.parent/'cusp_connection'
source=R03/'check_independent.py'
spec=importlib.util.spec_from_file_location('r03_mpmath',source)
baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inside(value,ball): return abs(value-baseline.point(ball))<baseline.rad(ball)

def main():
    mp.mp.dps=115;started=time.monotonic()
    path=HERE/'results/geometry_certificate.json';new=json.loads(path.read_text())
    oldpath=R03/'results/connection_certificate.json';old=json.loads(oldpath.read_text())
    rows=[]
    for i in (0,28,57):
        cell=old['cells'][i];t,lam,mu=list(map(baseline.point,cell['center']))
        nu=baseline.point(cell['driver_center']);d=[mp.mpf(0)]*11
        for n in range(3,11):
            d[n]=baseline.derivative(t,lam,mu,nu,n)
            if not inside(d[n],cell['central_derivatives'][n]):
                raise ArithmeticError(f'Independent derivative mismatch {i},{n}')
        mup=d[6]/(4*d[4]);lamp=(4*d[5]*mup-d[7])/(16*d[3])
        tp=(d[8]/64+d[4]*lamp/4-d[6]*mup/16)/d[3]
        g3=d[4]*tp-d[5]*lamp/4+d[7]*mup/16-d[9]/64
        g4=d[5]*tp-d[6]*lamp/4+d[8]*mup/16-d[10]/64
        C=-8*mp.sqrt(2)*d[3]/(3*d[4])
        Cp=8*mp.sqrt(2)*(d[3]*g4-g3*d[4])/(3*d[4]*d[4])
        if not inside(C,new['cells'][i]['opening_coefficient']): raise ArithmeticError('Opening mismatch')
        if not inside(Cp,new['cells'][i]['opening_shape']['Cprime']): raise ArithmeticError('Opening slope mismatch')
        rows.append({'cell':i,'derivative_orders':list(range(3,11)),
                     'values':[mp.nstr(v,105) for v in d[3:]],
                     'C':mp.nstr(C,45),'Cprime':mp.nstr(Cp,45),'all_checks_passed':True})
        print('Independent opening cell',i+1,'passed',flush=True)
    report={'status':'independent_opening_checks_passed','is_rigorous_certificate':False,
        'method':'mpmath 115 dps, 14 kernel terms, 16 Gauss-Legendre subintervals; candidate-center numerical comparison',
        'certificate_sha256':sha(path),'connection_certificate_sha256':sha(oldpath),
        'source_sha256':sha(Path(__file__)),'mpmath_integrator_sha256':sha(source),
        'rows':rows,'derivative_comparisons':24,'elapsed_seconds':time.monotonic()-started}
    (HERE/'results/independent_check.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__': main()
