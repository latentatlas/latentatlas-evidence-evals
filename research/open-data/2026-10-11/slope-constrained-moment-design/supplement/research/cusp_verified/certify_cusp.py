#!/usr/bin/env python3
"""Rebuild one cusp certificate and its local fold-geometry coefficients.

Use the contraction map x -> x-YG(x), with a fixed exact dyadic Y. No
Newton--Kantorovich large uniqueness radius is inferred from a small box.
"""
import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import flint
from flint import arb, arb_mat, ctx
from validated_flow import (absolute_derivative_bounds, cache, domain_tail,
    hessian_bound, jacobian, matmul, matvec, max_upper, midpoint_inverse,
    norm_mat, norm_vec, serialize, series_tail, upper, zero_ball)

HERE = Path(__file__).resolve().parent
CENTRE = [
    "44.2855634495954422721954241262900386326176429261573811378292387076846961",
    "-12.4370294944650469285355127627853706405082966227144254523860103143362578",
    "-28.8245326953905024900972546968668004761274237319355650936876615486277542",
]
QUARTIC_SEED = [
    "41.40034135868425088942455355819431055151139612255427483833",
    "-3.64569206160491909880688177327333527653667092707336707041",
    "8.33512049891860723771002354711907576727085121011107914060",
]


def build_certificate(dps=110, N=16, pieces=8, family="sextic"):
    ctx.dps = dps
    started = time.monotonic()
    # Exact dyadic points, with exact serialization in the certificate.
    j = 3 if family == "sextic" else 2
    control_name = "nu" if j == 3 else "mu"
    decimal_input = CENTRE if j == 3 else QUARTIC_SEED
    x = [arb(v).mid() for v in decimal_input]
    radius = arb("1e-24").lower()
    settings = dict(N=N, U=2, pieces=pieces,
                    abs_tol=f"1e-{dps-12}", rel_tol=f"1e-{dps-12}")
    shifts = [1,2,2*j]
    factors = [arb(1), -arb(1)/4, arb((-1)**j)/(4**j)]
    eqs = [0,1,2]
    refinement_steps = []
    if family == "quartic":
        for _ in range(5):
            c = cache(x[0], {1:x[1],j:x[2]}, 2+2*j, **settings)
            J = jacobian(c,eqs,shifts,factors)
            step = matvec(midpoint_inverse(J),c[:3])
            refinement_steps.append(serialize(norm_vec(step)))
            if norm_vec(step) < arb(f"1e-{dps-35}"):
                break
            x = [(a-b).mid() for a,b in zip(x,step)]
        else:
            raise ArithmeticError("Candidate refinement failed")
    params = {1: x[1], j: x[2]}
    box_params = {i: a+zero_ball(radius) for i, a in params.items()}
    print("Evaluating derivatives 0..8 with finite-sum quadrature", flush=True)
    c = cache(x[0], params, 8, **settings)
    J = jacobian(c, eqs, shifts, factors)
    Y = midpoint_inverse(J)
    Ydet = arb_mat(Y).det()
    if Ydet.contains(0):
        raise ArithmeticError("Preconditioner nonsingularity not established")
    YJ = matmul(Y, J)
    residual_matrix = [[arb(i == j)-YJ[i][j] for j in range(3)]
                       for i in range(3)]
    q0 = norm_mat(residual_matrix)
    max_bound_order = max(2+4*j,8+2*j)
    B = absolute_derivative_bounds(box_params,max_bound_order)
    M2 = hessian_bound(B, eqs, shifts, factors)
    ynorm = norm_mat(Y)
    eta = norm_vec(matvec(Y, c[:3]))
    q = upper(q0+ynorm*M2*radius)
    image_radius = upper(eta+q*radius)
    passed = q < 1 and image_radius < radius
    if not passed:
        raise ArithmeticError("Contraction/self-mapping test failed")
    root_radius = upper(eta/(1-q))
    # Enclose derivatives at the actual root by the mean value theorem;
    # the segment stays in the already verified box.
    root_derivs = []
    for n in range(9):
        delta = upper(root_radius * sum((abs(f)*B[n+s]
                                        for s,f in zip(shifts,factors)), arb(0)))
        root_derivs.append(c[n]+zero_ball(delta))
    D3, D4 = root_derivs[3], root_derivs[4]
    Fcontrol = factors[2]*root_derivs[2*j]
    Ftcontrol = factors[2]*root_derivs[2*j+1]
    control_det = Fcontrol*D3/4  # F_lambda=0 exactly at the proved cusp.
    Jdet_at_root = D3*control_det
    # Expanding the first column at a cusp gives a PLUS sign (row 3,
    # column 1). Check against a full matrix determinant as well.
    direct_Jdet = arb_mat(jacobian(root_derivs,eqs,shifts,factors)).det()
    if not (direct_Jdet-Jdet_at_root).contains(0):
        raise ArithmeticError("Full Jacobian determinant disagrees with cusp identity")
    if not (D3 > 0) or control_det.contains(0):
        raise ArithmeticError("Cusp/versal nondegeneracy not established")
    control_cubic = D3/(3*Fcontrol)
    lambda_cubic = arb(4)/3*(Ftcontrol/Fcontrol-D4/D3)
    geometry = {
        "lambda_quadratic_exact": "2",
        "lambda_cubic": serialize(lambda_cubic),
        "second_control": control_name,
        "second_control_cubic": serialize(control_cubic),
        "semicubical_ratio": serialize(control_cubic*control_cubic/8),
        "F_second_control": serialize(Fcontrol),
        "control_determinant": serialize(control_det),
        "G_determinant_at_root": serialize(Jdet_at_root),
        "G_determinant_direct_enclosure": serialize(direct_Jdet),
        "scope": "Taylor jets at the proved cusp; no explicit finite neighborhood or remainder constant is certified here.",
    }
    source_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (HERE/"validated_flow.py", HERE/"certify_cusp.py")}
    report = {
        "schema": "cusp-certificate-v1",
        "status": "contraction_and_cusp_checks_passed",
        "family": family,
        "scope": f"Only lambda and {control_name} active, unknowns (t,lambda,{control_name}), one explicitly specified root box",
        "trust_boundary": "Analytic bounds in PROOF.md plus Python/FLINT/Arb; not a formal proof-assistant verification or an independent expert review.",
        "environment": {"python": platform.python_version(),
                        "python_flint": flint.__version__, "dps": dps,
                        "bits": ctx.prec},
        "quadrature": settings,
        "center_decimal_input": decimal_input,
        "candidate_refinement_step_bounds": refinement_steps,
        "center_exact_dyadic": [serialize(v) for v in x],
        "radius": serialize(radius),
        "point_derivatives": [serialize(v) for v in c],
        "absolute_derivative_bounds": [serialize(v) for v in B],
        "jacobian_at_center": [[serialize(v) for v in row] for row in J],
        "preconditioner_exact_dyadic": [[serialize(v) for v in row] for row in Y],
        "preconditioner_det": serialize(Ydet),
        "q0": serialize(q0), "Y_norm_bound": serialize(ynorm),
        "M2_bound_on_entire_box": serialize(M2), "eta": serialize(eta),
        "q": serialize(q), "image_radius": serialize(image_radius),
        "root_radius": serialize(root_radius),
        "root_derivative_enclosures": [serialize(v) for v in root_derivs],
        "geometry": geometry,
        "series_tail_order8": serialize(series_tail(params,8,arb(2),N)),
        "domain_tail_max_bound_order": serialize(domain_tail(box_params,max_bound_order,arb(2))),
        "source_sha256": source_hashes,
        "elapsed_seconds": time.monotonic()-started,
    }
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dps", type=int, default=110)
    ap.add_argument("--terms", type=int, default=16)
    ap.add_argument("--pieces", type=int, default=8)
    ap.add_argument("--family", choices=["sextic","quartic"],default="sextic")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    report = build_certificate(args.dps,args.terms,args.pieces,args.family)
    if args.output is None:
        args.output = HERE/f"results/{args.family}_cusp_certificate.json"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("status","eta","q","root_radius","geometry","elapsed_seconds")},indent=2))


if __name__ == "__main__":
    main()
