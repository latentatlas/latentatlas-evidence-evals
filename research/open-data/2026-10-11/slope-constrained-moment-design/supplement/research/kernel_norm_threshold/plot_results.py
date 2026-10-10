#!/usr/bin/env python3
"""Scientific figures; exact rational data are converted only for rendering."""
import hashlib
import json
import struct
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.dont_write_bytecode=True
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def midpoint(v):
    m,e=v['mid_man_exp'];return float(Q(m)*Q(2)**e)


def save(fig,name,directory,metadata):
    paths=[directory/(name+'.'+ext) for ext in ('png','svg')]
    need=not any(p.exists() for p in paths)
    if not need:raise FileExistsError(name)
    fig.savefig(paths[0],dpi=200)
    fig.savefig(paths[1],metadata={'Date':None});plt.close(fig)
    metadata['files'].update({p.name:sha(p) for p in paths})
    metadata['png_dimensions'][name]=list(struct.unpack('>II',paths[0].read_bytes()[16:24]))


def main():
    directory=HERE/'figures';directory.mkdir(exist_ok=True)
    if (directory/'metadata.json').exists():raise FileExistsError('Existing plot metadata')
    cp=HERE/'results/threshold_certificate.json';rp=HERE/'results/threshold_check.json'
    op=HERE.parent/'kernel_design_principle/results/candidate_check.json'
    c=json.loads(cp.read_text());r=json.loads(rp.read_text());old=json.loads(op.read_text())
    lo,hi=map(Q,r['readable_minimum_norm_bracket']);ol,ou=map(Q,old['readable_minimum_norm_bracket'])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none','svg.hashsalt':'r12-norm-threshold'})
    blue,muted,grey='#244C78','#667585','#CDD4DE'
    metadata={'status':'scientific_figures_from_certified_bracket_and_exact_design_formula',
              'source_sha256':sha(__file__),
              'input_sha256':{'threshold_certificate.json':sha(cp),'threshold_check.json':sha(rp),'R11_candidate_check.json':sha(op)},
              'files':{},'png_dimensions':{},'readable_bracket':r['readable_minimum_norm_bracket']}
    fig,axes=plt.subplots(2,1,figsize=(10.5,6.1),layout='constrained',gridspec_kw={'height_ratios':[1,1.15]})
    fig.suptitle('Certified distance to an order-four zero at the same Q',fontsize=16,weight='bold',x=.08,ha='left')
    ax=axes[0];ax.set_xscale('log');ax.set_xlim(2e-10,4e-7);ax.set_ylim(-.55,1.55)
    ax.hlines(1,float(ol),float(ou),color=grey,linewidth=12)
    ax.vlines([float(ol),float(ou)],.83,1.17,color=muted,linewidth=1.3)
    ax.hlines(0,float(lo),float(hi),color=blue,linewidth=12)
    ax.vlines([float(lo),float(hi)],-.18,.18,color=blue,linewidth=1.8)
    ax.set_yticks([0,1],['R12','R11']);ax.tick_params(axis='y',length=0)
    ax.text(np.sqrt(float(ol*ou)),1.22,'First bracket: upper / lower ≈ 601.04',ha='center',color=muted,fontsize=10)
    ax.text(float(lo)*1.18,-.03,'New bracket; enlarged below',ha='left',va='center',color=blue,fontsize=10)
    ax.xaxis.set_major_locator(LogLocator(base=10,numticks=5))
    ax.set_xlabel(r'Relative amplitude budget $\delta=\|h\|_\infty$ (log scale)')
    ax.set_title('Same Q, same norm, no frequency or derivative constraint',loc='left',fontsize=10,color=muted,pad=7)
    for side in ('top','right','left'):ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#9EABB8')
    shift=Q('9.178707960e-10');scale=Q('1e-20')
    L,U=float((lo-shift)/scale),float((hi-shift)/scale)
    ax=axes[1];ax.set_xlim(0,12);ax.set_ylim(0,1)
    ax.fill_between([0,L],.28,.51,color='#F2DEDC')
    ax.fill_between([L,U],.28,.51,color='#B9CDE2')
    ax.fill_between([U,12],.28,.51,color='#D9EAE2')
    ax.vlines([L,U],.19,.66,color=blue,linewidth=1.5)
    ax.text(L,.73,'L = 9.1787079603827 × 10⁻¹⁰',ha='right',color=blue,fontsize=10)
    ax.text(U,.73,'U = 9.1787079608363 × 10⁻¹⁰',ha='left',color=blue,fontsize=10)
    ax.text(L/2,.39,'Excluded',ha='center',va='center',fontsize=10,color='#854C49')
    ax.text((L+U)/2,.39,'Threshold enclosed',ha='center',va='center',fontsize=10,weight='bold',color=blue)
    ax.text((U+12)/2,.39,'Feasible budget',ha='center',va='center',fontsize=10,color='#336657')
    ax.text(6,.04,r'$(U-L)/L < 5\times10^{-11}$',ha='center',va='bottom',color=blue,fontsize=12)
    ax.set_xlabel(r'Enlarged coordinate: $(\delta-9.178707960\times10^{-10})/10^{-20}$')
    ax.set_yticks([])
    for side in ('top','right','left'):ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#9EABB8')
    save(fig,'threshold_contraction',directory,metadata)
    metadata['threshold_contraction']={'zoom_shift':str(shift),'zoom_scale':str(scale),'zoom_endpoints':[L,U],
        'scope':'The log-scale mark represents a narrow interval, not a point-valued optimum. Lower-panel coordinates are an exact rational affine change before floating-point rendering.'}

    alpha=midpoint(c['alpha']);eta=midpoint(c['smoothing_width']);b=np.array(list(map(midpoint,c['breakpoints'])))
    w=np.array(list(map(midpoint,c['correction_weights'])));freq=np.array(c['correction_frequencies'])
    jump=-2*(-1.0)**np.arange(len(b))
    def design(u):
        u=np.asarray(u)
        Hplus=(1+np.tanh((u[:,None]-b)/eta))/2
        Hminus=(1+np.tanh((-u[:,None]-b)/eta))/2
        template=1+(Hplus+Hminus)@jump
        return -template+np.cos(2*u[:,None]*freq)@w/alpha
    u=np.unique(np.r_[np.linspace(0,.25,2500),np.concatenate([v+eta*np.linspace(-8,8,201) for v in b if v<.25])])
    u=u[(u>=0)&(u<=.25)]
    fig,axes=plt.subplots(1,2,figsize=(10.5,3.8),layout='constrained',gridspec_kw={'width_ratios':[1.65,1]})
    fig.suptitle('A smooth feasible multiplier near the minimum amplitude',fontsize=15,weight='bold',x=.08,ha='left')
    ax=axes[0];ax.plot(u,design(u),color=blue,linewidth=1.35)
    ax.set_xlim(0,.25);ax.set_ylim(-1.17,1.17);ax.set_xlabel('u (first part of the positive axis)')
    ax.set_ylabel(r'$h_c(u)/\alpha$');ax.set_title('Narrow transitions preserve the amplitude budget',loc='left',fontsize=10,color=muted)
    v=np.linspace(-6,6,401);j=3
    ax=axes[1];ax.plot(v,design(b[j]+eta*v),color=blue,linewidth=2)
    ax.set_xlim(-6,6);ax.set_ylim(-1.17,1.17)
    ax.set_xlabel(r'Local coordinate $(u-b_4)/\eta$');ax.set_title(r'One transition; $\eta=2^{-32}$',loc='left',fontsize=10,color=muted)
    for ax in axes:
        ax.axhline(0,color='#D9DFE5',linewidth=.7,zorder=0)
        ax.set_yticks([-1,0,1]);ax.grid(axis='y',color='#E5E9EF',linewidth=.6)
        for side in ('right','top'):ax.spines[side].set_visible(False)
        for side in ('bottom','left'):ax.spines[side].set_color('#9EABB8')
    save(fig,'smooth_near_minimum_design',directory,metadata)
    metadata['smooth_near_minimum_design']={'positive_knots':len(b),'display_u_interval':[0,.25],'local_knot_index_one_based':4,
        'smoothing_width':str(Q(1,2**32)),'coefficient_rendering':'Midpoints of the certified correction-weight intervals. Exact weights are defined by the moment system; the drawn samples are not a certificate.',
        'scope':'The narrow transitions are mathematically smooth. The amplitude norm does not constrain derivatives. The plot is not a root-region diagram.'}
    with (directory/'metadata.json').open('x') as stream:json.dump(metadata,stream,indent=2);stream.write('\n')
    print(json.dumps({'files':list(metadata['files']),'png_dimensions':metadata['png_dimensions']},indent=2))


if __name__=='__main__':main()
