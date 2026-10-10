#!/usr/bin/env python3
"""Static paper figures; certificates supply points, not interpolating lines."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
from check_family import endpoints


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(v):
    a,b=endpoints(v);return float((a+b)/2)


def main():
    out=HERE/'figures';out.mkdir(exist_ok=True)
    paths=[out/(n+'.'+e) for n in ('pinned_cusp_sheet','finite_fold_comparison') for e in ('png','svg')]
    if any(p.exists() for p in paths) or (out/'metadata.json').exists():raise FileExistsError('Figures already exist')
    pp=HERE/'results/point_certificates.json';fp=HERE/'results/fold_samples.json'
    points=json.loads(pp.read_text());folds=json.loads(fp.read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
                        'axes.spines.right':False,'axes.titleweight':'bold','svg.hashsalt':'R08-pinned-family'})
    colors={-.5:'#B76A24',0:'#777777',.5:'#176888'}
    fig,ax=plt.subplots(1,2,figsize=(12,5.6))
    fig.subplots_adjust(left=.09,right=.98,bottom=.23,top=.79,wspace=.30)
    fig.suptitle('A fixed quartic cusp, a changing cusp arc and opening',fontsize=16,y=.97)
    for eps in (-.5,.5):
        rows=[r for r in points['rows'] if mid(r['epsilon'])==eps]
        base=[r for r in points['rows'] if mid(r['epsilon'])==0]
        x=np.array([-mid(r['nu']) for r in rows])
        delta=np.array([mid(r['center'][2])-mid(b['center'][2]) for r,b in zip(rows,base)])
        change=np.array([100*(mid(r['C'])/mid(b['C'])-1) for r,b in zip(rows,base)])
        label=r'$\epsilon=-1/2$' if eps<0 else r'$\epsilon=+1/2$'
        ax[0].plot(x,delta,lw=1.7,marker='o',ms=4,color=colors[eps],label=label)
        ax[1].plot(x,change,lw=1.7,marker='o',ms=4,color=colors[eps],label=label)
    for a in ax:
        a.axhline(0,color='#666666',lw=.8,ls='--');a.grid(axis='y',alpha=.16)
        a.set_xlim(0,29);a.set_xlabel(r'Distance along driver interval, $-\nu$')
        a.legend(fontsize=10,loc='lower left')
    ax[0].set(title='A. Displacement from the original cusp arc',ylabel=r'$\mu_*(\nu,\epsilon)-\mu_*(\nu,0)$')
    ax[0].annotate('Q is fixed exactly',xy=(0,0),xytext=(3,.0075),fontsize=10,
                   arrowprops={'arrowstyle':'->','color':'#555555'},color='#333333')
    ax[1].set(title='B. Change in the leading width coefficient',ylabel=r'$100\,[C(\nu,\epsilon)/C(\nu,0)-1]$ (%)')
    ax[1].legend(fontsize=10,loc='center left')
    fig.text(.5,.055,'Points are certified at 7 driver values; connecting lines guide the eye. The continuum theorem uses 232 parameter boxes.',ha='center',fontsize=9)
    fig.text(.5,.020,r'$W(\ell,\nu,\epsilon)=C(\nu,\epsilon)\ell^{3/2}+O(\ell^2)$; panel B concerns the leading coefficient.',ha='center',fontsize=9)
    for e in ('png','svg'):fig.savefig(out/f'pinned_cusp_sheet.{e}',dpi=190,metadata={'Date':None} if e=='svg' else {})
    plt.close(fig)
    fig,ax=plt.subplots(1,2,figsize=(12,5.6))
    fig.subplots_adjust(left=.09,right=.98,bottom=.23,top=.79,wspace=.30)
    fig.suptitle('Finite fold regions: driver widening and amplitude narrowing',fontsize=15,y=.97)
    nu_colors={0:'#176888',-15:'#707777',-29:'#B76A24'}
    for nu in (0,-29):
        i=next(i for i,m in enumerate(folds['models']) if mid(m['nu'])==nu and mid(m['epsilon'])==0)
        rows=[r for r in folds['samples'] if r['model']==i]
        x=np.r_[0,[mid(r['ell'])*1e6 for r in rows]]
        high=np.r_[0,[mid(r['upper']['root_enclosures'][1])*1e9 for r in rows]]
        low=np.r_[0,[mid(r['lower']['root_enclosures'][1])*1e9 for r in rows]]
        ax[0].fill_between(x,low,high,color=nu_colors[nu],alpha=.12)
        ax[0].plot(x,high,color=nu_colors[nu],lw=1.7,marker='o',ms=3,label=rf'$\nu={nu}$')
        ax[0].plot(x,low,color=nu_colors[nu],lw=1.7,marker='o',ms=3)
    ax[0].text(.26,0,'3 real roots',fontsize=11,color='#34444B',ha='center')
    ax[0].set(title=r'A. Three-root regions at $\epsilon=0$',xlabel=r'$\ell$ ($\times10^{-6}$)',ylabel=r'$m$ ($\times10^{-9}$)',xlim=(0,1))
    ax[0].legend(loc='upper left',fontsize=10)
    for nu in (0,-15,-29):
        rows=[r for r in folds['comparisons'] if mid(r['nu'])==nu]
        x=[mid(r['ell'])*1e6 for r in rows]
        y=[mid(r['W_percent_plus_half_vs_minus_half']) for r in rows]
        ax[1].plot(x,y,color=nu_colors[nu],lw=1.7,marker='o',ms=4,label=rf'$\nu={nu}$')
    ax[1].set(title=r'B. Width change: $\epsilon=-1/2\ \to\ +1/2$',xlabel=r'$\ell$ ($\times10^{-6}$)',
              ylabel=r'$100\,[W_{+1/2}/W_{-1/2}-1]$ (%)',xlim=(0,1),ylim=(-.054,-.0405))
    ax[1].legend(loc='lower center',ncol=3,fontsize=9)
    for a in ax:a.grid(axis='y',alpha=.16)
    fig.text(.5,.055,'Each section uses its own exact cusp center, without rescaling the controls. Points are finite-width certificates.',ha='center',fontsize=9)
    fig.text(.5,.020,'Eight positive offsets per curve; connecting lines are visual aids. Certified interval widths are below plot resolution.',ha='center',fontsize=9)
    for e in ('png','svg'):fig.savefig(out/f'finite_fold_comparison.{e}',dpi=190,metadata={'Date':None} if e=='svg' else {})
    plt.close(fig)
    report={'status':'two_figures_generated_from_certified_points','proof_input':False,
            'input_sha256':{'point_certificates.json':sha(pp),'fold_samples.json':sha(fp)},
            'source_sha256':sha(__file__),'files':{p.name:sha(p) for p in paths},
            'interpretation':'Point/error enclosures are certified; interpolating lines and binary64 plotting coordinates are explanatory, not proof inputs.'}
    (out/'metadata.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
