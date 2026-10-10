"""Regressions for proof-affecting failures, not numerical smoke tests."""
import unittest
import json
from pathlib import Path
from flint import arb, ctx
from validated_flow import (absolute_derivative_bounds, derivative, domain_tail,
                            max_upper, norm_vec, norm_mat, series_tail)


class ProofRegressions(unittest.TestCase):
    def setUp(self):
        ctx.dps = 80

    def test_overlapping_interval_norm(self):
        a,b = arb(1,"0.9"),arb("1.5","0.9")
        self.assertGreaterEqual(norm_vec([a,b]),b.upper())
        self.assertGreaterEqual(norm_mat([[a,arb(0)],[b,arb(0)]]),b.upper())

    def test_unsafe_high_degree_tail_is_rejected(self):
        with self.assertRaises(ValueError):
            domain_tail({10:arb("0.0001")},0,2)

    def test_degree_four_positive_parameter_is_supported(self):
        bound=domain_tail({1:arb(-4),2:arb(9)},40,2)
        self.assertTrue(bound>0)
        self.assertTrue(bound<arb("1e-3800"))

    def test_derivative_factors_in_series_tail(self):
        low=series_tail({},0,arb(2),16)
        high=series_tail({},8,arb(2),16)
        self.assertTrue(abs(high/low-arb(4**8))<arb("1e-65"))

    def test_severe_series_truncation_is_still_enclosed(self):
        # The n=2 term is deliberately not negligible. The N=1 interval
        # must retain its error instead of silently looking high-precision.
        kw=dict(abs_tol="1e-60",rel_tol="1e-60")
        coarse=derivative(arb(2),{1:arb(-1)},2,N=1,**kw)
        fine=derivative(arb(2),{1:arb(-1)},2,N=12,**kw)
        self.assertTrue(coarse.contains(fine))

    def test_absolute_moment_bounds_dominate_point_derivatives(self):
        p={1:arb(-4),2:arb(8)}
        b=absolute_derivative_bounds(p,12)
        for n in (0,3,8,12):
            d=derivative(arb(41),p,n,abs_tol="1e-60",rel_tol="1e-60")
            self.assertTrue(abs(d)<b[n])

    def test_nonfinite_norm_is_rejected(self):
        with self.assertRaises(ValueError):
            max_upper([arb(1),arb("nan")])

    def test_taylor_enclosures_against_direct_quadrature(self):
        from local_roots import TaylorEnclosure,restore
        ctx.dps=110
        root=Path(__file__).resolve().parent
        d=json.loads((root/"results/quartic_cusp_certificate.json").read_text())
        x=[restore(v) for v in d["center_exact_dyadic"]]
        model=TaylorEnclosure(x,"0.0031","0.00000101")
        for s,dl in ((arb(2)/1000,arb(1)/1000000),
                     (-arb(5)/10000,-arb(1)/1000000)):
            for n in (0,1,3):
                box,_=model.evaluate(n,s,dl)
                point=derivative(x[0]+s,{1:x[1]+dl,2:x[2]},n,
                                 N=20,pieces=16,abs_tol="1e-96",rel_tol="1e-96")
                self.assertTrue(box.contains(point))

    def test_precision_variant_is_inside_primary_uniqueness_box(self):
        from local_roots import restore
        ctx.dps=160
        root=Path(__file__).resolve().parent/"results"
        a=json.loads((root/"quartic_cusp_certificate.json").read_text())
        b=json.loads((root/"quartic_precision_check.json").read_text())
        radius=restore(a["radius"])
        r_alt=restore(b["root_radius"])
        for aa,bb in zip(a["center_exact_dyadic"],b["center_exact_dyadic"]):
            self.assertTrue(abs(restore(aa)-restore(bb))+r_alt<radius)

    def test_cusp_determinant_sign_by_full_matrix(self):
        from local_roots import restore
        from validated_flow import jacobian
        from flint import arb_mat
        ctx.dps=110
        root=Path(__file__).resolve().parent/"results"
        for family,j in (("quartic",2),("sextic",3)):
            d=json.loads((root/f"{family}_cusp_certificate.json").read_text())
            c=[restore(v) for v in d["root_derivative_enclosures"]]
            direct=arb_mat(jacobian(c,[0,1,2],[1,2,2*j],
                                   [arb(1),-arb(1)/4,arb((-1)**j)/(4**j)])).det()
            derived=restore(d["geometry"]["G_determinant_at_root"])
            self.assertTrue((direct-derived).contains(0))
            self.assertTrue(direct*derived>0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
