"""R29: recentered continuation on the already identified R03 cusp graph.

Candidate Newton iterates select exact dyadic centers. Only the subsequent
interval contraction, integral enclosures and branch containment prove facts.
"""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from flint import arb,acb,arb_mat,ctx
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/'cusp_coefficient_motion'))
import motion as previous
base=previous.base
restore,pack,rational,upper,absup,sm=base.restore,base.pack,base.rational,base.upper,base.absup,base.sm
sym,rows,unbox=previous.sym,previous.rows,previous.unbox
sys.path.insert(0,str(RESEARCH/'cusp_connection'))
from explore import refine,point_cache,J
from validated_flow import finite_kernel,series_tail,domain_tail
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def old_data():
    return (read(RESEARCH/'theta_fourth_order/results/certificate.json'),
      unbox(read(RESEARCH/'cusp_connection/results/connection_certificate.json')),
      unbox(read(RESEARCH/'cusp_shape_design/results/local_jets.json')))
def segment(params,n,a,b):
    tau,lam,mu,nu=params
    assert all(x.is_exact() for x in params+[a,b])
    def fun(u,analytic):
        if not (4*u).exp().real>0:return acb('nan','nan')
        z=2*acb(tau)*u;trig=(z.cos(),-z.sin(),-z.cos(),z.sin())[n%4]
        return finite_kernel(u,8)*(acb(lam)*u*u+acb(mu)*u**4+acb(nu)*u**6).exp()*(2*u)**n*trig
    ans=acb.integral(fun,acb(a),acb(b),abs_tol=arb('1e-70'),rel_tol=arb('1e-70'),eval_limit=100000)
    assert ans.is_finite(),'Signed quadrature failed'
    return ans.real
def template_moments(params,knots,nmax):
    cuts=[arb(0)]+knots+[arb(1)];values=[arb(0)]*(nmax+1);records=[]
    for i,(a,b) in enumerate(zip(cuts,cuts[1:])):
        val=[segment(params,n,a,b) for n in range(nmax+1)]
        values=[values[n]+(-1)**i*val[n] for n in range(nmax+1)]
        records.append({'left':a,'right':b,'sign':(-1)**i,'finite_integrals':val})
    P={1:params[1],2:params[2],3:params[3]};tails=[]
    for n in range(nmax+1):
        e=upper(series_tail(P,n,arb(1),8)+domain_tail(P,n,arb(1)));tails.append(e);values[n]+=sym(e)
    return values,{'segments':records,'truncation_errors':tails,'template_moments':values}
def raw(z,t,b,order=1):
    p=previous.pjets(z,t,3,order)
    return [p[3][l]-sm(b[j]*p[j][l] for j in range(3)) for l in range(order+1)]
def root_candidates(t,b,seeds):
    zz=[]
    for z in seeds:
        z=z.mid()
        for _ in range(15):
            val,der=raw(z,t,b);step=val/der;z=(z-step).mid()
            if absup(step)<rational('1e-75'):break
        else:raise ArithmeticError('Root candidate failed')
        zz.append(z)
    assert all(0<z<1 for z in zz) and all(a<b for a,b in zip(zz,zz[1:]))
    return zz
def candidate_gram(params,b,zz):
    G=arb_mat(3,3)
    for z in zz:
        at=base.jet(z,params,b,order=1);p=at['p_jets'];w=at['weight_jets'][0];rp=raw(z,params[0],b)[1]
        for i in range(3):
            for j in range(3):G[i,j]+=2*w*p[i][0]*p[j][0]/abs(rp)
    return G
def dual_candidate(params,old):
    b=[restore(x).mid() for x in old['dual_center']]
    seeds=[restore(row['root_interval']).mid()*restore(old['Q_box'][0]).mid()/params[0] for row in old['finite_roots']]
    for iteration in range(10):
        zz=root_candidates(params[0],b,seeds);S,_=template_moments(params,zz,2)
        G=candidate_gram(params,b,zz);step=G.inv()*arb_mat([[s] for s in S]);b=[(b[i]+step[i,0]).mid() for i in range(3)]
        if max(absup(step[i,0]) for i in range(3))<rational('1e-50'):break
    else:raise ArithmeticError('Dual candidate failed')
    zz=root_candidates(params[0],b,zz)
    return b,zz,iteration+1
def positive_bounds_check(params,jets):
    # The R09 envelope ignores the negative sextic. Coefficients below its
    # upper quartic parameters are dominated pointwise for every u>=0.
    upper_controls=[jets['center'][i]+jets['local_majorant_domain'][i] for i in range(3)]
    assert params[1]<upper_controls[1] and params[2]<upper_controls[2] and params[3]<=0
