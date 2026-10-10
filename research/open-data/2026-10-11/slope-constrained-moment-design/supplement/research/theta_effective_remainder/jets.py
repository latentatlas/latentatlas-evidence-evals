"""R25 interval derivatives through order five; infinite theta series included."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from math import comb,factorial
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'theta_fourth_order'))
from interval_core import restore,pack,rational,zero_ball,upper,absup
from flint import arb

def sm(xs):return sum(xs,arb(0))
def theta_polynomials(order):
    out=[[-3,2]]
    for _ in range(order):
        p=out[-1];n=[0]*(len(p)+1)
        for i,c in enumerate(p):n[i]+=(5+4*i)*c;n[i+1]-=4*c
        out.append(n)
    return out

def pjets(u,tau,order=5):
    phase=2*tau*u;trig=[phase.cos(),-phase.sin(),-phase.cos(),phase.sin()]
    return [[sm(comb(l,h)*factorial(j)//factorial(j-h)*2**j*u**(j-h)*(2*tau)**(l-h)*trig[(j+l-h)%4]
                for h in range(min(j,l)+1)) for l in range(order+1)] for j in range(4)]

def jet(u,params,b,order=5,root=False):
    tau,lam,mu=params;pi=arb.pi();N=12;polys=theta_polynomials(order)
    phi=[arb(0) for _ in polys];errors=[]
    for n in range(1,N+1):
        x=pi*n*n*(4*u).exp();fac=pi*n*n*(5*u-x).exp()
        for l,P in enumerate(polys):phi[l]+=fac*sm(c*x**i for i,c in enumerate(P))
    lo,hi=u.lower(),u.upper();assert lo>=0;n=N+1
    # For k>=13, all absolute monomial ratios are <=(14/13)^14 exp(-27*pi)<1/2.
    for l,P in enumerate(polys):
        err=upper(2*sm(abs(c)*pi**(i+1)*n**(2*i+2)*((5+4*i)*hi-pi*n*n*(4*lo).exp()).exp()
                       for i,c in enumerate(P)))
        errors.append(err);phi[l]+=zero_ball(err)
    pd=[lam*u*u+mu*u**4,2*lam*u+4*mu*u**3,2*lam+12*mu*u*u,24*mu*u,24*mu]+[arb(0)]*order
    E=[arb(1)]
    for n in range(order):E.append(sm(comb(n,k)*pd[k+1]*E[n-k] for k in range(n+1)))
    ep=pd[0].exp();w=[ep*sm(comb(l,k)*phi[k]*E[l-k] for k in range(l+1)) for l in range(order+1)]
    p=pjets(u,tau,order);raw=[p[3][l]-sm(b[j]*p[j][l] for j in range(3)) for l in range(order+1)]
    q=[[sm(comb(l,k)*w[k]*p[j][l-k] for k in range(l+1)) for l in range(order+1)] for j in range(4)]
    if root:
        assert raw[0].contains(0)
        # This exact identity is used only for derivatives at the enclosed true root.
        raw[0]=arb(0)
    qr=[sm(comb(l,k)*w[k]*raw[l-k] for k in range(l+1)) for l in range(order+1)]
    return {'interval':u,'moment_jets':q,'residual_jets':qr,'weight_jets':w,
            'p_jets':p,'theta_omission_bounds':errors,'at_true_root':root}
