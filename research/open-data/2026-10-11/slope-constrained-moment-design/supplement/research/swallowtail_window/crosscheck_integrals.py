#!/usr/bin/env python3
"""Direct deformed-integral checks at nonzero original control offsets."""
import argparse,json,time
from pathlib import Path
import mpmath as mp
from model_v2 import *
from shape_model import Kernel


def mpv(v):
    a,e=v['mid_man_exp'];return mp.mpf(a)*mp.power(2,e)
def mpi(v):
    a,e=v['rad_man_exp'];r=mp.mpf(a)*mp.power(2,e);m=mpv(v);return m-r,m+r
def numerical(point,raw,design,n,dps):
    with mp.workdps(dps):
        s,l,m,nu=map(mpv,point);x=list(map(mpv,raw['center']))
        t,lam,mu=x[0]+s,x[1]+l,x[2]+m
        eps=mpv(raw['epsilon4']);scale=mpv(raw['normalizing_multiplier'])
        w=list(map(mpv,design['weights']));freq=design['frequencies'];pi=mp.pi
        def f(u):
            e4,e5,e9=mp.exp(4*u),mp.exp(5*u),mp.exp(9*u)
            phi=mp.fsum((2*pi*pi*k**4*e9-3*pi*k*k*e5)*mp.exp(-pi*k*k*e4) for k in range(1,17))
            h=mp.fsum(v*mp.cos(2*j*u) for j,v in zip(freq,w));z=2*t*u
            trig=(mp.cos(z),-mp.sin(z),-mp.cos(z),mp.sin(z))[n%4]
            return scale*phi*mp.exp(lam*u*u+mu*u**4+nu*u**6)*(1+eps*h)*(2*u)**n*trig
        return mp.quad(f,[mp.mpf(j)/8 for j in range(17)])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;mp.mp.dps=125;start=time.monotonic()
    jp=HERE/'results/model_v2.json';sp=HERE/'results/sample_certificate.json'
    raw=json.loads(jp.read_text());samples=json.loads(sp.read_text());m=Model(raw);k=Kernel()
    x=list(map(restore,raw['center']));qr=restore(raw['Q_radius']);eps=restore(raw['epsilon4']);scale=restore(raw['normalizing_multiplier'])
    L=arb(2)**-24;r=arb(2)**-12;T=arb(2)**-7
    points=[[-T,0,0,0],[T,arb(2)**-17,arb(2)**-34,-arb(2)**-34],
            [0,-L,0,0],[0,-L,-L*L,0],[r,L,0,0]]
    for row in samples['cusps']:
        c=list(map(restore,row['center']));points.append([c[0],L,c[1],c[2]])
    dc=list(map(restore,samples['double_fold']['center']))
    points.extend([[s,L,dc[2],dc[3]] for s in dc[:2]])
    rows=[];nums=[]
    for i,point in enumerate(points):
        point=list(map(arb,point));t,l,mu,nu=point
        boxes=m.derivatives(point,2);direct=[]
        for n in range(3):
            value=scale*k.derivative([x[0]+t,x[1]+l,x[2]+mu],nu,n,eps,kind='G',tol='1e-83',pieces=16)
            err=qr*(m.B[n+1]+m.B[n+2]/4+m.B[n+4]/16)
            value+=zero_ball(err);need((value-boxes[n]).contains(0),'Direct integral and Taylor model disagree')
            direct.append(value)
        pointsave=pack(point)
        a=numerical(pointsave,raw,k.design,0,90);b=numerical(pointsave,raw,k.design,0,115)
        lo,hi=mpi(pack(direct[0]));need(lo<b<hi and abs(a-b)<mp.mpf('1e-68'),'Independent midpoint quadrature disagreement')
        rows.append(pack({'index':i,'point':point,'direct_derivatives':direct,'Taylor_derivatives':boxes}))
        nums.append({'index':i,'order':0,'precisions':[90,115],'value':mp.nstr(b,108),
                     'precision_difference':mp.nstr(abs(a-b),15),'inside_direct_interval':True})
        print('Direct nonzero-control integral point',i,'passed',flush=True)
    out={'status':'27_rigorous_direct_integrals_and_9_two_precision_numerical_checks_passed',
        'input_sha256':{'model_v2.json':sha(jp),'sample_certificate.json':sha(sp)},
        'source_sha256':{'crosscheck_integrals.py':sha(__file__),'model_v2.py':sha(HERE/'model_v2.py')},
        'R09_kernel_source_sha256':sha(BASE/'shape_model.py'),'rows':rows,'mpmath_checks':nums,
        'trust_boundary':'The direct Arb integrations include weight/amplitude uncertainty and analytic series/domain tails; exact-Q displacement is bounded separately. Mpmath uses midpoint inputs and finite truncations and is supplementary numerical evidence.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')


if __name__=='__main__':main()
