"""Small rational interval substrate. No floating point in interval operations."""
from fractions import Fraction as F

class QI:
    def __init__(self, lo, hi=None):
        if isinstance(lo,QI):
            self.lo,self.hi=lo.lo,lo.hi
        else:
            self.lo=F(lo); self.hi=F(lo if hi is None else hi)
        assert self.lo<=self.hi
    def __add__(self,o):
        o=QI(o);return QI(self.lo+o.lo,self.hi+o.hi)
    __radd__=__add__
    def __neg__(self):return QI(-self.hi,-self.lo)
    def __sub__(self,o):return self+-QI(o)
    def __rsub__(self,o):return QI(o)+-self
    def __mul__(self,o):
        o=QI(o);v=[x*y for x in [self.lo,self.hi] for y in [o.lo,o.hi]]
        return QI(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=QI(o);assert o.lo>0 or o.hi<0,'Division by an interval containing zero.'
        return self*QI(1/o.hi,1/o.lo)
    def __rtruediv__(self,o):return QI(o)/self
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        if n==0:return QI(1)
        if n%2:return QI(self.lo**n,self.hi**n)
        return QI(0 if self.lo<=0<=self.hi else min(self.lo**n,self.hi**n),
                  max(self.lo**n,self.hi**n))
    def data(self):return [str(self.lo),str(self.hi)]
    def overlaps(self,o):
        o=QI(o);return max(self.lo,o.lo)<=min(self.hi,o.hi)
    @classmethod
    def from_data(cls,pair):return cls(*pair)

def poly_integral(coefficients,left,right):
    return sum((c*(right**(k+1)-left**(k+1))/F(k+1)
                for k,c in enumerate(coefficients)),0)

def multiply(p,q):
    out=[0]*(len(p)+len(q)-1)
    for i,c in enumerate(p):
        for j,d in enumerate(q):out[i+j]=out[i+j]+c*d
    return out

def five_piece_moment(q,cm,cp,a):
    """Direct integral of q against + / descending / - / ascending / +."""
    return (poly_integral(q,-1,cm-a)
        +poly_integral(multiply(q,[cm/a,-1/a]),cm-a,cm+a)
        -poly_integral(q,cm+a,cp-a)
        +poly_integral(multiply(q,[-cp/a,1/a]),cp-a,cp+a)
        +poly_integral(q,cp+a,1))
