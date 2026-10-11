#!/usr/bin/env python3
"""New positive majorants including nu variation; frozen exact jets reused."""
import argparse,json,time
from pathlib import Path
from model import *


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic();old=verify()
    jp=BASE/'results/local_jets.json';dp=BASE/'results/design_certificate.json'
    jets=json.loads(jp.read_text());design=json.loads(dp.read_text())
    eps=restore(design['quartic_boundary']['amplitude'])
    ds=[restore(f)+eps*restore(h) for f,h in zip(jets['F_at_exact_Q'],jets['H_at_exact_Q'])]
    ds[:4]=[arb(0)]*4;need(ds[4]<0,'Fourth derivative not negative')
    scale=24/ds[4];c=[scale*v for v in ds];c[:4]=[arb(0)]*4;c[4]=arb(24)
    x=list(map(restore,jets['center']));r=restore(jets['root_radius'])
    domain=[arb('0.02'),arb('0.001'),arb('0.0001'),arb('0.0001')]
    params={1:x[1]+zero_ball(domain[1]+r),2:x[2]+zero_ball(domain[2]+r),3:zero_ball(domain[3])}
    B0=absolute_derivative_bounds(params,60)
    B=[upper(abs(scale)*(1+abs(eps))*v) for v in B0]
    result=pack({'status':'normalized_quartic_jet_and_three_control_majorants_recorded',
        'frozen_R09':old,'input_sha256':{'local_jets.json':sha(jp),'design_certificate.json':sha(dp)},
        'source_sha256':{n:sha(HERE/n) for n in ('build_model.py','model.py')},
        'center':x,'Q_radius':r,'epsilon4':eps,'normalizing_multiplier':scale,
        'normalized_exact_Q_derivatives':c,'unnormalized_absolute_bounds':B0,'normalized_absolute_bounds':B,
        'domain':domain,'control_jet_matrix':controls(c),'control_preconditioner':inverse(c),
        'definition':'g=(24/G4(Q))*G_epsilon4. The multiplier is negative, nonzero and independent of all controls; g_0...g_3=0 and g_4=24 exactly at Q.',
        'trust_boundary':'R09 exact-Q F/H integral enclosures and exact pinning/epsilon4 identities. New absolute majorants include all three control variations; no reuse of the old nu=0 majorants for nu!=0.',
        'elapsed_seconds':time.monotonic()-start})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('Normalized fourth derivative',c[4],'and full three-control majorants recorded',flush=True)


if __name__=='__main__':main()
