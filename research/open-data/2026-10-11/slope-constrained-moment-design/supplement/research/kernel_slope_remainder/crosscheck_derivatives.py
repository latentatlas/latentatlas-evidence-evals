#!/usr/bin/env python3
"""Separate mpmath differentiation at interval centers and endpoints."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,time
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(v):
    m,e=v['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def rad(v):
    m,e=v['rad_man_exp'];return mp.mpf(m)*mp.power(2,e)
def contains(v,x):return abs(x-mid(v))<=rad(v)
def run(c,old,dps):
    mp.mp.dps=dps;start=time.monotonic();tau,lam,mu=map(mid,old['center']);a=list(map(mid,old['dual_center']));count=0;anchors=[]
    def rho(u):
        E=mp.exp(4*u)
        return mp.pi*mp.exp(5*u+lam*u*u+mu*u**4)*mp.fsum(k*k*(2*mp.pi*k*k*E-3)*mp.exp(-mp.pi*k*k*E) for k in range(1,13))
    def q(u,j):return rho(u)*(2*u)**j*mp.cos(2*tau*u+j*mp.pi/2)
    def qr(u):return rho(u)*((2*u)**3*mp.cos(2*tau*u+3*mp.pi/2)-mp.fsum(a[j]*(2*u)**j*mp.cos(2*tau*u+j*mp.pi/2) for j in range(3)))
    for key,samples in [('center_derivative_enclosures',[0]),('local_derivative_enclosures',[-1,0,1])]:
        for k,row in enumerate(c[key]):
            for position in samples:
                u=mid(row['interval'])+position*rad(row['interval'])
                for j in range(4):
                    for order in range(3):
                        v=mp.diff(lambda s:q(s,j),u,order)
                        assert contains(row['moment_jets'][j][order],v),(key,k,position,j,order)
                        count+=1
                for order in range(3):
                    v=mp.diff(qr,u,order);assert contains(row['residual_density_jets'][order],v),(key,k,position,'r',order)
                    if key=='center_derivative_enclosures':anchors.append(mp.nstr(v,65))
                    count+=1
    return dict(dps=dps,kernel_terms=12,derivative_comparisons=count,all_samples_inside_certificate=True,center_residual_jet_values=anchors,elapsed_seconds=time.monotonic()-start)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    paths={'certificate':HERE/'results/remainder_certificate.json','R15':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_certificate.json'}
    d={k:json.loads(p.read_text()) for k,p in paths.items()};values=[]
    for prec in [80,110]:
        values.append(run(d['certificate'],d['R15'],prec));print('Derivative crosscheck passed',prec,values[-1]['derivative_comparisons'],flush=True)
    difference=max(abs(mp.mpf(a)-mp.mpf(b)) for a,b in zip(values[0]['center_residual_jet_values'],values[1]['center_residual_jet_values']))
    assert difference<mp.mpf('1e-60')
    out=dict(status='separate_differentiation_samples_agree',source_sha256=sha(__file__),input_sha256={k:sha(p) for k,p in paths.items()},values=values,
        maximum_center_jet_difference=mp.nstr(difference,35),trust_boundary='Nonrigorous numerical differentiation at central Q and a0, using another arithmetic library and the original integral density. Finite samples corroborate but do not prove interval containment over whole boxes or control the infinite theta/root tails.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
