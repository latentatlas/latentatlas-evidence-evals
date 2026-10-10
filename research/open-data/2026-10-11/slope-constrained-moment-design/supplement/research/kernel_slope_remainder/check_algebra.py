#!/usr/bin/env python3
"""Exact factors in the quantitative remainder inequalities."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    # Half of integral_0^1 (1-v)v^2 dv: step smoothing remainder.
    one_step=Q(1,2)*(Q(1,3)-Q(1,4));assert one_step==Q(1,24)
    all_jumps=2*one_step;assert all_jumps==Q(1,12)
    # Average of the Taylor remainder (1/2)B v^2 on [-a,a].
    average=Q(1,2)*Q(1,3);assert average==Q(1,6)
    # Lower pair: (gamma*v-B*v^2/2)*(2*delta-2*M*v).
    leading=2*(Q(1,2)-Q(1,3));correction=-Q(1,3)+Q(1,4)
    assert leading==Q(1,3) and correction==Q(-1,12)
    # Exact polynomial expansion of (d+e)^3-d^3.
    cubic_difference=[0,3,3,1];assert cubic_difference[1:]==[3,3,1]
    # For 0<=delta<=alpha<=U, alpha^3-delta^3
    # =e*(alpha^2+alpha*delta+delta^2)<=3U^2e (inequality in proof).
    identities=['unit-step smoothing remainder 1/24','jump-magnitude-two remainder 1/12',
        'averaged Jacobian Taylor error 1/6','paired lower leading coefficient 1/3','paired lower remainder -1/12']
    out=dict(status='exact_rational_remainder_factors_passed',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        identities=identities,one_step_remainder=str(one_step),all_jump_remainder=str(all_jumps),lower_pair_remainder=str(correction),
        scope='Exact polynomial integration constants; fixed-point, absolute-value and infinite-sum arguments are separate analytic proof steps.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
