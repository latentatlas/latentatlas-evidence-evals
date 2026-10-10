#!/usr/bin/env python3
"""Scientific graph of the global error bound and an adaptive-prefix upper bound."""
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
    ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);a=ap.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
    mp.mp.dps=80;M0=mp.mpf('2e-5');eps=mp.mpf(1)/4096;delta_lower=mp.mpf('0.00000000091787079603827')
    K=mp.mpf('1.488e-53');c4=mp.mpf('2.49203004e-39');records=[]
    for i in range(241):
        M=M0*mp.power(10,mp.mpf(6)*i/240)
        records.append({'M':mp.nstr(M,50),'relative_error_percent_upper':mp.nstr(100*K/(c4*M*M),50),
              'active_root_coordinate_upper':mp.nstr(max(mp.mpf(1),mp.log(eps*M/delta_lower)/4),50)})
    x=np.array([float(r['M']) for r in records]);err=np.array([float(r['relative_error_percent_upper']) for r in records]);cut=np.array([float(r['active_root_coordinate_upper']) for r in records])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(1,2,figsize=(13,5.8));fig.subplots_adjust(left=.08,right=.98,bottom=.26,top=.77,wspace=.3)
    fig.suptitle('The fixed theta problem: a uniform fourth-order error bound',fontsize=16,y=.96)
    fig.text(.5,.865,r'$|\delta(M)-P_4(M)|<1.488\times10^{-53}/M^6$ for every $M\geq2\times10^{-5}$',ha='center',fontsize=13)
    for aa in ax:
        aa.set_xscale('log');aa.axvspan(float(M0),.002,color='#D6DBE0',alpha=.5)
        aa.set_xlim(x[0],x[-1]);aa.grid(alpha=.2);aa.set_xlabel(r'Slope budget $M$')
    ax[0].set_yscale('log');ax[0].plot(x,err,color='#237A74',lw=2.2)
    ax[0].set_title('Guaranteed error relative to the fourth-order term',fontsize=12,pad=14)
    ax[0].set_ylabel(r'Upper bound for $100\,|\delta-P_4|/(C_4/M^4)$  (%)')
    ax[0].text(.04,.08,'Gray: the previous finite window',transform=ax[0].transAxes,fontsize=10)
    ax[1].plot(x,cut,color='#C77930',lw=2.2);ax[1].axhline(1,color='#59646F',lw=1,ls='--')
    ax[1].set_title('A finite prefix can grow with the budget',fontsize=12,pad=14)
    ax[1].set_ylabel('Upper bound on the included root coordinate')
    ax[1].text(.05,.86,r'$\max\{1,\,\frac{1}{4}\log(\varepsilon M/\delta_{0,\mathrm{lower}})\}$'+'\n'+r'$\varepsilon=2^{-12}$',transform=ax[1].transAxes,fontsize=12)
    fig.text(.08,.13,'The upper budget restriction is removed. At each width only finitely many tail switches are included.',fontsize=11)
    fig.text(.08,.07,'Curves show proved bounds, not sampled optimal values. The right curve bounds the adaptive construction,\nnot the location of every zero or the support of the kernel. A sixth-order coefficient is not asserted.',fontsize=10,color='#515C67')
    paths=[]
    for ext in ['png','svg']:
        p=a.outdir/('global_fourth_order.'+ext)
        if p.exists():raise FileExistsError(p)
        fig.savefig(p,dpi=180,facecolor='white',metadata={'Date':None} if ext=='svg' else {});paths.append(p)
    data={'source_sha256':sha(__file__),'certificate_sha256':sha(HERE/'results/certificate.json'),
      'precision_digits':80,'curve_points':records,'global_theorem':True,'sampled_optimum':False,'root_coordinate_is_upper_bound':True,
      'figures':{p.name:sha(p) for p in paths}}
    (HERE/'results/plot_data.json').write_text(json.dumps(data,indent=2)+'\n');print('Global scientific bound figure written',len(records))
if __name__=='__main__':main()
