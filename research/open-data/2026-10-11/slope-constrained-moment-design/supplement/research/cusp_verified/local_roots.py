#!/usr/bin/env python3
"""Certify one-versus-three LOCAL real roots beside the quartic cusp.

Uses independently bounded real Taylor remainders. The interval and parameter
values are explicit; no global count or original zeta-zero ancestry is claimed.
"""
import hashlib
import itertools
import json
from math import factorial
from pathlib import Path
from flint import arb,ctx
from validated_flow import (absolute_derivative_bounds, cache, max_upper,
                            serialize, upper, zero_ball)

HERE=Path(__file__).resolve().parent


def restore(ball):
    m,e=ball["mid_man_exp"]
    rm,re=ball["rad_man_exp"]
    mid=arb(m)*arb(2)**e
    rad=arb(rm)*arb(2)**re
    return mid+zero_ball(rad)


class TaylorEnclosure:
    def __init__(self,x,half_t,half_lambda,order=8):
        self.x=x
        self.half_t=arb(half_t)
        self.half_lambda=arb(half_lambda)
        self.order=order
        # mu is fixed; active directions are only t and lambda.
        self.c=cache(x[0],{1:x[1],2:x[2]},3+2*(order-1),
                     N=16,abs_tol="1e-98",rel_tol="1e-98")
        boxparams={1:x[1]+zero_ball(self.half_lambda),2:x[2]}
        self.B=absolute_derivative_bounds(boxparams,3+2*order)

    def evaluate(self,n,dt,dlambda):
        dt,dlambda=arb(dt),arb(dlambda)
        if not (abs(dt)<=self.half_t.upper() and
                abs(dlambda)<=self.half_lambda.upper()):
            # Arb radius storage can widen the requested box by <1e-8.
            # The constructor must be supplied a larger permitted domain.
            raise ValueError("Requested point leaves the Taylor domain")
        a,b=dt,-dlambda/4
        out=arb(0)
        for p in range(self.order):
            for q in range(self.order-p):
                coef=arb(1)
                for _ in range(p):coef*=a
                for _ in range(q):coef*=b
                out+=coef*self.c[n+p+2*q]/(factorial(p)*factorial(q))
        W=upper(abs(a)+abs(b))
        remainder=upper(W**self.order/factorial(self.order)
                        *max_upper(self.B[n:n+2*self.order+1]))
        return out+zero_ball(remainder),remainder


def main():
    ctx.dps=110
    certificate=HERE/"results/quartic_cusp_certificate.json"
    data=json.loads(certificate.read_text())
    x=[restore(v) for v in data["center_exact_dyadic"]]
    # Domain has slack beyond the endpoints to absorb interval representation.
    model=TaylorEnclosure(x,"0.0031","0.00000101")
    half=arb(3)/1000
    eps=arb(1)/1000000
    cases=[]
    for sign in (-1,1):
        dl=sign*eps
        third,rem=model.evaluate(3,zero_ball(half),dl)
        assert third>0
        offsets=([-half,half] if sign<0 else
                 [-arb(2)/1000,-arb(5)/10000,arb(5)/10000,arb(2)/1000])
        witnesses=[]
        for s in offsets:
            value,r=model.evaluate(0,s,dl)
            witnesses.append({"t_offset":serialize(s),"F":serialize(value),
                              "remainder_bound":serialize(r),
                              "sign":1 if value>0 else -1 if value<0 else 0})
        expected=[-1,1] if sign<0 else [-1,1,-1,1]
        assert [v["sign"] for v in witnesses]==expected
        monotonicity=[]
        if sign<0:
            for k in range(32):
                l=-half+2*half*k/32
                r=-half+2*half*(k+1)/32
                interval=l.union(r)
                derivative,_=model.evaluate(1,interval,dl)
                assert derivative>0
                monotonicity.append({"left":serialize(l),"right":serialize(r),
                                     "F_t":serialize(derivative)})
        cases.append({"lambda_offset_exact_rational":f"{sign}/1000000",
                      "root_count":1 if sign<0 else 3,
                      "F_ttt_on_entire_window":serialize(third),
                      "F_ttt_remainder_bound":serialize(rem),
                      "sign_witnesses":witnesses,
                      "positive_derivative_cover":monotonicity,
                      "reason":("Opposite endpoint signs and positive F_t on a covering partition"
                                 if sign<0 else "Four alternating signs give >=3 roots; positive F_ttt gives <=3 by Rolle")})
    report={"status":"local_root_counts_certified",
            "scope":"Only t in [t0-0.003,t0+0.003]; mu equals the exact dyadic cusp-center coordinate, lambda=lambda0 +/- 1/1000000",
            "certificate_sha256":hashlib.sha256(certificate.read_bytes()).hexdigest(),
            "center_exact_dyadic":data["center_exact_dyadic"],
            "t_window_half_width_exact_rational":"3/1000",
            "taylor_order":model.order,"cases":cases,
            "source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (HERE/"local_roots.py",HERE/"validated_flow.py")}}
    (HERE/"results/local_root_counts.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"cases":[
        {"lambda_offset":v["lambda_offset_exact_rational"],
         "root_count":v["root_count"],
         "F_ttt":v["F_ttt_on_entire_window"]["enclosure"],
         "F_signs":[w["sign"] for w in v["sign_witnesses"]]} for v in cases]},indent=2))


if __name__=="__main__":main()
