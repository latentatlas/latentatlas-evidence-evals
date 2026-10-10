"""Three-variable real Taylor enclosures using the frozen cusp integrator.

No new quadrature rule is introduced here. The nonnegative real remainder
retains the derivative order of each multinomial term; see PROOF.md.
"""
import hashlib
import json
import platform
import sys
from math import factorial
from pathlib import Path

import flint
from flint import arb, ctx

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "cusp_verified"
sys.path.insert(0, str(BASE))
from validated_flow import (absolute_derivative_bounds, cache, serialize,
                            upper, zero_ball)
from local_roots import restore


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_baseline():
    manifest = json.loads((BASE / "manifest.json").read_text())
    checked = []
    for entry in manifest["files"]:
        path = BASE / entry["path"]
        if digest(path) != entry["sha256"]:
            raise ArithmeticError(f"Baseline changed: {entry['path']}")
        checked.append(entry["path"])
    return {"manifest_sha256": digest(BASE / "manifest.json"),
            "verified_files": checked}


class TaylorBox:
    def __init__(self, order=8, nmax=6, *, reuse_cache=True):
        if order < 2 or nmax < 0:
            raise ValueError("Invalid Taylor order or derivative range")
        self.baseline = verify_baseline()
        certificate = BASE / "results/quartic_cusp_certificate.json"
        self.certificate = json.loads(certificate.read_text())
        self.x = [restore(v) for v in self.certificate["center_exact_dyadic"]]
        if not all(v.is_exact() for v in self.x):
            raise ArithmeticError("Working precision cannot restore exact center")
        self.order, self.nmax = order, nmax
        # These are permitted evaluation domains, with slack around the
        # smaller theorem domains. Their endpoints are exact dyadics.
        self.half = [arb(2)**-8, arb(2)**-12, arb(2)**-19]
        self.cmax = nmax + 4*(order-1)
        settings = dict(N=16, U=2, pieces=8,
                        abs_tol="1e-98", rel_tol="1e-98")
        identity = {
            "certificate_sha256": digest(certificate),
            "integrator_sha256": digest(BASE / "validated_flow.py"),
            "center_exact_dyadic": self.certificate["center_exact_dyadic"],
            "maximum_derivative": self.cmax,
            "bits": ctx.prec, "python_flint": flint.__version__,
            "quadrature": settings,
        }
        cache_path = HERE / "results/center_derivatives.json"
        old = json.loads(cache_path.read_text()) if cache_path.exists() else None
        if reuse_cache and old is not None and old.get("identity") == identity:
            self.c = [restore(v) for v in old["derivatives"]]
            if len(self.c) != self.cmax+1 or not all(v.is_finite() for v in self.c):
                raise ArithmeticError("Invalid central derivative cache")
        else:
            print(f"Integrating central derivatives 0..{self.cmax}", flush=True)
            self.c = cache(self.x[0], {1:self.x[1], 2:self.x[2]},
                           self.cmax, **settings)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps({"identity":identity,
                "derivatives":[serialize(v) for v in self.c]}, indent=2)+"\n")
        self.cache_path = cache_path
        self.identity = identity
        params = {1:self.x[1]+zero_ball(self.half[1]),
                  2:self.x[2]+zero_ball(self.half[2])}
        self.B = absolute_derivative_bounds(params, nmax+4*order)
        self.terms = []
        self.remainder_terms = []
        for p in range(order+1):
            for q in range(order+1-p):
                for r in range(order+1-p-q):
                    term = (p,q,r,p+2*q+4*r,
                            arb(1)/(factorial(p)*factorial(q)*factorial(r)))
                    (self.terms if p+q+r < order
                     else self.remainder_terms).append(term)

    def evaluate(self, n, dt, dl, dm):
        if not 0 <= n <= self.nmax:
            raise ValueError("Derivative outside the certified range")
        offsets = [arb(dt), arb(dl), arb(dm)]
        for value, allowed in zip(offsets, self.half):
            if not value.is_finite() or not upper(abs(value)) <= allowed:
                raise ValueError("Requested interval leaves the Taylor domain")
        directions = [offsets[0], -offsets[1]/4, offsets[2]/16]
        # python-flint 0.9.0's real __pow__ routes a zero-crossing ball
        # through a general power and can return nan even for exponent 1.
        # Repeated interval multiplication is valid for every real ball.
        powers = []
        for a in directions:
            row = [arb(1)]
            for _ in range(self.order):
                row.append(row[-1]*a)
            powers.append(row)
        magnitudes = [[upper(abs(a))**p for p in range(self.order+1)]
                      for a in directions]
        polynomial = sum((powers[0][p]*powers[1][q]*powers[2][r]
                          * coefficient * self.c[n+shift]
                          for p,q,r,shift,coefficient in self.terms), arb(0))
        remainder = upper(sum((magnitudes[0][p]*magnitudes[1][q]
                               *magnitudes[2][r]*coefficient*self.B[n+shift]
                               for p,q,r,shift,coefficient in self.remainder_terms),
                              arb(0)))
        return polynomial+zero_ball(remainder), remainder

    def derivatives(self, dt, dl, dm, upto=6):
        return [self.evaluate(n,dt,dl,dm)[0] for n in range(upto+1)]

    def provenance(self):
        return {"baseline":self.baseline,
                "central_derivatives_sha256":digest(self.cache_path),
                "identity":self.identity,
                "taylor_order":self.order,
                "domain_half_widths":[serialize(v) for v in self.half],
                "uniform_derivative_bounds":[serialize(v) for v in self.B],
                "python":platform.python_version()}
