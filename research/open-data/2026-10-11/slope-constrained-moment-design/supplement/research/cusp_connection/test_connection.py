"""Direct-integral and exact-algebra checks for the four-variable extension."""
import json
import unittest
from fractions import Fraction as Q
from flint import arb,ctx
from explore import HERE,restore,point_cache,J
from bridge_taylor import TubeTaylor
from certify_connection import cusp_tangent
from validated_flow import matmul,zero_ball


class ConnectionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctx.dps=110
        cls.data=json.loads((HERE/'results/connection_certificate.json').read_text())
        cls.models=[]
        for index in (0,28,57):
            cell=cls.data['cells'][index]
            model=TubeTaylor(list(map(restore,cell['center'])),restore(cell['driver_center']),
                    list(map(restore,cell['predictor'])),restore(cell['driver_half_width']),
                    list(map(restore,cell['radii'])))
            cls.models.append((cell,model))

    def test_four_variable_enclosures_and_preconditioned_jacobian(self):
        count=0
        for cell,m in self.models:
            Y=[[restore(v) for v in row] for row in cell['preconditioner']]
            defect,_=m.preconditioned_defect(Y)
            for sign in (-1,1):
                z=sign*m.h
                w=[sign*m.radii[0]/2,-sign*m.radii[1]/2,sign*m.radii[2]/2]
                offsets=[m.v[j]*z+w[j] for j in range(3)]+[z]
                box,_=m.evaluate_box(offsets)
                x=[m.x[j]+offsets[j] for j in range(3)]
                direct=point_cache(x,m.nu+z,8,N=20,pieces=16,abs_tol='1e-96',rel_tol='1e-96')
                for n in (0,1,2,3,4,6,8):
                    self.assertTrue(box[n].contains(direct[n]),(m.nu,n,sign))
                    count+=1
                yj=matmul(Y,J(direct))
                for i in range(3):
                    for j in range(3):
                        self.assertTrue(defect[i][j].contains(arb(i==j)-yj[i][j]))
        self.assertEqual(count,42)

    def test_correlated_predictor_residual_against_direct_integrals(self):
        for cell,m in self.models:
            bound,_=m.predictor_residual()
            for sign in (-1,1):
                z=sign*m.h
                x=[a+v*z for a,v in zip(m.x,m.v)]
                direct=point_cache(x,m.nu+z,2,N=20,pieces=16,abs_tol='1e-96',rel_tol='1e-96')
                self.assertTrue(all(a.contains(b) for a,b in zip(bound,direct)))

    def test_domain_escape_and_nonfinite_arguments_rejected(self):
        _,m=self.models[0]
        with self.assertRaises(ValueError):
            m.evaluate_box([0,0,0,2*m.allowed[3]])
        with self.assertRaises(ValueError):
            m.evaluate_box([arb('nan'),0,0,0])
        values,_=m.box_derivatives()
        self.assertTrue(all(v.is_finite() for v in values))

    def test_cusp_tangent_exact_rational_identity(self):
        d=list(map(Q,[0,0,0,3,-5,7,-11,13,-17]))
        v=cusp_tangent(d)
        a=[[d[1],-d[2]/4,d[4]/16],
           [d[2],-d[3]/4,d[5]/16],
           [d[3],-d[4]/4,d[6]/16]]
        self.assertEqual(v,[Q(1,60),Q(1,20),Q(11,20)])
        for i in range(3):
            self.assertEqual(sum(a[i][j]*v[j] for j in range(3)),d[i+6]/64)


if __name__=='__main__':
    unittest.main(verbosity=2)
