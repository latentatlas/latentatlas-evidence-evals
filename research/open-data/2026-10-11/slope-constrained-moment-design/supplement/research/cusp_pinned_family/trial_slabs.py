#!/usr/bin/env python3
"""Try amplitude slabs while retaining exact source/version links."""
import argparse,json,time
from pathlib import Path
from flint import arb,ctx
from pinned_model import HERE,verify_inputs,sha,pack
from plane_model import certify


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--slabs',type=int,default=2);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=100;start=time.monotonic();inputs=verify_inputs()
    data=[json.loads((HERE.parent/p/'results'/n).read_text()) for p,n in (('cusp_connection','connection_certificate.json'),('cusp_geometry','geometry_certificate.json'),('cusp_width','width_certificate.json'))]
    rows=[]
    for j in range(args.slabs):
        left=-arb(1)/2+arb(5)*j/(4*args.slabs);right=-arb(1)/2+arb(5)*(j+1)/(4*args.slabs)
        rho=left.union(right)
        for i in (0,28,57):
            cache=json.loads((HERE/'cache'/f'cell_{i:02}.json').read_text())
            try:
                row=certify(*(d['cells'][i] for d in data),cache,rho)
                rows.append({'slab':j,'status':'passed','witness':row})
                print('slab',j,'cell',i,'passed; nu rate',row['transport']['nu']['rate_lower']['enclosure'],'rho rate',row['transport']['rho']['rate_lower']['enclosure'],flush=True)
            except ArithmeticError as e:
                rows.append({'slab':j,'index':i,'status':'bound_not_proved','rho':pack(rho),'reason':str(e)});print('slab',j,'cell',i,'bound not proved:',e,flush=True)
    report={'status':'sampled_slab_diagnostic_only','slabs':args.slabs,'rows':rows,'input_packages':inputs,
            'source_sha256':{n:sha(HERE/n) for n in ('pinned_model.py','plane_model.py','trial_slabs.py')},'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(exist_ok=True,parents=True)
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
