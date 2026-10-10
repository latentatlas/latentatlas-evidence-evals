#!/usr/bin/env python3
"""Independent rational implications of the R16 derivative certificate."""
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
def contains(a,b):return a.lo<=b.lo<=b.hi<=a.hi
def power(v,n):
    ans=I(1)
    for _ in range(n):ans=ans*v
    return ans
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    cp=HERE/'results/remainder_certificate.json';c=json.loads(cp.read_text())
    paths={'R15':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_certificate.json',
        'R15_check':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_check.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json'}
    for k,p in paths.items():assert c['input_sha256'][k]==sha(p),k
    for k,v in c['source_sha256'].items():assert sha(HERE/k)==v,k
    data={k:json.loads(p.read_text()) for k,p in paths.items()};old=data['R15']
    a0=exact(c['maximum_transition_half_width']);assert a0==Q(2)**-14
    M0=Q('0.00002');assert restore(c['minimum_slope_budget']).lo<=M0<=restore(c['minimum_slope_budget']).hi
    V=list(map(exact,c['scaled_center_bounds']));assert V==[512,768,384]
    # Restoring an Arb radius may round it outward by one magnitude ulp.
    # Enclosure containment is the required mathematical identity guard.
    for key in ['Q_box','dual_coefficient_box']:
        assert all(contains(restore(v),restore(b)) for v,b in zip(c[key],old[key]))
    x=list(map(restore,c['Q_box']));assert 41<x[0].lo<x[0].hi<42 and -4<x[1].lo<x[1].hi<0 and 0<x[2].lo<x[2].hi<9
    caps=[Q(1,1000),Q(1,10),Q(1,200)]
    assert all(absup(restore(v))<cap for v,cap in zip(c['dual_coefficient_box'],caps))
    C0,C1,C2=map(restore,c['tail_kernel_constants']);W=[C0,C1+44*C0,C2+88*C1+2052*C0]
    assert all(overlap(a,restore(b)) for a,b in zip(W,c['tail_weight_constants']))
    for j,row in enumerate(c['tail_moment_derivative_constants']):
        constants=[2**j*W[0],2**j*(W[1]+(j+84)*W[0]),2**j*(W[2]+2*(j+84)*W[1]+(j*(j-1)+168*j+7056)*W[0])]
        assert all(overlap(a,restore(b)) for a,b in zip(constants,row))
    assert exact(c['tail_start'])==1-a0>Q(3,4) and restore(c['tail_decay']).lo*Q(3,85)>16
    assert sum(Q(4**k,factorial(k)) for k in range(8))>50
    # Positive tails are accepted transcendental-envelope bounds. Reconstruct
    # their use in all finite sums with separate rational endpoints.
    tail=[[exact(v) for v in row] for row in c['tail_moment_derivative_sums']]
    tr=tail[3][2]+sum(cap*tail[j][2] for j,cap in enumerate(caps))
    assert tr<=exact(c['tail_residual_second_derivative_sum'])
    loc=c['local_derivative_enclosures'];cent=c['center_derivative_enclosures'];assert len(loc)==len(cent)==28
    q2=[Q(0)]*3;B2=Q(0);F=[I(0)]*3;J=[[I(0) for k in range(3)] for j in range(3)]
    boxes=[]
    for k,(row,root) in enumerate(zip(loc,old['uniform_roots'])):
        assert row['index']==k and row['jump']==-2*(-1)**k and contains(restore(row['root_interval']),restore(root['root_interval']))
        shift=a0*a0*V[k] if k<3 else Q(0);assert exact(row['shift_radius'])==shift
        box=restore(row['interval']);z=restore(row['root_interval']);assert box.lo<=z.lo-a0-shift and box.hi>=z.hi+a0+shift
        boxes.append(box)
        assert contains(restore(cent[k]['interval']),restore(root['root_interval']))
        for record in [row,cent[k]]:
            jets=[[restore(v) for v in line] for line in record['moment_jets']]
            aa=list(map(restore,c['dual_coefficient_box']))
            for l in range(3):
                qr=jets[3][l]-sum((aa[j]*jets[j][l] for j in range(3)),I(0))
                assert overlap(qr,restore(record['residual_density_jets'][l]))
        for j in range(3):
            q2[j]+=absup(restore(row['moment_jets'][j][2]));F[j]=F[j]+row['jump']*restore(cent[k]['moment_jets'][j][1])/6
            if k<3:J[j][k]=-row['jump']*restore(cent[k]['moment_jets'][j][0])
        B2+=absup(restore(row['residual_density_jets'][2]))
    q2=[q2[j]+tail[j][2] for j in range(3)];B2+=exact(c['tail_residual_second_derivative_sum'])
    assert all(v<=exact(b) for v,b in zip(q2,c['moment_second_derivative_sums'])) and B2<=exact(c['residual_second_derivative_sum'])
    F=[v+I(-tail[j][1]/3,tail[j][1]/3) for j,v in enumerate(F)]
    assert all(overlap(v,restore(b)) for v,b in zip(F,c['center_forcing']))
    assert determinant(J).nonzero()
    B=[list(map(exact,row)) for row in c['preconditioner']]
    error=[[I(int(i==k))-sum((B[i][j]*J[j][k] for j in range(3)),I(0)) for k in range(3)] for i in range(3)]
    forcing=[sum((B[i][j]*F[j] for j in range(3)),I(0)) for i in range(3)]
    variation=[[2*a0*a0*(V[k]*absup(restore(loc[k]['moment_jets'][j][1]))+absup(restore(loc[k]['moment_jets'][j][2]))/6) for k in range(3)] for j in range(3)]
    kappas=[];etas=[]
    for i in range(3):
        kap=sum((absup(error[i][k])+sum(abs(B[i][j])*variation[j][k] for j in range(3)))*V[k] for k in range(3))/V[i]
        eta=(absup(forcing[i])+a0*sum(abs(B[i][j])*q2[j] for j in range(3))/12)/V[i]
        assert kap<1 and kap+eta<1;kappas.append(kap);etas.append(eta)
    assert boxes[0].lo>0 and all(a.hi<b.lo for a,b in zip(boxes[:-1],boxes[1:]))
    assert boxes[-1].hi<1-a0 and 2*a0<Q(3,85)
    A3=B2/12;A4=sum(absup(restore(loc[k]['residual_density_jets'][1]))*V[k]**2+absup(restore(loc[k]['residual_density_jets'][2]))*V[k]/3 for k in range(3))
    assert A3<=exact(c['A3']) and A4<=exact(c['A4'])
    L=Q('0.00000000091787079603827');U=Q('0.00000000091787079608363')
    f3=restore(data['jets']['F_at_exact_Q'][3]);G=restore(old['weighted_root_sum']).hi;Dlow=f3.lo/U
    Emax=G*a0*a0/3+A3*a0**3+A4*a0**4;assert 0<Emax<Dlow
    Ubar=U/(1-Emax/Dlow);assert Ubar/a0<M0 and Ubar<1
    CU=Q('9.20340375e-25');CL=Q('9.20340371e-25');denom=Dlow-G*Ubar**2/M0**2;assert denom>0
    Km=U**5*B2/(12*f3.lo)
    Kp=(A3*Ubar**4+(A4*Ubar**5+G*Ubar**2*CU)/M0)/denom
    km=Q('9.624e-33');kp=Q('2.167e-32');assert Km<km and Kp<kp
    relative=max(km,kp)/(CL*M0);assert relative<Q('0.001178')
    table=[]
    for factor in [1,2,4,8]:
        M=M0*factor;lower_excess=CL/M**2-km/M**3;upper_excess=CU/M**2+kp/M**3
        assert lower_excess>0
        lower=L+lower_excess;upper=U+upper_excess
        table.append(dict(M=str(M),budget_factor=factor,
            excess_bracket=[decimal(lower_excess,30),decimal(upper_excess,30,True)],
            total_threshold_bracket=[decimal(lower,26),decimal(upper,26,True)],
            relative_excess_ppm_bracket=[decimal(lower_excess/U*10**6,9),decimal(upper_excess/L*10**6,9,True)],
            relative_approximation_error_upper=decimal(relative/factor,12,True)))
    oldwidth=Q('0.000000000917876530')-Q('0.000000000917873080')
    newwidth=Q(table[0]['total_threshold_bracket'][1])-Q(table[0]['total_threshold_bracket'][0])
    assert oldwidth/newwidth>870
    out=dict(status='independent_rational_uniform_remainder_passed',certificate_sha256=sha(cp),source_sha256=sha(__file__),
        minimum_slope_budget='0.00002',maximum_transition_half_width=str(a0),
        contraction_constants_upper=[decimal(v,16,True) for v in kappas],selfmap_center_constants_upper=[decimal(v,16,True) for v in etas],
        residual_second_derivative_sum_upper=decimal(B2,16,True),A3_upper=decimal(A3,16,True),A4_upper=decimal(A4,12,True),
        lower_remainder_constant_readable='9.624e-33',upper_remainder_constant_readable='2.167e-32',
        relative_error_upper_at_minimum_budget='0.001178',coefficient_bracket=['9.20340371e-25','9.20340375e-25'],
        certified_budget_examples=table,threshold_width_improvement_factor_lower=decimal(oldwidth/newwidth,3),
        trust_boundary='Local theta/moment derivative and infinite-tail envelopes, exact-Q and R15 optimizer identities accepted as inputs. Rational reconstruction checks the contraction, dual loss constants, absorption and displayed bounds. Does not formalize the analytic fixed-point/remainder proof.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status']);print('Kminus, Kplus',out['lower_remainder_constant_readable'],out['upper_remainder_constant_readable'])
    print('M0 threshold',table[0]['total_threshold_bracket'],'error upper',out['relative_error_upper_at_minimum_budget'])
if __name__=='__main__':main()
