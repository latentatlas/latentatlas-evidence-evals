#!/usr/bin/env python3
"""Independent numerical diagnostics of the explicit weighted transport.
No interval claims: rounded R29 points, truncated theta and finite quadrature.
"""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
INPUT=HERE.parent/'cusp_motion_continuation/results/direct_check.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
    old=json.loads(INPUT.read_text());selected=['-0.015625','-0.0078125','0.0'];runs=[]
    for precision in [60,90]:
        mp.mp.dps=precision
        pts={e['nu']:e for e in old['runs'][-1]['evaluations']}
        par=[[*map(mp.mpf,pts[nu]['cusp']),mp.mpf(nu)] for nu in selected]
        fs=[mp.mpf(pts[nu]['coefficients']['f']) for nu in selected]
        def weight(u,p):
            x=mp.pi*mp.exp(4*u)
            phi=sum(mp.pi*n*n*mp.exp(5*u)*(2*n*n*x-3)*mp.exp(-n*n*x) for n in range(1,13))
            return phi*mp.exp(p[1]*u*u+p[2]*u**4+p[3]*u**6)
        def logderivative(u,p):
            x=mp.pi*mp.exp(4*u)
            terms=[mp.pi*n*n*mp.exp(5*u)*(2*n*n*x-3)*mp.exp(-n*n*x) for n in range(1,13)]
            d=sum(a*(9+12/(2*n*n*x-3)-4*n*n*x) for n,a in enumerate(terms,1))/sum(terms)
            return d+2*p[1]*u+4*p[2]*u**3+6*p[3]*u**5
        def T(i,j,u):
            eta=par[i][0]/par[j][0]
            return fs[i]/fs[j]*eta**4*weight(eta*u,par[j])/weight(u,par[i])
        def q(j,u,p):return weight(u,p)*(2*u)**j*mp.cos(2*p[0]*u+j*mp.pi/2)
        errors=[];samples=[];derivative_errors=[];semigroup_errors=[]
        for i,j in [(0,1),(1,2),(0,2)]:
            eta=par[i][0]/par[j][0];distance=par[j][3]-par[i][3];bound=mp.exp(-distance/50)
            # Matched finite boundaries make change of variables exact for
            # the truncated kernel too. This diagnoses scaling and Jacobian.
            g=lambda u:(1+mp.sin(7*u))/3
            leftgrid=[mp.mpf(k)/8 for k in range(9)]
            for degree in range(4):
                lhs=mp.quadgl(lambda u:q(degree,u,par[i])*T(i,j,u)*g(eta*u),leftgrid)
                rhs=fs[i]/fs[j]*eta**(3-degree)*mp.quadgl(lambda x:q(degree,x,par[j])*g(x),[eta*x for x in leftgrid])
                error=abs(lhs-rhs)/max(abs(lhs),abs(rhs),mp.mpf('1e-50'));errors.append(error)
            maxW=mp.mpf(0);maxT=mp.mpf(0)
            for l in range(129):
                u=mp.mpf(l)/64;t=T(i,j,u);tu=t*(eta*logderivative(eta*u,par[j])-logderivative(u,par[i]))
                maxW=max(maxW,eta*t+abs(tu)/16384);maxT=max(maxT,t)
            for u in map(mp.mpf,['0','.1','.45','1','2']):
                t=T(i,j,u);analytic=t*(eta*logderivative(eta*u,par[j])-logderivative(u,par[i]));numeric=mp.diff(lambda v:T(i,j,v),u)
                derivative_errors.append(abs(analytic-numeric)/max(1,abs(analytic),abs(numeric)))
            assert maxW<bound and maxT<bound/eta
            samples.append({'indices':[i,j],'eta':mp.nstr(eta,45),'distance':mp.nstr(distance,45),'maximum_sampled_weighted_norm':mp.nstr(maxW,45),'proved_bound':mp.nstr(bound,45),'maximum_sampled_amplitude_factor':mp.nstr(maxT,45)})
        for u in map(mp.mpf,['0','.1','.45','1','2']):
            expected=T(0,2,u);composed=T(0,1,u)*T(1,2,par[0][0]/par[1][0]*u)
            semigroup_errors.append(abs(expected-composed)/max(1,abs(expected)))
        threshold=mp.mpf(10)**(-precision+12)
        assert max(errors)<threshold and max(derivative_errors)<threshold and max(semigroup_errors)<threshold
        runs.append({'dps':precision,'moment_comparisons':12,'max_relative_moment_error':mp.nstr(max(errors),30),
          'derivative_checks':15,'max_scaled_derivative_error':mp.nstr(max(derivative_errors),30),
          'semigroup_checks':5,'max_scaled_semigroup_error':mp.nstr(max(semigroup_errors),30),'sampled_pairs':samples})
        print('direct diagnostics',precision,'digits passed',flush=True)
    return {'status':'R31_independent_transport_diagnostics_passed','runs':runs,'input_sha256':sha(INPUT),'source_sha256':sha(__file__),
      'frozen_rounded_R29_points':selected,'theta_terms':12,'integration_domain':'matched [0,1] and [0,eta]',
      'tail_infinite_integral_verified_by_diagnostic':False,'rigorous_interval_evidence':False,
      'scope':'Scaling, Jacobian, product derivative, composition and point samples only. Whole-domain proof comes from the separate Arb/rational generator cover and analytic tail.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    result=run();args.output.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
