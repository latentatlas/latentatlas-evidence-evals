"""Real-parameter enclosures for the polynomial de Bruijn--Newman family.

The integrator sees an ENTIRE FINITE SUM. The omitted kernel series is bounded
on the real integration segment, outside the quadrature callback. The infinite
domain tail has a separate, uniform exponential majorant. See PROOF.md.
No code from the original certification engine is imported.
"""
from flint import arb, acb, arb_mat


def upper(x):
    """An exact dyadic upper bound, never a midpoint or a binary64 number."""
    x = arb(x)
    if not x.is_finite():
        raise ValueError("Nonfinite bound")
    return x.upper()


def max_upper(xs):
    # Comparisons are between exact dyadics, NOT overlapping balls.
    return max(upper(x) for x in xs)


def norm_vec(v):
    return max_upper(abs(x) for x in v)


def norm_mat(a):
    return max_upper(sum((abs(x) for x in row), arb(0)) for row in a)


def zero_ball(radius):
    return arb(0, upper(radius))


def positive_part_upper(a):
    return max(arb(0), upper(a))


def parameter_majorant(params, u):
    return sum((positive_part_upper(a) * u ** (2*j)
                for j, a in params.items()), arb(0))


def domain_tail(params, n, U):
    """Uniform real-axis bound for derivative n on [U,infinity).

    For each positive coefficient of degree d, U >= (d-1)/4 makes
    u**(d-1)*exp(-4u) decreasing. Thus c>0 below implies E'(u)<=-c
    for EVERY u>=U, not just at the cut-off.
    """
    U = arb(U)
    if not (U > 0) or n < 0:
        raise ValueError("Need U>0 and n>=0")
    dpoly = arb(0)
    for j, a in params.items():
        a = positive_part_upper(a)
        if a > 0:
            if not U >= arb(2*j-1)/4:
                raise ValueError("Cut-off does not establish a uniform tail")
            dpoly += (2*j) * a * U ** (2*j-1)
    pi = arb.pi()
    c = 4*pi*(4*U).exp() - 9 - arb(n)/U - dpoly
    if not c > 0:
        raise ValueError("Tail derivative majorant is not negative")
    C = 4*pi*pi + 6*pi
    value = C * (2*U)**n * (9*U + parameter_majorant(params, U)
                          - pi*(4*U).exp()).exp() / c
    return upper(value)


def series_tail(params, n, U, N):
    """Integrated real-segment error for dropping all kernel terms >N."""
    U = arb(U)
    if N < 1 or not U > 0 or n < 0:
        raise ValueError("Invalid truncation settings")
    pi = arb.pi()
    k = N+1
    # 16*exp(-3*pi) < 1/2, uniformly for every real u>=0.
    C = 2*pi*pi*(9*U).exp() + 3*pi*(5*U).exp()
    value = U * 2*C * k**4 * (-pi*k*k).exp()
    value *= (2*U)**n * parameter_majorant(params, U).exp()
    return upper(value)


def absolute_derivative_bounds(params, nmax, U=2, pieces=128):
    """Positive majorants on a real partition, without quadrature.

    On [l,r], use u^n<=r^n, 9u<=9r, -pi*exp(4u)<=-pi*exp(4l),
    and the larger endpoint upper bound for each a_j*u^(2j).
    This remains valid for coefficients of either sign and for intervals.
    """
    U = arb(U)
    pi = arb.pi()
    C = 4*pi*pi + 6*pi
    h = U/pieces
    if not h.is_exact() or not U > 0 or nmax < 0:
        raise ValueError("Need a positive exact dyadic partition")
    result = [arb(0) for _ in range(nmax+1)]
    for k in range(pieces):
        l, r = h*k, h*(k+1)
        poly_hi = sum((max_upper([a*l**(2*j), a*r**(2*j)])
                       for j,a in params.items()), arb(0))
        weight = C*h*(9*r+poly_hi-pi*(4*l).exp()).exp()
        power = arb(1)
        for n in range(nmax+1):
            result[n] += weight*power
            power *= 2*r
    return [upper(result[n]+domain_tail(params,n,U)) for n in range(nmax+1)]


def finite_kernel(u, N):
    """Finite entire function; no assertion about its complex series tail."""
    pi = acb.pi()
    e4, e5, e9 = (4*u).exp(), (5*u).exp(), (9*u).exp()
    total = acb(0)
    for k in range(1, N+1):
        p = pi*(k*k)
        total += (2*p*p*e9 - 3*p*e5) * (-p*e4).exp()
    return total


def derivative(t, params, n, *, N=16, U=2, abs_tol="1e-98",
               rel_tol="1e-98", pieces=8):
    """Full infinite-kernel, infinite-domain derivative enclosure.

    t and parameters are real arb values (possibly intervals). The explicit
    quadrature error and both analytic truncation errors are all retained.
    """
    t = acb(arb(t))
    params = {int(j): arb(a) for j, a in params.items()}
    if n < 0 or pieces < 1 or any(j < 1 for j in params):
        raise ValueError("Invalid derivative, subdivision, or polynomial")
    cut = arb(U)
    if not cut.is_exact() or not cut > 0:
        raise ValueError("Use an exact positive dyadic cut-off")
    # Prove that both tails are controlled BEFORE running quadrature.
    tail = upper(series_tail(params, n, cut, N)
                 + domain_tail(params, n, cut))

    def integrand(u, analytic):
        # A conservative evaluation-domain restriction prevents extreme
        # double-exponential complex growth. A nonfinite result is allowed
        # by Arb's contract and forces subdivision; no finite fake error.
        if not (4*u).exp().real > 0:
            return acb("nan", "nan")
        P = sum((acb(a)*u**(2*j) for j, a in params.items()), acb(0))
        z = 2*t*u
        trig = (z.cos(), -z.sin(), -z.cos(), z.sin())[n % 4]
        return finite_kernel(u, N)*P.exp()*(2*u)**n*trig

    total = acb(0)
    for k in range(pieces):
        total += acb.integral(integrand, acb(cut*k/pieces),
                              acb(cut*(k+1)/pieces),
                              abs_tol=arb(abs_tol)/pieces,
                              rel_tol=arb(rel_tol), eval_limit=100000)
    if not total.is_finite():
        raise ArithmeticError("Quadrature did not yield a finite enclosure")
    return total.real + zero_ball(tail)


def cache(t, params, nmax, **kw):
    return [derivative(t, params, n, **kw) for n in range(nmax+1)]


def jacobian(c, equations, shifts, factors):
    return [[factors[j]*c[n+shifts[j]] for j in range(len(shifts))]
            for n in equations]


def hessian_bound(bounds, equations, shifts, factors):
    return max_upper(sum((abs(factors[p]*factors[q])
                          * bounds[n+shifts[p]+shifts[q]]
                          for p in range(len(shifts))
                          for q in range(len(shifts))), arb(0))
                     for n in equations)


def matmul(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))), arb(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def matvec(a, v):
    return [sum((x*y for x, y in zip(row, v)), arb(0)) for row in a]


def midpoint_inverse(a):
    inv = arb_mat(a).inv()
    return [[inv[i,j].mid() for j in range(inv.ncols())]
            for i in range(inv.nrows())]


def serialize(x):
    """Lossless dyadic ball plus an outward-enclosing readable decimal."""
    x = arb(x)
    if not x.is_finite():
        raise ValueError("Cannot serialize a nonfinite proof quantity")
    return {"enclosure": x.str(30),
            "mid_man_exp": [int(v) for v in x.mid().man_exp()],
            "rad_man_exp": [int(v) for v in x.rad().man_exp()]}
