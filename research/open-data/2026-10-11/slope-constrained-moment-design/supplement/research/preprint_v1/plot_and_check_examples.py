#!/usr/bin/env python3
"""Fresh polynomial integrals, scalar inversion diagnostics, and paper figures."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
from fractions import Fraction as F
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
mp.mp.dps = 90

def two_switch(a, beta=mp.mpf(1)/4):
    d = -beta*a*a/(1+mp.sqrt(1-3*beta*beta*a*a))
    centers = [d-mp.mpf(".5"), d+mp.mpf(".5")]
    coeff = [-mp.mpf(1)/4, -beta/4, mp.mpf(1), beta]
    def primitive(x, shift=0):
        return sum(c*x**(i+1+shift)/(i+1+shift) for i,c in enumerate(coeff))
    def integral(l, r): return primitive(r)-primitive(l)
    def ramp(c, sig):
        return sig*(primitive(c+a,1)-primitive(c-a,1)-c*integral(c-a,c+a))/a
    c0,c1=centers
    s = (integral(-1,c0-a)+ramp(c0,-1)-integral(c0+a,c1-a)
         +ramp(c1,1)+integral(c1+a,1))
    return mp.mpf(1)/8/s, centers

def negative(a):
    return (mp.mpf(5)/8)/(mp.mpf(5)/2-a*a/3+3*a**4/10-3*a**6/7)

def main():
    figs=HERE/"figures"; figs.mkdir(exist_ok=True)
    checks=[]
    # Exact paper constants are evaluated without the inherited certificate helper.
    G,B,R,P=F(256,63),F(244,189),F(134,567),F(3721,18144)
    assert B*B/(2*G)==P and R-P==F(1,32)
    assert F(1,4)**5*(F(16,3)-F(1,16))==F(253,49152)
    M0=F("2e-5")
    assert F("1.02e-53")/M0**6==F("1.59375e-25")
    assert F("1.64e-53")/M0**6==F("2.5625e-25")
    assert F("9.181e-10")/M0<F(1,16384)
    assert F("9.17e-10")*F(".02259")>F("2.07e-11")
    for astr in [".12",".05",".01"]:
        a=mp.mpf(astr); A,cs=two_switch(a); beta=mp.mpf(1)/4
        q=lambda x:(x*x-mp.mpf(".25"))*(1+beta*x)
        cuts=[-mp.mpf(1),cs[0]-a,cs[0]+a,cs[1]-a,cs[1]+a,mp.mpf(1)]
        profiles=[lambda x:mp.mpf(1),lambda x:-(x-cs[0])/a,
                  lambda x:-mp.mpf(1),lambda x:(x-cs[1])/a,
                  lambda x:mp.mpf(1)]
        mean=sum(mp.quad(profiles[i],[cuts[i],cuts[i+1]]) for i in range(5))
        target=sum(mp.quad(lambda x,i=i:q(x)*profiles[i](x),
                           [cuts[i],cuts[i+1]]) for i in range(5))
        balance=[mp.quad(q,[c-a,c+a]) for c in cs]
        # The multiplier shifts the residual; the two q1 averages agree.
        assert abs(balance[0]-balance[1])<mp.mpf("1e-80")
        assert abs(mean)<mp.mpf("1e-80")
        assert abs(A*target-mp.mpf(1)/8)<mp.mpf("1e-80")
        checks.append({"a":astr,"mean":str(mean),"target_error":str(A*target-mp.mpf(1)/8),
                       "balance_difference":str(balance[0]-balance[1])})
    rows=[]
    c4a=mp.mpf(253)/49152; c4b=-mp.mpf(1)/15360
    for a in [mp.mpf(str(x)) for x in np.geomspace(.001,.15,180)]:
        aa,_=two_switch(a); ab=negative(a); ma=aa/a; mb=ab/a
        ra=(aa-mp.mpf(".25")-1/(48*ma*ma))*ma**4/c4a
        rb=(ab-mp.mpf(".25")-1/(480*mb*mb))*mb**4/abs(c4b)
        rows.append([float(ma),float(ra),float(mb),float(rb)])
    assert abs(rows[0][1]-1)<1e-4 and abs(rows[0][3]+1)<1e-4
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,
                         "axes.spines.top":False,"axes.spines.right":False})
    fig,ax=plt.subplots(1,2,figsize=(10,3.5),layout="constrained")
    a=.12; _,centers=two_switch(mp.mpf(".12")); c0,c1=map(float,centers)
    x=np.linspace(-1,1,1500)
    s=1-np.clip((x-(c0-a))/a,0,2)+np.clip((x-(c1-a))/a,0,2)
    ax[0].plot(x,s,color="#16697A",lw=2.2)
    ax[0].axhline(0,color=".8",lw=.7); ax[0].set(xlabel="x",ylabel="Normalized profile s(x)",ylim=(-1.2,1.2))
    ax[0].set_title("Two switches with exact mean balance")
    r=np.array(rows)
    ax[1].semilogx(r[:,0],r[:,1],color="#16697A",label="Two-switch example")
    ax[1].semilogx(r[:,2],r[:,3],color="#B65C25",label="Odd polynomial example")
    ax[1].axhline(1,color="#16697A",ls="--",lw=.8);ax[1].axhline(-1,color="#B65C25",ls="--",lw=.8)
    ax[1].set(xlabel="Slope budget M",ylabel="Fourth residual / |C4|",ylim=(-1.35,1.35))
    ax[1].set_title("Either sign of the fourth coefficient")
    ax[1].legend(fontsize=8,loc="center right",frameon=False)
    fig.savefig(figs/"examples.pdf",metadata={"CreationDate":None})
    fig.savefig(figs/"examples.png",dpi=180)
    plt.close(fig)
    d=np.linspace(0,1/64,200)
    lower=(2.7e-11+7.4e-26/float(M0)**2+1.9e-40/float(M0)**4)*d-2.66e-53/float(M0)**6
    upper=(3e-11+8.7e-26/float(M0)**2+5.3e-40/float(M0)**4)*d+2.66e-53/float(M0)**6
    fig,ax=plt.subplots(figsize=(7,3.4),layout="constrained")
    ax.fill_between(d*64,lower/1e-13,upper/1e-13,color="#A7D4CF",label="Coefficient + remainder enclosure")
    ax.plot(d*64,2.07e-11*d/1e-13,color="#B65C25",ls="--",label="Transport lower bound")
    ax.set(xlabel=r"Parameter distance 64d, where d = $\nu_2-\nu_1$",
           ylabel=r"Value difference / $10^{-13}$",xlim=(0,1))
    ax.legend(frameon=False,fontsize=9)
    fig.savefig(figs/"theta_comparison.pdf",metadata={"CreationDate":None})
    fig.savefig(figs/"theta_comparison.png",dpi=180);plt.close(fig)
    report={"exact_rational_checks":7,"fresh_integral_cases":checks,"diagnostic_precision":90,
            "figure_rows":rows,"not_interval_certified":True,
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "figures":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(figs.iterdir())}}
    (HERE/"example_checks.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":"passed","exact_rational_checks":7,"fresh_integral_cases":len(checks),"figures":len(report["figures"])}))
if __name__=="__main__":main()
