#!/usr/bin/env python3
"""Independent rational verification downstream of saved Taylor enclosures.

No FLINT or R08 generating module is imported. The analytic integral and
correlated two-variable polynomial enclosures remain input assumptions.
We independently expand the transport polynomials, verify their reduction
to the nu identities, rebuild geometry and both fold ODE jets, and check
all contraction and branch-containment inequalities with rational endpoints.
"""
import argparse, hashlib, json, sys, time
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode = True
if not __debug__: raise RuntimeError('Do not disable assertions')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'cusp_robustness'))
from check_robustness import (D, read, exact, powi, mul, grad, sym,
                              check_geometry, determinant, away0, TERMS3, TERMS4)
from check_width import divide, fifth_from_ode


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def endpoints(v):
    a,e=v['mid_man_exp'];r,f=v['rad_man_exp']
    m=Q(a)*Q(2)**e;b=Q(r)*Q(2)**f
    assert r>=0
    return m-b,m+b
def ab(v): return max(map(abs,endpoints(v)))


class P:
    """Small exact sparse multivariate polynomial, used only for algebra."""
    def __init__(self, terms, dim):
        self.t={k:Q(v) for k,v in terms.items() if v};self.dim=dim
    def of(self,x): return x if isinstance(x,P) else P({(0,)*self.dim:x},self.dim)
    def __add__(self,x):
        x=self.of(x);t=dict(self.t)
        for k,v in x.t.items():t[k]=t.get(k,Q(0))+v
        return P(t,self.dim)
    __radd__=__add__
    def __neg__(self):return P({k:-v for k,v in self.t.items()},self.dim)
    def __sub__(self,x):return self+-self.of(x)
    def __rsub__(self,x):return self.of(x)+-self
    def __mul__(self,x):
        x=self.of(x);t={}
        for k,v in self.t.items():
            for l,w in x.t.items():
                e=tuple(a+b for a,b in zip(k,l));t[e]=t.get(e,Q(0))+v*w
        return P(t,self.dim)
    __rmul__=__mul__
    def __truediv__(self,x):return self*Q(1,x)
    def __pow__(self,n):
        p=self.of(1)
        for _ in range(n):p=p*self
        return p
    def evaluate(self,x):
        s=0
        for e,c in self.t.items():
            v=c
            for a,n in zip(x,e):v=v*a**n
            s=s+v
        return s


def symbols(n):return [P({tuple(int(i==j) for i in range(n)):1},n) for j in range(n)]


def algebra():
    # Obtain derivatives of k=-a/b and A3=4/3(c/b-b/a) by
    # the quotient rule, after clearing the common a^2 b denominator
    # in the cusp tangent. This is separate from the generator's AD.
    x=symbols(13);a,b,c,d,e,f,g=x[:7];r0,r1,r2,r3,r4,r5=x[7:]
    U=b*r1-c*r0;V=-a*b*r2+b*b*r1+(a*d-b*c)*r0
    pa=a*a*b*r3+b*V-a*c*U-a*a*e*r0
    pb=a*a*b*r4+c*V-a*d*U-a*a*f*r0
    pc=a*a*b*r5+d*V-a*e*U-a*a*g*r0
    N=a*pb-b*pa
    N4=a*a*(b*pc-c*pb)-b*b*(a*pb-b*pa)
    y=symbols(9)
    substituted=y[:7]+[-y[n+3]/64 for n in range(6)]
    expected3=P({tuple(e)+(0,):c for e,c in TERMS3},9)
    expected4=P(dict(TERMS4),9)
    assert (64*N.evaluate(substituted)-expected3).t=={}
    assert (64*N4.evaluate(substituted)-expected4).t=={}
    return list(N.t.items()),list(N4.t.items())


def joint_ode(g,k,lp):
    """Differentiate G_n and K_n along the fold ODE, through order 5."""
    gj=[[v]+[D(0)]*5 for v in g];kj=[[v]+[D(0)]*5 for v in k]
    for q in range(1,6):
        w,d3,d4,d5=[v[:q] for v in (gj[2],gj[3],gj[4],gj[5])]
        delta=[a-b for a,b in zip(mul(d3,d4,q-1),mul(w,d5,q-1))]
        lprime=divide([4*v for v in mul(w,d4,q-1)],delta,q-1)
        mprime=divide([16*v for v in mul(w,w,q-1)],delta,q-1)
        for js in (gj,kj):
            for n in range(27-4*q):
                js[n][q]=(js[n+1][q-1]-mul(lprime,js[n+2][:q],q-1)[q-1]/4
                           +mul(mprime,js[n+4][:q],q-1)[q-1]/16)/q
    b=divide([4*lp*u-16*v for u,v in zip(gj[2],kj[0])],gj[4],5)
    return 120*b[5].abs_upper()


