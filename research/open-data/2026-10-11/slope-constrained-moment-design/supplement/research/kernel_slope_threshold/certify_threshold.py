#!/usr/bin/env python3
"""R14: smooth feasible design and a 28-crossing lower bound at M=2e-5."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'kernel_norm_threshold'))
# This file has the same basename as R12; load that dependency by explicit path.
spec=importlib.util.spec_from_file_location('r12_threshold',HERE.parent/'kernel_norm_threshold/certify_threshold.py')
r12=importlib.util.module_from_spec(spec);spec.loader.exec_module(r12)
restore,pack,upper,zero_ball=r12.restore,r12.pack,r12.upper,r12.zero_ball
from validated_flow import finite_kernel,series_tail
from flint import arb,acb,arb_mat,ctx

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,msg):
    if not v:raise ArithmeticError(msg)
def exact_ratio(pair):
    a,b=pair;v=arb(a)/arb(b);need(v.is_exact(),'Non-dyadic candidate');return v
def qfun(u,n,x,N):
    t,lam,mu=x
    z=2*acb(t)*u
    trig=(z.cos(),-z.sin(),-z.cos(),z.sin())[n%4]
    return finite_kernel(u,N)*(acb(lam)*u**2+acb(mu)*u**4).exp()*(2*u)**n*trig
def integral(fun,a,b,tol):
    out=acb.integral(fun,acb(a),acb(b),abs_tol=tol,rel_tol=tol,eval_limit=100000)
    need(out.is_finite(),'Quadrature nonfinite');return out.real

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    need(not args.output.exists(),'Refuse overwrite');start=time.monotonic();ctx.dps=110
    paths={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
           'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
           'R11':HERE.parent/'kernel_design_principle/results/candidate_certificate.json',
           'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
           'R13':HERE.parent/'kernel_slope_budget/results/budget_certificate.json',
           'probe':HERE/'diagnostics/candidate_probe.json'}
    data={k:json.loads(p.read_text()) for k,p in paths.items()};old=data['R12'];probe=data['probe'];q=data['Q']
    center=list(map(restore,q['center_exact_dyadic']));rQ=restore(q['root_radius'])
    x=[v+zero_ball(upper(rQ)) for v in center];params={1:x[1],2:x[2],3:arb(0)}
    f=list(map(restore,data['jets']['F_at_exact_Q']))[:9];f[:3]=[arb(0)]*3
    oldknots=list(map(restore,old['breakpoints']));knots=oldknots.copy()
    knots[:3]=list(map(exact_ratio,probe['first_three_knots_dyadic']))
    alpha=exact_ratio(probe['alpha_dyadic']);eta=arb(49500)*arb(2)**-30;V=arb(32);N=8
    need(probe['smoothing_width_dyadic']==[49500,-30] and probe['transition_cutoff']==32,'Candidate identity')
    count=len(knots);need(count==28 and old['initial_sign']==1,'Template identity')
    spacing=min([2*knots[0]]+[b-a for a,b in zip(knots[:-1],knots[1:])])
    need(spacing>2*V*eta and knots[-1]+V*eta<1,'Overlapping/out-of-range integration neighborhoods')
    need(spacing>=32*eta,'Global derivative separation fails')
    tol=arb('1e-55');shift=[];transition=[];S=list(map(restore,old['step_moments_at_exact_Q']))
    for k in range(3):
        left,right=oldknots[k],knots[k];orientation=1
        if right<left:left,right,orientation=right,left,-1
        dk=-2*(-1)**k;values=[]
        for n in range(9):
            def fun(u,analytic):
                if not (4*u).exp().real>0:return acb('nan','nan')
                return qfun(u,n,x,N)
            v=orientation*integral(fun,left,right,tol);values.append(v);S[n]-=dk*v
        shift.append(dict(index=k,old=oldknots[k],new=knots[k],jump=dk,oriented_integrals=values))
    print('Shift integrals: 27 passed',flush=True)
    for k,b in enumerate(knots):
        dk=-2*(-1)**k;values=[]
        for n in range(9):
            def fun(v,analytic):
                lo=acb(b)-acb(eta)*v;hi=acb(b)+acb(eta)*v
                if not (4*lo).exp().real>0 or not (4*hi).exp().real>0:return acb('nan','nan')
                return -acb(eta)*(qfun(hi,n,x,N)-qfun(lo,n,x,N))/(1+(2*v).exp())
            v=integral(fun,arb(0),V,tol);values.append(v);S[n]+=dk*v
        transition.append(dict(index=k,knot=b,jump=dk,rescaled_integrals=values))
        print('Transition',k+1,'/',count,'passed',flush=True)
    # Exact-Q parameters are interval inputs to every new integral.
    # Moving-step discrepancy has magnitude <=2; disjoint truncated smoothing
    # corrections have magnitude <=1. Three full series tails cover both.
    majorants=list(map(restore,old['lipschitz_bounds']));errors=[]
    for n in range(9):
        series=upper(3*series_tail(params,n,arb(1),N))
        tail=upper(2*count*majorants[n]*eta**2*(V+arb(1)/2)*(-2*V).exp())
        S[n]+=zero_ball(upper(series+tail));errors.append(dict(series=series,smoothing_tail=tail))
    matrix=[[restore(v) for v in row] for row in data['R11']['design_matrix']]
    dictionary=[[restore(row['moments'][n]) for row in data['R11']['dictionary']] for n in range(9)]
    A=arb_mat(matrix);det=A.det();need(not det.contains(0),'Moment correction matrix singular')
    rhs=[alpha*S[n]-(f[3] if n==3 else 0) for n in range(4)]
    solution=A.solve(arb_mat([[v] for v in rhs]));weights=[solution[j,0] for j in range(4)]
    g=[f[n]-alpha*S[n]+sum((dictionary[n][j]*weights[j] for j in range(4)),arb(0)) for n in range(9)]
    need(all(v.contains(0) for v in g[:4]),'Defining moment equations inconsistent');g[:4]=[arb(0)]*4
    norm=upper(alpha+sum((abs(v) for v in weights),arb(0)))
    frequencies=data['R11']['frequencies'];slope=upper(alpha/eta*(1+4*(2*count-1)*arb(1)/50**8)+sum((2*j*abs(v) for j,v in zip(frequencies,weights)),arb(0)))
    rank=g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    M=arb('0.00002');need(norm<1 and slope<M and g[4]<0 and rank<0,'Feasible nondegenerate design failed')
    # Lower bound uses the unchanged R12 residual and its certified exact roots.
    a=list(map(restore,old['a']));beta=restore(old['zero_box_radius']);radius=arb(2)**-14
    local=[];total=arb(0);pi=arb.pi()
    for k,b in enumerate(oldknots):
        u=b+zero_ball(upper(beta+radius));z=(4*u).exp()
        rho1=pi*(5*u).exp()*(2*pi*z-3)*(-pi*z+x[1]*u**2+x[2]*u**4).exp()
        derivative=r12.residual_derivative(u,x[0],a)
        need(u>0 and rho1>0 and not derivative.contains(0),'Local crossing lower bound failed')
        coefficient=rho1.lower()*abs(derivative).lower();total+=coefficient
        local.append(dict(index=k,center=b,interval=u,density_first_term=rho1,residual_derivative=derivative,coefficient_lower=coefficient))
    need(all(oldknots[k+1]-oldknots[k]>2*(beta+radius) for k in range(count-1)),'Loss neighborhoods overlap')
    L=arb('0.00000000091787079603827');ell=L/M;need(ell<radius,'Pair radius exceeds certified neighborhood')
    penalty=total*L**3/(3*M**2);D=restore(old['dual_objective_upper']);lower=(f[3]+penalty)/D
    display=['0.000000000917873080','0.000000000917876530']
    need(lower>arb(display[0]) and norm<arb(display[1]),'Readable bracket failed')
    out=dict(status='certified_finite_slope_near_minimum_design',input_sha256={k:sha(p) for k,p in paths.items()},
        source_sha256={'certify_threshold.py':sha(__file__),'../kernel_norm_threshold/certify_threshold.py':sha(HERE.parent/'kernel_norm_threshold/certify_threshold.py'),'../cusp_verified/validated_flow.py':sha(HERE.parent/'cusp_verified/validated_flow.py')},
        slope_budget=M,center=center,Q_box=x,Q_radius=rQ,kernel_terms=N,quadrature_dps=110,quadrature_tolerance=tol,
        alpha=alpha,smoothing_width=eta,transition_cutoff=V,breakpoints=knots,transition_min_spacing=spacing,
        shift_integrals=shift,transition_integrals=transition,moment_error_bounds=errors,smoothed_moments_at_exact_Q=S,
        correction_matrix_determinant=det,correction_rhs=rhs,correction_frequencies=frequencies,correction_weights=weights,
        modified_derivatives=g,three_control_determinant=rank,feasible_norm_upper=norm,feasible_slope_upper=slope,
        lower_local_radius=radius,lower_root_box_radius=beta,lower_crossings=local,lower_total_coefficient=total,
        lower_pair_radius=ell,dual_loss_lower=penalty,finite_budget_lower=lower,readable_bracket=display,
        relative_bracket_gap=arb(display[1])/arb(display[0])-1,
        relative_increase_over_unconstrained=[arb(display[0])/arb('0.00000000091787079608363')-1,arb(display[1])/L-1],
        scope='Fixed exact original Q and Lip_u(h)<=2e-5, no mass normalization. Explicit even real-analytic positive exact-order-four/rank-three witness. Bracket, not exact optimizer or full delta(M) curve. R10 finite window not transferred.',
        trust_boundary='New Arb integrals, local enclosures, prior R12 step moments/majorants/dual objective and R11 correction matrix. Exact feasibility is the defining linear moment solve. Independent rational reconstruction and different-quadrature checks are separate.',
        elapsed_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(pack(out),indent=2)+'\n')
    print(out['status']);print('lower',lower,'upper',norm,'slope',slope)
    print('relative gap',out['relative_bracket_gap']);print('g4',g[4],'rank',rank)
if __name__=='__main__':main()
