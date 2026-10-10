#!/usr/bin/env python3
"""Numerical end-to-end ramp design at M0; corroboration, not certification."""
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
def run(c,old,jets,dps,base_order,local_order):
    mp.mp.dps=dps;start=time.monotonic();tau,lam,mu=map(mid,old['center']);coef=list(map(mid,old['dual_center']))
    oldknots=[mid(v['root_interval']) for v in old['uniform_roots']]
    base_nodes,base_weights=mp.gauss_quadrature(base_order,'legendre');nodes,weights=mp.gauss_quadrature(local_order,'legendre')
    def p(u):return [(2*u)**j*mp.cos(2*tau*u+j*mp.pi/2) for j in range(4)]
    def rho(u):
        E=mp.exp(4*u)
        return mp.pi*mp.exp(5*u+lam*u*u+mu*u**4)*mp.fsum(k*k*(2*mp.pi*k*k*E-3)*mp.exp(-mp.pi*k*k*E) for k in range(1,13))
    def q(u):
        w=rho(u);return [w*v for v in p(u)]
    def residual(u):
        row=p(u);return row[3]-mp.fsum(coef[j]*row[j] for j in range(3))
    def integrate(left,right,use_base=False):
        nn,ww=(base_nodes,base_weights) if use_base else (nodes,weights)
        out=[mp.mpf(0)]*4;scale=(right-left)/2;center=(right+left)/2
        for node,weight in zip(nn,ww):
            row=q(center+scale*node)
            for j in range(4):out[j]+=scale*weight*row[j]
        return out
    def sign_moments(roots):
        ans=[mp.mpf(0)]*4;points=[mp.mpf(0)]+roots+[mp.mpf(1)]
        for k,(left,right) in enumerate(zip(points[:-1],points[1:])):
            row=integrate(left,right,True)
            for j in range(4):ans[j]+=(-1)**k*row[j]
        return ans
    # Numerical dual solve using independent quadrature and the full-density Hessian.
    for iteration in range(4):
        roots=[mp.findroot(residual,z,solver='newton',tol=mp.power(10,-dps+12)) for z in oldknots]
        S=sign_moments(roots)
        if max(abs(v) for v in S[:3])<mp.mpf('1e-55'):break
        H=mp.matrix(3,3)
        for z in roots:
            row=p(z);factor=2*rho(z)/abs(mp.diff(residual,z))
            for i in range(3):
                for j in range(3):H[i,j]+=factor*row[i]*row[j]
        change=mp.lu_solve(H,mp.matrix(S[:3]));coef=[v+d for v,d in zip(coef,change)]
    assert max(abs(v) for v in S[:3])<mp.mpf('1e-55')
    assert all(contains(v,b) for v,b in zip(old['dual_coefficient_box'],coef))
    assert all(contains(v['root_interval'],b) for v,b in zip(old['uniform_roots'],roots))
    f3=mid(jets['F_at_exact_Q'][3]);D=S[3]-mp.fsum(coef[j]*S[j] for j in range(3));delta=f3/D
    assert contains(old['delta_star_enclosure'],delta)
    Gamma=mp.fsum(rho(z)*abs(mp.diff(residual,z)) for z in roots);C=delta**4*Gamma/(3*f3)
    M=mp.mpf('0.00002');width=delta/M
    B=mp.matrix([[mid(v) for v in row] for row in c['preconditioner']]);F=mp.matrix([mid(v) for v in c['center_forcing']]);prediction=B*F
    centers=roots.copy()
    for k in range(3):centers[k]+=width**2*prediction[k]
    def ramp_moments(centers,width):
        ans=S.copy()
        for k in range(3):
            row=integrate(roots[k],centers[k]);jump=-2*(-1)**k
            for j in range(4):ans[j]-=jump*row[j]
        for k,z in enumerate(centers):
            jump=-2*(-1)**k
            for node,weight in zip(nodes,weights):
                v=(node+1)/2;factor=-jump*width/4*weight*(1-v)
                plus=q(z+width*v);minus=q(z-width*v)
                for j in range(4):ans[j]+=factor*(plus[j]-minus[j])
        return ans
    for outer in range(9):
        for inner in range(5):
            moments=ramp_moments(centers,width)
            if max(abs(v) for v in moments[:3])<mp.mpf('1e-43'):break
            J=mp.matrix(3,3)
            for k in range(3):
                average=integrate(centers[k]-width,centers[k]+width);jump=-2*(-1)**k
                for j in range(3):J[j,k]=-jump*average[j]/(2*width)
            change=mp.lu_solve(J,mp.matrix(moments[:3]))
            for k in range(3):centers[k]-=change[k]
        alpha=f3/moments[3]
        budget_error=abs(alpha/(width*M)-1)
        if budget_error<mp.mpf('1e-30'):break
        width=alpha/M
    assert max(abs(v) for v in moments[:3])<mp.mpf('1e-40') and budget_error<mp.mpf('1e-30')
    scaled=[(centers[k]-roots[k])/width**2 for k in range(3)]
    assert all(abs(v)<mid(b) for v,b in zip(scaled,c['scaled_center_bounds']))
    excess=alpha-delta;leading=C/M**2;relative=excess/leading-1
    assert -mp.mpf('9.624e-33')/M**3<excess-leading<mp.mpf('2.167e-32')/M**3
    return dict(dps=dps,base_gauss_order=base_order,local_gauss_order=local_order,kernel_terms=12,cutoff=1,
        dual_iterations=iteration+1,budget_iterations=outer+1,dual_coefficients=[mp.nstr(v,65) for v in coef],
        delta_star_estimate=mp.nstr(delta,65),ramp_amplitude=mp.nstr(alpha,65),transition_half_width=mp.nstr(width,65),
        scaled_center_displacements=[mp.nstr(v,65) for v in scaled],excess_estimate=mp.nstr(excess,65),
        leading_term_estimate=mp.nstr(leading,65),relative_excess_deviation=mp.nstr(relative,65),
        first_three_moment_residual=mp.nstr(max(abs(v) for v in moments[:3]),35),relative_budget_residual=mp.nstr(budget_error,35),
        numerical_design_within_certified_remainder=True,elapsed_seconds=time.monotonic()-start)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    paths={'certificate':HERE/'results/remainder_certificate.json','R15':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_certificate.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json'}
    data={k:json.loads(p.read_text()) for k,p in paths.items()};values=[]
    for prec,base,local in [(80,48,8),(110,64,12)]:
        values.append(run(data['certificate'],data['R15'],data['jets'],prec,base,local));print('Numerical ramp check passed',prec,flush=True)
    difference=abs(mp.mpf(values[0]['ramp_amplitude'])-mp.mpf(values[1]['ramp_amplitude']));assert difference<mp.mpf('1e-40')
    out=dict(status='separate_numerical_ramp_design_agrees',source_sha256=sha(__file__),input_sha256={k:sha(p) for k,p in paths.items()},values=values,
        cross_precision_amplitude_difference=mp.nstr(difference,35),trust_boundary='Nonrigorous numerical optimizer and ramp design at central Q, with 12 theta terms and cutoff 1. Useful end-to-end corroboration; approximate moment/budget residuals and uncomputed tails do not define a certified finite-M witness or exact optimizer.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
