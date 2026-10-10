#!/usr/bin/env python3
"""Certified finite fold samples at the exact quartic and sextic cusps.

These are plotting witnesses, not the proof of monotonicity between
samples. All offsets are relative to the exact R01 cusp, with its
uncertainty carried into central derivative enclosures.
"""
import json
import time
from math import factorial
from flint import arb, arb_mat, ctx
from transport_model import HERE, sha, restore, serialize, upper, zero_ball, verify_inputs
from validated_flow import (cache, absolute_derivative_bounds, midpoint_inverse,
                            matmul, matvec, norm_mat, norm_vec)


def require(ok, message):
    if not ok:
        raise ArithmeticError(message)


def pack(value):
    if isinstance(value, arb): return serialize(value)
    if isinstance(value, list): return [pack(v) for v in value]
    if isinstance(value, dict): return {k:pack(v) for k,v in value.items()}
    return value


class EndpointTaylor:
    def __init__(self, family):
        self.family=family
        path=HERE.parent/f'cusp_verified/results/{family}_cusp_certificate.json'
        raw=json.loads(path.read_text())
        self.source_hash=sha(path)
        self.x=list(map(restore,raw['center_exact_dyadic']))
        self.radius=restore(raw['radius'])
        self.half=[arb(2)**-9,arb(2)**-18,arb(2)**-28]
        if family=='quartic':
            params={1:self.x[1],2:self.x[2],3:arb(0)}
            shifts=(1,2,4); factors=(arb(1),arb(1)/4,arb(1)/16)
            self.driver=arb(0)
            parameter_domain={1:self.x[1]+zero_ball(upper(self.half[1]+self.radius)),
                              2:self.x[2]+zero_ball(upper(self.half[2]+self.radius)),3:arb(0)}
        elif family=='sextic':
            params={1:self.x[1],2:arb(0),3:self.x[2]}
            shifts=(1,2,6); factors=(arb(1),arb(1)/4,arb(1)/64)
            self.driver=self.x[2]+zero_ball(self.radius)
            parameter_domain={1:self.x[1]+zero_ball(upper(self.half[1]+self.radius)),
                              2:zero_ball(self.half[2]),3:self.driver}
        else:
            raise ValueError('Unknown endpoint')
        self.order=8; self.nmax=5
        self.B=absolute_derivative_bounds(parameter_domain,40)
        self.central=cache(self.x[0],params,33,N=16,U=2,pieces=8,
                           abs_tol='1e-98',rel_tol='1e-98')
        self.c=[v+zero_ball(self.radius*sum((f*self.B[n+j] for j,f in zip(shifts,factors)),arb(0)))
                for n,v in enumerate(self.central)]
        # These zeros belong to the exact cusp established in R01/R03.
        self.c[:3]=[arb(0)]*3
        self.terms=[];self.remainder=[]
        for a in range(self.order+1):
            for b in range(self.order+1-a):
                for c in range(self.order+1-a-b):
                    row=(a,b,c,a+2*b+4*c,arb(1)/(factorial(a)*factorial(b)*factorial(c)))
                    (self.terms if a+b+c<self.order else self.remainder).append(row)

    def derivatives(self,s,l,m):
        offsets=list(map(arb,(s,l,m)))
        require(all(v.is_finite() and upper(abs(v))<=h for v,h in zip(offsets,self.half)),
                'Outside endpoint Taylor domain')
        directions=[offsets[0],-offsets[1]/4,offsets[2]/16]
        powers=[];magnitudes=[]
        for v in directions:
            row=[arb(1)]
            for _ in range(self.order): row.append(row[-1]*v)
            powers.append(row)
            magnitudes.append([upper(abs(v))**k for k in range(self.order+1)])
        out=[]
        for n in range(self.nmax+1):
            val=sum((powers[0][a]*powers[1][b]*powers[2][c]*f*self.c[n+j]
                     for a,b,c,j,f in self.terms),arb(0))
            err=sum((magnitudes[0][a]*magnitudes[1][b]*magnitudes[2][c]*f*self.B[n+j]
                     for a,b,c,j,f in self.remainder),arb(0))
            out.append(val+zero_ball(err))
        return out

    def provenance(self):
        return pack({'family':self.family,'cusp_certificate_sha256':self.source_hash,
                     'driver':self.driver,'center_exact_dyadic':self.x,'cusp_radius':self.radius,
                     'domain_half_widths':self.half,'quadrature_derivatives':self.central,
                     'exact_cusp_derivatives':self.c,'absolute_derivative_bounds':self.B,
                     'order':self.order})


