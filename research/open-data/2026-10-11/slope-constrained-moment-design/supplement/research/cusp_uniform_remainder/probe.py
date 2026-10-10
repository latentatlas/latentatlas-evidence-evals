#!/usr/bin/env python3
"""Development probe: uniform arc enclosure and moving dual; no remainder yet."""
import sys
sys.dont_write_bytecode=True
import argparse,json,traceback
from flint import ctx
from model import *
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--width',default='1/65536');ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=120;out={'width':args.width,'source_sha256':{'probe.py':sha(__file__),'model.py':sha(HERE/'model.py')}}
    try:
        old=read(RESEARCH/'theta_fourth_order/results/certificate.json');old15=read(RESEARCH/'kernel_slope_asymptotics/results/asymptotic_certificate.json')
        out['arc']=cusp_box(rational(args.width));print('cusp box',out['arc']['parameter_box'],flush=True)
        out['dual']=moving_dual(out['arc'],old,old15);print('dual radii',out['dual']['radii'],'q',out['dual']['contraction_rows'],flush=True)
        out['coefficients']=coefficients(out['arc'],out['dual'],old)
        print('C4',out['coefficients']['C4'],'v',out['coefficients']['v'],flush=True)
        assert out['coefficients']['C4']>0 and out['coefficients']['Xi']>0
        out['status']='probe_passed_coefficient_only'
    except Exception:
        out['status']='probe_failed';out['exception']=traceback.format_exc();print(out['exception'],flush=True)
    args.output.write_text(json.dumps(pack(out),indent=2)+'\n')
    if out['status']=='probe_failed':raise SystemExit(1)
if __name__=='__main__':main()
