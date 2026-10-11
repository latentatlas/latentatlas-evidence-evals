#!/usr/bin/env python3
"""Numerical finite-dictionary search only; candidates require certification."""
import argparse,itertools,json,sys,time
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
from moment_dictionary import HERE,sha


def val(x):
    a,e=x['mid_man_exp'];return float(a*2.0**e)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dictionary',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();raw=json.loads(args.dictionary.read_text())
    q=json.loads((HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json').read_text())
    moments=np.array([[val(v) for v in row['moments']] for row in raw['rows']]).T
    A=moments[:3]/np.max(np.abs(moments[:3]),axis=1)[:,None]
    da=moments[3]/val(q['root_derivative_enclosures'][3]);db=moments[4]/val(q['root_derivative_enclosures'][4])
    rows=[]
    for inds in itertools.combinations(range(A.shape[1]),4):
        sub=A[:,inds]
        c=np.array([(-1)**j*np.linalg.det(np.delete(sub,j,axis=1)) for j in range(4)])
        if np.sum(np.abs(c))==0:continue
        w=c/np.sum(np.abs(c));a=float(w@da[list(inds)]);b=float(w@db[list(inds)])
        if b-a<0:w=-w;a=-a;b=-b
        safe=max(abs(a),abs(b))<2
        row={'frequencies':[j+1 for j in inds],'weights':w.tolist(),'a':a,'b':b,
             'log_opening_narrowing_rate':b-a,'safe_symmetric_half_amplitude':safe,
             'half_interval_C_ratio':((1+a/2)*(1-b/2))/((1+b/2)*(1-a/2)) if safe else None,
             'linear_residual':float(np.max(np.abs(A[:,inds]@w)))}
        rows.append(row)
    rows.sort(key=lambda v:v['log_opening_narrowing_rate'],reverse=True)
    safe=sorted((v for v in rows if v['safe_symmetric_half_amplitude']),key=lambda v:v['half_interval_C_ratio'])
    report={'status':'numerical_candidate_search_only','dictionary_sha256':sha(args.dictionary),
            'max_frequency':raw['max_frequency'],'candidate_count':len(rows),'top_linear_candidates':rows[:20],
            'top_safe_finite_candidates':safe[:20],'all_candidates':rows,'source_sha256':sha(__file__),
            'warning':'Floating-point selection is not an optimality certificate or exact moment cancellation proof.',
            'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(exist_ok=True,parents=True)
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'top_linear':rows[:3],'top_safe_finite':safe[:3]},indent=2))


if __name__=='__main__':main()
