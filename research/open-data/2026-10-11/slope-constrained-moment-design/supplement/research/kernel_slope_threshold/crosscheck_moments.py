#!/usr/bin/env python3
"""Separate mpmath quadrature in original u coordinates; corroboration, not proof."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,time
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(v):
    m,e=v['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def radius(v):
    m,e=v['rad_man_exp'];return mp.mpf(m)*mp.power(2,e)
def contains(v,x):return abs(x-mid(v))<=radius(v)

def run(c,old,r11,jets,dps,order):
    mp.mp.dps=dps;start=time.monotonic()
    t,lam,mu=map(mid,c['center']);knots=list(map(mid,c['breakpoints']));oldknots=list(map(mid,old['breakpoints']))
    eta=mid(c['smoothing_width']);alpha=mid(c['alpha']);S=list(map(mid,old['step_moments_at_exact_Q']))
    nodes,weights=mp.gauss_quadrature(order,'legendre')
    def vector(u):
        z=mp.exp(4*u);e5=mp.exp(5*u)
        kernel=mp.pi*e5*mp.fsum(k*k*(2*mp.pi*k*k*z-3)*mp.exp(-mp.pi*k*k*z) for k in range(1,13))
        rho=kernel*mp.exp(lam*u*u+mu*u**4);s=mp.sin(2*t*u);co=mp.cos(2*t*u)
        trig=[co,-s,-co,s];power=mp.mpf(1);out=[]
        for n in range(9):out.append(rho*power*trig[n%4]);power*=2*u
        return out
    def integrate(left,right,multiplier):
        ans=[mp.mpf(0)]*9;scale=(right-left)/2;center=(right+left)/2
        for v,w in zip(nodes,weights):
            u=center+scale*v;factor=scale*w*multiplier(u);row=vector(u)
            for n in range(9):ans[n]+=factor*row[n]
        return ans
    for k in range(3):
        change=integrate(oldknots[k],knots[k],lambda u:mp.mpf(1));jump=-2*(-1)**k
        for n in range(9):S[n]-=jump*change[n]
    panels=[0,1,2,4,8,16,32]
    for k,b in enumerate(knots):
        jump=-2*(-1)**k
        for sign in [-1,1]:
            for left,right in zip(panels[:-1],panels[1:]):
                a=b+sign*eta*left;z=b+sign*eta*right
                if a>z:a,z=z,a
                def multiplier(u):
                    H=(1+mp.tanh((u-b)/eta))/2
                    return jump*(H-(1 if sign==1 else 0))
                row=integrate(a,z,multiplier)
                for n in range(9):S[n]+=row[n]
    assert all(contains(v,s) for v,s in zip(c['smoothed_moments_at_exact_Q'],S))
    f=list(map(mid,jets['F_at_exact_Q']))[:9];f[:3]=[mp.mpf(0)]*3
    A=mp.matrix([[mid(v) for v in row] for row in r11['design_matrix']])
    rhs=mp.matrix([alpha*S[n]-(f[3] if n==3 else 0) for n in range(4)])
    w=mp.lu_solve(A,rhs)
    assert all(contains(v,value) for v,value in zip(c['correction_weights'],w))
    dictionary=[[mid(row['moments'][n]) for row in r11['dictionary']] for n in range(9)]
    g=[f[n]-alpha*S[n]+sum(dictionary[n][j]*w[j] for j in range(4)) for n in range(9)]
    assert all(contains(c['modified_derivatives'][n],g[n]) for n in range(4,9))
    rank=g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    assert contains(c['three_control_determinant'],rank)
    norm=alpha+sum(abs(v) for v in w)
    return dict(dps=dps,gauss_order=order,kernel_terms=12,transition_panels=28*2*6,
        smoothed_moments=[mp.nstr(v,65) for v in S],weights=[mp.nstr(v,65) for v in w],
        norm_estimate=mp.nstr(norm,65),rank_estimate=mp.nstr(rank,65),
        all_moments_weights_and_rank_inside_certificate=True,elapsed_seconds=time.monotonic()-start)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    paths={'certificate':HERE/'results/slope_threshold_certificate.json',
        'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
        'R11':HERE.parent/'kernel_design_principle/results/candidate_certificate.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json'}
    d={k:json.loads(p.read_text()) for k,p in paths.items()};values=[]
    for prec,order in [(70,48),(100,64)]:
        v=run(d['certificate'],d['R12'],d['R11'],d['jets'],prec,order);values.append(v)
        print('Separate quadrature passed',prec,'digits,',order,'Gauss nodes',flush=True)
    differences=[abs(mp.mpf(a)-mp.mpf(b)) for a,b in zip(values[0]['smoothed_moments'],values[1]['smoothed_moments'])]
    assert max(differences)<mp.mpf('1e-45')
    out=dict(status='separate_original_coordinate_quadratures_agree',source_sha256=sha(__file__),
        input_sha256={k:sha(p) for k,p in paths.items()},values=values,
        maximum_cross_precision_moment_difference=mp.nstr(max(differences),30),
        trust_boundary='Nonrigorous independent quadrature with another arithmetic library, original-coordinate half-transitions, 12 theta terms and two quadrature orders. Prior step moments/correction matrix remain shared. Full smoothing tails are enclosed by the rigorous certificate, not computed here.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'])
if __name__=='__main__':main()
