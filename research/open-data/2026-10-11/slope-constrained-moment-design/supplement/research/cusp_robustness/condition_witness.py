#!/usr/bin/env python3
"""An explicit positive/even kernel direction with large cusp sensitivity.

Uses cos(2*a*u) and the exact frequency-shift identity. New integral
enclosures are calculated at 0 and 2*a, retaining both original tails.
The result is an infinitesimal sensitivity, not a finite-error threshold.
"""
import argparse
import json
import time
from pathlib import Path
from flint import arb,ctx
from robust_model import HERE,load_inputs,restore,upper,zero_ball,pack,sha,require
from validated_flow import derivative


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic();packages,_,_=load_inputs()
    path=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json'
    q=json.loads(path.read_text())
    x=list(map(restore,q['center_exact_dyadic']))
    radius=restore(q['root_radius']);B=list(map(restore,q['absolute_derivative_bounds']))
    ds=list(map(restore,q['root_derivative_enclosures']))
    params={1:x[1],2:x[2],3:arb(0)};a=x[0]
    shifted=[]
    for frequency in (arb(0),2*a):
        row=[]
        for n in range(3):
            value=derivative(frequency,params,n)
            error=upper(radius*(B[n+1]+B[n+2]/4+B[n+4]/16))
            row.append({'order':n,'point_integral':value,'root_translation_error':error,
                        'at_true_cusp':value+zero_ball(error)})
            print('condition integral at',float(frequency),'order',n,'done',flush=True)
        shifted.append(row)
    forcing=[(shifted[0][n]['at_true_cusp']+shifted[1][n]['at_true_cusp'])/2 for n in range(3)]
    mprime=-16*forcing[0]/ds[4]
    lprime=(4*forcing[1]+ds[5]*mprime/4)/ds[3]
    tprime=(-forcing[2]+ds[4]*lprime/4-ds[6]*mprime/16)/ds[3]
    J=[[arb(0),arb(0),ds[4]/16],
       [arb(0),-ds[3]/4,ds[5]/16],
       [ds[3],-ds[4]/4,ds[6]/16]]
    residual=[sum((v*w for v,w in zip(row,(tprime,lprime,mprime))),arb(0))+r
              for row,r in zip(J,forcing)]
    require(all(v.contains(0) for v in residual),'Implicit tangent residual excludes zero')
    require(mprime>0,'Sensitivity sign unexpectedly unresolved')
    result={'status':'certified_infinitesimal_sensitivity',
        'perturbation':'Phi_epsilon(u)=Phi(u)*(1+epsilon*cos(2*a*u)), fixed a; |epsilon|<1 gives a positive even kernel.',
        'frequency_a':pack(a),'frequency_shift_identity':'F_epsilon(t)=F(t)+epsilon*(F(t+a)+F(t-a))/2',
        'base_point':'exact R01 quartic cusp, nu=0; a is its recorded exact dyadic t-center',
        'quartic_certificate_sha256':sha(path),'input_packages':packages,
        'shifted_integrals':pack(shifted),'forcing_at_cusp':pack(forcing),
        'cusp_epsilon_derivative':pack([tprime,lprime,mprime]),
        'implicit_residual':pack(residual),
        'display_derivatives':[[float(v.lower()),float(v.upper())] for v in (tprime,lprime,mprime)],
        'source_sha256':{p:sha(HERE/p) for p in ('condition_witness.py','robust_model.py')},
        'scope':'Derivative at epsilon=0 only. No finite epsilon breakdown or optimal robustness radius is asserted.',
        'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result['display_derivatives']),flush=True)


if __name__=='__main__':main()
