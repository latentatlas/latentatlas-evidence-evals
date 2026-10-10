#!/usr/bin/env python3
"""Six-point discovery; numerical candidates, not a continuum theorem."""
import argparse,json,time
from pathlib import Path
from flint import arb,ctx
from pinned_model import HERE,Kernel,verify_inputs,restore,pack,sha,opening,cusp_tangent


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=100;start=time.monotonic();inputs=verify_inputs();kernel=Kernel()
    old=json.loads((HERE.parent/'cusp_connection/results/connection_certificate.json').read_text())
    rows=[]
    for nu in (arb(-1),-arb(29)/2,arb(-29)):
        index=min(57,int(-2*float(nu)))
        raw=old['cells'][index]
        seed=[restore(a)+restore(v)*(nu-restore(raw['driver_center'])) for a,v in zip(raw['center'],raw['predictor'])]
        base,d,_,_,_=kernel.refine(seed,nu,arb(0))
        for eps in (-arb(1)/2,arb(1)/2):
            x,d,Y,error,steps=kernel.refine(base,nu,eps)
            C,Cnu=opening(d);tangent=cusp_tangent(d)
            row=pack({'nu':nu,'epsilon':eps,'point':x,'original_point':base,
                      'displacement':[a-b for a,b in zip(x,base)],'derivatives':d,
                      'C':C,'C_nu_candidate':Cnu,'cusp_tangent':tangent,'correction':error,'steps':steps})
            rows.append(row)
            print(json.dumps({'nu':float(nu),'epsilon':float(eps),'displacement':[float(a-b) for a,b in zip(x,base)],'C':float(C.mid()),'Cnu':float(Cnu.mid()),'mu':float(x[2]),'mup':float(tangent[2].mid())}),flush=True)
    report={'status':'six_point_numerical_discovery_only','is_continuum_certificate':False,
            'input_packages':inputs,'kernel_certificate_sha256':sha(kernel.pinned_path),
            'source_sha256':{p:sha(HERE/p) for p in ('pinned_model.py','explore_family.py')},
            'rows':rows,'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')


if __name__=='__main__':main()
