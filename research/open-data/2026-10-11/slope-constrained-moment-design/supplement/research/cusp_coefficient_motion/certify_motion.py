#!/usr/bin/env python3
"""Uniform positive C4 derivative along the exact short cusp arc."""
import sys
sys.dont_write_bytecode=True
import argparse,json
from flint import ctx
from motion import *
def produce_certificate():
    assert __debug__;ctx.dps=120
    paths={'R27':RESEARCH/'cusp_uniform_remainder/results/certificate.json',
      'R12':RESEARCH/'kernel_norm_threshold/results/threshold_certificate.json',
      'moment9':HERE/'results/sign_moment9.json','algebra':HERE/'results/algebra.json'}
    parent=unbox(read(paths['R27']));mom=unbox(read(paths['moment9']));algebra=read(paths['algebra'])
    expected=algebra['tail_envelopes'];constants=tail_constants()
    for k,values in constants['envelopes'].items():assert list(map(str,values))==list(map(str,expected[k]))
    data=produce(parent,mom);C=data['derivatives']['C4']
    assert rational('2.82e-40')<C and C<rational('4.35e-40')
    return pack({'status':'R28_uniform_positive_fourth_coefficient_derivative','dps':120,
      'driver_interval':['-1/65536','0'],'published_derivative_bounds':['2.82e-40','4.35e-40'],
      'published_anchored_coefficient_bounds':['2.49202340e-39','2.49203006e-39'],
      'source_sha256':{name:sha(HERE/name) for name in ['motion.py','certify_motion.py']},
      'input_sha256':{k:sha(p) for k,p in paths.items()},**data,
      'scope':'Strictly increasing exact C4 on [-2^-16,0], using moving cusp, moving dual, all root velocities and whole derivative tails. Derivative with respect to the original driver nu; no full-arc monotonicity or monotonicity of the finite-M optimum remainder is asserted.'})
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    data=produce_certificate();args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(data['status']);print(data['derivatives']['C4']['enclosure'])
if __name__=='__main__':main()
