#!/usr/bin/env python3
"""Independent numerical support: no FLINT or Taylor engine imported."""
import hashlib
import json
import time
from pathlib import Path
import mpmath as mp

HERE=Path(__file__).resolve().parent


def center(ball):
    m,e=ball['mid_man_exp']
    return mp.mpf(m)*mp.power(2,e)


def radius(ball):
    m,e=ball['rad_man_exp']
    return mp.mpf(m)*mp.power(2,e)


def integral(t,lam,mu,n):
    pi=mp.pi
    def f(u):
        e4=mp.exp(4*u)
        kernel=mp.fsum((2*pi*pi*k**4*mp.exp(9*u)-3*pi*k*k*mp.exp(5*u))
                      *mp.exp(-pi*k*k*e4) for k in range(1,15))
        return kernel*mp.exp(lam*u*u+mu*u**4)*(2*u)**n*mp.cos(2*t*u+n*pi/2)
    return mp.quad(f,[mp.mpf(k)/8 for k in range(17)],method='gauss-legendre')


def main():
    mp.mp.dps=115
    started=time.monotonic()
    path=HERE/'results/region_certificate.json'
    data=json.loads(path.read_text())
    x=list(map(center,data['center_exact_dyadic']))
    rows=[]
    for sample in data['independent_check_inputs']:
        offsets=list(map(center,sample['offsets']))
        t,lam,mu=[a+b for a,b in zip(x,offsets)]
        for key,enclosure in sample['derivatives'].items():
            n=int(key)
            value=integral(t,lam,mu,n)
            diff=abs(value-center(enclosure))
            rad=radius(enclosure)
            passed=diff<rad
            print(f"offset sign {mp.sign(offsets[0])}, D{n}: "
                  f"distance/radius={mp.nstr(diff/rad,7)}, pass={passed}",flush=True)
            if not passed:
                raise ArithmeticError('Independent value outside Taylor enclosure')
            rows.append({'offsets_exact_dyadic':sample['offsets'],'derivative':n,
                         'value':mp.nstr(value,104),
                         'absolute_midpoint_difference':mp.nstr(diff,14),
                         'difference_to_radius_ratio':mp.nstr(diff/rad,14),
                         'inside_recorded_enclosure':bool(passed)})
    report={'status':'independent_numerical_checks_passed',
            'is_rigorous_certificate':False,
            'method':'mpmath 115 dps, 14 kernel terms, Gauss-Legendre on [0,2] in 16 real pieces; numerical support only',
            'mpmath_version':mp.__version__,
            'certificate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'rows':rows,'elapsed_seconds':time.monotonic()-started}
    (HERE/'results/independent_check.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
