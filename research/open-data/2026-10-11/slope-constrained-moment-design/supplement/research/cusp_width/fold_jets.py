"""Taylor jets along the exact two-control implicit fold.

Coefficients are derivatives divided by factorial. Operations support
Arb intervals or exact Fractions; no finite-difference differentiation.
"""
from math import factorial


def multiply(a,b,K):
    out=[a[0]*0]*(K+1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            if i+j<=K: out[i+j]+=x*y
    return out


def powers(a,K):
    zero=a[0]*0
    out=[[zero+1]+[zero]*K]
    for _ in range(K):out.append(multiply(out[-1],a,K))
    return out


def compose(d,n,l,m,K):
    """D_n(t+h,lambda+l(h),mu+m(h)) through h**K."""
    lp=powers([-x/4 for x in l],K)
    mp=powers([x/16 for x in m],K)
    out=[d[0]*0]*(K+1)
    for a in range(K+1):
        for b in range(K+1-a):
            for c in range(K+1-a-b):
                product=multiply(lp[b],mp[c],K)
                value=d[n+a+2*b+4*c]/(factorial(a)*factorial(b)*factorial(c))
                for k in range(K+1-a):out[k+a]+=value*product[k]
    return out


def implicit_fold(d,K=4):
    """Solve each Taylor coefficient of H=(F,F_t)=0 for controls."""
    l,m=[d[0]*0]*(K+1),[d[0]*0]*(K+1)
    aa,bb,cc,dd=-d[2]/4,d[4]/16,-d[3]/4,d[5]/16
    det=aa*dd-bb*cc
    for k in range(1,K+1):
        h0=compose(d,0,l,m,k)[k]
        h1=compose(d,1,l,m,k)[k]
        l[k]=(-dd*h0+bb*h1)/det
        m[k]=(cc*h0-aa*h1)/det
    return l,m


def divide(u,v,K):
    out=[u[0]*0]*(K+1)
    for k in range(K+1):
        out[k]=(u[k]-sum(v[j]*out[k-j] for j in range(1,k+1)))/v[0]
    return out


def transport_jet(d,lambda_cusp_prime,K=4):
    """B=(4 lambda_*' D2 + D6/4)/D4 along the fold."""
    l,m=implicit_fold(d,K)
    d2,d4,d6=[compose(d,n,l,m,K) for n in (2,4,6)]
    u=[4*lambda_cusp_prime*x+y/4 for x,y in zip(d2,d6)]
    return divide(u,d4,K),l,m
