#!/usr/bin/env python3
"""Check saved inequality witnesses with exact rational interval arithmetic.

Imports neither FLINT nor the generating Taylor code. This checks arithmetic
and containment of the recorded witnesses, not the integrals that produce
them or the analytic argument. Those remain explicit trust dependencies.
"""
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise RuntimeError('Run the witness checker without Python -O/-OO')

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'cusp_verified'


class Interval:
    def __init__(self,lo,hi=None):
        self.lo=Q(lo)
        self.hi=self.lo if hi is None else Q(hi)
        if self.lo>self.hi:
            raise ValueError('Reversed interval')
    @staticmethod
    def of(x):
        return x if isinstance(x,Interval) else Interval(x)
    def __add__(self,other):
        b=self.of(other)
        return Interval(self.lo+b.lo,self.hi+b.hi)
    __radd__=__add__
    def __neg__(self):
        return Interval(-self.hi,-self.lo)
    def __sub__(self,other):
        return self+-self.of(other)
    def __rsub__(self,other):
        return self.of(other)+-self
    def __mul__(self,other):
        b=self.of(other)
        products=[a*v for a in (self.lo,self.hi) for v in (b.lo,b.hi)]
        return Interval(min(products),max(products))
    __rmul__=__mul__
    def __truediv__(self,other):
        b=self.of(other)
        if b.lo<=0<=b.hi:
            raise ZeroDivisionError('Divisor includes zero')
        return self*Interval(1/b.hi,1/b.lo)
    def abs_upper(self):
        return max(abs(self.lo),abs(self.hi))
    def contains(self,value):
        return self.lo<=value<=self.hi


def read(ball):
    a,e=ball['mid_man_exp']
    b,f=ball['rad_man_exp']
    center=Q(a)*Q(2)**e
    radius=Q(b)*Q(2)**f
    if radius<0:
        raise ValueError('Negative radius')
    return Interval(center-radius,center+radius)


def matrix(d,unknowns='controls'):
    if unknowns=='controls':
        return [[-d[2]/4,d[4]/16],[-d[3]/4,d[5]/16]]
    return [[d[1],d[4]/16],[d[2],d[5]/16]]


