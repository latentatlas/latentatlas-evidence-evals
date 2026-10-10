#!/usr/bin/env python3
"""R30 outward rational reconstruction of the effective remainder on an R29 cell."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,math
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'theta_fourth_order'))
from rational_intervals import RI,restore,mv,mm,BITS

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def U(x):return RI(x).hi
def AU(x):return RI(x).abs_upper()
def sm(xs):return sum(xs,RI(0))
def vector(x):return list(map(restore,x))
def matrix(x):return list(map(vector,x))
def ppow(a,n):
    result=[RI(1)]
    for _ in range(n):
        out=[RI(0)]*(len(result)+len(a)-1)
        for i,x in enumerate(result):
            for j,y in enumerate(a):out[i+j]+=x*y
        result=out
    return result
def nonnegative(x):return RI(0,U(x))
def symmetric(x):return RI(-U(x),U(x))
def run(data):
    cert=data['remainder'];a0=RI(F(1,16384));rho=RI(F(1,4000));Mlo=RI(F('2e-5'))
    co={k:restore(data['coefficients'][k]) for k in ['f','delta0','D','Gamma','Xi','C2','C4']}
    v=vector(data['coefficients']['v']);va=list(map(AU,v))
    rootrows=[];H=[RI(0)]*3;Ks=RI(0);checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append(name)
    ck('positive_inputs',co['f'].lo>0 and co['D'].lo>0 and co['Xi'].lo>0)
    ck('tail_v_bounds',all(va[j]<x for j,x in enumerate([5,4,180])))
    ck('expanded_dual_tail_domain',all(AU(x)<lim for x,lim in zip(vector(cert['expanded_trial_dual_box']),[F('.001'),F('.1'),F('.005')])))
    ck('tail_gap_sign',restore(cert['tail_gap_residual']).lo>0)
    ck('finite_root_count',len(cert['local'])==28)
    ck('disjoint_root_neighborhoods',all(restore(a['neighborhood']).hi<restore(b['neighborhood']).lo for a,b in zip(cert['local'],cert['local'][1:])))
    # The partition is a cover of the full finite domain, not sampled signs.
    pieces=[]
    for leaf in cert['sign_cover']:
        lo,hi=restore(leaf['lo']),restore(leaf['hi'])
        assert lo.lo<hi.hi
        assert (leaf['sign']*restore(leaf['raw_residual'])).lo>0
        pieces.append((lo.lo,hi.hi,'sign'))
    for row in cert['local']:
        I=restore(row['neighborhood']);z=restore(row['root'])
        assert I.lo<z.lo<z.hi<I.hi
        pieces.append((I.lo,I.hi,'root'))
    pieces.sort()
    ck('full_finite_domain_partition',pieces[0][0]==0 and pieces[-1][1]==1 and all(a[1]>=b[0] for a,b in zip(pieces,pieces[1:])))
    ck('finite_sign_leaf_count',len(cert['sign_cover'])==354)
    for row in cert['local']:
        q=matrix(row['root_jets']['moment_jets']);r=vector(row['root_jets']['residual_jets'])
        Q=[[AU(x) for x in rowj] for rowj in matrix(row['neighborhood_jets']['moment_jets'])]
        R=list(map(AU,vector(row['neighborhood_jets']['residual_jets'])))
        kap=(sm(q[j][0]*v[j] for j in range(3))-r[2]/6)/r[1];ka=AU(kap)
        sig=row['orientation'];qd=restore(row['trial_neighborhood_jets']['residual_jets'][1]);m=(sig*qd).lo;L=AU(qd)
        ck('positive_trial_derivative_'+str(row['index']),m>0)
        h=[U(AU(q[j][1])*RI(ka)**2+AU(q[j][2])*(ka+RI(ka)**3*a0**2)/3
              +Q[j][3]*(RI(F(1,5))+2*RI(ka)**2*a0**2+RI(ka)**4*a0**4)/12) for j in range(3)]
        for j in range(3):H[j]+=h[j]
        ks=U(AU(r[2])*RI(ka)**3/3+AU(r[3])*(2*RI(ka)**2+RI(ka)**4*a0**2)/12
             +AU(r[4])*(ka+RI(F(10,3))*RI(ka)**3*a0**2+RI(ka)**5*a0**4)/60
             +R[5]*(RI(F(1,7))+3*RI(ka)**2*a0**2+5*RI(ka)**4*a0**4+RI(ka)**6*a0**6)/360)
        Ks+=ks
        hb=U(AU(r[2])*RI(ka)**2/2+AU(r[3])*(ka+RI(ka)**3*a0**2)/6
              +R[4]*(RI(F(1,5))+2*RI(ka)**2*a0**2+RI(ka)**4*a0**4)/24
              +sm(va[j]*(AU(q[j][1])*ka+Q[j][2]*(RI(F(1,3))+RI(ka)**2*a0**2)/2) for j in range(3)))
        ck('balanced_cell_inside_neighborhood_'+str(row['index']),U(RI(ka)*a0*a0+hb*a0**4/m+a0)<rho.lo and U(RI(ka)*a0)<1)
        rootrows.append({'q':q,'Q':Q,'ka':ka,'m':m,'L':L,'hb':hb,'sig':sig})
    alg=json.loads((HERE/'results/algebra.json').read_text())
    tailcert=json.loads((HERE.parent/'theta_global_remainder/results/certificate.json').read_text())
    eps=RI(F(alg['epsilon']));V=list(map(F,alg['v_absolute_bounds']))
    S={d:restore(tailcert['weighted_tail_bounds'][str(d)]['root_sum']) for d in [12,16,24]}
    I={d:restore(tailcert['weighted_tail_bounds'][str(d)]['integral']) for d in [12,16,24]}
    Hj=list(map(F,alg['active_moment_constants']));Cs=F(alg['active_residual_sixth_constant']);C8=F(alg['active_dual_eighth_constant'])
    ht=[U(Hj[j]*S[12]+188/eps**2*S[12]+2**(j+1)/eps**4*I[16]/(1-48*a0)) for j in range(3)]
    tail6=U(Cs*S[16]+sm(V[j]*Hj[j]*S[12] for j in range(3))+300/eps**4*S[16]
                  +2071000/eps**2*S[16]+18/eps**6*I[24]/(1-72*a0))
    tail8=U(C8*S[24]);H0=[U(x) for x in H];forcingH=[U(H[j]+ht[j]) for j in range(3)]
    J=[[-2*rootrows[k]['sig']*rootrows[k]['q'][j][0] for k in range(3)] for j in range(3)]
    C=matrix(cert['repair_preconditioner']);CJ=mm(C,J);E=[[RI(i==j)-CJ[i][j] for j in range(3)] for i in range(3)]
    ck('exact_preconditioner',all(x.lo==x.hi for row in C for x in row))
    W=vector(cert['repair_scaled_box'])
    variation=[[U(2*(rootrows[k]['Q'][j][1]*(rootrows[k]['ka']*a0**2+W[k]*a0**4)+rootrows[k]['Q'][j][2]*a0**2/6)) for k in range(3)] for j in range(3)]
    contraction=[U(sm((AU(E[i][k])+sm(AU(C[i][j])*variation[j][k] for j in range(3)))*W[k]/W[i] for k in range(3))) for i in range(3)]
    eta=[U(sm(AU(C[i][j])*forcingH[j] for j in range(3))/W[i]) for i in range(3)]
    for i in range(3):
        ck('moment_contraction_'+str(i),contraction[i]+eta[i]<1)
        ck('repaired_cell_inside_neighborhood_'+str(i),U(rootrows[i]['ka']*a0**2+W[i]*a0**4+a0)<rho.lo)
    K6=U(Ks+sm(va[j]*H0[j] for j in range(3)))
    K8d=U(sm(RI(row['hb'])**2/row['m'] for row in rootrows))
    K8p=U(sm(2*rootrows[k]['hb']*W[k]+rootrows[k]['L']*W[k]**2 for k in range(3)))
    Kd=U(K6+tail6+a0**2*(K8d+tail8));Kp=U(K6+tail6+a0**2*K8p)
    f,delta,D,Gamma,Xi=[co[k] for k in ['f','delta0','D','Gamma','Xi']]
    loss=U(Gamma*a0**2/3+AU(Xi)*a0**4+Kp*a0**6)
    Ubar=U(RI(delta.hi)/(1-RI(loss)/D.lo))
    ck('uniform_valid_width_and_positivity',Ubar<1 and U(RI(Ubar)/Mlo)<a0.lo)
    ck('lower_auxiliary_endpoint',(Gamma/3-Xi*delta**2/Mlo**2).lo>0)
    ck('upper_auxiliary_endpoint',(RI(Ubar)-delta-Gamma*RI(Ubar)**3/(3*D*Mlo**2)-Kp*RI(Ubar)**7/(D*Mlo**6)).lo>0)
    ck('auxiliary_scalar_monotonicity',(D-Gamma*RI(Ubar)**2/Mlo**2-7*Kp*RI(Ubar)**6/Mlo**6).lo>0)
    t=Gamma/(3*D);ee=Xi/D;cc=3*t*t-ee;p=[RI(1),t,cc];p3=ppow(p,3);p5=ppow(p,5)
    residual=[RI(0)]*13
    for i,x in enumerate(p):residual[i]+=x
    residual[0]-=1
    for i,x in enumerate(p3):residual[i+1]-=t*x
    for i,x in enumerate(p5):residual[i+2]+=ee*x
    wmax=U(delta**2/Mlo**2);pol=U(sm(AU(x)*RI(wmax)**(n-3) for n,x in enumerate(residual) if n>=3))
    Kpol=U(f*delta**6*pol);dmin=(D-Gamma*RI(Ubar)**2/Mlo**2).lo
    ck('scalar_inverse_monotone',dmin>0)
    ck('approximation_in_amplitude_interval',U(delta.hi+co['C2'].hi/Mlo**2+co['C4'].hi/Mlo**4)<Ubar)
    km=U((Kpol+Kd*RI(Ubar)**7)/dmin);kp=U((Kpol+Kp*RI(Ubar)**7)/dmin)
    published=[F('1.02e-53'),F('1.64e-53')]
    ck('uniform_published_lower_constant',0<km<published[0])
    ck('uniform_published_upper_constant',0<kp<published[1])
    ck('positive_fourth_correction_all_budgets',published[0]/Mlo.lo**2<co['C4'].lo)
    ck('undersized_constant_negative_control',not kp<F('1e-54'))
    return {'status':'R30_independent_rational_remainder_passed','rounding_bits':BITS,
      'checks':checks,'check_count':len(checks),
      'C4_interval':[str(co['C4'].lo),str(co['C4'].hi)],'Kminus_upper':str(km),'Kplus_upper':str(kp),
      'repair_contraction_upper':list(map(str,contraction)),'repair_forcing_upper':list(map(str,eta)),
      'published_constants':list(map(str,published)),'source_sha256':sha(__file__),
      'rational_helper_sha256':sha(HERE.parent/'theta_fourth_order/rational_intervals.py'),
      'trust_boundary':'Independent rational reconstruction of local remainders, moment repair and scalar inversion. R29 cusp, dual and coefficient boxes are frozen validated inputs; local transcendental jets and infinite-tail bounds are explicit inputs. R29 independently reconstructs its coefficients in its own audit. No mechanical proof of the analytic chain.'}

def main():
    import gzip
    from derivative_check import motion_check
    ap=argparse.ArgumentParser();ap.add_argument('--cover-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists();index=json.loads((args.cover_dir/'certificate.json').read_text())
    parent=HERE.parent/'cusp_motion_continuation/results/cover';out=[];count=0
    for row in index['cells']:
        p=args.cover_dir/row['file'];q=parent/row['file'];assert sha(p)==row['sha256'] and sha(q)==row['input_cell_sha256']
        new=json.loads(gzip.decompress(p.read_bytes()));old=json.loads(gzip.decompress(q.read_bytes()))
        assert new['input_cell_sha256']==sha(q) and new['index']==old['index']==row['index']
        first=run({**old['cell'],'remainder':new['remainder']});second=motion_check(old['motion'],old['cell'])
        count+=first['check_count']+second['check_count']
        out.append({'index':row['index'],'file_sha256':sha(p),'input_cell_sha256':sha(q),'remainder':first,'derivative_AD':second})
        print('rational cell',row['index']+1,'checks',first['check_count']+second['check_count'],flush=True)
    result={'status':'R30_rational_remainder_and_three_derivatives_passed','rounding_bits':BITS,'check_count':count,'cells':out,
      'source_sha256':sha(__file__),'derivative_source_sha256':sha(HERE/'derivative_check.py'),
      'rational_helper_sha256':sha(HERE.parent/'theta_fourth_order/rational_intervals.py'),
      'certificate_sha256':sha(args.cover_dir/'certificate.json')}
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],count)
if __name__=='__main__':main()
