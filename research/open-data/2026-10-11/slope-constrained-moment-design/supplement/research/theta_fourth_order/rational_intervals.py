"""Outward dyadic interval arithmetic used only by the independent R24 checker."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'finite_slope_optimum'))
from exact_interval import QI
BITS=512;SCALE=2**BITS
class RI(QI):
    def __init__(self,lo,hi=None):
        raw=QI(lo,hi);a=raw.lo*SCALE;b=raw.hi*SCALE
        self.lo=F(a.numerator//a.denominator,SCALE)
        self.hi=F(-((-b.numerator)//b.denominator),SCALE)
    def __add__(self,o):return RI(QI.__add__(self,o))
    __radd__=__add__
    def __neg__(self):return RI(-self.hi,-self.lo)
    def __sub__(self,o):return self+-RI(o)
    def __rsub__(self,o):return RI(o)+-self
    def __mul__(self,o):return RI(QI.__mul__(self,o))
    __rmul__=__mul__
    def __truediv__(self,o):return RI(QI.__truediv__(self,o))
    def __rtruediv__(self,o):return RI(o)/self
    def __pow__(self,n):return RI(QI.__pow__(self,n))
    def abs_upper(self):return max(abs(self.lo),abs(self.hi))
def restore(x):
    m,e=x['mid_man_exp'];r,s=x['rad_man_exp'];center=F(m)*F(2)**e;rad=F(r)*F(2)**s
    return RI(center-rad,center+rad)
def dot(a,b):return sum((x*y for x,y in zip(a,b)),RI(0))
def mv(A,v):return [dot(row,v) for row in A]
def mm(A,B):return [[dot(row,col) for col in zip(*B)] for row in A]