def shape(row,driver,fourth,terms):
    source=row['fourth' if fourth else 'opening'][driver]
    scale=exact(source['scale']);assert scale>0
    cp=list(map(read,row['cusp_derivatives']));kp=list(map(read,row['K_cusp_derivatives']))
    variables=([('g',n) for n in range(3,12 if fourth else 11)] if driver=='nu'
               else [('g',n) for n in range(3,10)]+[('k',n) for n in range(6)])
    ds=[(cp if kind=='g' else kp)[n]/scale for kind,n in variables]
    errors=list(map(exact,source['jet_remainders']))
    gradient=grad(terms,[d+sym(e) for d,e in zip(ds,errors)])
    jeterror=sum(a.abs_upper()*e for a,e in zip(gradient,errors))
    gradient=grad(terms,ds)
    spatial=[sum((g*(cp if kind=='g' else kp)[n+s]*f/scale
                  for g,(kind,n) in zip(gradient,variables)),D(0))
             for s,f in ((1,Q(1)),(2,-Q(1,4)),(4,Q(1,16)))]
    rooterror=sum(v.abs_upper()*exact(r) for v,r in zip(spatial,row['contraction']['tight']))
    N=read(source['polynomial_bound'])+sym(jeterror+rooterror)
    a,b=cp[3]/scale,cp[4]/scale
    if fourth:value=(-2 if driver=='nu' else -128)*N/(a*a*a*b*b*b*b)
    else:value=N/((64 if driver=='nu' else 1)*a*a*b*b*b)
    return value


