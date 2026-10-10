#!/usr/bin/env python3
"""Scientific figures from the certified finite folds and exact formulas."""
import hashlib,json,sys
from pathlib import Path
from fractions import Fraction
sys.dont_write_bytecode=True
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
OUT=HERE/'figures'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(v):
    a,e=v['mid_man_exp'];return float(Fraction(a)*Fraction(2)**e)
def rational_mid(v):return float((Fraction(v[0])+Fraction(v[1]))/2)


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'metadata.json').exists():raise FileExistsError('Figures already recorded')
    names=['fold_samples.json','design_check.json','boundary_certificate.json','key_results.json']
    data={n:json.loads((HERE/'results'/n).read_text()) for n in names}
    folds=data[names[0]];design=data[names[1]];boundary=data[names[2]]
    a,b=map(rational_mid,(design['a'],design['b']));tau=1/128
    left,right=map(rational_mid,(boundary['mu_unfolding_boundary'],boundary['quartic_boundary']))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
        'axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,
        'axes.grid':True,'grid.alpha':0.16,'svg.fonttype':'none','savefig.facecolor':'white'})
    files={}
    def save(fig,name):
        for ext in ('png','svg'):
            p=OUT/(name+'.'+ext);fig.savefig(p,dpi=190);files[p.name]=sha(p)
        plt.close(fig)

    fig,axs=plt.subplots(1,2,figsize=(12,5.6))
    fig.subplots_adjust(left=.075,right=.975,bottom=.19,top=.78,wspace=.28)
    fig.suptitle('Fixed cusp, strongly changing three-root region',y=.97,fontsize=17,fontweight='bold')
    fig.text(.5,.885,r'Exact $Q$ is fixed; $\nu=0$. Each kernel differs from $\Phi$ by at most $0.78125\%$.',ha='center',fontsize=11)
    colors=['#377c9d','#9a761f','#c24b47']
    labels=[r'$\epsilon=-1/128$',r'$\epsilon=0$',r'$\epsilon=+1/128$']
    for model,color,label in zip((0,4,8),colors,labels):
        samples=sorted([s for s in folds['samples'] if s['model']==model],key=lambda s:s['j'])
        xx=np.array([0]+[mid(s['ell'])*1e6 for s in samples])
        high=np.array([0]+[mid(s['upper']['root_enclosures'][1])*1e9 for s in samples])
        low=np.array([0]+[mid(s['lower']['root_enclosures'][1])*1e9 for s in samples])
        axs[0].fill_between(xx,low,high,color=color,alpha=.12)
        axs[0].plot(xx,high,'o-',color=color,label=label,lw=1.7,ms=3.5)
        axs[0].plot(xx,low,'o-',color=color,lw=1.7,ms=3.5)
    axs[0].plot(0,0,'ko',ms=5);axs[0].annotate('same cusp Q',(0,0),(.13,-1.05),arrowprops={'arrowstyle':'->','lw':.9})
    axs[0].set(xlabel=r'$(\lambda-\lambda_Q)\times 10^6$',ylabel=r'$(\mu-\mu_Q)\times 10^9$',
               title='A  Certified fold boundaries',xlim=(-.025,1.04),ylim=(-1.45,1.45))
    axs[0].legend(loc='upper left',fontsize=9.5,frameon=True)
    ss=[next(s for s in folds['samples'] if s['model']==j and s['j']==8) for j in range(9)]
    eps=np.array([mid(folds['models'][j]['epsilon']) for j in range(9)])
    widths=np.array([mid(s['width'])*1e9 for s in ss])
    ref=[next(s for s in folds['samples'] if s['model']==j and s['j']==8) for j in (9,10)]
    axs[1].plot(eps*100,widths,'o-',color=colors[0],ms=5,label='Selected direction (certified points)')
    axs[1].plot(np.array([-tau,tau])*100,[mid(s['width'])*1e9 for s in ref],'^--',color='#6c7178',ms=6,label='Previous direction (same amplitudes)')
    axs[1].annotate('74.6395% narrower',xy=(eps[-1]*100,widths[-1]),xytext=(-.30,.83),
                    arrowprops={'arrowstyle':'->','color':colors[0]},color=colors[0],fontsize=12,fontweight='bold')
    axs[1].set(xlabel=r'$100\epsilon$',ylabel=r'Finite width $W\times 10^9$',title=r'B  Actual width at $\ell=10^{-6}$',ylim=(.4,2.7))
    axs[1].legend(loc='upper right',fontsize=8.5,frameon=True)
    fig.text(.5,.055,'Markers: rigorous fold enclosures (error bars smaller than markers). Lines and shading: visual guides.\nNesting between samples is proved separately on the entire stated window.',ha='center',fontsize=9,color='#444')
    save(fig,'finite_shape_design')

    fig,axs=plt.subplots(1,2,figsize=(12,5.6))
    fig.subplots_adjust(left=.075,right=.975,bottom=.20,top=.78,wspace=.27)
    fig.suptitle('Two distinct limits of a positive-kernel family',y=.97,fontsize=17,fontweight='bold')
    fig.text(.5,.885,r'$Q$ remains a zero of order at least three; $\Phi_\epsilon>0.9672\,\Phi$ throughout the open interval.',ha='center',fontsize=11)
    eps=np.linspace(left+1e-6,right,1600)
    for ax in axs:
        ax.axvspan(-tau*100,tau*100,color='#dcefe8',zorder=0)
        ax.axvline(left*100,color='#a27325',ls=':',lw=1.5)
        ax.axvline(right*100,color='#b33f5f',ls=':',lw=1.5)
        ax.axvline(0,color='#aaa',lw=.8)
        ax.set(xlim=(left*100-.25,right*100+.25),xlabel=r'$100\epsilon$')
    axs[0].plot(eps*100,(1+a*eps)/(1+b*eps),color='#2c738c',lw=2)
    axs[0].plot(0,1,'ko',ms=4)
    axs[0].set(title='A  Exact leading opening coefficient',ylabel=r'$C(\epsilon)/C(0)$',ylim=(-.2,10))
    axs[0].text(-1.7,7.3,r'$C(\epsilon)/C(0)=\frac{1+a\epsilon}{1+b\epsilon}$',fontsize=15)
    axs[0].annotate(r'$C\to+\infty$',xy=(left*100+.14,9.2),xytext=(-2.6,8.5),arrowprops={'arrowstyle':'->'},fontsize=11)
    axs[0].annotate(r'$C\to0$',xy=(right*100,0),xytext=(.8,2.1),arrowprops={'arrowstyle':'->'},fontsize=11)
    axs[1].plot(eps*100,1+a*eps,color='#b33f5f',lw=2,label=r'$G_3/F_3=1+a\epsilon$')
    axs[1].plot(eps*100,1+b*eps,color='#a27325',lw=2,label=r'$G_4/F_4=1+b\epsilon$')
    axs[1].plot([left*100,right*100],[0,0],'o',color='#333',ms=4)
    axs[1].set(title='B  Which derivative vanishes?',ylabel='Derivative multiplier',ylim=(-.25,3.05))
    axs[1].legend(loc='upper right',fontsize=10,frameon=True)
    axs[1].annotate('$G_4=0$\ncontrol rank lost',xy=(left*100,0),xytext=(-2.8,.65),fontsize=10,
                    arrowprops={'arrowstyle':'->','color':'#a27325'},color='#866022')
    axs[1].annotate('$G_3=0$\norder-four zero',xy=(right*100,0),xytext=(-.1,.45),fontsize=10,
                    arrowprops={'arrowstyle':'->','color':'#b33f5f'},color='#a73555')
    fig.text(.5,.06,'Green band: certified finite fold window. Outside it, the exact leading coefficient and endpoint ranks are proved;\nno common finite fold window is asserted. Vertical scale in A is clipped at 10. Modified kernels only.',ha='center',fontsize=9,color='#444')
    save(fig,'opening_boundaries')
    meta={'status':'figures_generated_from_recorded_certificates','files':files,
        'input_sha256':{n:sha(HERE/'results'/n) for n in names},'source_sha256':sha(__file__),
        'dimensions_png':[2280,1064],
        'scope':'First figure: finite certified points, connecting lines are guides; continuum nesting proved in local_certificate.json. Second: exact rational-in-amplitude formulas with certified coefficients, plotted using floating-point midpoints; not a plot of finite width outside the green band.'}
    with (OUT/'metadata.json').open('x') as f:json.dump(meta,f,indent=2);f.write('\n')
    print('Two PNG/SVG figure pairs recorded')


if __name__=='__main__':main()
