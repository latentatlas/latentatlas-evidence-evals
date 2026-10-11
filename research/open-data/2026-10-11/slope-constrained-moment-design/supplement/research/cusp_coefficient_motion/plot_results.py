#!/usr/bin/env python3
"""Scientific figure: proved motion cone and positive derivative enclosure."""
import sys
sys.dont_write_bytecode=True
import hashlib,json
from pathlib import Path
from fractions import Fraction as F
import mpmath as mp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=HERE/'results/plot_data.json'
    if out.exists():raise FileExistsError(out)
    cp=HERE/'results/certificate.json';dp=HERE/'results/direct_check.json';direct=json.loads(dp.read_text())
    mp.mp.dps=80;data=direct['runs'][1];center=next(x for x in data['evaluations'] if F(x['nu'])==0)
    C0=mp.mpf(center['coefficients']['C4']);samples=[]
    for row in sorted(data['evaluations'],key=lambda r:F(r['nu'])):
        change=10**6*(mp.mpf(row['coefficients']['C4'])/C0-1)
        samples.append({'nu':row['nu'],'C4':row['coefficients']['C4'],'relative_change_ppm':mp.nstr(change,70)})
    lo,hi=F('2.82e-40'),F('4.35e-40');Clo,Chi=F('2.49203004e-39'),F('2.49203006e-39')
    grid=[-F(1,65536)+F(k,200*65536) for k in range(201)]
    lower=[10**6*x*hi/Clo for x in grid];upper=[10**6*x*lo/Chi for x in grid]
    derivative=[{'nu':r['nu'],'C4_prime_finite_difference':r['steps'][1]['derivatives']['C4']} for r in data['rows']]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.hashsalt':'r28-cusp-coefficient-motion'})
    fig,ax=plt.subplots(1,2,figsize=(13,5.8));fig.subplots_adjust(left=.08,right=.97,bottom=.25,top=.75,wspace=.25)
    fig.suptitle('The fourth coefficient increases along the short cusp arc',fontsize=17,y=.98)
    fig.text(.5,.875,r'$-2^{-16}\leq\nu\leq 0\qquad 2.82\times10^{-40}<C_4^{\prime}(\nu)<4.35\times10^{-40}$',ha='center',fontsize=14)
    xs=np.array([float(x*10**6) for x in grid]);ax[0].fill_between(xs,list(map(float,lower)),list(map(float,upper)),color='#c8e6e3',label='Proved bounds from the derivative')
    ax[0].plot(xs,list(map(float,lower)),color='#16867d',lw=1.5);ax[0].plot(xs,list(map(float,upper)),color='#16867d',lw=1.5)
    ax[0].scatter([float(F(r['nu'])*10**6) for r in samples],[float(r['relative_change_ppm']) for r in samples],color='#c87826',s=20,zorder=3,label='Original-integral samples')
    ax[0].set(title='Quantified change from the endpoint',xlabel=r'Cusp driver $10^6\nu$',ylabel=r'$10^6[C_4(\nu)/C_4(0)-1]$  (ppm)',xlim=(xs[0]-.3,.3),ylim=(-3.0,.18))
    ax[0].legend(loc='upper left',fontsize=9,framealpha=.95)
    ax[1].fill_between(xs,2.82,4.35,color='#c8e6e3');ax[1].hlines([2.82,4.35],xs[0],0,color='#16867d',lw=1.5)
    ax[1].scatter([float(F(r['nu'])*10**6) for r in derivative],[float(r['C4_prime_finite_difference'])*1e40 for r in derivative],color='#c87826',s=32,zorder=3)
    ax[1].axhline(0,color='#666',lw=1)
    ax[1].text(.04,.37,'The whole derivative band\nstays strictly above zero.',transform=ax[1].transAxes,fontsize=11)
    ax[1].set(title='A common derivative bound on the entire arc',xlabel=r'Cusp driver $10^6\nu$',ylabel=r'$10^{40}C_4^{\prime}(\nu)$',xlim=(xs[0]-.3,.3),ylim=(-.2,4.8))
    for a in ax:
        a.grid(alpha=.19);a.set_axisbelow(True);a.spines[['right','top']].set_visible(False)
    fig.text(.08,.13,'Green regions are analytic + validated interval bounds for every driver on this arc.',fontsize=11)
    fig.text(.08,.08,'Orange points are separate numerical diagnostics: integral values (left), two-step finite differences (right).',fontsize=10,color='#566170')
    fig.text(.08,.035,'This is a theorem about the coefficient C₄ in the original ν coordinate; it does not assert monotonicity of the finite-M optimum.',fontsize=9.6,color='#566170')
    for suffix in ['png','svg']:
        path=HERE/'figures'/('coefficient_motion.'+suffix)
        if path.exists():raise FileExistsError(path)
        fig.savefig(path,dpi=180,metadata={'Date':None} if suffix=='svg' else {})
    plt.close(fig)
    payload={'status':'R28_scientific_motion_plot','source_sha256':sha(__file__),'certificate_sha256':sha(cp),'direct_check_sha256':sha(dp),
      'samples':samples,'derivative_diagnostics':derivative,'cone_grid':[str(x) for x in grid],
      'cone_lower_ppm':list(map(str,lower)),'cone_upper_ppm':list(map(str,upper)),
      'green_regions_are_uniform_bounds':True,'orange_points_are_diagnostics':True,
      'finite_M_optimum_monotonicity_claimed':False,'figures':{p.name:sha(p) for p in sorted((HERE/'figures').iterdir())}}
    out.write_text(json.dumps(payload,indent=2)+'\n');print(payload['status'])
if __name__=='__main__':main()
