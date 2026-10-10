#!/usr/bin/env python3
"""Separate a proved uniform coefficient band from a diagnostic sampled trend."""
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
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);args=ap.parse_args();args.outdir.mkdir(parents=True,exist_ok=True)
    cp=HERE/'results/certificate.json';dp=HERE/'results/direct_check.json';d=json.loads(dp.read_text());mp.mp.dps=80
    points=d['runs'][1]['rows'];base=mp.mpf(points[-1]['coefficients']['C4']);data=[]
    for row in points:
        nu=mp.mpf(row['nu']);c4=mp.mpf(row['coefficients']['C4'])
        data.append({'nu':mp.nstr(nu,45),'C4':mp.nstr(c4,45),'relative_C4_change_ppm':mp.nstr(10**6*(c4/base-1),45)})
    x=np.array([float(mp.mpf(r['nu'])*10**6) for r in data]);c=np.array([float(mp.mpf(r['C4'])*10**39) for r in data]);change=np.array([float(r['relative_C4_change_ppm']) for r in data])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(1,2,figsize=(13,5.8));fig.subplots_adjust(left=.07,right=.98,bottom=.27,top=.77,wspace=.27)
    fig.suptitle('A short theta cusp arc: uniform positivity and sampled variation',fontsize=16,y=.96)
    fig.text(.5,.865,r'$-2^{-16}\leq\nu\leq0$   |   the fourth-order error bound holds for every $M\geq2\times10^{-5}$',ha='center',fontsize=12.5)
    for a in ax:
        a.set_xlim(x[0],x[-1]);a.set_xlabel(r'Cusp driver $10^6\nu$');a.grid(alpha=.2)
    ax[0].fill_between([x[0],0],[2.47,2.47],[2.52,2.52],color='#237A74',alpha=.35)
    ax[0].axhline(2.47,color='#237A74',lw=1);ax[0].axhline(2.52,color='#237A74',lw=1)
    ax[0].scatter(x,c,color='#173B4A',s=30,zorder=3)
    ax[0].set_ylim(0,2.8);ax[0].set_ylabel(r'$10^{39} C_4(\nu)$');ax[0].set_title('Proved band for every point on the arc',pad=13)
    ax[0].text(.07,.63,r'$2.47\times10^{-39}<C_4(\nu)<2.52\times10^{-39}$'+'\n\nThe entire band stays above zero.',transform=ax[0].transAxes,fontsize=12)
    ax[1].plot(x,change,'o-',color='#C77930',lw=1.8,markersize=6)
    ax[1].set_ylim(-2.45,.25);ax[1].set_ylabel(r'$10^6\,[C_4(\nu)/C_4(0)-1]$  (ppm)')
    ax[1].set_title('Independent numerical samples: magnified change',pad=13)
    fig.text(.07,.135,'The common bound covers a continuous interval. The sample-to-sample trend is not a monotonicity theorem.',fontsize=11)
    fig.text(.07,.07,'Each cusp point permits its own design and its own exact coefficients. This is a short subarc, not the whole [−29, 0] curve.\nDots use direct numerical integral solves; the uniform band comes from the separate analytic and interval proof.',fontsize=10,color='#515C67')
    figs={}
    for ext in ['png','svg']:
        out=args.outdir/('cusp_uniformity.'+ext)
        if out.exists():raise FileExistsError(out)
        fig.savefig(out,dpi=180,facecolor='white',metadata={'Date':None} if ext=='svg' else {});figs[out.name]=sha(out)
    result={'source_sha256':sha(__file__),'certificate_sha256':sha(cp),'direct_check_sha256':sha(dp),'precision_digits':80,
      'points':data,'uniform_C4_band':['2.47e-39','2.52e-39'],'band_is_enclosure_not_exact_range':True,
      'trend_is_diagnostic_not_monotonicity_proof':True,'figures':figs}
    (HERE/'results/plot_data.json').write_text(json.dumps(result,indent=2)+'\n');print('R27 scientific figure written',len(data))
if __name__=='__main__':main()
