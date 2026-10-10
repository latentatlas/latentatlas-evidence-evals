#!/usr/bin/env python3
"""Plot certified bounds, never an invented optimal-value curve."""
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
d=json.loads((HERE/'results/budget_check.json').read_text())
p={k:float(Fraction(v)) for k,v in d['plotting_parameters'].items()}
L,U1,U2,M1,M2=p['L'],p['U1'],p['U2'],p['M1'],p['M2']
ms=np.unique(np.r_[np.logspace(-12,1,700),M1,M2])
ell=np.minimum(p['radius'],L/ms)
lo=np.maximum.reduce([np.full_like(ms,L),1-p['kappa']*ms,
    (p['f3_lower']+p['loss_coefficient']*(L*ell**2-2*ms*ell**3/3))/p['dual_upper']])
hi=np.where(ms<=M1,1-ms/M1*(1-U1),np.where(ms<=M2,U1+(ms-M1)/(M2-M1)*(U2-U1),U2))
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'svg.fonttype':'none','font.family':'DejaVu Sans'})
fig,axes=plt.subplots(1,2,figsize=(12,4.8),gridspec_kw={'width_ratios':[1.65,1]},layout='constrained')
ax=axes[0]
ax.fill_between(ms,lo,hi,color='#e7ebf0',label='Unresolved between proved bounds')
ax.loglog(ms,hi,color='#1c6b94',lw=2,label='Feasible smooth upper bound')
ax.loglog(ms,lo,color='#b45235',lw=1.8,label='Universal lower bound')
ax.axhline(L,color='#50545b',ls='--',lw=1,label=r'Unrestricted certified lower bound $L$')
ax.scatter([M1,M2],[U1,U2],s=38,color='#1c6b94',zorder=4)
ax.annotate('R11 witness',xy=(M1,U1),xytext=(2e-8,2e-6),arrowprops={'arrowstyle':'-','color':'#66717d'})
ax.annotate('R12 witness',xy=(M2,U2),xytext=(2e-2,8e-9),arrowprops={'arrowstyle':'-','color':'#66717d'})
ax.set(xlabel=r'Slope budget $M$ in the original $u$ coordinate',ylabel=r'Amplitude cost $\delta(M)$',
       title='Certified bounds under a slope constraint',xlim=(1e-12,10),ylim=(6e-10,1.6))
ax.grid(alpha=.18,which='major');ax.legend(fontsize=8,loc='upper right')

ax=axes[1]
free_width=(U2/L-1)*1e8
finite_low=float(Fraction(d['M_2e_minus5_lower']))
z=(finite_low/L-1)*1e8
ax.plot([0,free_width],[1,1],lw=8,color='#50545b',solid_capstyle='butt')
ax.scatter([free_width/2],[1],marker='|',s=160,color='#50545b',linewidths=2,zorder=4)
ax.scatter([z],[0],s=50,color='#b45235',zorder=4)
ax.annotate('',xy=(8.1,0),xytext=(z,0),arrowprops={'arrowstyle':'->','color':'#b45235','lw':2})
ax.text(.2,1.15,'R12: unrestricted threshold bracket',fontsize=9)
ax.text(.2,.8,'Bracket width < 0.005 on this axis',fontsize=8,color='#50545b')
ax.text(z,.2,'Finite-budget lower bound',ha='center',fontsize=9,color='#94472e')
ax.text(4,-.4,'Upper bound is much farther right.\nThe finite-budget optimum is not located.',
        ha='center',fontsize=8,color='#50545b')
ax.set(xlim=(-.25,8.4),ylim=(-.65,1.55),yticks=[0,1],
       yticklabels=[r'$M=2\times10^{-5}$','Unrestricted'],
       xlabel=r'$(\mathrm{cost}/L-1)\,10^8$',title='A strictly positive cost separation')
ax.grid(axis='x',alpha=.18)
fig.suptitle('Same exact cusp point • amplitude and slope are distinct constraints',fontsize=13)
(HERE/'figures').mkdir(exist_ok=True)
for suffix in ['png','svg']:
    fig.savefig(HERE/'figures'/('slope_budget_bounds.'+suffix),dpi=180)
plt.close(fig)