def jacobian(d): return [[d[1],d[4]/16],[d[2],d[5]/16]]


def certify_sample(model,ell,sign):
    s=(sign*(ell/2).sqrt()).mid()
    m=(16*model.c[3]*s*s*s/(3*model.c[4])).mid()
    for _ in range(6):
        d=model.derivatives(s,ell,m)
        Y=midpoint_inverse(jacobian([v.mid() for v in d]))
        correction=matvec(Y,[d[0].mid(),d[1].mid()])
        s=(s-correction[0]).mid();m=(m-correction[1]).mid()
    radii=[upper(ell.sqrt()*arb(2)**-20),upper(ell*ell.sqrt()*arb(2)**-20)]
    d0=model.derivatives(s,ell,m)
    box=[s+zero_ball(radii[0]),m+zero_ball(radii[1])]
    db=model.derivatives(box[0],ell,box[1])
    Y=midpoint_inverse(jacobian([v.mid() for v in d0]))
    require(not arb_mat(Y).det().contains(0),'Singular point preconditioner')
    yj=matmul(Y,jacobian(db))
    defect=[[arb(i==j)-yj[i][j] for j in range(2)] for i in range(2)]
    weighted=[[defect[i][j]*radii[j]/radii[i] for j in range(2)] for i in range(2)]
    q=norm_mat(weighted)
    residual=matvec(Y,d0[:2])
    eta=norm_vec([v/r for v,r in zip(residual,radii)])
    require(q<1 and eta+q<1,'Endpoint sample contraction failed')
    factor=upper(eta/(1-q))
    tight=[upper(r*factor) for r in radii]
    root=[v+zero_ball(r) for v,r in zip((s,m),tight)]
    require(sign*box[0]>0 and abs(box[0])<arb('0.003') and abs(box[1])<arb('2e-9'),
            'Fold sample not identified with the R04 arc')
    require(db[4]<0 and sign*db[2]>0,'Fold is not nondegenerate')
    return pack({'branch':'lower' if sign>0 else 'upper','center':[s,m],
                 'radii':radii,'preconditioner':Y,'box_derivatives':db,
                 'center_derivatives':d0,'q':q,'eta':eta,
                 'tight_root_radii':tight,'root_enclosures':root})


def main():
    ctx.dps=110;started=time.monotonic();inputs=verify_inputs()
    models={name:EndpointTaylor(name) for name in ('quartic','sextic')}
    rows=[]
    for k in range(1,33):
        ell=arb(k*k)/(1000000*32*32)
        row={'index':k,'ell':serialize(ell),'endpoints':{}}
        for name,model in models.items():
            upper_root=certify_sample(model,ell,-1)
            lower_root=certify_sample(model,ell,1)
            width=restore(upper_root['root_enclosures'][1])-restore(lower_root['root_enclosures'][1])
            row['endpoints'][name]={'upper':upper_root,'lower':lower_root,
                                   'width':serialize(width),
                                   'normalized_width':serialize(width/(ell*ell.sqrt()))}
        ratio=restore(row['endpoints']['sextic']['width'])/restore(row['endpoints']['quartic']['width'])
        require(ratio>1,'Endpoint width ordering failed')
        row['ratio']=serialize(ratio);rows.append(row)
        if k in (1,16,32):print('certified endpoint fold sample',k,'ratio',ratio.str(18),flush=True)
    report={'status':'128_endpoint_fold_contractions_passed','is_interval_certificate':True,
            'scope':'32 positive ell samples, two folds at each of the two exact R01 cusps. Interpolating lines are visual aids only.',
            'input_packages':inputs,'models':{n:m.provenance() for n,m in models.items()},
            'samples':rows,'source_sha256':sha(HERE/'endpoint_folds.py'),
            'elapsed_seconds':time.monotonic()-started}
    (HERE/'results/endpoint_folds.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'elapsed_seconds':report['elapsed_seconds']},indent=2))


if __name__=='__main__':main()
