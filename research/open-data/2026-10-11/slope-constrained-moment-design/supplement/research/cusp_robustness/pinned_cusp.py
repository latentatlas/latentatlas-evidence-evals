#!/usr/bin/env python3
"""An exact three-moment null direction, with finite-amplitude cusp bounds.

The direction is defined by cofactors of exact integrals at the exact
quartic cusp, not by rounded numerical coefficients. Laplace expansion
annihilates the three cusp equations identically for every amplitude.
"""
import argparse
import json
import time
from pathlib import Path
from flint import arb,arb_mat,ctx
from robust_model import HERE,load_inputs,restore,upper,zero_ball,pack,sha,require
from validated_flow import derivative


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic();packages,_,_=load_inputs()
    path=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json'
    old=json.loads(path.read_text());x=list(map(restore,old['center_exact_dyadic']))
    r=restore(old['root_radius']);B=list(map(restore,old['absolute_derivative_bounds']))
    ds=list(map(restore,old['root_derivative_enclosures']))
    frequencies=(1,2,3,4);params={1:x[1],2:x[2],3:arb(0)}
    moments=[[arb(0) for _ in frequencies] for _ in range(5)];integrals=[]
    for j,a in enumerate(frequencies):
        pair=[]
        for sign in (-1,1):
            row=[]
            for n in range(5):
                val=derivative(x[0]+sign*a,params,n)
                err=upper(r*(B[n+1]+B[n+2]/4+B[n+4]/16))
                enclosed=val+zero_ball(err);moments[n][j]+=enclosed/2
                row.append({'order':n,'point':val,'root_error':err,'at_exact_cusp':enclosed})
            pair.append(row)
        integrals.append(pair);print('pinned direction frequency',a,'integrals done',flush=True)
    cofactors=[]
    for j in range(4):
        minor=[[moments[n][k] for k in range(4) if k!=j] for n in range(3)]
        cofactors.append((-1)**j*arb_mat(minor).det())
    require(all(not a.contains(0) for a in cofactors),'Cofactor signs unresolved')
    norm=sum((abs(a) for a in cofactors),arb(0));require(norm>0,'Zero cofactor vector')
    weights=[a/norm for a in cofactors]
    forces=[sum((w*m for w,m in zip(weights,row)),arb(0)) for row in moments]
    require(all(v.contains(0) for v in forces[:3]),'Moment cancellation residual excludes zero')
    amplitude=arb(1)/2
    d3=ds[3]+zero_ball(amplitude*abs(forces[3]))
    d4=ds[4]+zero_ball(amplitude*abs(forces[4]))
    require(d3>0 and d4<0,'Finite-amplitude cusp nondegeneracy not proved')
    result={'status':'finite_amplitude_exact_cusp_pinning_certified',
        'definition':'M_nj = integral Phi exp(lambda_Q*u^2+mu_Q*u^4) cos(2*j*u) (2*u)^n cos(2*t_Q*u+n*pi/2) du at the EXACT Q; j=1,2,3,4. alpha_j=(-1)^(j-1) det(M_0:2,columns_except_j); w_j=alpha_j/sum|alpha|; h=sum w_j cos(2*j*u).',
        'normalization':'sum_j |w_j|=1 exactly by definition; hence |h|<=1. Numerical printed coefficients are not the definition.',
        'moment_annihilation':'M_0:2 * alpha=0 exactly by the alternating-minor identity; therefore G_epsilon(Q)=D1 G_epsilon(Q)=D2 G_epsilon(Q)=0 for every real epsilon.',
        'scope':'For |epsilon|<=1/2, Phi*(1+epsilon*h) remains positive/even and Q remains a nondegenerate cusp in the nu=0 section. Does NOT assert persistence of the entire arc or its finite root window at these larger amplitudes.',
        'input_packages':packages,'quartic_certificate_sha256':sha(path),'frequencies':list(frequencies),
        'source_sha256':{p:sha(HERE/p) for p in ('pinned_cusp.py','robust_model.py')},
        'shifted_integrals':pack(integrals),'moments':pack(moments),'cofactors':pack(cofactors),
        'normalizing_sum':pack(norm),'weights':pack(weights),'moment_response':pack(forces),
        'amplitude_interval':pack(zero_ball(amplitude)),'D3_finite_amplitude':pack(d3),'D4_finite_amplitude':pack(d4),
        'response_ratios':pack([abs(forces[3]/ds[3]),abs(forces[4]/ds[4])]),
        'display_weights':[float(w.mid()) for w in weights],
        'display_relative_D3_D4_response':[float(upper(abs(forces[n]/ds[n]))) for n in (3,4)],
        'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'weights':result['display_weights'],'ratios':result['display_relative_D3_D4_response']}),flush=True)


if __name__=='__main__':main()
