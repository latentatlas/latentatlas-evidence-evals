#!/usr/bin/env python3
"""Scientific interval figures; no unverified optimum curve is plotted."""
import sys
sys.dont_write_bytecode=True
import json
from fractions import Fraction
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
def save(fig,name):
    folder=HERE/'figures';folder.mkdir(exist_ok=True)
    for ext in ['png','svg']:fig.savefig(folder/(name+'.'+ext),dpi=180,facecolor='white')
    plt.close(fig)
def main():
    c=json.loads((HERE/'results/remainder_check.json').read_text())
    numerical=json.loads((HERE/'results/design_crosscheck.json').read_text())['values'][-1]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,
        'axes.titleweight':'bold','text.color':'#24384a','axes.labelcolor':'#24384a','svg.hashsalt':'R16'})
    blue='#245c8e';orange='#c35b29';grey='#778594';M0=float(c['minimum_slope_budget']);CL=float(c['coefficient_bracket'][0])
    km=float(c['lower_remainder_constant_readable']);kp=float(c['upper_remainder_constant_readable'])
    factor=np.linspace(1,8,600);lower=-100*km/(CL*M0*factor);upper=100*kp/(CL*M0*factor)
    fig,ax=plt.subplots(figsize=(10.6,5.7));fig.subplots_adjust(left=.12,right=.96,bottom=.23,top=.78)
    fig.suptitle('A usable error bound for the $1/M^2$ law',fontsize=18,fontweight='bold',y=.96)
    fig.text(.5,.87,r'Certified for every $M\geq M_0=0.00002$, at the same exact cusp and moment target',ha='center',fontsize=11)
    ax.fill_between(factor,lower,upper,color=blue,alpha=.17,label='Certified admissible interval')
    ax.plot(factor,lower,color=blue,lw=2);ax.plot(factor,upper,color=blue,lw=2)
    ax.axhline(0,color=grey,ls='--',lw=1.3,label=r'Leading term $C_*/M^2$')
    value=100*float(numerical['relative_excess_deviation']);ax.scatter([1],[value],s=60,facecolor='white',edgecolor=orange,lw=2,zorder=4)
    ax.annotate('Numerical ramp witness\n(not the exact optimizer)',xy=(1,value),xytext=(4.1,.076),fontsize=9,color=orange,arrowprops=dict(arrowstyle='-',color=orange))
    ax.set(xlim=(.86,8.12),ylim=(-.065,.135),xlabel=r'Slope budget ratio $M/M_0$',ylabel=r'Deviation from $C_*/M^2$ (%)')
    ax.set_xticks([1,2,3,4,5,6,7,8]);ax.grid(alpha=.16);ax.legend(loc='upper right',frameon=False,fontsize=10)
    fig.text(.5,.112,r'The bounds apply to $[\delta(M)-\delta_*]/[C_*/M^2]-1$, not to the total kernel or total amplitude.',ha='center',fontsize=10)
    fig.text(.5,.052,'The band is an analytic enclosure, not a statistical confidence interval. The numerical witness is separate corroboration.',ha='center',fontsize=9,color=grey)
    save(fig,'remainder_envelope')
    L=Fraction('0.00000000091787079603827');U=Fraction('0.00000000091787079608363')
    oldlow=float((Fraction('0.000000000917873080')/U-1)*10**6)
    oldhigh=float((Fraction('0.000000000917876530')/L-1)*10**6)
    newlow,newhigh=map(float,c['certified_budget_examples'][0]['relative_excess_ppm_bracket'])
    fig,axes=plt.subplots(1,2,figsize=(11.2,5.1));fig.subplots_adjust(left=.095,right=.97,bottom=.27,top=.75,wspace=.32)
    fig.suptitle('A narrower certified minimum at the same slope budget',fontsize=16,fontweight='bold',y=.96)
    fig.text(.5,.865,r'$M=0.00002$; the total-threshold interval is more than $870\times$ narrower than R14',ha='center',fontsize=11)
    for ax in axes:ax.grid(axis='x',alpha=.16)
    axes[0].hlines([1,0],[oldlow,newlow],[oldhigh,newhigh],colors=[grey,blue],lw=5)
    axes[0].plot([oldlow,oldhigh],[1,1],'|',color=grey,ms=15);axes[0].plot([newlow,newhigh],[0,0],'|',color=blue,ms=15)
    axes[0].set(xlim=(2.35,6.45),ylim=(-.55,1.55),yticks=[0,1],yticklabels=['R16','R14'],xlabel=r'Extra minimum relative to $\delta_*$ (parts per million)',title='A. Previous and new bounds')
    axes[1].hlines(0,newlow,newhigh,color=blue,lw=6);axes[1].plot([newlow,newhigh],[0,0],'|',color=blue,ms=19)
    axes[1].set(xlim=(2.5048,2.5103),ylim=(-.6,.6),yticks=[0],yticklabels=['R16'],xlabel=r'Extra minimum relative to $\delta_*$ (parts per million)',title='B. Zoom into the new interval')
    axes[1].ticklabel_format(axis='x',style='plain',useOffset=False)
    axes[1].text((newlow+newhigh)/2,.22,'2.505415726 to 2.509677504 ppm',ha='center',fontsize=10)
    fig.text(.5,.125,'Both panels show proven enclosing intervals. The different horizontal scales are intentional.',ha='center',fontsize=10)
    fig.text(.5,.06,'Narrowing the enclosure improves knowledge of the same mathematical optimum; it does not change the optimum.',ha='center',fontsize=9,color=grey)
    save(fig,'threshold_comparison')
    print('Two PNG/SVG figures written; visual review required.')
if __name__=='__main__':main()
