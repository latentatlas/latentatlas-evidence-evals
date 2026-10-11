"""R07: uniform bounded relative kernel errors, with frozen R03-R05 inputs.

No quadrature runs here. Frozen original-kernel Taylor jets and positive
moment majorants are reused. The relative perturbation h is fixed across
all controls, real measurable and |h| <= epsilon on [0,infinity).
"""
from pathlib import Path
import hashlib
import json
import sys
sys.dont_write_bytecode = True
from flint import arb, arb_mat

HERE = Path(__file__).resolve().parent
for package in ('cusp_verified', 'cusp_connection', 'cusp_geometry', 'cusp_width'):
    sys.path.insert(0, str(HERE.parent/package))
from validated_flow import upper, zero_ball, serialize, midpoint_inverse, matmul, matvec, norm_mat, norm_vec
from explore import restore
from bridge_taylor import operator_powers
from geometry_model import LocalCusp
from width_shape import certify_shape, partials
from transport_model import ExtendedCell, fourth_at_cusp, partials4
from certify_connection import cusp_tangent
from fold_jets import transport_jet


class BoundFailure(ArithmeticError):
    pass


def require(ok, message):
    if not ok:
        raise BoundFailure(message)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pack(v):
    if isinstance(v, arb): return serialize(v)
    if isinstance(v, list): return [pack(a) for a in v]
    if isinstance(v, dict): return {k: pack(a) for k, a in v.items()}
    return v


def load_inputs():
    names = ('cusp_verified','cusp_region','cusp_connection','cusp_geometry','cusp_width','cusp_literature')
    packages = []
    for name in names:
        base = HERE.parent/name
        manifest = json.loads((base/'manifest.json').read_text())
        for row in manifest['files']:
            require(sha(base/row['path']) == row['sha256'], f'Frozen input changed: {name}/{row["path"]}')
        packages.append({'package': name, 'files': len(manifest['files']),
                         'manifest_sha256': sha(base/'manifest.json')})
    paths = [HERE.parent/p/'results'/f for p, f in (
        ('cusp_connection','connection_certificate.json'),
        ('cusp_geometry','geometry_certificate.json'),
        ('cusp_width','width_certificate.json'))]
    data = [json.loads(p.read_text()) for p in paths]
    require(all(len(d['cells']) == 58 for d in data), 'Incomplete driver cover')
    return packages, paths, data


class SavedCell(ExtendedCell):
    """The proven R05 Taylor formula loaded exclusively from frozen data."""
    def __init__(self, raw, geo, width, index, tight):
        self.index = index
        self.x = list(map(restore, raw['center']))
        self.nu = restore(raw['driver_center'])
        self.v = list(map(restore, raw['predictor']))
        self.h = restore(raw['driver_half_width'])
        self.tight = list(tight)
        self.allowed = list(map(restore, raw['majorant_domain_half_widths']))
        self.c = list(map(restore, raw['central_derivatives'] + geo['extra_central_derivatives'] + width['extra_central_derivatives']))
        self.B = list(map(restore, raw['absolute_derivative_bounds'] + geo['extra_absolute_bounds'] + width['extra_absolute_bounds']))
        self.K, self.nmax = 8, 26
        require(len(self.c) == 69 and len(self.B) == 75, 'Wrong saved derivative extent')
        self.A = operator_powers({1:self.v[0], 2:-self.v[1]/4,
                                 4:self.v[2]/16, 6:-arb(1)/64}, self.K)

    def perturb(self, bounds, epsilon):
        return [value + zero_ball(epsilon*self.B[n]) for n, value in enumerate(bounds)]


