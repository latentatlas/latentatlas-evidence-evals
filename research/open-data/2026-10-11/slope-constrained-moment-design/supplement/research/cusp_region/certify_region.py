#!/usr/bin/env python3
"""Uniform implicit-curve and root-region certificate around quartic cusp."""
import json
import time
from pathlib import Path
from flint import arb, arb_mat, ctx
from taylor_box import TaylorBox, digest, restore
from validated_flow import (matmul, matvec, midpoint_inverse, norm_mat,
                            norm_vec, serialize, upper, zero_ball)

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def control_matrix(d):
    return [[-d[2]/4,d[4]/16],[-d[3]/4,d[5]/16]]


def weighted_matrix(a, radii):
    return [[a[i][j]*radii[j]/radii[i] for j in range(2)]
            for i in range(2)]


def fold_tangent(d):
    delta=d[3]*d[4]-d[2]*d[5]
    return 4*d[2]*d[4]/delta,16*d[2]*d[2]/delta


def uniform_curve(model, T, radii):
    d = model.derivatives(zero_ball(T),zero_ball(radii[0]),
                          zero_ball(radii[1]))
    at_center = control_matrix(model.c)
    Y = midpoint_inverse(at_center)
    require(not arb_mat(Y).det().contains(0), "Singular preconditioner")
    YA = matmul(Y, control_matrix(d))
    defect = [[arb(i==j)-YA[i][j] for j in range(2)] for i in range(2)]
    q = norm_mat(weighted_matrix(defect,radii))
    c = model.derivatives(zero_ball(T),0,0,upto=1)
    image = matvec(Y,c[:2])
    eta_components = [upper(abs(image[i])/radii[i]) for i in range(2)]
    eta = norm_vec(eta_components)
    require(q < 1 and eta+q < 1, "Uniform implicit curve contraction failed")
    # This stronger sign condition also gives analyticity by the IFT.
    delta = d[3]*d[4]-d[2]*d[5]
    require(d[3]>0 and d[4]<0 and delta<0, "Uniform derivative signs failed")
    lp,mp = fold_tangent(d)
    wprime = d[3]-d[4]*lp/4+d[6]*mp/16
    require(wprime > 0, "F_tt is not proved increasing along the fold")
    a = 4*d[4]/delta
    b = -16/delta
    require(a>0 and b>0, "Cusp growth coefficients must be positive")
    quadratic = a*wprime/2
    cubic = b*wprime*wprime/3
    semicubical = cubic/(quadratic*quadratic.sqrt())
    require(quadratic>arb('1.91') and quadratic<arb('2.09'),
            "Readable quadratic bounds failed")
    require(cubic>arb('1.72') and cubic<arb('1.94'),
            "Readable cubic bounds failed")
    require(semicubical>arb('0.57') and semicubical<arb('0.73'),
            "Readable semicubical bounds failed")
    ends = []
    for sign in (-1,1):
        value,_=model.evaluate(2,sign*T,zero_ball(radii[0]),zero_ball(radii[1]))
        require(sign*value>0, "F_tt endpoint sign failed")
        ends.append(serialize(value))
    return {"status":"uniform_contraction_passed",
            "t_half_width":serialize(T),
            "control_half_widths":[serialize(v) for v in radii],
            "preconditioner":[[serialize(v) for v in row] for row in Y],
            "H_on_centerline":[serialize(v) for v in c[:2]],
            "q":serialize(q),"eta":serialize(eta),
            "eta_plus_q":serialize(upper(eta+q)),
            "derivative_enclosures":[serialize(v) for v in d],
            "delta":serialize(delta),
            "lambda_prime":serialize(lp),"mu_prime_formula_enclosure":serialize(mp),
            "F_tt_total_derivative":serialize(wprime),
            "finite_cusp_bounds":{
                "lambda_over_s_squared":serialize(quadratic),
                "absolute_mu_over_absolute_s_cubed":serialize(cubic),
                "absolute_mu_over_lambda_to_three_halves":serialize(semicubical),
                "readable_rational_bounds":{
                    "lambda_over_s_squared":["191/100","209/100"],
                    "absolute_mu_over_absolute_s_cubed":["172/100","194/100"],
                    "absolute_mu_over_lambda_to_three_halves":["57/100","73/100"]},
                "scope":"s=t-t_star along the entire certified fold curve; parameter differences are from the actual cusp, not the rounded center."},
            "F_tt_endpoint_signs":ends}


