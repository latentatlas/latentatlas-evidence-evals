#!/usr/bin/env python3
"""R16 quantitative contraction and explicit O(M^-3) remainder constants."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json,time
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'kernel_slope_asymptotics'))
from certify_asymptotics import restore,pack,upper,zero_ball
from flint import arb,arb_mat,ctx
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,msg):
    if not v:raise ArithmeticError(msg)
def rational(s):
    v=Q(s);return arb(v.numerator)/arb(v.denominator)
def jet(u,x,a,N=12):
    """Enclose q_j and its first two u derivatives, j=0..3, and q_r."""
    pi=arb.pi();tau,lam,mu=x
    phi=[arb(0)]*3
    polynomials=[[-3,2],[-15,30,-8],[-75,330,-224,32]]
    for k in range(1,N+1):
        X=pi*k*k*(4*u).exp();factor=pi*k*k*(5*u-X).exp()
        for l,P in enumerate(polynomials):
            value=sum((coef*X**i for i,coef in enumerate(P)),arb(0));phi[l]+=factor*value
    lo,hi=u.lower(),u.upper();k=N+1
    errors=[]
    # The positive absolute monomial ratio for k>=13 is <1/2.
    # Use mixed endpoints for a pointwise enclosure across this u interval.
    for l,P in enumerate(polynomials):
        bound=upper(2*sum((abs(coef)*pi**(i+1)*k**(2*i+2)*((5+4*i)*hi-pi*k*k*(4*lo).exp()).exp() for i,coef in enumerate(P)),arb(0)))
        errors.append(bound);phi[l]+=zero_ball(bound)
    potential=lam*u*u+mu*u**4;ex=potential.exp();dP=2*lam*u+4*mu*u**3;ddP=2*lam+12*mu*u*u
    w=[ex*phi[0],ex*(phi[1]+dP*phi[0]),ex*(phi[2]+2*dP*phi[1]+(dP*dP+ddP)*phi[0])]
    q=[]
    for n in range(4):
        z=2*tau*u;cs=[z.cos(),-z.sin(),-z.cos(),z.sin()][n%4];sn=[z.sin(),z.cos(),-z.sin(),-z.cos()][n%4]
        p=(2*u)**n*cs
        dp=(2*n*(2*u)**(n-1)*cs if n else arb(0))-2*tau*(2*u)**n*sn
        ddp=(4*n*(n-1)*(2*u)**(n-2)*cs if n>=2 else arb(0))-(8*n*tau*(2*u)**(n-1)*sn if n else arb(0))-4*tau*tau*(2*u)**n*cs
        q.append([w[0]*p,w[1]*p+w[0]*dp,w[2]*p+2*w[1]*dp+w[0]*ddp])
    qr=[q[3][l]-sum((a[j]*q[j][l] for j in range(3)),arb(0)) for l in range(3)]
    return dict(interval=u,theta_series_errors=errors,moment_jets=q,residual_density_jets=qr)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    need(not args.output.exists(),'Refuse overwrite');ctx.dps=110;start=time.monotonic()
    paths={'R15':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_certificate.json',
        'R15_check':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_check.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json'}
    data={k:json.loads(p.read_text()) for k,p in paths.items()};old=data['R15'];x=list(map(restore,old['Q_box']));aa=list(map(restore,old['dual_coefficient_box']))
    rows=old['uniform_roots'];a0=arb(2)**-14;M0=rational('0.00002');V=[arb(512),arb(768),arb(384)]
    L=rational('0.00000000091787079603827');U=rational('0.00000000091787079608363')
    f3=restore(data['jets']['F_at_exact_Q'][3]);gamma=restore(old['weighted_root_sum'])
    need(x[0]>41 and x[0]<42 and x[1]>-4 and x[1]<0 and x[2]>0 and x[2]<9,'Tail parameter ranges')
    # Explicit common positive envelopes for q_j derivatives on the tail.
    pi=arb.pi();C0=4*pi*pi+6*pi;C1=60*pi*pi+30*pi+16*pi**3;C2=660*pi*pi+150*pi+448*pi**3+64*pi**4
    W0=C0;W1=C1+44*C0;W2=C2+88*C1+(44**2+116)*C0
    tail_constants=[]
    for j in range(4):
        tail_constants.append([2**j*W0,2**j*(W1+(j+84)*W0),2**j*(W2+2*(j+84)*W1+(j*(j-1)+168*j+84**2)*W0)])
    v0=1-a0;muplus=x[2].upper();decay=4*pi*(4*v0).exp()-4*muplus*v0**3-17-9/(1+v0)
    need(v0>arb(3)/4 and decay*3/85>16,'Derivative-envelope tail decay')
    envelope=((17*v0+muplus*v0**4-pi*(4*v0).exp()).exp()*(1+v0)**9)/(1-arb(1)/50**4)
    tail=[[upper(v*envelope) for v in row] for row in tail_constants]
    tail_r2=upper(tail[3][2]+arb(1)/1000*tail[0][2]+arb(1)/10*tail[1][2]+arb(1)/200*tail[2][2])
    # Exact root centers remain unknown, but the entire calculation covers
    # their R15 enclosures and uses exact zero/sign moment identities.
    local=[];center_jets=[];sum_q2=[arb(0)]*3;sum_r2=arb(0);forcing=[arb(0)]*3
    for k,row in enumerate(rows):
        root=restore(row['root_interval']);center=jet(root,x,aa);center_jets.append(center)
        shift=a0*a0*V[k] if k<3 else arb(0)
        u=root+zero_ball(upper(a0+shift));record=jet(u,x,aa);dk=-2*(-1)**k
        record.update(index=k,root_interval=root,jump=dk,shift_radius=shift)
        for j in range(3):
            sum_q2[j]+=upper(abs(record['moment_jets'][j][2]))
            forcing[j]+=dk*center['moment_jets'][j][1]/6
        sum_r2+=upper(abs(record['residual_density_jets'][2]));local.append(record)
    sum_q2=[upper(v+tail[j][2]) for j,v in enumerate(sum_q2)];sum_r2=upper(sum_r2+tail_r2)
    forcing=[v+zero_ball(upper(tail[j][1]/3)) for j,v in enumerate(forcing)]
    J=arb_mat([[-rows[k]['sign_before']*(-2)*center_jets[k]['moment_jets'][j][0] for k in range(3)] for j in range(3)])
    # J_jk=-d_k q_j(z_k), d_k=-2*(-1)^k.
    need(not J.det().contains(0),'Switch Jacobian singular')
    inv=J.inv();B=arb_mat([[inv[j,k].mid() for k in range(3)] for j in range(3)])
    need(all(B[j,k].is_exact() for j in range(3) for k in range(3)),'Preconditioner not exact dyadic')
    E=arb_mat(3,3)
    for j in range(3):
        for k in range(3):E[j,k]=(1 if j==k else 0)-(B*J)[j,k]
    BF=B*arb_mat([[v] for v in forcing]);derivative_change=[]
    for j in range(3):
        derivative_change.append([upper(2*a0*a0*(V[k]*abs(local[k]['moment_jets'][j][1])+abs(local[k]['moment_jets'][j][2])/6)) for k in range(3)])
    kappas=[];etas=[];component_bounds=[]
    for i in range(3):
        matrixrow=[upper(abs(E[i,k])+sum((abs(B[i,j])*derivative_change[j][k] for j in range(3)),arb(0))) for k in range(3)]
        kap=upper(sum((matrixrow[k]*V[k] for k in range(3)),arb(0))/V[i]);kappas.append(kap)
        eta=upper((abs(BF[i,0])+a0*sum((abs(B[i,j])*sum_q2[j] for j in range(3)),arb(0))/12)/V[i]);etas.append(eta)
        component_bounds.append(matrixrow)
        need(kap+eta<1,'Quantitative implicit-function contraction failed')
    # Every ramp and every selected center stays in its assigned disjoint cell.
    need(all(local[k]['interval'].upper()<local[k+1]['interval'].lower() for k in range(27)),'Finite transition overlap')
    need(local[0]['interval']>0 and local[-1]['interval'].upper()<1-a0 and 2*a0<arb(3)/85,'Boundary or tail transition overlap')
    A3=upper(sum_r2/12);A4=upper(sum((abs(local[k]['residual_density_jets'][1])*V[k]**2+abs(local[k]['residual_density_jets'][2])*V[k]/3 for k in range(3)),arb(0)))
    Dlow=(f3/U).lower();Gup=gamma.upper();Emax=upper(Gup*a0*a0/3+A3*a0**3+A4*a0**4)
    need(Emax<Dlow,'Residual moment positivity');Ubar=upper(U/(1-Emax/Dlow));need(Ubar/a0<M0 and Ubar<1,'Budget coverage or positivity')
    C_lo=rational('9.20340371e-25');C_hi=rational('9.20340375e-25')
    denom=(Dlow-Gup*Ubar**2/M0**2).lower();need(denom>0,'Upper remainder absorption fails')
    Kminus=upper(U**5*sum_r2/(12*f3.lower()))
    Kplus=upper((A3*Ubar**4+(A4*Ubar**5+Gup*Ubar**2*C_hi)/M0)/denom)
    relative=upper(max(Kminus,Kplus)/(C_lo*M0))
    out=dict(status='uniform_large_slope_remainder_constants_certified',input_sha256={k:sha(p) for k,p in paths.items()},
        source_sha256={'certify_remainder.py':sha(__file__),'../kernel_slope_asymptotics/certify_asymptotics.py':sha(HERE.parent/'kernel_slope_asymptotics/certify_asymptotics.py')},
        dps=110,Q_box=x,dual_coefficient_box=aa,maximum_transition_half_width=a0,minimum_slope_budget=M0,scaled_center_bounds=V,
        tail_kernel_constants=[C0,C1,C2],tail_weight_constants=[W0,W1,W2],tail_moment_derivative_constants=tail_constants,
        tail_start=v0,tail_decay=decay,tail_geometric_envelope=envelope,tail_moment_derivative_sums=tail,tail_residual_second_derivative_sum=tail_r2,
        local_derivative_enclosures=local,center_derivative_enclosures=center_jets,moment_second_derivative_sums=sum_q2,residual_second_derivative_sum=sum_r2,
        center_forcing=forcing,switch_jacobian=[[J[i,j] for j in range(3)] for i in range(3)],
        preconditioner=[[B[i,j] for j in range(3)] for i in range(3)],base_preconditioner_error=[[E[i,j] for j in range(3)] for i in range(3)],
        averaged_jacobian_variation_bounds=derivative_change,preconditioned_derivative_bounds=component_bounds,
        contraction_constants=kappas,selfmap_center_constants=etas,A3=A3,A4=A4,dual_objective_lower=Dlow,
        maximum_dual_loss=Emax,uniform_amplitude_upper=Ubar,upper_absorption_denominator=denom,
        lower_remainder_constant=Kminus,upper_remainder_constant=Kplus,relative_error_upper_at_minimum_budget=relative,
        scope='For every M>=2e-5: C_star/M^2-Kminus/M^3 <= delta(M)-delta_star <= C_star/M^2+Kplus/M^3, using the separate analytic proof and R15 true optimizer. Uniform Lipschitz ramp designs; no exact finite-M optimizer or physical model.',
        trust_boundary='Inherited exact optimizer and moment identities; fresh derivative enclosures and arithmetic constants. Quantitative contraction, tail-envelope proof and remainder inequalities are separate analytic arguments.',elapsed_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(pack(out),indent=2)+'\n')
    print(out['status']);print('forcing',BF);print('contraction',kappas,'center',etas)
    print('B2 sum',sum_r2,'A3',A3,'A4',A4);print('Kminus',Kminus,'Kplus',Kplus,'relative at M0',relative)
if __name__=='__main__':main()
