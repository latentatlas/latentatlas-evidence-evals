#!/usr/bin/env python3
"""Scientific figure of proved finite-window bounds, not a sampled optimum."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
from fractions import Fraction as F
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);a=ap.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
    mp.mp.dps=80;M0=mp.mpf('2e-5');M1=mp.mpf('2e-3');km=mp.mpf('9.593e-54');kp=mp.mpf('1.488e-53');c4lo=mp.mpf('2.49203004e-39')
    values=[]
    for i in range(201):
        M=M0*mp.power(M1/M0,mp.mpf(i)/200)
        values.append({'M':mp.nstr(M,50),'ratio_deviation_lower_ppm':mp.nstr(-1e6*km/(c4lo*M*M),50),
          'ratio_deviation_upper_ppm':mp.nstr(1e6*kp/(c4lo*M*M),50),'absolute_error_upper':mp.nstr(kp/M**6,50),
          'fourth_term_lower':mp.nstr(c4lo/M**4,50)})
    x=np.array([float(r['M']) for r in values]);lo=np.array([float(r['ratio_deviation_lower_ppm']) for r in values]);hi=np.array([float(r['ratio_deviation_upper_ppm']) for r in values])
    err=np.array([float(r['absolute_error_upper']) for r in values]);term=np.array([float(r['fourth_term_lower']) for r in values])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(13,5.8));fig.subplots_adjust(left=.075,right=.975,bottom=.27,top=.77,wspace=.28)
    fig.suptitle('A quantified fourth-order law for the fixed theta problem',fontsize=17,y=.96)
    fig.text(.5,.87,r'$P_4(M)=\delta_0+C_2/M^2+C_4/M^4$     |     $2\times10^{-5}\leq M\leq2\times10^{-3}$',ha='center',fontsize=13)
    ax=axes[0];ax.set_xscale('log');ax.fill_between(x,lo,hi,color='#50A29B',alpha=.28,label='proved enclosure')
    ax.plot(x,lo,color='#287A76',lw=1.8);ax.plot(x,hi,color='#287A76',lw=1.8);ax.axhline(0,color='#515C67',ls='--',lw=1)
    ax.set_title('Fourth-order correction: guaranteed deviation',fontsize=12,pad=16)
    ax.set_ylabel(r'$10^6\left[\frac{\delta(M)-\delta_0-C_2/M^2}{C_4/M^4}-1\right]$')
    ax.set_xlabel(r'Slope budget $M$');ax.set_xlim(x[0],x[-1]);ax.grid(alpha=.2)
    ax.text(.08,.87,'At the left endpoint:\n−9.624 to +14.928 ppm',transform=ax.transAxes,fontsize=10)
    ax.legend(loc='lower right',frameon=False,fontsize=10)
    ax=axes[1];ax.loglog(x,term,color='#D08034',lw=2,label=r'lower bound for $C_4/M^4$')
    ax.loglog(x,err,color='#287A76',lw=2,label=r'upper bound for $|\delta-P_4|$')
    ax.set_title('The error bound is smaller than the correction',fontsize=12,pad=16)
    ax.set_xlabel(r'Slope budget $M$');ax.set_ylabel('Amplitude');ax.set_xlim(x[0],x[-1]);ax.grid(alpha=.2,which='both');ax.legend(frameon=False,fontsize=10)
    fig.text(.075,.135,'At M = 2×10⁻⁵:  |δ − P₄| < 2.325×10⁻²⁵, less than 0.001493% of the fourth-order term.',fontsize=11)
    fig.text(.075,.075,'Exact coefficients are used in the theorem. Curves display bounds, not computed values of the optimum.\nThe finite window is essential; this figure does not establish an all-large-M sixth-order asymptotic law.',fontsize=10,color='#515C67')
    paths=[]
    for ext in ['png','svg']:
        p=a.outdir/('effective_fourth_order.'+ext)
        if p.exists():raise FileExistsError(p)
        fig.savefig(p,dpi=180,facecolor='white',metadata={'Date':None} if ext=='svg' else {})
        paths.append(p)
    out={'source_sha256':sha(__file__),'certificate_sha256':sha(HERE/'results/certificate.json'),
      'precision_digits':80,'bound_curves':values,'finite_window_only':True,'not_sampled_optimum_values':True,
      'figures':{p.name:sha(p) for p in paths}}
    (HERE/'results/plot_data.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Scientific bound figure written',len(values),'points')
if __name__=='__main__':main()
