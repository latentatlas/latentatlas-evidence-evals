#!/usr/bin/env python3
"""R25: explicit fourth-order error on a closed, finite slope-budget interval."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
from flint import arb,arb_mat,ctx
from jets import jet,pjets,theta_polynomials,sm,restore,pack,rational,zero_ball,upper,absup
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(A):return [[A[i,j] for j in range(A.ncols())] for i in range(A.nrows())]
def poly_mul(a,b):
    c=[arb(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c
def poly_pow(a,n):
    v=[arb(1)]
    for _ in range(n):v=poly_mul(v,a)
    return v
def cover(lo,hi,params,b,sgn,depth=0):
    I=(lo+hi)/2+zero_ball((hi-lo)/2)
    p=pjets(I,params[0],0);v=p[3][0]-sm(b[j]*p[j][0] for j in range(3))
    if sgn*v>0:return [{'lo':lo,'hi':hi,'sign':sgn,'raw_residual':v}]
    assert depth<30,'Failed finite root-complement sign cover'
    mid=(lo+hi)/2
    return cover(lo,mid,params,b,sgn,depth+1)+cover(mid,hi,params,b,sgn,depth+1)
def produce():
    assert __debug__;ctx.dps=120
    source=HERE.parent/'theta_fourth_order/results/certificate.json';old=json.loads(source.read_text())
    params=list(map(restore,old['Q_box']));b=list(map(restore,old['dual_box']))
    assert 41<params[0] and params[0]<42 and -4<params[1] and params[1]<0 and 0<params[2] and params[2]<9
    v=list(map(restore,old['linear_solve']['v_enclosure']));va=list(map(absup,v))
    co={k:restore(val) for k,val in old['coefficients'].items()}
    tails={k:restore(val) for k,val in old['tail_absolute_bounds'].items()}
    amin=arb(2)**-22;a0=arb(2)**-14;rho=rational('1/4000');Mlo=rational('0.00002');Mhi=rational('0.002')
    expanded=[x+zero_ball(upper(va[j]*a0*a0)) for j,x in enumerate(b)]
    local=[];Kstar=arb(0);Hm=[arb(0)]*3
    for k,row in enumerate(old['finite_roots']):
        z=restore(row['root_interval']);sig=row['orientation'];at=jet(z,params,b,root=True)
        q=at['moment_jets'];r=at['residual_jets'];kap=(sm(q[j][0]*v[j] for j in range(3))-r[2]/6)/r[1];ka=absup(kap)
        I=z+zero_ball(rho);near=jet(I,params,b);trial=jet(I,params,expanded)
        Q=[[absup(x) for x in rowj] for rowj in near['moment_jets']];R=list(map(absup,near['residual_jets']))
        m=(sig*trial['residual_jets'][1]).lower();L=absup(trial['residual_jets'][1]);assert m>0,(k,m)
        moment=[]
        for j in range(3):
            h=upper(absup(q[j][1])*ka**2+absup(q[j][2])*(ka+ka**3*a0**2)/3
                    +Q[j][3]*(rational('1/5')+2*ka**2*a0**2+ka**4*a0**4)/12)
            moment.append(h);Hm[j]+=h
        ks=upper(absup(r[2])*ka**3/3+absup(r[3])*(2*ka**2+ka**4*a0**2)/12
              +absup(r[4])*(ka+rational('10/3')*ka**3*a0**2+ka**5*a0**4)/60
              +R[5]*(rational('1/7')+3*ka**2*a0**2+5*ka**4*a0**4+ka**6*a0**6)/360)
        Kstar+=ks
        hb=upper(absup(r[2])*ka**2/2+absup(r[3])*(ka+ka**3*a0**2)/6
                 +R[4]*(rational('1/5')+2*ka**2*a0**2+ka**4*a0**4)/24
                 +sm(va[j]*(absup(q[j][1])*ka+Q[j][2]*(rational('1/3')+ka**2*a0**2)/2) for j in range(3)))
        shift=upper(hb*a0**4/m)
        assert ka*a0<1 and ka*a0*a0+shift+a0<rho
        local.append({'index':k,'orientation':sig,'root':z,'kappa':kap,'kappa_abs':ka,'root_jets':at,
          'neighborhood':I,'neighborhood_jets':near,'trial_neighborhood_jets':trial,'Q_abs':Q,'R_abs':R,
          'trial_derivative_lower':m,'trial_derivative_abs_upper':L,'moment_fourth_bound':moment,
          'residual_sixth_bound':ks,'balance_fourth_bound':hb,'balanced_center_distance_upper':shift})
    # All 28 finite roots of every trial residual, including their complements.
    leaves=[];left=arb(0);sign=-local[0]['orientation']
    for row in local:
        lo,hi=row['neighborhood'].lower(),row['neighborhood'].upper()
        assert left<lo
        leaves+=cover(left,lo,params,expanded,sign)
        assert row['orientation']==-sign
        for x,s in [(lo,sign),(hi,-sign)]:
            p=pjets(x,params[0],0);assert s*(p[3][0]-sm(expanded[j]*p[j][0] for j in range(3)))>0
        left=hi;sign=-sign
    leaves+=cover(left,arb(1),params,expanded,sign)
    # Integrated tail: each |q_j| <= 88*2^j*u^j*exp(9u+9u^4-pi*exp(4u)), log derivative < -540.
    tail_base=upper(88*(18-arb.pi()*arb(4).exp()).exp()/540)
    tail_q=[upper(2**j*tail_base) for j in range(4)]
    tail_objective=upper(2*(tail_q[3]+sm(absup(expanded[j])*tail_q[j] for j in range(3))))
    lead_tail=upper(tails['B_entry']+tails['G_entry']*sm(va))
    Hm0=list(map(upper,Hm));Hm=[upper(Hm[j]+lead_tail/amin**2+2*tail_q[j]/amin**4) for j in range(3)]
    J=arb_mat([[-2*local[k]['orientation']*local[k]['root_jets']['moment_jets'][j][0] for k in range(3)] for j in range(3)])
    ji=J.inv();C=arb_mat([[ji[i,j].mid() for j in range(3)] for i in range(3)])
    E=arb_mat([[arb(i==j)-(C*J)[i,j] for j in range(3)] for i in range(3)])
    force=[upper(sm(absup(C[i,j])*Hm[j] for j in range(3))) for i in range(3)]
    W=[]
    for x in force:
        n=arb(1)
        while n<2*x:n*=2
        W.append(n)
    variation=[[upper(2*(local[k]['Q_abs'][j][1]*(local[k]['kappa_abs']*a0**2+W[k]*a0**4)
                       +local[k]['Q_abs'][j][2]*a0**2/6)) for k in range(3)] for j in range(3)]
    contraction=[upper(sm((absup(E[i,k])+sm(absup(C[i,j])*variation[j][k] for j in range(3)))*W[k]/W[i] for k in range(3))) for i in range(3)]
    forcing=[upper(force[i]/W[i]) for i in range(3)]
    assert all(contraction[i]+forcing[i]<1 for i in range(3)),(contraction,forcing)
    assert all(local[k]['kappa_abs']*a0**2+W[k]*a0**4+a0<rho for k in range(3))
    K6=upper(Kstar+sm(va[j]*Hm0[j] for j in range(3)))
    K8dual=upper(sm(row['balance_fourth_bound']**2/row['trial_derivative_lower'] for row in local))
    K8primal=upper(sm(2*local[k]['balance_fourth_bound']*W[k]+local[k]['trial_derivative_abs_upper']*W[k]**2 for k in range(3)))
    Xi_tail=upper(tails['R']+tails['G_entry']*sm(va)**2/2+tails['B_entry']*sm(va))
    tail_as_sixth=upper(tails['Gamma']/(3*amin**4)+Xi_tail/amin**2+tail_objective/amin**6)
    Kdual=upper(K6+K8dual*a0**2+tail_as_sixth);Kprimal=upper(K6+K8primal*a0**2+tail_as_sixth)
    f,delta,D,Gamma,Xi=[co[k] for k in ['f','delta0','D','Gamma','Xi']]
    assert Xi>0
    loss=upper(Gamma*a0**2/3+absup(Xi)*a0**4+Kprimal*a0**6)
    Ubar=upper(delta.upper()/(1-loss/D.lower()))
    assert loss<D.lower() and Ubar<1
    assert Ubar/a0<Mlo and delta.lower()/amin>Mhi
    assert Ubar/Mlo<a0 and delta.lower()/Mhi>amin
    t=Gamma/(3*D);ee=Xi/D;cc=3*t*t-ee
    p=[arb(1),t,cc];p3=poly_pow(p,3);p5=poly_pow(p,5)
    residual=[arb(0)]*13
    for i,x in enumerate(p):residual[i]+=x
    residual[0]-=1
    for i,x in enumerate(p3):residual[i+1]-=t*x
    for i,x in enumerate(p5):residual[i+2]+=ee*x
    assert all(x.contains(0) for x in residual[:3])
    wmax=upper(delta**2/Mlo**2)
    scalar_remainder=upper(sm(absup(x)*wmax**(n-3) for n,x in enumerate(residual) if n>=3))
    Kpoly=upper(f*delta**6*scalar_remainder)
    derivative_lower=(D.lower()-Gamma.upper()*Ubar**2/Mlo**2).lower();assert derivative_lower>0
    assert delta.upper()+co['C2'].upper()/Mlo**2+co['C4'].upper()/Mlo**4<Ubar
    Kminus=upper((Kpoly+Kdual*Ubar**7)/derivative_lower)
    Kplus=upper((Kpoly+Kprimal*Ubar**7)/derivative_lower)
    summary={'Kminus':Kminus,'Kplus':Kplus,'relative_to_C4_at_Mlo_lower':upper(Kminus/(co['C4'].lower()*Mlo**2)),
             'relative_to_C4_at_Mlo_upper':upper(Kplus/(co['C4'].lower()*Mlo**2))}
    return pack({'status':'R25_finite_window_effective_fourth_order_bounds','dps':120,
       'source_sha256':{p.name:sha(p) for p in [Path(__file__),HERE/'jets.py']},'R24_certificate_sha256':sha(source),
       'Q_box':params,'dual_box':b,'v_enclosure':v,'coefficient_inputs':co,'tail_coefficient_inputs':tails,
       'minimum_half_width':amin,'maximum_half_width':a0,'neighborhood_radius':rho,'budget_interval':[Mlo,Mhi],
       'expanded_trial_dual_box':expanded,'theta_derivative_polynomials':theta_polynomials(5),'local':local,
       'sign_cover':leaves,'tail_q_integrals':tail_q,'tail_objective_bound':tail_objective,
       'tail_moment_leading_bound':lead_tail,'moment_fourth_bounds_finite':Hm0,'moment_forcing_bounds':Hm,
       'moment_jacobian':rows(J),'moment_preconditioner':rows(C),'moment_preconditioner_error':rows(E),
       'repair_scaled_box':W,'moment_jacobian_variation':variation,'repair_contraction':contraction,'repair_forcing':forcing,
       'Kstar6':upper(Kstar),'K6_finite':K6,'K8dual':K8dual,'K8primal':K8primal,'Xi_tail_bound':Xi_tail,
       'tail_as_sixth_bound':tail_as_sixth,'Kdual6':Kdual,'Kprimal6':Kprimal,'maximum_loss':loss,'amplitude_upper':Ubar,
       'inversion_t':t,'inversion_e':ee,'inversion_c':cc,'inversion_residual_coefficients':residual,
       'inversion_w_max':wmax,'inversion_scalar_remainder':scalar_remainder,'Kpoly':Kpoly,
       'inversion_derivative_lower':derivative_lower,'result':summary,
       'scope':'Finite interval 2e-5 <= M <= 2e-3 only. Exact Q,b*,delta0,C2,C4. No all-M O(M^-6) asymptotic claim. Analytic proof and local derivative/tail bounds are explicit dependencies.'})
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    d=produce();a.output.write_text(json.dumps(d,indent=2)+'\n')
    print(d['status']);print('sign leaves',len(d['sign_cover']))
    for k in ['K6_finite','K8dual','K8primal','Kdual6','Kprimal6','tail_as_sixth_bound']:print(k,d[k]['enclosure'])
    print('result', {k:v['enclosure'] for k,v in d['result'].items()})
    print('repair', [x['enclosure'] for x in d['repair_contraction']])
if __name__=='__main__':main()
