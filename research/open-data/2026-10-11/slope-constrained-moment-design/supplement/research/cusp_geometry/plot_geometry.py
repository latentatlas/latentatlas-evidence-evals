#!/usr/bin/env python3
"""Display common rigorous fold bands and the changing opening coefficient."""
import hashlib
import json
import math
from fractions import Fraction as Q
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
HERE=Path(__file__).resolve().parent

def mid(b):
    m,e=b['mid_man_exp'];return Q(m)*Q(2)**e
def rad(b):
    m,e=b['rad_man_exp'];return Q(m)*Q(2)**e
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    path=HERE/'results/geometry_certificate.json';data=json.loads(path.read_text())
    oldpath=HERE.parent/'cusp_connection/results/connection_certificate.json'
    old=json.loads(oldpath.read_text())
    endpath=HERE.parent/'cusp_verified/results/sextic_cusp_certificate.json'
    sextic=json.loads(endpath.read_text());sx=-float(mid(sextic['center_exact_dyadic'][2]))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,(a,b)=plt.subplots(1,2,figsize=(13,6.0))
    fig.subplots_adjust(left=.075,right=.975,top=.77,bottom=.24,wspace=.30)
    fig.suptitle('Cusp boyunca kök düzeni ve bölgenin açılması',x=.075,y=.96,
                 ha='left',fontsize=19,fontweight='bold',color='#193e37')
    fig.text(.075,.895,'Her kesit kendi cusp merkezine göre ölçülüyor; '+
             r'$\nu\in[-29,0]$ boyunca aynı sonlu pencere doğrulandı.',color='#475468')
    a.set_title('A  |  Bütün yol için ortak kök ve fold sınırları',loc='left',fontsize=11,pad=14,fontweight='bold')
    a.axhspan(-2,2,color='#edf0f4',zorder=0)
    x=[k/300 for k in range(301)]
    lo=[.49*v**1.5 for v in x];hi=[.86*v**1.5 for v in x]
    a.fill_between(x,[-v for v in lo],lo,color='#acd8c3',zorder=1)
    a.fill_between(x,lo,hi,color='#e9be81',zorder=1)
    a.fill_between(x,[-v for v in hi],[-v for v in lo],color='#e9be81',zorder=1)
    for ys in (lo,hi,[-v for v in lo],[-v for v in hi]):
        a.plot(x,ys,color='#92632e',lw=.8,alpha=.7)
    a.scatter([0],[0],s=70,marker='*',color='#193e37',zorder=5)
    a.annotate('cusp',xy=(0,0),xytext=(-.65,.45),arrowprops={'arrowstyle':'->','color':'#475468'},color='#344457')
    a.text(-.68,-.9,'1 kök',color='#687489',fontsize=12)
    a.text(.68,0,'3 kök',ha='center',va='center',color='#18523e',fontsize=11)
    a.set(xlim=(-1,1),ylim=(-2,2),xlabel=r'$10^6(\lambda-\lambda_*(\nu))$',
          ylabel=r'$10^9(\mu-\mu_*(\nu))$')
    a.grid(alpha=.15)
    a.legend(handles=[Patch(color='#acd8c3',label='3 kök garanti'),
                      Patch(color='#edf0f4',label='1 kök garanti'),
                      Patch(color='#e9be81',label='Fold konum aralıkları')],
             loc='upper left',fontsize=8.6,frameon=False)

    b.set_title('B  |  Cusp yakınındaki açılma katsayısı artıyor',loc='left',fontsize=11,pad=14,fontweight='bold')
    xs=[];ys=[]
    for i,cell in enumerate(data['cells']):
        center=-float(mid(cell['driver_center']));h=float(mid(cell['driver_half_width']))
        ball=cell['opening_coefficient'];lower=float(mid(ball)-rad(ball));upper=float(mid(ball)+rad(ball))
        b.fill_between([center-h,center+h],[lower,lower],[upper,upper],color='#bbd9ca',alpha=.6,lw=0,
                       label='Sertifikalı hücre aralıkları' if i==0 else None)
        ds=old['cells'][i]['central_derivatives']
        xs.append(center);ys.append(-8*math.sqrt(2)/3*float(mid(ds[3])/mid(ds[4])))
    cq=float(mid(data['endpoints']['quartic']['C']));cs=float(mid(data['endpoints']['sextic']['C']))
    b.plot([0]+xs,[cq]+ys,color='#195b47',lw=2,label='Hesaplanan merkez değerleri')
    b.scatter([0,sx],[cq,cs],s=44,color=['#195b47','#ad623b'],zorder=5)
    b.annotate('Quartic\n1,294609',xy=(0,cq),xytext=(2,1.282),fontsize=10,
               arrowprops={'arrowstyle':'->','color':'#475468'})
    b.annotate('Sextic\n1,326905',xy=(sx,cs),xytext=(17,1.34),fontsize=10,
               arrowprops={'arrowstyle':'->','color':'#475468'})
    b.text(3,1.342,'Başterim katsayısında\nyaklaşık %2,495 artış',fontsize=11,color='#195b47')
    b.set(xlim=(-.6,29.6),ylim=(1.26,1.36),xlabel=r'Quartic → sextic yönü: $-\nu$',
          ylabel=r'$C(\nu)=\lim_{\ell\to0^+} W_\nu(\ell)/\ell^{3/2}$')
    b.grid(alpha=.17)
    b.legend(loc='lower right',fontsize=8.4,frameon=False)
    fig.text(.075,.117,r'A: Turuncu şeritlerde kesin kök sayısı, gerçek fold konumuna bağlıdır. '+
             r'Kök sayıları $|t-t_*(\nu)|\leq0.003$ içindir.',fontsize=10,color='#475468')
    fig.text(.075,.068,r'B: Bütün yol için $C^\prime(\nu)<0$ kanıtlandı. '+
             'Bu, sonlu uzaklıktaki genişliğin her yerde monoton olduğunu henüz söylemez.',fontsize=10,color='#475468')
    for ext in ('png','svg'): fig.savefig(HERE/f'results/cusp_geometry.{ext}',dpi=180,facecolor='white')
    plt.close(fig)
    (HERE/'results/plot_metadata.json').write_text(json.dumps({
        'certificate_sha256':sha(path),'connection_certificate_sha256':sha(oldpath),
        'source_sha256':sha(Path(__file__)),
        'scope':'Common rigorous inner/outer fold bands; candidate center plot of leading width, with certified whole-cell coefficient enclosures'},indent=2)+'\n')
    print('Saved cusp_geometry.png and cusp_geometry.svg')

if __name__=='__main__':main()
