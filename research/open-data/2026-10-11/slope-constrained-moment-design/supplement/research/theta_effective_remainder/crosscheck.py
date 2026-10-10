#!/usr/bin/env python3
"""Independent numerical derivatives and direct ramp integrals; diagnostic only."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from math import factorial
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(rec):
    m,e=rec['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def rad(rec):
    m,e=rec['rad_man_exp'];return mp.mpf(m)*mp.power(2,e)
def up(rec):return mid(rec)+rad(rec)
def inside(rec,x):return abs(mid(rec)-x)<=rad(rec)
def run(cert,dps,order):
    mp.mp.dps=dps;tau,lam,mu=map(mid,cert['Q_box']);b=list(map(mid,cert['dual_box']));v=list(map(mid,cert['v_enclosure']))
    def pj(j,x):return (2*x)**j*mp.cos(2*tau*x+j*mp.pi/2)
    def raw(x):return pj(3,x)-mp.fsum(b[j]*pj(j,x) for j in range(3))
    def w(x):
        ee=mp.exp(4*x)
        return mp.pi*mp.exp(5*x+lam*x*x+mu*x**4)*mp.fsum(n*n*(2*mp.pi*n*n*ee-3)*mp.exp(-mp.pi*n*n*ee) for n in range(1,13))
    def q(j,x):return w(x)*pj(j,x)
    def qr(x):return w(x)*raw(x)
    nodes,weights=mp.gauss_quadrature(order,'legendre')
    widths=[mp.power(2,-k) for k in [14,18,22]]
    output=[];jet_checks=0;inequality_checks=0
    for row in cert['local']:
        z=mp.findroot(raw,mid(row['root']),solver='newton',tol=mp.power(10,-dps+10));assert inside(row['root'],z)
        qjets=[[mp.diff(lambda x:q(j,x),z,l) for l in range(6)] for j in range(4)]
        rjets=[mp.mpf(0)]+[mp.diff(qr,z,l) for l in range(1,6)]
        for j in range(4):
            for l in range(6):assert inside(row['root_jets']['moment_jets'][j][l],qjets[j][l]);jet_checks+=1
        for l in range(1,6):assert inside(row['root_jets']['residual_jets'][l],rjets[l]);jet_checks+=1
        sig=row['orientation'];kap=(mp.fsum(qjets[j][0]*v[j] for j in range(3))-rjets[2]/6)/rjets[1]
        assert inside(row['kappa'],kap)
        samples=[]
        for a in widths:
            c=z+kap*a*a;dv=[mp.mpf(0)]*3;dr=mp.mpf(0)
            for left,right,offset in [(c-a,z,1),(z,c+a,-1)]:
                half=(right-left)/2;center=(left+right)/2
                for nd,gw in zip(nodes,weights):
                    x=center+half*nd;weight=half*gw*sig*((x-c)/a+offset)*w(x)
                    ps=[pj(j,x) for j in range(4)]
                    for j in range(3):dv[j]+=weight*ps[j]
                    dr+=weight*(ps[3]-mp.fsum(b[j]*ps[j] for j in range(3)))
            avg=mp.mpf(0)
            for nd,gw in zip(nodes,weights):
                x=c+a*nd;avg+=gw*w(x)*(raw(x)-a*a*mp.fsum(v[j]*pj(j,x) for j in range(3)))/2
            mr=[(dv[j]-a*a*(-2*sig*qjets[j][0]*kap-sig*qjets[j][1]/3))/a**4 for j in range(3)]
            lr=-sig*rjets[1]*a*a/3-sig*(rjets[1]*kap*kap+rjets[2]*kap/3+rjets[3]/60)*a**4
            rr=(dr-lr)/a**6;balance=avg/a**4
            for j in range(3):assert abs(mr[j])<up(row['moment_fourth_bound'][j]);inequality_checks+=1
            assert abs(rr)<up(row['residual_sixth_bound']);inequality_checks+=1
            assert abs(balance)<up(row['balance_fourth_bound']);inequality_checks+=1
            samples.append({'half_width':mp.nstr(a,dps-8),'scaled_moment_remainders':[mp.nstr(x,dps-8) for x in mr],
                            'scaled_residual_remainder':mp.nstr(rr,dps-8),'scaled_balance_defect':mp.nstr(balance,dps-8)})
        output.append({'index':row['index'],'root':mp.nstr(z,dps-8),'kappa':mp.nstr(kap,dps-8),
              'moment_jets':[[mp.nstr(x,dps-8) for x in rr] for rr in qjets],
              'residual_jets':[mp.nstr(x,dps-8) for x in rjets],'samples':samples})
    return {'dps':dps,'quadrature_order':order,'theta_terms':12,'rows':output,'jet_comparisons':jet_checks,
            'local_remainder_inequalities':inequality_checks}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    cert=json.loads(a.certificate.read_text());runs=[]
    for dps,n in [(80,20),(110,28)]:
        runs.append(run(cert,dps,n));print('Independent jets and ramp integrals passed',dps,n,flush=True)
    mp.mp.dps=110;differences=[]
    for lo,hi in zip(runs[0]['rows'],runs[1]['rows']):
        for l,h in zip(lo['samples'],hi['samples']):
            lv=l['scaled_moment_remainders']+[l['scaled_residual_remainder'],l['scaled_balance_defect']]
            hv=h['scaled_moment_remainders']+[h['scaled_residual_remainder'],h['scaled_balance_defect']]
            for x,y in zip(lv,hv):
                x,y=mp.mpf(x),mp.mpf(y);dif=abs(x-y)/max(abs(y),mp.mpf('1e-100'))
                assert dif<mp.mpf('1e-40');differences.append(dif)
    out={'status':'R25_independent_numerical_local_checks_passed','runs':runs,
       'max_relative_precision_difference':mp.nstr(max(differences),40),'precision_comparisons':len(differences),
       'source_sha256':sha(__file__),'certificate_sha256':sha(a.certificate),
       'trust_boundary':'Central inputs and twelve theta terms. mpmath derivatives and direct piecewise Gauss ramp integrals corroborate the local bounds; these samples do not prove a supremum bound, exact moment repair, whole-tail estimate, or optimal value enclosure.'}
    a.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['max_relative_precision_difference'])
if __name__=='__main__':main()
