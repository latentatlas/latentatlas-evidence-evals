#!/usr/bin/env python3
"""Uniform fourth-order coefficient and remainder on a validated cusp subarc."""
import sys
sys.dont_write_bytecode=True
import argparse,json,traceback
from flint import ctx
from model import *
from remainder import produce as remainder
def produce():
    assert __debug__;ctx.dps=120
    paths={k:RESEARCH/v for k,v in {
      'R03':'cusp_connection/results/connection_certificate.json','R09_jets':'cusp_shape_design/results/local_jets.json',
      'R15':'kernel_slope_asymptotics/results/asymptotic_certificate.json','R24':'theta_fourth_order/results/certificate.json',
      'R26':'theta_global_remainder/results/certificate.json','R27_algebra':'cusp_uniform_remainder/results/algebra.json'}.items()}
    alg=read(paths['R27_algebra']);old=read(paths['R24']);old15=read(paths['R15'])
    arc=cusp_box(rational(alg['driver_width']));dual=moving_dual(arc,old,old15);co=coefficients(arc,dual,old)
    assert co['C4']>0 and co['Xi']>0
    rem=remainder(arc,dual,co,alg)
    return pack({'status':'R27_uniform_cusp_subarc_coefficient_and_remainder','dps':120,
        'source_sha256':{f:sha(HERE/f) for f in ['model.py','remainder.py','certify_uniform.py']},
        'input_sha256':{k:sha(p) for k,p in paths.items()},'arc':arc,'dual':dual,'coefficients':co,'remainder':rem,
        'scope':'For every exact cusp on nu in [-2^-16,0] and every M>=2e-5, a uniform fourth-order remainder. Parameter-dependent exact coefficients; pointwise design per cusp, not one kernel perturbation for all cusps. No global arc claim, C6, or finite-budget optimizer formula.'})
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    d=produce();args.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'])
    for k in ['delta0','C2','C4','Xi']:print(k,d['coefficients'][k]['enclosure'])
    for k in ['Kminus','Kplus','Kdual6','Kprimal6','upper_scalar_margin']:print(k,d['remainder'][k]['enclosure'])
if __name__=='__main__':main()
