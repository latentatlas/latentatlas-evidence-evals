#!/usr/bin/env python3
"""Fresh integral-based verification of the three fourth-order test cases."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
import mpmath as mp

HERE=Path(__file__).resolve().parent;PREV=HERE.parent/'finite_slope_optimum'
sys.path.insert(0,str(PREV))
from crosscheck_quadrature import solve as previous_integral_solve
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def num(v):
    q=F(v);return mp.mpf(q.numerator)/q.denominator
def solve(case,width,dps,coeff):
    with mp.workdps(dps):
        a=num(width)
        if case=='two_switch':
            original=previous_integral_solve(width,dps)
            S=mp.mpf(original['values']['unit_target']);A=mp.mpf(original['values']['amplitude'])
            M=mp.mpf(original['values']['slope_budget'])
            residual=original['max_integral_residual']
        else:
            if case=='negative_C4':
                q=lambda x:x-3*x**3+9*x**5;target=num('5/8')
            else:
                assert case=='C2_only'
                q=lambda x:x+mp.sign(x)*abs(x)**num('5/2');target=num('11/28')
            s=lambda x:max(mp.mpf(-1),min(mp.mpf(1),x/a))
            lower=mp.quad(s,[-1,-a,0,a,1])
            balance=mp.quad(q,[-a,0,a])
            S=mp.quad(lambda x:q(x)*s(x),[-1,-a,0,a,1])
            A=target/S;M=A/a
            residual=mp.nstr(max(abs(lower),abs(balance),abs(A*S-target)),12)
        assert mp.mpf(residual)<mp.mpf(10)**(-(dps-20))
        C2=num(coeff['C2']);leading=num('1/4')+C2/M**2;err2=A-leading
        values={'unit_target':S,'amplitude':A,'slope_budget':M,'leading_approximation':leading,
                'leading_error':err2,'scaled_fourth_residual':M**4*err2}
        if 'C4' in coeff:
            fourth=leading+num(coeff['C4'])/M**4;err4=A-fourth
            values.update(fourth_approximation=fourth,fourth_error=err4,error_ratio=abs(err4/err2))
        return {'dps':dps,'values':{k:mp.nstr(v,dps) for k,v in values.items()},
                'max_moment_balance_residual':residual}
def run(certificate):
    cert=json.loads(Path(certificate).read_text());rows=[]
    for r in cert['rows']:
        coeff=cert['coefficients'][r['case']]
        lo=solve(r['case'],r['a'],90,coeff);hi=solve(r['case'],r['a'],130,coeff);checks={}
        with mp.workdps(155):
            for k,value in hi['values'].items():
                value=mp.mpf(value);a,b=map(num,r['intervals'][k]);difference=abs(value-mp.mpf(lo['values'][k]))
                assert a<value<b,(r['case'],r['a'],k)
                assert difference<mp.mpf('1e-70'),(r['case'],r['a'],k,difference)
                checks[k]={'inside_rational_interval':True,'precision_difference':mp.nstr(difference,12)}
        rows.append({'case':r['case'],'a':r['a'],'low':lo,'high':hi,'checks':checks})
    return {'status':'independent_fourth_order_integral_crosscheck_passed','rows':rows,
        'source_sha256':sha(Path(__file__)),'R21_integral_solver_sha256':sha(PREV/'crosscheck_quadrature.py'),
        'certificate_sha256':sha(certificate),'mpmath':mp.__version__,'precisions':[90,130],
        'trust_boundary':'Nonrigorous numerical corroboration from direct integrals; rational enclosures and analytic proofs remain the primary evidence.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,default=HERE/'results/certificate.json');ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    out=run(args.certificate);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'budgets':len(out['rows']),'precision_runs':2*len(out['rows']),
                      'values_compared':sum(len(r['checks']) for r in out['rows'])}))
if __name__=='__main__':main()