def contract_at_fixed_t(model,t,radii):
    """Point controls on the uniform curve; an independent local contraction."""
    p = [arb(0),arb(0)]
    for _ in range(6):
        d=model.derivatives(t,*p,upto=5)
        change=matvec(midpoint_inverse(control_matrix(d)),d[:2])
        p=[(a-b).mid() for a,b in zip(p,change)]
    small=[arb(2)**-58,arb(2)**-58]
    dpoint=model.derivatives(t,*p,upto=5)
    Y=midpoint_inverse(control_matrix(dpoint))
    require(not arb_mat(Y).det().contains(0), "Local inverse is singular")
    boxed=[p[i]+zero_ball(small[i]) for i in range(2)]
    db=model.derivatives(t,*boxed,upto=5)
    ya=matmul(Y,control_matrix(db))
    defect=[[arb(i==j)-ya[i][j] for j in range(2)] for i in range(2)]
    q=norm_mat(weighted_matrix(defect,small))
    correction=matvec(Y,dpoint[:2])
    eta=norm_vec([correction[i]/small[i] for i in range(2)])
    require(q<1 and eta+q<1, "Fixed-t local contraction failed")
    require(all(abs(boxed[i])<radii[i] for i in range(2)),
            "Fixed-t root not contained in uniform uniqueness box")
    return {"t_offset":serialize(t),
            "control_offset_boxes":[serialize(v) for v in boxed],
            "center":[serialize(v) for v in p],
            "radii":[serialize(v) for v in small],
            "preconditioner":[[serialize(v) for v in row] for row in Y],
            "point_derivatives":[serialize(v) for v in dpoint],
            "box_derivatives":[serialize(v) for v in db],
            "q":serialize(q),"eta":serialize(eta)},boxed


def contract_at_right_boundary(model,L,M,T,radii,sign):
    """Enclose the two fold intersections with lambda=lambda0+L."""
    t=sign*(L/2).sqrt()
    m=(16*model.c[3]/(3*model.c[4]))*t*t*t
    p=[t.mid(),m.mid()]
    def matrix(d):
        return [[d[1],d[4]/16],[d[2],d[5]/16]]
    for _ in range(6):
        d=model.derivatives(p[0],L,p[1],upto=5)
        step=matvec(midpoint_inverse(matrix(d)),d[:2])
        p=[(a-b).mid() for a,b in zip(p,step)]
    small=[arb(2)**-45,arb(2)**-65]
    boxed=[p[i]+zero_ball(small[i]) for i in range(2)]
    dp=model.derivatives(p[0],L,p[1],upto=5)
    db=model.derivatives(boxed[0],L,boxed[1],upto=5)
    Y=midpoint_inverse(matrix(dp))
    require(not arb_mat(Y).det().contains(0),"Boundary preconditioner singular")
    ya=matmul(Y,matrix(db))
    defect=[[arb(i==j)-ya[i][j] for j in range(2)] for i in range(2)]
    q=norm_mat(weighted_matrix(defect,small))
    correction=matvec(Y,dp[:2])
    eta=norm_vec([correction[i]/small[i] for i in range(2)])
    require(q<1 and eta+q<1,"Boundary fold contraction failed")
    require(sign*boxed[0]>arb(1)/10000 and abs(boxed[0])<T,
            "Boundary fold must lie on its claimed side of the cusp")
    require(abs(boxed[1])<M and abs(boxed[1])<radii[1] and L<radii[0],
            "Boundary fold is outside the control regions")
    return {"t_sign":sign,"lambda_offset":serialize(L),
            "t_offset_box":serialize(boxed[0]),"mu_offset_box":serialize(boxed[1]),
            "center":[serialize(v) for v in p],
            "radii":[serialize(v) for v in small],
            "preconditioner":[[serialize(v) for v in row] for row in Y],
            "point_derivatives":[serialize(v) for v in dp],
            "box_derivatives":[serialize(v) for v in db],
            "q":serialize(q),"eta":serialize(eta)}


