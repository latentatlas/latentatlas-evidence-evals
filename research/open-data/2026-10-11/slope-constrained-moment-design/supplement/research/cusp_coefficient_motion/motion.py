"""Derivative of the moving exact fourth-order coefficient; Arb arithmetic."""
import sys
sys.dont_write_bytecode=True
import hashlib,json
from pathlib import Path
from math import comb,factorial
from fractions import Fraction as F
from flint import arb,arb_mat
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/'cusp_uniform_remainder'))
import model as base
restore,pack,rational,upper,absup,sm=base.restore,base.pack,base.rational,base.upper,base.absup,base.sm
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def unbox(x):
    if isinstance(x,dict):
        if 'mid_man_exp' in x:return restore(x)
        return {k:unbox(v) for k,v in x.items()}
    if isinstance(x,list):return [unbox(v) for v in x]
    return x
def sym(x):return base.symmetric(x)
def matrix(A):return arb_mat(A)
def rows(A):return [[A[i,j] for j in range(A.ncols())] for i in range(A.nrows())]
def pjets(u,tau,nmax,order):
    z=2*tau*u;trig=[z.cos(),-z.sin(),-z.cos(),z.sin()]
    return [[sm(comb(l,h)*(factorial(j)//factorial(j-h))*2**j*u**(j-h)*(2*tau)**(l-h)*trig[(j+l-h)%4]
            for h in range(min(j,l)+1)) for l in range(order+1)] for j in range(nmax+1)]
def root_jets(z,params,b):
    data=base.jet(z,params,b,order=4,root=True);w=data['weight_jets'];p=pjets(z,params[0],9,4)
    q=[[sm(comb(l,k)*w[k]*p[j][l-k] for k in range(l+1)) for l in range(5)] for j in range(10)]
    return {**data,'p_jets_extended':p,'moment_jets_extended':q}
def solve(G,y,C):
    G=matrix(G);C=matrix(C);y=matrix([[a] for a in y]);candidate=G.inv()*y
    v0=matrix([[candidate[i,0].mid()] for i in range(3)])
    defect=matrix([[arb(i==j)-(C*G)[i,j] for j in range(3)] for i in range(3)])
    eta=upper(max(upper(sm(absup(defect[i,j]) for j in range(3))) for i in range(3)));assert eta<1
    residual=C*(y-G*v0);forcing=upper(max(absup(residual[i,0]) for i in range(3)))
    radius=upper(forcing/(1-eta));answer=[v0[i,0]+sym(radius) for i in range(3)]
    return answer,{'seed':[v0[i,0] for i in range(3)],'preconditioner':rows(C),'defect':rows(defect),
      'eta':eta,'forcing':forcing,'radius':radius,'solution':answer}
def moving_sign_moments(cert,new9):
    old=unbox(read(RESEARCH/'kernel_norm_threshold/results/threshold_certificate.json'))
    arc=cert['arc'];params=arc['parameter_box'];b=cert['dual']['tight_box'];B=arc['positive_moment_bounds']
    dt,dl,dm,dn=map(absup,arc['offsets']);moments=old['step_moments_at_exact_Q']+[new9['moment_at_exact_Q']]
    records=[];out=[]
    for n in range(10):
        E=upper(dt*B[n+1]+dl*B[n+2]/4+dm*B[n+4]/16+dn*B[n+6]/64);terms=[]
        for root,knot in zip(cert['dual']['tight_roots'],old['breakpoints']):
            lo=min(root['root'].lower(),knot);hi=max(root['root'].upper(),knot)
            hull=(lo+hi)/2+sym((hi-lo)/2)
            weight=base.jet(hull,params,b,order=0)['weight_jets'][0]
            p=pjets(hull,params[0],n,0)[n][0];terms.append(upper(2*(hi-lo)*absup(weight*p)))
        # All sign differences beyond 1 are included. For n<=9 the log
        # derivative of 88*(2u)^n*exp(9u+9u^4-pi*exp(4u)) is <-540.
        tail=upper(2*88*2**n*(18-arb.pi()*arb(4).exp()).exp()/540)
        err=upper(E+sm(terms)+tail);out.append(moments[n]+sym(err))
        records.append({'order':n,'base_template_moment':moments[n],'L1_change':E,
          'root_motion_terms':terms,'whole_sign_tail':tail,'error':err,'enclosure':out[-1]})
    # These identities hold exactly at the already proved moving dual optimum.
    out[:3]=[arb(0)]*3;out[3]=cert['coefficients']['D']
    return out,records
def tail_constants():
    old=read(RESEARCH/'theta_global_remainder/results/algebra.json')
    W=list(map(F,old['weight_relative_constants']));b=[F(1,1000),F(1,10),F(1,200)]
    P=[[F(2**j)*sum(F(comb(l,h)*(factorial(j)//factorial(j-h))*84**(l-h)) for h in range(min(j,l)+1))
        for l in range(5)] for j in range(10)]
    K=[[sum(F(comb(l,k))*W[k]*P[j][l-k] for k in range(l+1)) for l in range(5)] for j in range(10)]
    H=[[K[j+1][l]+K[j+2][l]/4+K[j+4][l]/16+K[j+6][l]/64 for l in range(4)] for j in range(4)]
    A=[K[3][l]+sum(b[j]*K[j][l] for j in range(3)) for l in range(5)]
    L=[H[3][l]+sum(b[j]*H[j][l] for j in range(3))+10*sum(K[j][l] for j in range(3))+A[l+1] for l in range(4)]
    D=[[H[j][l]+K[j][l+1] for l in range(4)] for j in range(3)]
    cg=max(2*((D[i][0]*K[j][0]+K[i][0]*D[j][0])/567+K[i][0]*K[j][0]*L[1]/567**2) for i in range(3) for j in range(3))
    cb=max(((D[j][0]*A[2]+K[j][0]*L[2])/567+K[j][0]*A[2]*L[1]/567**2+D[j][1])/3 for j in range(3))
    cr=A[2]*L[2]/(18*567)+A[2]**2*L[1]/(36*567**2)+L[3]/60
    envelopes={'dual_rhs':(F(1),3,0),'Gamma_prime':(L[1],9,8),'G_prime_entry':(cg,7,8),'B_prime_entry':(cb,8,16),'R_prime':(cr,9,24)}
    return {'weight_constants':W,'p_constants':P,'q_constants':K,'parameter_partial_constants':H,
      'raw_density_constants':A,'total_residual_derivative_constants':L,'total_moment_derivative_constants':D,
      'envelopes':envelopes,'bprime_component_bound':10,'root_velocity_bound':'u',
      'log_decay_lower':500,'root_spacing_lower':F(3,85),'geometric_ratio_upper':F(1,50**4)}
def tails(constants):
    den=1-rational(constants['geometric_ratio_upper']);out={}
    for name,(C,p,d) in constants['envelopes'].items():
        assert p+9+d+36<100 and 600-(p+9+d+36)>500
        out[name]=upper(88*rational(C)*(18+d-arb.pi()*arb(4).exp()).exp()/den)
    return out
def produce(cert,new9):
    arc=cert['arc'];params=arc['parameter_box'];vel=arc['refined_velocity'];b=cert['dual']['tight_box'];co=cert['coefficients']
    assert all(absup(x)<1 for x in vel)
    roots=cert['dual']['tight_roots'];jets=[root_jets(r['root'],params,b) for r in roots]
    S,srecords=moving_sign_moments(cert,new9);tt=tail_constants();tail=tails(tt)
    def partial(values,j):return vel[0]*values[j+1]-vel[1]*values[j+2]/4+vel[2]*values[j+4]/16-values[j+6]/64
    Sd=[partial(S,j) for j in range(4)];rhs=Sd[:3];rterms=[]
    for root,at in zip(roots,jets):
        p=at['p_jets_extended'];q=at['moment_jets_extended'];gamma=root['orientation']*at['residual_jets'][1]
        rawtau=p[4][0]-sm(b[j]*p[j+1][0] for j in range(3))
        part=at['weight_jets'][0]*vel[0]*rawtau
        terms=[2*q[j][0]*part/gamma for j in range(3)];rterms.append(terms)
        rhs=[rhs[j]+terms[j] for j in range(3)]
    rhs=[x+sym(tail['dual_rhs']) for x in rhs]
    bp,solution=solve(co['G'],rhs,cert['dual']['preconditioner']);assert all(absup(x)<10 for x in bp)
    Dp=Sd[3]-sm(b[j]*Sd[j] for j in range(3));fp=partial(arc['derivatives'],3)
    gp=arb(0);Bp=[arb(0)]*3;Gp=[[arb(0)]*3 for _ in range(3)];Rp=arb(0);records=[]
    for root,at in zip(roots,jets):
        sig=root['orientation'];q=at['moment_jets_extended'];p=at['p_jets_extended'];r=at['residual_jets']
        rawtau=p[4][0]-sm(b[j]*p[j+1][0] for j in range(3));rawprime=p[3][1]-sm(b[j]*p[j][1] for j in range(3))
        zp=(sm(bp[j]*p[j][0] for j in range(3))-vel[0]*rawtau)/rawprime
        qdot=[[partial([q[n][l] for n in range(10)],j) for l in range(4)] for j in range(4)]
        rd=[qdot[3][l]-sm(b[j]*qdot[j][l]+bp[j]*q[j][l] for j in range(3))+r[l+1]*zp for l in range(4)]
        qt=[[qdot[j][l]+q[j][l+1]*zp for l in range(2)] for j in range(3)]
        gam=sig*r[1];gamd=sig*rd[1];gp+=gamd
        bg=[sig*((qt[j][0]*r[2]+q[j][0]*rd[2])/r[1]-q[j][0]*r[2]*rd[1]/r[1]**2-qt[j][1])/3 for j in range(3)]
        gg=[[2*((qt[i][0]*q[j][0]+q[i][0]*qt[j][0])/gam-q[i][0]*q[j][0]*gamd/gam**2) for j in range(3)] for i in range(3)]
        rr=r[2]*rd[2]/(18*gam)-r[2]**2*gamd/(36*gam**2)-sig*rd[3]/60
        Bp=[Bp[j]+bg[j] for j in range(3)];Gp=[[Gp[i][j]+gg[i][j] for j in range(3)] for i in range(3)];Rp+=rr
        records.append({'index':root['index'],'root':root['root'],'orientation':sig,'jets':at,'root_velocity':zp,
          'fixed_u_moment_derivatives':qdot,'total_residual_derivatives':rd,'total_moment_derivatives':qt,
          'Gamma_prime':gamd,'B_prime':bg,'G_prime':gg,'R_prime':rr})
    gp+=sym(tail['Gamma_prime']);Bp=[x+sym(tail['B_prime_entry']) for x in Bp]
    Gp=[[x+sym(tail['G_prime_entry']) for x in row] for row in Gp];Rp+=sym(tail['R_prime'])
    v=co['v'];Pp=sm(Bp[j]*v[j] for j in range(3))-sm(v[i]*Gp[i][j]*v[j] for i in range(3) for j in range(3))/2
    Xp=Rp-Pp;D=co['D'];f=co['f'];delta=co['delta0'];G=co['Gamma'];X=co['Xi']
    delta_log=fp/f-Dp/D;delta_p=delta*delta_log
    H=G**2/(3*D**2)-X/D
    Hp=2*G*gp/(3*D**2)-2*G**2*Dp/(3*D**3)-Xp/D+X*Dp/(D**2)
    C4p=delta**5*(5*delta_log*H+Hp)
    C2p=co['C2']*(3*delta_log+gp/G-Dp/D)
    return {'sign_moments':S,'sign_transport':srecords,'sign_partial_derivatives':Sd,'dual_rhs_root_terms':rterms,
      'dual_rhs':rhs,'dual_derivative_solve':solution,'b_prime':bp,'root_derivatives':records,
      'tail_derivative_bounds':tail,'derivatives':{'f':fp,'D':Dp,'delta0':delta_p,'Gamma':gp,
       'B':Bp,'G':Gp,'R':Rp,'P':Pp,'Xi':Xp,'C2':C2p,'C4':C4p},
      'C4_log_delta_contribution':delta**5*5*delta_log*H,'C4_shape_contribution':delta**5*Hp}
