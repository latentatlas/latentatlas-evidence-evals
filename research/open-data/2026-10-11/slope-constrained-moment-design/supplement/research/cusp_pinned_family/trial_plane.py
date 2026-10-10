#!/usr/bin/env python3
import argparse,json,time
from pathlib import Path
from flint import arb,ctx
from pinned_model import HERE,verify_inputs,sha
from plane_model import certify


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--rho-radius',default='0.75');ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=100;start=time.monotonic();inputs=verify_inputs()
    old,geo,width=[json.loads((HERE.parent/p/'results'/n).read_text()) for p,n in (('cusp_connection','connection_certificate.json'),('cusp_geometry','geometry_certificate.json'),('cusp_width','width_certificate.json'))]
    rows=[]
    for i in (0,28,57):
        cache=json.loads((HERE/'cache'/f'cell_{i:02}.json').read_text())
        try:
            row=certify(old['cells'][i],geo['cells'][i],width['cells'][i],cache,arb(0,arb(args.rho_radius)))
            rows.append({'status':'passed','witness':row})
            print('Plane cell',i,'passed; q',row['contraction']['q']['enclosure'],'nu rate',row['transport']['nu']['rate_lower']['enclosure'],'rho rate',row['transport']['rho']['rate_lower']['enclosure'],flush=True)
        except ArithmeticError as e:
            rows.append({'index':i,'status':'bound_not_proved','reason':str(e)});print('Plane cell',i,'bound not proved:',e,flush=True)
    report={'status':'three_cell_diagnostic_only','rho_radius':args.rho_radius,'rows':rows,'input_packages':inputs,
            'source_sha256':{n:sha(HERE/n) for n in ('pinned_model.py','plane_model.py','trial_plane.py')},'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(exist_ok=True,parents=True)
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
