#!/usr/bin/env python3
"""Audit R12 inputs with separate formulas and rescaled smooth-transition integrals.

Checks the EXISTING bounds/design only; no revised optimum is promoted.
No existing generating/checking module is imported. Arb remains shared trusted
interval arithmetic. The global smoothing-tail proof is recorded in the audit.
"""
import sys
sys.dont_write_bytecode=True
import hashlib,json,time
from pathlib import Path
from flint import arb,acb,arb_mat,ctx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
ctx.dps=140
start=time.monotonic()
def read(p):return json.loads((ROOT/p).read_text())
def restore(v):
 m,e=v['mid_man_exp'];r,f=v['rad_man_exp']
 return arb(m)*arb(2)**e+arb(0,arb(r)*arb(2)**f)
def sym(r):return arb(0,arb(r).upper())
def hi(v):return arb(v).upper()
def hull(a,b):return a.union(b)
def power(x,n):
 out=type(x)(1)
 for _ in range(n):out*=x
 return out
def record(v):
 return {'mid_man_exp':list(map(int,v.mid().man_exp())),
         'rad_man_exp':list(map(int,v.rad().man_exp())), 'enclosure':v.str(22)}

c=read('kernel_norm_threshold/results/threshold_certificate.json')
q=read('cusp_verified/results/quartic_cusp_certificate.json')
old=read('kernel_design_principle/results/candidate_certificate.json')
jets=read('cusp_shape_design/results/local_jets.json')
x=list(map(restore,q['center_exact_dyadic']));radius=restore(q['root_radius'])
t,lam,mu=[v+sym(radius) for v in x]
Bs=list(map(restore,q['absolute_derivative_bounds']))
a=list(map(restore,c['a']));knots=list(map(restore,c['breakpoints']))
eta=restore(c['smoothing_width']);alpha=restore(c['alpha'])
M=list(map(restore,c['lipschitz_bounds']))
E=list(map(restore,c['smooth_moment_errors']))
pi=arb.pi();C0=4*pi*pi+6*pi;C1=60*pi*pi+30*pi+16*pi**3
assert 64*(-3*pi).exp()<arb(1)/2

def phase_basis(u,n,tau=t):
 z=2*tau*u
 return power(2*u,n)*(z.cos(),-z.sin(),-z.cos(),z.sin())[n%4]

def phase_basis_u(u,n):
 z=2*t*u
 tr=(z.cos(),-z.sin(),-z.cos(),z.sin())
 out=2*t*power(2*u,n)*tr[(n+1)%4]
 if n:out+=2*n*power(2*u,n-1)*tr[n%4]
 return out

def residual(u):return phase_basis(u,3)-sum((a[j]*phase_basis(u,j) for j in range(3)),arb(0))
def slope(u):return phase_basis_u(u,3)-sum((a[j]*phase_basis_u(u,j) for j in range(3)),arb(0))
sign_subdivisions=0
def prove_sign(l,r,s,depth=0):
 global sign_subdivisions
 z=hull(l,r)
 if s*residual(z)>0:return
 if not slope(z).contains(0) and s*residual(l)>0 and s*residual(r)>0:return
 assert depth<30,'Independently expressed residual sign unresolved'
 mid=(l+r)/2;sign_subdivisions+=1
 prove_sign(l,mid,s,depth+1);prove_sign(mid,r,s,depth+1)
for box in c['root_boxes']:
 l,r=restore(box['left']),restore(box['right']);s=box['sign_before']
 assert s*residual(l)>0 and s*residual(r)<0 and not slope(hull(l,r)).contains(0)
for row in c['sign_cover']:prove_sign(restore(row['left']),restore(row['right']),row['sign'])

# Recompute the positive cell envelopes using a single exponential factor;
# old code factors exp(P-pi*exp(4l)) and exp(9r) / exp(13r) separately.
for k in range(256):
 l,r=arb(k)/128,arb(k+1)/128
 # Multiply by an exact monomial once. Repeated multiplication of a ball by
 # r widens its 30-bit radius at each operation and can exceed an old, valid
 # upper envelope by ~1e-97 without contradicting that bound.
 pu=max(hi(lam*l**2),hi(lam*r**2))+max(hi(mu*l**4),hi(mu*r**4))
 rho=C0*(9*r+pu-pi*(4*l).exp()).exp()
 drho=C1*(13*r+pu-pi*(4*l).exp()).exp()+rho*(2*hi(abs(lam))*r+4*hi(abs(mu))*r**3)
 for n in range(9):
  envelope=(drho+2*hi(abs(t))*rho)*(2*r)**n
  if n:envelope+=2*n*rho*(2*r)**(n-1)
  assert envelope<=M[n],('Global Lipschitz budget not reproduced',k,n)
