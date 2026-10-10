#!/usr/bin/env python3
"""Separate mpmath roots and original-coordinate quadrature at central dual a0."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,time
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(v):
    m,e=v['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def contains(v,x):
    m,e=v['rad_man_exp'];return abs(x-mid(v))<=mp.mpf(m)*mp.power(2,e)

def run(c,old,jets,dps,order):
    mp.mp.dps=dps;start=time.monotonic();t,lam,mu=map(mid,c['center']);a=list(map(mid,c['dual_center']))
    def residual(u):
        p=[(2*u)**j*mp.cos(2*t*u+j*mp.pi/2) for j in range(4)]
        return p[3]-mp.fsum(a[j]*p[j] for j in range(3))
    roots=[mp.findroot(residual,mid(v['old_knot']),solver='newton',tol=mp.power(10,-dps+10)) for v in c['uniform_roots']]
    assert all(contains(v['root_interval'],z) for v,z in zip(c['uniform_roots'],roots))
    def density(u):
        E=mp.exp(4*u)
        phi=mp.pi*mp.exp(5*u)*mp.fsum(k*k*(2*mp.pi*k*k*E-3)*mp.exp(-mp.pi*k*k*E) for k in range(1,13))
        return phi*mp.exp(lam*u*u+mu*u**4)
    contributions=[density(z)*abs(mp.diff(residual,z)) for z in roots];gamma=mp.fsum(contributions)
    assert all(contains(v['gamma_contribution'],b) for v,b in zip(c['uniform_roots'],contributions))
    assert contains(c['weighted_root_sum'],gamma)
    nodes,weights=mp.gauss_quadrature(order,'legendre');moments=[mp.mpf(0)]*3
    bounds=[mp.mpf(0)]+roots+[mp.mpf(1)]
    for k,(left,right) in enumerate(zip(bounds[:-1],bounds[1:])):
        scale=(right-left)/2;center=(right+left)/2
        for v,w in zip(nodes,weights):
            u=center+scale*v;factor=(-1)**k*scale*w*density(u)
            for j in range(3):moments[j]+=factor*(2*u)**j*mp.cos(2*t*u+j*mp.pi/2)
    gradient=[-v for v in moments]
    assert all(abs(v)<mid(row['absolute_gradient_upper']) for v,row in zip(gradient,c['gradient_rows']))
    # delta and f3 are shared numerical midpoints; this is NOT an optimality proof.
    delta=mid(c['delta_star_enclosure']);f3=mid(jets['F_at_exact_Q'][3]);C=delta**4*gamma/(3*f3)
    assert contains(c['leading_coefficient'],C)
    matrix=mp.matrix([[(2*z)**j*mp.cos(2*t*z+j*mp.pi/2) for j in range(3)] for z in roots[:3]])
    determinant=mp.det(matrix);assert contains(c['first_three_evaluation_determinant'],determinant)
    return dict(dps=dps,gauss_order=order,kernel_terms=12,root_count=28,
        roots=[mp.nstr(v,70) for v in roots],gamma=mp.nstr(gamma,70),coefficient_estimate=mp.nstr(C,70),
        gradient_at_central_dual=[mp.nstr(v,70) for v in gradient],switch_determinant=mp.nstr(determinant,70),
        all_checked_quantities_inside_certificate=True,elapsed_seconds=time.monotonic()-start)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    paths={'certificate':HERE/'results/asymptotic_certificate.json','R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json'}
    d={k:json.loads(p.read_text()) for k,p in paths.items()};values=[]
    for prec,order in [(80,48),(110,64)]:
        values.append(run(d['certificate'],d['R12'],d['jets'],prec,order));print('Separate root/quadrature check passed',prec,order,flush=True)
    diff=max(abs(mp.mpf(a)-mp.mpf(b)) for a,b in zip(values[0]['gradient_at_central_dual'],values[1]['gradient_at_central_dual']))
    gdiff=abs(mp.mpf(values[0]['gamma'])-mp.mpf(values[1]['gamma']));assert diff<mp.mpf('1e-45') and gdiff<mp.mpf('1e-60')
    out=dict(status='separate_roots_and_quadratures_agree',source_sha256=sha(__file__),input_sha256={k:sha(p) for k,p in paths.items()},
        values=values,maximum_gradient_difference=mp.nstr(diff,35),gamma_difference=mp.nstr(gdiff,35),
        trust_boundary='Nonrigorous independent roots, automatic numerical differentiation and Gauss quadrature with mpmath. Uses central Q and a0, 12 theta terms and [0,1]; rigorous parameter and infinite tails are in the Arb certificate. Does not locate exact a_star or prove asymptotics.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
