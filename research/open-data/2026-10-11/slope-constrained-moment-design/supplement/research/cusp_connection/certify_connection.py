#!/usr/bin/env python3
"""Certify a cusp curve linking the quartic and sextic reference points."""
import argparse
import json
import time
from pathlib import Path
from flint import arb,arb_mat,ctx
from explore import HERE,BASE,verify_inputs,refine,tangent,J,sha,restore
from bridge_taylor import TubeTaylor
from validated_flow import (matmul,matvec,midpoint_inverse,norm_mat,norm_vec,
                            serialize,upper,zero_ball)


def require(condition,message):
    if not condition:
        raise ArithmeticError(message)


def weighted(a,radii):
    return [[a[i][j]*radii[j]/radii[i] for j in range(3)] for i in range(3)]


def cusp_tangent(d):
    # At an actual cusp, D1=D2=0. Use the hierarchy identities to solve
    # the triangular cusp system in order: mu, lambda, t.
    mup=d[6]/(4*d[4])
    lamp=(4*d[5]*mup-d[7])/(16*d[3])
    tp=(d[8]/64+d[4]*lamp/4-d[6]*mup/16)/d[3]
    return [tp,lamp,mup]


def make_cell(nu,h,seed,radius):
    x,c,Y,point_error,steps=refine(seed,nu)
    v=tangent(c,Y)
    radii=[radius]*3
    model=TubeTaylor(x,nu,v,h,radii)
    d,drem=model.box_derivatives()
    H,Hrem=model.predictor_residual()
    Y=midpoint_inverse(J(model.c))
    require(not arb_mat(Y).det().contains(0),'Preconditioner singular')
    yj=matmul(Y,J(d))
    naive_defect=[[arb(i==j)-yj[i][j] for j in range(3)] for i in range(3)]
    naive_q=norm_mat(weighted(naive_defect,radii))
    defect,defect_remainders=model.preconditioned_defect(Y)
    q=norm_mat(weighted(defect,radii))
    residual=matvec(Y,H)
    eta=norm_vec([residual[i]/radii[i] for i in range(3)])
    require(q<1 and eta+q<1,
            f'Uniform tube failed at nu={nu}: q={q}, eta={eta}')
    root_factor=upper(eta/(1-q))
    tight=[upper(r*root_factor) for r in radii]
    require(d[3]>0 and d[4]<0 and d[6]<0,'Cusp signs not uniform')
    velocities=cusp_tangent(d)
    require(velocities[2]>0,'Mu monotonicity was not proved')
    return {'driver_center':serialize(nu),'driver_half_width':serialize(h),
            'driver_left':serialize(nu-h),'driver_right':serialize(nu+h),
            'center':[serialize(a) for a in x],
            'predictor':[serialize(a) for a in v],
            'radii':[serialize(a) for a in radii],
            'preconditioner':[[serialize(a) for a in row] for row in Y],
            'preconditioned_defect':[[serialize(a) for a in row] for row in defect],
            'preconditioned_defect_remainders':[[serialize(a) for a in row] for row in defect_remainders],
            'uncorrelated_q_bound':serialize(naive_q),
            'uniform_derivatives':[serialize(a) for a in d],
            'uniform_derivative_remainders':[serialize(a) for a in drem],
            'predictor_residual':[serialize(a) for a in H],
            'predictor_remainders':[serialize(a) for a in Hrem],
            'q':serialize(q),'eta':serialize(eta),'eta_plus_q':serialize(upper(eta+q)),
            'tight_root_radii':[serialize(a) for a in tight],
            'cusp_tangent_enclosures':[serialize(a) for a in velocities],
            't_decreases_with_nu':bool(velocities[0]<0),
            'lambda_increases_with_nu':bool(velocities[1]>0),
            'taylor_order':model.order,
            'central_derivatives':[serialize(a) for a in model.c],
            'majorant_domain_half_widths':[serialize(a) for a in model.allowed],
            'taylor_box_half_widths':[serialize(a) for a in model.half],
            'absolute_derivative_bounds':[serialize(a) for a in model.B],
            'candidate_newton_steps':steps,'candidate_correction':serialize(point_error)}


def affine(cell,nu):
    c=list(map(restore,cell['center']))
    v=list(map(restore,cell['predictor']))
    nc=restore(cell['driver_center'])
    return [a+b*(nu-nc) for a,b in zip(c,v)]


def glue_cells(cells):
    seams=[]
    for i,(a,b) in enumerate(zip(cells,cells[1:])):
        nu=restore(a['driver_left'])
        require(nu==restore(b['driver_right']),'Gap in the driver cover')
        ca,cb=affine(a,nu),affine(b,nu)
        small=list(map(restore,a['tight_root_radii']))
        big=list(map(restore,b['radii']))
        displacements=[upper(abs(ca[j]-cb[j])+small[j]) for j in range(3)]
        require(all(displacements[j]<big[j] for j in range(3)),
                'Seam root not proved inside the next uniqueness tube')
        seams.append({'left_index':i,'right_index':i+1,'driver':serialize(nu),
                      'root_containment_bounds':[serialize(v) for v in displacements]})
    return seams