U=arb(2)
Pplus=max(arb(0),hi(lam))*U*U+max(arb(0),hi(mu))*U**4
Pprime=2*max(arb(0),hi(lam))*U+4*max(arb(0),hi(mu))*U**3
margin=4*pi*(4*U).exp()-13-arb(11)/U-Pprime
assert margin>0 and U>=arb(3)/4
rhoU=C0*(9*U+Pplus-pi*(4*U).exp()).exp()
drhoU=C1*(13*U+Pplus-pi*(4*U).exp()).exp()+rhoU*(2*hi(abs(lam))*U+4*hi(abs(mu))*U**3)
for n in range(9):
 envelope=(drhoU+2*hi(abs(t))*rhoU)*(2*U)**n
 if n:envelope+=2*n*rhoU*(2*U)**(n-1)
 assert envelope<=M[n]
print('Fresh residual signs and 2304 Lipschitz envelopes passed',flush=True)

N=12
def density(z,parameters):
 la,mm=parameters
 # Independent term arrangement: pi*k^2*exp(5u)*(2*pi*k^2*exp(4u)-3).
 pc=acb.pi();e4=(4*z).exp();e5=(5*z).exp()
 phi=sum((pc*k*k*e5*(2*pc*k*k*e4-3)*(-pc*k*k*e4).exp() for k in range(1,N+1)),acb(0))
 return phi*(acb(la)*z*z+acb(mm)*z**4).exp()

def moment_integrand(z,n,parameters,tau):
 return density(z,parameters)*phase_basis(z,n,acb(tau))

def integrate(fun,l,r,tol='1e-83'):
 def callback(z,analytic):
  v=fun(z)
  return v if v.is_finite() else acb('nan','nan')
 v=acb.integral(callback,acb(l),acb(r),abs_tol=arb(tol),rel_tol=arb(tol),eval_limit=100000)
 assert v.is_finite()
 return v.real

# Independently arranged truncation envelopes for the 12-term positive sum.
def series_error(n,cut,parameters):
 la,mm=parameters;k=N+1
 p=max(arb(0),hi(la))*cut**2+max(arb(0),hi(mm))*cut**4
 return hi(2*cut*(2*pi*pi*(9*cut).exp()+3*pi*(5*cut).exp())*k**4*
           (-pi*k*k+p).exp()*(2*cut)**n)
def tail_error(n,cut,parameters):
 la,mm=parameters;l=max(arb(0),hi(la));m=max(arb(0),hi(mm))
 slope_margin=4*pi*(4*cut).exp()-9-arb(n)/cut-2*l*cut-4*m*cut**3
 assert slope_margin>0 and cut>=arb(3)/4
 return hi(C0*(2*cut)**n*(9*cut+l*cut*cut+m*cut**4-pi*(4*cut).exp()).exp()/slope_margin)

ends=[arb(0)]+knots+[arb(1),arb(5)/4,arb(3)/2,arb(7)/4,arb(2)]
newS=[]
for n in range(9):
 v=arb(0)
 for j,(l,r) in enumerate(zip(ends[:-1],ends[1:])):
  sign=(-1)**j if j<28 else 1
  v+=sign*integrate(lambda z:moment_integrand(z,n,x[1:],x[0]),l,r)
 error=series_error(n,arb(2),x[1:])+tail_error(n,arb(2),x[1:])
 error+=radius*(Bs[n+1]+Bs[n+2]/4+Bs[n+4]/16)
 v+=sym(error)
 previous=restore(c['step_moments_at_exact_Q'][n])
 assert previous.contains(v),('Fresh entire step moment not inside old bound',n)
 newS.append(v)
 print('Fresh step moment',n,'contained in previous certificate',flush=True)

