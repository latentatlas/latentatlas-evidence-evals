#!/usr/bin/env python3
"""Scientific illustration and readable table; plot samples are not certificates."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,os,tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);args=ap.parse_args()
    out=args.outdir
    figures=out/'figures';results=out/'results'
    for directory in [figures,results]:directory.mkdir(parents=True,exist_ok=True)
    for dest in [figures/'finite_optimum.png',figures/'finite_optimum.svg',
                 results/'plot_data.json',results/'NUMERICAL_TABLE.md']:
        if dest.exists():raise FileExistsError(dest)
    with tempfile.TemporaryDirectory(prefix='r21-matplotlib-') as config:
        os.environ['MPLCONFIGDIR']=config
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
        import numpy as np
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
            'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'r21-finite-optimum'})
        certificate=HERE/'results/certificate.json';cert=json.loads(certificate.read_text())
        widths=np.geomspace(.005,.2,360);beta=.25
        shifts=-beta*widths**2/(1+np.sqrt(1-3*beta**2*widths**2))
        dual=shifts**2+beta*shifts**3+beta*shifts/2+widths**2/3+beta*shifts*widths**2
        target=.5-2*shifts**2-2*beta*shifts**3-2*widths**2/3-2*beta*shifts*widths**2
        A=.125/target;M=A/widths;scaled=M*M*(A-.25)
        for row in cert['rows']:
            av=float(row['a'].split('/')[0])/float(row['a'].split('/')[1])
            dv=-beta*av*av/(1+np.sqrt(1-3*beta*beta*av*av))
            assert abs(dv-float(row['approximate_midpoints']['center_shift']))<1e-16
        fig,axs=plt.subplots(1,3,figsize=(15,4.4),layout='constrained')
        blue='#2166ac';orange='#c65a13';dark='#263645'
        a=.2;d=float(cert['rows'][0]['approximate_midpoints']['center_shift'])
        x=np.linspace(-1,1,1801)
        s=1-np.clip((x-(d-.5))/a+1,0,2)+np.clip((x-(d+.5))/a+1,0,2)
        base=np.where(abs(x)>.5,1.,-1.)
        axs[0].plot(x,base,color='#8a929b',ls=':',lw=1.6,label='Unrestricted sign profile')
        axs[0].plot(x,s,color=blue,lw=2.4,label='Exact finite-slope optimum')
        for center in [d-.5,d+.5]:
            axs[0].axvspan(center-a,center+a,color=blue,alpha=.07)
            axs[0].plot(center,0,'o',color=orange,ms=5)
        axs[0].set(xlabel='$x$',ylabel='Unit profile $s_a(x)$',ylim=(-1.2,1.25),
                   title='(a) Two coupled transitions, $a=0.2$')
        axs[0].legend(loc='upper center',bbox_to_anchor=(.5,.98),fontsize=8.4,frameon=True)
        axs[1].plot(widths,shifts,color=blue,lw=2.2,label='Common center shift $d(a)$')
        axs[1].plot(widths,dual,color=orange,lw=2.2,label='Dual coefficient $b(a)$')
        axs[1].plot(widths,-widths**2/8,color=blue,ls=':',lw=1.6,label='$-a^2/8$')
        axs[1].plot(widths,61*widths**2/192,color=orange,ls=':',lw=1.6,label='$61a^2/192$')
        axs[1].set(xlabel='Half-width $a$',ylabel='Parameter value',title='(b) Centers and dual coefficient move')
        axs[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        axs[1].legend(fontsize=8.4,loc='upper left')
        axs[2].plot(M,scaled,color=blue,lw=2.2,label='Exact optimum curve')
        axs[2].axhline(1/48,color=orange,ls='--',lw=1.7,label='Leading coefficient $1/48$')
        markers_x=[float(r['approximate_midpoints']['slope_budget']) for r in cert['rows']]
        markers_y=[float(r['approximate_midpoints']['scaled_amplitude_excess']) for r in cert['rows']]
        axs[2].scatter(markers_x,markers_y,color=dark,s=23,zorder=4,label='Rationally enclosed samples')
        axs[2].set(xscale='log',xlabel='Slope budget $M$',ylabel=r'$M^2[\delta(M)-1/4]$',
                   title='(c) Agreement with the earlier leading law')
        axs[2].xaxis.set_major_locator(FixedLocator([2,5,10,20,50]))
        axs[2].xaxis.set_major_formatter(FixedFormatter(['2','5','10','20','50']))
        axs[2].xaxis.set_minor_formatter(NullFormatter())
        axs[2].legend(fontsize=8.2,loc='upper right')
        for ax in axs:ax.grid(alpha=.16)
        fig.suptitle('Exact finite-slope design with one preserved moment',fontsize=15,fontweight='bold',color=dark)
        fig.supxlabel('Polynomial verification example on [-1,1]; not a theta-family certificate.',fontsize=9,color='#555555')
        fig.savefig(figures/'finite_optimum.png',dpi=180)
        fig.savefig(figures/'finite_optimum.svg',metadata={'Date':None})
        plt.close(fig)
        data={'certificate_sha256':sha(certificate),'plotter_sha256':sha(Path(__file__)),
              'scope':'Floating-point illustration; rigorous values are in the rational certificate.',
              'samples':[{'a':float(a),'d':float(d),'b':float(b),'M':float(m),'scaled_excess':float(c)}
                         for a,d,b,m,c in zip(widths,shifts,dual,M,scaled)],
              'figures':{p.name:sha(p) for p in sorted(figures.iterdir()) if p.suffix in ['.png','.svg']},
              'matplotlib':matplotlib.__version__,'numpy':np.__version__}
        (results/'plot_data.json').write_text(json.dumps(data,indent=2)+'\n')
    table=['# R21 — İki geçişli örneğin yaklaşık gösterim tablosu','',
           'Aşağıdaki sayılar rasyonel aralıkların yuvarlatılmış orta noktalarıdır.',
           'Kesin sonuçlar `certificate.json` içindeki kesir uçlarıdır; bu ondalıklar aralık değildir.','',
           '| a | Ortak merkez kayması d | Dual b | Optimum A=δ(M) | M | M²(A−1/4) |',
           '|---|---:|---:|---:|---:|---:|']
    for row in cert['rows']:
        v=row['approximate_midpoints']
        table.append('| '+row['a']+' | '+' | '.join(v[k] for k in ['center_shift','dual_coefficient','amplitude','slope_budget','scaled_amplitude_excess'])+' |')
    table+=['','Limit: M²(δ(M)−1/4) → 1/48 ≈ 0.0208333333333333333.',
            'Genel sonlu-geçişli teorem bütün yeterince büyük M içindir; bu örnekte',
            'uniform analitik kontrol bütün M≥M(1/5) aralığını kapsar.','']
    (results/'NUMERICAL_TABLE.md').write_text('\n'.join(table))
    print(json.dumps({'status':'scientific_figure_and_table_created','samples':len(data['samples'])}))
if __name__=='__main__':main()
