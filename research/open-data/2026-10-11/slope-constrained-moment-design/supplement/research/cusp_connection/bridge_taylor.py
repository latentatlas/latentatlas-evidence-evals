"""Taylor enclosures for affine continuation tubes in four real variables."""
from math import factorial
from flint import arb
from explore import point_cache
from validated_flow import absolute_derivative_bounds,upper,zero_ball


def operator_powers(weights,order):
    """Powers of sum weights[s]*D_t**s, by polynomial multiplication.

    Works for exact points or real balls crossing zero; no general signed
    real power operation is used.
    """
    powers=[{0:arb(1)}]
    for _ in range(order):
        row={}
        for a,value in powers[-1].items():
            for b,weight in weights.items():
                row[a+b]=row.get(a+b,arb(0))+value*weight
        powers.append(row)
    return powers


class TubeTaylor:
    def __init__(self,x,nu,v,h,radii,order=8,nmax=8):
        if order<2 or nmax<0 or not h>0 or any(not r>0 for r in radii):
            raise ValueError('Invalid Taylor tube settings')
        self.x,self.nu,self.v=list(x),arb(nu),list(v)
        self.h,self.radii,self.order,self.nmax=arb(h),list(radii),order,nmax
        if not all(a.is_exact() for a in self.x+[self.nu]+self.v):
            raise ValueError('Taylor expansion centers and predictors must be exact')
        self.half=[upper(abs(v[i])*h+radii[i]) for i in range(3)]+[h]
        # Larger domain absorbs all radius representation and arithmetic
        # widening in evaluations; derivative majorants cover this domain.
        self.allowed=[2*a for a in self.half]
        self.c=point_cache(x,nu,nmax+6*(order-1))
        params={1:x[1]+zero_ball(self.allowed[1]),
                2:x[2]+zero_ball(self.allowed[2]),
                3:nu+zero_ball(self.allowed[3])}
        self.B=absolute_derivative_bounds(params,nmax+6*order)
        self.predictor_powers=operator_powers(
            {1:v[0],2:-v[1]/4,4:v[2]/16,6:-arb(1)/64},order)

    def box_derivatives(self,upto=8):
        return self.evaluate_box([zero_ball(a) for a in self.half],upto)

    def evaluate_box(self,offsets,upto=8):
        if len(offsets)!=4 or not 0<=upto<=self.nmax:
            raise ValueError('Invalid derivative box')
        offsets=list(map(arb,offsets))
        if any(not a.is_finite() or not upper(abs(a))<=b
               for a,b in zip(offsets,self.allowed)):
            raise ValueError('Taylor request leaves the proved domain')
        powers=operator_powers({1:offsets[0],2:-offsets[1]/4,
                               4:offsets[2]/16,6:-offsets[3]/64},self.order)
        values,errors=[],[]
        for n in range(upto+1):
            polynomial=sum((sum((coef*self.c[n+s] for s,coef in powers[k].items()),arb(0))
                            /factorial(k) for k in range(self.order)),arb(0))
            remainder=upper(sum((abs(coef)*self.B[n+s] for s,coef in powers[-1].items()),arb(0))
                            /factorial(self.order))
            values.append(polynomial+zero_ball(remainder))
            errors.append(remainder)
        return values,errors

    def predictor_residual(self):
        z=zero_ball(self.h)
        zp=[arb(1)]
        for _ in range(self.order):
            zp.append(zp[-1]*z)
        out,rems=[],[]
        for n in range(3):
            # Retain the correlation of all four displacements with z.
            value=sum((zp[k]/factorial(k)*sum((coef*self.c[n+s]
                    for s,coef in self.predictor_powers[k].items()),arb(0))
                    for k in range(self.order)),arb(0))
            remainder=upper(self.h**self.order/factorial(self.order)*sum(
                (abs(coef)*self.B[n+s] for s,coef in self.predictor_powers[-1].items()),arb(0)))
            out.append(value+zero_ball(remainder))
            rems.append(remainder)
        return out,rems

    def preconditioned_defect(self,Y):
        """Enclose I-Y*J before interval dependency destroys cancellations.

        Linear combinations of central derivatives are formed first; their
        common Taylor displacement is then applied. Remainders still use
        absolute bounds and do not assume any cancellation.
        """
        offsets=[zero_ball(a) for a in self.half]
        powers=operator_powers({1:offsets[0],2:-offsets[1]/4,
                               4:offsets[2]/16,6:-offsets[3]/64},self.order)
        shifts=[1,2,4]
        factors=[arb(1),-arb(1)/4,arb(1)/16]
        out,rems=[],[]
        for i in range(3):
            row,errors=[],[]
            for j in range(3):
                value=sum((sum((coef*sum((Y[i][ell]*self.c[ell+shifts[j]+s]
                    for ell in range(3)),arb(0)) for s,coef in powers[k].items()),arb(0))
                    /factorial(k) for k in range(self.order)),arb(0))*factors[j]
                rem=upper(abs(factors[j])/factorial(self.order)*sum((abs(coef)*sum(
                    (abs(Y[i][ell])*self.B[ell+shifts[j]+s] for ell in range(3)),arb(0))
                    for s,coef in powers[-1].items()),arb(0)))
                row.append(arb(i==j)-value+zero_ball(rem))
                errors.append(rem)
            out.append(row)
            rems.append(errors)
        return out,rems
