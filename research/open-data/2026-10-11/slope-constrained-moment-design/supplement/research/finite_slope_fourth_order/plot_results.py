#!/usr/bin/env python3
"""High-precision sampling for scientific figures; these curves are illustrations."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import mpmath as mp

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);args=ap.parse_args()
    out=args.outdir;figdir=out/'figures';resdir=out/'results'
    for p in [figdir,resdir]:p.mkdir(parents=True,exist_ok=True)
    for p in [figdir/'fourth_order.png',figdir/'fourth_order.svg',resdir/'plot_data.json',resdir/'TABLE.md']:
        if p.exists():raise FileExistsError(p)
    certpath=HERE/'results/certificate.json';cert=json.loads(certpath.read_text())
    curves={}
    with mp.workdps(80):
        for case,amin,amax in [('two_switch','0.0005','0.2'),('negative_C4','0.0005','0.2'),('C2_only','0.000625','0.04')]:
            rows=[];lo=mp.mpf(amin);hi=mp.mpf(amax)
            for i in range(180):
                a=lo*(hi/lo)**(mp.mpf(i)/179)
                if case=='two_switch':
                    beta=mp.mpf(1)/4;d=-beta*a*a/(1+mp.sqrt(1-3*beta*beta*a*a))
                    S=mp.mpf(1)/2-2*d*d-2*beta*d**3-mp.mpf(2)/3*a*a-2*beta*d*a*a
                    f=mp.mpf(1)/8;C2=mp.mpf(1)/48
                elif case=='negative_C4':
                    S=mp.mpf(5)/2-a*a/3+mp.mpf(3)/10*a**4-mp.mpf(3)/7*a**6
                    f=mp.mpf(5)/8;C2=mp.mpf(1)/480
                else:
                    S=mp.mpf(11)/7-a*a/3-mp.mpf(8)/63*a**mp.mpf('3.5')
                    f=mp.mpf(11)/28;C2=mp.mpf(7)/2112
                A=f/S;M=A/a;scaled=M**4*(A-mp.mpf(1)/4-C2/M**2)
                rows.append({'a':float(a),'M':float(M),'scaled_fourth_residual':float(scaled)})
            curves[case]=rows
    with tempfile.TemporaryDirectory(prefix='r22-mpl-') as cfg:
        os.environ['MPLCONFIGDIR']=cfg
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FixedLocator,FixedFormatter,NullFormatter
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                             'axes.spines.right':False,'svg.hashsalt':'r22-fourth-order'})
        fig,axs=plt.subplots(1,3,figsize=(15,4.8),layout='constrained')
        blue='#2166ac';orange='#c65a13';dark='#263645'
        titles=['(a) Positive fourth-order coefficient','(b) Negative fourth-order coefficient',r'(c) $C^2$ only: no finite fourth-order limit']
        for ax,case,title in zip(axs,['two_switch','negative_C4','C2_only'],titles):
            rows=curves[case];xs=[r['M'] for r in rows];ys=[r['scaled_fourth_residual'] for r in rows]
            ax.plot(xs,ys,color=blue,lw=2.3,label='Exact optimum curve')
            markers=[r for r in cert['rows'] if r['case']==case]
            ax.scatter([float(r['approximate_midpoints']['slope_budget']) for r in markers],
                       [float(r['approximate_midpoints']['scaled_fourth_residual']) for r in markers],
                       color=dark,s=25,zorder=4,label='Rationally enclosed samples')
            if case=='two_switch':
                ax.axhline(253/49152,color=orange,ls='--',label=r'$C_4=253/49152$')
            elif case=='negative_C4':
                ax.axhline(-1/15360,color=orange,ls='--',label=r'$C_4=-1/15360$')
            else:
                ax.plot(xs,[x**.5/6336 for x in xs],color=orange,ls='--',label=r'Leading growth $\sqrt{M}/6336$')
            ticks=[2,5,10,50,200] if case!='C2_only' else [10,20,50,100,400]
            ax.set(xscale='log',xlabel='Slope budget $M$',ylabel=r'$M^4[\delta(M)-\delta_0-C_2/M^2]$',title=title)
            ax.xaxis.set_major_locator(FixedLocator(ticks));ax.xaxis.set_major_formatter(FixedFormatter(list(map(str,ticks))))
            ax.xaxis.set_minor_formatter(NullFormatter());ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0),useOffset=False)
            ax.grid(alpha=.15);ax.legend(fontsize=8.1,loc='best')
        fig.suptitle('Fourth-order structure and the regularity boundary',fontsize=15,fontweight='bold',color=dark)
        fig.supxlabel('Compact verification examples. Curves illustrate exact parametrizations; they are not theta-family certificates.',fontsize=9,color='#555555')
        fig.savefig(figdir/'fourth_order.png',dpi=180);fig.savefig(figdir/'fourth_order.svg',metadata={'Date':None});plt.close(fig)
        meta={'curves':curves,'sample_precision_digits':80,'certificate_sha256':sha(certpath),
              'source_sha256':sha(Path(__file__)),'matplotlib':matplotlib.__version__,
              'figures':{p.name:sha(p) for p in sorted(figdir.iterdir()) if p.suffix in ['.png','.svg']},
              'trust_boundary':'Floating-point rendering of high-precision samples, not a numerical proof.'}
        (resdir/'plot_data.json').write_text(json.dumps(meta,indent=2)+'\n')
    lines=['# R22 — Yaklaşık gösterim tablosu','',
           'Bu ondalıklar aralık değildir. Kesin rasyonel uçlar certificate.json içindedir.',
           'Hata oranı, M⁻⁴ eklenmiş yaklaşımın mutlak hatasının yalnız M⁻² yaklaşımının hatasına oranıdır.','',
           '| Örnek | a | M | M⁴ ölçekli artık | Yeni/eski hata oranı |',
           '|---|---|---:|---:|---:|']
    for row in cert['rows']:
        v=row['approximate_midpoints'];fmt=lambda k:format(float(v[k]),'.10g')
        lines.append('| '+row['case']+' | '+row['a']+' | '+fmt('slope_budget')+' | '+fmt('scaled_fourth_residual')+' | '+(fmt('error_ratio') if 'error_ratio' in v else 'uygulanmaz')+' |')
    lines+=['','İlk iki örnekte sınırlar sırasıyla 253/49152 ve −1/15360.',
            'C² örneğinde bu ölçekli artık sınırsız büyür; sonlu C₄ yoktur.','']
    (resdir/'TABLE.md').write_text('\n'.join(lines))
    print(json.dumps({'status':'fourth_order_scientific_figure_created','curve_samples':540}))
if __name__=='__main__':main()
