#!/usr/bin/env python3
"""Small exact checks independent of producer formulas; not a proof assistant."""
import sys
sys.dont_write_bytecode = True
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
import argparse
import hashlib
import json

N = 5
ZERO = (0,)*N
def add(*polys):
    out = {}
    for p in polys:
        for e,c in p.items():
            out[e] = out.get(e,F(0))+c
    return {e:c for e,c in out.items() if c}
def scale(p,c): return {e:v*c for e,v in p.items() if v*c}
def mul(p,q):
    out = {}
    for e,c in p.items():
        for f,d in q.items():
            key=tuple(a+b for a,b in zip(e,f))
            out[key]=out.get(key,F(0))+c*d
    return {e:c for e,c in out.items() if c}
def var(i):
    e=list(ZERO);e[i]=1
    return {tuple(e):F(1)}
def det(matrix):
    ans={}
    for p in permutations(range(len(matrix))):
        inversions=sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))
        prod={ZERO:F((-1)**inversions)}
        for i,j in enumerate(p):prod=mul(prod,matrix[i][j])
        ans=add(ans,prod)
    return ans
def poly_integral(coef,left,right):
    return sum(c*(right**(k+1)-left**(k+1))/F(k+1) for k,c in enumerate(coef))
def multiply1(p,q):
    out=[F(0)]*(len(p)+len(q)-1)
    for i,c in enumerate(p):
        for j,d in enumerate(q):out[i+j]+=c*d
    return out
def theta_operator(p):
    # Direct differentiation of exp(5u-x) P(x), x'=4x.
    out=[F(0)]*(len(p)+1)
    for k,c in enumerate(p):
        out[k]+=(5+4*k)*c
        out[k+1]-=4*c
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    if not __debug__:raise RuntimeError('Assertions must be enabled.')
    checks=[]
    def record(name,ok,explanation):
        assert ok,name
        checks.append({'name':name,'passed':True,'explanation':explanation})
    g={n:var(n-4) for n in range(4,9)}
    # Independently form all entries from parameter derivatives at g0=...=g3=0.
    jets=lambda n:g.get(n,{})
    matrix=[[scale(jets(n+2),F(-1,4)),scale(jets(n+4),F(1,16)),
             scale(jets(n+6),F(-1,64))] for n in range(3)]
    expected=scale(mul(g[4],add(mul(g[4],g[7]),scale(mul(g[5],g[6]),-1))),F(1,4096))
    record('rank_three_determinant',det(matrix)==expected,'Permutation expansion of all six determinant terms.')
    f3,f4=var(0),var(1)
    record('cusp_control_determinant',
           det([[{},scale(f4,F(1,16))],[scale(f3,F(-1,4)),scale(var(2),F(1,16))]])==scale(mul(f3,f4),F(1,64)),
           'The first row uses Ftt=0 at the original triple zero.')
    p0=list(map(F,[-3,2]));p1=theta_operator(p0);p2=theta_operator(p1)
    record('theta_first_derivative_polynomial',p1==list(map(F,[-15,30,-8])),'Product and chain rules, not an imported coefficient list.')
    record('theta_second_derivative_polynomial',p2==list(map(F,[-75,330,-224,32])),'Repeated direct product and chain rules.')
    # Unit-scaled paired loss, including the lower remainder coefficient.
    record('paired_loss_one_third',poly_integral([F(0),F(2),F(-2)],F(0),F(1))==F(1,3),'Integral of 2v(1-v).')
    record('paired_taylor_loss_one_twelfth',poly_integral([F(0),F(0),F(-1),F(1)],F(0),F(1))==F(-1,12),'Integral of -v^2(1-v).')
    # New research pilot: direct three-piece integration, independent of proposed gain formula.
    pilot=[]
    for beta,width in [(F(1,4),F(1,10)),(F(1,4),F(1,20)),(F(-1,4),F(1,10)),(F(1,8),F(1,5))]:
        q=[F(0),F(1),beta];center=-beta*width**2/3
        def objective(c):
            left,right=c-width,c+width
            assert -1<left<0<right<1
            middle=multiply1(q,[-c/width,1/width])
            return (-poly_integral(q,F(-1),left)+poly_integral(middle,left,right)
                    +poly_integral(q,right,F(1)))
        gain=objective(center)-objective(F(0))
        expected_gain=beta**2*width**4/9+2*beta**4*width**6/81
        assert gain==expected_gain and gain>0
        # Total variation is 1 because q has one sign change at zero.
        assert 1-objective(F(0))==width**2/3
        pilot.append({'beta':str(beta),'half_width':str(width),'trial_center':str(center),
                      'exact_objective_gain':str(gain),'gain_positive':True,
                      'centered_loss':str(width**2/3)})
    record('four_asymmetric_ramp_counterexamples',len(pilot)==4,
           'Each shifted admissible ramp improves a zero-centered ramp. This does not solve the moment-constrained theta problem.')
    out={'status':'exact_equation_and_balanced_ramp_diagnostics_passed','checks':checks,
         'check_groups':len(checks),'pilot':pilot,
         'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'trust_boundary':'Exact finite algebra only; analytic arguments, interval enclosures and literature priority are separate.'}
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'check_groups':len(checks)}))

if __name__=='__main__':main()
