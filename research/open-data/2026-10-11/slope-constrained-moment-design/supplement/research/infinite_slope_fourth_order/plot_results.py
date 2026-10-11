#!/usr/bin/env python3
"""Scientific figure for the infinite periodic example; not a theta plot."""
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
def mid(v):
    return (mp.mpf(v['lower'][0])*mp.power(2,v['lower'][1])+mp.mpf(v['upper'][0])*mp.power(2,v['upper'][1]))/2
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--outdir',type=Path,required=True);args=ap.parse_args()
    if args.outdir.exists():raise FileExistsError(args.outdir)
    args.outdir.mkdir(parents=True);mp.mp.dps=80
    cp=HERE/'results/certificate.json';cert=json.loads(cp.read_text())
    pi=mp.pi;L=mp.exp(-mp.mpf('.5'))/(1-mp.exp(-1));D=(1+2*pi*L)/(1+pi*pi)
    c=(1-D)/(pi*D);Gamma=pi*L;Xi=Gamma*((11+3*pi*pi)/180-1/(36*D*D))
    delta=mp.mpf(1)/4;C2=delta**3*Gamma/(3*D);C4=delta**5*(Gamma**2/(3*D**2)-Xi/D);s=-1+1j*pi
    curve=[]
    for aw in np.geomspace(.2,.002,180):
        a=mp.mpf(str(aw))
        def Z(d):return -1/s+2j*L*mp.exp(s*d)*mp.sinh(s*a)/(s*s*a)
        d=mp.findroot(lambda dd:mp.im(Z(dd))-c*mp.re(Z(dd)),(0,.01))
        A=(D/4)/mp.re(Z(d));M=A/a;scaled=M**4*(A-delta-C2/M**2)
        curve.append({'a':str(a),'M':mp.nstr(M,45),'scaled_residual':mp.nstr(scaled,45)})
    tails=[]
    for N in range(1,65):
        fac=1-mp.exp(-N);cn=delta**5*((Gamma*fac)**2/(3*D**2)-Xi*fac/D)
        tails.append({'N':N,'error':mp.nstr(C4-cn,45)})
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':11,
                         'svg.hashsalt':'r23-infinite-switch-example','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,3,figsize=(15,6),gridspec_kw={'width_ratios':[1.1,1,1]})
    fig.subplots_adjust(left=.055,right=.985,bottom=.30,top=.79,wspace=.31)
    blue='#146C94';red='#BE4B35';gold='#A67412'
    d=float(mid(cert['rows'][0]['intervals']['d']));a=.2
    x=np.linspace(0,3.2,1800);sign=np.where(np.cos(np.pi*x)>=0,1.,-1.);profile=np.where(np.cos(np.pi*(x-d))>=0,1.,-1.)
    for k in range(4):
        center=k+.5+d;mask=np.abs(x-center)<=a
        profile[mask]=(-1)**(k+1)*(x[mask]-center)/a
    axs[0].plot(x,sign,color='0.65',lw=1.2,ls='--',label='limiting sign profile')
    axs[0].plot(x,profile,color=blue,lw=2,label='balanced ramps, a = 0.2')
    axs[0].set(xlim=(0,3.2),ylim=(-1.22,1.28),xlabel='position u',ylabel='unit profile',title='Infinitely repeating switches')
    axs[0].text(.06,.92,r'$s(u+1)=-s(u)$',transform=axs[0].transAxes,fontsize=10)
    axs[0].legend(loc='lower center',bbox_to_anchor=(.5,-.40),frameon=False,fontsize=9)
    axs[1].plot([float(r['M']) for r in curve],[float(r['scaled_residual']) for r in curve],color=blue,lw=2,label='whole-tail value')
    axs[1].axhline(float(C4),color=red,lw=1.5,ls='--',label=r'$C_4 = 0.00634907424\ldots$')
    axs[1].scatter([float(mid(r['intervals']['M'])) for r in cert['rows']],
                   [float(mid(r['intervals']['scaled_fourth_residual'])) for r in cert['rows']],color=blue,s=27,zorder=3,label='certified sample budgets')
    axs[1].set(xscale='log',xlabel='slope budget M',ylabel=r'$M^4[\delta(M)-\delta_0-C_2/M^2]$',title='Fourth-order coefficient')
    axs[1].ticklabel_format(axis='y',style='sci',scilimits=(-3,-3),useMathText=True)
    axs[1].legend(loc='lower center',bbox_to_anchor=(.5,-.43),frameon=False,fontsize=9)
    axs[2].semilogy([r['N'] for r in tails],[float(r['error']) for r in tails],color=gold,lw=2)
    axs[2].scatter([r['roots'] for r in cert['geometric_series_truncation']],
                   [float(mid(r['C4_error'])) for r in cert['geometric_series_truncation']],color=gold,s=24,zorder=3)
    axs[2].set(xlabel='number N of retained switch terms',ylabel=r'$|C_4-C_{4,N}|$',title='Coefficient-series tail',xlim=(0,66))
    for ax in axs:ax.grid(alpha=.18)
    fig.suptitle('Fourth-order cost with infinitely many switches',fontsize=17,x=.5,y=.96)
    fig.text(.5,.87,r'Control example: $q_1=e^{-u}\cos(\pi u)$, one preserved moment; $\delta_0=1/4$',ha='center',fontsize=11)
    fig.text(.5,.025,'All value calculations include the infinite geometric tail. This example is separate from the theta family.',ha='center',fontsize=10,color='#444444')
    paths=[]
    for ext in ['png','svg']:
        p=args.outdir/('infinite_switches.'+ext)
        fig.savefig(p,dpi=180,metadata={'Date':None} if ext=='svg' else {'Software':'R23 scientific plot'})
        paths.append(p)
    plt.close(fig)
    data={'source_sha256':sha(__file__),'certificate_sha256':sha(cp),'precision_digits':80,
      'value_curve':curve,'tail_curve':tails,'profile_samples':len(x),'profile_width':'1/5',
      'figures':{p.name:sha(p) for p in paths},'scope':'Infinite exponential/trigonometric example; theta is not plotted. Curves are numerical; six value markers and seven tail markers have Arb enclosures.'}
    (args.outdir/'plot_data.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':'figure_written','value_samples':len(curve),'tail_samples':len(tails),'paths':[str(p) for p in paths]}))
if __name__=='__main__':main()
