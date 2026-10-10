#!/usr/bin/env python3
"""Solve the three original integral equations, without the reduced d/b formulas."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
import mpmath as mp

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def number(s):
    p=F(s);return mp.mpf(p.numerator)/p.denominator
def solve(width,dps):
    with mp.workdps(dps):
        a=number(width);beta=number('1/4');f=number('1/8')
        q=lambda x:(x*x-number('1/4'))*(1+beta*x)
        one=lambda x:mp.mpf(1)
        def integral(fun,cm,cp):
            # Independently integrate the function values, not producer polynomials.
            return (mp.quad(fun,[-1,cm-a])
                +mp.quad(lambda x:-fun(x)*(x-cm)/a,[cm-a,cm+a])
                -mp.quad(fun,[cm+a,cp-a])
                +mp.quad(lambda x:fun(x)*(x-cp)/a,[cp-a,cp+a])
                +mp.quad(fun,[cp+a,1]))
        def equations(cm,cp,b):
            return (mp.quad(lambda x:q(x)-b,[cm-a,cm+a])/(2*a),
                    mp.quad(lambda x:q(x)-b,[cp-a,cp+a])/(2*a),
                    integral(one,cm,cp))
        cm,cp,b=mp.findroot(equations,(-mp.mpf('.5'),mp.mpf('.5'),mp.mpf(0)),
                          tol=mp.mpf(10)**(-(dps-15)),maxsteps=30)
        S=integral(q,cm,cp);A=f/S;M=A/a
        residuals=list(equations(cm,cp,b))+[A*integral(q,cm,cp)-f]
        assert max(map(abs,residuals))<mp.mpf(10)**(-(dps-18))
        # A second primitive calculation checks the sign in both support cells.
        support_sign_checks=[]
        for c,sigma in [(cm,-1),(cp,1)]:
            for j in range(1,20):
                x=c-a+2*a*j/20
                Q=mp.quad(lambda t:q(t)-b,[c-a,x])
                support_sign_checks.append(sigma*Q<0)
        assert all(support_sign_checks)
        vals={'left_center':cm,'right_center':cp,'center_shift':(cm+cp)/2,
              'dual_coefficient':b,'unit_target':S,'amplitude':A,'slope_budget':M}
        return {'dps':dps,'values':{k:mp.nstr(v,dps) for k,v in vals.items()},
                'max_integral_residual':mp.nstr(max(map(abs,residuals)),12),
                'sampled_primitive_signs_passed':len(support_sign_checks)}

def run(certificate):
    cert=json.loads(Path(certificate).read_text());rows=[]
    for row in cert['rows']:
        low=solve(row['a'],80);high=solve(row['a'],120)
        checks={}
        with mp.workdps(145):
            for key,val in high['values'].items():
                value=mp.mpf(val);diff=abs(value-mp.mpf(low['values'][key]))
                lo,hi=map(number,row['intervals'][key])
                assert lo<value<hi,(row['a'],key)
                assert diff<mp.mpf('1e-70'),(row['a'],key,diff)
                checks[key]={'inside_rational_interval':True,'precision_difference':mp.nstr(diff,12)}
        rows.append({'a':row['a'],'lower_precision':low,'higher_precision':high,'comparisons':checks})
    return {'status':'independent_integral_system_crosscheck_passed','rows':rows,
            'source_sha256':sha(Path(__file__)),'certificate_sha256':sha(certificate),
            'mpmath_version':mp.__version__,'precisions':[80,120],
            'trust_boundary':'Nonrigorous high-precision quadrature and nonlinear solve, independent of the reduced producer formulas. Sampled primitive signs are diagnostics; the full sign proof is analytic.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,default=HERE/'results/certificate.json');ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    out=run(args.certificate);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'widths':len(out['rows']),'precision_runs':2*len(out['rows'])}))
if __name__=='__main__':main()
