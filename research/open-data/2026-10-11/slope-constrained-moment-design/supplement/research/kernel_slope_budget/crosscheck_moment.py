#!/usr/bin/env python3
"""Non-rigorous, separate mpmath corroboration for the one new positive moment."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,time
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def exact(v):
    m,e=v['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists();start=time.monotonic()
    q=json.loads((HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json').read_text())
    c=json.loads((HERE/'results/budget_certificate.json').read_text())
    rows=[]
    for dps in (90,115):
        mp.mp.dps=dps;t,lam,mu=map(exact,q['center_exact_dyadic']);pi=mp.pi
        def fun(u):
            z=mp.exp(4*u)
            kernel=mp.fsum(pi*k*k*mp.exp(5*u)*(2*pi*k*k*z-3)*mp.exp(-pi*k*k*z) for k in range(1,21))
            return kernel*mp.exp(lam*u*u+mu*u**4)*(2*u)**4
        val=mp.quadgl(fun,[mp.mpf(k)/8 for k in range(17)],maxdegree=9)
        target=c['positive_moment_4_at_exact_Q'];mid=exact(target)
        r,e=target['rad_man_exp'];rad=mp.mpf(r)*mp.power(2,e)
        difference=abs(val-mid)
        # This is numerical corroboration, not a rigorous enclosure from mpmath.
        assert difference<mp.mpf('1e-80')
        rows.append(dict(dps=dps,value=mp.nstr(val,100),difference=mp.nstr(difference,12),
                         inside_arb_enclosure=bool(difference<=rad)))
    out=dict(status='separate_positive_moment_numerics_agree',theta_terms=20,values=rows,
             acceptance='Absolute numerical difference < 1e-80; mpmath is not an interval proof.',
             elapsed_seconds=time.monotonic()-start,
             source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
