#!/usr/bin/env python3
"""Readably scaled outward decimal bounds from the rational checks."""
import json
from pathlib import Path
from check_window import Q,D,sha,HERE


def fixed(n,p):
    sign='-' if n<0 else '';n=abs(n)
    return sign+str(n//10**p)+('.'+str(n%10**p).zfill(p) if p else '')
def bounds(v,places=10,scale=1):
    v=list(map(Q,v));s=10**places
    lo,hi=v[0]*scale,v[1]*scale
    return [fixed((lo.numerator*s)//lo.denominator,places),fixed(-((-hi.numerator*s)//hi.denominator),places)]


def main():
    output=HERE/'results/key_results.json'
    if output.exists():raise FileExistsError(output)
    names=['window_check.json','sample_check.json','chart_check.json']
    inputs={n:json.loads((HERE/'results'/n).read_text()) for n in names}
    samples=inputs['sample_check.json'];special=[]
    for row in samples['records']:
        if row['name'].startswith('cusp'):
            values=row['root_enclosures'];special.append({'name':row['name'],
                's':bounds(values[0],14),'mu_shift_times_1e12':bounds(values[1],10,10**12),
                'nu_times_1e12':bounds(values[2],10,10**12)})
        elif row['name']=='two_double_roots':
            values=row['root_enclosures'];special.append({'name':row['name'],'s_left':bounds(values[0],14),'s_right':bounds(values[1],14),
                'mu_shift_times_1e15':bounds(values[2],10,10**15),'nu_times_1e15':bounds(values[3],10,10**15)})
    L=Q(2)**-24
    out={'status':'exact_integer_outward_summary','global_domain':{
        'T':str(Q(2)**-7),'lambda_radius':str(Q(2)**-17),'mu_and_nu_radius':str(Q(2)**-34)},
        'lambda_section':str(L),'open_region_radii':[str(L/128),str(L*L/256),str(L*L/256)],
        'g4_interval':bounds(inputs['window_check.json']['g4_bounds'],6),
        'cusp_g3_slope_interval':bounds(inputs['window_check.json']['cusp_g3_slope'],6),
        'special_points':special,'chart_counts':inputs['chart_check.json']['counts'],
        'sample_contractions':len(samples['records']),
        'input_sha256':{n:sha(HERE/'results'/n) for n in names},'source_sha256':sha(__file__),
        'rounding':'Integer floor/ceiling applied to exact rational endpoints; decimal figures do not define exact points.'}
    with output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