def check_cell(raw,row,rho_terms):
    R=list(map(exact,raw['radii']));Y=[list(map(read,v)) for v in row['preconditioner']]
    assert away0(determinant(Y))
    con=row['contraction']
    q=max(sum(ab(v)*R[j]/R[i] for j,v in enumerate(r)) for i,r in enumerate(con['defects']))
    eta=max(ab(v)/r for v,r in zip(con['residual'],R))
    assert q<=exact(con['q']) and eta<=exact(con['eta']) and q+eta<1
    tight=list(map(exact,con['tight']))
    assert all(r*eta/(1-q)<=t<Ri for r,t,Ri in zip(R,tight,R))
    rho=read(row['rho']);h=exact(raw['driver_half_width'])
    ext=(Q(2)**-8,Q(2)**-12,Q(2)**-19)
    for v,u,r,e,allowed in zip(raw['predictor'],row['rho_predictor'],tight,ext,raw['majorant_domain_half_widths']):
        assert abs(exact(v))*h+abs(exact(u))*rho.abs_upper()+r+e<exact(allowed)
    cp=list(map(read,row['cusp_derivatives']));kp=list(map(read,row['K_cusp_derivatives']))
    assert cp[3].lo>0 and cp[4].hi<0 and cp[6].hi<0
    mun=cp[6]/(4*cp[4]);ln=(4*cp[5]*mun-cp[7])/(16*cp[3])
    mur=-16*kp[0]/cp[4];lr=(4*kp[1]+cp[5]*mur/4)/cp[3]
    assert mun.lo>Q(26,100) and mun.hi<Q(34,100)
    wp,geom=check_geometry(cp,list(map(read,row['neighborhood_derivatives'])),
                           [list(map(read,v)) for v in row['geometry']['preconditioner']])
    scale=exact(row['opening']['nu']['scale'])
    g=list(map(read,row['fold_derivatives']));k=list(map(read,row['K_fold_derivatives']))
    g[0]=g[1]=D(0);g[2]=sym(wp.hi*Q(3,4000))
    g=[v/scale for v in g];k=[v/scale for v in k]
    result={}
    for driver,lp,ts in (('nu',ln,(TERMS3,TERMS4)),('rho',lr,rho_terms)):
        assert exact(row['opening'][driver]['scale'])==exact(row['fourth'][driver]['scale'])==scale
        opening=shape(row,driver,False,ts[0]);fourth=shape(row,driver,True,ts[1]).abs_upper()
        assert opening.hi<0
        fifth=fifth_from_ode(g,lp) if driver=='nu' else joint_ode(g,k,lp)
        S=Q(3,4000);third=-32*opening+sym(fourth*S+fifth*S*S/2)
        assert third.lo>0
        assert third.lo**2>(3*Q(3,10000))**2*Q(221,100)**3
        assert third.hi**2<(3*Q(3,1000))**2*Q(180,100)**3
        result[driver]={'k_derivative':[str(opening.lo),str(opening.hi)],
                        'B_third':[str(third.lo),str(third.hi)],
                        'B_fourth_abs':str(fourth),'B_fifth_abs':str(fifth)}
    return {'index':row['index'],'q':str(q),'eta':str(eta),'geometry':geom,'transport':result}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--sample',action='store_true');args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();p=HERE/'results/family_certificate.json';cert=json.loads(p.read_text())
    for name,h in cert['source_sha256'].items():assert sha(HERE/name)==h
    for entry in cert['input_packages']:
        base=HERE.parent/entry['package'];assert sha(base/'manifest.json')==entry['manifest_sha256']
        for r in json.loads((base/'manifest.json').read_text())['files']:assert sha(base/r['path'])==r['sha256']
    oldpath=HERE.parent/'cusp_connection/results/connection_certificate.json'
    old=json.loads(oldpath.read_text())
    for name,h in cert['input_certificates'].items():assert sha(HERE.parent/name)==h
    assert sha(HERE/'cache/index.json')==cert['H_cache_index_sha256']
    index=json.loads((HERE/'cache/index.json').read_text());assert len(index['files'])==58
    for entry in index['files']:assert sha(HERE/'cache'/entry['file'])==entry['sha256']
    alpha=read(cert['alpha']);factor=1+alpha*D(-Q(1,2),Q(1,2));assert factor.lo>Q(7995,10000)
    # Bounds on the physical epsilon derivative follow from d rho/d eps.
    assert Q(3,10000)/factor.hi**2>Q(2,10000)
    assert Q(3,1000)/factor.lo**2<Q(5,1000)
    assert (D(-Q(1,2))/(1-alpha/2)).lo>-Q(1,2)
    assert (D(Q(1,2))/(1+alpha/2)).hi<Q(3,4)
    terms=algebra();checks=[];nujoins=[];rhojoins=0
    assert len(cert['slabs'])==4 and len(cert['nu_joins'])==228 and len(cert['rho_joins'])==174
    qcert=json.loads((HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json').read_text())
    for j,slab in enumerate(cert['slabs']):
        assert exact(slab['left'])==-Q(1,2)+5*Q(j,16)
        assert exact(slab['right'])==exact(slab['left'])+Q(5,16)
        assert len(slab['cells'])==58
        for i in ((0,28,57) if args.sample else range(58)):
            row=slab['cells'][i];assert row['index']==i and row['rho']==slab['rho']
            assert exact(old['cells'][i]['driver_center'])==-Q(2*i+1,4)
            assert exact(old['cells'][i]['driver_half_width'])==Q(1,4)
            checks.append({'slab':j,**check_cell(old['cells'][i],row,terms)})
            if i%10==0 or i==57:print('Rational domain check slab',j+1,'cell',i+1,flush=True)
        if not args.sample:
            rho=read(slab['rho'])
            for i in range(57):
                a,b=old['cells'][i:i+2];ra,rb=slab['cells'][i:i+2]
                nu=exact(a['driver_left']);assert nu==exact(b['driver_right'])
                ratios=[]
                for n in range(3):
                    da=exact(a['center'][n])+exact(a['predictor'][n])*(nu-exact(a['driver_center']))
                    db=exact(b['center'][n])+exact(b['predictor'][n])*(nu-exact(b['driver_center']))
                    delta=da-db+(exact(ra['rho_predictor'][n])-exact(rb['rho_predictor'][n]))*rho
                    ratio=(delta.abs_upper()+exact(ra['contraction']['tight'][n]))/exact(b['radii'][n])
                    assert ratio<1;ratios.append(str(ratio))
                nujoins.append({'slab':j,'cell':i,'ratios':ratios})
            if j<3:
                assert slab['right']==cert['slabs'][j+1]['left']
                for i in range(58):
                    assert slab['cells'][i]['rho_predictor']==cert['slabs'][j+1]['cells'][i]['rho_predictor']
                    rhojoins+=1
            for edge,nu in ((0,Q(0)),(57,Q(-29))):
                raw=old['cells'][edge];row=slab['cells'][edge]
                a=[exact(x)+exact(v)*(nu-exact(raw['driver_center']))+exact(u)*rho
                   for x,v,u in zip(raw['center'],raw['predictor'],row['rho_predictor'])]
                if edge==0:
                    for x,y,r in zip(a,qcert['center_exact_dyadic'],raw['radii']):
                        assert (x-exact(y)).abs_upper()+exact(qcert['radius'])<exact(r)
                else:assert (a[2]+sym(exact(row['contraction']['tight'][2]))).hi<0
            assert exact(qcert['center_exact_dyadic'][2])-exact(qcert['radius'])>0
    report={'status':'sample_passed' if args.sample else 'independent_rational_downstream_checks_passed',
            'cells':len(checks),'nu_joins':len(nujoins),'rho_joins':rhojoins,
            'exact_symbolic_identities':2,'rho_opening_monomials':len(terms[0]),'rho_fourth_monomials':len(terms[1]),
            'rate_bounds':{'nu':['0.0003','0.003'],'rho':['0.0003','0.003'],'epsilon':['0.0002','0.005']},
            'trust_boundary':'Saved integral/majorant enclosures, Taylor bounds for the preconditioned Jacobian and residual, cusp and neighborhood jets, predictor polynomial ranges and their Taylor remainders are assumed valid. From those inputs this checker independently verifies rational contraction/radius inequalities, all branch joins, full local root geometry, expanded transport polynomials and both fifth-order fold ODEs. It does not independently regenerate the two-variable Taylor polynomials or the quadrature.',
            'rounding':'Exact rational endpoint operations, outward to a 192-bit dyadic grid; no floating-point proof comparisons.',
            'certificate_sha256':sha(p),'source_sha256':sha(__file__),'checks':checks,'nu_join_checks':nujoins,
            'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print('Completed',report['status'],len(checks),'cells;',len(nujoins),rhojoins,'joins',flush=True)


if __name__=='__main__':main()
