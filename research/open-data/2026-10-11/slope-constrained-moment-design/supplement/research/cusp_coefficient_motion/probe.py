#!/usr/bin/env python3
"""Recorded first attempt; failure is retained, never a sign verdict."""
import sys
sys.dont_write_bytecode=True
import argparse,json,traceback
from flint import ctx
from motion import *
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=120
    try:
        cert=unbox(read(RESEARCH/'cusp_uniform_remainder/results/certificate.json'))
        mom=unbox(read(HERE/'results/sign_moment9.json'));data=produce(cert,mom)
        data={'status':'positive_derivative_enclosed' if data['derivatives']['C4']>0 else 'derivative_sign_unresolved',**data}
    except Exception as ex:data={'status':'failed','error':repr(ex),'traceback':traceback.format_exc()}
    data=pack(data);data['motion_source_sha256']=sha(HERE/'motion.py');args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(data['status'])
    if 'error' in data:print(data['traceback'])
    else:
        for k,v in data['derivatives'].items():
            if isinstance(v,dict):print(k,v['enclosure'])
        print('bprime',[x['enclosure'] for x in data['b_prime']])
if __name__=='__main__':main()
