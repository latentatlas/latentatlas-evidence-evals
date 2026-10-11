#!/usr/bin/env python3
"""Interior numerical checks without importing FLINT or continuation code."""
import json
import hashlib
import time
from pathlib import Path
import mpmath as mp

HERE=Path(__file__).resolve().parent


def point(ball):
    m,e=ball['mid_man_exp']
    return mp.mpf(m)*mp.power(2,e)


def rad(ball):
    m,e=ball['rad_man_exp']
    return mp.mpf(m)*mp.power(2,e)


def derivative(t,lam,mu,nu,n):
    pi=mp.pi
    def f(u):
        e4=mp.exp(4*u)
        kernel=mp.fsum((2*pi*pi*k**4*mp.exp(9*u)-3*pi*k*k*mp.exp(5*u))
                      *mp.exp(-pi*k*k*e4) for k in range(1,15))
        return kernel*mp.exp(lam*u*u+mu*u**4+nu*u**6)*(2*u)**n*mp.cos(2*t*u+n*pi/2)
    return mp.quad(f,[mp.mpf(k)/8 for k in range(17)],method='gauss-legendre')


def main():
    mp.mp.dps=115
    start=time.monotonic()
    path=HERE/'results/connection_certificate.json'
    data=json.loads(path.read_text())
    rows=[]
    for index in (0,28,57):
        cell=data['cells'][index]
        t,lam,mu=list(map(point,cell['center']))
        nu=point(cell['driver_center'])
        for n in (0,1,2,3,4,6):
            expected=cell['central_derivatives'][n]
            actual=derivative(t,lam,mu,nu,n)
            diff=abs(actual-point(expected))
            radius=rad(expected)
            if not diff<radius:
                raise ArithmeticError(f'Independent derivative outside enclosure: {index}, D{n}')
            rows.append({'cell':index,'driver':cell['driver_center'],
                         'derivative':n,'value':mp.nstr(actual,104),
                         'distance_to_radius_ratio':mp.nstr(diff/radius,14),
                         'inside_enclosure':True})
        print(f'Independent cell {index+1}: six derivative checks passed',flush=True)
    report={'status':'independent_numerical_checks_passed',
            'is_rigorous_certificate':False,
            'method':'mpmath 115 dps, 14 kernel terms, Gauss-Legendre on [0,2] in 16 pieces',
            'certificate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'rows':rows,'elapsed_seconds':time.monotonic()-start}
    (HERE/'results/independent_check.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
