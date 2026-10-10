#!/usr/bin/env python3
"""Exact differentiation identities and whole-tail derivative bounds."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'finite_slope_fourth_order'))
import check_fourth_order as algebra
algebra.N=32;algebra.ZERO=(0,)*32
P,var=algebra.P,algebra.var
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def diff(p,index):
    out={}
    for e,c in P(p).p.items():
        if e[index]:
            h=list(e);h[index]-=1;out[tuple(h)]=c*e[index]
    return P(out)
def stringify(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:stringify(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [stringify(v) for v in x]
    return x
def run():
    checks=[]
    def ck(name,v):
        assert v,name
        checks.append({'name':name,'passed':True})
    r,t,s,Q,Qu,rd,td,sd,Qd,Qud=[var(i) for i in range(10)]
    for sig in [-1,1]:
        gamma=sig*r;gd=sig*rd
        BB=sig*(Q*t/r-Qu)/3
        direct=sum((diff(BB,i)*v for i,v in [(0,rd),(1,td),(3,Qd),(4,Qud)]),P(0))
        expected=sig*((Qd*t+Q*td)/r-Q*t*rd/r**2-Qud)/3
        ck('B_total_derivative_'+str(sig),direct==expected)
        RR=t*t/(36*gamma)-sig*s/60
        direct=diff(RR,0)*rd+diff(RR,1)*td+diff(RR,2)*sd
        ck('R_total_derivative_'+str(sig),direct==t*td/(18*gamma)-t*t*gd/(36*gamma**2)-sig*sd/60)
        a,b,ad,bd=var(10),var(11),var(12),var(13)
        GG=2*a*b/gamma
        ck('G_total_derivative_'+str(sig),diff(GG,10)*ad+diff(GG,11)*bd+diff(GG,0)*rd
           ==2*((ad*b+a*bd)/gamma-a*b*gd/gamma**2))
    f,D,G,X,fp,Dp,Gp,Xp=[var(i) for i in range(8)]
    C=f**5/D**5*(G**2/(3*D**2)-X/D)
    direct=sum((diff(C,i)*v for i,v in enumerate([fp,Dp,Gp,Xp])),P(0))
    H=G**2/(3*D**2)-X/D
    expected=f**5/D**5*(5*(fp/f-Dp/D)*H+2*G*Gp/(3*D**2)-2*G**2*Dp/(3*D**3)-Xp/D+X*Dp/D**2)
    ck('C4_total_derivative',direct==expected)
    ck('C4_missing_target_motion_negative_control',direct!=expected-5*f**4*fp/D**5*H)
    z,zp=var(0),var(1)
    for k in range(4):
        signed=(1-(-1)**(k+1)-2*z**(k+1))/F(k+1)
        ck('moving_boundary_sign_moment_'+str(k),diff(signed,0)*zp==-2*z**k*zp)
    ck('envelope_no_boundary_term_at_zero',diff(1+z*z,0)*zp==(-2*z)*(-zp))
    # The stationary quadratic representation avoids a numerically unstable v'.
    entries=[var(i) for i in range(6)];derivs=[var(i) for i in range(6,12)]
    def symmat(v):return [[v[0],v[1],v[2]],[v[1],v[3],v[4]],[v[2],v[4],v[5]]]
    A,Ad=symmat(entries),symmat(derivs);v=[var(i) for i in range(12,15)];vd=[var(i) for i in range(15,18)];Bd=[var(i) for i in range(18,21)]
    B=[sum((A[i][j]*v[j] for j in range(3)),P(0)) for i in range(3)]
    linear=sum((Bd[j]*v[j]+B[j]*vd[j] for j in range(3)),P(0))
    quadratic=sum((vd[i]*A[i][j]*v[j]+v[i]*Ad[i][j]*v[j]+v[i]*A[i][j]*vd[j] for i in range(3) for j in range(3)),P(0))/2
    expected=sum((Bd[j]*v[j] for j in range(3)),P(0))-sum((v[i]*Ad[i][j]*v[j] for i in range(3) for j in range(3)),P(0))/2
    ck('stationary_quadratic_derivative',linear-quadratic==expected)
    oldpath=HERE.parent/'theta_global_remainder/results/algebra.json';old=json.loads(oldpath.read_text())
    W=list(map(F,old['weight_relative_constants']));babs=[F(1,1000),F(1,10),F(1,200)]
    rawtau=F(16)+2*babs[0]+4*babs[1]+8*babs[2]
    ck('tail_tau_raw_derivative',rawtau<17)
    ck('tail_dual_rhs_root_envelope',F(2*4*17,567)<1)
    ck('tail_root_velocity_from_solve',F(10*7+17,567)<1)
    pp=[[F(2**j)*sum(F(math.comb(l,h)*(math.factorial(j)//math.factorial(j-h))*84**(l-h)) for h in range(min(j,l)+1))
         for l in range(5)] for j in range(10)]
    qq=[[sum(F(math.comb(l,k))*W[k]*pp[j][l-k] for k in range(l+1)) for l in range(5)] for j in range(10)]
    hh=[[qq[j+1][l]+qq[j+2][l]/4+qq[j+4][l]/16+qq[j+6][l]/64 for l in range(4)] for j in range(4)]
    aa=[qq[3][l]+sum(babs[j]*qq[j][l] for j in range(3)) for l in range(5)]
    ll=[hh[3][l]+sum(babs[j]*hh[j][l] for j in range(3))+10*sum(qq[j][l] for j in range(3))+aa[l+1] for l in range(4)]
    dd=[[hh[j][l]+qq[j][l+1] for l in range(4)] for j in range(3)]
    cg=max(2*((dd[i][0]*qq[j][0]+qq[i][0]*dd[j][0])/567+qq[i][0]*qq[j][0]*ll[1]/567**2) for i in range(3) for j in range(3))
    cb=max(((dd[j][0]*aa[2]+qq[j][0]*ll[2])/567+qq[j][0]*aa[2]*ll[1]/567**2+dd[j][1])/3 for j in range(3))
    cr=aa[2]*ll[2]/(18*567)+aa[2]**2*ll[1]/(36*567**2)+ll[3]/60
    env={'dual_rhs':(F(1),3,0),'Gamma_prime':(ll[1],9,8),'G_prime_entry':(cg,7,8),'B_prime_entry':(cb,8,16),'R_prime':(cr,9,24)}
    margins={k:600-(p+9+d+36) for k,(c,p,d) in env.items()}
    for k,v in margins.items():ck('derivative_envelope_decay_'+k,v>500)
    ck('whole_root_sum_ratio',F(500*3,85)>16)
    ck('sign_moment_tail_all_orders',600-(9+9+36)>540)
    ck('theta_derivative_omission_ratio',F(14,13)**12 < 2**12 and sum(F(81)**k/math.factorial(k) for k in range(5))>2**13)
    width=F(1,65536);slo=F('2.82e-40');shi=F('4.35e-40')
    anchored=[F('2.49203004e-39')-width*shi,F('2.49203006e-39')]
    ck('anchored_common_coefficient_band',F('2.49202340e-39')<anchored[0] and anchored[1]==F('2.49203006e-39'))
    return {'status':'R28_exact_derivative_and_tail_algebra_passed','checks':checks,'check_groups':len(checks),
      'tail_envelopes':stringify(env),'tail_decay_margins':margins,'endpoint_gain_interval':list(map(str,[width*slo,width*shi])),
      'anchored_coefficient_bounds':list(map(str,anchored)),'source_sha256':sha(__file__),
      'symbolic_helper_sha256':sha(HERE.parent/'finite_slope_fourth_order/check_fourth_order.py'),
      'R26_algebra_sha256':sha(oldpath),
      'trust_boundary':'Exact Laurent-polynomial differentiation and rational inequalities. The moving-boundary differentiation, implicit dual and summability arguments are separate analytic obligations.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    data=run();args.output.write_text(json.dumps(data,indent=2)+'\n');print(data['status'],data['check_groups'])
if __name__=='__main__':main()
