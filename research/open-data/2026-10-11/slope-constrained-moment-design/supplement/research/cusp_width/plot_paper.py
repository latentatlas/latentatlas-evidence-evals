#!/usr/bin/env python3
"""Two paper figures; floating-point conversion is for rendering only."""
import hashlib
import json
import math
from fractions import Fraction as Q
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mid(v):
    a,e=v['mid_man_exp'];return Q(a)*Q(2)**e
def rad(v):
    a,e=v['rad_man_exp'];return Q(a)*Q(2)**e
def bounds(v):return float(mid(v)-rad(v)),float(mid(v)+rad(v))


def save(fig,stem):
    fig.savefig(HERE/f'output/pdf/{stem}.pdf',facecolor='white',
                metadata={'Title':stem,'Author':'Huseyin Buldurgan',
                          'Subject':'Verified local cusp geometry; see separate captions'})
    for ext in ('eps','svg','png'):
        fig.savefig(HERE/f'paper/{stem}.{ext}',dpi=220,facecolor='white')
    plt.close(fig)


def main():
    p4=HERE.parent/'cusp_geometry/results/geometry_certificate.json'
    p3=HERE.parent/'cusp_connection/results/connection_certificate.json'
    p5=HERE/'results/width_certificate.json';pe=HERE/'results/endpoint_folds.json'
    geo=json.loads(p4.read_text());old=json.loads(p3.read_text())
    width=json.loads(p5.read_text());ends=json.loads(pe.read_text())
    check=json.loads((HERE/'results/rational_check.json').read_text())
    ec=json.loads((HERE/'results/endpoint_check.json').read_text())
    assert check['certificate_sha256']==sha(p5) and ec['certificate_sha256']==sha(pe)
    assert len(check['per_cell'])==58 and len(ec['checks'])==128
    assert width['geometry_certificate_sha256']==sha(p4)
    assert width['connection_certificate_sha256']==sha(p3)
    for n,h in width['source_sha256'].items():assert sha(HERE/n)==h
    (HERE/'output/pdf').mkdir(parents=True,exist_ok=True)
    (HERE/'paper').mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'Times New Roman','font.size':9,
                         'mathtext.fontset':'stix','pdf.fonttype':42,'ps.fonttype':42,
                         'axes.linewidth':.65,'lines.linewidth':1.1,
                         'axes.spines.top':False,'axes.spines.right':False,
                         'xtick.major.width':.6,'ytick.major.width':.6,
                         'svg.hashsalt':'cusp-width-r05'})
    blue='#225b86';orange='#a34529';green='#276251'
    fig,(a,b)=plt.subplots(1,2,figsize=(7.05,3.25))
    fig.subplots_adjust(left=.09,right=.975,bottom=.21,top=.91,wspace=.35)
    for ax,label in ((a,'(a)'),(b,'(b)')):
        ax.text(0,1.05,label,transform=ax.transAxes,fontweight='bold')
        ax.grid(color='#e2e2e2',lw=.45,zorder=0)
    x=[i/400 for i in range(401)]
    inner=[.49*z**1.5 for z in x];outer=[.86*z**1.5 for z in x]
    a.set_facecolor('#f2f2f2')
    a.fill_between(x,[-z for z in outer],outer,color='#ead7bb',zorder=2)
    a.fill_between(x,[-z for z in inner],inner,color='#c3ddcf',zorder=3)
    for values in (inner,outer,[-z for z in inner],[-z for z in outer]):
        a.plot(x,values,color='#876234',lw=.65,zorder=4)
    a.scatter([0],[0],color='black',s=12,zorder=5)
    a.annotate('cusp',(0,0),(-.63,.42),arrowprops={'arrowstyle':'->','lw':.6},fontsize=8)
    a.text(-.62,-1.13,'1 root',color='#464646')
    a.text(.71,-.03,'3 roots',ha='center',va='center',color='#174932',zorder=5)
    a.set(xlim=(-1,1),ylim=(-2,2),xlabel=r'$10^6\ell$',ylabel=r'$10^9m$')
    a.legend(handles=[Patch(facecolor='#c3ddcf',label='Three roots guaranteed'),
                      Patch(facecolor='#ead7bb',label='Fold enclosures'),
                      Patch(facecolor='#f2f2f2',edgecolor='#aaa',label='One root guaranteed')],
             loc='upper left',fontsize=7.2,frameon=False,handlelength=1.5)
    xs=[];ys=[]
    for i,c in enumerate(geo['cells']):
        center=-float(mid(c['driver_center']));h=float(mid(c['driver_half_width']))
        lo,hi=bounds(c['opening_coefficient'])
        b.fill_between([center-h,center+h],[lo,lo],[hi,hi],color='#d4e3db',lw=0,zorder=1)
        ds=old['cells'][i]['central_derivatives']
        xs.append(center);ys.append(-8*math.sqrt(2)/3*float(mid(ds[3])/mid(ds[4])))
    cq=float(mid(geo['endpoints']['quartic']['C']))
    cs=float(mid(geo['endpoints']['sextic']['C']))
    sx=-float(mid(ends['models']['sextic']['driver']))
    b.plot([0]+xs,[cq]+ys,color=green,lw=1.3,zorder=3)
    b.scatter([0,sx],[cq,cs],color=[blue,orange],s=19,zorder=4)
    b.annotate('Q',(0,cq),(1.2,1.281),color=blue,fontsize=9)
    b.annotate('S',(sx,cs),(26.1,1.337),color=orange,fontsize=9)
    b.set(xlim=(-.5,29.5),ylim=(1.255,1.36),xlabel=r'$-\nu$',ylabel=r'$C(\nu)$')
    b.legend(handles=[Patch(facecolor='#d4e3db',label='Whole-cell enclosures'),
                      Line2D([],[],color=green,label='Computed center values')],
             loc='lower right',fontsize=7.2,frameon=False,handlelength=1.5)
    save(fig,'figure_1_cusp_geometry')

    fig,(a,b)=plt.subplots(1,2,figsize=(7.05,3.45))
    fig.subplots_adjust(left=.09,right=.975,bottom=.23,top=.91,wspace=.39)
    for ax,label in ((a,'(a)'),(b,'(b)')):
        ax.text(0,1.055,label,transform=ax.transAxes,fontweight='bold')
        ax.grid(color='#e2e2e2',lw=.45,zorder=0)
    x=[0]+[1e6*float(mid(r['ell'])) for r in ends['samples']]
    curves={}
    for family in ('quartic','sextic'):
        curves[family]={branch:[0]+[1e9*float(mid(r['endpoints'][family][branch]['root_enclosures'][1]))
                                   for r in ends['samples']] for branch in ('upper','lower')}
    a.fill_between(x,curves['sextic']['lower'],curves['sextic']['upper'],color='#e5c0b0',zorder=1)
    a.fill_between(x,curves['quartic']['lower'],curves['quartic']['upper'],color='#cfdeea',zorder=2)
    for family,color,style in (('quartic',blue,'--'),('sextic',orange,'-')):
        for branch in ('upper','lower'):
            y=curves[family][branch]
            a.plot(x,y,color=color,ls=style,lw=1.1,zorder=3)
            a.scatter(x[1::4],y[1::4],color=color,s=4,zorder=4)
    a.set(xlim=(-.025,1.025),ylim=(-.76,.76),xlabel=r'$10^6\ell$',ylabel=r'$10^9m$')
    a.legend(handles=[Line2D([],[],color=blue,ls='--',label=r'Q: $\nu=0$'),
                      Line2D([],[],color=orange,label=r'S: $\nu\simeq-28.824533$')],
             loc='lower left',fontsize=7.2,frameon=False,handlelength=2.2)
    a.text(.67,0,'3 roots',ha='center',va='center',color='#213f59',fontsize=8.5)
    inset=a.inset_axes([.085,.57,.42,.34])
    for family,color,style in (('quartic',blue,'--'),('sextic',orange,'-')):
        inset.plot(x,curves[family]['upper'],color=color,ls=style,lw=1)
    inset.set(xlim=(.82,1.005),ylim=(.48,.68),xticks=[.85,1],yticks=[.5,.65])
    inset.tick_params(labelsize=6.5,pad=1.5,length=2)
    inset.set_title('Upper fold: detail',fontsize=7,pad=3)
    inset.set_facecolor('white')
    # All these rectangles are enclosures, not samples of a single curve.
    for c in width['cells']:
        center=-float(mid(c['driver_center']));h=float(mid(c['driver_half_width']))
        lo=1000*float(mid(c['normalized_width_rate_lower']))
        hi=1000*float(mid(c['normalized_width_rate_upper']))
        b.fill_between([center-h,center+h],[lo,lo],[hi,hi],color='#c3ddcf',lw=0,zorder=2)
        b.plot([center-h,center+h],[lo,lo],color=green,lw=.7,zorder=3)
        b.plot([center-h,center+h],[hi,hi],color=green,lw=.7,zorder=3)
    b.axhline(0,color='#555',ls='--',lw=.7,zorder=1)
    b.set(xlim=(-.5,29.5),ylim=(-.12,2.6),xlabel=r'$-\nu$',
          ylabel=r'$-10^3\ell^{-3/2}\,\partial_\nu W_\nu(\ell)$')
    b.text(.5,.95,r'Valid for every $0<\ell\leq10^{-6}$',transform=b.transAxes,
           ha='center',va='top',fontsize=8)
    b.legend(handles=[Patch(facecolor='#c3ddcf',edgecolor=green,label='Whole-cell bounds')],
             loc='lower left',fontsize=7.5,frameon=False)
    save(fig,'figure_2_finite_width')
    meta={'source_sha256':sha(Path(__file__)),
          'inputs':{str(p.relative_to(HERE.parent)):sha(p) for p in
                    (p3,p4,p5,pe,HERE/'results/rational_check.json',HERE/'results/endpoint_check.json')},
          'scope':'Figure 1: common guaranteed root regions and coefficient bounds. Figure 2: certified endpoint samples connected only for display, and uniform finite-width-rate enclosures.',
          'font':'Times New Roman with STIX mathematical glyphs; embedded TrueType in PDF/EPS',
          'rendering_only_binary64':True,
          'outputs':{str(p.relative_to(HERE)):sha(p) for p in sorted((HERE/'paper').glob('figure_*.*'))}}
    for p in sorted((HERE/'output/pdf').glob('*.pdf')):meta['outputs'][str(p.relative_to(HERE))]=sha(p)
    (HERE/'results/plot_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('Saved two vector PDF/EPS/SVG figures and PNG previews.')


if __name__=='__main__':main()
