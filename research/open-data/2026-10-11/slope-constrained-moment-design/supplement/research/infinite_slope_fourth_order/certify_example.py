#!/usr/bin/env python3
"""Arb certificates for the infinite periodic example and theta weighted tail."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
from flint import arb,acb,ctx
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ar(x):
    x=F(x);return arb(x.numerator)/arb(x.denominator)
def ball(lo,hi):
    lo,hi=F(lo),F(hi);return ar((lo+hi)/2)+arb(0,ar((hi-lo)/2).upper())
def packed(x):
    return {'lower':[int(v) for v in x.lower().man_exp()],
            'upper':[int(v) for v in x.upper().man_exp()], 'display':str(x)}
def produce():
    assert __debug__;ctx.dps=100
    alg=json.loads((HERE/'results/algebra.json').read_text())
    pi=arb.pi();i=acb(0,1);s=acb(-1,pi)
    L=arb(-1/2).exp()/(1-arb(-1).exp());D=(1+2*pi*L)/(1+pi*pi);c=(1-D)/(pi*D)
    f=D/4;delta=arb(1)/4;Gamma=pi*L;G=2*L/pi;B=L/(3*D);v=pi/(6*D)
    R=Gamma*(11+3*pi*pi)/180;P=Gamma/(36*D*D);Xi=R-P
    C2=delta**3*Gamma/(3*D);C4=delta**5*(Gamma**2/(3*D*D)-Xi/D)
    coeff={name:packed(x) for name,x in locals().copy().items() if name in ['L','D','c','f','delta','Gamma','G','B','v','R','P','Xi','C2','C4']}
    assert D>0 and D<1 and C2>0 and C4>0
    def E(d,a):return (s*acb(d)).exp()*(s*acb(a)).sinh()/(s*acb(a))
    def Z(d,a):return -1/s+2*i*acb(L)*E(d,a)/s
    def mom(d,a):
        z=Z(d,a);return z.imag-c*z.real
    rows=[]
    for aa in ['1/5','1/10','1/20','1/50','1/100','1/200']:
        a=ar(aa);lo,hi=F(-1,50),F(1,50)
        original=(lo,hi);d0=ball(lo,hi)
        deriv=2*i*acb(L)*E(d0,a);derivative=deriv.imag-c*deriv.real
        assert derivative>0 and mom(ar(lo),a)<0 and mom(ar(hi),a)>0
        for _ in range(220):
            mid=(lo+hi)/2;fm=mom(ar(mid),a)
            if fm<0:lo=mid
            elif fm>0:hi=mid
            else:raise ArithmeticError('Increase Arb precision: bisection sign unresolved')
        d=ball(lo,hi);ev=E(d,a);den=ev.real+c*ev.imag
        assert not den.contains(0)
        b=-ev.imag/den;z=Z(d,a);S=z.real;A=f/S;M=A/a
        assert mom(d,a).contains(0) and S>0 and abs(d)+a<ar('1/2') and 1+b*c>0
        def residual(x):return (-x).exp()*((1+b*c)*(pi*x).cos()-b*(pi*x).sin())
        left=residual(ar('1/2')+d-a);right=residual(ar('1/2')+d+a)
        assert left>0 and right<0
        balance=(acb(1+b*c,b)*ev).imag
        assert balance.contains(0)
        leading=A-delta-C2/M**2;fourth=leading-C4/M**4;scaled=leading*M**4
        assert leading>0 and fourth>0 and fourth<leading
        vals={'d':d,'b':b,'S':S,'A':A,'M':M,'scaled_fourth_residual':scaled,
              'leading_error':leading,'fourth_error':fourth,'error_ratio':fourth/leading}
        rows.append({'a':aa,'bisection_steps':220,'initial_bracket':list(map(str,original)),
            'root_bracket':list(map(str,[lo,hi])),'initial_moment_derivative':packed(derivative),
            'endpoint_moments':[packed(mom(ar(lo),a)),packed(mom(ar(hi),a))],
            'residual_cell_endpoints':[packed(left),packed(right)],
            'balanced_cell_check':packed(balance),'intervals':{k:packed(x) for k,x in vals.items()}})
    rho=ar('1/1000');x=2+rho;CE=arb(alg['theta_envelope_constant'])
    cr=3*(-4*rho).exp()-2*(4*rho).exp();assert cr>ar('97/100')
    E2=CE*(1+x)**12*(21*x+9*x**4-pi*(4*(2-rho)).exp()).exp()
    H2=CE**3/18*(1+x)**36*(63*x+27*x**4+8*x*x-pi*cr*arb(8).exp()).exp()
    tail=(2*E2+H2)/(1-(-arb(3)/85).exp())
    tail_log10=tail.log()/arb(10).log()
    ratio=arb(1024)*(-3*pi).exp();assert ratio<arb(1)/2
    assert tail<arb(10)**-3500
    theta={'rho':'1/1000','tail_starts_at':2,'root_spacing_lower':'3/85',
           'E_constant':alg['theta_envelope_constant'],'weighted_decay_c':packed(cr),
           'theta_derivative_term_ratio_upper':packed(ratio),
           'weighted_majorant_tail_upper':packed(tail),'log10_upper_expression':packed(tail_log10),
           'simple_tail_bound':'10^-3500','not_a_theta_C4_enclosure':True}
    trunc=[]
    for N in [1,2,4,8,16,32,64]:
        omitted=arb(-N).exp();factor=1-omitted
        cn=delta**5*((Gamma*factor)**2/(3*D**2)-Xi*factor/D)
        err=C4-cn;assert err>0
        trunc.append({'roots':N,'omitted_fraction':packed(omitted),'C4_partial':packed(cn),'C4_error':packed(err)})
    return {'status':'R23_Arb_example_and_theta_tail_passed','dps':100,'coefficients':coeff,'rows':rows,
       'theta_weighted_tail':theta,'geometric_series_truncation':trunc,
       'source_sha256':sha(__file__),'algebra_sha256':sha(HERE/'results/algebra.json'),
       'trust_boundary':'Arb transcendental enclosures, six isolated exact-example budgets, and a theta weighted-majorant tail. Relies on documented analytic support, periodicity and envelope derivations; not a numerical theta C4 or uniform fourth-order remainder certificate.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    data=produce();args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(data['status']);print('C2',data['coefficients']['C2']['display']);print('C4',data['coefficients']['C4']['display'])
    print('theta weighted tail log10',data['theta_weighted_tail']['log10_upper_expression']['display'])
if __name__=='__main__':main()
