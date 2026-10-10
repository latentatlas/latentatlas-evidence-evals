#!/usr/bin/env python3
"""Outward decimal summaries; exact dyadic certificate data stays primary."""
import json,sys
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
sys.dont_write_bytecode=True
from check_family import endpoints,sha
HERE=Path(__file__).resolve().parent


def bounds(v,places):
    a,b=endpoints(v)
    with localcontext() as ctx:
        ctx.prec=160;quantum=Decimal(1).scaleb(-places)
        return [str((Decimal(q.numerator)/Decimal(q.denominator)).quantize(quantum,rounding=r))
                for q,r in ((a,ROUND_FLOOR),(b,ROUND_CEILING))]


def main():
    path=HERE/'results/key_results.json'
    if path.exists():raise FileExistsError(path)
    pp=HERE/'results/point_certificates.json';fp=HERE/'results/fold_samples.json'
    p=json.loads(pp.read_text());f=json.loads(fp.read_text());rows=[]
    for c in f['comparisons']:
        if c['j']!=8:continue
        cp=next(r for r in p['comparisons'] if r['nu']==c['nu'])
        rows.append({'nu':bounds(c['nu'],0)[0],
            'finite_W_change_percent_interval':bounds(c['W_percent_plus_half_vs_minus_half'],8),
            'leading_C_change_percent_interval':bounds(cp['C_percent_plus_half_vs_minus_half'],10),
            'mu_shift_minus_half_interval':bounds(cp['mu_displacement_minus_half'],10),
            'mu_shift_plus_half_interval':bounds(cp['mu_displacement_plus_half'],10)})
    report={'status':'outward_decimal_summary','finite_ell':'0.000001','comparison':'epsilon -1/2 to +1/2',
            'rows':rows,'input_sha256':{'point_certificates.json':sha(pp),'fold_samples.json':sha(fp)},
            'source_sha256':sha(__file__),'rounding':'Outward decimal endpoints, computed from exact serialized dyadic balls.'}
    path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows,indent=2))


if __name__=='__main__':main()
