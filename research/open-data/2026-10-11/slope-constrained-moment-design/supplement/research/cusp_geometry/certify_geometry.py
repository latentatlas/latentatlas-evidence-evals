#!/usr/bin/env python3
"""Uniform finite cusp neighborhoods and monotone leading opening width."""
import argparse
import json
import time
from flint import arb,arb_mat,ctx
from geometry_model import (HERE,BASE,CONNECTION,CorrelatedCell,LocalCusp,
                            verify_inputs,restore,serialize,sha,upper,zero_ball)
from width_shape import certify_shape
from validated_flow import midpoint_inverse,matmul,matvec,norm_mat,norm_vec


def require(ok,message):
    if not ok: raise ArithmeticError(message)


def pack(obj):
    if isinstance(obj,arb): return serialize(obj)
    if isinstance(obj,list): return [pack(v) for v in obj]
    if isinstance(obj,dict): return {k:pack(v) for k,v in obj.items()}
    return obj


def certify_cell(raw,index):
    model=CorrelatedCell(raw,index)
    c,cr=model.enclose(upto=14)
    T,L,M=arb(3)/1000,arb(1)/1000000,arb(1)/500000000
    radii=[arb(2)**-13,arb(2)**-20]
    limits=[arb(2)**-8,2*radii[0],2*radii[1]]
    b,br=model.enclose(limits,upto=10)
    local=LocalCusp(c,b,limits)
    d=local.derivatives(zero_ball(T),zero_ball(radii[0]),zero_ball(radii[1]))
    Y=midpoint_inverse([[arb(0),c[4].mid()/16],[-c[3].mid()/4,c[5].mid()/16]])
    require(not arb_mat(Y).det().contains(0),'Singular fold preconditioner')
    A=[[-d[2]/4,d[4]/16],[-d[3]/4,d[5]/16]]
    ya=matmul(Y,A)
    q=norm_mat([[(arb(i==j)-ya[i][j])*radii[j]/radii[i]
                 for j in range(2)] for i in range(2)])
    H=local.derivatives(zero_ball(T),0,0,upto=1)
    eta=norm_vec([v/r for v,r in zip(matvec(Y,H),radii)])
    require(q<arb('0.59') and q+eta<arb('0.74'),'Uniform fold contraction failed')
    delta=d[3]*d[4]-d[2]*d[5]
    lp,mp=4*d[2]*d[4]/delta,16*d[2]*d[2]/delta
    wp=d[3]-d[4]*lp/4+d[6]*mp/16
    require(d[3]>0 and d[4]<0 and delta<0 and wp>0,'Fold geometry signs failed')
    quadratic=(4*d[4]/delta)*wp/2
    cubic=(-16/delta)*wp*wp/3
    semi=cubic/(quadratic*quadratic.sqrt())
    require(quadratic>arb('1.80') and quadratic<arb('2.21'),'Quadratic bounds failed')
    require(cubic>arb('1.61') and cubic<arb('2.09'),'Cubic bounds failed')
    require(semi>arb('0.49') and semi<arb('0.86'),'Semicubical bounds failed')
    # These rational comparisons locate exits without separate root solves.
    require(arb('1.80')*T*T>L,'Arms do not reach the right boundary')
    require(arb('0.86')*L*L.sqrt()<M,'Arms may exit through a mu edge')
    ends=[]
    for sign in (-1,1):
        f=local.evaluate(0,sign*T,zero_ball(L),zero_ball(M))
        f2=local.evaluate(2,sign*T,zero_ball(radii[0]),zero_ball(radii[1]))
        require(sign*f>0 and sign*f2>0,'Window endpoint signs failed')
        ends.append({'sign':sign,'F':f,'F_tt_on_Q':f2})
    three=[]
    for s,sign in zip([arb(-3)/2000,arb(-3)/10000,arb(3)/10000,arb(3)/2000],[-1,1,-1,1]):
        f=local.evaluate(0,s,L/2,0)
        require(sign*f>0,'Three-root witness failed')
        three.append({'s':s,'sign':sign,'F':f})
    one=[]
    for k in range(32):
        a,boundary=-T+2*T*k/32,-T+2*T*(k+1)/32
        value=local.evaluate(1,a.union(boundary),-L/2,0)
        require(value>0,'One-root witness failed')
        one.append({'left':a,'right':boundary,'F_t':value})
    shape=certify_shape(model,c)
    require(shape['N']>0 and shape['Cprime']<0,'Opening coefficient monotonicity failed')
    require(shape['Cprime']>arb('-0.0019') and shape['Cprime']<arb('-0.0007'),
            'Readable opening derivative bounds failed')
    C=8*arb(2).sqrt()/3*c[3]/-c[4]
    return pack({'index':index,'driver_center':model.nu,'driver_half_width':model.h,
        'local_limits':limits,'cusp_derivatives':c,'cusp_remainders':cr,
        'neighborhood_derivatives':b,'neighborhood_remainders':br,
        'extra_central_derivatives':model.c[51:],'extra_absolute_bounds':model.B[57:],
        'uniform_fold':{'preconditioner':Y,'derivatives':d,'H_on_centerline':H,
                        'q':q,'eta':eta,'delta':delta,'wprime':wp,
                        'quadratic':quadratic,'cubic':cubic,'semicubical':semi},
        'window_endpoints':ends,'three_root_witness':three,'one_root_cover':one,
        'opening_coefficient':C,'opening_shape':shape})


