#!/usr/bin/env python3
"""R15 rational reconstruction; accepts local transcendental balls as inputs."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'kernel_design_principle'))
from check_candidate import I,restore,determinant,decimal
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(v):
    m,e=v['mid_man_exp'];r,f=v['rad_man_exp'];assert r==0
    return Q(m)*Q(2)**e
def absup(v):return max(abs(v.lo),abs(v.hi))
def overlap(a,b):return max(a.lo,b.lo)<=min(a.hi,b.hi)
def enclosing(v,a,b):assert v.lo<=a<=b<=v.hi
def power(v,n):
    ans=I(1)
    for _ in range(n):ans=ans*v
    return ans

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists();cp=HERE/'results/asymptotic_certificate.json';c=json.loads(cp.read_text())
    paths={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
        'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
        'R14':HERE.parent/'kernel_slope_threshold/results/slope_threshold_certificate.json'}
    for k,p in paths.items():assert c['input_sha256'][k]==sha(p),k
    for k,v in c['source_sha256'].items():assert sha(HERE/k)==v,k
    data={k:json.loads(p.read_text()) for k,p in paths.items()};old=data['R12'];q=data['Q']
    center=list(map(exact,q['center_exact_dyadic']));qr=restore(q['root_radius']).hi
    for v,b in zip(c['Q_box'],center):enclosing(restore(v),b-qr,b+qr)
    a0=list(map(exact,old['a']));assert a0==list(map(exact,c['dual_center']))
    R=exact(c['dual_localization_radius']);assert R==Q(2)**-40
    for v,b in zip(c['dual_coefficient_box'],a0):enclosing(restore(v),b-R,b+R)
    knots=list(map(exact,old['breakpoints']));beta=exact(old['zero_box_radius']);coarse=Q(2)**-24
    assert len(knots)==len(c['central_root_contractions'])==len(c['uniform_roots'])==28
    displacements=[]
    for k,row in enumerate(c['central_root_contractions']):
        assert row['index']==k;dr=restore(row['derivative_on_old_box']);assert dr.nonzero()
        image=I(knots[k])-restore(row['residual_at_old_knot'])/dr
        assert overlap(image,restore(row['newton_image']))
        bound=exact(row['displacement_upper']);assert absup(image-I(knots[k]))<=bound<beta
        displacements.append(bound)
    gradient=[]
    for n,row in enumerate(c['gradient_rows']):
        assert row['order']==n
        errors=[2*displacements[k]*exact(old['root_boxes'][k]['rho_upper'])*(2*(knots[k]+beta))**n for k in range(28)]
        assert all(e<=exact(b) for e,b in zip(errors,row['root_errors']))
        value=absup(restore(old['step_moments_at_exact_Q'][n]))+sum(errors)+exact(row['tail_error'])
        assert value<=exact(row['absolute_gradient_upper']);gradient.append(value)
    grad=sum(gradient);assert grad<=exact(c['gradient_l1_upper'])
    # Uniform finite root isolation and Newton-image containment.
    H=[[I(0) for j in range(3)] for i in range(3)];gamma=I(0);loss=Q(0);p3=[];root_intervals=[];expanded=[]
    for k,row in enumerate(c['uniform_roots']):
        assert row['index']==k and exact(row['old_knot'])==knots[k] and row['sign_before']==(-1)**k
        assert exact(row['coarse_left'])==knots[k]-coarse and exact(row['coarse_right'])==knots[k]+coarse
        assert restore(row['coarse_derivative']).nonzero()
        ends=list(map(restore,row['coarse_endpoints']));assert ((-1)**k*ends[0]).lo>0 and ((-1)**k*ends[1]).hi<0
        rad=coarse
        assert len(row['contractions'])>=1
        for contract in row['contractions']:
            assert exact(contract['input_radius'])==rad
            derivative=restore(contract['derivative']);assert derivative.nonzero()
            bound=absup(restore(contract['residual_at_center'])/derivative)
            new=exact(contract['output_radius']);assert bound<=new<rad;rad=new
        assert exact(row['root_radius'])==rad
        stop=row['stopped_proposal']
        if stop is not None:assert exact(stop['input_radius'])==rad<=exact(stop['proposed_radius'])
        box=restore(row['root_interval']);enclosing(box,knots[k]-rad,knots[k]+rad);root_intervals.append(box)
        derivative=restore(row['residual_derivative']).absolute();assert derivative.lo>0
        density=restore(row['full_density']);first=restore(row['first_density']);assert density.lo>0 and first.lo>0
        p=list(map(restore,row['p_values']));assert len(p)==9
        for i in range(3):
            for j in range(3):H[i][j]=H[i][j]+2*first*p[i]*p[j]/derivative
        if k<3:p3.append(p[:3])
        contribution=density*derivative;assert overlap(contribution,restore(row['gamma_contribution']));gamma=gamma+contribution
        expanded_box=restore(row['expanded_interval']);enclosing(expanded_box,knots[k]-rad-Q(2)**-14,knots[k]+rad+Q(2)**-14)
        assert expanded_box.lo>0;expanded.append(expanded_box)
        lo=restore(row['expanded_density']).lo*restore(row['expanded_derivative']).absolute().lo
        stored=restore(row['loss_coefficient_lower']);assert lo>0
        enclosing(stored,lo,lo);loss+=stored.lo
    # Sign leaves and isolated root boxes form an unbroken partition of [0,1].
    pieces=[]
    for row in c['uniform_sign_cover']:
        left,right=exact(row['left']),exact(row['right']);assert left<right
        crossings=sum(b+coarse<=left for b in knots);assert row['sign']==(-1)**crossings
        if row['method']=='range':assert (row['sign']*restore(row['residual'])).lo>0
        else:
            assert row['method']=='monotone' and restore(row['derivative']).nonzero()
            assert all((row['sign']*restore(v)).lo>0 for v in row['endpoints'])
        pieces.append((left,right))
    pieces+= [(b-coarse,b+coarse) for b in knots];pieces.sort()
    assert pieces[0][0]==0 and pieces[-1][1]==1 and all(a[1]==b[0] for a,b in zip(pieces[:-1],pieces[1:]))
    m=Q(1,200);enclosing(restore(c['strong_convexity_constant']),m,m)
    B=[[H[i][j]-(m if i==j else 0) for j in range(3)] for i in range(3)]
    minors=[determinant([row[:n] for row in B[:n]]) for n in [1,2,3]]
    assert all(v.lo>0 for v in minors) and m*R>2*grad
    det=determinant(p3);assert det.nonzero() and overlap(det,restore(c['first_three_evaluation_determinant']))
    # Independent rational tail inequalities; transcendental W(1), margin are inputs.
    assert all(absup(restore(v))<cap for v,cap in zip(c['dual_coefficient_box'],[Q(1,1000),Q(1,10),Q(1,200)]))
    t=restore(c['Q_box'][0]);assert 41<t.lo<t.hi<42
    numerator=Q(32,200)+Q(8,10*200)+Q(24,1000)+Q(2,1000*10)
    assert numerator/49<Q(1,200);enclosing(restore(c['tail_phase_derivative_numerator_bound']),numerator,numerator)
    assert c['tail_phase_derivative_range']==[81,85]
    spacing=Q(1,200)
    assert 2*root_intervals[0].lo>spacing and all(b.lo-a.hi>spacing for a,b in zip(root_intervals[:-1],root_intervals[1:]))
    assert 1-root_intervals[-1].hi>spacing and Q(3,85)>spacing
    assert restore(c['tail_weight_decay_lower']).lo*Q(3,85)>16
    assert sum(Q(4**k,factorial(k)) for k in range(8))>50
    tail=exact(c['tail_weight_at_one_upper'])/(1-Q(1,50**4))
    assert tail<=exact(c['weighted_root_sum_tail_upper'])
    Gamma=gamma+I(0,tail) # Positive tail: tighter than the producer's symmetric enclosure.
    assert overlap(Gamma,restore(c['weighted_root_sum']))
    L=Q('0.00000000091787079603827');U=Q('0.00000000091787079608363')
    assert restore(old['minimum_norm_lower_bound']).lo>L and restore(old['feasible_norm_upper_enclosure']).hi<U
    delta=I(L,U);f=list(map(restore,data['jets']['F_at_exact_Q']))[:9];assert f[3].lo>0
    C=power(delta,4)*Gamma/(3*f[3]);Crel=power(delta,3)*Gamma/(3*f[3]);assert C.lo>0
    assert overlap(C,restore(c['leading_coefficient'])) and overlap(Crel,restore(c['relative_leading_coefficient']))
    assert Q('9.20340371e-25')<C.lo<C.hi<Q('9.20340375e-25')
    assert Q('1.297542117')<Gamma.lo<Gamma.hi<Q('1.297542121')
    assert Q('1.002690547e-15')<Crel.lo<Crel.hi<Q('1.002690552e-15')
    # Uniform positive lower excess relative to the TRUE optimum, all M>=2e-5.
    assert c['finite_budget_lower_valid_for_M_at_least']=='0.00002' and L/Q('0.00002')<Q(2)**-14
    assert all(a.hi<b.lo for a,b in zip(expanded[:-1],expanded[1:]))
    Cfinite=loss*L**4/(3*f[3].hi);CfiniteRel=loss*L**3/(3*f[3].hi)
    assert Q('9.13976214e-25')<Cfinite
    # Limiting geometric rank: no finite-M optimizer shape or uniqueness claim.
    S=list(map(restore,c['limiting_sign_moments']));g=[f[n]-delta*S[n] for n in range(9)]
    assert all(v.lo<=0<=v.hi for v in g[:4]);g[:4]=[I(0)]*4
    matrix=[[-g[n+2]/4,g[n+4]/16,-g[n+6]/64] for n in range(3)]
    rank=determinant(matrix);reduced=g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    assert g[4].hi<0 and rank.hi<0 and reduced.hi<0 and overlap(rank,reduced)
    out=dict(status='independent_rational_asymptotic_hypotheses_passed',certificate_sha256=sha(cp),source_sha256=sha(__file__),
        gradient_l1_upper=decimal(grad,35,True),localization_margin_lower=decimal(m*R-2*grad,35),
        strong_convexity_minors=[v.pair() for v in minors],switch_determinant=det.pair(),
        root_count_on_unit_interval=28,sign_cover_leaves=len(c['uniform_sign_cover']),
        gamma_readable_bracket=['1.297542117','1.297542121'],
        coefficient_readable_bracket=['9.20340371e-25','9.20340375e-25'],
        relative_coefficient_readable_bracket=['1.002690547e-15','1.002690552e-15'],
        reconstructed_coefficient=C.pair(),reconstructed_gamma=Gamma.pair(),
        finite_budget_absolute_constant_lower='9.13976214e-25',
        finite_budget_relative_constant_lower=decimal(CfiniteRel,28),limiting_control_determinant=rank.pair(),
        trust_boundary='Root-function, density, trigonometric, exponential and inherited moment/tail enclosures accepted as inputs. Rational check reconstructs contractions, coverage, positive curvature, localization, coefficients, finite lower and rank. Analytic asymptotic proof remains separate.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status']);print('C bracket',out['coefficient_readable_bracket']);print('finite lower C',out['finite_budget_absolute_constant_lower'])
if __name__=='__main__':main()
