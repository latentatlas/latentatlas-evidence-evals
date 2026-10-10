#!/usr/bin/env python3
"""Rational sign data for exact prescribed-opening and boundary corollaries."""
import argparse,json,time
from pathlib import Path
from fractions import Fraction as Q
from check_design import HERE,sha,D,read,rowinterval


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();dp=HERE/'results/design_certificate.json';cp=HERE/'results/design_check.json'
    design=json.loads(dp.read_text());check=json.loads(cp.read_text())
    assert check['certificate_sha256']==sha(dp)
    a=D(*map(Q,check['a']));b=D(*map(Q,check['b']))
    assert a.hi<0 and b.lo>0
    left=-D(1)/b;right=-D(1)/a
    assert left.lo>-Q(41,1250) and left.hi<0<right.lo and right.hi<Q(19,1000)
    factor=1+a*left;assert factor.lo>Q('2.74')
    report={'status':'rational_boundary_signs_and_prescribed_opening_corollary_passed',
        'design_certificate_sha256':sha(dp),'design_check_sha256':sha(cp),'source_sha256':sha(__file__),
        'a':rowinterval(a),'b':rowinterval(b),'mu_unfolding_boundary':rowinterval(left),
        'quartic_boundary':rowinterval(right),'D3_factor_at_left_boundary':rowinterval(factor),
        'kernel_multiplier_common_lower':'0.9672',
        'exact_prescription':'For every r>0, epsilon(r)=(1-r)/(r*b-a) lies in (-1/b,-1/a). Then 1+a*epsilon=r*(b-a)/(r*b-a)>0 and 1+b*epsilon=(b-a)/(r*b-a)>0, so C(epsilon)=r*C(0) exactly.',
        'scope':'Fixed exact Q, unchanged lambda/mu coordinates, positive smooth modified kernels. The leading local width coefficient C attains every positive value. No uniform finite root window over this entire open amplitude interval, no unbounded finite W claim, and no result for the original undeformed kernel.',
        'boundary_meaning':'At the negative endpoint G4=0 while G3>0, so the lambda/mu cusp unfolding loses rank. At the positive endpoint G3=0, G4!=0 and the lambda/mu/nu control jets have rank three, as checked separately.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print('Full positive leading-opening range certified; left boundary',float(left.lo),'right boundary',float(right.hi),flush=True)


if __name__=='__main__':main()
