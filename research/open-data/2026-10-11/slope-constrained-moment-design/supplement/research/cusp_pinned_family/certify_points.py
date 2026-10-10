#!/usr/bin/env python3
"""Narrow physical-family cusp boxes, for quantitative comparisons/figures."""
import argparse,json,time
from pathlib import Path
from flint import arb,arb_mat,ctx
from pinned_model import *
from validated_flow import hessian_bound


def point(kernel,seed,nu,eps):
    x,d,Y,err,steps=kernel.refine(seed,nu,eps)
    R=arb(2)**-74
    B=[upper((1+abs(eps))*v) for v in absolute_derivative_bounds(
       {1:x[1]+zero_ball(R),2:x[2]+zero_ball(R),3:nu},14)]
    q0=norm_mat([[arb(i==j)-z for j,z in enumerate(row)] for i,row in enumerate(matmul(Y,J(d)))])
    M2=hessian_bound(B,[0,1,2],[1,2,4],[arb(1),-arb(1)/4,arb(1)/16])
    eta=norm_vec(matvec(Y,d[:3]));q=upper(q0+norm_mat(Y)*M2*R)
    if not (q<1 and eta+q*R<R and not arb_mat(Y).det().contains(0)):raise ArithmeticError('Point contraction failed')
    tight=upper(eta/(1-q))
    cp=[v+zero_ball(tight*(B[n+1]+B[n+2]/4+B[n+4]/16)) for n,v in enumerate(d)]
    if not (cp[3]>0 and cp[4]<0):raise ArithmeticError('Point cusp rank failed')
    C,Cnu=opening(cp)
    return pack({'nu':nu,'epsilon':eps,'center':x,'radius':R,'point_derivatives':d,
                 'absolute_bounds':B,'preconditioner':Y,'q0':q0,'M2':M2,'eta':eta,'q':q,
                 'root_radius':tight,'cusp_derivatives':cp,'C':C,'C_nu':Cnu,'newton_steps':steps})


def identify(row,sheet,old):
    nu=restore(row['nu']);eps=restore(row['epsilon']);rho=eps/(1+restore(sheet['alpha'])*eps)
    i=min(57,int(-2*float(nu)));raw=old['cells'][i]
    slab=next(s for s in sheet['slabs'] if rho>=restore(s['left']) and rho<=restore(s['right']))
    wide=slab['cells'][i];r=restore(row['root_radius']);ratios=[]
    for x,a,v,u,R in zip(row['center'],raw['center'],raw['predictor'],wide['rho_predictor'],raw['radii']):
        center=restore(a)+restore(v)*(nu-restore(raw['driver_center']))+restore(u)*rho
        ratio=upper((abs(restore(x)-center)+r)/restore(R))
        if not ratio<1:raise ArithmeticError('Point root not inside sheet uniqueness box')
        ratios.append(ratio)
    row['sheet_identification']=pack({'cell':i,'slab':slab['index'],'rho':rho,'ratios':ratios})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=100;start=time.monotonic();inputs=verify_inputs();kernel=Kernel()
    old=json.loads((HERE.parent/'cusp_connection/results/connection_certificate.json').read_text())
    sheetpath=HERE/'results/family_certificate.json';sheet=json.loads(sheetpath.read_text())
    rows=[]
    for nu in map(arb,(0,-5,-10,-15,-20,-25,-29)):
        i=min(57,int(-2*float(nu)));raw=old['cells'][i]
        seed=[restore(x)+restore(v)*(nu-restore(raw['driver_center'])) for x,v in zip(raw['center'],raw['predictor'])]
        for eps in (-arb(1)/2,arb(0),arb(1)/2):
            row=point(kernel,seed,nu,eps);identify(row,sheet,old);rows.append(row)
            print('Physical point',float(nu),float(eps),'C',restore(row['C']),flush=True)
    comparisons=[]
    for i in range(0,len(rows),3):
        low,base,high=rows[i:i+3]
        comparisons.append(pack({'nu':restore(base['nu']),
            'C_percent_plus_half_vs_minus_half':100*(restore(high['C'])/restore(low['C'])-1),
            'mu_displacement_minus_half':restore(low['center'][2])-restore(base['center'][2])+zero_ball(restore(low['root_radius'])+restore(base['root_radius'])),
            'mu_displacement_plus_half':restore(high['center'][2])-restore(base['center'][2])+zero_ball(restore(high['root_radius'])+restore(base['root_radius']))}))
    report={'status':'21_point_contractions_and_sheet_identifications_passed','rows':rows,'comparisons':comparisons,
        'scope':'C is the leading coefficient in W=C ell^(3/2)+O(ell^2); its displayed percentage is not an exact finite-window width percentage.',
        'input_packages':inputs,'family_certificate_sha256':sha(sheetpath),
        'source_sha256':{n:sha(HERE/n) for n in ('pinned_model.py','certify_points.py')},
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')


if __name__=='__main__':main()
