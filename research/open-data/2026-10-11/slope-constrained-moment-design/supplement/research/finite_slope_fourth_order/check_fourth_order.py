#!/usr/bin/env python3
"""Exact local Taylor algebra, normalization, independent examples and matrix tests."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent;PREV=HERE.parent/'finite_slope_optimum'
sys.path.insert(0,str(PREV))
from exact_interval import poly_integral,five_piece_moment,multiply
N=9;ZERO=(0,)*N
class P:
    def __init__(self,v=0):
        self.p=v.p.copy() if isinstance(v,P) else ({e:F(c) for e,c in v.items() if c} if isinstance(v,dict) else ({ZERO:F(v)} if v else {}))
    def __add__(self,o):
        out=self.p.copy()
        for e,v in P(o).p.items():out[e]=out.get(e,F(0))+v
        return P(out)
    __radd__=__add__
    def __neg__(self):return P({e:-v for e,v in self.p.items()})
    def __sub__(self,o):return self+-P(o)
    def __rsub__(self,o):return P(o)+-self
    def __mul__(self,o):
        out={}
        for e,v in self.p.items():
            for h,w in P(o).p.items():
                key=tuple(a+b for a,b in zip(e,h));out[key]=out.get(key,F(0))+v*w
        return P(out)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=P(o);assert len(o.p)==1
        e,v=next(iter(o.p.items()));return self*P({tuple(-a for a in e):1/v})
    def __rtruediv__(self,o):return P(o)/self
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        out=P(1)
        for _ in range(n):out=out*self
        return out
    def __eq__(self,o):return self.p==P(o).p
    def trunc(self,index,degree):return P({e:v for e,v in self.p.items() if e[index]<=degree})
    def average(self,index):
        out={}
        for e,v in self.p.items():
            assert e[index]>=0
            if e[index]%2:continue
            h=list(e);h[index]=0;h=tuple(h)
            out[h]=out.get(h,F(0))+v/F(e[index]+1)
        return P(out)
def var(i):
    e=[0]*N;e[i]=1;return P({tuple(e):1})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inverse2(A):
    det=A[0][0]*A[1][1]-A[0][1]*A[1][0];assert det
    return [[A[1][1]/det,-A[0][1]/det],[-A[1][0]/det,A[0][0]/det]]
def mv(A,v):return [sum(x*y for x,y in zip(row,v)) for row in A]
def dot(v,w):return sum(x*y for x,y in zip(v,w))
def transpose(A):return list(map(list,zip(*A)))
def mm(A,B):return [[dot(row,col) for col in zip(*B)] for row in A]
def one_moment(q,a):
    return -poly_integral(q,-1,-a)+poly_integral(multiply(q,[P(0),1/a]),-a,a)+poly_integral(q,a,1)
def run():
    groups=[]
    def check(name,ok,why):
        assert ok,name
        groups.append({'name':name,'passed':True,'reason':why})
    a,y,k,r,t,u,eta,zeta,w=[var(i) for i in range(N)]
    h=a*y+k*a**2+eta*a**3+zeta*a**4
    local=(-r*h**2/2-t*h**3/6-u*h**4/24).average(1).trunc(0,4)
    expected=-r*a**2/6-a**4*(r*k**2/2+t*k/6+u/120)
    check('local_averaged_primitive',local==expected,'Exact integration in y, including arbitrary third/fourth-order center shifts which cancel through degree four.')
    for sigma in [-1,1]:
        kap=(w-t/6)/r
        lhs=-sigma*(r*kap**2+t*kap/3+u/60)
        rhs=t**2/(36*sigma*r)-sigma*u/60-w**2/(sigma*r)
        check('completed_square_orientation_'+str(sigma),lhs==rhs,'Laurent-polynomial identity with gamma=sigma*r; both transition orientations.')
    eps,A0,tt,ee=[var(i) for i in range(4)]
    c2=A0**3*tt;c4=A0**5*(3*tt**2-ee);amp=A0+c2*eps**2+c4*eps**4
    width=eps*amp
    residual=(amp/A0-1-tt*width**2-(tt**2-ee)*width**4).trunc(0,4)
    check('implicit_budget_normalization',residual==0,'Substitute a=epsilon*A, not a=epsilon*A0, and expand through order four.')
    wrongamp=A0+c2*eps**2+A0**5*(tt**2-ee)*eps**4;wrongwidth=eps*wrongamp
    wrong=(wrongamp/A0-1-tt*wrongwidth**2-(tt**2-ee)*wrongwidth**4).trunc(0,4)
    check('normalization_negative_control',wrong!=0 and wrong==-2*A0**4*tt**2*eps**4,
          'Omitting the implicit-width feedback is detected by an exact nonzero residual.')
    # Direct five-piece integration and the balance equation in the old two-switch example.
    a=var(0);beta=var(1);d=-beta*a**2/2-F(3,8)*beta**3*a**4
    q=[P(F(-1,4)),-beta/4,P(1),beta]
    direct=five_piece_moment(q,d-F(1,2),d+F(1,2),a).trunc(0,4)
    check('two_switch_direct_target_series',direct==F(1,2)-F(2,3)*a**2+beta**2*a**4/2
          and (2*d+3*beta*d**2+beta*a**2).trunc(0,4)==0,
          'Direct five-piece antiderivatives with the independently solved center expansion.')
    D=F(1,2);Gamma=F(2);G=F(256,63);B=F(244,189)
    RR=sum(q2*q2/(36*abs(q1))-s*F(3,2)/60 for q1,q2,s in [(F(-7,8),F(5,4),-1),(F(9,8),F(11,4),1)])
    PP=B*B/(2*G);Xi=RR-PP;C2=F(1,4)**3*Gamma/(3*D);C4=F(1,4)**5*(Gamma**2/(3*D*D)-Xi/D)
    check('two_switch_general_coefficient',
          (RR,PP,Xi,C2,C4)==(F(134,567),F(3721,18144),F(1,32),F(1,48),F(253,49152)),
          'General local-jet formula matches the directly integrated a^4 coefficient.')
    negq=list(map(P,[0,1,0,-3,0,9]));negative=one_moment(negq,a)
    check('negative_coefficient_direct_integral',negative==F(5,2)-a**2/3+F(3,10)*a**4-F(3,7)*a**6
          and one_moment([P(1)],a)==0,
          'Exact three-piece integral for x-3x^3+9x^5 and its preserved constant moment.')
    negC2=F(1,4)**3/(3*F(5,2));negC4=F(1,4)**5*(F(1,3)/F(5,2)**2-F(3,10)/F(5,2))
    check('negative_C4_sign',negC2==F(1,480) and negC4==F(-1,15360),
          'A smooth admissible example disproves any universal C4 nonnegativity claim.')
    # Stress-test the matrix identity with two moments and three jet locations.
    Q=[list(map(F,v)) for v in [(1,-2),(2,1),(-1,3)]]
    primes=list(map(F,[-2,3,-5]));seconds=list(map(F,[7,-11,13]));thirds=list(map(F,[17,19,-23]))
    Qp=[list(map(F,v)) for v in [(2,1),(-3,4),(1,-2)]];sgn=[-1,1,-1]
    gram=[[2*sum(q[j]*q[l]/abs(r) for q,r in zip(Q,primes)) for l in range(2)] for j in range(2)]
    force=[sum(F(s)*(q[j]*t/r-qp[j]) for q,qp,r,t,s in zip(Q,Qp,primes,seconds,sgn))/3 for j in range(2)]
    v=mv(inverse2(gram),force)
    kap=[(dot(q,v)-t/6)/r for q,r,t in zip(Q,primes,seconds)]
    direct4=-sum(F(s)*(r*k*k+t*k/3+u/60) for s,r,t,u,k in zip(sgn,primes,seconds,thirds,kap))
    shape=sum(t*t/(36*abs(r))-F(s)*u/60 for r,t,u,s in zip(primes,seconds,thirds,sgn))
    penalty=dot(force,v)/2
    check('two_moment_matrix_identity',gram[0][0]>0 and gram[0][0]*gram[1][1]-gram[0][1]**2>0
          and direct4==shape-penalty and penalty>0,
          'Exact two-by-two Gram calculation; a finite algebra stress test, not a second fully realized integral family.')
    L=[list(map(F,row)) for row in [(2,1),(-1,1)]]
    gp=mm(mm(L,gram),transpose(L));bp=mv(L,force)
    check('moment_basis_invariance',dot(bp,mv(inverse2(gp),bp))/2==penalty,
          'Invertible change of lower-moment basis leaves the quadratic penalty unchanged.')
    # C2-only counterexample: substitute a=s^2 so all powers are integer and rational.
    s=var(0);powers=[F(1),F(5,2)];Dfrac=sum(F(2)/(p+1) for p in powers)
    frac_target=P(Dfrac)-sum(F(2)*s**int(2*(p+1))/((p+1)*(p+2)) for p in powers)
    Cfrac=F(1,4)**4*F(1,2)*F(8,63)/Dfrac
    check('fractional_regularity_counterexample',Dfrac==F(11,7)
          and frac_target==F(11,7)-s**4/3-F(8,63)*s**7
          and Cfrac==F(1,6336) and F(1,4)**3/(3*Dfrac)==F(7,2112),
          'Direct power integrals produce exponent 7/2 between the cubic and quartic scales.')
    return {'status':'fourth_order_exact_algebra_passed','check_groups':len(groups),'checks':groups,
            'two_switch':{'R':str(RR),'P':str(PP),'Xi':str(Xi),'C2':str(C2),'C4':str(C4)},
            'negative_C4':{'C2':str(negC2),'C4':str(negC4)},
            'C2_only':{'D':str(Dfrac),'C2':'7/2112','fractional_exponent':'7/2','fractional_coefficient':str(Cfrac)},
            'matrix_stress_test':{'G':[[str(x) for x in row] for row in gram],'B':list(map(str,force)),
                                  'P':str(penalty),'Xi':str(direct4),'not_an_additional_integral_example':True},
            'source_sha256':sha(Path(__file__)),'direct_integral_helper_sha256':sha(PREV/'exact_interval.py'),
            'trust_boundary':'Exact finite algebra and controlled sign/counterexample checks; does not mechanically prove the analytic asymptotic remainder or literature priority.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    data=run();args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':data['status'],'check_groups':data['check_groups']}))
if __name__=='__main__':main()
