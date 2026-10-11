#!/usr/bin/env python3
"""Compare recreated proof numbers with the frozen records, ignoring timing.
Changes in timing/provenance hashes are reported separately from math data.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parent

OUTPUTS={
 '01_certify_cusp_family_quartic':'cusp_verified/results/quartic_cusp_certificate.json',
 '01_certify_cusp_family_sextic':'cusp_verified/results/sextic_cusp_certificate.json',
 '07_certify_robustness':'cusp_robustness/results/robustness_certificate.json',
 '07_condition_witness':'cusp_robustness/results/condition_witness.json',
 '07_pinned_cusp':'cusp_robustness/results/pinned_cusp_certificate.json',
 '08_certify_family':'cusp_pinned_family/results/family_certificate.json',
 '08_certify_points':'cusp_pinned_family/results/point_certificates.json',
 '08_certify_fold_samples':'cusp_pinned_family/results/fold_samples.json',
 '09_moment_dictionary':'cusp_shape_design/results/dictionary_16.json',
 '09_certify_design':'cusp_shape_design/results/design_certificate.json',
 '09_build_local_jets':'cusp_shape_design/results/local_jets.json',
 '09_certify_boundaries':'cusp_shape_design/results/boundary_certificate.json',
 '09_certify_local_v2':'cusp_shape_design/results/local_certificate.json',
 '09_certify_samples':'cusp_shape_design/results/fold_samples.json',
 '10_build_model_v2':'swallowtail_window/results/model_v2.json',
 '10_certify_window':'swallowtail_window/results/window_certificate.json',
 '10_certify_samples':'swallowtail_window/results/sample_certificate.json',
 '10_certify_chart':'swallowtail_window/results/chart_certificate.json',
 '11_certify_candidate':'kernel_design_principle/results/candidate_certificate.json',
 '12_certify_threshold':'kernel_norm_threshold/results/threshold_certificate.json',
}

def ball(x):
 m,e=x['mid_man_exp'];r,f=x['rad_man_exp']
 center=Q(m)*Q(2)**e;radius=Q(r)*Q(2)**f
 return center-radius,center+radius

def compare(x,y,path,record):
 if isinstance(x,dict) and isinstance(y,dict):
  if 'mid_man_exp' in x and 'rad_man_exp' in x:
   record['balls']+=1
   a,b=ball(x),ball(y)
   if a==b:record['identical_balls']+=1
   else:
    record['changed_balls'].append({'path':path,'overlap':max(a[0],b[0])<=min(a[1],b[1]),
      'old':x.get('enclosure'),'new':y.get('enclosure')})
   return
  for k in set(x)|set(y):
   if k not in x or k not in y:record['other_changes'].append({'path':path+'/'+k,'type':'key'});continue
   if any(z in k for z in ('sha256','elapsed','created_utc','completed_utc')):
    if x[k]!=y[k]:record['metadata_changes']+=1
    continue
   compare(x[k],y[k],path+'/'+k,record)
 elif isinstance(x,list) and isinstance(y,list):
  if len(x)!=len(y):record['other_changes'].append({'path':path,'type':'length','old':len(x),'new':len(y)})
  for i,(a,b) in enumerate(zip(x,y)):compare(a,b,path+'/'+str(i),record)
 elif x!=y:record['other_changes'].append({'path':path,'old':x,'new':y})

rows=[]
for run in sorted((HERE/'regenerations').glob('*/run.json')):
 job=json.loads(run.read_text());folder=run.parent;pairs=[]
 if (folder/'result.json').exists():
  assert job['id'] in OUTPUTS,job['id']
  pairs.append((RESEARCH/OUTPUTS[job['id']],folder/'result.json'))
 if (folder/'generated').exists():
  for p in sorted((folder/'generated').rglob('*.json')):
   q=RESEARCH/p.relative_to(folder/'generated')
   if q.exists():pairs.append((q,p))
 for old,new in pairs:
  record={'job':job['id'],'input':str(old.relative_to(RESEARCH)),
   'recreated':str(new.relative_to(HERE)),'balls':0,'identical_balls':0,
   'changed_balls':[],'other_changes':[],'metadata_changes':0}
  compare(json.loads(old.read_text()),json.loads(new.read_text()),'',record)
  rows.append(record)
out={'files_compared':len(rows),'interval_balls_compared':sum(r['balls'] for r in rows),
 'identical_interval_balls':sum(r['identical_balls'] for r in rows),
 'disjoint_interval_changes':sum(not v['overlap'] for r in rows for v in r['changed_balls']),
 'changed_overlapping_intervals':sum(v['overlap'] for r in rows for v in r['changed_balls']),
 'nonmetadata_changes':sum(len(r['other_changes']) for r in rows),'files':rows}
(HERE/'regeneration_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='files'},indent=2))