def cusp_contraction(raw, epsilon):
    Y = [list(map(restore, row)) for row in raw['preconditioner']]
    B = list(map(restore, raw['absolute_derivative_bounds']))
    R = list(map(restore, raw['radii']))
    require(not arb_mat(Y).det().contains(0), 'Singular cusp preconditioner')
    E = upper(max(upper(sum((abs(Y[i][n])*B[n] for n in range(3)), arb(0))/R[i]) for i in range(3)))
    factors = (arb(1), arb(1)/4, arb(1)/16)
    shifts = (1,2,4)
    Q = upper(max(upper(sum((sum((abs(Y[i][n])*B[n+shifts[j]] for n in range(3)),arb(0))
                            * factors[j]*R[j]/R[i] for j in range(3)),arb(0))) for i in range(3)))
    q = upper(restore(raw['q']) + epsilon*Q)
    eta = upper(restore(raw['eta']) + epsilon*E)
    require(q < 1 and q+eta < 1, 'Cusp contraction/self-mapping failed')
    displacement = [upper(r*epsilon*E/(1-q)) for r in R]
    oldtight = list(map(restore, raw['tight_root_radii']))
    tight = [min(upper(r*eta/(1-q)), upper(a+d)) for r,a,d in zip(R,oldtight,displacement)]
    return {'E':E,'Q':Q,'q':q,'eta':eta,'displacement':displacement,'tight':tight}


def local_geometry(c, b, limits, T, L, M):
    local = LocalCusp(c,b,limits)
    radii = [arb(2)**-13, arb(2)**-20]
    d = local.derivatives(zero_ball(T), zero_ball(radii[0]), zero_ball(radii[1]))
    Y = midpoint_inverse([[arb(0),c[4].mid()/16],[-c[3].mid()/4,c[5].mid()/16]])
    require(not arb_mat(Y).det().contains(0), 'Singular fold preconditioner')
    A = [[-d[2]/4,d[4]/16],[-d[3]/4,d[5]/16]]
    YA = matmul(Y,A)
    q = norm_mat([[(arb(i==j)-YA[i][j])*radii[j]/radii[i] for j in range(2)] for i in range(2)])
    H = local.derivatives(zero_ball(T),0,0,upto=1)
    eta = norm_vec([v/r for v,r in zip(matvec(Y,H),radii)])
    require(q < 1 and eta+q < 1, 'Uniform fold contraction failed')
    delta = d[3]*d[4]-d[2]*d[5]
    require(d[3]>0 and d[4]<0 and delta<0, 'Fold rank/derivative signs failed')
    lp,mp = 4*d[2]*d[4]/delta,16*d[2]*d[2]/delta
    wp = d[3]-d[4]*lp/4+d[6]*mp/16
    require(wp>0,'Fold D2 monotonicity failed')
    quadratic,cubic = (4*d[4]/delta)*wp/2,(-16/delta)*wp*wp/3
    semi = cubic/(quadratic*quadratic.sqrt())
    require(quadratic>arb('1.80') and quadratic<arb('2.21'),'Quadratic growth failed')
    require(cubic>arb('1.61') and cubic<arb('2.09'),'Cubic growth failed')
    require(semi>arb('0.49') and semi<arb('0.86'),'Semicubical growth failed')
    require(arb('1.80')*T*T>L and arb('0.86')*L*L.sqrt()<M,'Fold exits failed')
    endpoints=[]
    for sign in (-1,1):
        f=local.evaluate(0,sign*T,zero_ball(L),zero_ball(M))
        f2=local.evaluate(2,sign*T,zero_ball(radii[0]),zero_ball(radii[1]))
        require(sign*f>0 and sign*f2>0,'Root-window endpoint sign failed')
        endpoints.append({'sign':sign,'F':f,'F2':f2})
    three=[]
    for s,sign in zip([arb(-3)/2000,arb(-3)/10000,arb(3)/10000,arb(3)/2000],[-1,1,-1,1]):
        f=local.evaluate(0,s,L/2,0)
        require(sign*f>0,'Three-root witness failed')
        three.append({'s':s,'sign':sign,'F':f})
    one=[]
    for k in range(32):
        a,z=-T+2*T*k/32,-T+2*T*(k+1)/32
        value=local.evaluate(1,a.union(z),-L/2,0)
        require(value>0,'One-root witness failed')
        one.append({'left':a,'right':z,'F1':value})
    return {'preconditioner':Y,'derivatives':d,'H':H,'q':q,'eta':eta,
            'delta':delta,'wprime':wp,'quadratic':quadratic,'cubic':cubic,
            'semicubical':semi,'endpoints':endpoints,'three_witness':three,'one_cover':one}


