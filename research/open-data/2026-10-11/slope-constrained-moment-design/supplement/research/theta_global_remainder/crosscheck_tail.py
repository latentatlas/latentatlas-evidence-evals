#!/usr/bin/env python3
"""Independent original-density checks at distant active switches; diagnostic only."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
from fractions import Fraction as F
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def midpoint(rec):
    m,e=rec['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def val(s):
    q=F(s);return mp.mpf(q.numerator)/q.denominator
def run(old,alg,dps,order):
    mp.mp.dps=dps;tau,lam,mu=map(midpoint,old['Q_box']);b=list(map(midpoint,old['dual_box']));v=list(map(midpoint,old['v_enclosure']))
    eps=val(alg['epsilon']);W=list(map(val,alg['weight_relative_constants']));E=[list(map(val,row)) for row in alg['q_relative_constants']]
    H=list(map(val,alg['active_moment_constants']));Cs=val(alg['active_residual_sixth_constant']);Ch=val(alg['active_balance_fourth_constant'])
    A4=val(alg['residual_neighborhood_fourth_constant']);A5=val(alg['residual_neighborhood_fifth_constant'])
    def p(j,x):return (2*x)**j*mp.cos(2*tau*x+j*mp.pi/2)
    def raw(x,bb):return p(3,x)-mp.fsum(bb[j]*p(j,x) for j in range(3))
    def weight(x):
        ee=mp.exp(4*x)
        return mp.pi*mp.exp(5*x+lam*x*x+mu*x**4)*mp.fsum(n*n*(2*mp.pi*n*n*ee-3)*mp.exp(-mp.pi*n*n*ee) for n in range(1,13))
    def q(j,x):return weight(x)*p(j,x)
    def qr(x):return weight(x)*raw(x,b)
    nodes,weights=mp.gauss_quadrature(order,'legendre');out=[];checks=0
    for phase_index in [27,40,53,80]:
        z=mp.findroot(lambda x:raw(x,b),phase_index*mp.pi/(2*tau),solver='newton',tol=mp.power(10,-dps+10))
        assert z>1
        wz=weight(z);e4=mp.exp(4*z);sigma=int(mp.sign(mp.diff(qr,z)))
        qjet=[[mp.diff(lambda x:q(j,x),z,l)/wz for l in range(6)] for j in range(4)]
        r=[mp.mpf(0)]+[mp.diff(qr,z,l)/wz for l in range(1,6)]
        for j in range(4):
            for l in range(6):assert abs(qjet[j][l])<=E[j][l]*z**j*e4**l;checks+=1
        kap=(mp.fsum(qjet[j][0]*v[j] for j in range(3))-r[2]/6)/r[1]
        assert abs(kap)<46*e4;checks+=1
        samples=[]
        for factor in [mp.mpf(1)/2,mp.mpf(1)]:
            a=factor*eps/e4;c=z+kap*a*a;bb=[b[j]+v[j]*a*a for j in range(3)]
            def trial(x):return weight(x)*raw(x,bb)
            endpoint=[]
            for x in [z-3*a,z+3*a]:
                wx=weight(x);wr=[mp.diff(weight,x,l)/(wx*mp.exp(4*l*x)) for l in range(6)]
                for l in range(6):assert abs(wr[l])<=W[l];checks+=1
                r4=mp.diff(qr,x,4)/(wz*z**3*e4**3);r5=mp.diff(qr,x,5)/(wz*z**3*e4**4)
                derivative=sigma*mp.diff(trial,x)/(wz*z**3)
                assert abs(r4)<A4 and abs(r5)<A5 and derivative>200;checks+=3
                ratio=wx/wz;assert mp.mpf('.5')<ratio<2;checks+=1
                endpoint.append({'normalized_weight_derivatives':[mp.nstr(x,dps-10) for x in wr],
                    'normalized_residual_fourth':mp.nstr(r4,dps-10),'normalized_residual_fifth':mp.nstr(r5,dps-10),
                    'normalized_trial_derivative':mp.nstr(derivative,dps-10),'weight_ratio':mp.nstr(ratio,dps-10)})
            dv=[mp.mpf(0)]*3;dr=mp.mpf(0);avg=mp.mpf(0)
            for left,right,offset in [(c-a,z,1),(z,c+a,-1)]:
                center=(left+right)/2;half=(right-left)/2
                for nd,gw in zip(nodes,weights):
                    x=center+half*nd;fac=half*gw*sigma*((x-c)/a+offset)*weight(x)/wz
                    for j in range(3):dv[j]+=fac*p(j,x)
                    dr+=fac*raw(x,b)
            for nd,gw in zip(nodes,weights):
                x=c+a*nd;avg+=gw*trial(x)/(2*wz)
            mr=[(dv[j]-a*a*(-2*sigma*qjet[j][0]*kap-sigma*qjet[j][1]/3))/(a**4*z**j*e4**3) for j in range(3)]
            base=-sigma*r[1]*a*a/3-sigma*(r[1]*kap*kap+r[2]*kap/3+r[3]/60)*a**4
            rr=(dr-base)/(a**6*z**3*e4**4);bal=avg/(a**4*z**3*e4**3)
            for j in range(3):assert abs(mr[j])<H[j];checks+=1
            assert abs(rr)<Cs and abs(bal)<Ch;checks+=2
            samples.append({'active_fraction':mp.nstr(factor,10),'half_width':mp.nstr(a,dps-10),
              'endpoint_checks':endpoint,'normalized_moment_remainders':[mp.nstr(x,dps-10) for x in mr],
              'normalized_target_remainder':mp.nstr(rr,dps-10),'normalized_balance_defect':mp.nstr(bal,dps-10)})
        out.append({'phase_index':phase_index,'root':mp.nstr(z,dps-10),'kappa_over_exp4z':mp.nstr(kap/e4,dps-10),
                    'normalized_moment_jets':[[mp.nstr(qjet[j][l]/(z**j*e4**l),dps-10) for l in range(6)] for j in range(4)],
                    'samples':samples})
    return {'dps':dps,'quadrature_order':order,'theta_terms':12,'inequalities_checked':checks,'rows':out}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    op=HERE.parent/'theta_effective_remainder/results/certificate.json';apath=HERE/'results/algebra.json'
    old=json.loads(op.read_text());alg=json.loads(apath.read_text());runs=[]
    for dps,n in [(90,20),(130,28)]:
        runs.append(run(old,alg,dps,n));print('Independent tail check',dps,n,'passed',runs[-1]['inequalities_checked'],flush=True)
    mp.mp.dps=130;diffs=[]
    for lo,hi in zip(runs[0]['rows'],runs[1]['rows']):
        for l,h in zip(lo['samples'],hi['samples']):
            lv=l['normalized_moment_remainders']+[l['normalized_target_remainder'],l['normalized_balance_defect']]
            hv=h['normalized_moment_remainders']+[h['normalized_target_remainder'],h['normalized_balance_defect']]
            for x,y in zip(lv,hv):
                x,y=mp.mpf(x),mp.mpf(y);err=abs(x-y)/max(abs(y),mp.mpf('1e-100'))
                assert err<mp.mpf('1e-40');diffs.append(err)
    out={'status':'R26_independent_distant_switch_checks_passed','runs':runs,'precision_comparisons':len(diffs),
         'maximum_relative_precision_difference':mp.nstr(max(diffs),40),'source_sha256':sha(__file__),
         'R25_certificate_sha256':sha(op),'algebra_sha256':sha(apath),
         'trust_boundary':'Diagnostic only: central inputs, twelve theta terms and finitely many distant switches. Direct derivatives and ramp integrals corroborate the bounds but do not replace the analytic uniform weighted-tail proof.'}
    a.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['maximum_relative_precision_difference'])
if __name__=='__main__':main()
