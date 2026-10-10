#!/usr/bin/env python3
"""Independent mpmath real-axis check; numerical support, NOT a certificate.

Does not import validated_flow or the old engine. Reads only exact dyadic
centers from the certificates, then sums the kernel and integrates directly.
"""
import json
import hashlib
import time
from pathlib import Path
import mpmath as mp

HERE = Path(__file__).resolve().parent
mp.mp.dps = 115


def point(ball):
    m,e = ball["mid_man_exp"]
    return mp.mpf(m)*mp.power(2,e)


def evaluate(t, lam, control, j, n):
    pi = mp.pi
    def f(u):
        e4 = mp.exp(4*u)
        phi = mp.fsum((2*pi*pi*k**4*mp.exp(9*u)-3*pi*k*k*mp.exp(5*u))
                      *mp.exp(-pi*k*k*e4) for k in range(1,13))
        return phi*mp.exp(lam*u*u+control*u**(2*j))*(2*u)**n*mp.cos(2*t*u+n*pi/2)
    return mp.quad(f,[mp.mpf(k)/8 for k in range(17)],method="gauss-legendre")


def main():
    started = time.monotonic()
    rows = []
    inputs = {}
    for family,j in (("sextic",3),("quartic",2)):
        cert = json.loads((HERE/f"results/{family}_cusp_certificate.json").read_text())
        inputs[family] = cert["center_exact_dyadic"]
        t,lam,control = map(point,cert["center_exact_dyadic"])
        for n in range(5):
            value = evaluate(t,lam,control,j,n)
            expected = point(cert["point_derivatives"][n])
            difference = abs(value-expected)
            ok = difference < mp.mpf("1e-96")
            rows.append(dict(family=family,order=n,value=mp.nstr(value,102),
                             absolute_difference=mp.nstr(difference,12),
                             agreement_within_1e_96=bool(ok)))
            print(f"{family} d{n}: difference={mp.nstr(difference,8)}, pass={ok}",flush=True)
            if not ok:
                raise AssertionError("Independent numerical check failed")
    result = {"status":"independent_numerical_agreement", "is_rigorous_certificate":False,
              "method":"mpmath 115 dps, Gauss-Legendre, 12 terms, real segment [0,2], 16 subsegments",
              "mpmath_version":mp.__version__,"rows":rows,
              "input_centers_exact_dyadic":inputs,
              "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "elapsed_seconds":time.monotonic()-started}
    (HERE/"results/independent_check.json").write_text(json.dumps(result,indent=2)+"\n")


if __name__ == "__main__":
    main()