def contraction(Y,A,H,radii):
    determinant=Y[0][0]*Y[1][1]-Y[0][1]*Y[1][0]
    assert not determinant.contains(0)
    assert all(r.lo==r.hi and r.lo>0 for r in radii)
    defects=[[Interval(i==j)-sum((Y[i][k]*A[k][j] for k in range(2)),Interval(0))
              for j in range(2)] for i in range(2)]
    q=max(sum((defects[i][j]*radii[j]/radii[i]).abs_upper()
              for j in range(2)) for i in range(2))
    eta=max((sum((Y[i][k]*H[k] for k in range(2)),Interval(0))/radii[i]).abs_upper()
            for i in range(2))
    assert q<1 and q+eta<1
    return {'q_upper':str(q),'eta_upper':str(eta),
            'q_upper_display':float(q),'eta_plus_q_display':float(q+eta)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path=HERE/'results/region_certificate.json'
    data=json.loads(path.read_text())
    for name,expected in data['source_sha256'].items():
        assert sha(HERE/name)==expected,('source mismatch',name)
    baseline=json.loads((BASE/'manifest.json').read_text())
    for entry in baseline['files']:
        assert sha(BASE/entry['path'])==entry['sha256']
    assert sha(BASE/'manifest.json')==data['provenance']['baseline']['manifest_sha256']
    old=json.loads((BASE/'results/quartic_cusp_certificate.json').read_text())
    assert data['center_exact_dyadic']==old['center_exact_dyadic']
    T,L,M=Q(3,1000),Q(1,1000000),Q(1,500000000)
    assert read(old['radius']).hi<min(T,L/2,M,Q(1,10000))
    curve=data['uniform_curve']
    radii=list(map(read,curve['control_half_widths']))
    assert [r.lo for r in radii]==[Q(2)**-13,Q(2)**-20]
    assert read(curve['t_half_width']).contains(T)
    d=list(map(read,curve['derivative_enclosures']))
    Y=[list(map(read,row)) for row in curve['preconditioner']]
    uniform=contraction(Y,matrix(d),list(map(read,curve['H_on_centerline'])),radii)
    delta=d[3]*d[4]-d[2]*d[5]
    assert d[3].lo>0 and d[4].hi<0 and delta.hi<0
    lp=4*d[2]*d[4]/delta
    mp=16*d[2]*d[2]/delta
    wp=d[3]-d[4]*lp/4+d[6]*mp/16
    assert wp.lo>0
    a=4*d[4]/delta
    b=Interval(-16)/delta
    quadratic=a*wp/2
    cubic=b*wp*wp/3
    assert quadratic.lo>Q(191,100) and quadratic.hi<Q(209,100)
    assert cubic.lo>Q(172,100) and cubic.hi<Q(194,100)
    # Compare squares to avoid inexact radicals in the 3/2 bounds.
    assert cubic.lo**2>Q(57,100)**2*quadratic.hi**3
    assert cubic.hi**2<Q(73,100)**2*quadratic.lo**3
    assert read(curve['F_tt_endpoint_signs'][0]).hi<0
    assert read(curve['F_tt_endpoint_signs'][1]).lo>0
    for entry in data['root_window_boundary']:
        z=read(entry['derivatives'][0])*entry['sign']
        assert z.lo>0
    local=[]
    for kind,entries in [('controls',data['interior_fold_witnesses']),
                         ('t_mu',data['right_boundary_folds'])]:
        assert len(entries)==2
        for index,entry in enumerate(entries):
            A=matrix(list(map(read,entry['box_derivatives'])),kind)
            H=list(map(read,entry['point_derivatives'][:2]))
            y=[list(map(read,row)) for row in entry['preconditioner']]
            rr=list(map(read,entry['radii']))
            local.append(contraction(y,A,H,rr))
            if kind=='controls':
                l,m=list(map(read,entry['control_offset_boxes']))
                centers=list(map(read,entry['center']))
                for box,c,r in zip((l,m),centers,rr):
                    assert c.lo==c.hi
                    assert box.contains(c.lo-r.lo) and box.contains(c.hi+r.hi)
                assert l.lo>L and m.abs_upper()<M
                assert l.abs_upper()<radii[0].lo and m.abs_upper()<radii[1].lo
                assert read(entry['t_offset']).contains(Q((-1,1)[index],1000))
            else:
                t,m=read(entry['t_offset_box']),read(entry['mu_offset_box'])
                centers=list(map(read,entry['center']))
                for box,c,r in zip((t,m),centers,rr):
                    assert c.lo==c.hi
                    assert box.contains(c.lo-r.lo) and box.contains(c.hi+r.hi)
                assert entry['t_sign']==(-1,1)[index]
                assert (t*entry['t_sign']).lo>Q(1,10000)
                assert t.abs_upper()<T and m.abs_upper()<M
                assert read(entry['lambda_offset']).contains(L)
    witness_counts=[]
    for entry in data['root_count_witnesses']:
        count=entry['root_count']
        assert count in (1,3)
        witness_counts.append(count)
        values=list(map(read,entry['F_values']))
        signs=[-1,1] if count==1 else [-1,1,-1,1]
        assert len(values)==len(signs)
        assert all((v*s).lo>0 for v,s in zip(values,signs))
        offsets=list(map(read,entry['t_offsets']))
        assert all(a.hi<b.lo for a,b in zip(offsets,offsets[1:]))
        assert all(-T<=v.lo and v.hi<=T for v in offsets[1:-1])
        if count==1:
            assert offsets[0].contains(-T) and offsets[-1].contains(T)
            assert read(entry['lambda_offset']).contains(-L/2)
            cover=entry['positive_F_t_cover']
            assert len(cover)==32
            for k,part in enumerate(cover):
                assert read(part['left']).contains(-T+2*T*k/32)
                assert read(part['right']).contains(-T+2*T*(k+1)/32)
                assert read(part['F_t']).lo>0
        else:
            assert offsets[0].lo>-T and offsets[-1].hi<T
            assert read(entry['lambda_offset']).contains(L/2)
    assert sorted(witness_counts)==[1,3]
    report={'status':'exact_rational_witness_checks_passed',
            'scope':'Rechecks certificate inequalities and stated containments with fractions; does not re-integrate or formalize the analytic proof',
            'certificate_sha256':sha(path),'source_sha256':sha(Path(__file__)),
            'uniform_contraction':uniform,'four_local_contractions':local,
            'baseline_files_unchanged':len(baseline['files']),
            'sign_geometry_and_root_count_checks':True}
    (HERE/'results/witness_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],
                      'q_upper':uniform['q_upper_display'],
                      'eta_plus_q':uniform['eta_plus_q_display'],
                      'local_contractions_checked':len(local)},indent=2))


if __name__=='__main__':
    main()