# Integrate the smoothing correction after u=b+eta*v. Pair v and -v to
# keep the cancellation. There is no tiny mesh in u and no unresolved spike.
# For each positive knot, its mirror contributes the same half-line value.
# The omitted |v|>V correction is <= Nknots*M*eta^2*(2V+1)*exp(-2V).
Vcut=arb(40);vends=list(map(arb,[0,1,2,4,8,16,32,40]));deltas=[]
for n in range(9):
 correction=arb(0)
 for k,b in enumerate(knots):
  jump=-2*(-1)**k
  def scaled(z):
   difference=moment_integrand(acb(b)+acb(eta)*z,n,[lam,mu],t)-moment_integrand(acb(b)-acb(eta)*z,n,[lam,mu],t)
   return -acb(jump)*acb(eta)*difference/(1+(2*z).exp())
  for l,r in zip(vends[:-1],vends[1:]):correction+=integrate(scaled,l,r,'1e-73')
 # For the finite theta truncation use its uniform pointwise error on [0,1].
 # Each jump contributes at most 2*eta*pointwise_error; sum all 28 jumps.
 trunc=2*len(knots)*eta*series_error(n,arb(1),[lam,mu])
 tail=len(knots)*M[n]*eta*eta*(2*Vcut+1)*(-2*Vcut).exp()
 correction+=sym(trunc+tail)
 assert abs(correction)<E[n],('Smooth moment error exceeds original budget',n)
 assert restore(c['smooth_moments_at_exact_Q'][n]).contains(newS[n]+correction)
 deltas.append(correction)
 print('Rescaled smooth correction',n,'inside previous error budget',flush=True)

f=list(map(restore,jets['F_at_exact_Q'][:9]));f[:3]=[arb(0)]*3
A=arb_mat([[restore(v) for v in row] for row in old['design_matrix']])
smooth=[s+d for s,d in zip(newS,deltas)]
rhs=[alpha*smooth[n]-(f[3] if n==3 else 0) for n in range(4)]
wmat=A.solve(arb_mat([[v] for v in rhs]));w=[wmat[j,0] for j in range(4)]
assert all(restore(v).contains(z) for v,z in zip(c['correction_weights'],w))
cost=alpha+sum(map(abs,w),arb(0))
assert cost<restore(c['feasible_norm_upper_enclosure'])
g=[f[n]-alpha*smooth[n]+sum((restore(row['moments'][n])*w[j] for j,row in enumerate(old['dictionary'])),arb(0)) for n in range(9)]
assert all(v.contains(0) for v in g[:4])
assert g[4]<0 and g[4]*(g[4]*g[7]-g[5]*g[6])/4096<0
out={'status':'fresh_R12_sign_envelope_integral_and_smooth_design_audit_passed',
 'residual_root_boxes':28,'old_sign_leaves_rechecked':113,'additional_sign_bisections':sign_subdivisions,
 'Lipschitz_cell_envelopes':256*9,'Lipschitz_tail_envelopes':9,
 'step_integrals':(len(ends)-1)*9,'step_orders':list(range(9)),
 'rescaled_transition_integrals':28*7*9,'smooth_orders':list(range(9)),
 'step_moments_contained_in_old_enclosures':True,'smooth_errors_inside_old_budgets':True,
 'correction_weights_contained_in_old_enclosures':True,'original_cost_upper_bound_verified':True,
 'original_order_four_and_rank_three_verified':True,
 'dps':140,'theta_terms':12,'step_cutoff':2,'rescaled_transition_cutoff':40,
 'smoothing_corrections':[record(v) for v in deltas],
 'method':'Independent integrand arrangement and higher precision; full step moments include [1,2]. Smooth differences integrated in v=(u-b)/eta, paired around each knot, with logistic-tail and theta-tail bounds. Does not import old research computation modules.',
 'trust_boundary':'Still uses Arb as rigorous integration/arithmetic backend, old exact Q, old absolute derivative majorants for negligible Q transfer, and R11 correction-matrix inputs. These were separately replayed. No external review or formal verification.',
 'scope':'Verifies old certificate budgets; no improved theorem, interval or new kernel is promoted.',
 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'elapsed_seconds':time.monotonic()-start}
(HERE/'threshold_input_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],flush=True)
