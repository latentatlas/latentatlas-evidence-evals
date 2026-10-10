#!/usr/bin/env python3
"""Re-solve original integrals at nearby cusps; finite differences, diagnostic."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(x):
    m,e=x['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def ends(x):
    m=mid(x);r,e=x['rad_man_exp'];r=mp.mpf(r)*mp.power(2,e);return m-r,m+r
def inside(x,y):
    a,b=ends(x);return a<=y<=b
def run(cert,previous,moment9,dps,cusp_order,sign_order):
    mp.mp.dps=dps;h=mp.mpf(1)/65536;tol=mp.power(10,-dps+20)
    oldrows=previous['runs'][1]['rows'];rootseeds=list(map(mp.mpf,oldrows[-1]['roots']))
    def phi(u):
        e4=mp.exp(4*u)
        return mp.pi*mp.exp(5*u)*mp.fsum(n*n*(2*mp.pi*n*n*e4-3)*mp.exp(-mp.pi*n*n*e4) for n in range(1,13))
    def p(j,u,tau):return (2*u)**j*mp.cos(2*tau*u+j*mp.pi/2)
    nodes,weights=mp.gauss_quadrature(cusp_order,'legendre');grid=[]
    for k in range(4):
        center=(mp.mpf(k)+mp.mpf('.5'))/4
        for x,w in zip(nodes,weights):
            u=center+x/8;grid.append((u,w*phi(u)/8))
    sn,sw=mp.gauss_quadrature(sign_order,'legendre')
    def moments(x,nu):
        tau,lam,mu=x;acc=[[] for _ in range(9)]
        for u,pw in grid:
            w=pw*mp.exp(lam*u*u+mu*u**4+nu*u**6);angle=2*tau*u
            trig=[mp.cos(angle),-mp.sin(angle),-mp.cos(angle),mp.sin(angle)];power=mp.mpf(1)
            for n in range(9):acc[n].append(w*power*trig[n%4]);power*=2*u
        return [mp.fsum(a) for a in acc]
    cache={};evaluations=[]
    def evaluate(nu):
        key=mp.nstr(nu,60)
        if key in cache:return cache[key]
        source=min(oldrows,key=lambda row:abs(mp.mpf(row['nu'])-nu));x=list(map(mp.mpf,source['cusp']));b=list(map(mp.mpf,source['b']))
        for _ in range(10):
            d=moments(x,nu);J=mp.matrix([[d[i+1],-d[i+2]/4,d[i+4]/16] for i in range(3)])
            step=mp.lu_solve(J,mp.matrix(d[:3]));x=[x[j]-step[j] for j in range(3)]
            if max(map(abs,step))<tol:break
        else:raise ArithmeticError('cusp Newton failed')
        d=moments(x,nu);tau,lam,mu=x
        def weight(u):return phi(u)*mp.exp(lam*u*u+mu*u**4+nu*u**6)
        def raw(u,b):return p(3,u,tau)-mp.fsum(b[j]*p(j,u,tau) for j in range(3))
        def roots(b):return [mp.findroot(lambda u:raw(u,b),z,solver='newton',tol=tol) for z in rootseeds]
        def signs(zz):
            S=[mp.mpf(0)]*4;cuts=[mp.mpf(0)]+zz+[mp.mpf(1)]
            for k,(a,z) in enumerate(zip(cuts,cuts[1:])):
                center=(a+z)/2;half=(z-a)/2
                for node,qw in zip(sn,sw):
                    u=center+half*node;fac=(-1)**k*half*qw*weight(u)
                    for j in range(4):S[j]+=fac*p(j,u,tau)
            return S
        def gram(b,zz):
            G=mp.matrix(3)
            for z in zz:
                fac=2*weight(z)/abs(mp.diff(lambda u:raw(u,b),z));pv=[p(j,z,tau) for j in range(3)]
                for i in range(3):
                    for j in range(3):G[i,j]+=fac*pv[i]*pv[j]
            return G
        for _ in range(9):
            zz=roots(b);S=signs(zz);G=gram(b,zz);step=mp.lu_solve(G,mp.matrix(S[:3]));b=[b[j]+step[j] for j in range(3)]
            if max(map(abs,step))<tol:break
        else:raise ArithmeticError('dual Newton failed')
        zz=roots(b);S=signs(zz);G=gram(b,zz);Gamma=mp.mpf(0);B=mp.matrix(3,1);R=mp.mpf(0)
        for z in zz:
            density=lambda u:weight(u)*raw(u,b)
            r,t,s=[mp.diff(density,z,k) for k in [1,2,3]];sgn=mp.sign(r);gam=abs(r);Gamma+=gam
            for j in range(3):
                q=weight(z)*p(j,z,tau);qp=mp.diff(lambda u:weight(u)*p(j,u,tau),z)
                B[j]+=sgn*(q*t/r-qp)/3
            R+=t*t/(36*gam)-sgn*s/60
        v=mp.lu_solve(G,B);P=(B.T*v)[0]/2;Xi=R-P;D=S[3]-mp.fsum(b[j]*S[j] for j in range(3));f=d[3];delta=f/D
        co={'f':f,'D':D,'delta0':delta,'Gamma':Gamma,'R':R,'P':P,'Xi':Xi,
            'C2':delta**3*Gamma/(3*D),'C4':delta**5*(Gamma**2/(3*D*D)-Xi/D)}
        cache[key]={'coefficients':co,'b':b}
        evaluations.append({'nu':key,'cusp':[mp.nstr(y,dps-10) for y in x],
          'b':[mp.nstr(y,dps-10) for y in b],'coefficients':{k:mp.nstr(y,dps-10) for k,y in co.items()},
          'maximum_cusp_residual':mp.nstr(max(map(abs,d[:3])),dps-10),
          'maximum_sign_residual':mp.nstr(max(map(abs,S[:3])),dps-10)})
        print('integral solve',dps,key,mp.nstr(co['C4'],15),flush=True)
        return cache[key]
    rows=[];checks=0
    for numerator in [-2,-1,0]:
        nu=h*numerator/2;center=evaluate(nu);steps=[]
        for denom in [16,32]:
            e=h/denom
            if numerator==-2:offsets=[0,e,2*e];weights0=[-3,4,-1];mode='forward_second_order'
            elif numerator==0:offsets=[0,-e,-2*e];weights0=[3,-4,1];mode='backward_second_order'
            else:offsets=[-e,e];weights0=[-1,1];mode='central_second_order'
            vals=[evaluate(nu+offset) for offset in offsets];derivatives={}
            for key in center['coefficients']:
                value=mp.fsum(w*val['coefficients'][key] for w,val in zip(weights0,vals))/(2*e)
                assert inside(cert['derivatives'][key],value),(key,nu,value);checks+=1;derivatives[key]=mp.nstr(value,dps-12)
            bd=[mp.fsum(w*val['b'][j] for w,val in zip(weights0,vals))/(2*e) for j in range(3)]
            for j in range(3):assert inside(cert['b_prime'][j],bd[j]);checks+=1
            steps.append({'step':mp.nstr(e,60),'stencil':mode,'derivatives':derivatives,'b_derivative':[mp.nstr(y,dps-12) for y in bd]})
        change=abs(mp.mpf(steps[0]['derivatives']['C4'])-mp.mpf(steps[1]['derivatives']['C4']))/abs(mp.mpf(steps[1]['derivatives']['C4']))
        assert change<mp.mpf('1e-9')
        rows.append({'nu':mp.nstr(nu,60),'steps':steps,'relative_C4_step_change':mp.nstr(change,40)})
    # New ninth moment is checked using the original fixed sign template.
    R12=json.loads((HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json').read_text())
    Q=json.loads((HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json').read_text())
    tau,lam,mu=map(mid,Q['center_exact_dyadic']);cuts=[mp.mpf(0)]+list(map(mid,R12['breakpoints']))+[mp.mpf(1)];m9=mp.mpf(0)
    for k,(a,b) in enumerate(zip(cuts,cuts[1:])):
        center=(a+b)/2;half=(b-a)/2
        for node,w in zip(sn,sw):
            u=center+half*node;m9+=(-1)**k*half*w*phi(u)*mp.exp(lam*u*u+mu*u**4)*p(9,u,tau)
    assert inside(moment9['moment_at_exact_Q'],m9);checks+=1
    return {'dps':dps,'cusp_gauss_order_per_quarter':cusp_order,'sign_gauss_order_per_cell':sign_order,
      'theta_terms':12,'cutoff':1,'evaluations':evaluations,'rows':rows,'comparison_count':checks,
      'ninth_template_moment':mp.nstr(m9,dps-12)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    paths={'certificate':HERE/'results/certificate.json','previous_direct':HERE.parent/'cusp_uniform_remainder/results/direct_check.json','moment9':HERE/'results/sign_moment9.json'}
    c,old,m=[json.loads(paths[k].read_text()) for k in ['certificate','previous_direct','moment9']]
    runs=[run(c,old,m,*spec) for spec in [(80,64,32),(110,80,40)]];mp.mp.dps=110;diff=[]
    for lo,hi in zip(runs[0]['rows'],runs[1]['rows']):
        for l,h in zip(lo['steps'],hi['steps']):
            lv=list(l['derivatives'].values())+l['b_derivative'];hv=list(h['derivatives'].values())+h['b_derivative']
            for x,y in zip(lv,hv):
                x,y=mp.mpf(x),mp.mpf(y);err=abs(x-y)/max(abs(y),mp.mpf('1e-100'));assert err<mp.mpf('1e-35');diff.append(err)
    data={'status':'R28_independent_integral_finite_difference_checks_passed','runs':runs,'precision_comparisons':len(diff),
      'maximum_relative_precision_difference':mp.nstr(max(diff),40),'source_sha256':sha(__file__),
      'input_sha256':{k:sha(p) for k,p in paths.items()},
      'trust_boundary':'Diagnostic only. Re-solves cusp and optimal sign moments from truncated original integrals, then differences the fourth coefficient without the analytic derivative formula. Two step sizes and precisions do not constitute an interval derivative proof.'}
    args.output.write_text(json.dumps(data,indent=2)+'\n');print(data['status'],data['maximum_relative_precision_difference'])
if __name__=='__main__':main()
