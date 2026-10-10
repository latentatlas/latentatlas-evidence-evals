#!/usr/bin/env python3
"""Outward decimal summaries using integer arithmetic only."""
import json,sys
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
from check_design import sha,read,D
HERE=Path(__file__).resolve().parent


def fixed(n,p):
    sign='-' if n<0 else '';n=abs(n)
    return sign+str(n//10**p)+('.'+str(n%10**p).zfill(p) if p else '')
def bounds(v,p):
    lo,hi=(v.lo,v.hi) if isinstance(v,D) else tuple(map(Q,v))
    s=10**p
    return [fixed((lo.numerator*s)//lo.denominator,p),fixed(-((-hi.numerator*s)//hi.denominator),p)]


def main():
    output=HERE/'results/key_results.json'
    if output.exists():raise FileExistsError(output)
    names=['design_certificate.json','design_check.json','boundary_certificate.json','sample_check.json','fold_samples.json']
    inp={n:json.loads((HERE/'results'/n).read_text()) for n in names}
    design,check,boundary,samples,folds=[inp[n] for n in names]
    rows={r['direction']:r['change_percent'] for r in samples['last_offset_comparisons']}
    widths=[]
    for i in (0,4,8,9,10):
        sample=next(s for s in folds['samples'] if s['model']==i and s['j']==8)
        widths.append({'model':i,'direction':folds['models'][i]['direction'],
            'epsilon':bounds(read(folds['models'][i]['epsilon']),7),
            'W_times_1e9':bounds(10**9*read(sample['width']),10)})
    out={'status':'exact_integer_outward_decimal_summary','comparison':'epsilon -1/128 to +1/128 at exact Q, nu=0, ell=1e-6',
        'a':bounds(check['a'],12),'b':bounds(check['b'],12),'S':bounds(check['finite_class_optimum'],12),
        'gain_over_reference':bounds(read(design['linear_gain_over_R07']),6),
        'selected_finite_W_change_percent':bounds(rows['selected'],8),
        'reference_finite_W_change_percent':bounds(rows['reference'],8),
        'selected_leading_C_change_percent':bounds(read(design['C_percent_change']),10),
        'reference_leading_C_change_percent':bounds(read(design['baseline_same_amplitude_C_percent_change']),12),
        'mu_unfolding_boundary':bounds(boundary['mu_unfolding_boundary'],12),
        'quartic_boundary':bounds(check['quartic_amplitude'],12),
        'quartic_fourth_derivative_times_1e12':bounds(10**12*D(*map(Q,check['quartic_fourth_derivative'])),12),
        'quartic_control_det_times_1e38':bounds(10**38*D(*map(Q,check['quartic_control_determinant'])),12),
        'safe_relative_kernel_percent':['0.78125','0.78125'],
        'kernel_multiplier_common_lower':boundary['kernel_multiplier_common_lower'],
        'widths':widths,'input_sha256':{n:sha(HERE/'results'/n) for n in names},
        'source_sha256':sha(__file__),'rounding':'Integer floor/ceiling of exact rational bounds; no binary/decimal floating-point rounding assumption.'}
    with output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