def endpoint_coefficients():
    out={}
    for name in ('quartic','sextic'):
        path=BASE/f'results/{name}_cusp_certificate.json'
        data=json.loads(path.read_text());d=list(map(restore,data['root_derivative_enclosures']))
        out[name]={'C':8*arb(2).sqrt()/3*d[3]/-d[4],'certificate_sha256':sha(path)}
    ratio=out['sextic']['C']/out['quartic']['C']
    require(ratio>arb('1.024') and ratio<arb('1.026'),'Endpoint opening comparison failed')
    out['ratio']=ratio;out['increase_percent']=100*(ratio-1)
    return pack(out)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--trial',action='store_true')
    args=parser.parse_args();ctx.dps=110;started=time.monotonic()
    inputs=verify_inputs();path=CONNECTION/'results/connection_certificate.json'
    data=json.loads(path.read_text());indices=[0,28,57] if args.trial else range(58)
    cells=[]
    for i in indices:
        item=certify_cell(data['cells'][i],i);cells.append(item)
        if i%10==0 or i==57 or args.trial:
            print('cell',i+1,'q',item['uniform_fold']['q']['enclosure'],
                  'Cprime',item['opening_shape']['Cprime']['enclosure'],flush=True)
    report={'schema':'cusp-geometry-v1',
        'status':'trial_passed' if args.trial else 'uniform_regions_and_monotone_opening_passed',
        'scope':'For every nu in [-29,0], exact-cusp-centered |s|<=.003, |ell|<=1e-6, |m|<=2e-9; complete local root counts and strictly decreasing leading width coefficient C(nu)',
        'input_packages':inputs,'connection_certificate_sha256':sha(path),
        'cells':cells,'endpoints':endpoint_coefficients(),
        'readable_bounds':{'quadratic':['1.80','2.21'],'cubic':['1.61','2.09'],
            'semicubical':['0.49','0.86'],'width':['0.98','1.72'],
            'Cprime':['-0.0019','-0.0007']},
        'source_sha256':{p:sha(HERE/p) for p in ['geometry_model.py','width_shape.py','certify_geometry.py']},
        'elapsed_seconds':time.monotonic()-started}
    out=HERE/('diagnostics/trial_certificate.json' if args.trial else 'results/geometry_certificate.json')
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'cells':len(cells),
                      'endpoints':report['endpoints'],'elapsed_seconds':report['elapsed_seconds']},indent=2),flush=True)


if __name__=='__main__': main()
