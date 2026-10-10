#!/usr/bin/env python3
"""R24 coefficient decomposition and ratio of formal terms; no optimum curve."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(r):return mp.mpf(r['mid_man_exp'][0])*mp.power(2,r['mid_man_exp'][1])
def rad(r):return mp.mpf(r['rad_man_exp'][0])*mp.power(2,r['rad_man_exp'][1])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);args=ap.parse_args()
    if args.outdir.exists():raise FileExistsError(args.outdir)
    args.outdir.mkdir(parents=True);mp.mp.dps=80
    cp=HERE/'results/certificate.json';cert=json.loads(cp.read_text());co=cert['coefficients']
    keys=['C4_amplitude_part','C4_shape_part','C4_moment_part','C4'];labels=['amplitude\nnormalization','local\nshape','moment\ncorrection','total $C_4$']
    barvals=[float(mid(co[k])*mp.mpf('1e39')) for k in keys]
    ratio=mid(co['C4_over_C2']);rlo=ratio-rad(co['C4_over_C2']);rhi=ratio+rad(co['C4_over_C2'])
    curves=[]
    for mf in np.geomspace(2e-5,2e-3,200):
        M=mp.mpf(str(mf));val=ratio/(M*M)
        curves.append({'M':str(M),'ratio':mp.nstr(val,45),'lower':mp.nstr(rlo/M**2,45),'upper':mp.nstr(rhi/M**2,45)})
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
        'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'r24-theta-c4'})
    fig,axs=plt.subplots(1,2,figsize=(13,5.7));fig.subplots_adjust(left=.085,right=.97,bottom=.23,top=.76,wspace=.32)
    colors=['#246A96','#BC493E','#A07824','#24836B']
    axs[0].bar(range(4),barvals,color=colors,width=.62)
    axs[0].axhline(0,color='0.4',lw=.8)
    for i,v in enumerate(barvals):axs[0].text(i,v+(0.08 if v>0 else -0.10),format(v,'+.6f'),ha='center',va='bottom' if v>0 else 'top',fontsize=10)
    axs[0].set_xticks(range(4),labels);axs[0].set_ylim(-1.1,3.22)
    axs[0].set(ylabel=r'contribution to $C_4$  ($\times 10^{-39}$)',title='Certified coefficient decomposition')
    axs[0].grid(axis='y',alpha=.18);axs[0].set_axisbelow(True)
    xx=[float(r['M']) for r in curves];yy=[float(r['ratio']) for r in curves]
    axs[1].loglog(xx,yy,color='#246A96',lw=2.1)
    axs[1].fill_between(xx,[float(r['lower']) for r in curves],[float(r['upper']) for r in curves],color='#246A96',alpha=.25)
    refM=mid(cert['formal_reference_terms']['M']);refR=mid(cert['formal_reference_terms']['ratio_C4_term_to_C2_term'])
    axs[1].scatter([float(refM)],[float(refR)],color='#BC493E',s=34,zorder=3)
    axs[1].text(.43,.86,r'$M=2\times10^{-5}$'+'\n'+r'ratio $\approx6.76932\times10^{-6}$',transform=axs[1].transAxes,fontsize=11)
    axs[1].set(xlabel='slope budget M',ylabel=r'$(C_4/M^4)/(C_2/M^2)$',title='Relative size of the two known terms')
    axs[1].grid(which='both',alpha=.17)
    fig.suptitle('Positive fourth-order coefficient at the fixed theta cusp',fontsize=16,y=.965)
    fig.text(.5,.87,r'$2.49203004\times10^{-39}<C_{4,\theta}<2.49203006\times10^{-39}$',ha='center',fontsize=13)
    fig.text(.5,.08,'Left: all three contributions use the same exact base problem. Right: ratio of formal asymptotic terms.',ha='center',fontsize=10,color='#444444')
    fig.text(.5,.035,'The actual finite-budget optimum and the fourth-order remainder are not enclosed by the right panel.',ha='center',fontsize=10,color='#444444')
    paths=[]
    for ext in ['png','svg']:
        p=args.outdir/('theta_fourth_order.'+ext);fig.savefig(p,dpi=180,metadata={'Date':None} if ext=='svg' else {'Software':'R24 scientific plot'});paths.append(p)
    plt.close(fig)
    data={'source_sha256':sha(__file__),'certificate_sha256':sha(cp),'precision_digits':80,
       'decomposition_keys':keys,'scaled_decomposition':barvals,'formal_ratio_curve':curves,
       'figures':{p.name:sha(p) for p in paths},'not_a_plot_of_the_finite_budget_optimum':True}
    (args.outdir/'plot_data.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':'R24_scientific_figure_written','panels':2,'ratio_samples':len(curves)}))
if __name__=='__main__':main()
