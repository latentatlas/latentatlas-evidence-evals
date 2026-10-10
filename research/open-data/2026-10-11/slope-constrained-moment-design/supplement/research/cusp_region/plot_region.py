#!/usr/bin/env python3
"""Scientific illustration of the certified region; pixels are not a proof."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flint import arb,ctx
from taylor_box import TaylorBox,restore,digest
from validated_flow import matvec,midpoint_inverse
from certify_region import control_matrix

HERE=Path(__file__).resolve().parent


def fold_point(model,dt):
    p=[(2*dt*dt).mid(),(16*model.c[3]/(3*model.c[4])*dt*dt*dt).mid()]
    for _ in range(4):
        d=model.derivatives(dt,*p,upto=5)
        change=matvec(midpoint_inverse(control_matrix(d)),d[:2])
        p=[(a-b).mid() for a,b in zip(p,change)]
    return [float(v) for v in p]


def main():
    ctx.dps=110
    model=TaylorBox()
    path=HERE/'results/region_certificate.json'
    report=json.loads(path.read_text())
    L=arb(1)/1000000
    branches=[]
    for fold in report['right_boundary_folds']:
        tend=restore(fold['t_offset_box']).mid()
        points=[]
        for k in range(121):
            # Floats are used only for display after interval evaluation.
            dt=tend*k/120
            lam,mu=fold_point(model,dt)
            points.append([lam*1e6,mu*1e9])
        branches.append(np.array(points))
    trajectory=[]
    for k in range(501):
        dt=-arb(3)/1000+arb(6)/1000*k/500
        dm=arb(0)
        for _ in range(4):
            f=model.evaluate(0,dt,L,dm)[0]
            fmu=model.evaluate(4,dt,L,dm)[0]/16
            dm=(dm-f/fmu).mid()
        trajectory.append([float(dm)*1e9,float(dt)*1e3])
    trajectory=np.array(trajectory)
    low,high=sorted(float(restore(v['mu_offset_box']).mid())*1e9
                    for v in report['right_boundary_folds'])

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,(ax,bx)=plt.subplots(1,2,figsize=(12.0,5.5))
    fig.subplots_adjust(left=.08,right=.98,top=.79,bottom=.20,wspace=.28)
    fig.suptitle('A certified local cusp and its real-root transitions',
                 x=.08,y=.96,ha='left',fontsize=18,fontweight='bold')
    fig.text(.08,.89,'Quartic deformation  |  all root counts refer to '+
             r'$t\in[t_0-0.003,\,t_0+0.003]$',fontsize=11,color='#495568')

    ax.set_facecolor('#f2f5f9')
    polygon=np.vstack((branches[0],branches[1][::-1]))
    ax.fill(polygon[:,0],polygon[:,1],color='#b9e4cc',zorder=1)
    for b in branches:
        ax.plot(b[:,0],b[:,1],color='#146b53',lw=2.4,zorder=3)
    ax.scatter([0],[0],s=34,c='#202938',zorder=4)
    ax.annotate('cusp',xy=(0,0),xytext=(-.55,-.55),fontsize=11,
                arrowprops={'arrowstyle':'->','color':'#526072'},color='#202938')
    ax.text(-.80,1.25,'1 simple real zero',color='#34445a',fontsize=12)
    ax.text(.74,0,'3 simple\nreal zeros',ha='center',va='center',
            color='#104d3c',fontsize=11,fontweight='bold')
    ax.text(.13,.94,'double zero + simple zero\non each fold',fontsize=10,
            color='#146b53',ha='left')
    ax.set(xlim=(-1,1),ylim=(-2,2),xlabel=r'$10^6(\lambda-\lambda_0)$',
           ylabel=r'$10^9(\mu-\mu_0)$')
    ax.set_title('A  |  Complete count in the control rectangle',loc='left',
                 fontsize=11,pad=12,fontweight='bold')
    ax.grid(alpha=.16,zorder=0)

    bx.axvspan(low,high,color='#b9e4cc',zorder=0)
    bx.plot(trajectory[:,0],trajectory[:,1],color='#203a5b',lw=2.2)
    for edge in (low,high):
        bx.axvline(edge,color='#146b53',ls='--',lw=1)
    for fold in report['right_boundary_folds']:
        bx.scatter([float(restore(fold['mu_offset_box']).mid())*1e9],
                   [float(restore(fold['t_offset_box']).mid())*1e3],
                   c='#146b53',s=30,zorder=4)
    bx.text(0,2.60,'3 zeros',ha='center',fontsize=11,color='#104d3c',fontweight='bold')
    bx.text(-1.4,2.60,'1 zero',ha='center',fontsize=11,color='#34445a')
    bx.text(1.4,2.60,'1 zero',ha='center',fontsize=11,color='#34445a')
    bx.set(xlim=(-2,2),ylim=(-3,3),xlabel=r'$10^9(\mu-\mu_0)$',
           ylabel=r'$10^3(t-t_0)$')
    bx.set_title(r'B  |  Root motion at $\lambda=\lambda_0+10^{-6}$',
                 loc='left',fontsize=11,pad=12,fontweight='bold')
    bx.grid(alpha=.16)
    fig.text(.08,.080,'Read panel B vertically: each intersection is a real zero. '
             'At the dashed boundaries two zeros merge.',fontsize=10,color='#495568')
    fig.text(.08,.037,'Curves are numerical illustrations. The region and counts '
             'are proved by the interval certificate and analytic argument.',
             fontsize=10,color='#495568')
    for suffix in ('png','svg'):
        fig.savefig(HERE/f'results/cusp_region.{suffix}',dpi=180,facecolor='white')
    plt.close(fig)
    (HERE/'results/plot_data.json').write_text(json.dumps({
        'scope':'Illustrative sample coordinates; not standalone proof objects',
        'certificate_sha256':digest(path),'source_sha256':digest(Path(__file__)),
        'folds_in_scaled_control_coordinates':[v.tolist() for v in branches],
        'roots_in_scaled_mu_t_coordinates':trajectory.tolist()},indent=2)+'\n')
    print('Saved cusp_region.png and cusp_region.svg')


if __name__=='__main__':
    main()
