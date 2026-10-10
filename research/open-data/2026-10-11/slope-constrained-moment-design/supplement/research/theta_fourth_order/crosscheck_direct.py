#!/usr/bin/env python3
"""Independent mpmath roots, direct differentiation and quadrature at central inputs."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def midpoint(r):
    m,e=r['mid_man_exp'];return mp.mpf(m)*mp.power(2,e)
def radius(r):
    m,e=r['rad_man_exp'];return mp.mpf(m)*mp.power(2,e)
def inside(r,x):return abs(x-midpoint(r))<=radius(r)
def solve(cert,dps,order):
    mp.mp.dps=dps;tau,lam,mu=map(midpoint,cert['Q_box']);b=list(map(midpoint,cert['dual_center']))
    def p(j,x):return (2*x)**j*mp.cos(2*tau*x+j*mp.pi/2)
    def raw(x):return p(3,x)-mp.fsum(b[j]*p(j,x) for j in range(3))
    def weight(x):
        e4=mp.exp(4*x)
        return mp.pi*mp.exp(5*x+lam*x*x+mu*x**4)*mp.fsum(n*n*(2*mp.pi*n*n*e4-3)*mp.exp(-mp.pi*n*n*e4) for n in range(1,13))
    def density(x):return weight(x)*raw(x)
    rows=[];G=mp.matrix(3);B=mp.matrix(3,1);Gamma=mp.mpf(0);RR=mp.mpf(0)
    for cr in cert['finite_roots']:
        root=mp.findroot(raw,midpoint(cr['root_interval']),solver='newton',tol=mp.power(10,-dps+15))
        assert inside(cr['root_interval'],root)
        qjet=[mp.diff(density,root,l) for l in [1,2,3]]
        q=[weight(root)*p(j,root) for j in range(3)]
        qp=[mp.diff(lambda x:weight(x)*p(j,x),root) for j in range(3)]
        gamma=abs(qjet[0]);sigma=mp.sign(qjet[0]);gr=[[2*q[i]*q[j]/gamma for j in range(3)] for i in range(3)]
        br=[sigma*(q[j]*qjet[1]/qjet[0]-qp[j])/3 for j in range(3)]
        rr=qjet[1]**2/(36*gamma)-sigma*qjet[2]/60
        for rec,x in zip(cr['density_root_jets'],qjet):assert inside(rec,x),('root jet',cr['index'])
        for i in range(3):
            assert inside(cr['B'][i],br[i]);B[i]+=br[i]
            for j in range(3):assert inside(cr['G'][i][j],gr[i][j]);G[i,j]+=gr[i][j]
        assert inside(cr['Gamma'],gamma) and inside(cr['R'],rr)
        Gamma+=gamma;RR+=rr
        rows.append({'root':mp.nstr(root,dps-8),'q_root_jets':[mp.nstr(v,dps-8) for v in qjet],
                     'Gamma':mp.nstr(gamma,dps-8),'R':mp.nstr(rr,dps-8),
                     'G':[[mp.nstr(v,dps-8) for v in row] for row in gr],'B':[mp.nstr(v,dps-8) for v in br]})
    v=mp.lu_solve(G,B);PP=(B.T*v)[0]/2;Xi=RR-PP
    nodes,weights=mp.gauss_quadrature(order,'legendre');D=mp.mpf(0);f=mp.mpf(0)
    bounds=[mp.mpf(0)]+[mp.mpf(row['root']) for row in rows]+[mp.mpf(1)]
    for k,(left,right) in enumerate(zip(bounds[:-1],bounds[1:])):
        half=(right-left)/2;center=(left+right)/2
        for node,gw in zip(nodes,weights):
            u=center+half*node;wu=weight(u);factor=half*gw*wu
            D+=(-1)**k*factor*raw(u);f+=factor*p(3,u)
    delta=f/D;C2=delta**3*Gamma/(3*D);C4=delta**5*(Gamma**2/(3*D**2)-Xi/D)
    data={'f':f,'delta0':delta,'D':D,'Gamma':Gamma,'R':RR,'P':PP,'Xi':Xi,'C2':C2,'C4':C4,
          'C4_amplitude_part':delta**5*Gamma**2/(3*D**2),'C4_shape_part':-delta**5*RR/D,
          'C4_moment_part':delta**5*PP/D,'C4_over_C2':C4/C2}
    # f at the central Q is not required to fit the much tighter exact-Q f interval.
    # All final coefficients except f are compared with the new true-optimizer enclosures.
    for key,x in data.items():
        if key!='f':assert inside(cert['coefficients'][key],x),(key,mp.nstr(x,40),cert['coefficients'][key]['enclosure'])
    for j in range(3):assert inside(cert['linear_solve']['v_enclosure'][j],v[j])
    for i in range(3):
        assert inside(cert['infinite_sums']['B'][i],B[i])
        for j in range(3):assert inside(cert['infinite_sums']['G'][i][j],G[i,j])
    return {'dps':dps,'quadrature_order':order,'theta_terms':12,'cutoff':1,'root_count':28,
            'rows':rows,'values':{k:mp.nstr(x,dps-8) for k,x in data.items()},
            'G':[[mp.nstr(G[i,j],dps-8) for j in range(3)] for i in range(3)],
            'B':[mp.nstr(B[i],dps-8) for i in range(3)],'v':[mp.nstr(v[i],dps-8) for i in range(3)]}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    cert=json.loads(args.certificate.read_text());runs=[]
    for dps,n in [(80,72),(120,96)]:
        runs.append(solve(cert,dps,n));print('Independent direct check passed',dps,n,flush=True)
    diffs={}
    for key,value in runs[1]['values'].items():
        value=mp.mpf(value);difference=abs(value-mp.mpf(runs[0]['values'][key]))/max(abs(value),mp.mpf('1e-100'))
        assert difference<mp.mpf('1e-55'),(key,difference)
        diffs[key]=mp.nstr(difference,35)
    out={'status':'R24_direct_differentiation_and_quadrature_agree','runs':runs,'relative_precision_differences':diffs,
        'source_sha256':sha(__file__),'certificate_sha256':sha(args.certificate),
        'per_run_root_values_compared':28*18,'per_run_final_values_compared':12,
        'trust_boundary':'Nonrigorous check at central Q and b0 using the original density, numerical differentiation and Gauss quadrature. Twelve theta terms and [0,1] are used here; parameter uncertainty, exact b*, omitted terms and the infinite root tail are handled by the separate certificate.'}
    args.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
