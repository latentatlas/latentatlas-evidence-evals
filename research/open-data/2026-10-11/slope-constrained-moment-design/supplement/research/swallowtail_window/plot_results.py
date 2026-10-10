#!/usr/bin/env python3
"""Scientific figures from finite certificates; no generative imagery."""
import json,sys
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Patch
from model_v2 import *


def mid(v):
    a,e=v['mid_man_exp'];return float(Q(a)*Q(2)**e)
def rmid(v):return float((Q(v[0])+Q(v[1]))/2)


def main():
    ctx.dps=90;out=HERE/'figures';out.mkdir(exist_ok=True)
    if (out/'metadata.json').exists():raise FileExistsError('Figures already recorded')
    names=['model_v2.json','window_certificate.json','sample_certificate.json','sample_check.json','chart_certificate.json','chart_check.json']
    data={n:json.loads((HERE/'results'/n).read_text()) for n in names}
    m=Model(data['model_v2.json']);cert=data['window_certificate.json'];sc=data['sample_check.json'];samples=data['sample_certificate.json'];chart=data['chart_certificate.json']
    L=arb(2)**-24;r=arb(2)**-12
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,
        'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,
        'svg.fonttype':'none','savefig.facecolor':'white'})
    files={}
    def save(fig,name):
        for ext in ('png','svg'):
            p=out/(name+'.'+ext);fig.savefig(p,dpi=190);files[p.name]=sha(p)
        plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(12.6,5.4),sharex=True,sharey=True)
    fig.subplots_adjust(left=.07,right=.98,bottom=.21,top=.76,wspace=.16)
    fig.suptitle('Three finite regimes near the constructed order-four zero',y=.97,fontsize=17,fontweight='bold')
    fig.text(.5,.865,r'Original controls; fixed modified kernel. $L=2^{-24}$, $s=t-t_Q$, $g=24G/G_4(Q)$.',ha='center',fontsize=11)
    colors=['#396f9e','#b97b22','#2d7c64'];x=np.linspace(-2,2,241)
    for ax,row,color in zip(axes,cert['open_witnesses'],colors):
        p=list(map(restore,row['center']));y=[]
        for z in x:y.append(float((m.derivatives([r*arb(str(z))]+p,0)[0]/(L*L)).mid()))
        ax.plot(x,y,color=color,lw=2);ax.axhline(0,color='#303030',lw=.9)
        if row['count']:
            roots=[z for z in sc['records'] if z['name'].startswith(row['name']+'_root_')]
            ax.plot([rmid(z['root_enclosures'][0])/float(r) for z in roots],[0]*len(roots),'o',color=color,ms=7)
        ax.set(title=str(row['count'])+' simple real roots',xlabel=r'$s/\sqrt{L}$',xlim=(-2,2),ylim=(-2,8))
        label={'zero':r'$\ell=-L,\ m=0,\ \nu=0$','two':r'$\ell=-L,\ m=-L^2,\ \nu=0$','four':r'$\ell=L,\ m=0,\ \nu=0$'}[row['name']]
        ax.text(.5,.93,label,transform=ax.transAxes,ha='center',fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
    axes[0].set_ylabel(r'$g(s)/L^2$')
    fig.text(.5,.06,r'Each center belongs to an open box with control radii $(L/128,L^2/256,L^2/256)$.'+'\n'+r'Counts hold throughout those boxes in the full window $|s|\leq2^{-7}$. Curves are Taylor midpoint visualizations.',ha='center',fontsize=9,color='#444')
    save(fig,'finite_root_regimes')

    fig,ax=plt.subplots(figsize=(9.5,7.1))
    fig.subplots_adjust(left=.10,right=.965,bottom=.215,top=.83)
    fig.suptitle('Certified 0 / 2 / 4 root regions in a swallowtail section',y=.98,fontsize=16,fontweight='bold')
    fig.text(.5,.912,r'Fixed original $\lambda-\lambda_Q=2^{-24}$; an explicit affine chart of $(\mu-\mu_Q,\nu)$.',ha='center',fontsize=10.5)
    palette=['#e7e7e7','#c8dced','#f4ddb0','#aed2c0'];cmap=ListedColormap(palette)
    values=np.array([[{None:0,0:1,2:2,4:3}[chart['cells'][i][j]['count']] for i in range(64)] for j in range(56)])
    ax.pcolormesh(np.linspace(-4,4,65),np.linspace(-1.5,5.5,57),values,cmap=cmap,norm=BoundaryNorm(np.arange(-.5,4.5),4),shading='flat',rasterized=False)
    E=np.array([[mid(v) for v in row] for row in chart['affine_matrix']]);Einv=np.linalg.inv(E);lf=float(L);rf=float(r)
    def xy(mu,nu):
        w,v=Einv@np.array([mu,nu]);return v/(rf**3),w/(lf**2)+.75
    pts=[xy(mid(z['root_enclosures'][0]),mid(z['root_enclosures'][1])) for z in samples['fold_samples']]
    ax.plot(*np.array(pts).T,color='#333',lw=1.8,label='Fold boundary (certified samples)')
    for z in sc['records']:
        if z['name'].startswith('cusp_'):
            a,b=xy(rmid(z['root_enclosures'][1]),rmid(z['root_enclosures'][2]));ax.plot(a,b,'*',ms=15,color='#b34245',zorder=5)
            ax.annotate('cusp',(a,b),(a*.74,-1.21),ha='center',fontsize=10,color='#943a3c',arrowprops={'arrowstyle':'->','lw':.8,'color':'#943a3c'})
        if z['name']=='two_double_roots':
            a,b=xy(rmid(z['root_enclosures'][2]),rmid(z['root_enclosures'][3]));ax.plot(a,b,'D',ms=6,color='#222',zorder=5)
            ax.annotate('two distinct double roots',(a,b),(.9,3.28),ha='left',fontsize=10,arrowprops={'arrowstyle':'->','lw':.8})
    for x0,y0,s in [(0,4.6,'0 roots'),(-3,1.0,'2 roots'),(0,.92,'4 roots')]:
        ax.text(x0,y0,s,ha='center',va='center',fontsize=15,fontweight='bold',color='#233c40')
    ax.set(xlabel=r'$\alpha$',ylabel=r'$\beta$',xlim=(-4,4),ylim=(-1.5,5.5))
    handles=[Patch(facecolor=palette[i],label=s) for i,s in enumerate(['Unresolved cell','0 roots','2 roots','4 roots'])]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.53,.115),ncol=4,frameon=False,fontsize=9)
    fig.text(.5,.038,'2,804 closed cells have a proved root count; 780 gray cells remain unresolved by this grid.\nFold points, both cusps and the double-fold intersection are certified. Lines between fold samples are visual guides.',ha='center',fontsize=9,color='#444')
    save(fig,'certified_swallowtail_section')
    meta={'status':'scientific_figures_from_certified_data','source_sha256':sha(__file__),
        'input_sha256':{n:sha(HERE/'results'/n) for n in names},'files':files,
        'png_dimensions':{'finite_root_regimes':[2394,1026],'certified_swallowtail_section':[1805,1349]},
        'scope':'Root profiles are midpoint Taylor illustrations with certified root markers. Phase colors are whole-cell certificates. The display chart is explicitly affine in original controls and is not an unknown normal-form coordinate transformation.'}
    with (out/'metadata.json').open('x') as f:json.dump(meta,f,indent=2);f.write('\n')
    print('Two PNG/SVG figure pairs recorded',flush=True)


if __name__=='__main__':main()
