#!/usr/bin/env python3
"""Independent outward-rounded rational reconstruction of the R25 inequalities."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'theta_fourth_order'))
from rational_intervals import RI,restore,mv,mm,BITS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def U(x):return RI(x).hi
def AU(x):return RI(x).abs_upper()
def sm(xs):return sum(xs,RI(0))
def vector(v):return list(map(restore,v))
def matrix(v):return list(map(vector,v))
def pmul(a,b):
    c=[RI(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c
def ppow(a,n):
    p=[RI(1)]
    for _ in range(n):p=pmul(p,a)
    return p
def run(cert):
    a0=restore(cert['maximum_half_width']);amin=restore(cert['minimum_half_width']);rho=restore(cert['neighborhood_radius'])
    Mlo,Mhi=vector(cert['budget_interval']);v=vector(cert['v_enclosure']);va=list(map(AU,v))
    co={k:restore(x) for k,x in cert['coefficient_inputs'].items()};tails={k:restore(x) for k,x in cert['tail_coefficient_inputs'].items()}
    rootrows=[];H=[RI(0)]*3;Ks=RI(0);checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append(name)
    # The partition is a cover of the full finite domain, not sampled signs.
    pieces=[]
    for leaf in cert['sign_cover']:
        lo,hi=restore(leaf['lo']),restore(leaf['hi'])
        assert lo.lo==lo.hi and hi.lo==hi.hi and lo.lo<hi.lo
        assert (leaf['sign']*restore(leaf['raw_residual'])).lo>0
        pieces.append((lo.lo,hi.lo,'sign'))
    for row in cert['local']:
        I=restore(row['neighborhood']);z=restore(row['root'])
        assert I.lo<z.lo<z.hi<I.hi
        pieces.append((I.lo,I.hi,'root'))
    pieces.sort()
    ck('full_finite_domain_partition',pieces[0][0]==0 and pieces[-1][1]==1 and all(a[1]==b[0] for a,b in zip(pieces,pieces[1:])))
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
    tailq=vector(cert['tail_q_integrals']);expanded=vector(cert['expanded_trial_dual_box'])
    T0=U(2*(tailq[3]+sm(AU(expanded[j])*tailq[j] for j in range(3))))
    lead=U(tails['B_entry']+tails['G_entry']*sm(va))
    H0=[U(x) for x in H];forcingH=[U(H[j]+lead/amin**2+2*tailq[j]/amin**4) for j in range(3)]
    J=[[-2*rootrows[k]['sig']*rootrows[k]['q'][j][0] for k in range(3)] for j in range(3)]
    C=matrix(cert['moment_preconditioner']);CJ=mm(C,J);E=[[RI(i==j)-CJ[i][j] for j in range(3)] for i in range(3)]
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
    xt=U(tails['R']+tails['G_entry']*sm(va)**2/2+tails['B_entry']*sm(va))
    tail6=U(tails['Gamma']/(3*amin**4)+xt/amin**2+T0/amin**6)
    Kd=U(K6+K8d*a0**2+tail6);Kp=U(K6+K8p*a0**2+tail6)
    f,delta,D,Gamma,Xi=[co[k] for k in ['f','delta0','D','Gamma','Xi']]
    loss=U(Gamma*a0**2/3+AU(Xi)*a0**4+Kp*a0**6)
    ck('positive_normalized_target',loss<D.lo)
    Ubar=U(RI(delta.hi)/(1-RI(loss)/D.lo))
    ck('primal_budget_endpoint_coverage',U(RI(Ubar)/a0)<Mlo.lo and (RI(delta.lo)/amin).lo>Mhi.hi)
    ck('optimal_amplitude_width_coverage',U(RI(Ubar)/Mlo)<a0.lo and (RI(delta.lo)/Mhi).lo>amin.hi)
    t=Gamma/(3*D);ee=Xi/D;cc=3*t*t-ee;p=[RI(1),t,cc];p3=ppow(p,3);p5=ppow(p,5)
    residual=[RI(0)]*13
    for i,x in enumerate(p):residual[i]+=x
    residual[0]-=1
    for i,x in enumerate(p3):residual[i+1]-=t*x
    for i,x in enumerate(p5):residual[i+2]+=ee*x
    wmax=U(delta**2/Mlo**2);pol=U(sm(AU(x)*RI(wmax)**(n-3) for n,x in enumerate(residual) if n>=3))
    Kpol=U(f*delta**6*pol);dmin=(RI(D.lo)-Gamma.hi*RI(Ubar)**2/Mlo**2).lo
    ck('scalar_inverse_monotone',dmin>0 and Xi.lo>0)
    ck('approximation_in_amplitude_interval',U(delta.hi+co['C2'].hi/Mlo**2+co['C4'].hi/Mlo**4)<Ubar)
    km=U((Kpol+Kd*RI(Ubar)**7)/dmin);kp=U((Kpol+Kp*RI(Ubar)**7)/dmin)
    published=[F('9.593e-54'),F('1.488e-53')]
    ck('published_lower_remainder_constant',0<km<published[0])
    ck('published_upper_remainder_constant',0<kp<published[1])
    ck('positive_quartic_correction_whole_window',published[0]<F('2.49203004e-39')*Mlo.lo**2)
    # A smaller-than-computed remainder constant must fail the same acceptance rule.
    ck('undersized_constant_negative_control',not kp<F('1e-54'))
    return {'status':'R25_independent_rational_bounds_passed','rounding_bits':BITS,'checks':checks,'check_count':len(checks),
      'Kminus_upper':str(km),'Kplus_upper':str(kp),'published_constants':list(map(str,published)),
      'contraction_upper':list(map(str,contraction)),'forcing_upper':list(map(str,eta)),
      'source_sha256':sha(__file__),'rational_helper_sha256':sha(HERE.parent/'theta_fourth_order/rational_intervals.py'),
      'trust_boundary':'Independently reconstructs bounds from interval jets. The jets, sign-cover values, infinite-tail enclosures and exact-Q/root identities remain explicit analytic/transcendental inputs; this is not a proof-assistant verification.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    data=run(json.loads(a.certificate.read_text()));data['certificate_sha256']=sha(a.certificate)
    a.output.write_text(json.dumps(data,indent=2)+'\n');print(data['status'],data['check_count'])
    print('Kminus',float(F(data['Kminus_upper'])),'Kplus',float(F(data['Kplus_upper'])))
if __name__=='__main__':main()