def anchor(nu):
    old,curve,jets=old_data();B=jets['absolute_F_bounds'];cell=curve['cells'][0]
    assert -rational('1/2')<nu<0 and nu.is_exact()
    seed=[(cell['center'][j]+cell['predictor'][j]*(nu-cell['driver_center'])).mid() for j in range(3)]
    x,_,Y,err,steps=refine(seed,nu)
    F=point_cache(x,nu,nmax=39)
    radius=arb(2)**-160;params=[a+sym(radius) for a in x]+[nu]
    positive_bounds_check(params,jets)
    dd,rem=base.taylor(F,B,[sym(radius)]*3+[arb(0)],6,order=3)
    C=arb_mat(Y);JJ=arb_mat(J(dd));E=arb_mat([[arb(i==j)-(C*JJ)[i,j] for j in range(3)] for i in range(3)])
    q=upper(max(sm(absup(E[i,j]) for j in range(3)) for i in range(3)))
    rr=C*arb_mat([[v] for v in F[:3]]);eta=upper(max(absup(rr[i,0])/radius for i in range(3)))
    assert not C.det().contains(0) and q+eta<1
    rstar=upper(radius*eta/(1-q));exactbox=[a+sym(rstar) for a in x]
    affine=[cell['center'][j]+cell['predictor'][j]*(nu-cell['driver_center']) for j in range(3)]
    distances=[upper(absup(x[j]-affine[j])+radius) for j in range(3)]
    assert all(distances[j]<cell['radii'][j] for j in range(3))
    # A root in our smaller box is also in the R03 uniqueness tube. This is
    # containment plus uniqueness, not merely overlap of approximate boxes.
    b,knots,nsteps=dual_candidate(x+[nu],old)
    S,quadrature=template_moments(x+[nu],knots,9)
    errors=[upper(rstar*(B[n+1]+B[n+2]/4+B[n+4]/16)) for n in range(10)]
    S=[S[n]+sym(errors[n]) for n in range(10)]
    root_template={**old,'finite_roots':[dict(row,root_interval=pack(z)) for row,z in zip(old['finite_roots'],knots)]}
    roots,cover=base.isolate_roots(exactbox+[nu],b,root_template,True)
    out={'nu':nu,'center':x,'root_radius':rstar,'box':exactbox,'central_derivatives':F,'B':B,
      'cusp_validation':{'trial_radius':radius,'preconditioner':Y,'defect':rows(E),'q':q,'eta':eta,
        'q_plus_eta':upper(q+eta),'branch_containment':distances,'candidate_iterations':steps,'candidate_error':err},
      'dual_center':b,'knots':knots,'template_moments':S,'template_quadrature':quadrature,
      'template_cusp_displacement_errors':errors,'dual_candidate_iterations':nsteps,
      'point_roots':roots,'point_sign_cover':cover,'root_template':root_template}
    arc={'offsets':[arb(0)]*4,'parameter_box':exactbox+[nu],'positive_moment_bounds':B}
    pointS,pointRecords=transport(out,arc,b,roots)
    out['point_sign_moments']=pointS;out['point_sign_transport']=pointRecords
    return out
def cusp_arc(a,h):
    old,curve,jets=old_data();nu=a['nu'];assert nu-h>=-rational('1/2') and nu+h<=0
    B=a['B'];F=a['central_derivatives'];s=sym(h);coarse=curve['cells'][0]['cusp_tangent_enclosures'];r=a['root_radius']
    assert coarse[1]>0 and coarse[2]>0
    offsets=[sym(r)+v*s for v in coarse]+[s];first,rems=base.taylor(F,B,offsets,8)
    v=base.tangent(first)
    for _ in range(2):
        offsets=[sym(r)+z*s for z in v]+[s];ds,rems=base.taylor(F,B,offsets,9);v=base.tangent(ds)
    offsets=[sym(r)+z*s for z in v]+[s];ds,rems=base.taylor(F,B,offsets,9)
    params=[a['center'][j]+offsets[j] for j in range(3)]+[nu+s]
    assert ds[3]>0 and ds[4]<0 and ds[6]<0
    assert 41<params[0]<42 and -4<params[1]<0 and 0<params[2]<9
    assert all(absup(x)<1 for x in v) and v[1]>0 and v[2]>0
    # R03 proves lambda and mu increase on [-1/2,0]. Actual expansion
    # segments stay below Q(0) (plus the dyadic center's tiny error).
    return {'driver_center':nu,'driver_half_width':h,'driver_left':nu-h,'driver_right':nu+h,
      'positive_moment_bounds':B,'coarse_velocity':coarse,'refined_velocity':v,'offsets':offsets,
      'parameter_box':params,'derivatives':ds,'taylor_remainders':rems,'taylor_order':6}
