#!/usr/bin/env python3
"""Exact small diagnostics for R18's norm and parameter translations.

No dependency on the theta calculations and no novelty/proof certificate.
Two-variable linear programs are solved by rational vertex enumeration.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path


def vertex_max(rows, objective):
    """Maximize c.x over a nonempty bounded polygon, including segments."""
    points = set()
    for (a, b, c), (d, e, f) in combinations(rows, 2):
        det = a * e - b * d
        if not det:
            continue
        x, y = (c * e - b * f) / det, (a * f - c * d) / det
        if all(r * x + s * y <= t for r, s, t in rows):
            points.add((x, y))
    assert points, "No feasible vertex; invalid diagnostic LP"
    value, point = max((objective[0] * x + objective[1] * y, (x, y))
                       for x, y in points)
    return value, point


def norm_lp(A, M, d, weights=(-1, 1), zero_first=False):
    A, M, d = map(F, (A, M, d))
    assert A > 0 and M > 0 and d > 0
    rows = [(F(1), F(0), A), (F(-1), F(0), A),
            (F(0), F(1), A), (F(0), F(-1), A),
            (F(-1), F(1), M*d), (F(1), F(-1), M*d)]
    if zero_first:
        rows += [(F(1), F(0), F(0)), (F(-1), F(0), F(0))]
    return vertex_max(rows, tuple(map(F, weights)))


def run_checks():
    assert not sys.flags.optimize, "Assertions must be enabled"
    checks = []
    cases = [(F(1), F(1,4), F(1)), (F(1), F(2), F(1)),
             (F(2,3), F(7,2), F(4,5)), (F(5,4), F(3,5), F(7,3))]
    atom_values = []
    for A, M, d in cases:
        pair, point = norm_lp(A, M, d)
        positive, _ = norm_lp(A, M, d, (1, 0))
        assert pair == min(2*A, M*d)
        assert positive == A
        atom_values.append(dict(A=str(A), M=str(M), distance=str(d),
                                pair_value=str(pair), witness=list(map(str, point)),
                                positive_atom_value=str(positive)))
    checks.append(dict(id='atom_norms_from_exact_LP', cases=atom_values))

    rescalings = []
    for A, M, d in cases:
        # Unequal weights also exercise nonzero total signed mass.
        weights = (F(-2,3), F(5,4))
        direct, _ = norm_lp(A, M, d, weights)
        unit_A, _ = norm_lp(1, M/A, d, weights)
        unit_M, _ = norm_lp(A/M, 1, d, weights)
        C = 2*A/M
        hkm_dual, _ = norm_lp(C/2, 1, d, weights)
        coordinate_scale = F(7,3)
        new_coordinate, _ = norm_lp(A, M/coordinate_scale,
                                     d*coordinate_scale, weights)
        assert direct == A*unit_A == M*unit_M == M*hkm_dual == new_coordinate
        rescalings.append(dict(A=str(A), M=str(M), distance=str(d), C=str(C),
                               value=str(direct), unit_amplitude=str(unit_A),
                               unit_slope=str(unit_M), coordinate_value=str(new_coordinate)))
    checks.append(dict(id='amplitude_slope_HKM_coordinate_scalings', cases=rescalings))

    constrained, witness = norm_lp(1, F(1,4), 1, (0,1), zero_first=True)
    unlimited_dual_a0, _ = norm_lp(1, F(1,4), 1, (0,1))
    finite_dual_a1, _ = norm_lp(1, F(1,4), 1, (-1,1))
    assert constrained == finite_dual_a1 == F(1,4) < unlimited_dual_a0 == 1
    checks.append(dict(id='fixed_unlimited_dual_is_not_finite_M_dual',
                       constrained_value=str(constrained), witness=list(map(str,witness)),
                       fixed_a0_value=str(unlimited_dual_a0), a1_value=str(finite_dual_a1)))

    # On {0,1}, max(|x|,|y|)+|y-x| <= 1 is eight linear inequalities.
    sum_rows = []
    for s, t in product((F(-1),F(1)), repeat=2):
        sum_rows += [(s-t,t,F(1)), (-t,s+t,F(1))]
    sum_norm, sum_point = vertex_max(sum_rows, (F(-1),F(1)))
    max_norm, _ = norm_lp(1,1,1)
    assert sum_norm == F(2,3) < max_norm == 1
    checks.append(dict(id='max_and_sum_norms_have_different_values',
                       sum_value=str(sum_norm), sum_witness=list(map(str,sum_point)),
                       max_value=str(max_norm)))

    # HKM equation (2): mu=delta_0, nu=0, p=1, C=2. Only plan is zero.
    C=F(2); mass_mu=F(1); mass_nu=F(0); transported=F(0)
    defining_value=C*((mass_mu+mass_nu)/2-transported)
    dual_value, _=norm_lp(C/2,1,1,(1,0))
    TV_half=F(1,2)
    displayed_theorem_value=(C/2)*TV_half
    assert defining_value == dual_value == 1
    assert displayed_theorem_value == F(1,2) != defining_value
    checks.append(dict(id='L11_displayed_TV_factor_conflicts_with_definition',
                       definition=str(defining_value), dual=str(dual_value),
                       displayed_TV_line=str(displayed_theorem_value),
                       action='Use the definition and dual, not the inconsistent TV factor.'))

    continuous=[]
    for A,M in [(F(1),F(1)),(F(1),F(2)),(F(2,3),F(5))]:
        assert M>=A
        a=A/M
        # Integrate the actual piecewise witness, using antiderivatives.
        inner=2*M*a**3/3
        outer=A*(1-a**2)
        integral=inner+outer
        assert integral == A-A**3/(3*M**2)
        assert A-integral > 0
        continuous.append(dict(A=str(A),M=str(M),half_width=str(a),
                               norm_value=str(integral),loss=str(A-integral)))
    checks.append(dict(id='continuous_linear_density_does_not_saturate',cases=continuous))
    return dict(status='R18_exact_normalization_diagnostics_passed',
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                check_groups=len(checks),checks=checks,
                mathematical_scope='Small norm/duality diagnostics only; not a formal theorem or priority certificate.')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path)
    args=ap.parse_args(); result=run_checks()
    if args.output:
        assert not args.output.exists(), 'Refuse to overwrite a prior diagnostic result'
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(status=result['status'],check_groups=result['check_groups'],
                              output=str(args.output)),indent=2))
    else:
        print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
