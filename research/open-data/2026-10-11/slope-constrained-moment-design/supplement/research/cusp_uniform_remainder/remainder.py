"""R27 recomputation of every finite-cell and scalar remainder bound over the arc."""
from model import *
def produce(arc,dual,co,alg):
    params=arc['parameter_box'];b=dual['tight_box'];v=co['v'];va=list(map(absup,v))
    a0=rational(alg['a_max']);rho=rational('1/4000');M0=rational('2e-5');V=list(map(rational,alg['v_absolute_bounds']))
    assert all(va[j]<V[j] for j in range(3))
    expanded=[b[j]+symmetric(upper(va[j]*a0*a0)) for j in range(3)]
    assert all(absup(expanded[j])<rational(x) for j,x in enumerate(['.001','.1','.005']))
    gap=rational('1.0005')+symmetric(rational('.0005'));p=pjets(gap,params[0],0)
    gapvalue=p[3][0]-sm(expanded[j]*p[j][0] for j in range(3));assert gapvalue>0
    local=[];Kstar=arb(0);Hm=[arb(0)]*3
    for row in dual['tight_roots']:
        z=row['root'];sig=row['orientation'];at=jet(z,params,b,root=True)
        q=at['moment_jets'];r=at['residual_jets'];kap=(sm(q[j][0]*v[j] for j in range(3))-r[2]/6)/r[1];ka=absup(kap)
        I=z+symmetric(rho);near=jet(I,params,b);trial=jet(I,params,expanded)
        Q=[[absup(x) for x in rr] for rr in near['moment_jets']];R=list(map(absup,near['residual_jets']))
        m=(sig*trial['residual_jets'][1]).lower();L=absup(trial['residual_jets'][1]);assert m>0
        H=[upper(absup(q[j][1])*ka**2+absup(q[j][2])*(ka+ka**3*a0**2)/3
           +Q[j][3]*(rational('1/5')+2*ka**2*a0**2+ka**4*a0**4)/12) for j in range(3)]
        for j in range(3):Hm[j]+=H[j]
        ks=upper(absup(r[2])*ka**3/3+absup(r[3])*(2*ka**2+ka**4*a0**2)/12
          +absup(r[4])*(ka+rational('10/3')*ka**3*a0**2+ka**5*a0**4)/60
          +R[5]*(rational('1/7')+3*ka**2*a0**2+5*ka**4*a0**4+ka**6*a0**6)/360)
        Kstar+=ks
        hb=upper(absup(r[2])*ka**2/2+absup(r[3])*(ka+ka**3*a0**2)/6
             +R[4]*(rational('1/5')+2*ka**2*a0**2+ka**4*a0**4)/24
             +sm(va[j]*(absup(q[j][1])*ka+Q[j][2]*(rational('1/3')+ka**2*a0**2)/2) for j in range(3)))
        shift=upper(hb*a0**4/m);assert ka*a0<1 and ka*a0*a0+shift+a0<rho
        local.append({'index':row['index'],'orientation':sig,'root':z,'kappa':kap,'kappa_abs':ka,'root_jets':at,
          'neighborhood':I,'neighborhood_jets':near,'trial_neighborhood_jets':trial,'Q_abs':Q,'R_abs':R,
          'trial_derivative_lower':m,'trial_derivative_abs_upper':L,'moment_fourth_bound':H,
          'residual_sixth_bound':ks,'balance_fourth_bound':hb,'balanced_center_distance_upper':shift})
    leaves=[];left=arb(0);sign=-local[0]['orientation']
    for row in local:
        lo,hi=row['neighborhood'].lower(),row['neighborhood'].upper();assert left<lo
        leaves+=cover(left,lo,params,expanded,sign)
        for x,s in [(lo,sign),(hi,-sign)]:
            p=pjets(x,params[0],0);assert s*(p[3][0]-sm(expanded[j]*p[j][0] for j in range(3)))>0
        left=hi;sign=-sign
    leaves+=cover(left,arb(1),params,expanded,sign)
    old26=read(RESEARCH/'theta_global_remainder/results/certificate.json');eps=rational(alg['epsilon'])
    S={d:restore(old26['weighted_tail_bounds'][str(d)]['root_sum']) for d in [12,16,24]}
    Int={d:restore(old26['weighted_tail_bounds'][str(d)]['integral']) for d in [12,16,24]}
    Hj=list(map(rational,alg['active_moment_constants']));Cs=rational(alg['active_residual_sixth_constant']);C8=rational(alg['active_dual_eighth_constant'])
    Htail=[upper(Hj[j]*S[12]+188*eps**-2*S[12]+2**(j+1)*eps**-4*Int[16]/(1-48*a0)) for j in range(3)]
    Ktail=upper(Cs*S[16]+sm(V[j]*Hj[j]*S[12] for j in range(3))+300*eps**-4*S[16]
                 +2071000*eps**-2*S[16]+18*eps**-6*Int[24]/(1-72*a0))
    tail8=upper(C8*S[24]);Hfinite=list(map(upper,Hm));H=[upper(Hm[j]+Htail[j]) for j in range(3)]
    J=arb_mat([[-2*local[k]['orientation']*local[k]['root_jets']['moment_jets'][j][0] for k in range(3)] for j in range(3)])
    inv=J.inv();C=arb_mat([[inv[i,j].mid() for j in range(3)] for i in range(3)])
    error=arb_mat([[arb(i==j)-(C*J)[i,j] for j in range(3)] for i in range(3)])
    force=[upper(sm(absup(C[i,j])*H[j] for j in range(3))) for i in range(3)]
    W=[dyadic_above(2*x) for x in force]
    variation=[[upper(2*(local[k]['Q_abs'][j][1]*(local[k]['kappa_abs']*a0**2+W[k]*a0**4)
                   +local[k]['Q_abs'][j][2]*a0**2/6)) for k in range(3)] for j in range(3)]
    contraction=[upper(sm((absup(error[i,k])+sm(absup(C[i,j])*variation[j][k] for j in range(3)))*W[k]/W[i] for k in range(3))) for i in range(3)]
    forcing=[upper(force[i]/W[i]) for i in range(3)]
    assert all(contraction[i]+forcing[i]<1 for i in range(3))
    assert all(local[k]['kappa_abs']*a0**2+W[k]*a0**4+a0<rho for k in range(3))
    K6=upper(Kstar+sm(va[j]*Hfinite[j] for j in range(3)))
    K8dual=upper(sm(row['balance_fourth_bound']**2/row['trial_derivative_lower'] for row in local))
    K8primal=upper(sm(2*local[k]['balance_fourth_bound']*W[k]+local[k]['trial_derivative_abs_upper']*W[k]**2 for k in range(3)))
    Kd=upper(K6+Ktail+a0*a0*(K8dual+tail8));Kp=upper(K6+Ktail+a0*a0*K8primal)
    f,delta,D,Gamma,Xi=[co[k] for k in ['f','delta0','D','Gamma','Xi']];assert Xi>0
    loss=upper(Gamma*a0*a0/3+absup(Xi)*a0**4+Kp*a0**6)
    U=upper(delta.upper()/(1-loss/D.lower()));assert U<1 and U/M0<a0
    low=(Gamma/3-Xi*delta**2/M0**2).lower();high=(U-delta-Gamma*U**3/(3*D*M0**2)-Kp*U**7/(D*M0**6)).lower()
    jd=(D-Gamma*U**2/M0**2-7*Kp*U**6/M0**6).lower();fd=(D-Gamma*U**2/M0**2).lower()
    assert low>0 and high>0 and jd>0 and fd>0
    t=Gamma/(3*D);e=Xi/D;c=3*t*t-e;poly=[arb(1),t,c];p3=poly_pow(poly,3);p5=poly_pow(poly,5)
    rem=[arb(0)]*13
    for i,x in enumerate(poly):rem[i]+=x
    rem[0]-=1
    for i,x in enumerate(p3):rem[i+1]-=t*x
    for i,x in enumerate(p5):rem[i+2]+=e*x
    assert all(x.contains(0) for x in rem[:3])
    wmax=upper(delta**2/M0**2);scalar=upper(sm(absup(x)*wmax**(n-3) for n,x in enumerate(rem) if n>=3))
    Kpoly=upper(f*delta**6*scalar)
    assert delta.upper()+co['C2'].upper()/M0**2+co['C4'].upper()/M0**4<U
    km=upper((Kpoly+Kd*U**7)/fd);kp=upper((Kpoly+Kp*U**7)/fd)
    assert co['C4'].lower()>km/M0**2
    return {'local':local,'expanded_trial_dual_box':expanded,'sign_cover':leaves,'tail_gap_residual':gapvalue,
       'moment_fourth_bounds_finite':Hfinite,'moment_tail_bounds':Htail,'target_sixth_tail':Ktail,'dual_eighth_tail':tail8,
       'moment_fourth_bounds':H,'repair_jacobian':rows(J),'repair_preconditioner':rows(C),'repair_defect':rows(error),
       'repair_scaled_box':W,'repair_variation':variation,'repair_contraction':contraction,'repair_forcing':forcing,
       'K6_finite':K6,'K8dual':K8dual,'K8primal':K8primal,'Kdual6':Kd,'Kprimal6':Kp,
       'loss':loss,'amplitude_upper':U,'lower_scalar_coefficient':low,'upper_scalar_margin':high,
       'auxiliary_derivative_lower':jd,'inversion_derivative_lower':fd,'inversion_residual':rem,
       'inversion_wmax':wmax,'Kpoly':Kpoly,'Kminus':km,'Kplus':kp,'minimum_slope_budget':M0}
