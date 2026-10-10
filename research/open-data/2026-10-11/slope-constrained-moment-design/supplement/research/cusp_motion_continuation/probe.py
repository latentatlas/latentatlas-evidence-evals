#!/usr/bin/env python3
"""Retain successful or failed enclosure attempts; never infer a sign from failure."""
import sys
sys.dont_write_bytecode=True
import argparse,traceback,time
from continuation import *
from differentiate import produce
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--center',required=True);ap.add_argument('--half-width',required=True)
    ap.add_argument('--anchor',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists();ctx.dps=120;t=time.monotonic();out={}
    try:
        if args.anchor and args.anchor.exists():a=unbox(read(args.anchor));assert a['nu']==rational(args.center)
        else:
            a=anchor(rational(args.center))
            if args.anchor:args.anchor.write_text(json.dumps(pack(a),indent=2)+'\n')
        print('anchor done',time.monotonic()-t,flush=True)
        c=cell(a,rational(args.half_width));out['cell']=c;d=produce(a,c);out['motion']=d
        out['status']='positive_derivative_enclosed' if d['derivatives']['C4']>0 else 'derivative_sign_unresolved'
        print(out['status'],d['derivatives']['C4'],flush=True)
        print('C4',c['coefficients']['C4'],'radii',c['dual']['radii'],flush=True)
    except Exception as ex:
        out.update(status='failed',error=repr(ex),traceback=traceback.format_exc());print(out['traceback'],flush=True)
    out.update(center=args.center,half_width=args.half_width,elapsed_seconds=time.monotonic()-t,
      source_sha256={s:sha(HERE/s) for s in ['continuation.py','differentiate.py','probe.py']})
    args.output.write_text(json.dumps(pack(out),indent=2)+'\n')
if __name__=='__main__':main()
