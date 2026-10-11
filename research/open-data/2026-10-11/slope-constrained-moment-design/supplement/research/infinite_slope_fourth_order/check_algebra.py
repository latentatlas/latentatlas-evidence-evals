#!/usr/bin/env python3
"""Exact R23 algebra and rational sufficient inequalities; no analytic proof claim."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'finite_slope_fourth_order'
sys.path.insert(0,str(PREV))
from check_fourth_order import P,var,mv,mm,dot,transpose,inverse2
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def derived(p):
    out=[0]*(len(p)+1)
    for j,v in enumerate(p):out[j]+=(5+4*j)*v;out[j+1]-=4*v
    return out
def cmul(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def cadd(*xs):return tuple(sum(x[i] for x in xs) for i in range(2))
def cscale(x,s):return tuple(y*s for y in x)
def run():
    checks=[]
    def ck(name,ok):
        assert ok,name
        checks.append({'name':name,'passed':True})
    pol=[[-3,2]]
    for _ in range(3):pol.append(derived(pol[-1]))
    ck('third_theta_derivative_recurrence',pol==[[-3,2],[-15,30,-8],[-75,330,-224,32],[-375,3270,-4232,1440,-128]])
    e9lo=sum(F(9)**n/math.factorial(n) for n in range(31))
    ck('all_third_derivative_theta_series_ratios',e9lo>8000 and F(1024,8000)<F(1,2))
    rho=F(1,1000);clo=3*(1-4*rho)-2/(1-4*rho)
    ck('weighted_cubic_majorant_decay',clo>F(97,100))
    angle=F(425,4)*rho
    coercivity=7*81*(1-angle**2/2)-25*angle
    ck('tail_residual_crossing_lower_bound',coercivity>550)
    ck('tail_root_motion_bound',F(7,7*81)<F(1,80))
    e8lo=sum(F(8)**n/math.factorial(n) for n in range(31))
    ck('weighted_tail_log_derivative',e8lo>2500 and 4*3*F(97,100)*2500/27>1000 and 1000-223>1)
    phi=[2*sum(abs(v)*4**(j+1) for j,v in enumerate(p)) for p in pol]
    bell=[1,44,44**2+116,44**3+3*44*116+216]
    w=[sum(math.comb(l,j)*phi[j]*bell[l-j] for j in range(l+1)) for l in range(4)]
    pj=[[2**j*sum(math.comb(l,h)*math.factorial(j)//math.factorial(j-h)*84**(l-h)
             for h in range(min(j,l)+1)) for l in range(4)] for j in range(4)]
    CE=sum(math.comb(l,h)*w[h]*pj[j][l-h] for j in range(4) for l in range(4) for h in range(l+1))
    ck('theta_envelope_constant_positive',CE>0 and bell==[1,44,2052,100712])
    # Arbitrary trial vector, not silently assumed to satisfy the moments.
    Q=[list(map(F,q)) for q in [(1,-2),(2,1),(-1,3)]]
    rp=list(map(F,[-2,3,-5]));t=list(map(F,[7,-11,13]));u=list(map(F,[17,19,-23]))
    qp=[list(map(F,q)) for q in [(2,1),(-3,4),(1,-2)]];sgn=[-1,1,-1]
    G=[[2*sum(q[j]*q[l]/abs(r) for q,r in zip(Q,rp)) for l in range(2)] for j in range(2)]
    B=[sum(F(s)*(q[j]*tt/r-p[j]) for s,q,tt,r,p in zip(sgn,Q,t,rp,qp))/3 for j in range(2)]
    R=sum(tt*tt/(36*abs(r))-F(s)*uu/60 for tt,r,s,uu in zip(t,rp,sgn,u))
    vtest=list(map(F,[F(7,11),F(-5,13)]))
    kap=[(dot(q,vtest)-tt/6)/r for q,tt,r in zip(Q,t,rp)]
    moment=[-2*sum(F(s)*q[j]*k for s,q,k in zip(sgn,Q,kap))-sum(F(s)*p[j] for s,p in zip(sgn,qp))/3 for j in range(2)]
    S4=-sum(F(s)*(r*k*k+tt*k/3+uu/60) for s,r,k,tt,uu in zip(sgn,rp,kap,t,u))
    ck('trial_path_moment_coefficient',moment==[a-b for a,b in zip(B,mv(G,vtest))])
    ck('trial_residual_support_coefficient',S4-dot(vtest,moment)==R+dot(vtest,mv(G,vtest))/2-dot(B,vtest))
    v=mv(inverse2(G),B);penalty=dot(B,v)/2
    ck('coefficient_minimization',R+dot(v,mv(G,v))/2-dot(B,v)==R-penalty and penalty>0)
    # Independent complex-exponential integration expansion for the infinite example.
    a,omega,D,L,nu=[var(i) for i in range(5)]
    k=F(1,3)-1/(6*D);c=(1-D)/(omega*D);s=(P(-1),omega);s2=cmul(s,s);s3=cmul(s2,s)
    change=cadd((k*a**2+nu*a**4,P(0)),cscale(s,a**2/6+k*k*a**4/2),
                cscale(s2,k*a**4/6),cscale(s3,a**4/120))
    dz=cmul((P(0),2*L),change)
    xi=omega*L*((11+3*omega**2)/180-1/(36*D**2))
    ck('infinite_example_direct_target',dz[0]==-omega*L*a**2/3+xi*a**4)
    ck('infinite_example_exact_moment_leading_term',(dz[1]-c*dz[0]).trunc(0,2)==0)
    return {'status':'R23_exact_algebra_passed','checks':checks,'check_groups':len(checks),
       'theta_derivative_polynomials':pol,'theta_envelope_constant':CE,
       'theta_phi_constants_integer_upper':phi,'expP_derivative_constants':bell,
       'rho_max':str(rho),'weighted_decay_coefficient_rational_lower':str(clo),
       'tail_crossing_rational_lower':str(coercivity),'source_sha256':sha(__file__),
       'R22_algebra_helper_sha256':sha(PREV/'check_fourth_order.py'),
       'trust_boundary':'Exact finite identities and rational inequalities. Dominated convergence, infinite support and the weighted theorem remain analytic proof obligations.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    data=run();args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'status':data['status'],'check_groups':data['check_groups'],'theta_envelope_constant':data['theta_envelope_constant']}))
if __name__=='__main__':main()
