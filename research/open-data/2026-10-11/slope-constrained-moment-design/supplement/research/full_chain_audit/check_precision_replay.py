#!/usr/bin/env python3
"""Check the additional R01 130-digit rerun using exact rational endpoints."""
import sys
sys.dont_write_bytecode = True
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'cusp_verified/results'

def ball(d):
    m, e = d['mid_man_exp']; r, f = d['rad_man_exp']
    c, rad = Q(m)*Q(2)**e, Q(r)*Q(2)**f
    return c-rad, c+rad

counts = {'identical_interval_balls': 0, 'ignored_metadata_differences': 0}
def compare(a, b, path=''):
    if isinstance(a, dict):
        assert isinstance(b, dict) and a.keys() == b.keys(), path
        if 'mid_man_exp' in a and 'rad_man_exp' in a:
            assert ball(a) == ball(b), path
            counts['identical_interval_balls'] += 1
            return
        for k in a:
            if any(s in k for s in ('sha256', 'elapsed', 'created_utc', 'completed_utc')):
                counts['ignored_metadata_differences'] += a[k] != b[k]
            else:
                compare(a[k], b[k], path+'/'+k)
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)): compare(x, y, path+'/'+str(i))
    else:
        assert a == b, (path, a, b)

old130 = json.loads((OLD/'quartic_precision_check.json').read_text())
new130 = json.loads((HERE/'quartic_precision_replay.json').read_text())
old110 = json.loads((OLD/'quartic_cusp_certificate.json').read_text())
compare(old130, new130)
root_boxes = []
for data in (old110, new130):
    r = ball(data['root_radius'])[1]
    root_boxes.append([(ball(c)[0]-r, ball(c)[1]+r)
                       for c in data['center_exact_dyadic']])
assert all(a[0] <= b[0] <= b[1] <= a[1]
           for a, b in zip(*root_boxes))
out = dict(status='precision_rerun_identical_and_root_contained',
           **counts, higher_precision_root_box_inside_110_digit_box=True,
           dps=130, theta_terms=20, integration_panels=16,
           command='PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python '
                   'research/cusp_verified/certify_cusp.py --family quartic '
                   '--dps 130 --terms 20 --pieces 16 --output '
                   'research/full_chain_audit/quartic_precision_replay.json',
           source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           scope='Existing R01 precision result only; no new scientific claim.')
(HERE/'precision_comparison.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
