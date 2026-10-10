#!/usr/bin/env python3
"""Scientific illustration from the continuation certificate."""
import json
import hashlib
from fractions import Fraction as Q
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'cusp_verified'


def mid(ball):
    m,e=ball['mid_man_exp']
    return Q(m)*Q(2)**e


def rad(ball):
    m,e=ball['rad_man_exp']
    return Q(m)*Q(2)**e


def main():
    path=HERE/'results/connection_certificate.json'
    data=json.loads(path.read_text())
    q=json.loads((BASE/'results/quartic_cusp_certificate.json').read_text())
    s=json.loads((BASE/'results/sextic_cusp_certificate.json').read_text())
    cells=data['cells']
    qmu=float(mid(q['center_exact_dyadic'][2]))
    snu=float(mid(s['center_exact_dyadic'][2]))
    nu=[float(mid(c['driver_center'])) for c in cells]
    mu=[float(mid(c['center'][2])) for c in cells]

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,(ax,bx)=plt.subplots(1,2,figsize=(12.0,5.6))
    fig.subplots_adjust(left=.08,right=.98,top=.79,bottom=.20,wspace=.27)
    fig.suptitle('Quartic and sextic cusps lie on one certified curve',x=.08,y=.96,
                 ha='left',fontsize=18,fontweight='bold')
    fig.text(.08,.895,r'$F=F_t=F_{tt}=0$ throughout the path  |  '+
             r'58 connected tubes cover every $\nu\in[-29,0]$',fontsize=11,color='#495568')
    ax.set_title('A  |  The two polynomial slices are connected',loc='left',
                 fontsize=11,fontweight='bold',pad=12)
    ax.plot([0]+nu,[qmu]+mu,lw=2.3,color='#176d59')
    for c in cells:
        nc=mid(c['driver_center'])
        h=mid(c['driver_half_width'])
        mc=mid(c['center'][2])
        v=mid(c['predictor'][2])
        rr=mid(c['tight_root_radii'][2])+rad(c['tight_root_radii'][2])
        xs=[float(nc-h),float(nc+h)]
        lower=[float(mc-v*h-rr),float(mc+v*h-rr)]
        upper=[float(mc-v*h+rr),float(mc+v*h+rr)]
        ax.fill_between(xs,lower,upper,color='#78b69b',alpha=.5,lw=0)
    ax.scatter([0],[qmu],s=50,color='#145e4c',zorder=5)
    ax.scatter([snu],[0],s=50,color='#ac5338',zorder=5)
    ax.annotate('Quartic cusp\n'+r'$\nu=0,\ \mu\approx8.33512$',
                xy=(0,qmu),xytext=(-16,7.85),color='#145e4c',
                arrowprops={'arrowstyle':'->','color':'#145e4c'},fontsize=11)
    ax.annotate('Sextic cusp\n'+r'$\mu=0,\ \nu\approx-28.82453$',
                xy=(snu,0),xytext=(-24,1.7),color='#94472f',
                arrowprops={'arrowstyle':'->','color':'#94472f'},fontsize=11)
    ax.axhline(0,color='#98a4b3',lw=.8)
    ax.set(xlim=(-30,1),ylim=(-.45,9),xlabel=r'Sextic coefficient $\nu$',
           ylabel=r'Quartic coefficient $\mu$')
    ax.grid(alpha=.18)

    bx.set_title('B  |  The third derivative stays strictly positive',loc='left',
                 fontsize=11,fontweight='bold',pad=12)
    for i,c in enumerate(cells):
        left=float(mid(c['driver_left']))
        right=float(mid(c['driver_right']))
        d=c['uniform_derivatives'][3]
        lo=float(mid(d)-rad(d))*1e13
        hi=float(mid(d)+rad(d))*1e13
        bx.fill_between([left,right],[lo,lo],[hi,hi],color='#86bda6',alpha=.65,
                        lw=0,label='Certified enclosure' if i==0 else None)
    center_d=[float(mid(c['central_derivatives'][3]))*1e13 for c in cells]
    bx.plot(nu,center_d,color='#174c40',lw=1.6,label='Computed center values')
    bx.plot([-29,0],[.8,.8],ls='--',color='#b56a35',lw=1.3,label='Proved lower bound')
    bx.axhline(0,color='#667282',lw=1)
    bx.set(xlim=(-30,1),ylim=(-.10,4.1),xlabel=r'Sextic coefficient $\nu$',
           ylabel=r'$10^{13}F_{ttt}$ along the cusp curve')
    bx.grid(alpha=.18)
    bx.legend(loc='upper left',frameon=False,fontsize=9)
    fig.text(.08,.083,r'Along the certified curve, $0.26<d\mu/d\nu<0.34$: '+
             'the sextic slice is crossed exactly once.',fontsize=10.5,color='#34445a')
    fig.text(.08,.035,'Lines illustrate the curve; interval tubes, root containment '+
             'and the analytic argument establish the connection.',fontsize=10,color='#495568')
    for suffix in ('png','svg'):
        fig.savefig(HERE/f'results/cusp_connection.{suffix}',dpi=180,facecolor='white')
    plt.close(fig)
    meta={'certificate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'scope':'Illustration from certified cells; plotted connecting lines are not proof objects'}
    (HERE/'results/plot_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('Saved cusp_connection.png and cusp_connection.svg')


if __name__=='__main__':
    main()