def transport(a,arc,b,roots):
    B=arc['positive_moment_bounds'];params=arc['parameter_box'];offsets=list(map(absup,arc['offsets']))
    # Arc offsets are measured from the dyadic cusp center; the stored
    # moments already include its exact-cusp displacement. Counting that
    # displacement again is conservative and avoids an unstated subtraction.
    dt,dl,dm,dn=offsets;out=[];records=[]
    for n in range(10):
        E=upper(dt*B[n+1]+dl*B[n+2]/4+dm*B[n+4]/16+dn*B[n+6]/64);terms=[]
        for root,knot in zip(roots,a['knots']):
            lo=min(root['root'].lower(),knot);hi=max(root['root'].upper(),knot);u=(lo+hi)/2+sym((hi-lo)/2)
            w=base.jet(u,params,b,order=0)['weight_jets'][0];p=previous.pjets(u,params[0],n,0)[n][0]
            terms.append(upper(2*(hi-lo)*absup(w*p)))
        tail=upper(2*88*2**n*(18-arb.pi()*arb(4).exp()).exp()/540)
        error=upper(E+sm(terms)+tail);value=a['template_moments'][n]+sym(error);out.append(value)
        records.append({'order':n,'base_template_moment':a['template_moments'][n],'L1_change':E,
          'root_motion_terms':terms,'whole_sign_tail':tail,'error':error,'enclosure':value})
    return out,records
def fixed_b_rhs(arc,b,roots,S):
    vel=arc['refined_velocity'];params=arc['parameter_box'];rhs=[]
    for j in range(3):rhs.append(vel[0]*S[j+1]-vel[1]*S[j+2]/4+vel[2]*S[j+4]/16-S[j+6]/64)
    terms=[]
    for row in roots:
        at=previous.root_jets(row['root'],params,b);p=at['p_jets_extended'];q=at['moment_jets_extended'];gamma=row['orientation']*at['residual_jets'][1]
        hh=at['weight_jets'][0]*vel[0]*(p[4][0]-sm(b[j]*p[j+1][0] for j in range(3)))
        vals=[2*q[j][0]*hh/gamma for j in range(3)];terms.append(vals);rhs=[rhs[j]+vals[j] for j in range(3)]
    tail=previous.tails(previous.tail_constants())['dual_rhs'];rhs=[x+sym(tail) for x in rhs]
    return rhs,terms,tail
def gram(params,b,roots,old):
    G=arb_mat(3,3);jj=[]
    for row in roots:
        at=base.jet(row['root'],params,b,order=3,root=True);jj.append(at);q=at['moment_jets'];gamma=row['orientation']*at['residual_jets'][1];assert gamma>0
        for i in range(3):
            for j in range(3):G[i,j]+=2*q[i][0]*q[j][0]/gamma
    tail=restore(old['tail_absolute_bounds']['G_entry'])
    return arb_mat([[G[i,j]+(base.nonnegative(tail) if i==j else sym(tail)) for j in range(3)] for i in range(3)]),jj
