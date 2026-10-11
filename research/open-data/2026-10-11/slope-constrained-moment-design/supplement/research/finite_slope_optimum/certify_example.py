#!/usr/bin/env python3
"""Rational bisection and interval enclosures for the R21 polynomial example."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from decimal import Decimal,localcontext
from fractions import Fraction as F
from pathlib import Path
from exact_interval import QI

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def approximate(i):
    x=(i.lo+i.hi)/2
    with localcontext() as ctx:
        ctx.prec=35
        return format(Decimal(x.numerator)/Decimal(x.denominator),'.18g')

def produce():
    inp=json.loads((HERE/'inputs.json').read_text());beta=F(inp['beta']);f=F(inp['target'])
    rows=[]
    for a in map(F,inp['half_widths']):
        assert 0<a<=F(1,5)
        def equation(d):return 2*d+3*beta*d*d+beta*a*a
        lo,hi=map(F,inp['center_shift_initial_bracket'])
        assert equation(lo)<0<equation(hi) and 2+6*beta*lo>0
        for _ in range(inp['bisection_steps']):
            mid=(lo+hi)/2;val=equation(mid)
            if val<0:lo=mid
            elif val>0:hi=mid
            else:lo=hi=mid;break
        assert equation(lo)<=0<=equation(hi)
        d=QI(lo,hi)
        b=d**2+beta*d**3+beta*d/2+a*a/3+beta*d*a*a
        target=F(1,2)-2*d**2-2*beta*d**3-F(2,3)*a*a-2*beta*d*a*a
        assert target.lo>F(47,100)
        A=f/target;M=A/a;gain=2*d**2*(1+2*beta*d)
        assert gain.lo>0 and A.hi<1
        values={'center_shift':d,'left_center':d-F(1,2),'right_center':d+F(1,2),
                'dual_coefficient':b,'unit_target':target,'amplitude':A,'slope_budget':M,
                'unit_objective_gain':gain,'center_shift_over_a2':d/(a*a),
                'dual_over_a2':b/(a*a),'scaled_amplitude_excess':M**2*(A-F(1,4))}
        rows.append({'a':str(a),'root_endpoint_sign_values':[str(equation(lo)),str(equation(hi))],
                     'intervals':{k:v.data() for k,v in values.items()},
                     'approximate_midpoints':{k:approximate(v) for k,v in values.items()}})
    return {'status':'exact_rational_example_enclosures_passed','rows':rows,
            'inputs_sha256':sha(HERE/'inputs.json'),'producer_sha256':sha(Path(__file__)),
            'interval_substrate_sha256':sha(HERE/'exact_interval.py'),
            'unrestricted_amplitude':'1/4','leading_cost_coefficient':'1/48',
            'trust_boundary':'Exact rational brackets for a unique algebraic root and outward interval arithmetic. Global optimality is proved in PROOF.md and EXAMPLE.md, not inferred from these numbers.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert __debug__,'Assertions must be enabled.'
    if args.output.exists():raise FileExistsError(args.output)
    out=produce();args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'rows':len(out['rows'])}))
if __name__=='__main__':main()