def identify_endpoints(cells):
    q=json.loads((BASE/'results/quartic_cusp_certificate.json').read_text())
    s=json.loads((BASE/'results/sextic_cusp_certificate.json').read_text())
    xq=list(map(restore,q['center_exact_dyadic']))
    rq=restore(q['radius'])
    cq=affine(cells[0],arb(0))
    radii=list(map(restore,cells[0]['radii']))
    bq=[upper(abs(xq[i]-cq[i])+rq) for i in range(3)]
    require(all(a<b for a,b in zip(bq,radii)),'Quartic point not identified')
    ts,ls,ns=list(map(restore,s['center_exact_dyadic']))
    rs=restore(s['radius'])
    driver=ns+zero_ball(rs)
    matches=[]
    for index,cell in enumerate(cells):
        if driver>restore(cell['driver_left']) and driver<restore(cell['driver_right']):
            matches.append(index)
    require(len(matches)==1,'Sextic driver box must be in one cell interior')
    i=matches[0]
    cs=affine(cells[i],driver)
    target=[ts+zero_ball(rs),ls+zero_ball(rs),arb(0)]
    bs=[upper(abs(target[j]-cs[j])) for j in range(3)]
    radii=list(map(restore,cells[i]['radii']))
    require(all(a<b for a,b in zip(bs,radii)),'Sextic point not identified')
    return {'quartic':{'cell':0,'certificate_sha256':sha(BASE/'results/quartic_cusp_certificate.json'),
                       'containment_bounds':[serialize(a) for a in bq]},
            'sextic':{'cell':i,'certificate_sha256':sha(BASE/'results/sextic_cusp_certificate.json'),
                      'driver_box':serialize(driver),
                      'containment_bounds':[serialize(a) for a in bs]}}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--trial',action='store_true')
    args=ap.parse_args()
    ctx.dps=110
    start=time.monotonic()
    inputs=verify_inputs()
    discovery=json.loads((HERE/'results/exploration.json').read_text())
    require(discovery['source_sha256']==sha(HERE/'explore.py'),'Discovery source changed')
    cells=[]
    h=arb(1)/4
    radius=arb(2)**-10
    for k in range(1 if args.trial else 58):
        nu=-arb(2*k+1)/4
        node=discovery['forward'][k//2]
        x=list(map(restore,node['point']))
        v=list(map(restore,node['tangent']))
        nc=restore(node['nu'])
        seed=[(a+b*(nu-nc)).mid() for a,b in zip(x,v)]
        cell=make_cell(nu,h,seed,radius)
        cells.append(cell)
        if k%5==0 or args.trial or k==57:
            print(f'cell {k+1}: nu={nu.str(8)}, q={restore(cell["q"]).str(7)}, '
                  f'eta+q={restore(cell["eta_plus_q"]).str(7)}',flush=True)
    if args.trial:
        (HERE/'results/trial_cell.json').write_text(json.dumps(cells[0],indent=2)+'\n')
        return
    require(restore(cells[0]['driver_right'])==0 and
            restore(cells[-1]['driver_left'])==-29,'Cover endpoints incorrect')
    seams=glue_cells(cells)
    endpoints=identify_endpoints(cells)
    report={'schema':'cusp-connection-v1',
            'status':'uniform_tubes_gluing_and_endpoint_identification_passed',
            'scope':'One analytic cusp graph (t,lambda,mu)(nu), nu in [-29,0], inside the recorded affine tubes',
            'trust_boundary':'Local computer-assisted theorem conditional on the analytic proof and certified integral enclosures; not externally reviewed',
            'input_packages':inputs,'cells':cells,'seams':seams,'endpoints':endpoints,
            't_decreases_with_nu_on_entire_path':all(c['t_decreases_with_nu'] for c in cells),
            'lambda_increases_with_nu_on_entire_path':all(c['lambda_increases_with_nu'] for c in cells),
            'mu_increases_with_nu_on_entire_path':True,
            'quadrature':{'terms':16,'cutoff':2,'pieces':8,'abs_tol':'1e-98','rel_tol':'1e-98','dps':110},
            'source_sha256':{p.name:sha(p) for p in
                             (HERE/'explore.py',HERE/'bridge_taylor.py',HERE/'certify_connection.py')},
            'elapsed_seconds':time.monotonic()-start}
    (HERE/'results/connection_certificate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'cells':len(cells),'seams':len(seams),
                     'elapsed_seconds':report['elapsed_seconds']},indent=2),flush=True)


if __name__=='__main__':
    main()
