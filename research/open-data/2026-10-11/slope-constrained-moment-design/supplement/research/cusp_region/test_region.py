"""Proof-relevant checks of the new two-control Taylor calculation."""
import json
import unittest
from fractions import Fraction
from flint import arb,ctx
from taylor_box import TaylorBox, HERE, restore
from validated_flow import derivative, matvec, norm_vec
from certify_region import control_matrix, fold_tangent


class RegionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctx.dps=110
        cls.model=TaylorBox()

    def test_zero_crossing_intervals_are_finite_and_contain_center(self):
        # Regression for python-flint real general powers on signed balls.
        from validated_flow import zero_ball
        for n in range(7):
            enclosed,_=self.model.evaluate(n,zero_ball(arb('0.003')),
                    zero_ball(arb('0.000001')),zero_ball(arb('0.000000002')))
            self.assertTrue(enclosed.is_finite())
            self.assertTrue(enclosed.contains(self.model.c[n]))

    def test_two_control_taylor_against_direct_integrals(self):
        m=self.model
        # Both signs and a pure quartic-control displacement. All evaluations
        # are from the integral, with finer truncation and subdivision.
        points=[(arb(3)/1000,arb(1)/1000000,-arb(1)/500000000),
                (-arb(3)/1000,-arb(1)/1000000,arb(1)/500000000),
                (arb(0),arb(0),arb(1)/500000000),
                (arb(1)/2000,arb(3)/4000000,arb(1)/1000000000)]
        for dt,dl,dm in points:
            for n in (0,1,2,3,4,6):
                enclosure,_=m.evaluate(n,dt,dl,dm)
                direct=derivative(m.x[0]+dt,{1:m.x[1]+dl,2:m.x[2]+dm},n,
                                  N=20,pieces=16,abs_tol='1e-96',rel_tol='1e-96')
                self.assertTrue(enclosure.contains(direct),(n,dt,dl,dm))

    def test_domain_escape_and_nonfinite_requests_are_rejected(self):
        with self.assertRaises(ValueError):
            self.model.evaluate(0,arb('0.004'),0,0)
        with self.assertRaises(ValueError):
            self.model.evaluate(0,0,0,arb('0.000002'))
        with self.assertRaises(ValueError):
            self.model.evaluate(0,arb('nan'),0,0)

    def test_tangent_satisfies_both_implicit_equations_exactly(self):
        # Rational arithmetic gives an algebraic check independent of balls.
        d=list(map(Fraction,[0,0,2,3,-5,7,11]))
        tangent=fold_tangent(d)
        A=control_matrix(d)
        self.assertEqual(sum(A[0][j]*tangent[j] for j in range(2)),0)
        self.assertEqual(sum(A[1][j]*tangent[j] for j in range(2)),-d[2])

    def test_boundary_fold_residuals_from_direct_integrals(self):
        report=json.loads((HERE/'results/region_certificate.json').read_text())
        for fold in report['right_boundary_folds']:
            t,mu=[restore(v) for v in fold['center']]
            lam=restore(fold['lambda_offset'])
            d=[derivative(self.model.x[0]+t,
                          {1:self.model.x[1]+lam,2:self.model.x[2]+mu},n,
                          N=20,pieces=16,abs_tol='1e-96',rel_tol='1e-96')
               for n in (0,1)]
            Y=[[restore(v) for v in row] for row in fold['preconditioner']]
            radii=[restore(v) for v in fold['radii']]
            correction=matvec(Y,d)
            eta=norm_vec([correction[i]/radii[i] for i in range(2)])
            self.assertTrue(eta+restore(fold['q'])<1)


if __name__=='__main__':
    unittest.main(verbosity=2)
