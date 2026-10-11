#!/usr/bin/env python3
"""One new rigorous sign-template moment at the original exact cusp."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/'kernel_norm_threshold'))
from certify_threshold import finite_segment,restore,pack,upper,zero_ball
from validated_flow import series_tail,domain_tail
from flint import arb,ctx
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def produce():
    assert __debug__;ctx.dps=120
    paths={'R12':RESEARCH/'kernel_norm_threshold/results/threshold_certificate.json',
      'Q':RESEARCH/'cusp_verified/results/quartic_cusp_certificate.json',
      'R09':RESEARCH/'cusp_shape_design/results/local_jets.json'}
    old,q,jets=[json.loads(paths[k].read_text()) for k in ['R12','Q','R09']]
    center=list(map(restore,q['center_exact_dyadic']));radius=restore(q['root_radius'])
    B=list(map(restore,jets['absolute_F_bounds']));knots=list(map(restore,old['breakpoints']))
    assert len(knots)==28 and old['initial_sign']==1 and all(x.is_exact() for x in center+knots)
    ends=[arb(0)]+knots+[arb(1)];records=[];total=arb(0)
    for i,(a,b) in enumerate(zip(ends,ends[1:])):
        value=finite_segment(center,9,a,b,N=8);total+=(-1)**i*value
        records.append({'left':a,'right':b,'sign':(-1)**i,'finite_integral':value})
    params={1:center[1],2:center[2],3:arb(0)}
    truncation=upper(series_tail(params,9,arb(1),8)+domain_tail(params,9,arb(1)))
    displacement=upper(radius*(B[10]+B[11]/4+B[13]/16))
    value=total+zero_ball(upper(truncation+displacement))
    return pack({'status':'R28_ninth_sign_template_moment_enclosed','dps':120,'order':9,'theta_terms':8,
      'cutoff':1,'segments':records,'finite_sum':total,'truncation_bound':truncation,
      'exact_Q_displacement_bound':displacement,'moment_at_exact_Q':value,
      'input_sha256':{k:sha(p) for k,p in paths.items()},
      'source_sha256':{'sign_moment.py':sha(__file__),
        '../kernel_norm_threshold/certify_threshold.py':sha(RESEARCH/'kernel_norm_threshold/certify_threshold.py'),
        '../cusp_verified/validated_flow.py':sha(RESEARCH/'cusp_verified/validated_flow.py')},
      'scope':'Fixed R12 dyadic sign template, positive after the last breakpoint; full half-line moment at exact Q. This is not yet the moving optimal sign moment.'})
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    d=produce();args.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['moment_at_exact_Q']['enclosure'])
if __name__=='__main__':main()
