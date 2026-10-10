#!/usr/bin/env python3
"""Scientific illustrations of certified intervals and one feasible design."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
def mid(v):
    m,e=v['mid_man_exp'];return float(m)*2.**e
def main():
    c=json.loads((HERE/'results/slope_threshold_certificate.json').read_text())
    ck=json.loads((HERE/'results/slope_threshold_check.json').read_text())
    old=json.loads((HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json').read_text())
    L=9.1787079603827e-10;U0=9.1787079608363e-10
    lo,hi=map(float,c['readable_bracket']);oldlo=9.17870847e-10;oldhi=2.3803280902557e-7
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    out=HERE/'figures';out.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),gridspec_kw={'width_ratios':[1,1.55]})
    ax=axes[0];ax.set_yscale('log')
    for x,a,b,color,label in [(0,oldlo,oldhi,'#87939c','R13'),(1,lo,hi,'#006b83','R14')]:
        ax.vlines(x,a,b,color=color,lw=9,alpha=.8);ax.plot([x-.11,x+.11],[a,a],color=color,lw=2);ax.plot([x-.11,x+.11],[b,b],color=color,lw=2)
    ax.set_xticks([0,1],['Önceki aralık\nR13','Yeni aralık\nR14']);ax.set_xlim(-.55,1.65);ax.set_ylim(6e-10,5e-7)
    ax.set_ylabel('Gerekli en küçük bağıl değişiklik');ax.set_title('Aynı hedef, aynı eğim sınırı',loc='left',fontweight='bold')
    ax.grid(axis='y',which='major',alpha=.2)
    ax.annotate('Üst sınır\n2,38033 × 10⁻⁷',(0,oldhi),xytext=(.30,1.6e-7),fontsize=10,arrowprops={'arrowstyle':'-','color':'#657780'})
    ax.text(.4,1.25e-9,'Yeni aralık bu ölçekte\nçok ince; sağda büyütülüyor.',fontsize=9,color='#006b83')
    ax=axes[1];a=(lo/L-1)*1e6;b=(hi/L-1)*1e6
    ax.axvspan(a,b,ymin=.19,ymax=.48,color='#bfe1e7',alpha=.9)
    ax.hlines(1,a,b,color='#006b83',lw=7);ax.plot([a,b],[1,1],'|',color='#006b83',markersize=22,markeredgewidth=2)
    ax.vlines([a,b],.7,1.3,color='#006b83',lw=1)
    ax.text(a,.55,'Alt sınır\n'+f'{a:.3f}'.replace('.',','),ha='center',color='#006b83')
    ax.text(b,.55,'Üst sınır\n'+f'{b:.3f}'.replace('.',','),ha='center',color='#006b83')
    ax.plot([0],[2],'|',color='#59616b',markersize=20,markeredgewidth=2)
    ax.annotate('Sınırsız eşik aralığı\nGenişlik < 0,00005; görünürlük işareti',xy=(0,2),xytext=(1.0,2.1),fontsize=9,
                arrowprops={'arrowstyle':'-','color':'#59616b'},color='#59616b')
    ax.text((a+b)/2,1.6,'Gerçek minimum bu aralıkta\nTam değeri ve optimum tasarım bilinmiyor',ha='center',fontsize=10)
    ax.set_yticks([1,2],['Eğim sınırlı\nM = 0,00002','Eğim sınırsız']);ax.set_ylim(.2,2.8);ax.set_xlim(-.55,7.2)
    ax.set_xlabel('Büyütülmüş koordinat: (değişiklik / L − 1) × 10⁶\nL = 9,1787079603827 × 10⁻¹⁰',fontsize=10)
    ax.set_title('Yeni aralığın büyütülmüş görünümü',loc='left',fontweight='bold');ax.grid(axis='x',alpha=.2)
    fig.suptitle('Değişme hızı sınırlıyken eşik artık dar bir aralıkta',fontsize=16,fontweight='bold',y=1.01)
    fig.text(.5,.005,'Kanıtlı sınırlar gösteriliyor; noktalar veya çizgiler hesaplanmış bir optimum eğri değildir.',ha='center',fontsize=9,color='#4d5963')
    fig.tight_layout(rect=[0,.04,1,.97])
    for ext in ['png','svg']:fig.savefig(out/('finite_slope_threshold.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig)
    alpha=mid(c['alpha']);eta=mid(c['smoothing_width']);knots=np.array(list(map(mid,c['breakpoints'])))
    w=np.array(list(map(mid,c['correction_weights'])));freq=np.array(c['correction_frequencies']);ds=-2*(-1.)**np.arange(len(knots))
    def values(u):
        z=(u[:,None]-knots)/eta;zminus=(-u[:,None]-knots)/eta
        step=1+((1+np.tanh(z))/2+(1+np.tanh(zminus))/2)@ds
        sder=((1-np.tanh(z)**2)-(1-np.tanh(zminus)**2))@ds/(2*eta)
        h=-alpha*step+np.cos(2*u[:,None]*freq)@w
        dh=-alpha*sder+(-2*freq*np.sin(2*u[:,None]*freq))@w
        return h,dh
    fig,axes=plt.subplots(1,2,figsize=(12,4.5));v=np.linspace(-5,5,1401);u=knots[0]+eta*v;h,dh=values(u)
    axes[0].plot(v,h/alpha,color='#006b83',lw=2.5);axes[0].set_ylabel('h(u) / α');axes[0].set_title('İlk geçişteki uygun tasarım',loc='left',fontweight='bold')
    axes[1].plot(v,dh/2e-5,color='#995220',lw=2.5);axes[1].axhline(1,color='#777777',ls='--',lw=1,label='İzin verilen üst sınır')
    axes[1].set_ylabel('h′(u) / M');axes[1].set_title('Aynı geçişin değişme hızı',loc='left',fontweight='bold');axes[1].legend(fontsize=9)
    for ax in axes:ax.set_xlabel('(u − c₁) / η');ax.grid(alpha=.2)
    axes[0].set_ylim(-1.1,1.1);axes[1].set_ylim(-.04,1.1)
    fig.suptitle('Düzgün tasarım: ani sıçrama yerine sonlu genişlikte geçiş',fontsize=15,fontweight='bold')
    fig.text(.5,.005,'Bu grafik bir uygun adayı örnekler. Global norm, eğim ve moment koşulları grafikten değil sertifikadan gelir.',ha='center',fontsize=9,color='#4d5963')
    fig.tight_layout(rect=[0,.045,1,.95])
    for ext in ['png','svg']:fig.savefig(out/('smooth_design_transition.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig)
if __name__=='__main__':main()