def main():
    ctx.dps=110
    started=time.monotonic()
    model=TaylorBox()
    T=arb(3)/1000
    radii=[arb(2)**-13,arb(2)**-20]
    print("Checking uniform fold curve",flush=True)
    curve=uniform_curve(model,T,radii)
    print("q =",curve["q"]["enclosure"],"eta =",curve["eta"]["enclosure"],flush=True)
    L,M=arb(1)/1000000,arb(1)/500000000
    old_radius=restore(model.certificate['radius'])
    require(all(old_radius<v for v in (T,L/2,M,arb(1)/10000,*radii)),
            "The reference cusp box must lie inside the new domains")
    ends=[]
    for sign in (-1,1):
        d=model.derivatives(sign*T,zero_ball(L),zero_ball(M),upto=3)
        require(sign*d[0]>0, "Root-window boundary sign failed")
        require(d[1]>0, "Root-window boundary derivative failed")
        ends.append({"sign":sign,"derivatives":[serialize(v) for v in d]})
    inside=[]
    for sign in (-1,1):
        item,boxes=contract_at_fixed_t(model,sign*arb(1)/1000,radii)
        require(boxes[0]>L, "Fold has not reached right control boundary")
        require(abs(boxes[1])<M, "Fold may leave through mu boundary first")
        inside.append(item)
    boundary_folds=[contract_at_right_boundary(model,L,M,T,radii,sign)
                    for sign in (-1,1)]
    witnesses=[]
    for sign in (-1,1):
        dl=sign*L/2
        offsets=([-T,T] if sign<0 else
                 [-arb(3)/2000,-arb(3)/10000,arb(3)/10000,arb(3)/2000])
        vals=[model.evaluate(0,s,dl,0)[0] for s in offsets]
        expected=[-1,1] if sign<0 else [-1,1,-1,1]
        require(all(a*v>0 for a,v in zip(expected,vals)), "Root witnesses failed")
        positive_cover=[]
        if sign<0:
            for k in range(32):
                a=-T+2*T*k/32
                b=-T+2*T*(k+1)/32
                value,_=model.evaluate(1,a.union(b),dl,0)
                require(value>0,"One-root witness monotonicity failed")
                positive_cover.append({"left":serialize(a),"right":serialize(b),
                                       "F_t":serialize(value)})
        witnesses.append({"lambda_offset":serialize(dl),"mu_offset":"0",
                          "root_count":1 if sign<0 else 3,
                          "t_offsets":[serialize(v) for v in offsets],
                          "F_values":[serialize(v) for v in vals],
                          "positive_F_t_cover":positive_cover})
    independent_inputs=[]
    for sign in (-1,1):
        offsets=[sign*arb(1)/1000,sign*arb(3)/4000000,sign*arb(1)/1000000000]
        independent_inputs.append({
            "offsets":[serialize(v) for v in offsets],
            "derivatives":{str(n):serialize(model.evaluate(n,*offsets)[0])
                           for n in (0,1,3)}})
    report={"schema":"quartic-cusp-region-v1",
            "status":"region_inequalities_passed",
            "scope":"I=t0+[-3/1000,3/1000]; P=(lambda0,mu0)+[-1/1000000,1/1000000] x [-1/500000000,1/500000000]",
            "trust_boundary":"Conditional on the analytic argument in PROOF.md and the frozen baseline; local computer-assisted result, not externally reviewed.",
            "center_exact_dyadic":model.certificate["center_exact_dyadic"],
            "region_half_widths":{"t":serialize(T),"lambda":serialize(L),"mu":serialize(M)},
            "uniform_curve":curve,"root_window_boundary":ends,
            "right_boundary_folds":boundary_folds,
            "interior_fold_witnesses":inside,"root_count_witnesses":witnesses,
            "independent_check_inputs":independent_inputs,
            "provenance":model.provenance(),
            "source_sha256":{p.name:digest(p) for p in (HERE/"taylor_box.py",HERE/"certify_region.py",HERE/"PROOF.md")},
            "elapsed_seconds":time.monotonic()-started}
    output=HERE/"results/region_certificate.json"
    output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"q":curve["q"]["enclosure"],
                      "eta_plus_q":curve["eta_plus_q"]["enclosure"],
                      "delta":curve["delta"]["enclosure"],
                      "F_tt_total_derivative":curve["F_tt_total_derivative"]["enclosure"],
                      "elapsed_seconds":report["elapsed_seconds"]},indent=2))


if __name__=="__main__":
    main()
