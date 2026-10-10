"""Direct-integral, exact-algebra and domain regression tests for R04."""
import json
import unittest
from fractions import Fraction as Q
from flint import arb,ctx
from geometry_model import (HERE,CONNECTION,CorrelatedCell,LocalCusp,restore,
                            point_cache,zero_ball)
from width_shape import numerator,partials,Polynomial
from certify_connection import cusp_tangent


class GeometryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctx.dps=110
        old=json.loads((CONNECTION/'results/connection_certificate.json').read_text())
        new=json.loads((HERE/'results/geometry_certificate.json').read_text())
        cls.models=[]
        for i in (0,28,57):
            cell=CorrelatedCell(old['cells'][i],i)
            record=new['cells'][i]
            local=LocalCusp(list(map(restore,record['cusp_derivatives'])),
                list(map(restore,record['neighborhood_derivatives'])),
                list(map(restore,record['local_limits'])))
            cls.models.append((cell,local))

    def test_correlated_enclosures_with_direct_finer_integrals(self):
        comparisons=0
        for cell,_ in self.models:
            limits=[arb(2)**-8,arb(2)**-12,arb(2)**-19]
            bounds,_=cell.enclose(limits,upto=14)
            for sign in (-1,1):
                z=sign*cell.h
                w=[sign*(cell.tight[0]+limits[0]/2),
                   -sign*(cell.tight[1]+limits[1]/2),sign*(cell.tight[2]+limits[2]/2)]
                x=[cell.x[j]+cell.v[j]*z+w[j] for j in range(3)]
                direct=point_cache(x,cell.nu+z,14,N=20,pieces=16)
                for n in (0,1,2,3,4,6,9,10,14):
                    self.assertTrue(bounds[n].contains(direct[n]),(cell.index,sign,n))
                    comparisons+=1
        self.assertEqual(comparisons,54)

    def test_cusp_centered_values_against_direct_integrals(self):
        comparisons=0
        for cell,local in self.models:
            for sign in (-1,1):
                s=sign*arb(7)/10000;l=-sign*arb(3)/4000000;m=sign*arb(1)/1000000000
                x=[a+b for a,b in zip(cell.x,(s,l,m))]
                direct=point_cache(x,cell.nu,2,N=20,pieces=16)
                for n in (0,1,2):
                    self.assertTrue(local.evaluate(n,s,l,m).contains(direct[n]),(cell.index,sign,n))
                    comparisons+=1
        self.assertEqual(comparisons,18)

    def test_opening_derivative_exact_identity_and_partial_derivatives(self):
        from check_geometry import TERMS
        for vals in ([3,-5,7,-11,13,-17,19,-23],[5,-7,11,13,-17,19,-23,29]):
            d=list(map(Q,[0,0,0]+list(vals)))
            v=cusp_tangent(d)
            g3=d[4]*v[0]-d[5]*v[1]/4+d[7]*v[2]/16-d[9]/64
            g4=d[5]*v[0]-d[6]*v[1]/4+d[8]*v[2]/16-d[10]/64
            expected=(d[3]*g4-g3*d[4])/(d[4]*d[4])
            self.assertEqual(numerator(d[3:11])/(64*d[3]*d[3]*d[4]*d[4]*d[4]),expected)
            expanded=Q(0)
            for exps,coef in TERMS:
                term=Q(coef)
                for value,e in zip(d[3:11],exps): term*=value**e
                expanded+=term
            self.assertEqual(numerator(d[3:11]),expanded)
            grad=partials(list(map(arb,vals)))
            for j in range(8):
                poly=numerator([Polynomial([arb(v),arb(i==j)]) for i,v in enumerate(vals)])
                self.assertTrue(grad[j].contains(poly.c[1]))

    def test_domain_rejection_and_zero_crossing_power(self):
        cell,local=self.models[0]
        with self.assertRaises(ValueError): cell.enclose([1,0,0])
        with self.assertRaises(ValueError): local.evaluate(0,arb('nan'),0,0)
        with self.assertRaises(ValueError): local.evaluate(0,1,0,0)
        values=local.derivatives(zero_ball(arb('0.003')),zero_ball(arb('1e-6')),zero_ball(arb('2e-9')))
        self.assertTrue(all(v.is_finite() for v in values))

if __name__=='__main__': unittest.main(verbosity=2)
