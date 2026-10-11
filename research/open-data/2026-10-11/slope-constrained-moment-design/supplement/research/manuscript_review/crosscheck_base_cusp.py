#!/usr/bin/env python3
"""Run the separate real-axis implementation on this review's fresh C1 output."""
import sys
sys.dont_write_bytecode=True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    source=HERE.parent/'cusp_verified/check_independent.py'
    spec=importlib.util.spec_from_file_location('separate_real_quadrature',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    cert_path=HERE/'base_cusp_fresh.json';cert=json.loads(cert_path.read_text())
    t,lam,mu=map(module.point,cert['center_exact_dyadic'])
    start=time.monotonic();rows=[]
    for n in range(5):
        value=module.evaluate(t,lam,mu,2,n)
        difference=abs(value-module.point(cert['point_derivatives'][n]))
        assert difference<module.mp.mpf('1e-96')
        rows.append({'order':n,'value':module.mp.nstr(value,102),
                     'absolute_difference':module.mp.nstr(difference,15),'agreement_within_1e_96':True})
        print('Separate cusp derivative',n,'passed',flush=True)
    out={'status':'five_base_cusp_derivatives_independently_corroborated',
         'rows':rows,'fresh_certificate_sha256':sha(cert_path),
         'quadrature_source_sha256':sha(source),'runner_source_sha256':sha(Path(__file__)),
         'method':'mpmath 115 dps, 12 theta terms, 16 Gauss-Legendre subsegments on [0,2]',
         'elapsed_seconds':time.monotonic()-start,'is_rigorous_certificate':False}
    args.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
