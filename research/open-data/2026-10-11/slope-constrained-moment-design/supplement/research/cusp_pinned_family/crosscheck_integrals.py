#!/usr/bin/env python3
"""Selected new H jets by frequency shifts and separate mpmath integrals."""
import argparse,json,time
from pathlib import Path
import mpmath as mp
from flint import arb,ctx
from pinned_model import HERE,Kernel,restore,pack,sha
from validated_flow import derivative


def mpvalue(v):
    a,e=v['mid_man_exp'];return mp.mpf(a)*mp.power(2,e)
def mpinterval(v):
    m=mpvalue(v);r,e=v['rad_man_exp'];r=mp.mpf(r)*mp.power(2,e)
    return m-r,m+r


def direct(row,weights,n,dps):
    with mp.workdps(dps):
        t,lam,mu=[mpvalue(v) for v in row['center']];nu=mpvalue(row['driver_center'])
        ws=[mpvalue(v) for v in weights];p=mp.pi
        def fun(u):
            e4,e5,e9=mp.exp(4*u),mp.exp(5*u),mp.exp(9*u)
            phi=mp.fsum((2*p*p*j**4*e9-3*p*j*j*e5)*mp.exp(-p*j*j*e4) for j in range(1,17))
            h=mp.fsum(w*mp.cos(2*j*u) for j,w in enumerate(ws,1))
            phase=2*t*u
            trig=(mp.cos(phase),-mp.sin(phase),-mp.cos(phase),mp.sin(phase))[n%4]
            return phi*mp.exp(lam*u*u+mu*u**4+nu*u**6)*h*(2*u)**n*trig
        return mp.quad(fun,[mp.mpf(j)/8 for j in range(17)])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;mp.mp.dps=120;start=time.monotonic();kernel=Kernel();shifted=[];numerical=[]
    for i in (0,28,57):
        path=HERE/'cache'/f'cell_{i:02}.json';row=json.loads(path.read_text())
        t,lam,mu=map(restore,row['center']);nu=restore(row['driver_center'])
        for n in (0,1,2,3,4,26,68):
            value=arb(0)
            for j,w in enumerate(kernel.weights,1):
                value+=w/2*sum((derivative(t+sign*j,{1:lam,2:mu,3:nu},n,
                    N=18,pieces=16,abs_tol='1e-85',rel_tol='1e-85') for sign in (-1,1)),arb(0))
            old=restore(row['H_derivatives'][n])
            if not (value-old).contains(0):raise ArithmeticError('Shift identity integral disagreement')
            shifted.append(pack({'cell':i,'order':n,'frequency_shift_integral':value,
                                 'direct_cache_integral':old,'cache_sha256':sha(path)}))
        print('Rigorous frequency-shift comparison cell',i,'passed',flush=True)
        for n in (0,3,8):
            a=direct(row,kernel.pinned['weights'],n,90);b=direct(row,kernel.pinned['weights'],n,115)
            lo,hi=mpinterval(row['H_derivatives'][n])
            if not (lo<b<hi and abs(a-b)<mp.mpf('1e-80')):raise ArithmeticError('Separate numerical integral disagreement')
            numerical.append({'cell':i,'order':n,'dps':[90,115],'value':mp.nstr(b,105),
                'precision_difference':mp.nstr(abs(a-b),12),'inside_rigorous_cache_ball':True})
        print('Separate mpmath comparison cell',i,'passed',flush=True)
    report={'status':'21_rigorous_shift_and_9_separate_numerical_checks_passed',
            'rigorous_shift_comparisons':shifted,'mpmath_checks':numerical,
            'scope':'Selected checks, not a replacement for all 4002 rigorous H integrations. mpmath is a non-rigorous precision-stability check with midpoint inputs and finite truncation; the Arb integrations include analytic series and infinite-domain tails.',
            'source_sha256':{n:sha(HERE/n) for n in ('crosscheck_integrals.py','pinned_model.py')},
            'kernel_certificate_sha256':sha(kernel.pinned_path),'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')


if __name__=='__main__':main()
