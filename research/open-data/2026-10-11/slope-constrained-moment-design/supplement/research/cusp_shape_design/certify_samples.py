#!/usr/bin/env python3
"""Direct finite fold widths, with an equal-amplitude old-direction comparison."""
import argparse,json,time
from pathlib import Path
from math import factorial
from flint import arb,ctx
from shape_model import *
from endpoint_folds import EndpointTaylor,certify_sample
from pinned_model import Kernel as ReferenceKernel


class SampleTaylor(EndpointTaylor):
    def __init__(self,data,eps,H=None):
        self.eps=eps;self.F=list(map(restore,data['F_at_exact_Q']))
        self.H=list(map(restore,data['H_at_exact_Q'])) if H is None else H
        self.c=[f+eps*h for f,h in zip(self.F,self.H)];self.c[:3]=[arb(0)]*3
        self.B=[upper((1+abs(eps))*restore(b)) for b in data['absolute_F_bounds']]
        self.half=[arb(2)**-9,arb(2)**-18,arb(2)**-28];self.order=8;self.nmax=5
        self.terms=[];self.remainder=[]
        for a in range(9):
            for b in range(9-a):
                for c in range(9-a-b):
                    row=(a,b,c,a+2*b+4*c,arb(1)/(factorial(a)*factorial(b)*factorial(c)))
                    (self.terms if a+b+c<8 else self.remainder).append(row)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic();jp=HERE/'results/local_jets.json';data=json.loads(jp.read_text())
    ref=ReferenceKernel();x=list(map(restore,data['center']));r=restore(data['root_radius']);B=list(map(restore,data['absolute_F_bounds']))
    Href=[];refpoints=[]
    for n in range(34):
        value=ref.derivative(x,0,n,kind='H',tol='1e-83',pieces=16)
        refpoints.append(value);Href.append(value+zero_ball(r*(B[n+1]+B[n+2]/4+B[n+4]/16)))
    Href[:3]=[arb(0)]*3
    models=[];samples=[]
    params=[('selected',arb(j)/512) for j in range(-4,5)]+[('reference',-arb(1)/128),('reference',arb(1)/128)]
    for idx,(label,eps) in enumerate(params):
        model=SampleTaylor(data,eps,Href if label=='reference' else None)
        models.append(pack({'direction':label,'epsilon':eps,'cusp_derivatives':model.c,'absolute_bounds':model.B,
                            'local_domain':model.half,'order':model.order}))
        for j in range(1,9):
            ell=arb(j*j)/(64*1000000);hi=certify_sample(model,ell,-1);lo=certify_sample(model,ell,1)
            W=restore(hi['root_enclosures'][1])-restore(lo['root_enclosures'][1])
            samples.append(pack({'model':idx,'j':j,'ell':ell,'upper':hi,'lower':lo,'width':W}))
        print('Finite folds',label,'amplitude',eps,'passed',flush=True)
    comparisons=[]
    for label,minus,plus in (('selected',0,8),('reference',9,10)):
        for j in range(1,9):
            wm=restore(next(r['width'] for r in samples if r['model']==minus and r['j']==j))
            wp=restore(next(r['width'] for r in samples if r['model']==plus and r['j']==j))
            change=100*(wp/wm-1);need(change<0,'Finite narrowing not established')
            comparisons.append(pack({'direction':label,'j':j,'change_percent':change}))
            if j==8:print(label,'finite percent change at ell=1e-6',change,flush=True)
    report=pack({'status':'176_finite_fold_contractions_with_equal_amplitude_comparison_passed',
        'models':models,'samples':samples,'comparisons':comparisons,'reference_H_at_center':refpoints,'reference_H_at_exact_Q':Href,
        'reference_kernel_certificate_sha256':sha(ref.pinned_path),'jet_certificate_sha256':sha(jp),
        'source_sha256':{n:sha(HERE/n) for n in ('certify_samples.py','shape_model.py')},
        'scope':'Both directions compared at exactly epsilon=+-1/128; samples are exact-Q centered. Continuum monotonicity for selected direction is in local_certificate.json.',
        'elapsed_seconds':time.monotonic()-start})
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')


if __name__=='__main__':main()
