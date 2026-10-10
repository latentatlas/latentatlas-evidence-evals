#!/usr/bin/env python3
"""R11: one exact smooth feasible design and a universal norm lower bound."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'cusp_shape_design'
sys.path.insert(0, str(BASE))
from moment_dictionary import restore, pack, upper, zero_ball
from validated_flow import derivative, finite_kernel, series_tail, domain_tail
from flint import arb, acb, arb_mat, ctx


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(value, message):
    if not value:
        raise ArithmeticError(message)


def positive_moment(x, n):
    """Integral of rho*(2u)^n at the exact dyadic parameter center."""
    _, lam, mu = x
    params = {1: lam, 2: mu, 3: arb(0)}
    N, U, panels = 16, arb(2), 8
    tail = upper(series_tail(params, n, U, N) + domain_tail(params, n, U))

    def fun(u, analytic):
        if not (4*u).exp().real > 0:
            return acb('nan', 'nan')
        return finite_kernel(u, N)*(acb(lam)*u*u + acb(mu)*u**4).exp()*(2*u)**n

    total = acb(0)
    for k in range(panels):
        total += acb.integral(fun, acb(U*k/panels), acb(U*(k+1)/panels),
                             abs_tol=arb('1e-93')/panels, rel_tol=arb('1e-93'), eval_limit=100000)
    need(total.is_finite(), 'Positive moment did not converge')
    return total.real + zero_ball(tail)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), 'Refuse to overwrite a recorded result')
    start = time.monotonic()
    ctx.dps = 110
    qp = HERE.parent / 'cusp_verified/results/quartic_cusp_certificate.json'
    jp = BASE / 'results/local_jets.json'
    q, jets = json.loads(qp.read_text()), json.loads(jp.read_text())
    x = list(map(restore, q['center_exact_dyadic']))
    r = restore(q['root_radius'])
    B = list(map(restore, q['absolute_derivative_bounds']))
    f = list(map(restore, jets['F_at_exact_Q']))[:9]
    f[:3] = [arb(0)]*3
    need(f[3] > 0, 'Base zero order not established')
    frequencies = [40, 41, 42, 43]
    rows = []
    for frequency in frequencies:
        moments, pairs = [], []
        for n in range(9):
            pair = [derivative(x[0] + sign*frequency, {1:x[1], 2:x[2], 3:arb(0)}, n,
                              N=16, U=2, pieces=8, abs_tol='1e-93', rel_tol='1e-93')
                    for sign in (-1, 1)]
            displacement = upper(r*(B[n+1] + B[n+2]/4 + B[n+4]/16))
            moments.append(sum(pair, arb(0))/2 + zero_ball(displacement))
            pairs.append(pair)
        rows.append({'frequency':frequency, 'moments':moments, 'shifted_integrals':pairs})
        print('Frequency', frequency, 'complete', flush=True)
    M = [[rows[j]['moments'][n] for j in range(4)] for n in range(9)]
    A = arb_mat(M[:4])
    det = A.det()
    need(not det.contains(0), 'Moment design matrix not certified invertible')
    b = [arb(0), arb(0), arb(0), -f[3]]
    solution = A.solve(arb_mat([[v] for v in b]))
    w = [solution[i,0] for i in range(4)]
    cost = sum((abs(v) for v in w), arb(0))
    need(cost < 1, 'Relative-norm budget does not ensure positivity')
    response = [sum((M[n][j]*w[j] for j in range(4)), arb(0)) for n in range(9)]
    g = [f[n]+response[n] for n in range(9)]
    need(all(g[n].contains(0) for n in range(4)), 'Enclosed solve residual inconsistent')
    # These identities follow from the EXACT defining linear system, not small residuals.
    g[:4] = [arb(0)]*4
    need(not g[4].contains(0), 'Order exactly four unresolved')
    rank = g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    need(not rank.contains(0), 'Three-control unfolding rank unresolved')
    a3_center = positive_moment(x, 3)
    a3 = a3_center + zero_ball(upper(r*(B[5]/4+B[7]/16)))
    need(a3 > 0, 'Positive absolute moment not bounded away from zero')
    lower = f[3]/a3
    need(lower > 0 and lower < cost, 'Norm bounds inconsistent')
    out = {
        'status':'exact_smooth_pinned_order_four_design_and_universal_norm_bracket_passed',
        'frozen_R10_manifest_sha256':sha(HERE.parent/'swallowtail_window/manifest.json'),
        'input_sha256':{'R01_quartic_certificate':sha(qp), 'R09_local_jets':sha(jp)},
        'source_sha256':{'certify_candidate.py':sha(__file__),
                         '../cusp_verified/validated_flow.py':sha(HERE.parent/'cusp_verified/validated_flow.py')},
        'frequencies':frequencies,
        'center':x, 'Q_radius':r,
        'quadrature':{'dps':110, 'terms':16, 'cutoff':2, 'panels':8, 'tolerance':'1e-93'},
        'dictionary':rows, 'base_derivatives':f,
        'design_matrix':M[:4], 'design_matrix_determinant':det, 'target':b,
        'weights':w, 'moment_response':response, 'modified_derivatives':g,
        'three_control_determinant':rank,
        'positive_moment_3_at_center':a3_center, 'positive_moment_3_at_exact_Q':a3,
        'universal_norm_lower_bound':lower,
        'feasible_coefficient_l1_cost':cost,
        'kernel_multiplier_lower_bound':1-cost,
        'bracket_ratio_upper':cost/lower,
        'definition':'At exact Q, let A_nj be the exact cosine moments for n=0..3 and j=40..43. Define w by A*w=(0,0,0,-F3). Then h=sum w_j*cos(2*j*u). No rounded coefficients define h.',
        'objective_scope':'Bound the infimum of ||h||_infinity over all real measurable bounded h that keep Q fixed and cancel derivative 3. The upper bound uses one smooth cosine candidate, not a claimed optimizer; l1 cost need not equal its supremum norm.',
        'nondegeneracy_scope':'The new candidate has order exactly four and rank-three lambda/mu/nu unfolding. R10 finite-window bounds and figures have not been transferred to this different kernel.',
        'trust_boundary':'New Arb shifted integrals and one positive moment include analytic series/domain tails and exact-Q displacement. The rational checker takes these integral enclosures and frozen R09 derivatives as inputs.',
        'elapsed_seconds':time.monotonic()-start,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(pack(out), stream, indent=2)
        stream.write('\n')
    print('Universal norm lower bound:', lower)
    print('Smooth feasible l1 upper bound:', cost)
    print('Bracket ratio:', cost/lower)
    print('Modified fourth derivative:', g[4])
    print('Three-control determinant:', rank)


if __name__ == '__main__':
    main()
