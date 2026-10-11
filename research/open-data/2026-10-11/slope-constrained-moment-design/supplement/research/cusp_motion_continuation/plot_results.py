#!/usr/bin/env python3
"""Scientific figure: proved continuum bounds and separate diagnostics."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from fractions import Fraction as F
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ends(x):
    m,e=x['mid_man_exp'];r,s=x['rad_man_exp'];v=F(m)*F(2)**e;d=F(r)*F(2)**s;return v-d,v+d
def main():
    certp=HERE/'results/cover/certificate.json';directp=HERE/'results/direct_check.json';probep=HERE/'diagnostics/probe_coarse.json'
    c,d,p=[json.loads(x.read_text()) for x in [certp,directp,probep]]
    L=F(1,64);lo,hi=map(F,c['published_derivative_bounds']);Clo=F('2.49203004e-39');Chi=F('2.49203006e-39')
    grid=[-L+L*i/200 for i in range(201)];lower=[100*x*hi/Clo for x in grid];upper=[100*x*lo/Chi for x in grid]
    rows=d['runs'][1]['rows'];ev={F(x['nu']):x for x in d['runs'][1]['evaluations']};C0=F(ev[F(0)]['coefficients']['C4']);samples=[]
    for r in rows:
        nu=F(r['nu']);v=F(ev[nu]['coefficients']['C4'])
        samples.append({'nu':str(nu),'C4':str(v),'relative_percent':str(100*(v/C0-1)),
          'C4_prime_diagnostic':r['steps'][1]['derivatives']['C4']})
    bands=[{'left':row['left'],'right':row['right'],'bounds':list(map(str,ends(row['C4_prime'])))} for row in c['cells']]
    coarse=ends(p['motion']['derivatives']['C4']);fine=(min(ends(row['C4_prime'])[0] for row in c['cells'][:4]),max(ends(row['C4_prime'])[1] for row in c['cells'][:4]))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'r29-fixed'})
    fig,ax=plt.subplots(1,3,figsize=(17.4,5.6),gridspec_kw={'width_ratios':[1.22,1.12,.90]})
    fig.subplots_adjust(left=.066,right=.981,bottom=.23,top=.77,wspace=.35)
    green='#237f6c';orange='#d27320';blue='#316eaa';muted='#65717f'
    fig.suptitle('Fourth-order coefficient: a 1024-fold extension of the proved arc',x=.066,ha='left',y=.96,fontsize=17,fontweight='bold')
    fig.text(.066,.883,r'Exact cusp driver $\nu\in[-1/64,0]$  |  32 validated cells  |  Original $u$ and $\nu$ coordinates',color=muted,fontsize=11)
    ax[0].fill_between(list(map(float,grid)),list(map(float,lower)),list(map(float,upper)),color=green,alpha=.19,label='Proved from derivative bounds')
    ax[0].plot(list(map(float,grid)),list(map(float,lower)),color=green,lw=1);ax[0].plot(list(map(float,grid)),list(map(float,upper)),color=green,lw=1)
    ax[0].scatter([float(F(x['nu'])) for x in samples],[float(F(x['relative_percent'])) for x in samples],s=30,color=orange,zorder=5,label='Independent integral diagnostics')
    ax[0].set(title='A   Change relative to the endpoint',xlabel=r'Cusp driver $\nu$',ylabel=r'$100\,[C_4(\nu)/C_4(0)-1]$  (%)',xlim=(-float(L),0),ylim=(-.36,.019))
    ax[0].legend(loc='lower right',fontsize=8,frameon=False)
    for band in bands:
        a,b=map(float,map(F,[band['left'],band['right']]));yl,yu=[float(F(x)/F('1e-40')) for x in band['bounds']]
        ax[1].fill_between([a,b],[yl,yl],[yu,yu],color=blue,alpha=.23,linewidth=0)
    ax[1].plot([],[],color=blue,lw=7,alpha=.30,label='Proved interval on each cell')
    ax[1].scatter([float(F(x['nu'])) for x in samples],[float(F(x['C4_prime_diagnostic'])/F('1e-40')) for x in samples],s=30,color=orange,label='Finite-difference diagnostics',zorder=5)
    ax[1].axhline(0,color='#333333',lw=1)
    ax[1].set(title='B   Positive derivative on the full arc',xlabel=r'Cusp driver $\nu$',ylabel=r"$C_4'(\nu)\,/\,10^{-40}$",xlim=(-float(L),0),ylim=(-.17,5.8))
    ax[1].legend(loc='lower right',fontsize=8,frameon=False)
    for k,(bound,color) in enumerate([(coarse,orange),(fine,green)]):
        a,b=[float(x/F('1e-40')) for x in bound];mid=(a+b)/2
        ax[2].errorbar(k,mid,yerr=(b-a)/2,fmt='none',color=color,capsize=12,elinewidth=4)
    ax[2].axhline(0,color='#333333',lw=1)
    ax[2].set(title='C   A wide box can hide the sign',ylabel=r"Enclosure of $C_4'\,/\,10^{-40}$",xlim=(-.55,1.55),ylim=(-6.7,14))
    ax[2].set_xticks([0,1],['One large box\n(inconclusive)','Four smaller boxes\n(positive)'])
    ax[2].text(.5,.98,r'Same interval: $[-1/512,0]$',ha='center',va='top',transform=ax[2].transAxes,fontsize=9,color=muted)
    for axes in ax:
        axes.grid(axis='y',alpha=.19);axes.set_axisbelow(True);axes.title.set_fontsize(11);axes.title.set_fontweight('bold')
    for axes in ax[:2]:axes.ticklabel_format(axis='x',style='plain',useOffset=False);axes.set_xticks([-.015625,-.0078125,0],['−1/64','−1/128','0'])
    fig.text(.066,.065,'Colored regions and bars: rigorous enclosures under the analytic proof. Orange points: numerical diagnostics.\nNo monotonicity of the finite-budget optimum or extension of the previous remainder constants is claimed.',fontsize=9,color=muted,linespacing=1.6)
    fig.canvas.draw();renderer=fig.canvas.get_renderer();outside=[]
    for txt in fig.findobj(matplotlib.text.Text):
        if not txt.get_visible() or not txt.get_text():continue
        bb=txt.get_window_extent(renderer)
        if bb.x0<0 or bb.y0<0 or bb.x1>fig.bbox.width or bb.y1>fig.bbox.height:outside.append(txt.get_text())
    assert not outside,outside
    images=HERE/'figures';images.mkdir(exist_ok=True)
    fig.savefig(images/'continuation.png',dpi=180,facecolor='white');fig.savefig(images/'continuation.svg',facecolor='white',metadata={'Date':None});plt.close(fig)
    data={'source_sha256':sha(__file__),'certificate_sha256':sha(certp),'direct_check_sha256':sha(directp),'coarse_probe_sha256':sha(probep),
      'grid':list(map(str,grid)),'lower_percent':list(map(str,lower)),'upper_percent':list(map(str,upper)),
      'samples':samples,'bands':bands,'coarse_comparison':list(map(str,coarse)),'refined_comparison':list(map(str,fine)),
      'figures':{p.name:sha(p) for p in images.iterdir() if p.is_file()},'text_outside_canvas':outside,
      'no_convexity_or_finite_M_monotonicity_claim':True}
    (HERE/'results/plot_data.json').write_text(json.dumps(data,indent=2)+'\n');print('Scientific figure written; visual inspection still required.')
if __name__=='__main__':main()
