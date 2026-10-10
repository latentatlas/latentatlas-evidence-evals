#!/usr/bin/env python3
"""R27 outward rational reconstruction; finite-cell formulas adapted from R25."""
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
def check_dual(data):
    d=data['dual'];a=data['arc'];co=data['coefficients'];checks=[]
    def ck(n,v):
        assert v,n
        checks.append(n)
    old=json.loads((HERE.parent/'theta_fourth_order/results/certificate.json').read_text())
    old15=json.loads((HERE.parent/'kernel_slope_asymptotics/results/asymptotic_certificate.json').read_text())
    B=vector(a['positive_moment_bounds']);offs=list(map(AU,vector(a['offsets'])))
    changes=[U(offs[0]*B[j+1]+offs[1]*B[j+2]/4+offs[2]*B[j+4]/16+offs[3]*B[j+6]/64) for j in range(4)]
    domain=vector(a['majorant_domain'])
    ck('negative_driver_width',restore(a['driver_width']).lo==F(1,65536))
    ck('moment_majorant_domain',offs[1]<domain[1].lo and offs[2]<domain[2].lo)
    grad=[]
    for j in range(3):
        errors=d['sign_change_errors'][j]
        grad.append(U(restore(old15['gradient_rows'][j]['absolute_gradient_upper'])+changes[j]
                      +sm(vector(errors['root_terms']))+restore(errors['integral_tail'])))
    C=matrix(d['preconditioner']);G=matrix(d['Gram']);radii=vector(d['radii'])
    CG=mm(C,G);defect=[[RI(i==j)-CG[i][j] for j in range(3)] for i in range(3)]
    contract=[U(sm(AU(defect[i][j])*radii[j]/radii[i] for j in range(3))) for i in range(3)]
    force=[U(sm(AU(C[i][j])*grad[j] for j in range(3))/radii[i]) for i in range(3)]
    for i in range(3):ck('uniform_dual_contraction_'+str(i),contract[i]+force[i]<1)
    ck('dual_tightening_factor',max(force)/(1-max(contract))<F('.161'))
    tails={k:restore(v) for k,v in old['tail_absolute_bounds'].items()}
    Gamma=RI(0);BB=[RI(0)]*3;RR=RI(0);GG=[[RI(0) for _ in range(3)] for _ in range(3)]
    for row,at in zip(d['tight_roots'],d['tight_jets']):
        q=matrix(at['moment_jets']);r=vector(at['residual_jets']);sig=row['orientation'];gamma=sig*r[1]
        ck('positive_coefficient_root_'+str(row['index']),gamma.lo>0)
        Gamma+=gamma
        for j in range(3):BB[j]+=sig*(q[j][0]*r[2]/r[1]-q[j][1])/3
        for i in range(3):
            for j in range(3):GG[i][j]+=2*q[i][0]*q[j][0]/gamma
        RR+=r[2]**2/(36*gamma)-sig*r[3]/60
    Gamma+=nonnegative(tails['Gamma']);BB=[x+symmetric(tails['B_entry']) for x in BB];RR+=symmetric(tails['R'])
    GG=[[GG[i][j]+(nonnegative(tails['G_entry']) if i==j else symmetric(tails['G_entry'])) for j in range(3)] for i in range(3)]
    v0=vector(co['solve_v0']);CG=mm(C,GG);error=[[RI(i==j)-CG[i][j] for j in range(3)] for i in range(3)]
    eta=max(U(sm(AU(x) for x in row)) for row in error);ck('uniform_linear_solve',eta<1)
    residue=[BB[i]-mv(GG,v0)[i] for i in range(3)];forcing=max(map(AU,mv(C,residue)));rad=forcing/(1-eta)
    vv=[v0[i]+symmetric(rad) for i in range(3)];P=sm(BB[j]*vv[j] for j in range(3))/2;Xi=RR-P
    bb=vector(d['tight_box']);prior=vector(old['dual_box'])
    dc=U(changes[3]+sm(max(AU(bb[j]),AU(prior[j]))*changes[j] for j in range(3)))
    D=restore(old['coefficients']['D'])+symmetric(dc);f=restore(co['f']);delta=f/D
    C2=delta**3*Gamma/(3*D);C4=delta**5*(Gamma**2/(3*D*D)-Xi/D)
    ck('uniform_positive_target',f.lo>0 and D.lo>0)
    ck('published_positive_C4',F('2.47e-39')<C4.lo<C4.hi<F('2.52e-39'))
    ck('positive_Xi',Xi.lo>0)
    for j,bound in enumerate([5,4,180]):ck('enlarged_v_bound_'+str(j),AU(vv[j])<bound)
    return {'f':f,'delta0':delta,'D':D,'Gamma':Gamma,'Xi':Xi,'C2':C2,'C4':C4},checks,contract,force

def run(data):
    cert=data['remainder'];a0=RI(F(1,16384));rho=RI(F(1,4000));Mlo=RI(F('2e-5'))
    co,dual_checks,dual_contraction,dual_force=check_dual(data)
    v=vector(data['coefficients']['v']);va=list(map(AU,v))
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
    ck('positive_fourth_correction_all_budgets',published[0]/Mlo.lo**2<F('2.47e-39'))
    ck('undersized_constant_negative_control',not kp<F('1e-54'))
    return {'status':'R27_independent_rational_bounds_passed','rounding_bits':BITS,
      'checks':dual_checks+checks,'check_count':len(dual_checks)+len(checks),
      'C4_interval':[str(co['C4'].lo),str(co['C4'].hi)],'Kminus_upper':str(km),'Kplus_upper':str(kp),
      'dual_contraction_upper':list(map(str,dual_contraction)),'dual_forcing_upper':list(map(str,dual_force)),
      'repair_contraction_upper':list(map(str,contraction)),'repair_forcing_upper':list(map(str,eta)),
      'published_constants':list(map(str,published)),'source_sha256':sha(__file__),
      'rational_helper_sha256':sha(HERE.parent/'theta_fourth_order/rational_intervals.py'),
      'trust_boundary':'Independent reconstruction of parameter-change bounds, dual contraction, Gram solve, coefficients, local remainders, moment repair and scalar bounds. Cusp/Taylor enclosures, local transcendental jets, root sign/contraction values, sign-motion integral estimates and whole-tail enclosures are explicit inputs. This does not mechanically prove the analytic chain.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    d=run(json.loads(args.certificate.read_text()));d['certificate_sha256']=sha(args.certificate)
    args.output.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['check_count'])
    print('C4',list(map(lambda x:float(F(x)),d['C4_interval'])))
    print('Kminus',float(F(d['Kminus_upper'])),'Kplus',float(F(d['Kplus_upper'])))
if __name__=='__main__':main()
