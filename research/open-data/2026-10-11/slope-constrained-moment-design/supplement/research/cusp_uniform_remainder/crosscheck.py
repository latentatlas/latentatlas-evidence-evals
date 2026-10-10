#!/usr/bin/env python3
"""Direct original-integral cusp/dual solves along the arc; diagnostic only."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mid(x):
    m,e=x['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def bounds(x):
    c=mid(x);r,e=x['rad_man_exp'];r=mp.mpf(r)*mp.power(2,e);return c-r,c+r
def inside(x,y):
    lo,hi=bounds(x);return lo<=y<=hi
def run(cert,old,dps,cusp_order,sign_order):
    mp.mp.dps=dps;h=mp.mpf(1)/65536;Q=list(map(mid,cert['arc']['Q0_box']));vel=list(map(mid,cert['arc']['refined_velocity']))
    baseb=list(map(mid,old['dual_center']));rootseeds=[mid(x['root_interval']) for x in old['finite_roots']]
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
    def moments(x,nu,nmax):
        tau,lam,mu=x;terms=[[] for _ in range(nmax+1)]
        for u,pw in grid:
            w=pw*mp.exp(lam*u*u+mu*u**4+nu*u**6);phase=2*tau*u;trig=[mp.cos(phase),-mp.sin(phase),-mp.cos(phase),mp.sin(phase)]
            power=mp.mpf(1)
            for n in range(nmax+1):terms[n].append(w*power*trig[n%4]);power*=2*u
        return [mp.fsum(t) for t in terms]
    output=[];checks=0
    for numerator in [-4,-3,-2,-1,0]:
        nu=h*numerator/4;x=[Q[j]+nu*vel[j] for j in range(3)];tol=mp.power(10,-dps+25)
        for iteration in range(9):
            d=moments(x,nu,8);J=mp.matrix([[d[i+1],-d[i+2]/4,d[i+4]/16] for i in range(3)])
            step=mp.lu_solve(J,mp.matrix(d[:3]));x=[x[j]-step[j] for j in range(3)]
            if max(map(abs,step))<tol:break
        else:raise ArithmeticError('Direct cusp solve did not settle')
        d=moments(x,nu,8);tau,lam,mu=x
        for j in range(3):assert inside(cert['arc']['parameter_box'][j],x[j]);checks+=1
        def weight(u):return phi(u)*mp.exp(lam*u*u+mu*u**4+nu*u**6)
        def raw(u,b):return p(3,u,tau)-mp.fsum(b[j]*p(j,u,tau) for j in range(3))
        def roots(b):return [mp.findroot(lambda u:raw(u,b),z,solver='newton',tol=tol) for z in rootseeds]
        def signs(b,zz):
            total=[mp.mpf(0)]*4;ends=[mp.mpf(0)]+zz+[mp.mpf(1)]
            for k,(left,right) in enumerate(zip(ends,ends[1:])):
                center=(left+right)/2;half=(right-left)/2;sgn=(-1)**k
                for node,qw in zip(sn,sw):
                    u=center+half*node;fac=sgn*half*qw*weight(u)
                    for j in range(4):total[j]+=fac*p(j,u,tau)
            return total
        def gram(b,zz):
            G=mp.matrix(3)
            for z in zz:
                rp=mp.diff(lambda u:raw(u,b),z);w=weight(z);pv=[p(j,z,tau) for j in range(3)]
                for i in range(3):
                    for j in range(3):G[i,j]+=2*w*pv[i]*pv[j]/abs(rp)
            return G
        b=list(baseb)
        for iteration in range(8):
            zz=roots(b);s=signs(b,zz);G=gram(b,zz);step=mp.lu_solve(G,mp.matrix(s[:3]))
            # d/db of the sign moments is -G.
            b=[b[j]+step[j] for j in range(3)]
            if max(map(abs,step))<tol:break
        else:raise ArithmeticError('Direct dual solve did not settle')
        zz=roots(b);s=signs(b,zz);G=gram(b,zz);Gamma=mp.mpf(0);B=mp.matrix(3,1);R=mp.mpf(0);jetrecords=[]
        for k,z in enumerate(zz):
            fun=lambda u:weight(u)*raw(u,b)
            r,t,third=[mp.diff(fun,z,l) for l in [1,2,3]];sigma=mp.sign(r);gamma=abs(r);Gamma+=gamma
            q=[weight(z)*p(j,z,tau) for j in range(3)]
            qp=[mp.diff(lambda u:weight(u)*p(j,u,tau),z) for j in range(3)]
            for j in range(3):B[j]+=sigma*(q[j]*t/r-qp[j])/3
            R+=t*t/(36*gamma)-sigma*third/60
            assert inside(cert['dual']['tight_roots'][k]['root'],z);checks+=1
            if k in [0,1,27]:
                qjets=[[mp.diff(lambda u:weight(u)*p(j,u,tau),z,l) for l in range(6)] for j in range(4)]
                for j in range(4):
                    for l in range(6):assert inside(cert['remainder']['local'][k]['root_jets']['moment_jets'][j][l],qjets[j][l]);checks+=1
                jetrecords.append({'index':k,'moment_jets':[[mp.nstr(v,dps-15) for v in rr] for rr in qjets]})
        v=mp.lu_solve(G,B);P=(B.T*v)[0]/2;Xi=R-P;D=s[3]-mp.fsum(b[j]*s[j] for j in range(3));f=d[3];delta=f/D
        co={'f':f,'D':D,'delta0':delta,'Gamma':Gamma,'R':R,'P':P,'Xi':Xi,'C2':delta**3*Gamma/(3*D),
            'C4':delta**5*(Gamma**2/(3*D*D)-Xi/D)}
        for key,value in co.items():assert inside(cert['coefficients'][key],value);checks+=1
        for j in range(3):assert inside(cert['dual']['tight_box'][j],b[j]) and inside(cert['coefficients']['v'][j],v[j]);checks+=2
        output.append({'nu':mp.nstr(nu,40),'cusp':[mp.nstr(a,dps-15) for a in x],'cusp_residuals':[mp.nstr(a,dps-15) for a in d[:3]],
          'b':[mp.nstr(a,dps-15) for a in b],'v':[mp.nstr(v[j],dps-15) for j in range(3)],
          'sign_moment_residuals':[mp.nstr(a,dps-15) for a in s[:3]],'roots':[mp.nstr(z,dps-15) for z in zz],
          'coefficients':{k:mp.nstr(a,dps-15) for k,a in co.items()},'checked_root_jets':jetrecords})
        print('direct cusp/dual',dps,nu,'C4',mp.nstr(co['C4'],18),flush=True)
    return {'dps':dps,'cusp_gauss_order_per_quarter':cusp_order,'sign_gauss_order_per_cell':sign_order,
      'theta_terms':12,'integration_cutoff':'1','enclosure_checks':checks,'rows':output}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    cp=HERE/'results/certificate.json';op=HERE.parent/'theta_fourth_order/results/certificate.json'
    cert=json.loads(cp.read_text());old=json.loads(op.read_text());runs=[]
    for spec in [(90,64,32),(130,96,48)]:runs.append(run(cert,old,*spec))
    mp.mp.dps=130;diff=[]
    for lo,hi in zip(runs[0]['rows'],runs[1]['rows']):
        l=lo['cusp']+lo['b']+lo['v']+list(lo['coefficients'].values());h=hi['cusp']+hi['b']+hi['v']+list(hi['coefficients'].values())
        for x,y in zip(l,h):
            x,y=mp.mpf(x),mp.mpf(y);err=abs(x-y)/max(abs(y),mp.mpf('1e-100'));assert err<mp.mpf('1e-40');diff.append(err)
    data={'status':'R27_independent_direct_arc_checks_passed','runs':runs,'precision_comparisons':len(diff),
       'maximum_relative_precision_difference':mp.nstr(max(diff),40),'certificate_sha256':sha(cp),'source_sha256':sha(__file__),
       'R24_certificate_sha256':sha(op),'trust_boundary':'Diagnostic: solves original truncated-integral cusp and dual equations with mpmath at five drivers. Twelve theta terms, finite cutoff and central inputs; no rigorous enclosure or continuum claim comes from these samples.'}
    args.output.write_text(json.dumps(data,indent=2)+'\n');print(data['status'],data['maximum_relative_precision_difference'])
if __name__=='__main__':main()
