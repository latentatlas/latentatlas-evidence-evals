#!/usr/bin/env python3
"""Static scientific figures: exact normalized mechanism and certified weights."""
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
    m,e=v['mid_man_exp'];return m*2.**e
def save(fig,name):
    folder=HERE/'figures';folder.mkdir(exist_ok=True)
    for ext in ['png','svg']:fig.savefig(folder/(name+'.'+ext),dpi=180,facecolor='white')
    plt.close(fig)
def main():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,
        'axes.labelcolor':'#253446','text.color':'#253446','axes.titleweight':'bold','svg.hashsalt':'R15'})
    blue='#245c8e';orange='#ca5b28';grey='#778492'
    x=np.linspace(-1.6,1.6,1001);ramp=np.clip(x,-1,1)
    fig,ax=plt.subplots(1,2,figsize=(11.6,4.9));fig.subplots_adjust(left=.075,right=.975,bottom=.235,top=.79,wspace=.32)
    fig.suptitle('Why a slope limit creates a quadratic cost',fontsize=17,fontweight='bold',y=.96)
    fig.text(.5,.878,r'One simple switch, scaled by its transition half-width $a\sim\delta_*/M$',ha='center',fontsize=11)
    ax[0].plot([-1.6,0,0,1.6],[-1,-1,1,1],color=grey,ls='--',lw=1.7,label='Discontinuous sign')
    ax[0].plot(x,ramp,color=orange,lw=2.7,label='Linear transition')
    ax[0].set(xlim=(-1.6,1.6),ylim=(-1.22,1.25),xlabel=r'$x=(u-z)/a$',ylabel='Normalized sign',title='A. Replace the jump')
    ax[0].legend(loc='lower right',fontsize=9,frameon=False);ax[0].set_xticks([-1,0,1]);ax[0].set_yticks([-1,0,1])
    ax[0].grid(alpha=.15);ax[0].text(-1.48,.65,r'$|s_a^\prime|=1/a$',fontsize=12)
    loss=np.maximum(0,np.abs(x)*(1-np.abs(x)))
    ax[1].fill_between(x,0,loss,color=blue,alpha=.22);ax[1].plot(x,loss,color=blue,lw=2.4)
    ax[1].set(xlim=(-1.6,1.6),ylim=(0,.38),xlabel=r'$x=(u-z)/a$',ylabel='Normalized dual-loss density',title='B. Integrate the loss')
    ax[1].set_xticks([-1,0,1]);ax[1].grid(alpha=.15)
    ax[1].text(0,.322,r'$\int_{-1}^{1}|x|(1-|x|)\,dx=1/3$',ha='center',fontsize=13)
    fig.text(.5,.113,r'Local loss $\sim\delta_* a^2 w(z)|r_*^\prime(z)|/3$; summing and dividing by $D_*$ gives $C_*/M^2$.',ha='center',fontsize=11)
    fig.text(.5,.048,'Schematic of the asymptotic construction. It does not identify an exact finite-slope optimizer.',ha='center',fontsize=9,color=grey)
    save(fig,'linear_transition_loss')
    c=json.loads((HERE/'results/asymptotic_certificate.json').read_text())
    z=np.array([mid(r['root_interval']) for r in c['uniform_roots']]);weights=np.array([mid(r['gamma_contribution']) for r in c['uniform_roots']])
    total=mid(c['weighted_root_sum']);percent=100*weights/total
    fig,ax=plt.subplots(1,2,figsize=(11.6,4.9),gridspec_kw={'width_ratios':[1.7,1]})
    fig.subplots_adjust(left=.073,right=.975,bottom=.24,top=.78,wspace=.28)
    fig.suptitle('Which switches determine the leading coefficient?',fontsize=17,fontweight='bold',y=.96)
    fig.text(.5,.878,r'Positive weights $\gamma_k=w(z_k)|r_*^\prime(z_k)|$, with $\Gamma=\sum_k\gamma_k\approx1.297542119$',ha='center',fontsize=11)
    ax[0].bar(z,percent,width=.009,color=blue,alpha=.9)
    ax[0].set(xlim=(-.015,1.015),ylim=(0,20),xlabel=r'Switch location $z_k$ in the original $u$ coordinate',ylabel=r'Share of $\Gamma$ (%)',title='A. Individual switch contributions')
    ax[0].grid(axis='y',alpha=.16)
    for k in [1,2,6,7,8]:ax[0].annotate(str(k+1),(z[k],percent[k]),xytext=(0,5),textcoords='offset points',ha='center',fontsize=8)
    ax[0].text(.57,14,'28 certified switches\nin $[0,1]$; labels\nshow switch indices.',fontsize=10,linespacing=1.6,color=grey)
    ax[1].step(np.r_[0,z,1],np.r_[0,np.cumsum(percent),np.sum(percent)],where='post',color=orange,lw=2.4)
    ax[1].set(xlim=(0,1),ylim=(0,104),xlabel=r'Upper switch location',ylabel='Cumulative share (%)',title='B. Accumulated contribution')
    ax[1].grid(alpha=.16);ax[1].set_yticks([0,25,50,75,100])
    fig.text(.5,.12,r'The infinite tail beyond $u=1$ is included analytically: $\Gamma_{\rm tail}<5.705\times10^{-63}$.',ha='center',fontsize=10)
    fig.text(.5,.058,'Plotted values are interval midpoints; enclosure widths are below drawing resolution. These are dual-residual zeros, not zeros of F.',ha='center',fontsize=8.8,color=grey)
    save(fig,'switch_contributions')
    print('Two PNG/SVG scientific figures written; require visual inspection before closure.')
if __name__=='__main__':main()
