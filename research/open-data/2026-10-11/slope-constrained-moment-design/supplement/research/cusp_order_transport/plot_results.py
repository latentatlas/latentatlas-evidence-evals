#!/usr/bin/env python3
"""Plot rigorous generator and finite-value lower bounds, not fitted optima."""
import sys
sys.dont_write_bytecode=True
import hashlib,json
from pathlib import Path
from fractions import Fraction as F
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    rp=HERE/'results/rational_check.json';r=json.loads(rp.read_text())
    finite=r['finite_cells'];x=[float((F(t['left'])+F(t['right']))/2) for t in finite];y=[float(F(t['dissipativity_upper'])) for t in finite]
    # Exact positive rational separations on a logarithmic-looking grid.
    ds=[F(i,10)*F(10)**power for power in range(-18,-2) for i in range(10,100)]
    ds=[d for d in ds if d<=F(1,64)]+[F(1,64)];ds=sorted(set(ds));M=F('2e-5')
    L=F('2.7e-11')+F('7.4e-26')/M**2+F('1.9e-40')/M**4;KS=F('2.66e-53')
    rows=[{'distance':str(d),'R30_lower_per_distance':str(L-KS/M**6/d),'R31_lower_per_distance':'2.07e-11'} for d in ds]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'r31-fixed'})
    fig,ax=plt.subplots(1,2,figsize=(14.4,6.0));fig.subplots_adjust(left=.072,right=.976,bottom=.24,top=.75,wspace=.3)
    green='#237f6c';blue='#316eaa';orange='#c6782f';muted='#596879'
    fig.suptitle('Strict ordering without a minimum parameter separation',x=.072,ha='left',y=.955,fontsize=17,fontweight='bold')
    fig.text(.072,.88,r'Exact cusp arc $[-1/64,0]$  |  Actual optimal amplitude at every $M\geq2\times10^{-5}$',fontsize=11,color=muted)
    ax[0].plot(x,y,color=blue,lw=2,label='Upper bounds on 1,024 whole cells')
    ax[0].axhline(-.02,color=green,lw=1.5,linestyle='--',label=r'Required bound: $-c=-0.02$')
    ax[0].set(xlim=(0,1),ylim=(-.11,.002),xlabel=r'Integration coordinate $u$',ylabel=r'Upper bound for $r+\kappa+a_0|r_u|$',title='A   The transport contracts on the whole domain')
    ax[0].legend(loc='lower left',frameon=False,fontsize=9)
    ax[0].text(.035,.43,r'$u\geq1$: analytic bound $<-0.0511$',transform=ax[0].transAxes,color=muted,fontsize=9)
    ax[0].text(.035,.35,'Infinite tail included in the proof',transform=ax[0].transAxes,color=muted,fontsize=9)
    ax[1].semilogx([float(F(t['distance'])) for t in rows],[float(F(t['R30_lower_per_distance'])/F('1e-11')) for t in rows],color=orange,lw=2,label='R30: endpoint remainder comparison')
    ax[1].axhline(2.07,color=green,lw=2,label='R31: transport lower bound')
    ax[1].axhline(0,color='#333333',lw=.7)
    ax[1].set(xlim=(1e-18,1/64),ylim=(-.9,3.15),xlabel=r'Positive parameter separation $d=\nu_2-\nu_1$',ylabel=r'Lower bound for $(\delta_{\nu_2}-\delta_{\nu_1})/d\,/\,10^{-11}$',title=r'B   Positive for every $d>0$; example $M=M_0$')
    ax[1].set_xticks([1e-18,1e-14,1e-10,1e-6,1e-2]);ax[1].minorticks_off()
    ax[1].legend(loc='lower right',frameon=False,fontsize=9)
    for a in ax:
        a.grid(axis='y',alpha=.2);a.set_axisbelow(True);a.title.set_fontweight('bold');a.title.set_fontsize(11)
    fig.text(.072,.115,'Both panels display proved bounds. Panel B does not plot an exact or numerically fitted optimizer.',color=muted,fontsize=10)
    fig.text(.072,.066,'The normalized fourth-order residual and differentiability of the finite-budget optimum remain separate open questions.',color=muted,fontsize=10)
    fig.canvas.draw();renderer=fig.canvas.get_renderer();outside=[]
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_visible() or not t.get_text():continue
        b=t.get_window_extent(renderer)
        if b.x0<0 or b.y0<0 or b.x1>fig.bbox.width or b.y1>fig.bbox.height:outside.append(t.get_text())
    assert not outside,outside
    folder=HERE/'figures';folder.mkdir(exist_ok=True)
    fig.savefig(folder/'order_transport.png',dpi=180,facecolor='white');fig.savefig(folder/'order_transport.svg',facecolor='white',metadata={'Date':None});plt.close(fig)
    out={'source_sha256':sha(__file__),'rational_check_sha256':sha(rp),'finite_rows':finite,'comparison_rows':rows,'text_outside_canvas':outside,'optimizer_computed':False,'figures':{p.name:sha(p) for p in sorted(folder.iterdir()) if p.is_file()}}
    (HERE/'results/plot_data.json').write_text(json.dumps(out,indent=2)+'\n');print('Figure created; visual inspection required.')
if __name__=='__main__':main()
