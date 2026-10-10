#!/usr/bin/env python3
"""Exact comparison example for R06; no floating point or external packages.

This is NOT a positive Jacobi-kernel example. It checks that the three
commuting derivative identities alone do not determine the sign of C'.
Run from any directory. JSON is written only with an explicit --output.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import factorial
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


# Sparse polynomial keys are powers of (x, lambda, mu, nu).
def clean(p):
    return {k: v for k, v in p.items() if v}


def add(p, q):
    r = dict(p)
    for k, v in q.items():
        r[k] = r.get(k, Q(0)) + v
    return clean(r)


def scale(p, a):
    return clean({k: a * v for k, v in p.items()})


def diff(p, axis, order=1):
    for _ in range(order):
        r = {}
        for k, v in p.items():
            if k[axis]:
                l = list(k)
                l[axis] -= 1
                r[tuple(l)] = v * k[axis]
        p = r
    return p


def generator(p):
    out = {}
    for axis, order, a in ((1, 2, Q(-1, 4)), (2, 4, Q(1, 16)),
                           (3, 6, Q(-1, 64))):
        part = {}
        for k, v in diff(p, 0, order).items():
            l = list(k)
            l[axis] += 1
            part[tuple(l)] = a * v
        out = add(out, part)
    return out


def at_origin(p):
    return p.get((0, 0, 0, 0), Q(0))


def determinant3(a):
    return (a[0][0] * (a[1][1]*a[2][2] - a[1][2]*a[2][1])
            - a[0][1] * (a[1][0]*a[2][2] - a[1][2]*a[2][0])
            + a[0][2] * (a[1][0]*a[2][1] - a[1][1]*a[2][0]))


def check(sigma):
    p = {(3, 0, 0, 0): Q(1, 6), (4, 0, 0, 0): Q(-1, 24),
         (9, 0, 0, 0): Q(sigma, factorial(9))}
    term, g, j = p, dict(p), 0
    while term:
        j += 1
        term = scale(generator(term), Q(1, j))
        g = add(g, term)
    require(j == 5, "Exponential must terminate exactly at L^5 p = 0")
    for axis, order, a in ((1, 2, Q(-1, 4)), (2, 4, Q(1, 16)),
                           (3, 6, Q(-1, 64))):
        require(diff(g, axis) == scale(diff(g, 0, order), a),
                f"Polynomial heat identity failed: axis {axis}")
    d = [at_origin(diff(g, 0, n)) for n in range(11)]
    require(d == [Q(0), Q(0), Q(0), Q(1), Q(-1), Q(0), Q(0),
                  Q(0), Q(0), Q(sigma), Q(0)], "Unexpected cusp jet")
    jac = [[at_origin(diff(diff(g, 0, n), axis)) for axis in range(3)]
           for n in range(3)]
    det = determinant3(jac)
    require(det == Q(-1, 64), "Cusp graph Jacobian is singular or wrong")
    nu_rhs = [at_origin(diff(diff(g, 0, n), 3)) for n in range(3)]
    require(nu_rhs == [0, 0, 0], "Cusp tangent should vanish at nu=0")
    # Invertibility of jac and nu_rhs=0 give c'(0)=0 exactly.
    adot = at_origin(diff(diff(g, 0, 3), 3))
    bdot = at_origin(diff(diff(g, 0, 4), 3))
    kdot = (d[3]*bdot - adot*d[4]) / d[4]**2
    cprime_over_sqrt2 = Q(8, 3) * kdot
    require(adot == Q(-sigma, 64) and bdot == 0, "Jet transport failed")
    require(cprime_over_sqrt2 == Q(-sigma, 24), "Opening derivative failed")
    return {"sigma": sigma, "polynomial_monomials": len(g),
            "identities_checked_as_polynomials": 3,
            "cusp_jet_D0_to_D10": [str(v) for v in d],
            "cusp_jacobian_determinant": str(det),
            "cusp_tangent": ["0", "0", "0"],
            "C_prime_over_sqrt2": str(cprime_over_sqrt2)}


def run():
    rows = [check(sigma) for sigma in (-1, 1)]
    require(Q(rows[0]["C_prime_over_sqrt2"]) > 0
            and Q(rows[1]["C_prime_over_sqrt2"]) < 0, "Signs not opposite")
    return {"status": "exact_polynomial_checks_passed", "examples": rows,
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "Three heat identities alone do not force an opening direction.",
            "limitation": "Polynomials are not asserted to be transforms of positive Jacobi-type kernels; no priority claim."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as f:
            f.write(rendered)
    print(rendered, end="")
