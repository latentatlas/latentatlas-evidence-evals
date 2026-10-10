#!/usr/bin/env python3
"""R14 exploratory candidate selection; floating-point output is not a proof."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(v):
    m,e=v['mid_man_exp'];return float(m)*2.**e

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists()
    p=HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json';c=json.loads(p.read_text())
    jp=HERE.parent/'cusp_shape_design/results/local_jets.json';j=json.loads(jp.read_text())
    t,lam,mu=map(mid,c['center']);old=np.array(list(map(mid,c['breakpoints'])))
    S=np.array(list(map(mid,c['step_moments_at_exact_Q'])));f3=mid(j['F_at_exact_Q'][3])
    eta=49500/2**30;V=32.;knots=old.copy();d=-2*(-1.)**np.arange(len(old))
    xs,ws=np.polynomial.legendre.leggauss(96);v=(xs+1)*V/2;vw=ws*V/2
    zs,zws=np.polynomial.legendre.leggauss(24)
    def q(u,n):
        u=np.asarray(u);z=np.exp(4*u);K=np.zeros_like(u)
        for k in range(1,9):K+=(2*np.pi**2*k**4*np.exp(9*u)-3*np.pi*k*k*np.exp(5*u))*np.exp(-np.pi*k*k*z)
        return K*np.exp(lam*u*u+mu*u**4)*(2*u)**n*np.cos(2*t*u+n*np.pi/2)
    def moments(bs):
        answer=S[:4].copy()
        for n in range(4):
            for k in range(3):
                width=bs[k]-old[k];u=(bs[k]+old[k])/2+width/2*zs
                answer[n]-=d[k]*width/2*np.dot(zws,q(u,n))
            lo=bs[:,None]-eta*v;hi=bs[:,None]+eta*v
            answer[n]+=eta*np.sum(d*np.dot(-(q(hi,n)-q(lo,n))/(1+np.exp(2*v)),vw))
        return answer
    history=[]
    for k in range(7):
        sm=moments(knots)
        history.append({'iteration':k,'first_three_moments':sm[:3].tolist(),'first_three_knots':knots[:3].tolist()})
        J=np.array([[-d[i]*q(knots[i],n) for i in range(3)] for n in range(3)])
        step=np.linalg.solve(J,-sm[:3]);knots[:3]+=step
    sm=moments(knots);alpha=f3/sm[3]
    out=dict(status='nonrigorous_candidate_only',source_sha256=sha(__file__),input_sha256={'R12':sha(p),'jets':sha(jp)},
        smoothing_width_dyadic=[49500,-30],transition_cutoff=32,
        first_three_knots=knots[:3].tolist(),first_three_knots_dyadic=[list(float(x).as_integer_ratio()) for x in knots[:3]],
        alpha=float(alpha),alpha_dyadic=list(float(alpha).as_integer_ratio()),
        smoothed_moments=sm.tolist(),approximate_slope=float(alpha/eta),
        approximate_relative_increase=float(alpha/mid(c['alpha'])-1),history=history,
        method='96-point floating Gauss-Legendre transition integrals and 24-point shifted steps; approximate Newton with unsmoothed Jacobian. Exact moment correction and interval certification are separate.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','first_three_knots','alpha','approximate_slope','approximate_relative_increase']},indent=2))
if __name__=='__main__':main()
