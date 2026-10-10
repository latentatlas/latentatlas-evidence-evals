#!/usr/bin/env python3
"""Bounded diagnostic before a full 58-cell theorem. Never overwrites output."""
import argparse
import json
import time
from pathlib import Path
from flint import arb,ctx
from robust_model import load_inputs,cell_bounds,BoundFailure

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--epsilon',default='1e-19')
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic()
    packages,paths,data=load_inputs();rows=[]
    for i in (0,28,57):
        tick=time.monotonic()
        try:
            cell=cell_bounds(*(d['cells'][i] for d in data),i,arb(args.epsilon))
            row={'index':i,'status':'passed','Cprime':cell['Cprime']['enclosure'],
                 'q':cell['contraction']['q']['enclosure'],
                 'displacement':[v['enclosure'] for v in cell['contraction']['displacement']],
                 'third':cell['third']['enclosure'],'rate_lower':cell['rate_lower']['enclosure'],
                 'rate_upper':cell['rate_upper']['enclosure']}
        except BoundFailure as e:
            row={'index':i,'status':'bound_not_proved','reason':str(e)}
        row['elapsed_seconds']=time.monotonic()-tick;rows.append(row)
        print(json.dumps(row),flush=True)
    result={'status':'diagnostic_only','epsilon_input':args.epsilon,
            'sample_cells':rows,'elapsed_seconds':time.monotonic()-start,
            'meaning':'A failed sufficient bound is not a counterexample to robustness.'}
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
