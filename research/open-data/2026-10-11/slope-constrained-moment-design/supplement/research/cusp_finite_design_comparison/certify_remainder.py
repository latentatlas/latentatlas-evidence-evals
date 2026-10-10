#!/usr/bin/env python3
"""R30: fresh effective remainders on each frozen R29 cusp/dual cell."""
import sys
sys.dont_write_bytecode=True
import argparse,gzip,hashlib,json
from pathlib import Path
from flint import ctx
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/'cusp_uniform_remainder'))
from remainder import produce
from model import pack,restore
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def unbox(x):
    if isinstance(x,dict):
        if 'mid_man_exp' in x:return restore(x)
        return {k:unbox(v) for k,v in x.items()}
    if isinstance(x,list):return [unbox(v) for v in x]
    return x
def certify(output):
    assert __debug__;ctx.dps=120;assert not output.exists();output.mkdir(parents=True)
    parent=RESEARCH/'cusp_motion_continuation/results/cover';index=read(parent/'certificate.json')
    assert index['driver_interval']==['-1/64','0'] and index['cell_count']==32
    alg=read(HERE/'results/algebra.json');assert alg['driver_width']=='1/64'
    records=[]
    for row in index['cells']:
        p=parent/row['file'];assert sha(p)==row['sha256']
        old=unbox(json.loads(gzip.decompress(p.read_bytes())));cell=old['cell']
        rem=produce(cell['arc'],cell['dual'],cell['coefficients'],alg)
        name=row['file'];payload={'index':row['index'],'input_cell_sha256':sha(p),'remainder':rem}
        raw=(json.dumps(pack(payload),sort_keys=True,separators=(',',':'))+'\n').encode()
        (output/name).write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
        records.append({'index':row['index'],'file':name,'sha256':sha(output/name),'input_cell_sha256':sha(p),
          'left':row['left'],'right':row['right'],'Kminus':rem['Kminus'],'Kplus':rem['Kplus'],
          'sign_cover_leaves':len(rem['sign_cover'])})
        print('remainder cell',row['index']+1,'/32','Kminus',float(rem['Kminus']),
          'Kplus',float(rem['Kplus']),flush=True)
    inputs={'R29_cover':parent/'certificate.json','R27_remainder':RESEARCH/'cusp_uniform_remainder/remainder.py',
      'R27_model':RESEARCH/'cusp_uniform_remainder/model.py','R26_tail':RESEARCH/'theta_global_remainder/results/certificate.json',
      'R30_algebra':HERE/'results/algebra.json'}
    cert={'status':'R30_uniform_effective_remainder_cover','dps':120,'driver_interval':['-1/64','0'],
      'cell_count':32,'minimum_slope_budget':'2e-5','input_sha256':{k:sha(p) for k,p in inputs.items()},
      'source_sha256':sha(__file__),'cells':records,
      'trust_boundary':'Fresh full sextic local jets, sign cover, moment repair and scalar inversion. Frozen R29 cusp/dual/coefficient enclosures and R26 weighted infinite-tail bounds are explicit dependencies. Analytic proof is separate.'}
    (output/'certificate.json').write_text(json.dumps(pack(cert),indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();certify(args.output_dir)
if __name__=='__main__':main()
