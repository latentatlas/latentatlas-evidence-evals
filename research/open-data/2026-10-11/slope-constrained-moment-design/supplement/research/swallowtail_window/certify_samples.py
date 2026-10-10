#!/usr/bin/env python3
"""Finite cusp, double-fold intersection, fold-curve and simple-root samples."""
import argparse,json,time
from pathlib import Path
from model_v2 import *


def solve(fun,guess,radii,iterations=7):
    x=[arb(v).mid() for v in guess]
    for _ in range(iterations):
        f,j=fun(x);y=midpoint_inverse([[z.mid() for z in row] for row in j])
        dx=matvec(y,[v.mid() for v in f]);x=[(v-w).mid() for v,w in zip(x,dx)]
    f0,j0=fun(x);Y=midpoint_inverse([[v.mid() for v in row] for row in j0])
    box=[x0+zero_ball(r) for x0,r in zip(x,radii)];fb,jb=fun(box)
    q,eta=contraction(Y,jb,f0,radii)
    tight=[upper(r*eta/(1-q)) for r in radii];root=[x0+zero_ball(r) for x0,r in zip(x,tight)]
    return {'center':x,'radii':radii,'preconditioner':Y,'q':q,'eta':eta,
        'center_equations':f0,'box_jacobian':jb,'box_equations':fb,
        'tight_radii':tight,'root_enclosures':root}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic();mp=HERE/'results/model_v2.json';data=json.loads(mp.read_text());m=Model(data)
    cp=HERE/'results/window_certificate.json';cert=json.loads(cp.read_text())
    L=arb(2)**-24;r=arb(2)**-12;Y2=[[restore(v) for v in row] for row in cert['fold_surface']['Y']]
    def initial(s):
        d=m.derivatives([s,L,0,0],1);return [-v for v in matvec(Y2,d)]
    cusps=[]
    for sign in (-1,1):
        s=sign*(L/2).sqrt();mu,nu=initial(s)
        def fun(x):
            s,mu,nu=x;d=m.derivatives([s,L,mu,nu],8)
            return d[:3],[[d[n+1],d[n+4]/16,-d[n+6]/64] for n in range(3)]
        row=solve(fun,[s,mu,nu],[r*arb(2)**-18,arb(2)**-66,arb(2)**-66])
        x=row['root_enclosures'];d=m.derivatives([x[0],L,x[1],x[2]],4)
        need(sign*d[3]>0,'Cusp not ordinary')
        need(abs(x[0])<arb(2)**-7 and abs(x[1])<arb(2)**-34 and abs(x[2])<arb(2)**-34,'Cusp leaves physical box')
        row.update({'branch':sign,'G3':d[3]});cusps.append(row)
        print('Section cusp',sign,'certified',flush=True)
    # Both minima simultaneously zero at the same original controls.
    sp=(3*L/2).sqrt()
    def doublefun(x):
        s1,s2,mu,nu=x;d1=m.derivatives([s1,L,mu,nu],7);d2=m.derivatives([s2,L,mu,nu],7)
        return [d1[0],d1[1],d2[0],d2[1]],[
            [d1[1],arb(0),d1[4]/16,-d1[6]/64],
            [d1[2],arb(0),d1[5]/16,-d1[7]/64],
            [arb(0),d2[1],d2[4]/16,-d2[6]/64],
            [arb(0),d2[2],d2[5]/16,-d2[7]/64]]
    double=solve(doublefun,[-sp,sp,L*L,arb(0)],[r*arb(2)**-18,r*arb(2)**-18,arb(2)**-66,arb(2)**-66])
    z=double['root_enclosures'];need(z[0]<z[1],'Double roots not distinct')
    nd=[m.derivatives([s,L,z[2],z[3]],2)[2] for s in z[:2]];need(all(v>0 for v in nd),'Double roots not minima')
    need(all(abs(v)<arb(2)**-34 for v in z[2:]),'Double fold leaves physical box')
    double['second_derivatives']=nd;print('Two distinct double roots at the same controls certified',flush=True)
    # A curve in the physical lambda=L section. Include special points
    # separately; the sequence is a plotting sample, not a connectivity proof.
    folds=[]
    for i in range(81):
        s=r*arb(i-40)/25
        def fun(x):
            d=m.derivatives([s,L,x[0],x[1]],7)
            return d[:2],[[d[n+4]/16,-d[n+6]/64] for n in range(2)]
        row=solve(fun,initial(s),[arb(2)**-66,arb(2)**-66],5)
        row.update({'index':i,'s':s});folds.append(row)
    print('81 fold-curve samples certified',flush=True)
    roots=[]
    for name,l,mu,count in [('two',-L,-L*L,2),('four',L,arb(0),4)]:
        guesses=[-r,r] if count==2 else [sign*r*((3+side*arb(6).sqrt())/2).sqrt() for sign in (-1,1) for side in (-1,1)]
        group=[]
        for guess in sorted(guesses):
            def fun(x):
                d=m.derivatives([x[0],l,mu,0],1);return [d[0]],[[d[1]]]
            row=solve(fun,[guess],[r*arb(2)**-18]);group.append(row)
        roots.append({'name':name,'controls':[l,mu,arb(0)],'count':count,'roots':group})
    out=pack({'status':'2_cusps_double_fold_81_fold_samples_and_6_simple_roots_certified',
        'model_sha256':sha(mp),'window_certificate_sha256':sha(cp),
        'source_sha256':{n:sha(HERE/n) for n in ('certify_samples.py','model_v2.py')},
        'lambda_section':L,'root_scale':r,'cusps':cusps,'double_fold':double,'fold_samples':folds,'simple_roots':roots,
        'scope':'All samples use original controls relative to the exact Q, at the fixed modified kernel epsilon4. Uniform surface and cusp identification is from window_certificate.json; sampled line segments are not a proof.',
        'elapsed_seconds':time.monotonic()-start})
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')


if __name__=='__main__':main()
