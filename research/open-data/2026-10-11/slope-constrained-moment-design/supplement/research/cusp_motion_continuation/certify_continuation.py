#!/usr/bin/env python3
"""A finite, gap-free cover with individually re-integrated local anchors."""
import sys
sys.dont_write_bytecode=True
import argparse,gzip
from continuation import *
from differentiate import produce
def write_gzip(path,data):
    assert not path.exists()
    payload=(json.dumps(pack(data),sort_keys=True,separators=(',',':'))+'\n').encode()
    path.write_bytes(gzip.compress(payload,compresslevel=9,mtime=0))
def read_gzip(path):return json.loads(gzip.decompress(Path(path).read_bytes()))
def certify(output):
    assert __debug__;ctx.dps=120;assert not output.exists();output.mkdir(parents=True)
    h=arb(1)/4096;records=[];left=None;right=arb(0)
    for i in range(32):
        nu=-(2*i+1)*h;a=anchor(nu);c=cell(a,h);m=produce(a,c)
        assert c['arc']['driver_right']==right;right=c['arc']['driver_left']
        lo,hi=m['derivatives']['C4'].lower(),m['derivatives']['C4'].upper()
        assert rational('1.9e-40')<lo and hi<rational('5.3e-40'),(i,lo,hi)
        if left is not None:
            # This numerical intersection is a consistency check. The proof
            # identifies the cusp through R03 containment and the dual through
            # uniqueness of the global minimizer at the shared exact driver.
            assert all(left['dual']['tight_box'][j].overlaps(c['dual']['tight_box'][j]) for j in range(3))
        name=f'cell_{i:03d}.json.gz';write_gzip(output/name,{'index':i,'anchor':a,'cell':c,'motion':m})
        records.append({'index':i,'file':name,'sha256':sha(output/name),
          'left':str(-(i+1))+'/2048','right':str(-i)+'/2048',
          'C4_prime':m['derivatives']['C4'],'C4':c['coefficients']['C4'],
          'dual_contraction_rows':c['dual']['contraction_rows'],'dual_scaled_forcing':c['dual']['scaled_forcing'],
          'cusp_q_plus_eta':a['cusp_validation']['q_plus_eta'],
          'first_three_switch_determinant':c['coefficients']['first_three_switch_determinant'],
          'sign_cover_leaves':len(c['dual']['sign_cover'])})
        print('cell',i+1,'/32',float(nu),'C4prime',float(lo),float(hi),flush=True);left=c
    assert right==-arb(1)/64
    parents={'R03':RESEARCH/'cusp_connection/results/connection_certificate.json',
      'R09':RESEARCH/'cusp_shape_design/results/local_jets.json',
      'R24':RESEARCH/'theta_fourth_order/results/certificate.json',
      'R26_algebra':RESEARCH/'theta_global_remainder/results/algebra.json',
      'R28':RESEARCH/'cusp_coefficient_motion/results/certificate.json'}
    data={'status':'R29_recentered_positive_derivative_cover','dps':120,'driver_interval':['-1/64','0'],
      'half_width':'1/4096','cell_count':32,'published_derivative_bounds':['1.9e-40','5.3e-40'],
      'published_coefficient_bounds':['2.48374879e-39','2.49203006e-39'],
      'source_sha256':{s:sha(HERE/s) for s in ['continuation.py','differentiate.py','certify_continuation.py']},
      'input_sha256':{k:sha(p) for k,p in parents.items()},'cells':records,
      'scope':'C4 and C4 prime on the exact R03 graph. The R23 pointwise asymptotic coefficient persists. No extension of R27 finite-M remainder constants, no claim of maximal continuation, no C6 or convexity or finite-M-optimum monotonicity.'}
    (output/'certificate.json').write_text(json.dumps(pack(data),indent=2)+'\n');return data
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
    certify(args.output_dir)
if __name__=='__main__':main()
