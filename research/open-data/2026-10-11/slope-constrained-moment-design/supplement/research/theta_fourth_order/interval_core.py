"""R24 interval jets and root-based coefficients. All transcendental values use Arb."""
import sys
sys.dont_write_bytecode=True
from fractions import Fraction as F
from math import comb,factorial
from flint import arb,arb_mat,ctx

POLYS=[[-3,2],[-15,30,-8],[-75,330,-224,32]]
def rational(x):
    x=F(x);return arb(x.numerator)/arb(x.denominator)
def upper(x):return x.upper()
def absup(x):return abs(x).upper()
def zero_ball(x):
    assert x>=0
    return arb(0,x.upper())
def restore(rec):
    m,e=rec['mid_man_exp'];r,s=rec['rad_man_exp']
    return arb(m)*arb(2)**e+zero_ball(arb(r)*arb(2)**s)
def pack(x):
    if isinstance(x,arb):
        return {'enclosure':str(x),'mid_man_exp':[int(v) for v in x.mid().man_exp()],
                'rad_man_exp':[int(v) for v in x.rad().man_exp()]}
    if isinstance(x,dict):return {k:pack(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [pack(v) for v in x]
    return x
def pjets(u,tau):
    phase=2*tau*u;trig=[phase.cos(),-phase.sin(),-phase.cos(),phase.sin()]
    out=[]
    for j in range(4):
        row=[]
        for l in range(4):
            row.append(sum((comb(l,h)*factorial(j)//factorial(j-h)*2**j*u**(j-h)*(2*tau)**(l-h)*trig[(j+l-h)%4]
                            for h in range(min(j,l)+1)),arb(0)))
        out.append(row)
    return out
def residual_jets(p,b):
    return [p[3][l]-sum((b[j]*p[j][l] for j in range(3)),arb(0)) for l in range(4)]
def weight_jets(u,params,N=12):
    tau,lam,mu=params;pi=arb.pi();phi=[arb(0) for _ in range(3)]
    for n in range(1,N+1):
        x=pi*n*n*(4*u).exp();factor=pi*n*n*(5*u-x).exp()
        for l,P in enumerate(POLYS):phi[l]+=factor*sum((c*x**j for j,c in enumerate(P)),arb(0))
    lo,hi=u.lower(),u.upper();n=N+1;errors=[]
    # u>=0 and n>=13; absolute monomial ratios are bounded by 2^8 e^{-3*pi}<1/2.
    assert lo>=0
    for l,P in enumerate(POLYS):
        err=upper(2*sum((abs(c)*pi**(j+1)*n**(2*j+2)*((5+4*j)*hi-pi*n*n*(4*lo).exp()).exp()
                         for j,c in enumerate(P)),arb(0)))
        phi[l]+=zero_ball(err);errors.append(err)
    P=lam*u*u+mu*u**4;dP=2*lam*u+4*mu*u**3;ddP=2*lam+12*mu*u*u;ep=P.exp()
    w=[ep*phi[0],ep*(phi[1]+dP*phi[0]),ep*(phi[2]+2*dP*phi[1]+(dP*dP+ddP)*phi[0])]
    assert w[0]>0
    return {'weight_jets':w,'theta_derivative_series_errors':errors,'theta_terms':N}
def root_contribution(u,params,b,orientation,N=12):
    p=pjets(u,params[0]);raw=residual_jets(p,b);wdata=weight_jets(u,params,N);w,wp,wpp=wdata['weight_jets']
    rp,rpp,rppp=raw[1:];sigma=orientation
    assert sigma*rp>0
    # These are identities at the true enclosed zero, not a claim that r(u)=0 throughout its box.
    qprime=w*rp;qsecond=2*wp*rp+w*rpp;qthird=3*wpp*rp+3*wp*rpp+w*rppp
    gamma=sigma*qprime;pj=[p[j][0] for j in range(3)]
    G=[[2*w*pj[j]*pj[k]/(sigma*rp) for k in range(3)] for j in range(3)]
    B=[sigma*(wp*pj[j]+w*(pj[j]*rpp/rp-p[j][1]))/3 for j in range(3)]
    Rpos=qsecond*qsecond/(36*gamma);Rsub=sigma*qthird/60;RR=Rpos-Rsub
    # Equivalent logarithmic-jet expression, useful as an internal arithmetic guard.
    ell=wp/w;mm=wpp/w;h=rpp/rp;jj=rppp/rp
    other=gamma*((2*ell+h)**2/36-(3*mm+3*ell*h+jj)/60)
    assert (RR-other).contains(0)
    return {'root_interval':u,'orientation':sigma,'p_jets':p,'raw_residual_jets':raw,**wdata,
            'density_root_jets':[qprime,qsecond,qthird],'Gamma':gamma,'G':G,'B':B,
            'R_positive_part':Rpos,'R_subtracted_part':Rsub,'R':RR,'R_logarithmic_check':other}
