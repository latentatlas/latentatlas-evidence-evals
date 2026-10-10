"""R27 interval model: negative-sextic cusp arc, moving dual, and local jets."""
import sys
sys.dont_write_bytecode=True
import hashlib,json
from pathlib import Path
from math import comb,factorial
from flint import arb,arb_mat
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/'theta_effective_remainder'))
from jets import pjets,theta_polynomials,restore,pack,rational,zero_ball,upper,absup,sm
from certify_remainder import cover,poly_pow
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def rows(A):return [[A[i,j] for j in range(A.ncols())] for i in range(A.nrows())]
def symmetric(x):return zero_ball(upper(x))
def nonnegative(x):return x/2+symmetric(x/2)
def dyadic_above(x):
    n=arb(1)
    while n/2>x:n/=2
    while n<x:n*=2
    return n
def jet(u,params,b,order=5,root=False):
    tau,lam,mu,nu=params;pi=arb.pi();N=12;polys=theta_polynomials(order)
    phi=[arb(0) for _ in polys];errors=[]
    for n in range(1,N+1):
        x=pi*n*n*(4*u).exp();fac=pi*n*n*(5*u-x).exp()
        for l,P in enumerate(polys):phi[l]+=fac*sm(c*x**i for i,c in enumerate(P))
    lo,hi=u.lower(),u.upper();assert lo>=0;n=N+1
    for P in polys:
        err=upper(2*sm(abs(c)*pi**(i+1)*n**(2*i+2)*((5+4*i)*hi-pi*n*n*(4*lo).exp()).exp() for i,c in enumerate(P)))
        errors.append(err);phi[len(errors)-1]+=symmetric(err)
    potential={2:lam,4:mu,6:nu}
    pd=[sm(value*(factorial(k)//factorial(k-l))*u**(k-l) for k,value in potential.items() if k>=l) for l in range(order+1)]
    E=[arb(1)]
    for n in range(order):E.append(sm(comb(n,k)*pd[k+1]*E[n-k] for k in range(n+1)))
    ep=pd[0].exp();w=[ep*sm(comb(l,k)*phi[k]*E[l-k] for k in range(l+1)) for l in range(order+1)]
    p=pjets(u,tau,order);raw=[p[3][l]-sm(b[j]*p[j][l] for j in range(3)) for l in range(order+1)]
    q=[[sm(comb(l,k)*w[k]*p[j][l-k] for k in range(l+1)) for l in range(order+1)] for j in range(4)]
    if root:
        assert raw[0].contains(0);raw[0]=arb(0)
    qr=[sm(comb(l,k)*w[k]*raw[l-k] for k in range(l+1)) for l in range(order+1)]
    return {'interval':u,'moment_jets':q,'residual_jets':qr,'weight_jets':w,'p_jets':p,
            'theta_omission_bounds':errors,'at_true_root':root}
def powers(weights,order):
    out=[{0:arb(1)}]
    for _ in range(order):
        row={}
        for j,v in out[-1].items():
            for k,w in weights.items():row[j+k]=row.get(j+k,arb(0))+v*w
        out.append(row)
    return out
def taylor(F,B,offsets,upto,order=6):
    p=powers({1:offsets[0],2:-offsets[1]/4,4:offsets[2]/16,6:-offsets[3]/64},order)
    assert upto+6*(order-1)<len(F) and upto+6*order<len(B)
    values=[];rems=[]
    for n in range(upto+1):
        value=sm(sm(c*F[n+j] for j,c in p[k].items())/factorial(k) for k in range(order))
        rem=upper(sm(absup(c)*B[n+j] for j,c in p[-1].items())/factorial(order))
        values.append(value+symmetric(rem));rems.append(rem)
    return values,rems
def tangent(d):
    mu=d[6]/(4*d[4]);lam=(4*d[5]*mu-d[7])/(16*d[3])
    tau=(d[8]/64+d[4]*lam/4-d[6]*mu/16)/d[3]
    return [tau,lam,mu]
def cusp_box(width):
    q=read(RESEARCH/'theta_fourth_order/results/certificate.json')
    data=read(RESEARCH/'cusp_shape_design/results/local_jets.json')
    curve=read(RESEARCH/'cusp_connection/results/connection_certificate.json')['cells'][0]
    Q=list(map(restore,q['Q_box']));F=list(map(restore,data['F_at_exact_Q']));B=list(map(restore,data['absolute_F_bounds']))
    domain=list(map(restore,data['local_majorant_domain']))
    # The existing arc covers [-1/2,0]. For nu<=0, its positive moment
    # majorants at nu=0 also cover every segment used by this Taylor expansion.
    assert width>0 and width<=rational('1/65536')
    nu=-width/2+symmetric(width/2);coarse=list(map(restore,curve['cusp_tangent_enclosures']))
    offsets=[x*nu for x in coarse]+[nu]
    assert absup(offsets[1])<domain[1] and absup(offsets[2])<domain[2]
    first,rem=taylor(F,B,offsets,8)
    v=tangent(first);refined=[x*nu for x in v]+[nu]
    # Both enclosures follow from integration of a velocity valid over the whole arc.
    assert all(absup(refined[i])<=absup(offsets[i]) for i in range(3))
    values,rems=taylor(F,B,refined,9)
    params=[Q[j]+refined[j] for j in range(3)]+[nu]
    assert 41<params[0] and params[0]<42 and -4<params[1] and params[1]<0 and 0<params[2] and params[2]<9
    # Arb radius widening may extend the representational box a few ulps beyond
    # nu=0. The mathematical domain is the exact interval [-width,0].
    return {'driver_width':width,'Q0_box':Q,'coarse_velocity':coarse,'coarse_offsets':offsets,
      'coarse_derivatives':first,'refined_velocity':v,'offsets':refined,'parameter_box':params,
      'derivatives':values,'taylor_remainders':rems,'positive_moment_bounds':B,
      'majorant_domain':domain,'taylor_order':6}
def isolate_roots(params,b,old,with_cover=True):
    roots=[];rho=rational('1/4000');left=arb(0);sign=1;leaves=[]
    for row in old['finite_roots']:
        center=restore(row['root_interval']).mid();I=center+symmetric(rho)
        p=pjets(I,params[0],1);dr=p[3][1]-sm(b[j]*p[j][1] for j in range(3))
        sigma=row['orientation'];assert sigma*dr>0,('coarse derivative',row['index'])
        lo,hi=I.lower(),I.upper()
        for x,s in [(lo,sign),(hi,-sign)]:
            pp=pjets(x,params[0],0);assert s*(pp[3][0]-sm(b[j]*pp[j][0] for j in range(3)))>0,('bracket',row['index'])
        if with_cover:leaves+=cover(left,lo,params,b,sign)
        initial=I;steps=[]
        for _ in range(3):
            c=I.mid();pc=pjets(c,params[0],0);rr=pc[3][0]-sm(b[j]*pc[j][0] for j in range(3))
            pp=pjets(I,params[0],1);dd=pp[3][1]-sm(b[j]*pp[j][1] for j in range(3))
            radius=upper(absup(rr/dd));candidate=c+symmetric(radius)
            if not I.contains(candidate) or not candidate.rad()<I.rad():break
            steps.append({'input':I,'center':c,'residual':rr,'derivative':dd,'output':candidate});I=candidate
        assert steps
        roots.append({'index':row['index'],'root':I,'orientation':sigma,'coarse':initial,'contractions':steps})
        left=hi;sign=-sign
    if with_cover:leaves+=cover(left,arb(1),params,b,sign)
    assert all(roots[i]['coarse'].upper()<roots[i+1]['coarse'].lower() for i in range(27))
    return roots,leaves
def perturbation_bounds(arc):
    B=arc['positive_moment_bounds'];dt,dl,dm,dn=list(map(absup,arc['offsets']))
    return [upper(dt*B[j+1]+dl*B[j+2]/4+dm*B[j+4]/16+dn*B[j+6]/64) for j in range(4)]
def moving_dual(arc,old,old15):
    params=arc['parameter_box'];center=list(map(restore,old['dual_center']));E=perturbation_bounds(arc)
    center_roots,_=isolate_roots(params,center,old,False)
    gradient=[];sign_errors=[]
    for j in range(3):
        terms=[]
        for r,prior in zip(center_roots,old15['uniform_roots']):
            z=r['root'];base=restore(prior['root_interval']);lo=min(z.lower(),base.lower());hi=max(z.upper(),base.upper())
            hull=(lo+hi)/2+symmetric((hi-lo)/2);q=jet(hull,params,center,order=0)['moment_jets'][j][0]
            terms.append(upper(2*(hi-lo)*absup(q)))
        tail=upper(2*88*2**j*(18-arb.pi()*arb(4).exp()).exp()/540)
        sg=upper(sm(terms)+tail);sign_errors.append({'root_terms':terms,'integral_tail':tail,'total':sg})
        gradient.append(upper(restore(old15['gradient_rows'][j]['absolute_gradient_upper'])+E[j]+sg))
    C=arb_mat([list(map(restore,row)) for row in old['linear_solve']['preconditioner']])
    forcing=[upper(sm(absup(C[i,j])*gradient[j] for j in range(3))) for i in range(3)]
    radii=[dyadic_above(4*x) for x in forcing]
    b=[center[i]+symmetric(radii[i]) for i in range(3)]
    roots,leaves=isolate_roots(params,b,old,True)
    gf=arb_mat(3,3)
    jets=[]
    for row in roots:
        at=jet(row['root'],params,b,order=3,root=True);jets.append(at)
        gamma=row['orientation']*at['residual_jets'][1];assert gamma>0
        for i in range(3):
            for j in range(3):gf[i,j]+=2*at['moment_jets'][i][0]*at['moment_jets'][j][0]/gamma
    tail=restore(old['tail_absolute_bounds']['G_entry'])
    G=arb_mat([[gf[i,j]+(nonnegative(tail) if i==j else symmetric(tail)) for j in range(3)] for i in range(3)])
    defect=arb_mat([[arb(i==j)-(C*G)[i,j] for j in range(3)] for i in range(3)])
    contraction=[upper(sm(absup(defect[i,j])*radii[j]/radii[i] for j in range(3))) for i in range(3)]
    scaled_force=[upper(forcing[i]/radii[i]) for i in range(3)]
    assert all(contraction[i]+scaled_force[i]<1 for i in range(3)),('dual contraction',contraction,scaled_force,radii)
    assert not C.det().contains(0)
    # Global convexity plus positive definite local Hessian identifies this
    # stationary dual uniquely as the unrestricted optimum for each parameter.
    minors=[arb_mat([[G[i,j] for j in range(k)] for i in range(k)]).det() for k in [1,2,3]]
    assert all(x>0 for x in minors)
    factor=upper(max(scaled_force)/(1-max(contraction)))
    tight=[center[i]+symmetric(upper(radii[i]*factor)) for i in range(3)]
    assert all(b[i].contains(tight[i]) for i in range(3))
    tight_roots,_=isolate_roots(params,tight,old,False)
    tight_jets=[jet(row['root'],params,tight,order=3,root=True) for row in tight_roots]
    return {'center':center,'radii':radii,'box':b,'center_roots':center_roots,'L1_density_changes':E,
      'gradient_upper':gradient,'sign_change_errors':sign_errors,'preconditioner':rows(C),
      'forcing_upper':forcing,'scaled_forcing':scaled_force,'Gram':rows(G),'Gram_minors':minors,
      'preconditioned_defect':rows(defect),'contraction_rows':contraction,'roots':roots,'sign_cover':leaves,'root_jets':jets,
      'tightening_factor':factor,'tight_box':tight,'tight_roots':tight_roots,'tight_jets':tight_jets}
def coefficients(arc,dual,old):
    rows0=dual['tight_roots'];jets=dual['tight_jets'];Gamma=arb(0);B=[arb(0)]*3;R=arb(0);Gf=arb_mat(3,3)
    for row,at in zip(rows0,jets):
        sig=row['orientation'];q=at['moment_jets'];r=at['residual_jets'];gamma=sig*r[1];Gamma+=gamma
        for j in range(3):B[j]+=sig*(q[j][0]*r[2]/r[1]-q[j][1])/3
        for i in range(3):
            for j in range(3):Gf[i,j]+=2*q[i][0]*q[j][0]/gamma
        R+=r[2]**2/(36*gamma)-sig*r[3]/60
    tails={k:restore(v) for k,v in old['tail_absolute_bounds'].items()}
    Gamma+=nonnegative(tails['Gamma']);B=[x+symmetric(tails['B_entry']) for x in B];R+=symmetric(tails['R'])
    G=arb_mat([[Gf[i,j]+(nonnegative(tails['G_entry']) if i==j else symmetric(tails['G_entry'])) for j in range(3)] for i in range(3)])
    C=arb_mat([list(map(restore,row)) for row in old['linear_solve']['preconditioner']])
    y=arb_mat([[x] for x in B]);candidate=G.inv()*y;v0=arb_mat([[candidate[i,0].mid()] for i in range(3)]);res=y-G*v0
    defect=arb_mat([[arb(i==j)-(C*G)[i,j] for j in range(3)] for i in range(3)])
    eta=upper(max(upper(sm(absup(defect[i,j]) for j in range(3))) for i in range(3)));assert eta<1
    forcing=upper(max(absup(x[0]) for x in rows(C*res)));rad=upper(forcing/(1-eta))
    v=[v0[i,0]+symmetric(rad) for i in range(3)]
    P=sm(B[j]*v[j] for j in range(3))/2;Xi=R-P
    E=dual['L1_density_changes'];bb=dual['tight_box']
    Dchange=upper(E[3]+sm(max(absup(bb[j]),absup(restore(old['dual_box'][j])))*E[j] for j in range(3)))
    D=restore(old['coefficients']['D'])+symmetric(Dchange);assert D>0
    f=arc['derivatives'][3];assert f>0
    delta=f/D;C2=delta**3*Gamma/(3*D);C4=delta**5*(Gamma**2/(3*D*D)-Xi/D)
    return {'f':f,'delta0':delta,'D':D,'Gamma':Gamma,'R':R,'P':P,'Xi':Xi,'C2':C2,'C4':C4,
      'v':v,'B':B,'G':rows(G),'D_variation_bound':Dchange,'solve_defect':rows(defect),
      'solve_v0':[v0[i,0] for i in range(3)],'solve_eta':eta,'solve_forcing':forcing,'solve_radius':rad}
