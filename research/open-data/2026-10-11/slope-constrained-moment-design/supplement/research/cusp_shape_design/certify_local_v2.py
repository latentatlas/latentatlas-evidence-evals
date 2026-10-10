#!/usr/bin/env python3
"""Uniform finite-root geometry at the exact pinned Q, over the safe amplitude."""
import argparse,json,time
from pathlib import Path
from flint import arb,arb_mat,ctx
from shape_model import *
from geometry_model import LocalCusp
from validated_flow import midpoint_inverse,matmul,matvec,norm_mat,norm_vec
from fold_jets import implicit_fold,compose,divide


def geometry(c,b):
    T,L,M=arb('0.003'),arb('1e-6'),arb('2e-9')
    limits=[arb(2)**-8,arb(2)**-12,arb(2)**-18]
    radii=[arb(2)**-13,arb(2)**-19];local=LocalCusp(c,b,limits)
    d=local.derivatives(zero_ball(T),zero_ball(radii[0]),zero_ball(radii[1]))
    Y=midpoint_inverse([[arb(0),c[4].mid()/16],[-c[3].mid()/4,c[5].mid()/16]])
    need(not arb_mat(Y).det().contains(0),'Singular fold preconditioner')
    J=[[-d[2]/4,d[4]/16],[-d[3]/4,d[5]/16]];yj=matmul(Y,J)
    q=norm_mat([[(arb(i==j)-yj[i][j])*radii[j]/radii[i] for j in range(2)] for i in range(2)])
    H=local.derivatives(zero_ball(T),0,0,upto=1)
    eta=norm_vec([v/r for v,r in zip(matvec(Y,H),radii)])
    need(q+eta<1,'Uniform fold contraction failed')
    delta=d[3]*d[4]-d[2]*d[5];need(d[3]>0 and d[4]<0 and delta<0,'Fold signs failed')
    lp,mp=4*d[2]*d[4]/delta,16*d[2]*d[2]/delta
    wp=d[3]-d[4]*lp/4+d[6]*mp/16;need(wp>0,'Fold G2 derivative not positive')
    quad=4*d[4]/delta*wp/2;cubic=-16/delta*wp*wp/3
    need(quad>0 and cubic>0,'Fold growth failed')
    semi=cubic/(quad*quad.sqrt())
    need(quad*T*T>L and semi*L*L.sqrt()<M,'Fold does not fit finite control window')
    endpoints=[]
    for sign in (-1,1):
        f=local.evaluate(0,sign*T,zero_ball(L),zero_ball(M))
        f2=local.evaluate(2,sign*T,zero_ball(radii[0]),zero_ball(radii[1]))
        need(sign*f>0 and sign*f2>0,'Boundary sign failed')
        endpoints.append({'sign':sign,'G':f,'G2':f2})
    three=[]
    for s,sign in zip([arb(-3)/2000,arb(-3)/10000,arb(3)/10000,arb(3)/2000],[-1,1,-1,1]):
        f=local.evaluate(0,s,L/2,0);need(sign*f>0,'Three-root witness failed')
        three.append({'s':s,'sign':sign,'G':f})
    one=[]
    for j in range(32):
        a=-T+2*T*j/32;z=-T+2*T*(j+1)/32;v=local.evaluate(1,a.union(z),-L/2,0)
        need(v>0,'One-root witness failed');one.append({'left':a,'right':z,'G1':v})
    return {'preconditioner':Y,'q':q,'eta':eta,'derivatives':d,'delta':delta,'wprime':wp,
            'quadratic':quad,'cubic':cubic,'semicubical':semi,'endpoints':endpoints,
            'three_witness':three,'one_cover':one}


def cell(data,eps):
    model=LocalTaylor(data,eps);c=model.c
    need(c[3]>0 and c[4]<0,'Cusp nondegeneracy failed')
    b,_=model.enclose((arb(2)**-8,arb(2)**-12,arb(2)**-18),10)
    geo=geometry(c,b)
    a,bb,cc=c[3:6];h3,h4,h5=model.H[3:6]
    # Use the amplitude-independent numerator before interval division.
    kp=(model.F[3]*h4-model.F[4]*h3)/(bb*bb)
    need(kp<0,'Opening direction failed')
    A3p=arb(4)/3*((h5*bb-cc*h4)/(bb*bb)-(h4*a-bb*h3)/(a*a))
    fourth=96*(-a/bb)*A3p
    S=arb(1)/1000
    need(geo['quadratic']*S*S>arb('1e-6'),'Transport interval too short')
    extra=[2*S,upper(geo['quadratic'])*S*S,upper(geo['cubic'])*S*S*S]
    fd,fh=model.enclose(extra,26)
    fd[0]=fd[1]=arb(0);fd[2]=zero_ball(upper(geo['wprime'])*S)
    l,m=implicit_fold(fd,5);g4=compose(fd,4,l,m,5);h0=compose(fh,0,l,m,5)
    jet=divide([-16*v for v in h0],g4,5)
    M4=upper(abs(fourth));M5=upper(120*abs(jet[5]))
    third=-32*kp+zero_ball(M4*S+M5*S*S/2)
    need(third>0,'Finite amplitude transport sign failed')
    low=(third/(3*geo['quadratic']*geo['quadratic'].sqrt())).lower()
    high=(third/(3*geo['quadratic']*geo['quadratic'].sqrt())).upper()
    need(low>10 and high<500,'Readable transport rate bound failed')
    return pack({'epsilon':eps,'cusp_derivatives':c[:16],'H_cusp_derivatives':model.H[:16],
        'neighborhood_derivatives':b,'geometry':geo,'k_amplitude_derivative':kp,
        'fourth_at_cusp':fourth,'transport_S':S,'transport_extra':extra,
        'fold_derivatives':fd,'H_fold_derivatives':fh,'transport_jet':jet,
        'M4':M4,'M5':M5,'B_third':third,'rate_lower':low,'rate_upper':high})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--slabs',type=int,default=16);ap.add_argument('--sample',action='store_true');args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=100;start=time.monotonic();jp=HERE/'results/local_jets.json';data=json.loads(jp.read_text())
    rows=[]
    for j in ((0,args.slabs//2,args.slabs-1) if args.sample else range(args.slabs)):
        a=-arb(1)/128+arb(j)/(64*args.slabs);b=a+arb(1)/(64*args.slabs)
        try:
            r=cell(data,a.union(b));r.update({'index':j,'left':pack(a),'right':pack(b)});rows.append(r)
            print('Amplitude cell',j,'passed; rate',r['rate_lower']['enclosure'],r['rate_upper']['enclosure'],flush=True)
        except ArithmeticError as e:
            if not args.sample:raise
            rows.append({'index':j,'status':'bound_not_proved','reason':str(e)})
            print('Sample cell',j,'bound not proved:',e,flush=True)
    report={'status':'sample_only' if args.sample else 'uniform_fixed_Q_finite_geometry_and_nesting_passed',
        'slab_count':args.slabs,'cells':rows,'jet_certificate_sha256':sha(jp),
        'source_sha256':{n:sha(HERE/n) for n in ('certify_local_v2.py','shape_model.py')},
        'scope':'nu=0, exact Q fixed, |epsilon|<=1/128, |s|<=0.003, |ell|<=1e-6, |m|<=2e-9. Each slab has the same exact cusp and common fold uniqueness box; adjacent slabs agree by uniqueness.',
        'readable_rate_bounds':['10','500'],'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')


if __name__=='__main__':main()
