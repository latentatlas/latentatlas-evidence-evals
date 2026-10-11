#!/usr/bin/env python3
"""Separate outward-rational reconstruction with automatic differentiation."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'theta_fourth_order'))
from rational_intervals import RI,restore,mm,mv,BITS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def unbox(x):
    if isinstance(x,dict):
        if 'mid_man_exp' in x:return restore(x)
        return {k:unbox(v) for k,v in x.items()}
    if isinstance(x,list):return [unbox(v) for v in x]
    return x
def sm(xs):return sum(xs,RI(0))
def sym(x):return RI(-x,x)
class AD:
    def __init__(self,v,d=0):
        if isinstance(v,AD):self.v,self.d=v.v,v.d
        else:self.v,self.d=RI(v),RI(d)
    def __add__(self,o):
        o=AD(o);return AD(self.v+o.v,self.d+o.d)
    __radd__=__add__
    def __neg__(self):return AD(-self.v,-self.d)
    def __sub__(self,o):return self+-AD(o)
    def __rsub__(self,o):return AD(o)+-self
    def __mul__(self,o):
        o=AD(o);return AD(self.v*o.v,self.d*o.v+self.v*o.d)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=AD(o);return AD(self.v/o.v,(self.d*o.v-self.v*o.d)/o.v**2)
    def __rtruediv__(self,o):return AD(o)/self
    def __pow__(self,n):
        return AD(self.v**n,n*self.v**(n-1)*self.d) if n else AD(1)
def motion_check(data,parent):
    c,p=unbox(data),unbox(parent);co=p['coefficients'];arc=p['arc'];b=p['dual']['tight_box'];vel=arc['refined_velocity'];checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append(name)
    B=arc['positive_moment_bounds'];offs=[x.abs_upper() for x in arc['offsets']];S=[]
    for row in c['sign_transport']:
        n=row['order'];err=(offs[0]*B[n+1]+offs[1]*B[n+2]/4+offs[2]*B[n+4]/16+offs[3]*B[n+6]/64
                           +sm(row['root_motion_terms'])+row['whole_sign_tail']).hi
        S.append(row['base_template_moment']+sym(err));ck('sign_transport_'+str(n),err>0)
    S[:3]=[RI(0)]*3;S[3]=co['D']
    def partial(q,j):return vel[0]*q[j+1]-vel[1]*q[j+2]/4+vel[2]*q[j+4]/16-q[j+6]/64
    Sd=[partial(S,j) for j in range(4)];rhs=Sd[:3];tail=c['tail_derivative_bounds']
    for row in c['root_derivatives']:
        at=row['jets'];q=at['moment_jets_extended'];pp=at['p_jets_extended'];r=at['residual_jets'];sig=row['orientation']
        ck('simple_root_'+str(row['index']),(sig*r[1]).lo>0)
        h=vel[0]*at['weight_jets'][0]*(pp[4][0]-sm(b[j]*pp[j+1][0] for j in range(3)))
        rhs=[rhs[j]+2*q[j][0]*h/(sig*r[1]) for j in range(3)]
    rhs=[x+sym(tail['dual_rhs'].hi) for x in rhs]
    sol=c['dual_derivative_solve'];A=co['G'];C=sol['preconditioner'];v0=sol['seed'];CG=mm(C,A)
    E=[[RI(i==j)-CG[i][j] for j in range(3)] for i in range(3)];eta=max(sum(x.abs_upper() for x in row) for row in E)
    ck('implicit_dual_solve',eta<1);forcing=max(x.abs_upper() for x in mv(C,[rhs[i]-mv(A,v0)[i] for i in range(3)]))
    bp=[v0[i]+sym(forcing/(1-eta)) for i in range(3)]
    for j in range(3):ck('tail_bprime_bound_'+str(j),bp[j].abs_upper()<10)
    Gamma=AD(0);GG=[[AD(0) for j in range(3)] for i in range(3)];BB=[AD(0) for _ in range(3)];RR=AD(0)
    for row in c['root_derivatives']:
        at=row['jets'];q=at['moment_jets_extended'];pp=at['p_jets_extended'];r=at['residual_jets'];sig=row['orientation']
        zp=(sm(bp[j]*pp[j][0] for j in range(3))-vel[0]*(pp[4][0]-sm(b[j]*pp[j+1][0] for j in range(3))))/(pp[3][1]-sm(b[j]*pp[j][1] for j in range(3)))
        qd=[[partial([q[n][l] for n in range(10)],j) for l in range(4)] for j in range(4)]
        # Forward AD differentiates the coefficient formulas instead of
        # reusing the producer's explicit quotient derivatives.
        qr=[AD(r[l],qd[3][l]-sm(b[j]*qd[j][l]+bp[j]*q[j][l] for j in range(3))+r[l+1]*zp) for l in range(4)]
        Q=[[AD(q[j][l],qd[j][l]+q[j][l+1]*zp) for l in range(2)] for j in range(3)]
        gam=sig*qr[1];Gamma+=gam
        for j in range(3):BB[j]+=sig*(Q[j][0]*qr[2]/qr[1]-Q[j][1])/3
        for i in range(3):
            for j in range(3):GG[i][j]+=2*Q[i][0]*Q[j][0]/gam
        RR+=qr[2]**2/(36*gam)-sig*qr[3]/60
    old=unbox(json.loads((HERE.parent/'theta_fourth_order/results/certificate.json').read_text()))['tail_absolute_bounds']
    Gamma+=AD(RI(0,old['Gamma'].hi),sym(tail['Gamma_prime'].hi))
    for j in range(3):BB[j]+=AD(sym(old['B_entry'].hi),sym(tail['B_prime_entry'].hi))
    for i in range(3):
        for j in range(3):GG[i][j]+=AD(RI(0,old['G_entry'].hi) if i==j else sym(old['G_entry'].hi),sym(tail['G_prime_entry'].hi))
    RR+=AD(sym(old['R'].hi),sym(tail['R_prime'].hi))
    v=co['v']
    stationary_energy=sum((BB[j]*v[j] for j in range(3)),AD(0))-sum((GG[i][j]*v[i]*v[j] for i in range(3) for j in range(3)),AD(0))/2
    Xi=AD(co['Xi'],RR.d-stationary_energy.d)
    D=AD(co['D'],Sd[3]-sm(b[j]*Sd[j] for j in range(3)));f=AD(co['f'],partial(arc['derivatives'],3))
    delta=f/D;C4=delta**5*(Gamma**2/(3*D**2)-Xi/D)
    ck('published_derivative_band',F('1.9e-40')<C4.d.lo<C4.d.hi<F('5.3e-40'))
    h=F(1,64);lo=F('2.49203004e-39')-h*F('5.3e-40');hi=F('2.49203006e-39')
    ck('published_anchored_band',F('2.48374879e-39')==lo<hi)
    return {'status':'R29_rational_AD_derivative_reconstruction_passed','checks':checks,'check_count':len(checks),
      'rounding_bits':BITS,'C4_prime_interval':list(map(str,[C4.d.lo,C4.d.hi])),
      'b_prime_intervals':[[str(x.lo),str(x.hi)] for x in bp],
      'accepted_inputs':'R29 local exact cusp, velocity, dual and coefficient boxes; new transcendental root jets; fixed-template integral and sign-motion bounds; analytic whole-tail enclosures. Automatic differentiation reconstructs the derivative arithmetic, not the analytic differentiation theorem.'}

def determinant(A):
    if len(A)==1:return A[0][0]
    return sum(((-1)**j*A[0][j]*determinant([[x for k,x in enumerate(row) if k!=j] for row in A[1:]]) for j in range(len(A))),RI(0))
def continuation_check(record):
    from math import factorial
    a,c=unbox(record['anchor']),unbox(record['cell']);checks=[]
    def ck(name,condition):
        assert condition,name
        checks.append(name)
    val=a['cusp_validation'];r=val['trial_radius'];B=a['B'];F0=a['central_derivatives']
    offs=[sym(r.hi)]*3+[RI(0)];powers=[{0:RI(1)}]
    weights={1:offs[0],2:-offs[1]/4,4:offs[2]/16,6:RI(0)}
    for _ in range(3):
        terms={}
        for i,v in powers[-1].items():
            for j,w in weights.items():terms[i+j]=terms.get(i+j,RI(0))+v*w
        powers.append(terms)
    dd=[]
    for n in range(7):
        poly=sm(sm(v*F0[n+j] for j,v in powers[k].items())/factorial(k) for k in range(3))
        error=sm(v.abs_upper()*B[n+j] for j,v in powers[3].items()).hi/6
        dd.append(poly+sym(error))
    JJ=[[dd[i+1],-dd[i+2]/4,dd[i+4]/16] for i in range(3)];CC=val['preconditioner'];CJ=mm(CC,JJ)
    E=[[RI(i==j)-CJ[i][j] for j in range(3)] for i in range(3)]
    q=max(sum(x.abs_upper() for x in row) for row in E)
    eta=max(x.abs_upper() for x in mv(CC,F0[:3]))/r.lo
    ck('cusp_preconditioner_invertible',not determinant(CC).contains(0))
    ck('anchor_newton_contraction',q+eta<1)
    ck('anchor_root_radius',r.hi*eta/(1-q)<=a['root_radius'].hi)
    prior=unbox(json.loads((HERE.parent/'cusp_connection/results/connection_certificate.json').read_text()))['cells'][0]
    affine=[prior['center'][j]+prior['predictor'][j]*(a['nu']-prior['driver_center']) for j in range(3)]
    for j in range(3):ck('R03_uniqueness_containment_'+str(j),(a['center'][j]-affine[j]).abs_upper()+r.hi<prior['radii'][j].lo)
    old=unbox(json.loads((HERE.parent/'cusp_shape_design/results/local_jets.json').read_text()))
    for j in [1,2]:ck('positive_moment_dominance_'+str(j),a['center'][j].hi+r.hi<(old['center'][j]+old['local_majorant_domain'][j]).lo)
    ck('negative_sextic_center',a['nu'].hi<0)
    d=c['dual'];arc=c['arc'];C=d['preconditioner'];h=arc['driver_half_width'].hi
    initial=mv(C,a['point_sign_moments'][:3]);rate=mv(C,d['fixed_b_rhs'])
    forcing=[initial[i].abs_upper()+h*rate[i].abs_upper() for i in range(3)]
    rr=d['radii'];GG=d['Gram'];CG=mm(C,GG);E=[[RI(i==j)-CG[i][j] for j in range(3)] for i in range(3)]
    qs=[sum(E[i][j].abs_upper()*rr[j].hi/rr[i].lo for j in range(3)) for i in range(3)]
    etas=[forcing[i]/rr[i].lo for i in range(3)]
    ck('dual_preconditioner_invertible',not determinant(C).contains(0))
    for i in range(3):ck('uniform_dual_contraction_'+str(i),qs[i]+etas[i]<1)
    factor=max(etas)/(1-max(qs))
    for i in range(3):ck('dual_tightening_'+str(i),rr[i].hi*factor<=d['tightening_factor'].hi*rr[i].hi)
    for k in range(1,4):ck('Gram_positive_minor_'+str(k),determinant([row[:k] for row in GG[:k]]).lo>0)
    ck('three_switch_repair_rank',not determinant(c['coefficients']['first_three_switch_matrix']).contains(0))
    for i,root in enumerate(d['roots']):
        ck('root_contraction_'+str(i),len(root['contractions'])>0)
        for step in root['contractions']:
            ck('root_inclusion_'+str(i)+'_'+str(len(checks)),step['input'].lo<=step['output'].lo and step['output'].hi<=step['input'].hi)
    for i,leaf in enumerate(d['sign_cover']):
        # These transcendental interval inputs are recomputed in the Arb replay.
        ck('sign_leaf_'+str(i),(leaf['sign']*leaf['raw_residual']).lo>0)
    co=c['coefficients'];Sp=a['point_sign_moments'];b0=a['dual_center'];bb=d['tight_box']
    dr=[(bb[i]-b0[i]).abs_upper() for i in range(3)]
    anchor_error=sum(Sp[i].abs_upper()*dr[i] for i in range(3))+sum(GG[i][j].abs_upper()*dr[i]*dr[j] for i in range(3) for j in range(3))/2
    Dcenter=Sp[3]-sm(b0[i]*Sp[i] for i in range(3));Derr=anchor_error+h*co['D_derivative_bound'].abs_upper()
    ck('positive_dual_objective',Dcenter.lo-Derr>0)
    ck('D_variation_enclosure',Derr<=co['D_total_error'].hi)
    solve=co['linear_solve'];A=co['G'];C=solve['preconditioner'];v0=solve['seed'];CG=mm(C,A)
    eps=max(sum((RI(i==j)-CG[i][j]).abs_upper() for j in range(3)) for i in range(3));ck('coefficient_linear_solve',eps<1)
    rho=max(x.abs_upper() for x in mv(C,[co['B'][i]-mv(A,v0)[i] for i in range(3)]))/(1-eps)
    vv=[v0[i]+sym(rho) for i in range(3)];Xi=co['R']-sm(co['B'][i]*vv[i] for i in range(3))/2
    C4=(co['f']/co['D'])**5*(co['Gamma']**2/(3*co['D']**2)-Xi/co['D'])
    ck('positive_raw_coefficient',C4.lo>0)
    return {'check_count':len(checks),'checks':checks,'C4_raw_interval':[str(C4.lo),str(C4.hi)],
      'accepted_inputs':'Transcendental cusp jets and positive moment majorants; quadrature and sign/root enclosures, fixed-b derivative rhs, D derivative bound and coefficient root sums. Contractions and linear algebra rebuilt using outward rational arithmetic; derivative formulas are independently AD reconstructed below.'}
def main():
    import gzip
    ap=argparse.ArgumentParser();ap.add_argument('--cover-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert not args.output.exists();cert=json.loads((args.cover_dir/'certificate.json').read_text());out=[];count=0
    for rec in cert['cells']:
        p=args.cover_dir/rec['file'];assert sha(p)==rec['sha256'];data=json.loads(gzip.decompress(p.read_bytes()))
        first=continuation_check(data);second=motion_check(data['motion'],data['cell']);count+=first['check_count']+second['check_count']
        out.append({'index':rec['index'],'file_sha256':sha(p),'continuation':first,'derivative_AD':second})
        print('rational cell',rec['index']+1,'checks',first['check_count']+second['check_count'],flush=True)
    result={'status':'R29_rational_continuation_and_derivative_checks_passed','cells':out,'check_count':count,'rounding_bits':BITS,
      'certificate_sha256':sha(args.cover_dir/'certificate.json'),'source_sha256':sha(__file__),
      'rational_helper_sha256':sha(HERE.parent/'theta_fourth_order/rational_intervals.py')}
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],count)
if __name__=='__main__':main()
