#!/usr/bin/env python3
"""Exact finite-budget consequences of the uniform remainder and derivative bands."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
M0=F('2e-5');H=F(1,64);KM=F('1.02e-53');KP=F('1.64e-53');KS=KM+KP
LOW=[F('2.7e-11'),F('7.4e-26'),F('1.9e-40')]
HIGH=[F('3.0e-11'),F('8.7e-26'),F('5.3e-40')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pair_bounds(separation,budget):
    d=F(separation);m=F(budget);assert 0<=d<=H and m>=M0
    lo=d*sum(LOW[j]/m**(2*j) for j in range(3))-KS/m**6
    hi=d*sum(HIGH[j]/m**(2*j) for j in range(3))+KS/m**6
    return {'actual_difference':[str(lo),str(hi)],
      'normalized_fourth_difference':[str(LOW[2]*d-KS/m**2),str(HIGH[2]*d+KS/m**2)]}
def produce():
    assert __debug__;p=HERE/'results/rational_check.json';data=json.loads(p.read_text());checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append(name)
    ck('32_rational_cells',len(data['cells'])==32)
    for row in data['cells']:
        ad=row['derivative_AD'];rem=row['remainder'];i=row['index']
        for j,name in enumerate(['delta0','C2','C4']):
            lo,hi=map(F,ad[name+'_prime_interval'])
            ck(f'{name}_derivative_cell_{i}',LOW[j]<lo<hi<HIGH[j])
        ck(f'remainder_cell_{i}',0<F(rem['Kminus_upper'])<KM and 0<F(rem['Kplus_upper'])<KP)
    exact_actual_resolution=KS/(M0**6*LOW[0])
    stronger_actual_resolution=KS/(M0**6*sum(LOW[j]/M0**(2*j) for j in range(3)))
    published_actual_resolution=F('1.54e-14');fourth_resolution=KS/(M0**2*LOW[2])
    ck('rounded_actual_resolution',0<stronger_actual_resolution<exact_actual_resolution<published_actual_resolution)
    ck('exact_fourth_resolution',fourth_resolution==F(7,20000))
    ck('uniform_grid_fourth_order',LOW[2]/2048-KS/M0**2>0)
    ck('uniform_grid_actual_order',LOW[0]/2048-KS/M0**6>0)
    ck('all_budgets_resolution_scaling',LOW[0]*published_actual_resolution*M0**6>KS)
    # Negative controls: these upper error bounds alone cannot resolve
    # arbitrarily small separations. Failing a sufficient test is NOT reversal.
    tiny_actual=F('1e-16');tiny_fourth=F('1e-5')
    ck('tiny_actual_comparison_unresolved',F(pair_bounds(tiny_actual,M0)['actual_difference'][0])<0)
    ck('tiny_fourth_comparison_unresolved',F(pair_bounds(tiny_fourth,M0)['normalized_fourth_difference'][0])<0)
    grid=[-H+F(k,2048) for k in range(33)];ck('exact_33_node_grid',grid[0]==-H and grid[-1]==0)
    cases=[]
    for m in [M0,2*M0,10*M0,100*M0]:
        for label,d in [('full_arc',H),('one_cell',F(1,2048))]:
            b=pair_bounds(d,m);ck('positive_comparison_'+label+'_'+str(m),all(F(v[0])>0 for v in b.values()))
            cases.append({'budget':str(m),'separation':str(d),'label':label,**b})
    lower_C4=F('2.48374879e-39')
    ck('positive_fourth_correction',lower_C4>KM/M0**2)
    return {'status':'R30_exact_finite_value_comparisons_passed','checks':checks,'check_count':len(checks),
      'driver_interval':['-1/64','0'],'minimum_slope_budget':str(M0),'lower_derivatives':list(map(str,LOW)),
      'upper_derivatives':list(map(str,HIGH)),'remainder_constants':[str(KM),str(KP)],
      'actual_resolution_simple_exact_at_M0':str(exact_actual_resolution),
      'actual_resolution_stronger_at_M0':str(stronger_actual_resolution),
      'actual_resolution_published_at_M0':str(published_actual_resolution),
      'fourth_resolution_at_M0':str(fourth_resolution),'ordered_grid':list(map(str,grid)),
      'cases':cases,'relative_fourth_error_at_M0':[str(-KM/(M0**2*lower_C4)),str(KP/(M0**2*lower_C4))],
      'source_sha256':sha(__file__),'rational_check_sha256':sha(p),
      'scope':'Strict pairwise inequalities at the same M, for exact parameter-dependent coefficients. Z_M=M^4(delta-delta0-C2/M^2). Each driver permits a separate perturbation. These value bounds do not prove monotonicity for all distinct drivers, a derivative of the finite-M optimum, or a common profile for the whole arc.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    d=produce();args.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['check_count'])
    for row in d['cases'][:2]:print(row['label'],{k:[float(F(x)) for x in row[k]] for k in ['actual_difference','normalized_fourth_difference']})
if __name__=='__main__':main()
