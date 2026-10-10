#!/usr/bin/env python3
"""Scientific figure from exact rational comparison bounds; no fitted optimum."""
import sys
sys.dont_write_bytecode=True
import json
from fractions import Fraction as F
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from compare_values import HERE,M0,H,KS,LOW,pair_bounds,sha
def main():
    cp=HERE/'results/comparisons.json';c=json.loads(cp.read_text());grid=[-H+H*i/256 for i in range(257)]
    rows=[{'nu':str(nu),**pair_bounds(nu+H,M0)} for nu in grid]
    budgets=[M0*(1+F(99*i,256)) for i in range(257)]
    resolutions=[{'budget':str(m),'actual_sufficient':str(F('1.54e-14')*(M0/m)**6),
      'fourth_threshold':str(KS/(LOW[2]*m**2))} for m in budgets]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'r30-fixed'})
    fig,ax=plt.subplots(1,3,figsize=(17.4,5.7),gridspec_kw={'width_ratios':[1.1,1.1,1.0]})
    fig.subplots_adjust(left=.063,right=.977,bottom=.25,top=.76,wspace=.36)
    green='#237f6c';blue='#316eaa';muted='#65717f';orange='#cf7626'
    fig.suptitle('From coefficient motion to finite-budget design comparisons',x=.063,ha='left',y=.96,fontsize=17,fontweight='bold')
    fig.text(.063,.88,r'Exact cusp arc $[-1/64,0]$  |  Uniform remainder for every $M\geq M_0=2\times10^{-5}$',color=muted,fontsize=11)
    for i,(key,scale,color,title,ylabel) in enumerate([
      ('actual_difference',F('1e-13'),green,'A   Actual optimal amplitude',r'$[\delta_\nu(M_0)-\delta_{-1/64}(M_0)]\,/\,10^{-13}$'),
      ('normalized_fourth_difference',F('1e-42'),blue,'B   After removing the first two terms',r'$[Z_{M_0}(\nu)-Z_{M_0}(-1/64)]\,/\,10^{-42}$')]):
        x=list(map(float,grid));lo=[float(F(r[key][0])/scale) for r in rows];hi=[float(F(r[key][1])/scale) for r in rows]
        ax[i].fill_between(x,lo,hi,color=color,alpha=.22,label='Proved lower / upper bounds')
        ax[i].plot(x,lo,color=color,lw=1.2);ax[i].plot(x,hi,color=color,lw=1.2)
        ax[i].axhline(0,color='#333333',lw=.7);ax[i].scatter([-float(H)],[0],color=color,s=25,zorder=4,label='Reference difference = 0')
        ax[i].set(title=title,xlabel=r'Cusp driver $\nu$',ylabel=ylabel,xlim=(-float(H),0))
        ax[i].set_xticks([-float(H),-float(H)/2,0],['−1/64','−1/128','0'])
        ax[i].legend(loc='upper left',frameon=False,fontsize=8)
    ratio=[float(m/M0) for m in budgets]
    ax[2].loglog(ratio,[float(F(r['fourth_threshold'])) for r in resolutions],color=blue,lw=2.2,label=r'For $Z_M$: $\Delta\nu>\eta_4(M)$')
    ax[2].loglog(ratio,[float(F(r['actual_sufficient'])) for r in resolutions],color=green,lw=2.2,label=r'For $\delta(M)$: $\Delta\nu\geq\eta_0(M)$')
    ax[2].axhline(1/2048,color=orange,linestyle='--',lw=1.4,label='Spacing of 33 ordered nodes')
    ax[2].set(title='C   Sufficient separation for ordering',xlabel=r'Slope budget $M/M_0$',ylabel=r'Cusp-driver separation $\Delta\nu$',xlim=(1,100),ylim=(1e-27,2e-3))
    ax[2].legend(loc='center left',frameon=False,fontsize=8)
    for axes in ax:
        axes.grid(axis='y',alpha=.18);axes.set_axisbelow(True);axes.title.set_fontsize(11);axes.title.set_fontweight('bold')
    fig.text(.063,.094,r'$Z_M(\nu)=M^4[\delta_\nu(M)-\delta_0(\nu)-C_2(\nu)/M^2]$.  Shading encloses exact differences; no numerical optimizer is plotted.',fontsize=9,color=muted)
    fig.text(.063,.047,'All 33 equally spaced nodes are strictly ordered at every allowed budget. Ordering at arbitrarily small separations remains unproved.',fontsize=9,color=muted)
    fig.canvas.draw();renderer=fig.canvas.get_renderer();outside=[]
    for txt in fig.findobj(matplotlib.text.Text):
        if not txt.get_visible() or not txt.get_text():continue
        b=txt.get_window_extent(renderer)
        if b.x0<0 or b.y0<0 or b.x1>fig.bbox.width or b.y1>fig.bbox.height:outside.append(txt.get_text())
    assert not outside,outside
    folder=HERE/'figures';folder.mkdir(exist_ok=True)
    fig.savefig(folder/'finite_design_comparison.png',dpi=180,facecolor='white')
    fig.savefig(folder/'finite_design_comparison.svg',facecolor='white',metadata={'Date':None});plt.close(fig)
    data={'source_sha256':sha(__file__),'comparison_source_sha256':sha(HERE/'compare_values.py'),
      'comparisons_sha256':sha(cp),'rows':rows,'resolutions':resolutions,'text_outside_canvas':outside,
      'finite_budget_optimizer_computed':False,'figures':{p.name:sha(p) for p in sorted(folder.iterdir()) if p.is_file()}}
    (HERE/'results/plot_data.json').write_text(json.dumps(data,indent=2)+'\n');print('Scientific figure written; visual inspection required.')
if __name__=='__main__':main()
