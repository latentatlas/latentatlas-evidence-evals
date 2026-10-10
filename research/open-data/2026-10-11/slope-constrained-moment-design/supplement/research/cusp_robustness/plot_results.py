#!/usr/bin/env python3
"""Explanatory static figures from retained certificates; not proof inputs."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_width'))
from check_width import read


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mid(v):
    a=read(v);return float((a.lo+a.hi)/2)


def main():
    directory=HERE/'figures';directory.mkdir(exist_ok=True)
    targets=[directory/(name+'.'+ext) for name in ('uniform_robustness','pinned_direction') for ext in ('png','svg')]
    if any(p.exists() for p in targets) or (directory/'metadata.json').exists():raise FileExistsError('Figures already exist')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,
                        'svg.hashsalt':'R07-cusp-robustness','axes.titleweight':'bold'})
    rp=HERE/'results/rational_check.json';rr=json.loads(rp.read_text());assert rr['cells_checked']==58 and rr['joins_checked']==57
    raw=rr['checks'][::-1];centers=np.array([-(2*r['index']+1)/4 for r in raw]);edges=np.linspace(-29,0,59)
    from fractions import Fraction as Q
    displacement=np.array([max(float(Q(x)) for x in r['displacement']) for r in raw])
    low=np.array([float(Q(r['third'][0]))/(3*2.21**1.5) for r in raw])
    high=np.array([float(Q(r['third'][1]))/(3*1.80**1.5) for r in raw])
    fig,ax=plt.subplots(1,2,figsize=(12,5.3))
    fig.subplots_adjust(left=.09,right=.985,bottom=.24,top=.79,wspace=.27)
    fig.suptitle(r'Uniform guarantee for every fixed $\|h\|_\infty\leq10^{-18}$',fontsize=15,y=.98)
    ax[0].stairs(displacement*1e5,edges,color='#175b83',lw=2,fill=True,alpha=.30)
    ax[0].stairs(displacement*1e5,edges,color='#175b83',lw=1.4)
    ax[0].axhline(4,color='#444444',ls='--',lw=1,label=r'Proved common bound: $4\times10^{-5}$')
    ax[0].set(xlabel=r'Driver $\nu$',ylabel=r'Upper bound for $\|c_h-c\|_\infty$ ($\times10^{-5}$)',title='A. Cusp displacement',xlim=(-29,0),ylim=(0,4.35))
    ax[0].legend(loc='lower left',fontsize=9)
    ax[1].fill_between(edges,np.r_[low,low[-1]]*1e3,np.r_[high,high[-1]]*1e3,step='post',color='#168276',alpha=.28,label='Cellwise certified interval')
    ax[1].axhline(.3,color='#555555',ls='--',lw=1);ax[1].axhline(3,color='#555555',ls='--',lw=1)
    ax[1].set(xlabel=r'Driver $\nu$',ylabel=r'$-\partial_\nu W_h/\ell^{3/2}$ ($\times10^{-3}$)',title='B. Fold-width growth stays positive',xlim=(-29,0),ylim=(0,3.18))
    ax[1].legend(loc='upper right',fontsize=9)
    for a in ax:a.grid(axis='y',alpha=.15)
    fig.text(.5,.045,r'All $0<\ell\leq10^{-6}$; each section is centered at its own perturbed cusp. Bands are bounds, not sampled solutions.',ha='center',fontsize=9)
    for ext in ('png','svg'):fig.savefig(directory/f'uniform_robustness.{ext}',dpi=190,metadata={'Date':None} if ext=='svg' else {})
    plt.close(fig)
    pp=HERE/'results/pinned_cusp_certificate.json';p=json.loads(pp.read_text())
    qp=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';q=json.loads(qp.read_text())
    weights=np.array([mid(v) for v in p['weights']]);u=np.linspace(0,np.pi/2,501)
    h=np.sum(weights[:,None]*np.cos(2*np.arange(1,5)[:,None]*u[None,:]),axis=0)
    eps=np.linspace(-.5,.5,301)
    ratios=[]
    for n in (3,4):
        z=read(p['moment_response'][n])/read(q['root_derivative_enclosures'][n]);ratios.append((float(z.lo),float(z.hi)))
    fig,ax=plt.subplots(1,2,figsize=(12,5.3))
    fig.subplots_adjust(left=.09,right=.985,bottom=.24,top=.79,wspace=.27)
    fig.suptitle('A selected smooth direction keeps the exact quartic cusp fixed',fontsize=15,y=.98)
    upper=1+.5*np.abs(h);lower=1-.5*np.abs(h)
    ax[0].fill_between(u,lower,upper,color='#287f9b',alpha=.20,label=r'All $|\epsilon|\leq1/2$')
    ax[0].plot(u,1+.5*h,color='#145a80',lw=2,label=r'$\epsilon=+1/2$')
    ax[0].plot(u,1-.5*h,color='#b36b25',lw=2,label=r'$\epsilon=-1/2$')
    ax[0].axhline(1,color='#555',lw=.8,ls='--')
    ax[0].set(xlabel=r'$u$',ylabel=r'Kernel ratio $\Phi_\epsilon(u)/\Phi(u)$',title='A. A finite change of the kernel',xlim=(0,np.pi/2),ylim=(.42,1.58))
    ax[0].legend(fontsize=9,loc='upper left')
    for n,r,color,style in zip((3,4),ratios,('#145a80','#d27621'),('-','--')):
        val=1+eps*np.mean(r)
        ax[1].plot(eps,val,color=color,ls=style,lw=2.0,label=rf'$D_{n}G_\epsilon(Q)/D_{n}F(Q)$')
    ax[1].axhline(.7995,color='#555',ls=':',lw=1,label='Certified common lower bound: 0.7995')
    ax[1].set(xlabel=r'Amplitude $\epsilon$',ylabel='Derivative ratio at the exact cusp',title='B. Cusp nondegeneracy persists',xlim=(-.5,.5),ylim=(.76,1.24))
    ax[1].legend(fontsize=9,loc='upper right')
    for a in ax:a.grid(axis='y',alpha=.15)
    fig.text(.5,.05,r'One cofactor-defined direction $h_0$ and one cusp $Q$. This larger-amplitude result does not cover the entire cusp arc.',ha='center',fontsize=9)
    for ext in ('png','svg'):fig.savefig(directory/f'pinned_direction.{ext}',dpi=190,metadata={'Date':None} if ext=='svg' else {})
    plt.close(fig)
    meta={'status':'figures_generated_from_certificates','proof_input':False,
        'inputs':{str(path.relative_to(HERE.parent)):sha(path) for path in (rp,pp,qp)},'source_sha256':sha(Path(__file__)),
        'files':{p.name:sha(p) for p in targets},'uniform_cells':58,
        'pinning_display_weights':weights.tolist(),'pinning_display_ratio_intervals':ratios,
        'interpretation':'Uniform plots use all-cell certified bounds. Pinning plot uses rounded display values of exact cofactor-defined coefficients; exact cancellation is established by the formula, not by displayed rounded numbers.'}
    (directory/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')


if __name__=='__main__':main()
