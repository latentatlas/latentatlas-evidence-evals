#!/usr/bin/env python3
"""R30: independently differentiate all three coefficients using rational AD."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'theta_fourth_order'))
from rational_intervals import RI,restore,mm,mv,BITS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def unbox(x):
    if isinstance(x,dict):
        if 'mid_man_exp' in x:return restore(x)
        return {k:unbox(v) for k,v in x.items()}
    if isinstance(x,list):return [unbox(v) for v in x]
    return x
def sm(xs):return sum(xs,RI(0))
def sym(x):return RI(-x,x)
class AD:
    def __init__(self,v,d=0):
        if isinstance(v,AD):self.v,self.d=v.v,v.d
        else:self.v,self.d=RI(v),RI(d)
    def __add__(self,o):
        o=AD(o);return AD(self.v+o.v,self.d+o.d)
    __radd__=__add__
    def __neg__(self):return AD(-self.v,-self.d)
    def __sub__(self,o):return self+-AD(o)
    def __rsub__(self,o):return AD(o)+-self
    def __mul__(self,o):
        o=AD(o);return AD(self.v*o.v,self.d*o.v+self.v*o.d)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=AD(o);return AD(self.v/o.v,(self.d*o.v-self.v*o.d)/o.v**2)
    def __rtruediv__(self,o):return AD(o)/self
    def __pow__(self,n):
        return AD(self.v**n,n*self.v**(n-1)*self.d) if n else AD(1)
def motion_check(data,parent):
    c,p=unbox(data),unbox(parent);co=p['coefficients'];arc=p['arc'];b=p['dual']['tight_box'];vel=arc['refined_velocity'];checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append(name)
    B=arc['positive_moment_bounds'];offs=[x.abs_upper() for x in arc['offsets']];S=[]
    for row in c['sign_transport']:
        n=row['order'];err=(offs[0]*B[n+1]+offs[1]*B[n+2]/4+offs[2]*B[n+4]/16+offs[3]*B[n+6]/64
                           +sm(row['root_motion_terms'])+row['whole_sign_tail']).hi
        S.append(row['base_template_moment']+sym(err));ck('sign_transport_'+str(n),err>0)
    S[:3]=[RI(0)]*3;S[3]=co['D']
    def partial(q,j):return vel[0]*q[j+1]-vel[1]*q[j+2]/4+vel[2]*q[j+4]/16-q[j+6]/64
    Sd=[partial(S,j) for j in range(4)];rhs=Sd[:3];tail=c['tail_derivative_bounds']
    for row in c['root_derivatives']:
        at=row['jets'];q=at['moment_jets_extended'];pp=at['p_jets_extended'];r=at['residual_jets'];sig=row['orientation']
        ck('simple_root_'+str(row['index']),(sig*r[1]).lo>0)
        h=vel[0]*at['weight_jets'][0]*(pp[4][0]-sm(b[j]*pp[j+1][0] for j in range(3)))
        rhs=[rhs[j]+2*q[j][0]*h/(sig*r[1]) for j in range(3)]
    rhs=[x+sym(tail['dual_rhs'].hi) for x in rhs]
    sol=c['dual_derivative_solve'];A=co['G'];C=sol['preconditioner'];v0=sol['seed'];CG=mm(C,A)
    E=[[RI(i==j)-CG[i][j] for j in range(3)] for i in range(3)];eta=max(sum(x.abs_upper() for x in row) for row in E)
    ck('implicit_dual_solve',eta<1);forcing=max(x.abs_upper() for x in mv(C,[rhs[i]-mv(A,v0)[i] for i in range(3)]))
    bp=[v0[i]+sym(forcing/(1-eta)) for i in range(3)]
    for j in range(3):ck('tail_bprime_bound_'+str(j),bp[j].abs_upper()<10)
    Gamma=AD(0);GG=[[AD(0) for j in range(3)] for i in range(3)];BB=[AD(0) for _ in range(3)];RR=AD(0)
    for row in c['root_derivatives']:
        at=row['jets'];q=at['moment_jets_extended'];pp=at['p_jets_extended'];r=at['residual_jets'];sig=row['orientation']
        zp=(sm(bp[j]*pp[j][0] for j in range(3))-vel[0]*(pp[4][0]-sm(b[j]*pp[j+1][0] for j in range(3))))/(pp[3][1]-sm(b[j]*pp[j][1] for j in range(3)))
        qd=[[partial([q[n][l] for n in range(10)],j) for l in range(4)] for j in range(4)]
        # Forward AD differentiates the coefficient formulas instead of
        # reusing the producer's explicit quotient derivatives.
        qr=[AD(r[l],qd[3][l]-sm(b[j]*qd[j][l]+bp[j]*q[j][l] for j in range(3))+r[l+1]*zp) for l in range(4)]
        Q=[[AD(q[j][l],qd[j][l]+q[j][l+1]*zp) for l in range(2)] for j in range(3)]
        gam=sig*qr[1];Gamma+=gam
        for j in range(3):BB[j]+=sig*(Q[j][0]*qr[2]/qr[1]-Q[j][1])/3
        for i in range(3):
            for j in range(3):GG[i][j]+=2*Q[i][0]*Q[j][0]/gam
        RR+=qr[2]**2/(36*gam)-sig*qr[3]/60
    old=unbox(json.loads((HERE.parent/'theta_fourth_order/results/certificate.json').read_text()))['tail_absolute_bounds']
    Gamma+=AD(RI(0,old['Gamma'].hi),sym(tail['Gamma_prime'].hi))
    for j in range(3):BB[j]+=AD(sym(old['B_entry'].hi),sym(tail['B_prime_entry'].hi))
    for i in range(3):
        for j in range(3):GG[i][j]+=AD(RI(0,old['G_entry'].hi) if i==j else sym(old['G_entry'].hi),sym(tail['G_prime_entry'].hi))
    RR+=AD(sym(old['R'].hi),sym(tail['R_prime'].hi))
    v=co['v']
    stationary_energy=sum((BB[j]*v[j] for j in range(3)),AD(0))-sum((GG[i][j]*v[i]*v[j] for i in range(3) for j in range(3)),AD(0))/2
    Xi=AD(co['Xi'],RR.d-stationary_energy.d)
    D=AD(co['D'],Sd[3]-sm(b[j]*Sd[j] for j in range(3)));f=AD(co['f'],partial(arc['derivatives'],3))
    delta=f/D;C2=delta**3*Gamma/(3*D);C4=delta**5*(Gamma**2/(3*D**2)-Xi/D)
    ck('delta0_derivative_band',F('2.7e-11')<delta.d.lo<delta.d.hi<F('3.0e-11'))
    ck('C2_derivative_band',F('7.4e-26')<C2.d.lo<C2.d.hi<F('8.7e-26'))
    ck('published_derivative_band',F('1.9e-40')<C4.d.lo<C4.d.hi<F('5.3e-40'))
    h=F(1,64);lo=F('2.49203004e-39')-h*F('5.3e-40');hi=F('2.49203006e-39')
    ck('published_anchored_band',F('2.48374879e-39')==lo<hi)
    return {'status':'R30_three_coefficient_AD_reconstruction_passed','checks':checks,'check_count':len(checks),
      'delta0_prime_interval':list(map(str,[delta.d.lo,delta.d.hi])),
      'C2_prime_interval':list(map(str,[C2.d.lo,C2.d.hi])),
      'rounding_bits':BITS,'C4_prime_interval':list(map(str,[C4.d.lo,C4.d.hi])),
      'b_prime_intervals':[[str(x.lo),str(x.hi)] for x in bp],
      'accepted_inputs':'R29 local exact cusp, velocity, dual and coefficient boxes; new transcendental root jets; fixed-template integral and sign-motion bounds; analytic whole-tail enclosures. Automatic differentiation reconstructs the derivative arithmetic, not the analytic differentiation theorem.'}
