#!/usr/bin/env python3
"""New rigorous H derivative jets at the 58 frozen original centers."""
import argparse,json,time,concurrent.futures
from pathlib import Path
from flint import ctx
from pinned_model import HERE,Kernel,verify_inputs,restore,pack,sha


def compute(args):
    index,raw,outdir=args;ctx.dps=100;start=time.monotonic();kernel=Kernel()
    path=Path(outdir)/f'cell_{index:02}.json'
    if path.exists():raise FileExistsError(path)
    x=list(map(restore,raw['center']));nu=restore(raw['driver_center'])
    ds=kernel.cache(x,nu,68,kind='H')
    data={'index':index,'center':raw['center'],'driver_center':raw['driver_center'],
          'H_derivatives':pack(ds),'quadrature':{'dps':100,'abs_tol':'1e-70','rel_tol':'1e-70','terms':16,'cutoff':2,'panels':8},
          'kernel_certificate_sha256':sha(kernel.pinned_path),
          'source_sha256':{p:sha(HERE/p) for p in ('pinned_model.py','build_moment_cache.py')},
          'elapsed_seconds':time.monotonic()-start}
    with path.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    return index,sha(path),time.monotonic()-start


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--indices',nargs='*',type=int);ap.add_argument('--workers',type=int,default=2);args=ap.parse_args()
    start=time.monotonic();inputs=verify_inputs()
    rawpath=HERE.parent/'cusp_connection/results/connection_certificate.json';old=json.loads(rawpath.read_text())
    outdir=HERE/'cache';outdir.mkdir(exist_ok=True)
    indices=args.indices if args.indices is not None else list(range(58))
    missing=[i for i in indices if not (outdir/f'cell_{i:02}.json').exists()]
    require_range=all(0<=i<58 for i in indices)
    if not require_range:raise ValueError('Invalid index')
    for i in indices:
        p=outdir/f'cell_{i:02}.json'
        if p.exists():
            d=json.loads(p.read_text())
            for name,h in d['source_sha256'].items():
                if sha(HERE/name)!=h:raise ArithmeticError('Existing cache source mismatch')
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i,h,elapsed in pool.map(compute,[(i,old['cells'][i],str(outdir)) for i in missing]):
            print('Rigorous H jet',i,'of 57 done;',round(elapsed,2),'seconds',flush=True)
    if len(indices)==58:
        data={'status':'58_rigorous_H_jets_available','input_packages':inputs,'connection_certificate_sha256':sha(rawpath),
              'files':[{'index':i,'file':f'cell_{i:02}.json','sha256':sha(outdir/f'cell_{i:02}.json')} for i in range(58)],
              'derivatives_per_cell':69,'elapsed_seconds':time.monotonic()-start}
        with (outdir/'index.json').open('x') as f:json.dump(data,f,indent=2);f.write('\n')
