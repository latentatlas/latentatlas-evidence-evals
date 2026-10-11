"""Cancellation-preserving sign proof for the cusp opening coefficient."""
from math import factorial
from flint import arb
from geometry_model import upper,zero_ball


class Polynomial:
    def __init__(self,c): self.c=list(c) if isinstance(c,(tuple,list)) else [arb(c)]
    @staticmethod
    def of(v): return v if isinstance(v,Polynomial) else Polynomial(v)
    def __add__(self,other):
        b=self.of(other);out=[arb(0)]*max(len(self.c),len(b.c))
        for i,a in enumerate(self.c): out[i]+=a
        for i,a in enumerate(b.c): out[i]+=a
        return Polynomial(out)
    __radd__=__add__
    def __neg__(self): return Polynomial([-v for v in self.c])
    def __sub__(self,other): return self+-self.of(other)
    def __rsub__(self,other): return self.of(other)+-self
    def __mul__(self,other):
        b=self.of(other);out=[arb(0)]*(len(self.c)+len(b.c)-1)
        for i,a in enumerate(self.c):
            for j,v in enumerate(b.c): out[i+j]+=a*v
        return Polynomial(out)
    __rmul__=__mul__


class Dual:
    def __init__(self,value,grad=None):
        self.value=value
        self.grad=list(grad) if grad is not None else [arb(0)]*8
    @staticmethod
    def of(v): return v if isinstance(v,Dual) else Dual(arb(v))
    def __add__(self,other):
        b=self.of(other)
        return Dual(self.value+b.value,[a+v for a,v in zip(self.grad,b.grad)])
    __radd__=__add__
    def __neg__(self): return Dual(-self.value,[-v for v in self.grad])
    def __sub__(self,other): return self+-self.of(other)
    def __rsub__(self,other): return self.of(other)+-self
    def __mul__(self,other):
        b=self.of(other)
        return Dual(self.value*b.value,[a*b.value+self.value*v for a,v in zip(self.grad,b.grad)])
    __rmul__=__mul__


def numerator(d):
    """N with k' = N/(64 D3^2 D4^3), k=-D3/D4, at a cusp."""
    a,b,c,d6,e,f,g,h=d
    return ((a*c-b*b)*(a*b*f+b*c*d6-b*b*e-a*d6*d6)
            +(b*c-a*d6)*(c*d6-b*e)*a
            +(a*f-b*e)*d6*a*a+(b*g-a*h)*a*a*b)


def partials(d):
    args=[]
    for i,v in enumerate(d):
        grad=[arb(j==i) for j in range(8)]
        args.append(Dual(v,grad))
    return numerator(args).grad


def certify_shape(cell,cusp_bounds):
    # Fixed positive scale reduces sizes without altering the sign or
    # the homogeneous quotient for k'.
    scale=cell.c[3].mid()
    if not scale>0: raise ArithmeticError('Positive scale required')
    polynomials=[];errors=[]
    for n in range(3,11):
        polynomials.append(Polynomial([sum((a*cell.c[n+s] for s,a in cell.A[p].items()),arb(0))
                                      /(factorial(p)*scale) for p in range(cell.K)]))
        errors.append(upper(cell.h**cell.K/factorial(cell.K)*sum(
            (abs(a)*cell.B[n+s] for s,a in cell.A[cell.K].items()),arb(0))/scale))
    poly=numerator(polynomials)
    polynomial_bound=poly.c[0]+zero_ball(sum((abs(a)*cell.h**i
                                  for i,a in enumerate(poly.c) if i),arb(0)))
    d=[v/scale for v in cusp_bounds]
    # Mean-value bound for replacing the polynomial jets by the exact
    # derivatives on the affine predictor. The enlarged interval contains
    # both endpoint vectors and their straight segment in derivative space.
    grad=partials([d[n]+zero_ball(errors[n-3]) for n in range(3,11)])
    jet_error=upper(sum((abs(a)*e for a,e in zip(grad,errors)),arb(0)))
    # The actual cusp lies at predictor+w, |w_i|<=old tight radius.
    # Apply the spatial chain rule to N, preserving its linear sums.
    grad_actual=partials(d[3:11])
    chain=[sum((grad_actual[n-3]*d[n+shift]*factor for n in range(3,11)),arb(0))
           for shift,factor in ((1,arb(1)),(2,-arb(1)/4),(4,arb(1)/16))]
    root_error=upper(sum((abs(a)*r for a,r in zip(chain,cell.tight)),arb(0)))
    N=polynomial_bound+zero_ball(jet_error+root_error)
    kprime=N/(64*d[3]*d[3]*d[4]*d[4]*d[4])
    return {'N':N,'kprime':kprime,'Cprime':8*arb(2).sqrt()/3*kprime,
            'polynomial_coefficients':poly.c,'jet_error':jet_error,
            'root_error':root_error,'jet_remainders':errors,'scale':scale,
            'spatial_gradient':chain}
