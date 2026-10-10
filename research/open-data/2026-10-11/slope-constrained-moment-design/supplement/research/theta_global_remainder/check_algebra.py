#!/usr/bin/env python3
"""R26 exact constants for an adaptive finite prefix and uniform weighted tails."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def constants():
    checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append({'name':name,'passed':True})
    eps=F(1,4096);a0=F(1,16384);V=[F(4),F(3),F(168)];vs=sum(V)
    polys=[[-3,2]]
    for _ in range(5):
        P=polys[-1];out=[0]*(len(P)+1)
        for i,c in enumerate(P):out[i]+=(5+4*i)*c;out[i+1]-=4*c
        polys.append(out)
    ck('known_third_theta_derivative',polys[3]==[-375,3270,-4232,1440,-128])
    ck('tail_theta_absolute_series_ratio',F(2)**14/F(2)**450<F(1,2))
    phi=[F(1)]+[2*(F(abs(P[0]),3)+sum(F(abs(c))*4**(i-1) for i,c in enumerate(P) if i)) for P in polys[1:]]
    bell=[1]
    for n in range(5):bell.append(sum(math.comb(n,k)*bell[n-k] for k in range(n+1)))
    ck('potential_derivative_normalization',F(44,50)<1 and F(116,50**2)<1 and F(216,50**3)<1 and F(216,50**4)<1)
    ck('Bell_numbers',bell==[1,1,2,5,15,52])
    weight=[sum(F(math.comb(l,k))*phi[k]*bell[l-k] for k in range(l+1)) for l in range(6)]
    ck('inherited_log_weight_bounds',weight[1]==135 and weight[2]<3800)
    def pc(j,l):return F(2**j)*sum(F(math.comb(l,h)*math.factorial(j),math.factorial(j-h))*84**(l-h) for h in range(min(j,l)+1))
    p=[[pc(j,l) for l in range(6)] for j in range(4)]
    raw=[p[3][l]+F(1,1000)*p[0][l]+F(1,10)*p[1][l]+F(1,200)*p[2][l] for l in range(6)]
    ck('inherited_raw_bounds',raw[1]<900 and raw[2]<63000 and raw[3]<5400000)
    q=[[sum(F(math.comb(l,k))*weight[k]*p[j][l-k]/50**(l-k) for k in range(l+1)) for l in range(6)] for j in range(4)]
    # The phase representation remains valid on the full coarse coefficient box.
    phase_error=(F(82,10)*F(4,100)+F(21,1000)*F(242,10))/F(78,10)**2
    ck('coarse_box_phase_monotonicity',phase_error<F(1,50) and 82-phase_error>81 and 84+phase_error<85)
    ck('coarse_box_amplitude_derivative',F(242,10)+F(4,100)<25 and F(78,10)>7)
    ck('uniform_tail_root_motion',F(168,81)<3)
    raw_variation=63000*(1+3*a0)**3*3*a0
    perturbation=a0**2*sum(V[j]*p[j][1] for j in range(3))*(1+3*a0)**2
    ck('active_raw_derivative',raw_variation<12 and perturbation<1 and 567-12-1>550)
    raw_value=2700*(1+3*a0)**3+682*(1+3*a0)**2*a0
    ck('active_raw_residual',sum(V[j]*2**j for j in range(3))==682 and raw_value<2800)
    ck('log_weight_on_active_cell',F(135)/(1-12*a0)<136 and 408*eps<F(1,2))
    ck('active_density_derivative_lower',550-136*2800*eps>400)
    ck('neighborhood_product_factor', (1+3*a0)**3<2 and F(1)/(1-60*a0)<2 and F(1)/(1-408*eps)<2)
    kappa=F(46)
    ck('scaled_center_bound',F(270,6)+F(112,300)+F(2,50)<kappa and F(682,567)<2)
    ck('cell_geometry',kappa*eps<1 and 2+3*a0<3 and 6*a0<F(3,85) and 3*a0<F(1,1000))
    # Derivatives of q* on z+-3a gain one exponential power from r*(z)=0.
    A={}
    for n in [4,5]:
        A[n]=8*(2800*eps*weight[n]+sum(F(math.comb(n,k))*weight[k]*raw[n-k]/50**(n-1-k) for k in range(n)))
    T=F(900*273);U=F(900*12400);K=kappa
    moment=[q[j][1]*K*K+q[j][2]*(K+K**3*eps**2)/3
            +8*q[j][3]*(F(1,5)+2*K*K*eps**2+K**4*eps**4)/12 for j in range(3)]
    star6=T*K**3/3+U*(2*K*K+K**4*eps**2)/12
    star6+=A[4]*(K+F(10,3)*K**3*eps**2+K**5*eps**4)/60
    star6+=A[5]*(F(1,7)+3*K*K*eps**2+5*K**4*eps**4+K**6*eps**6)/360
    balance=T*K*K/2+U*(K+K**3*eps**2)/6+A[4]*(F(1,5)+2*K*K*eps**2+K**4*eps**4)/24
    balance+=sum(V[j]*(q[j][1]*K+8*q[j][2]*(F(1,3)+K*K*eps**2)/2) for j in range(3))/50
    ck('tail_B_constant',F(4,3)*(135+F(112+86,50))<187)
    ck('inactive_leading_constant',187+F(32,567)*vs/50<188)
    ck('inactive_Xi_constant',2070000+F(16,567)*vs**2/2500+187*vs/50<2071000)
    ck('trial_objective_density_constant',8+F(1,1000)+F(2,10)+F(4,200)<9)
    ck('weighted_tail_decay',600-(3+9+24+36)>500 and F(500*3,85)>16)
    ck('inactive_integral_factor_bounds',72*a0<1 and 48*a0<1)
    return {'status':'R26_exact_tail_constants_passed','checks':checks,'check_groups':len(checks),
      'epsilon':str(eps),'a_max':str(a0),'v_absolute_bounds':list(map(str,V)),'theta_polynomials':polys,
      'phi_relative_constants':list(map(str,phi)),'weight_relative_constants':list(map(str,weight)),
      'p_derivative_constants':[[str(x) for x in row] for row in p],
      'raw_derivative_constants':list(map(str,raw)),'q_relative_constants':[[str(x) for x in row] for row in q],
      'residual_neighborhood_fourth_constant':str(A[4]),'residual_neighborhood_fifth_constant':str(A[5]),
      'active_moment_constants':list(map(str,moment)),'active_residual_sixth_constant':str(star6),
      'active_balance_fourth_constant':str(balance),'active_dual_eighth_constant':str(balance**2/200),
      'source_sha256':sha(__file__),
      'trust_boundary':'Exact rational inequalities and derivative coefficients; the analytic use of adaptive prefixes, tail weights and scalar feasibility is stated in PROOF.md.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    d=constants();a.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['check_groups'])
if __name__=='__main__':main()
