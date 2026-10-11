#!/usr/bin/env python3
"""Render a budget bracket; no numerical root count or optimality is inferred."""
import hashlib
import json
import struct
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    source = HERE/'results/candidate_check.json'
    data = json.loads(source.read_text())
    assert data['status'] == 'independent_rational_pinned_design_rank_and_norm_bracket_passed'
    endpoints = data['readable_minimum_norm_bracket']
    lower, upper = map(float, endpoints)
    assert 0 < lower < upper < 1
    directory = HERE/'figures'
    directory.mkdir(exist_ok=True)
    paths = [directory/('minimum_relative_change.'+ext) for ext in ('png','svg')]
    assert not any(p.exists() for p in paths)
    assert not (directory/'metadata.json').exists()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                         'svg.fonttype':'none','svg.hashsalt':'r11-cost-bracket'})
    fig, ax = plt.subplots(figsize=(10.7,4.2),layout='constrained')
    fig.patch.set_facecolor('white')
    left, right = 1e-11,1e-5
    ax.set_xscale('log');ax.set_xlim(left,right);ax.set_ylim(0,1)
    colors = ['#B95C58','#D5DAE2','#428575']
    for x0,x1,color in zip((left,lower,upper),(lower,upper,right),colors):
        ax.fill_between([x0,x1],.32,.50,color=color,linewidth=0)
    for x in (lower,upper):
        ax.vlines(x,.25,.65,color='#172B42',linewidth=1.5)
    ax.text(lower,.72,r'$L=3.9603640200\times10^{-10}$',ha='center',va='bottom',fontsize=11)
    ax.text(upper,.72,r'$U=2.3803280903\times10^{-7}$',ha='center',va='bottom',fontsize=11)
    ax.text((left*lower)**.5,.40,'Excluded',ha='center',va='center',color='white',weight='bold')
    ax.text((lower*upper)**.5,.40,'Threshold unresolved',ha='center',va='center',color='#172B42',weight='bold')
    ax.text((upper*right)**.5,.40,'Feasible budget',ha='center',va='center',color='white',weight='bold')
    ax.text(lower,.18,'Universal lower bound',ha='center',va='top',fontsize=10,color='#172B42')
    ax.text(upper,.18,'Smooth exact design\n'+r'$\|h_c\|_\infty\leq U$',ha='center',va='top',fontsize=10,color='#172B42')
    ax.annotate('',xy=(upper,.61),xytext=(lower,.61),
                arrowprops={'arrowstyle':'|-|','color':'#5C6979','linewidth':1.1})
    ratio=float(Fraction(endpoints[1])/Fraction(endpoints[0]))
    ax.text((lower*upper)**.5,.65,f'Bound ratio: {ratio:.2f}',ha='center',va='bottom',fontsize=10,color='#5C6979')
    ax.set_yticks([])
    for side in ('left','right','top'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#8F9BA7')
    ax.xaxis.set_major_locator(LogLocator(base=10,numticks=7))
    ax.xaxis.set_minor_locator(LogLocator(base=10,subs=range(2,10),numticks=100))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis='x',which='both',color='#8F9BA7')
    ax.set_xlabel(r'Allowed relative kernel change $\delta=\|h\|_\infty$ (log scale)',labelpad=10)
    fig.suptitle('Distance to an order-four zero at the same Q',fontsize=17,weight='bold',x=.055,ha='left')
    ax.set_title('Original theta example  |  Real bounded multipliers  |  No frequency constraint',
                 fontsize=10,color='#5C6979',loc='left',pad=7)
    fig.savefig(paths[0],dpi=200)
    fig.savefig(paths[1],metadata={'Date':None})
    plt.close(fig)
    dims=list(struct.unpack('>II',paths[0].read_bytes()[16:24]))
    report={
        'status':'scientific_budget_bracket_from_certified_endpoints',
        'source_sha256':sha(__file__),
        'input_sha256':{'candidate_check.json':sha(source)},
        'readable_minimum_norm_bracket':endpoints,
        'display_only_ratio':ratio,
        'display_only_xlim':[left,right],
        'png_dimensions':dims,
        'files':{p.name:sha(p) for p in paths},
        'interpretation':'No admissible design has norm below L. A smooth exact nondegenerate design has norm at most U. The exact minimum lies in the unresolved bracket; no frequency constraint is imposed. U bounds a coefficient l1 sum, not a computed exact sup norm.',
        'rendering_precision':'Matplotlib uses floating point for placement only. Exact rational interval endpoints remain in the cited checker JSON.',
    }
    with (directory/'metadata.json').open('x') as stream:
        json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'files':[p.name for p in paths],'png_dimensions':dims}))


if __name__=='__main__':
    main()