def moving_dual(a,arc):
    old,_,_=old_data();params=arc['parameter_box'];b0=a['dual_center'];h=arc['driver_half_width']
    center_roots,_=base.isolate_roots(params,b0,a['root_template'],False)
    S,records=transport(a,arc,b0,center_roots);rhs,terms,tail=fixed_b_rhs(arc,b0,center_roots,S)
    pointG,_=gram(a['box']+[a['nu']],b0,a['point_roots'],old)
    inv=pointG.inv();C=arb_mat([[inv[i,j].mid() for j in range(3)] for i in range(3)])
    initial=C*arb_mat([[x] for x in a['point_sign_moments'][:3]]);rate=C*arb_mat([[x] for x in rhs])
    forcing=[upper(absup(initial[i,0])+h*absup(rate[i,0])) for i in range(3)]
    radii=[base.dyadic_above(max(4*x,rational('1e-45'))) for x in forcing];b=[b0[j]+sym(radii[j]) for j in range(3)]
    assert absup(b[0])<rational('1/1000') and absup(b[1])<rational('1/10') and absup(b[2])<rational('1/200')
    roots,cover=base.isolate_roots(params,b,a['root_template'],True);G,jj=gram(params,b,roots,old)
    defect=arb_mat([[arb(i==j)-(C*G)[i,j] for j in range(3)] for i in range(3)])
    contraction=[upper(sm(absup(defect[i,j])*radii[j]/radii[i] for j in range(3))) for i in range(3)]
    scaled=[upper(forcing[i]/radii[i]) for i in range(3)]
    assert all(contraction[i]+scaled[i]<1 for i in range(3)),('dual contraction',contraction,scaled)
    assert not C.det().contains(0)
    minors=[arb_mat([[G[i,j] for j in range(k)] for i in range(k)]).det() for k in [1,2,3]];assert all(v>0 for v in minors)
    factor=upper(max(scaled)/(1-max(contraction)));tight=[b0[j]+sym(upper(radii[j]*factor)) for j in range(3)]
    assert all(b[j].contains(tight[j]) for j in range(3))
    tightroots,_=base.isolate_roots(params,tight,a['root_template'],False);_,tightjets=gram(params,tight,tightroots,old)
    return {'center':b0,'radii':radii,'box':b,'center_roots':center_roots,'center_sign_transport':records,
      'fixed_b_rhs':rhs,'fixed_b_rhs_terms':terms,'fixed_b_rhs_tail':tail,'point_Gram':rows(pointG),
      'preconditioner':rows(C),'preconditioned_initial_residual':[initial[i,0] for i in range(3)],
      'preconditioned_residual_derivative':[rate[i,0] for i in range(3)],'forcing_upper':forcing,
      'scaled_forcing':scaled,'Gram':rows(G),'Gram_minors':minors,'preconditioned_defect':rows(defect),
      'contraction_rows':contraction,'roots':roots,'sign_cover':cover,'tightening_factor':factor,
      'tight_box':tight,'tight_roots':tightroots,'tight_jets':tightjets}
def coefficients(a,arc,dual):
    old,_,_=old_data();bb=dual['tight_box'];S,records=transport(a,arc,bb,dual['tight_roots'])
    v=arc['refined_velocity'];S[:3]=[arb(0)]*3
    partial=lambda j:v[0]*S[j+1]-v[1]*S[j+2]/4+v[2]*S[j+4]/16-S[j+6]/64
    Dprime=partial(3)-sm(bb[j]*partial(j) for j in range(3))
    Sp=a['point_sign_moments'];b0=a['dual_center'];Dcenter=Sp[3]-sm(b0[j]*Sp[j] for j in range(3))
    dr=[absup(bb[j]-b0[j]) for j in range(3)];G=dual['Gram']
    ancherror=upper(sm(absup(Sp[j])*dr[j] for j in range(3))+sm(absup(G[i][j])*dr[i]*dr[j] for i in range(3) for j in range(3))/2)
    Derror=upper(ancherror+arc['driver_half_width']*absup(Dprime));D=Dcenter+sym(Derror);assert D>0
    Gamma=arb(0);B=[arb(0)]*3;R=arb(0);Gf=arb_mat(3,3)
    for row,at in zip(dual['tight_roots'],dual['tight_jets']):
        sig=row['orientation'];q=at['moment_jets'];r=at['residual_jets'];gamma=sig*r[1];Gamma+=gamma
        for j in range(3):B[j]+=sig*(q[j][0]*r[2]/r[1]-q[j][1])/3
        for i in range(3):
            for j in range(3):Gf[i,j]+=2*q[i][0]*q[j][0]/gamma
        R+=r[2]**2/(36*gamma)-sig*r[3]/60
    tails={k:restore(z) for k,z in old['tail_absolute_bounds'].items()}
    Gamma+=base.nonnegative(tails['Gamma']);B=[z+sym(tails['B_entry']) for z in B];R+=sym(tails['R'])
    GG=[[Gf[i,j]+(base.nonnegative(tails['G_entry']) if i==j else sym(tails['G_entry'])) for j in range(3)] for i in range(3)]
    vv,solve=previous.solve(GG,B,dual['preconditioner']);P=sm(B[j]*vv[j] for j in range(3))/2;Xi=R-P
    f=arc['derivatives'][3];delta=f/D
    C2=delta**3*Gamma/(3*D);C4=delta**5*(Gamma**2/(3*D**2)-Xi/D)
    return {'f':f,'D':D,'delta0':delta,'Gamma':Gamma,'B':B,'G':GG,'v':vv,'R':R,'P':P,'Xi':Xi,'C2':C2,'C4':C4,
      'linear_solve':solve,'D_center_objective':Dcenter,'D_anchor_error':ancherror,'D_derivative_bound':Dprime,
      'D_total_error':Derror,'D_sign_transport':records}
def cell(a,h):
    arc=cusp_arc(a,h);dual=moving_dual(a,arc);co=coefficients(a,arc,dual)
    return {'arc':arc,'dual':dual,'coefficients':co}
