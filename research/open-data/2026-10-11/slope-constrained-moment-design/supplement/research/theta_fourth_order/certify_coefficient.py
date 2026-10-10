#!/usr/bin/env python3
"""R24: enclose the true fixed-theta C4, including all switches and matrix error."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
from flint import arb,arb_mat,ctx
from interval_core import restore,pack,rational,zero_ball,upper,absup,pjets,residual_jets,root_contribution
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sm(xs):return sum(xs,arb(0))
def matrix_rows(A):return [[A[i,j] for j in range(A.ncols())] for i in range(A.nrows())]
def nonnegative_interval(upper_bound):
    h=upper_bound/2;return h+zero_ball(h.upper())
def produce():
    assert __debug__;ctx.dps=120
    paths={'R15':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_certificate.json',
           'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
           'R23':HERE.parent/'infinite_slope_fourth_order/manifest.json','algebra':HERE/'results/algebra.json'}
    old=json.loads(paths['R15'].read_text());jets=json.loads(paths['jets'].read_text())
    params=list(map(restore,old['Q_box']));center=list(map(restore,old['dual_center']))
    prior_box=list(map(restore,old['dual_coefficient_box']));prior_radius=restore(old['dual_localization_radius'])
    grad=restore(old['gradient_l1_upper']);m=restore(old['strong_convexity_constant'])
    # Strong convexity and grad D(b*)=0 imply distance <= ||grad D(b0)||_2/m <= grad_l1/m.
    localization_radius=upper(grad/m);assert localization_radius<prior_radius
    box=[v+zero_ball(localization_radius) for v in center]
    assert all(oldb.contains(newb) for oldb,newb in zip(prior_box,box))
    roots=[];rows=[]
    for k,oldrow in enumerate(old['uniform_roots']):
        inherited=restore(oldrow['root_interval']);I=inherited;contractions=[]
        for _ in range(3):
            c=I.mid();fc=residual_jets(pjets(c,params[0]),box)[0]
            derivative=residual_jets(pjets(I,params[0]),box)[1]
            assert not derivative.contains(0)
            radius=upper(abs(fc/derivative));candidate=c+zero_ball(radius)
            if not I.contains(candidate) or not candidate.rad()<I.rad():break
            contractions.append({'input_interval':I,'center':c,'residual':fc,'derivative':derivative,
                                 'radius':radius,'output_interval':candidate})
            I=candidate
        assert contractions
        record=root_contribution(I,params,box,-oldrow['sign_before'])
        assert record['raw_residual_jets'][0].contains(0)
        record['index']=k;record['inherited_root_interval']=inherited;record['contractions']=contractions
        rows.append(record);roots.append(I)
    assert len(rows)==28 and all(roots[k].upper()<roots[k+1].lower() for k in range(27))
    tau,lam,mu=params
    assert 41<tau and tau<42 and -4<lam and lam<0 and 0<mu and mu<9
    assert abs(box[0])<rational('1/1000') and abs(box[1])<rational('1/10') and abs(box[2])<rational('1/200')
    pi=arb.pi();e4=arb(4).exp();assert 3<pi and pi<4 and e4>50
    denominator=1-arb(1)/50**4
    tail={'Gamma':upper(79200*(18-pi*e4).exp()/denominator),
          'G_entry':upper(5*(18-pi*e4).exp()/denominator),
          'B_entry':upper(16400*(22-pi*e4).exp()/denominator),
          'R':upper(182160000*(26-pi*e4).exp()/denominator)}
    gf=sm(r['Gamma'] for r in rows);bf=[sm(r['B'][j] for r in rows) for j in range(3)]
    Gf=[[sm(r['G'][i][j] for r in rows) for j in range(3)] for i in range(3)]
    Rf=sm(r['R'] for r in rows)
    gamma=gf+nonnegative_interval(tail['Gamma'])
    B=arb_mat([[v+zero_ball(tail['B_entry'])] for v in bf])
    G=arb_mat([[Gf[i][j]+(nonnegative_interval(tail['G_entry']) if i==j else zero_ball(tail['G_entry']))
                for j in range(3)] for i in range(3)])
    R=Rf+zero_ball(tail['R'])
    shifted=arb_mat([[G[i,j]-(m if i==j else 0) for j in range(3)] for i in range(3)])
    minors=[arb_mat([[shifted[i,j] for j in range(n)] for i in range(n)]).det() for n in [1,2,3]]
    assert all(x>0 for x in minors)
    inverse=G.inv();C=arb_mat([[inverse[i,j].mid() for j in range(3)] for i in range(3)])
    direct=inverse*B;v0=arb_mat([[direct[i,0].mid()] for i in range(3)])
    assert all(C[i,j].is_exact() for i in range(3) for j in range(3)) and all(v0[i,0].is_exact() for i in range(3))
    E=arb_mat([[arb(i==j)-(C*G)[i,j] for j in range(3)] for i in range(3)])
    eta=upper(max(upper(sm(absup(E[i,j]) for j in range(3))) for i in range(3)))
    assert eta<1
    residual=B-G*v0;pre_residual=C*residual
    forcing=upper(max(absup(pre_residual[i,0]) for i in range(3)))
    v_radius=upper(forcing/(1-eta));v=[v0[i,0]+zero_ball(v_radius) for i in range(3)]
    # The Neumann inequality, not a displayed floating inverse alone, validates the solve.
    P=sm(B[j,0]*v[j] for j in range(3))/2;assert P>0
    Xi=R-P
    f=restore(jets['F_at_exact_Q'][3]);delta=restore(old['delta_star_enclosure']);D=f/delta
    C2=delta**3*gamma/(3*D)
    amplitude_part=delta**5*gamma**2/(3*D*D)
    shape_part=-delta**5*R/D;moment_part=delta**5*P/D
    C4=delta**5*(gamma**2/(3*D*D)-Xi/D)
    assert C4>0 and (C4-amplitude_part-shape_part-moment_part).contains(0)
    assert (C2-restore(old['leading_coefficient'])).contains(0)
    assert (gamma-restore(old['weighted_root_sum'])).contains(0)
    # Formal asymptotic terms at a named budget are not a bound for the actual optimum there.
    Mref=rational('0.00002');formal_C2=C2/Mref**2;formal_C4=C4/Mref**4
    result={'status':'fixed_theta_fourth_order_coefficient_certified_positive','dps':120,
       'input_sha256':{k:sha(p) for k,p in paths.items()},
       'source_sha256':{'certify_coefficient.py':sha(__file__),'interval_core.py':sha(HERE/'interval_core.py')},
       'Q_box':params,'dual_center':center,'prior_dual_radius':prior_radius,'gradient_l1_upper':grad,
       'strong_convexity_constant':m,'improved_dual_radius':localization_radius,'dual_box':box,
       'finite_roots':rows,'tail_start':1,'tail_root_spacing_lower':'3/85','tail_common_log_decay_lower':540,
       'tail_geometric_denominator':denominator,'tail_absolute_bounds':tail,
       'finite_sums':{'Gamma':gf,'G':Gf,'B':bf,'R':Rf},
       'infinite_sums':{'Gamma':gamma,'G':matrix_rows(G),'B':[B[j,0] for j in range(3)],'R':R},
       'shifted_Gram_principal_minors':minors,
       'linear_solve':{'preconditioner':matrix_rows(C),'v0':[v0[i,0] for i in range(3)],
          'error_matrix':matrix_rows(E),'eta':eta,'residual':[residual[i,0] for i in range(3)],
          'preconditioned_residual':[pre_residual[i,0] for i in range(3)],'forcing_upper':forcing,
          'v_radius':v_radius,'v_enclosure':v,'Arb_direct_enclosure':[direct[i,0] for i in range(3)]},
       'coefficients':{'f':f,'delta0':delta,'D':D,'Gamma':gamma,'R':R,'P':P,'Xi':Xi,'C2':C2,'C4':C4,
          'C4_amplitude_part':amplitude_part,'C4_shape_part':shape_part,'C4_moment_part':moment_part,'C4_over_C2':C4/C2},
       'formal_reference_terms':{'M':Mref,'C2_term':formal_C2,'C4_term':formal_C4,
          'ratio_C4_term_to_C2_term':formal_C4/formal_C2,'not_a_finite_M_error_certificate':True},
       'trust_boundary':'Inherited exact Q/b* localization and R23 analytic value theorem; fresh finite-root interval jets, analytic whole-tail bounds and validated matrix solve. Numerical C4 and sign are enclosed. No effective onset, finite-M fourth-order remainder, cusp-uniform theorem or exact finite-M optimizer is supplied.'}
    return pack(result)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=produce();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
    for key in ['Gamma','D','R','P','Xi','C2','C4','C4_over_C2']:print(key,result['coefficients'][key]['enclosure'])
    print('dual radius',result['improved_dual_radius']['enclosure']);print('linear eta',result['linear_solve']['eta']['enclosure'])
    print('tail R',result['tail_absolute_bounds']['R']['enclosure'])
if __name__=='__main__':main()
