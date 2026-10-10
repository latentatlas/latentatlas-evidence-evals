#!/usr/bin/env python3
"""R07 uniform theorem witness; never overwrites an earlier run."""
import argparse
import json
import time
from fractions import Fraction
from pathlib import Path
from flint import arb,ctx
from robust_model import HERE,load_inputs,cell_bounds,require,restore,upper,zero_ball,pack,sha


def affine(raw,nu):
    return [restore(x)+restore(v)*(nu-restore(raw['driver_center']))
            for x,v in zip(raw['center'],raw['predictor'])]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--epsilon',default='1e-18')
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic()
    requested=Fraction(args.epsilon)
    require(0<requested<1,'Require 0 < epsilon < 1')
    epsilon=upper(arb(requested.numerator)/requested.denominator)
    packages,paths,data=load_inputs()
    cells=[]
    for i in range(58):
        raw=data[0]['cells'][i]
        require(restore(raw['driver_center'])==-arb(2*i+1)/4,'Driver cover changed')
        require(restore(raw['driver_half_width'])==arb(1)/4,'Driver half-width changed')
        cells.append(cell_bounds(*(d['cells'][i] for d in data),i,epsilon))
        if i%10==0 or i==57:print('R07 uniform cell',i+1,'of 58 passed',flush=True)
    seams=[]
    for i in range(57):
        a,b=data[0]['cells'][i:i+2]
        nu=restore(a['driver_left'])
        require(nu==restore(b['driver_right']),'Driver gap')
        left,right=affine(a,nu),affine(b,nu)
        tight=list(map(restore,cells[i]['contraction']['tight']))
        radii=list(map(restore,b['radii']))
        ratios=[upper((abs(x-y)+r)/R) for x,y,r,R in zip(left,right,tight,radii)]
        require(all(v<1 for v in ratios),'Perturbed root containment at seam failed')
        seams.append(pack({'left_index':i,'driver':nu,'containment_ratios':ratios}))
    ends={}
    for key,i,nu in (('nu_0',0,arb(0)),('nu_minus_29',57,arb(-29))):
        values=affine(data[0]['cells'][i],nu)
        ball=[v+zero_ball(restore(r)) for v,r in zip(values,cells[i]['contraction']['tight'])]
        ends[key]=pack(ball)
    require(restore(ends['nu_0'][2])>0 and restore(ends['nu_minus_29'][2])<0,
            'Unique sextic crossing endpoint signs failed')
    displacement=max(restore(x) for c in cells for x in c['contraction']['displacement'])
    require(displacement<arb('4e-5'),'Readable cusp displacement failed')
    result={'schema':'R07-uniform-relative-kernel-perturbation-v1',
        'status':'arb_uniform_bounds_passed',
        'perturbation_class':'One fixed real measurable h(u), independent of all four controls, |h(u)| <= epsilon a.e.; extend h evenly to the real line; Phi_h=Phi*(1+h).',
        'epsilon_requested_rational':str(requested),'epsilon_proof_upper':pack(epsilon),
        'scope':'nu in [-29,0]; one connected cusp arc in the specified tubes, full local root box, decreasing-nu outward fold motion in each perturbed cusp-centered original coordinate system.',
        'trust_boundary':'Frozen original-kernel integral jets/absolute moment bounds and the stated analytic perturbation and local-geometry lemmas; arbitrary h is bounded analytically, never quadrature-sampled.',
        'input_packages':packages,'input_certificates':{str(p.relative_to(HERE.parent)):sha(p) for p in paths},
        'source_sha256':{p:sha(HERE/p) for p in ('robust_model.py','certify_robustness.py')},
        'cells':cells,'seams':seams,'endpoint_enclosures':ends,
        'uniform_displacement':pack(displacement),
        'readable_bounds':{'T':'0.003','L':'1e-6','M':'2e-9','mu_prime':['0.26','0.34'],
             'normalized_width_rate':['0.0003','0.003'],'cusp_displacement_each_coordinate':'4e-5',
             'sextic_crossing_driver_displacement':'2e-4'},
        'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('58 cells and 57 joins passed; displacement < 4e-5; output',args.output,flush=True)


if __name__=='__main__':main()
