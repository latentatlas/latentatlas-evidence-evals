#!/usr/bin/env python3
"""Recorded feasibility probes, not a final theorem certificate."""
import argparse,json,time
from pathlib import Path
from model_v2 import *


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=90;start=time.monotonic();mp=HERE/'results/model_v2.json';data=json.loads(mp.read_text());m=Model(data)
    T=arb('0.01');pr=list(map(arb,['1e-5','1e-10','1e-10']));rows={}
    ds=m.derivatives([zero_ball(T)]+[zero_ball(v) for v in pr],8)
    endpoints=[m.derivatives([sign*T]+[zero_ball(v) for v in pr],4) for sign in (-1,1)]
    rows['window']={'T':T,'parameter_radii':pr,'derivatives':ds,'endpoints':endpoints}
    print('Global g4',ds[4],'boundary g',*[r[0] for r in endpoints],flush=True)
    # Uniform fold surface, for |s|<=T and the physical lambda interval.
    mr=nr=20*T**3
    fd=m.derivatives([zero_ball(T),zero_ball(pr[0]),zero_ball(mr),zero_ball(nr)],8)
    f0=m.derivatives([zero_ball(T),zero_ball(pr[0]),0,0],1)
    fy=midpoint_inverse([r[1:] for r in controls(m.c,(0,1))])
    try:
        fq,fe=contraction(fy,[r[1:] for r in controls(fd,(0,1))],f0,[mr,nr])
        print('Fold surface contraction',fq,fe,flush=True)
        rows['fold_surface']={'q':fq,'eta':fe,'radii':[mr,nr],'Y':fy,'derivatives':fd}
    except ArithmeticError as e:rows['fold_surface']={'failure':str(e)};print('Fold failed',e,flush=True)
    # Uniform cusp curve, solving all three controls for each s.
    cr=[4*T*T,20*T**3,20*T**3]
    cd=m.derivatives([zero_ball(T)]+[zero_ball(v) for v in cr],9)
    c0=m.derivatives([zero_ball(T),0,0,0],2);cy=inverse(m.c)
    try:
        cq,ce=contraction(cy,controls(cd),c0[:3],cr)
        ji=arb_mat(controls(cd)).inv();v=[ji[i,2] for i in range(3)]
        rho=cd[4]-cd[3]*sum((z*u for z,u in zip(controls(cd,(3,))[0],v)),arb(0))
        print('Cusp curve contraction',cq,ce,'g3 derivative',rho,flush=True)
        rows['cusp_curve']={'q':cq,'eta':ce,'radii':cr,'Y':cy,'derivatives':cd,'g3_curve_derivative':rho}
    except (ArithmeticError,ValueError,ZeroDivisionError) as e:rows['cusp_curve']={'failure':str(e)};print('Cusp failed',e,flush=True)
    for ell in ('-1e-7','1e-7'):
        ell=arb(ell);rt=abs(ell).sqrt();v=[m.derivatives([rt*a,ell,0,0],4)[0] for a in (-3,-1,0,1,3)]
        print('lambda',ell,'g signs',v,flush=True)
    rows.update({'status':'feasibility_probe_only','model_sha256':sha(mp),'source_sha256':sha(__file__),'elapsed_seconds':time.monotonic()-start})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(pack(rows),f,indent=2);f.write('\n')


if __name__=='__main__':main()
