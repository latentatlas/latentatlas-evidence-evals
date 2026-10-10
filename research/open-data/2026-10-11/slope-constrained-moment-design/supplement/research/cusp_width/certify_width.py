#!/usr/bin/env python3
"""Certify strict nesting and finite-width monotonicity on the R04 window."""
import argparse
import json
import time
from flint import arb,ctx
from transport_model import *
from fold_jets import transport_jet
from certify_connection import cusp_tangent

def require(ok,message):
    if not ok:raise ArithmeticError(message)
def pack(v):
    if isinstance(v,arb):return serialize(v)
    if isinstance(v,list):return [pack(x) for x in v]
    if isinstance(v,dict):return {k:pack(x) for k,x in v.items()}
    return v

def certify_cell(raw,geo,index):
    cell=ExtendedCell(raw,geo,index)
    S=arb(3)/4000
    cp,cpr=cell.enclose(upto=15)
    v=cusp_tangent(cp)
    fourth=fourth_at_cusp(cell,cp)
    extra=[2*S,arb('2.22')*S*S,arb('2.10')*S*S*S]
    d,rem=cell.enclose(extra,upto=26)
    d[0]=d[1]=arb(0)
    wp=restore(geo['uniform_fold']['wprime'])
    d[2]=zero_ball(upper(wp)*S)
    jet,l,m=transport_jet(d,v[1],K=5)
    M5=upper(120*abs(jet[5]))
    B3=-32*restore(geo['opening_shape']['kprime'])
    M4=upper(abs(fourth['B4']))
    error=upper(M4*S+M5*S*S/2)
    third=B3+zero_ball(error)
    require(third>0,'Transport third derivative not positive')
    # Both folds at every 0<ell<=1e-6 lie in |s|<S by R04.
    require(arb('1.80')*S*S>arb('1e-6'),'Insufficient finite width coverage')
    rate=third/(3*arb('2.21').sqrt()*arb('2.21'))
    rate_lower=rate.lower()
    rate_upper=(third/(3*arb('1.80').sqrt()*arb('1.80'))).upper()
    require(rate_lower>arb('0.0004') and rate_upper<arb('0.0025'),
            'Readable normalized width-rate bounds failed')
    return pack({'index':index,'driver_center':cell.nu,'driver_half_width':cell.h,
        's_half_width':S,'neighborhood_half_widths':extra,
        'cusp_derivatives':cp,'cusp_remainders':cpr,'fold_derivatives':d,
        'fold_enclosure_remainders':rem,
        'extra_central_derivatives':cell.c[57:],'extra_absolute_bounds':cell.B[63:],
        'lambda_cusp_prime':v[1],'fourth_at_cusp':fourth,
        'transport_jet':jet,'lambda_fold_jet':l,'mu_fold_jet':m,
        'fifth_derivative_abs_bound':M5,'third_derivative_at_cusp':B3,
        'fourth_derivative_at_cusp_abs_bound':M4,'third_derivative_error':error,
        'third_derivative_on_fold':third,
        'normalized_width_rate_lower':rate_lower,'normalized_width_rate_upper':rate_upper})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trial',action='store_true');args=ap.parse_args()
    ctx.dps=110;started=time.monotonic();inputs=verify_inputs()
    p3=HERE.parent/'cusp_connection/results/connection_certificate.json'
    p4=HERE.parent/'cusp_geometry/results/geometry_certificate.json'
    r3=json.loads(p3.read_text());r4=json.loads(p4.read_text())
    cells=[]
    for i in ([0,28,57] if args.trial else range(58)):
        row=certify_cell(r3['cells'][i],r4['cells'][i],i);cells.append(row)
        if i%10==0 or i==57 or args.trial:
            print('cell',i+1,'third',row['third_derivative_on_fold']['enclosure'],
                  'rate_lower',row['normalized_width_rate_lower']['enclosure'],flush=True)
    report={'schema':'finite-cusp-width-v1',
        'status':'trial_passed' if args.trial else 'strict_nesting_and_finite_width_monotonicity_passed',
        'scope':'For every nu in [-29,0] and 0<ell<=1e-6, the exact-cusp-centered upper fold decreases with nu, the lower fold increases, and W_nu(ell) strictly decreases with nu.',
        'readable_normalized_rate_bounds':['0.0004','0.0025'],
        'input_packages':inputs,'connection_certificate_sha256':sha(p3),
        'geometry_certificate_sha256':sha(p4),'cells':cells,
        'source_sha256':{n:sha(HERE/n) for n in ('fold_jets.py','transport_model.py','certify_width.py')},
        'elapsed_seconds':time.monotonic()-started}
    out=HERE/('diagnostics/trial_certificate.json' if args.trial else 'results/width_certificate.json')
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'cells':len(cells),'elapsed_seconds':report['elapsed_seconds']},indent=2))

if __name__=='__main__':main()
