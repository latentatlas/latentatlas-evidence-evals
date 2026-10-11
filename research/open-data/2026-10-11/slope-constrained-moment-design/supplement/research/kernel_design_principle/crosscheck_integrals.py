#!/usr/bin/env python3
"""Product-form Arb quadrature and separate two-precision mpmath checks."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent/'cusp_shape_design'
sys.path.insert(0,str(BASE))
from shape_model import Kernel
from moment_dictionary import restore,pack,upper,zero_ball,sha
from flint import arb,ctx
import mpmath as mp


def need(value,message):
    if not value:
        raise ArithmeticError(message)


def midpoint(v):
    m,e = v['mid_man_exp']
    return mp.mpf(m)*mp.power(2,e)


def numerical(data,order,dps):
    with mp.workdps(dps):
        t,lam,mu = map(midpoint,data['center'])
        weights = list(map(midpoint,data['weights']))
        def integrand(u):
            e4=mp.exp(4*u)
            phi=sum((2*mp.pi**2*k**4*mp.exp(9*u)-3*mp.pi*k*k*mp.exp(5*u))*mp.exp(-mp.pi*k*k*e4) for k in range(1,17))
            h=sum(w*mp.cos(2*j*u) for w,j in zip(weights,data['frequencies']))
            phase=2*t*u
            trig=(mp.cos(phase),-mp.sin(phase),-mp.cos(phase),mp.sin(phase))[order%4]
            return phi*mp.exp(lam*u*u+mu*u**4)*(1+h)*(2*u)**order*trig
        return +mp.quad(integrand,[mp.mpf(k)/16 for k in range(33)])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    need(not args.output.exists(),'Refuse to overwrite recorded result')
    start=time.monotonic();ctx.dps=110
    path=HERE/'results/candidate_certificate.json';data=json.loads(path.read_text())
    qp=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';q=json.loads(qp.read_text())
    x=list(map(restore,data['center']));r=restore(data['Q_radius'])
    B=list(map(restore,q['absolute_derivative_bounds']))
    kernel=Kernel();kernel.weights=list(map(restore,data['weights']));kernel.freq=data['frequencies']
    cost=restore(data['feasible_coefficient_l1_cost']);factor=1+upper(cost)
    rows=[]
    for n in range(9):
        # The reused integrator's tail factor is 2, safely above 1+||h||inf.
        value=kernel.derivative(x,arb(0),n,arb(1),kind='G',tol='1e-93',pieces=8)
        direct=value+zero_ball(upper(factor*r*(B[n+1]+B[n+2]/4+B[n+4]/16)))
        saved=restore(data['modified_derivatives'][n])
        need(direct.overlaps(saved),'Direct product integral mismatch')
        row={'order':n,'direct_at_center':value,'direct_at_exact_Q':direct,'spectral_design_value':saved}
        if n in (0,3,4):
            a,b=numerical(data,n,90),numerical(data,n,115)
            with mp.workdps(120):
                delta=abs(a-b)
                need(delta<mp.mpf('1e-78'),'Two-precision numerical mismatch')
                mm,ee=pack(value)['mid_man_exp'];rr,re=pack(value)['rad_man_exp']
                mid=mp.mpf(mm)*mp.power(2,ee);radius=mp.mpf(rr)*mp.power(2,re)
                need(abs(b-mid)<=radius,'Numerical value outside direct interval')
                row['mpmath']={'precisions':[90,115],'value':mp.nstr(b,108),'precision_difference':mp.nstr(delta,15),'inside_direct_interval':True}
        rows.append(row)
    report={'status':'9_direct_product_integrals_and_3_two_precision_numerical_checks_passed',
            'certificate_sha256':sha(path),'R01_certificate_sha256':sha(qp),
            'source_sha256':{'crosscheck_integrals.py':sha(__file__),'../cusp_shape_design/shape_model.py':sha(BASE/'shape_model.py')},
            'rows':pack(rows), 'elapsed_seconds':time.monotonic()-start,
            'scope':'New candidate only. Spectral-shift construction compared to direct product integration. Numerical midpoint/finite-truncation checks are support, not rigorous enclosures or exact pinning proofs.'}
    with args.output.open('x') as stream:
        json.dump(report,stream,indent=2);stream.write('\n')
    print(report['status'])


if __name__=='__main__':
    main()
