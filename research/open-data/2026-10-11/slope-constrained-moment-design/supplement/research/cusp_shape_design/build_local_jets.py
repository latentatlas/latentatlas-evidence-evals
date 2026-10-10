#!/usr/bin/env python3
"""Direct F/H integrals at Q through order 54, with exact-root uncertainty."""
import argparse,json,time
from pathlib import Path
from flint import arb,ctx
from shape_model import *
from moment_dictionary import verify


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic();inputs=verify();kernel=Kernel()
    x=list(map(restore,kernel.q['center_exact_dyadic']));r=restore(kernel.q['root_radius'])
    domain=[arb(2)**-7,arb(2)**-10,arb(2)**-17]
    B=absolute_derivative_bounds({1:x[1]+zero_ball(domain[1]+r),2:x[2]+zero_ball(domain[2]+r),3:arb(0)},58)
    F=[];H=[];fpoint=[];hpoint=[]
    for n in range(55):
        f=kernel.derivative(x,0,n,kind='F');h=kernel.derivative(x,0,n,kind='H')
        err=upper(r*(B[n+1]+B[n+2]/4+B[n+4]/16))
        fpoint.append(f);hpoint.append(h);F.append(f+zero_ball(err));H.append(h+zero_ball(err))
        if n<9:
            need((H[-1]-restore(kernel.design['moment_response'][n])).contains(0),'Direct H/shifted dictionary disagree')
            need((F[-1]-restore(kernel.q['root_derivative_enclosures'][n])).contains(0),'Direct F/frozen root derivative disagree')
        if n%10==0:print('Direct local jet order',n,'done',flush=True)
    # Exact identities at the proved Q, not small-residual assumptions.
    F[:3]=[arb(0)]*3;H[:3]=[arb(0)]*3
    report=pack({'status':'55_direct_F_and_H_jets_with_exact_Q_enclosures',
        'input_packages':inputs,'design_certificate_sha256':sha(kernel.design_path),
        'source_sha256':{n:sha(HERE/n) for n in ('shape_model.py','build_local_jets.py')},
        'F_at_center':fpoint,'H_at_center':hpoint,'F_at_exact_Q':F,'H_at_exact_Q':H,
        'absolute_F_bounds':B,'center':x,'root_radius':r,'local_majorant_domain':domain,
        'quadrature':{'dps':110,'tolerance':'1e-83','terms':16,'panels':16,'cutoff':2},
        'direct_shift_crosschecks':9,'elapsed_seconds':time.monotonic()-start})
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')


if __name__=='__main__':main()
