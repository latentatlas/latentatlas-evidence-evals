#!/usr/bin/env python3
"""Exact transport identities and a whole-half-line theta tail argument."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,math
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'finite_slope_fourth_order'))
import check_fourth_order as algebra
algebra.N=16;algebra.ZERO=(0,)*16
P,var=algebra.P,algebra.var
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def diff(p,i):
    out={}
    for e,c in P(p).p.items():
        if e[i]:
            t=list(e);t[i]-=1;out[tuple(t)]=c*e[i]
    return P(out)
def run():
    checks=[]
    def ck(name,value):
        assert value,name
        checks.append({'name':name,'passed':True})
    eta=var(0)
    for j in range(4):ck('moment_scaling_'+str(j),eta**4*eta**(-j)*eta**-1==eta**(3-j))
    ck('missing_jacobian_negative_control',eta**4*eta**-3!=1)
    k,u,oldL,newL,flog,pdot=[var(i) for i in range(1,7)]
    time_log=-flog+4*k+pdot+k*eta*u*oldL;space_log=eta*oldL-newL
    ck('transport_generator',time_log-k*u*space_log==-flog+4*k+pdot+k*u*newL)
    r,ru,T,Tu,Tuu,a=[var(i) for i in range(7,13)]
    for sign in [-1,1]:
        W=eta*T+a*sign*Tu
        DT=r*T;DTu=(r+k)*Tu+ru*T;Deta=k*eta
        ck('weighted_norm_generator_'+str(sign),Deta*T+eta*DT+a*sign*DTu-(r+k)*W==a*sign*ru*T)
    X,A,N,C=[var(i) for i in range(4)]
    ell=9+12/A-4*X
    ck('first_theta_log_derivative',diff(ell,0)*4*X+diff(ell,1)*8*X==-16*X-96*X/A**2)
    aa=2*X-3;cc=2*N*X-3
    difference=((9-4*N*X)*cc+12)*aa-((9-4*X)*aa+12)*cc
    ck('relative_theta_log_derivative',difference==-4*(N-1)*X*(aa*cc+6))
    quotient_log=4*X*(2*N*aa-2*cc-(N-1)*aa*cc)
    ck('relative_term_product_rule',difference==quotient_log)
    ck('ratio_majorant_x_ge_3',F(6,21*3)+1<F(5,4))
    ck('second_log_difference',F(96*12,21**2)<3 and 32+3<4*4*3)
    ck('second_relative_derivative',2*(25+F(20,12))<100)
    ck('uniform_geometric_tail_ratio',1+15+F(15**2,2)>2*F(3,2)**8)
    ck('tail_geometric_ratio',1+750>2*F(3,2)**8)
    exp450=sum(F(450)**j/math.factorial(j) for j in range(6))
    tail_constants=[64,192000,1152000000]
    ck('theta_relative_tail_jets_below_quarter',exp450>4*max(tail_constants))
    ck('logarithm_tail_second_derivative_below_one',F(1,4)+F(1,4)**2<1)
    ck('leading_log_curvature_correction',F(96*150,297**2)<1)
    exp4=sum(F(4)**j/math.factorial(j) for j in range(15))
    ck('exp4_lower_bound',exp4>F(109,2))
    ck('pi_exp4_lower_bound',F(157,50)*F(109,2)>170)
    # (1+4u) exp(4u)>270 u^5 for u>=1. Put x=u-1 and retain
    # the first six positive exponential terms. The only negative
    # coefficient belongs to a strictly positive quadratic.
    x=var(0);poly=F(109,2)*(5+4*x)*sum((F(4)**j*x**j/math.factorial(j) for j in range(6)),P(0))-270*(1+x)**5
    coeff=[poly.p.get((j,)+(0,)*15,F(0)) for j in range(7)]
    ck('exponential_polynomial_positive_quadratic',coeff[0]>0 and coeff[2]>0 and 4*coeff[0]*coeff[2]>coeff[1]**2)
    ck('exponential_polynomial_positive_higher_terms',all(v>0 for v in coeff[3:]))
    a0=F(1,16384);H=F(1,64);c=F(1,50);km=F('.00259');kp=F('.00260');lp=F('.3264');mp=F('.2942');flow=F('.0437')
    effective=km-5*a0*kp
    polynomial=[-flow+5*kp+a0*kp,10*km+a0*(2*lp+18*kp),lp,a0*(4*mp+144*kp),mp+36*km,a0*(6+36*H*kp),F(1)]
    derivative_bound=sum(j*v for j,v in enumerate(polynomial))
    derivative_margin=4*effective*3*270-derivative_bound
    at_one=sum(polynomial)-4*effective*170
    ck('negative_weight_log_upper_on_tail',10-600+36<0)
    ck('effective_exponential_coefficient',effective>0)
    ck('positive_tail_polynomial_derivative_coefficients',all(x>0 for x in polynomial[1:]))
    ck('decreasing_dissipativity_majorant',derivative_margin>0)
    ck('tail_dissipativity_strict_rate',at_one<-c)
    U=F('9.181e-10');M0=F('2e-5');lower=F('9.17e-10');lograte=c+km
    ck('optimal_profiles_fit_weighted_norm',U/M0<a0)
    ck('published_linear_value_rate',lower*lograte>F('2.07e-11'))
    ck('positive_contraction_rate',c>0 and km>0)
    return {'status':'R31_exact_transport_and_tail_algebra_passed','checks':checks,'check_groups':len(checks),
      'contraction_rate':str(c),'a0':str(a0),'minimum_budget':str(M0),'optimal_amplitude_upper':str(U),
      'optimal_amplitude_lower':str(lower),'logarithmic_value_rate':str(lograte),'linear_value_rate':'2.07e-11',
      'theta_tail_jet_constants_at_x150':list(map(str,tail_constants)),
      'exponential_polynomial_coefficients':list(map(str,coeff)),
      'tail_effective_kappa':str(effective),'tail_polynomial':list(map(str,polynomial)),
      'tail_derivative_margin':str(derivative_margin),'tail_dissipativity_upper_at_one':str(at_one),
      'source_sha256':sha(__file__),'symbolic_helper_sha256':sha(HERE.parent/'finite_slope_fourth_order/check_fourth_order.py'),
      'trust_boundary':'Exact product/Jacobian identities, Laurent-polynomial identities and rational tail inequalities. pi>3.14 is checked from the Arb cover. Change of variables, characteristic comparison and the optimal-value inference are separate analytic arguments.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    d=run();args.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['check_groups']);print('tail upper',float(F(d['tail_dissipativity_upper_at_one'])))
if __name__=='__main__':main()
