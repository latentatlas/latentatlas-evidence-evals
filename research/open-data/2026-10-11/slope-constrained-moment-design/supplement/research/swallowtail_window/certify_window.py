#!/usr/bin/env python3
"""A complete finite multiple-root parametrization and open 0/2/4 witnesses."""
import argparse,json,time
from pathlib import Path
from model_v2 import *


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=100;start=time.monotonic();mp=HERE/'results/model_v2.json';raw=json.loads(mp.read_text());m=Model(raw)
    T=arb(2)**-7;P=[arb(2)**-17,arb(2)**-34,arb(2)**-34]
    X=[zero_ball(T)]+[zero_ball(v) for v in P]
    ds=m.derivatives(X,8);need(ds[4]>22 and ds[4]<26,'Fourth derivative bound')
    endpoints=[m.derivatives([sign*T]+X[1:],4) for sign in (-1,1)]
    for sign,row in zip((-1,1),endpoints):
        need(row[0]>arb('1e-9'),'Root-window boundary not positive')
        need(sign*row[1]>arb('1e-6'),'Derivative-window boundary sign')
    global_box={'T':T,'parameter_radii':P,'derivatives':ds,'endpoints':endpoints,
        'readable_fourth_derivative_bounds':[22,26],
        'root_count_rule':'Off the root discriminant, count sign changes in the ordered sequence g(-T), g(r_1),...,g(r_k),g(T), where r_i are all distinct stationary points in (-T,T). Each intervening interval is strictly monotone. There are at most three stationary points and at most four zeros with multiplicity; the endpoint values are positive, so the simple-zero count is 0,2 or 4.'}
    R=[4*T*T,32*T**3,32*T**3]
    AX=[zero_ball(T)]+[zero_ball(v) for v in R]
    ad=m.derivatives(AX,9)
    # Entire fold surface: every (s,lambda) in this auxiliary rectangle
    # has one (mu,nu) in the common auxiliary box, so all multiple roots
    # of the physical control box belong to the parametrization.
    fy=midpoint_inverse([r[1:] for r in controls(m.c,(0,1))])
    f0=m.derivatives([zero_ball(T),zero_ball(R[0]),0,0],1)
    fq,fe=contraction(fy,[r[1:] for r in controls(ad,(0,1))],f0,R[1:])
    fold={'Y':fy,'q':fq,'eta':fe,'derivatives':ad,'central_equations':f0,
        'radii_mu_nu':R[1:],'lambda_radius':R[0]}
    # Entire cusp curve: for each s solve (g,g_t,g_tt)=0 in all controls.
    cy=inverse(m.c);c0=m.derivatives([zero_ball(T),0,0,0],2)
    cq,ce=contraction(cy,controls(ad),c0,R)
    ci=arb_mat(controls(ad)).inv();v=[ci[i,2] for i in range(3)]
    slope=ad[4]-ad[3]*sum((z*u for z,u in zip(controls(ad,(3,))[0],v)),arb(0))
    need(slope>16 and slope<32,'Cusp G3 monotonicity not established')
    need(v[0]<-arb('0.1') and v[0]>-arb('0.24'),'Cusp lambda direction unresolved')
    growth=-v[0]*slope/2
    need(growth>arb('0.8') and growth<4,'Readable cusp quadratic bounds')
    cusp={'Y':cy,'q':cq,'eta':ce,'radii':R,'central_equations':c0,
        'inverse_last_column':v,'G3_along_curve_derivative':slope,
        'lambda_quadratic_coefficient_bounds':growth,
        'readable_lambda_quadratic_bounds':['0.8','4'],
        'meaning':'The unique control curve p_c(s) satisfies p_c(0)=0, p_c_prime=-g3*Jp_inverse*e3. Along it g3 is strictly increasing through zero. Hence s!=0 gives an ordinary triple zero, s=0 gives the unique order-four zero in the auxiliary box. Lambda_c has a strict minimum at zero and lies between 0.8*s^2 and 4*s^2.'}
    # Three genuinely open boxes in ORIGINAL lambda,mu,nu coordinates.
    L=arb(2)**-24;Rsmall=[L/128,L*L/256,L*L/256];rho=arb(2)**-20
    witnesses=[]
    for label,center,count in [('zero',[-L,arb(0),arb(0)],0),('two',[-L,-L*L,arb(0)],2),('four',[L,arb(0),arb(0)],4)]:
        box=[x+zero_ball(r) for x,r in zip(center,Rsmall)]
        need(all(upper(abs(b))<p for b,p in zip(box,P)),'Witness outside global box')
        row={'name':label,'count':count,'center':center,'radii':Rsmall,'parameter_box':box}
        if count in (0,2):
            strip=m.derivatives([zero_ball(rho)]+box,4)
            sides=[m.derivatives([sign*rho]+box,3) for sign in (-1,1)]
            need(strip[2]>0,'Convexity in central strip not established')
            for sign,side in zip((-1,1),sides):
                need(sign*side[3]>0,'G3 critical point not bracketed')
                need(sign*side[1]>0,'Minimum not bracketed')
            # g4>0 globally puts the minimum of g2 in this strip;
            # therefore g2>0 everywhere, and g has just one minimum.
            if count==0:need(strip[0]>0,'Zero-root witness minimum not positive')
            else:need(m.derivatives([0]+box,0)[0]<0,'Two-root witness central value not negative')
            row.update({'critical_strip_radius':rho,'strip_derivatives':strip,'side_derivatives':sides,
                        'g_at_zero':m.derivatives([0]+box,0)[0]})
        else:
            root_scale=arb(2)**-12;positions=[a*root_scale for a in (-3,-1,0,1,3)]
            values=[m.derivatives([s]+box,0)[0] for s in positions]
            for sign,value in zip((1,-1,1,-1,1),values):need(sign*value>0,'Four-root witness signs')
            row.update({'sign_positions':positions,'sign_values':values})
        witnesses.append(row);print('Open original-control box',label,'passed',flush=True)
    out=pack({'status':'finite_physical_window_complete_discriminant_and_open_0_2_4_boxes_passed',
        'model_sha256':sha(mp),'source_sha256':{n:sha(HERE/n) for n in ('certify_window.py','model_v2.py')},
        'global_box':global_box,'auxiliary_radii':R,'fold_surface':fold,'cusp_curve':cusp,'open_witnesses':witnesses,
        'scope':'The fixed modified kernel at exact epsilon4 from R09. Zero counts in |t-tQ|<=2^-7 only; physical lambda/mu/nu box given explicitly. The fold/cusp graphs cover an auxiliary box and include every multiple root from the physical box. No global zero count, no original fixed-kernel A4 claim.',
        'elapsed_seconds':time.monotonic()-start})
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print('Global box, fold surface and cusp curve passed; contractions',fq+fe,cq+ce,'G3 slope',slope,flush=True)


if __name__=='__main__':main()