def cell_bounds(raw,geo,width,index,epsilon):
    contraction = cusp_contraction(raw,epsilon)
    model=SavedCell(raw,geo,width,index,contraction['tight'])
    cp0,cpr=model.enclose(upto=15)
    cp=model.perturb(cp0,epsilon)
    require(cp[3]>0 and cp[4]<0 and cp[6]<0,'Perturbed cusp signs failed')
    tangent=cusp_tangent(cp)
    require(tangent[2]>arb('0.26') and tangent[2]<arb('0.34'),'Mu tangent bound failed')
    shape0=certify_shape(model,cp0)
    scale=shape0['scale']
    grad=partials([value/scale for value in cp[3:11]])
    nerror=upper(epsilon*sum((abs(v)*model.B[n] for n,v in zip(range(3,11),grad)),arb(0))/scale)
    N=shape0['N']+zero_ball(nerror)
    ds=[v/scale for v in cp]
    kp=N/(64*ds[3]*ds[3]*ds[4]*ds[4]*ds[4])
    require(N>0 and kp<0,'Opening derivative sign failed')
    Cprime=8*arb(2).sqrt()/3*kp
    T,L,M=arb(3)/1000,arb('1e-6'),arb('2e-9')
    limits=[arb(2)**-8,arb(2)**-12,arb(2)**-19]
    b0,br=model.enclose(limits,upto=10)
    b=model.perturb(b0,epsilon)
    geometry=local_geometry(cp,b,limits,T,L,M)
    fourth0=fourth_at_cusp(model,cp0)
    s4=fourth0['scale']
    grad4=partials4([v/s4 for v in cp[3:12]])
    n4error=upper(epsilon*sum((abs(v)*model.B[n] for n,v in zip(range(3,12),grad4)),arb(0))/s4)
    N4=fourth0['N4']+zero_ball(n4error)
    a,b4=cp[3]/s4,cp[4]/s4
    B4=-2*N4/(a*a*a*b4*b4*b4*b4)
    S=arb(3)/4000
    extra=[2*S,arb('2.22')*S*S,arb('2.10')*S*S*S]
    fd0,fdr=model.enclose(extra,upto=26)
    fd=model.perturb(fd0,epsilon)
    fd[0]=fd[1]=arb(0)
    fd[2]=zero_ball(upper(geometry['wprime'])*S)
    jet,l,m=transport_jet(fd,tangent[1],K=5)
    M5=upper(120*abs(jet[5]));M4=upper(abs(B4))
    third=-32*kp+zero_ball(upper(M4*S+M5*S*S/2))
    require(third>0,'Finite-window fold direction failed')
    require(arb('1.80')*S*S>L,'Finite-window coverage failed')
    ratelow=(third/(3*arb('2.21')*arb('2.21').sqrt())).lower()
    ratehigh=(third/(3*arb('1.80')*arb('1.80').sqrt())).upper()
    require(ratelow>arb('0.0003') and ratehigh<arb('0.003'),'Readable rate enclosure failed')
    return pack({'index':index,'contraction':contraction,
        'original_cusp_derivatives':cp0,'cusp_remainders':cpr,'perturbed_cusp_derivatives':cp,
        'cusp_tangent':tangent,'opening_original':shape0,'opening_error':nerror,
        'opening_N':N,'kprime':kp,'Cprime':Cprime,
        'limits':limits,'original_neighborhood_derivatives':b0,'neighborhood_remainders':br,
        'perturbed_neighborhood_derivatives':b,'geometry':geometry,
        'fourth_original':fourth0,'fourth_error':n4error,'N4':N4,'B4':B4,
        'fold_extra':extra,'original_fold_derivatives':fd0,'fold_remainders':fdr,
        'perturbed_fold_derivatives':fd,'M4':M4,'M5':M5,
        'transport_jet':jet,'third':third,'rate_lower':ratelow,'rate_upper':ratehigh})
