#!/usr/bin/env python3
"""Finite fold widths at nine exact cusps of the physical epsilon family."""
import argparse,json,time
from math import factorial
from pathlib import Path
from flint import arb,ctx
from pinned_model import *
from endpoint_folds import EndpointTaylor,certify_sample


class PhysicalTaylor(EndpointTaylor):
    def __init__(self,kernel,row):
        self.x=list(map(restore,row['center']));self.radius=restore(row['root_radius'])
        self.nu=restore(row['nu']);self.eps=restore(row['epsilon'])
        self.half=[arb(2)**-9,arb(2)**-18,arb(2)**-28]
        params={1:self.x[1]+zero_ball(self.half[1]+self.radius),
                2:self.x[2]+zero_ball(self.half[2]+self.radius),3:self.nu}
        self.B=[upper((1+abs(self.eps))*b) for b in absolute_derivative_bounds(params,40)]
        self.central=kernel.cache(self.x,self.nu,33,self.eps)
        self.c=[d+zero_ball(self.radius*(self.B[n+1]+self.B[n+2]/4+self.B[n+4]/16))
                for n,d in enumerate(self.central)]
        self.c[:3]=[arb(0)]*3
        self.order=8;self.nmax=5;self.terms=[];self.remainder=[]
        for a in range(9):
            for b in range(9-a):
                for c in range(9-a-b):
                    value=(a,b,c,a+2*b+4*c,arb(1)/(factorial(a)*factorial(b)*factorial(c)))
                    (self.terms if a+b+c<8 else self.remainder).append(value)
    def record(self):
        return pack({'nu':self.nu,'epsilon':self.eps,'center':self.x,'root_radius':self.radius,
                     'domain_half_widths':self.half,'central_derivatives':self.central,
                     'exact_cusp_derivatives':self.c,'absolute_bounds':self.B,'order':self.order})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=100;start=time.monotonic();kernel=Kernel()
    pp=HERE/'results/point_certificates.json';points=json.loads(pp.read_text());models=[];samples=[]
    for row in points['rows']:
        if float(restore(row['nu'])) not in (0,-15,-29):continue
        model=PhysicalTaylor(kernel,row);idx=len(models);models.append(model.record())
        for j in range(1,9):
            ell=arb(j*j)/(1000000*64)
            hi=certify_sample(model,ell,-1);lo=certify_sample(model,ell,1)
            W=restore(hi['root_enclosures'][1])-restore(lo['root_enclosures'][1])
            samples.append(pack({'model':idx,'j':j,'ell':ell,'upper':hi,'lower':lo,
                                 'width':W,'normalized_width':W/(ell*ell.sqrt())}))
        print('Finite fold model',idx,float(model.nu),float(model.eps),'passed',flush=True)
    comparisons=[]
    for group in range(3):
        for j in range(1,9):
            low=next(r for r in samples if r['model']==3*group and r['j']==j)
            high=next(r for r in samples if r['model']==3*group+2 and r['j']==j)
            change=100*(restore(high['width'])/restore(low['width'])-1)
            if not change<0:raise ArithmeticError('Finite width ordering failed')
            comparisons.append(pack({'nu':restore(models[3*group]['nu']),'j':j,
                'ell':restore(low['ell']),'W_percent_plus_half_vs_minus_half':change}))
    report={'status':'144_finite_fold_contractions_passed','models':models,'samples':samples,'comparisons':comparisons,
            'point_certificate_sha256':sha(pp),'source_sha256':{n:sha(HERE/n) for n in ('certify_fold_samples.py','pinned_model.py')},
            'frozen_fold_engine_sha256':sha(HERE.parent/'cusp_width/endpoint_folds.py'),
            'scope':'Eight positive ell samples, both folds at nu=0,-15,-29 and epsilon=-1/2,0,1/2. The continuum monotonicity is established separately by family_certificate.json.',
            'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')


if __name__=='__main__':main()
