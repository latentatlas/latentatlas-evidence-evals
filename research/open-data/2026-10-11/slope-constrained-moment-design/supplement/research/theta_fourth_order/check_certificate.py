#!/usr/bin/env python3
"""Independent standard-library arithmetic from certified local jets to theta C4."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
from rational_intervals import RI,restore,dot,mv,mm,BITS
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def overlap(x,y):return max(x.lo,y.lo)<=min(x.hi,y.hi)
def data(x):return [str(x.lo),str(x.hi)]
def run(path):
    assert __debug__;cert=json.loads(path.read_text());read=lambda x:restore(x)
    oldpath=HERE.parent/'kernel_slope_asymptotics/results/asymptotic_certificate.json';old=json.loads(oldpath.read_text())
    assert cert['input_sha256']['R15']==sha(oldpath)
    assert cert['source_sha256']['interval_core.py']==sha(HERE/'interval_core.py')
    assert cert['source_sha256']['certify_coefficient.py']==sha(HERE/'certify_coefficient.py')
    grad=read(old['gradient_l1_upper']);m=read(old['strong_convexity_constant']);radius=read(cert['improved_dual_radius'])
    assert radius.hi>=grad.hi/m.lo and radius.hi<read(old['dual_localization_radius']).lo
    box=[read(r) for r in cert['dual_box']]
    for new,oldb in zip(box,map(read,old['dual_coefficient_box'])):assert oldb.lo<=new.lo<=new.hi<=oldb.hi
    gamma=RI(0);G=[[RI(0) for _ in range(3)] for _ in range(3)];B=[RI(0) for _ in range(3)];RR=RI(0)
    local_checks=0;contractions=0
    for cr in cert['finite_roots']:
        I=read(cr['inherited_root_interval'])
        for step in cr['contractions']:
            inp,out=read(step['input_interval']),read(step['output_interval']);assert overlap(inp,I)
            assert inp.lo<=out.lo<=out.hi<=inp.hi
            c=read(step['center']);r=read(step['radius']);image=c-read(step['residual'])/read(step['derivative'])
            assert out.lo<=image.lo and image.hi<=out.hi
            I=out;contractions+=1
        assert overlap(I,read(cr['root_interval']))
        p=[[read(x) for x in row] for row in cr['p_jets']]
        raw=[p[3][l]-sum((box[j]*p[j][l] for j in range(3)),RI(0)) for l in range(4)]
        sigma=cr['orientation'];assert sigma in [-1,1] and (sigma*raw[1]).lo>0
        for a,b in zip(raw,cr['raw_residual_jets']):assert overlap(a,read(b));local_checks+=1
        w,wp,wpp=map(read,cr['weight_jets']);assert w.lo>0
        q1=w*raw[1];q2=2*wp*raw[1]+w*raw[2];q3=3*wpp*raw[1]+3*wp*raw[2]+w*raw[3]
        for a,b in zip([q1,q2,q3],cr['density_root_jets']):assert overlap(a,read(b));local_checks+=1
        gam=sigma*q1;gamma+=gam
        rpos=q2**2/(36*gam);rsub=sigma*q3/60;rterm=rpos-rsub;RR+=rterm
        assert overlap(gam,read(cr['Gamma'])) and overlap(rterm,read(cr['R']));local_checks+=2
        for i in range(3):
            bb=sigma*(wp*p[i][0]+w*(p[i][0]*raw[2]/raw[1]-p[i][1]))/3
            assert overlap(bb,read(cr['B'][i]));B[i]+=bb;local_checks+=1
            for j in range(3):
                gg=2*w*p[i][0]*p[j][0]/(sigma*raw[1])
                assert overlap(gg,read(cr['G'][i][j]));G[i][j]+=gg;local_checks+=1
    tail={k:read(v) for k,v in cert['tail_absolute_bounds'].items()}
    assert all(x.lo>0 for x in tail.values())
    gamma+=RI(0,tail['Gamma'].hi);RR+=RI(-tail['R'].hi,tail['R'].hi)
    B=[v+RI(-tail['B_entry'].hi,tail['B_entry'].hi) for v in B]
    G=[[G[i][j]+RI(0 if i==j else -tail['G_entry'].hi,tail['G_entry'].hi) for j in range(3)] for i in range(3)]
    C=[[read(x) for x in row] for row in cert['linear_solve']['preconditioner']]
    v0=[read(x) for x in cert['linear_solve']['v0']]
    assert all(x.lo==x.hi for row in C for x in row) and all(x.lo==x.hi for x in v0)
    CG=mm(C,G);E=[[RI(i==j)-CG[i][j] for j in range(3)] for i in range(3)]
    eta=max(sum(x.abs_upper() for x in row) for row in E);assert eta<1
    residual=[x-y for x,y in zip(B,mv(G,v0))];pre=mv(C,residual)
    vr=max(x.abs_upper() for x in pre)/(1-eta)
    v=[x+RI(-vr,vr) for x in v0];P=dot(B,v)/2;Xi=RR-P
    f=read(cert['coefficients']['f']);delta=read(old['delta_star_enclosure']);D=f/delta
    C2=delta**3*gamma/(3*D);C4=delta**5*(gamma**2/(3*D**2)-Xi/D)
    lower=F('2.49203004e-39');upper=F('2.49203006e-39')
    assert lower<C4.lo<C4.hi<upper
    assert P.lo>0 and Xi.lo>0 and C4.lo>0
    assert overlap(C4,read(cert['coefficients']['C4']))
    # A sign error in the moment penalty changes C4 materially and is rejected.
    wrong=delta**5*(gamma**2/(3*D**2)-(RR+P)/D)
    assert not overlap(wrong,C4)
    return {'status':'R24_independent_rational_arithmetic_passed','rounding_bits':BITS,
       'input_certificate_sha256':sha(path),'source_sha256':sha(__file__),
       'rational_interval_source_sha256':sha(HERE/'rational_intervals.py'),
       'base_interval_helper_sha256':sha(HERE.parent/'finite_slope_optimum/exact_interval.py'),
       'root_count':len(cert['finite_roots']),'contractions_checked':contractions,'local_quantities_compared':local_checks,
       'independent_eta_upper':str(eta),'independent_v_radius':str(vr),
       'reconstructed_intervals':{k:data(x) for k,x in {'Gamma':gamma,'D':D,'R':RR,'P':P,'Xi':Xi,'C2':C2,'C4':C4}.items()},
       'published_C4_strict_bounds':[str(lower),str(upper)],
       'negative_control_wrong_moment_sign_rejected':True,
       'trust_boundary':'Exact rational reconstruction with outward dyadic rounding from local transcendental enclosures and inherited analytic root/localization/tail inputs. Overlap checks are diagnostics; the independently reconstructed final interval lies strictly inside the stated published bounds.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=run(args.certificate);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status']);print('local checks',result['local_quantities_compared'],'contractions',result['contractions_checked'])
    vals=result['reconstructed_intervals']['C4'];print('independent C4 endpoints',*[format(float(F(x)),'.17g') for x in vals])
if __name__=='__main__':main()
