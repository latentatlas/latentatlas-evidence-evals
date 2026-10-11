"""Algebraic and independent-integral regression checks for R05."""
import json
import sys
import time
import unittest
from fractions import Fraction as Q
from flint import arb,ctx
from transport_model import (HERE,ExtendedCell,numerator4,restore,verify_inputs,sha)
from fold_jets import transport_jet
from width_shape import numerator as numerator3
from check_width import D, TERMS, fifth_from_ode
from certify_connection import cusp_tangent
from validated_flow import derivative
from endpoint_folds import EndpointTaylor


class WidthChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctx.dps=110;verify_inputs()
        old=json.loads((HERE.parent/'cusp_connection/results/connection_certificate.json').read_text())
        geo=json.loads((HERE.parent/'cusp_geometry/results/geometry_certificate.json').read_text())
        cls.models=[ExtendedCell(old['cells'][i],geo['cells'][i],i) for i in (0,28,57)]

    def test_cusp_transport_exact_cancellations(self):
        for values in ([3,-5,7,-11,13,-17,19,-23,29],
                       [5,-7,11,13,-17,19,-23,29,31],
                       [2,-3,-5,7,-11,13,-17,19,-23]):
            ds=list(map(Q,[0,0,0]+list(values)+list(range(37,52))))
            v=cusp_tangent(ds)
            b,l,m=transport_jet(ds,v[1],K=5)
            self.assertEqual(b[0],v[2])
            self.assertEqual(b[1],0);self.assertEqual(b[2],0)
            kp=numerator3(ds[3:11])/(64*ds[3]**2*ds[4]**3)
            self.assertEqual(6*b[3],-32*kp)
            self.assertEqual(24*b[4],-2*numerator4(ds[3:12])/(ds[3]**3*ds[4]**4))
            self.assertEqual(l[2],2);self.assertEqual(m[4],-4)
            expanded=Q(0)
            for exps,coef in TERMS:
                p=Q(coef)
                for value,e in zip(ds[3:12],exps):p*=value**e
                expanded+=p
            self.assertEqual(expanded,numerator4(ds[3:12]))
            # Independent differential recurrence versus implicit-series algebra.
            bound=fifth_from_ode([D(v) for v in ds[:27]],D(v[1]))
            self.assertGreaterEqual(bound,abs(120*b[5]))
            self.assertLess(bound-abs(120*b[5]),Q(1,10**35))

    def test_extended_correlated_enclosures_against_direct_integrals(self):
        comparisons=0
        for cell in self.models:
            S=arb(3)/4000
            extra=[2*S,arb('2.22')*S*S,arb('2.10')*S*S*S]
            boxes,_=cell.enclose(extra,upto=26)
            for sign in (-1,1):
                z=sign*cell.h
                w=[sign*(cell.tight[0]+extra[0]/2),
                   -sign*(cell.tight[1]+extra[1]/2),sign*(cell.tight[2]+extra[2]/2)]
                x=[cell.x[j]+cell.v[j]*z+w[j] for j in range(3)]
                for n in (3,4,10,15,20,26):
                    direct=derivative(x[0],{1:x[1],2:x[2],3:cell.nu+z},n,N=20,pieces=16)
                    self.assertTrue(boxes[n].contains(direct),(cell.index,sign,n))
                    comparisons+=1
        self.assertEqual(comparisons,36)

    def test_outward_rational_arithmetic(self):
        for x in (Q(1,3),Q(-2,7),Q(1234567,19)):
            for y in (Q(2,5),Q(-5,11)):
                for result,value in ((D(x)+D(y),x+y),(D(x)*D(y),x*y),(D(x)/D(y),x/y)):
                    self.assertLessEqual(result.lo,value)
                    self.assertGreaterEqual(result.hi,value)
        with self.assertRaises(ZeroDivisionError):D(1)/D(-1,1)
        with self.assertRaises(ValueError):D(2,1)

    def test_endpoint_taylor_against_direct_integrals(self):
        data=json.loads((HERE/'results/endpoint_folds.json').read_text())
        comparisons=0
        for name in ('quartic','sextic'):
            model=EndpointTaylor(name)
            for index in (0,15,31):
                row=data['samples'][index];ell=restore(row['ell'])
                for branch in ('upper','lower'):
                    s,m=map(restore,row['endpoints'][name][branch]['center'])
                    enclosed=model.derivatives(s,ell,m)
                    if name=='quartic':params={1:model.x[1]+ell,2:model.x[2]+m,3:arb(0)}
                    else:params={1:model.x[1]+ell,2:m,3:model.x[2]}
                    for n in (0,1,2,4,5):
                        direct=derivative(model.x[0]+s,params,n,N=20,pieces=16)
                        self.assertTrue(enclosed[n].contains(direct),(name,index,branch,n))
                        comparisons+=1
        self.assertEqual(comparisons,60)
        row=data['samples'][-1]
        wq=restore(row['endpoints']['quartic']['width'])
        ws=restore(row['endpoints']['sextic']['width'])
        pct=100*(restore(row['ratio'])-1)
        self.assertTrue(arb('1.2946095162e-9')<wq<arb('1.2946095164e-9'))
        self.assertTrue(arb('1.3269052468e-9')<ws<arb('1.3269052470e-9'))
        self.assertTrue(arb('2.49463101')<pct<arb('2.49463103'))

    def test_domain_rejection(self):
        cell=self.models[0]
        for extra in ((-1,0,0),(0,arb('nan'),0),(0,0),(1,0,0)):
            with self.assertRaises(ValueError):cell.enclose(extra)
        for n in (-1,27):
            with self.assertRaises(ValueError):cell.enclose(upto=n)


if __name__=='__main__':
    started=time.monotonic()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WidthChecks))
    report={'status':'passed' if result.wasSuccessful() else 'failed',
            'test_groups':result.testsRun,
            'direct_integral_comparisons':96 if result.wasSuccessful() else None,
            'source_sha256':{n:sha(HERE/n) for n in
                             ('test_width.py','transport_model.py','fold_jets.py','check_width.py','endpoint_folds.py')},
            'certificate_sha256':sha(HERE/'results/width_certificate.json'),
            'endpoint_certificate_sha256':sha(HERE/'results/endpoint_folds.json'),
            'elapsed_seconds':time.monotonic()-started}
    (HERE/'results/test_report.json').write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
