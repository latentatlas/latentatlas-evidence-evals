#!/usr/bin/env python3
"""Exact rational enclosures at sample budgets, not a uniform remainder bound."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from decimal import Decimal,localcontext
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent;PREV=HERE.parent/'finite_slope_optimum'
sys.path.insert(0,str(PREV))
from exact_interval import QI
from certify_example import produce as previous_produce

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def abs_iv(v):
    if v.lo>=0:return v
    if v.hi<=0:return -v
    return QI(0,max(-v.lo,v.hi))
def outward(v,bits=180):
    scale=2**bits
    lo=v.lo*scale;hi=v.hi*scale
    return QI(F(lo.numerator//lo.denominator,scale),F(-((-hi.numerator)//hi.denominator),scale))
def approx(v):
    x=(v.lo+v.hi)/2
    with localcontext() as ctx:
        ctx.prec=35
        return format(Decimal(x.numerator)/Decimal(x.denominator),'.18g')
def sample(name,width,S,A,M,C2,C4=None):
    leading=F(1,4)+C2/M**2;error2=A-leading
    vals={'unit_target':S,'amplitude':A,'slope_budget':M,'leading_approximation':leading,
          'leading_error':error2,'scaled_fourth_residual':M**4*error2}
    if C4 is not None:
        fourth=leading+C4/M**4;error4=A-fourth
        ratio=abs_iv(error4)/abs_iv(error2)
        assert ratio.hi<1,(name,width)
        vals.update(fourth_approximation=fourth,fourth_error=error4,error_ratio=ratio)
    return {'case':name,'a':str(width),'intervals':{k:outward(v).data() for k,v in vals.items()},
            'approximate_midpoints':{k:approx(v) for k,v in vals.items()}}
def produce():
    oldpath=PREV/'results/certificate.json';old=json.loads(oldpath.read_text())
    fresh=previous_produce();assert fresh==old,'R21 fresh rational replay changed.'
    rows=[]
    for row in fresh['rows']:
        iv={k:QI.from_data(v) for k,v in row['intervals'].items()};a=F(row['a'])
        rows.append(sample('two_switch',a,iv['unit_target'],iv['amplitude'],iv['slope_budget'],F(1,48),F(253,49152)))
    for a in map(F,[r['a'] for r in fresh['rows']]):
        S=QI(F(5,2)-a*a/3+F(3,10)*a**4-F(3,7)*a**6);A=F(5,8)/S;M=A/a
        rows.append(sample('negative_C4',a,S,A,M,F(1,480),F(-1,15360)))
    for root_width in [F(1,5),F(1,10),F(1,20),F(1,40)]:
        a=root_width**2
        S=QI(F(11,7)-a*a/3-F(8,63)*root_width**7);A=F(11,28)/S;M=A/a
        rows.append(sample('C2_only',a,S,A,M,F(7,2112)))
    return {'status':'fourth_order_rational_sample_enclosures_passed','rows':rows,
        'coefficients':{'two_switch':{'delta0':'1/4','C2':'1/48','C4':'253/49152','R':'134/567','P':'3721/18144','Xi':'1/32'},
                        'negative_C4':{'delta0':'1/4','C2':'1/480','C4':'-1/15360','R':'3/10','P':'0','Xi':'3/10'},
                        'C2_only':{'delta0':'1/4','C2':'7/2112','fractional_exponent':'7/2','fractional_coefficient':'1/6336'}},
        'source_sha256':sha(Path(__file__)),'R21_certificate_sha256':sha(oldpath),
        'R21_producer_sha256':sha(PREV/'certify_example.py'),'rational_interval_source_sha256':sha(PREV/'exact_interval.py'),
        'output_rounding':'Outward dyadic rounding, denominator 2^180, from exact rational arithmetic.',
        'R21_fresh_replay_identical':True,
        'trust_boundary':'Rigorous enclosures at stated parametric budgets M(a). Analytic theorem supplies optimality and limiting coefficients. Samples do not give a uniform error bound or a theta result.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    data=produce();args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':data['status'],'sample_budgets':len(data['rows']),'interval_records':sum(len(r['intervals']) for r in data['rows'])}))
if __name__=='__main__':main()
