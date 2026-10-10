"""Two-parameter Taylor tubes for F + rho K, K=H-alpha F.

The physical family F+epsilon H differs by the positive constant
1+alpha*epsilon, with rho=epsilon/(1+alpha*epsilon). All source jets
are rigorously enclosed integrals; no sampled parameter grid is a proof.
"""
from math import factorial
from flint import arb,arb_poly,arb_mat
from pinned_model import *
from bridge_taylor import operator_powers
from width_shape import numerator as Nnu,partials as gradNnu
from transport_model import numerator4 as N4nu,partials4 as gradN4nu
from fold_jets import transport_jet,implicit_fold,compose,divide
sys.path.insert(0,str(HERE.parent/'cusp_robustness'))
from robust_model import local_geometry


def require(ok,message):
    if not ok:raise ArithmeticError(message)


class Bi:
    """Kronecker-encoded bivariate Arb polynomial; no exponent aliasing."""
    stride=64
    def __init__(self,value=0,zdegree=0):
        self.p=value if isinstance(value,arb_poly) else arb_poly([arb(value)])
        self.zdegree=zdegree
    @staticmethod
    def of(x):return x if isinstance(x,Bi) else Bi(x)
    @classmethod
    def coefficients(cls,items):
        zdegree=max((p for (p,q) in items),default=0)
        require(zdegree<cls.stride,'Bivariate aliasing risk')
        size=max((p+cls.stride*q for p,q in items),default=0)+1
        coeff=[arb(0)]*size
        for (p,q),v in items.items():coeff[p+cls.stride*q]+=v
        return cls(arb_poly(coeff),zdegree)
    def __add__(self,other):
        b=self.of(other);return Bi(self.p+b.p,max(self.zdegree,b.zdegree))
    __radd__=__add__
    def __neg__(self):return Bi(-self.p,self.zdegree)
    def __sub__(self,other):return self+-self.of(other)
    def __rsub__(self,other):return self.of(other)+-self
    def __mul__(self,other):
        b=self.of(other);degree=self.zdegree+b.zdegree
        require(degree<self.stride,'Bivariate product would alias exponents')
        return Bi(self.p*b.p,degree)
    __rmul__=__mul__
    def bound(self,nu_half,rho):
        rows=[[] for _ in range(self.zdegree+1)]
        for index,value in enumerate(self.p):
            p,q=index%self.stride,index//self.stride
            if value==0:continue
            require(p<=self.zdegree,'Invalid encoded exponent')
            rows[p]+=[arb(0)]*max(0,q+1-len(rows[p]));rows[p][q]+=value
        values=[arb_poly(row)(rho) if row else arb(0) for row in rows]
        radius=sum((abs(v)*nu_half**p for p,v in enumerate(values) if p),arb(0))
        return values[0]+zero_ball(radius)


RHO=Bi.coefficients({(0,1):arb(1)})


class Plane:
    def __init__(self,raw,geo,width,cache,rho):
        self.raw=raw;self.index=cache['index'];self.rho=arb(rho);self.rhomax=upper(abs(rho))
        self.x=list(map(restore,raw['center']));self.nu=restore(raw['driver_center'])
        self.v=list(map(restore,raw['predictor']));self.h=restore(raw['driver_half_width'])
        self.R=list(map(restore,raw['radii']));self.allowed=list(map(restore,raw['majorant_domain_half_widths']))
        self.F=list(map(restore,raw['central_derivatives']+geo['extra_central_derivatives']+width['extra_central_derivatives']))
        self.H=list(map(restore,cache['H_derivatives']))
        self.B=list(map(restore,raw['absolute_derivative_bounds']+geo['extra_absolute_bounds']+width['extra_absolute_bounds']))
        kernel=Kernel();self.alpha=restore(kernel.pinned['moment_response'][3])/restore(kernel.q['root_derivative_enclosures'][3])
        self.beta=upper(1+abs(self.alpha));self.K=[h-self.alpha*f for h,f in zip(self.H,self.F)]
        self.Y=midpoint_inverse(J(self.F));self.u=[(-v).mid() for v in matvec(self.Y,self.K[:3])]
        self.A=operator_powers({1:self.v[0],2:-self.v[1]/4,4:self.v[2]/16,6:-arb(1)/64},8)
        self.T=operator_powers({1:self.u[0],2:-self.u[1]/4,4:self.u[2]/16},8)
        self.P={};self.pc={};self.tc={}
        for p in range(9):
            for q in range(9-p):
                row={}
                for a,v in self.A[p].items():
                    for b,w in self.T[q].items():row[a+b]=row.get(a+b,arb(0))+v*w/(factorial(p)*factorial(q))
                self.P[p,q]=row
        self.tight=list(self.R)
    def point(self,kind,n,p,q):
        key=(kind,n,p,q)
        if key not in self.pc:
            c=self.F if kind=='F' else self.K
            self.pc[key]=sum((v*c[n+s] for s,v in self.P[p,q].items()),arb(0))
        return self.pc[key]
    def tail(self,n,p,q):
        key=(n,p,q)
        if key not in self.tc:self.tc[key]=sum((abs(v)*self.B[n+s] for s,v in self.P[p,q].items()),arb(0))
        return self.tc[key]
    def domain(self,radii):
        require(all(upper(abs(v)*self.h+abs(u)*self.rhomax+r)<a for v,u,r,a in zip(self.v,self.u,radii,self.allowed)), 'Two-parameter tube leaves original majorant domain')
    def linear_polys(self,weights,radii):
        self.domain(radii)
        W=operator_powers({1:zero_ball(radii[0]),2:-zero_ball(radii[1])/4,4:zero_ball(radii[2])/16},8)
        fc={};kc={};tail=arb(0)
        for p in range(9):
            for q in range(9-p):
                vf,vk=arb(0),arb(0)
                for r in range(9-p-q):
                    for s,w0 in W[r].items():
                        if w0==0:continue
                        w=w0/factorial(r)
                        if p+q+r<8:
                            vf+=w*sum((a*self.point('F',n+s,p,q) for n,a in weights.items()),arb(0))
                            vk+=w*sum((a*self.point('K',n+s,p,q) for n,a in weights.items()),arb(0))
                        else:
                            tail+=self.h**p*self.rhomax**q*abs(w)*sum((abs(a)*self.tail(n+s,p,q) for n,a in weights.items()),arb(0))
                if p+q<8:fc[p,q]=vf;kc[p,q]=vk
        f,k=Bi.coefficients(fc),Bi.coefficients(kc)
        return f+RHO*k,k,upper(tail*(1+self.rhomax*self.beta)),upper(tail*self.beta)
    def enclose(self,extra=(0,0,0),upto=26,radii=None):
        radii=[upper(a+arb(b)) for a,b in zip(self.tight if radii is None else radii,extra)]
        outg,outk,rg,rk=[],[],[],[]
        for n in range(upto+1):
            g,k,eg,ek=self.linear_polys({n:arb(1)},radii)
            outg.append(g.bound(self.h,self.rho)+zero_ball(eg));outk.append(k.bound(self.h,self.rho)+zero_ball(ek));rg.append(eg);rk.append(ek)
        return outg,outk,rg,rk
    def predictor_polys(self,upto=15):
        return [self.linear_polys({n:arb(1)},(arb(0),)*3) for n in range(upto+1)]
    def contraction(self):
        require(not arb_mat(self.Y).det().contains(0),'Singular plane preconditioner')
        qrows=[];defects=[];remainders=[]
        for i in range(3):
            row=[];remrow=[]
            for j,(shift,factor) in enumerate(((1,arb(1)),(2,-arb(1)/4),(4,arb(1)/16))):
                weights={n+shift:self.Y[i][n]*factor for n in range(3)}
                poly,_,rem,_=self.linear_polys(weights,self.R)
                row.append((Bi(arb(i==j))-poly).bound(self.h,self.rho)+zero_ball(rem));remrow.append(rem)
            defects.append(row);remainders.append(remrow)
            qrows.append(sum((abs(v)*self.R[j]/self.R[i] for j,v in enumerate(row)),arb(0)))
        q=max(upper(v) for v in qrows)
        center=[]
        for i in range(3):
            poly,_,rem,_=self.linear_polys({n:self.Y[i][n] for n in range(3)},(arb(0),)*3)
            center.append(poly.bound(self.h,self.rho)+zero_ball(rem))
        eta=max(upper(abs(v)/r) for v,r in zip(center,self.R))
        require(q<1 and q+eta<1,f'Plane contraction failed: q={q}, eta={eta}')
        self.tight=[upper(r*eta/(1-q)) for r in self.R]
        return {'q':q,'eta':eta,'defects':defects,'defect_remainders':remainders,'residual':center,'tight':self.tight}


class Dual:
    def __init__(self,value,grad=None):self.value=value;self.grad=grad if grad is not None else [arb(0)]*13
    @staticmethod
    def of(v):return v if isinstance(v,Dual) else Dual(arb(v))
    def __add__(self,other):
        b=self.of(other);return Dual(self.value+b.value,[a+c for a,c in zip(self.grad,b.grad)])
    __radd__=__add__
    def __neg__(self):return Dual(-self.value,[-a for a in self.grad])
    def __sub__(self,other):return self+-self.of(other)
    def __rsub__(self,other):return self.of(other)+-self
    def __mul__(self,other):
        b=self.of(other);return Dual(self.value*b.value,[a*b.value+self.value*c for a,c in zip(self.grad,b.grad)])
    __rmul__=__mul__


def rho_polynomial(v,fourth=False):
    a,b,c,d,e,f,g=v[:7];r0,r1,r2,r3,r4,r5=v[7:]
    U=b*r1-c*r0;V=-a*b*r2+b*b*r1+(a*d-b*c)*r0
    if not fourth:
        return a*a*b*(a*r4-b*r3)+(a*c-b*b)*V+(b*c-a*d)*a*U+a*a*(b*e-a*f)*r0
    P3=a*a*b*r3+b*V-a*c*U-a*a*e*r0
    P4=a*a*b*r4+c*V-a*d*U-a*a*f*r0
    P5=a*a*b*r5+d*V-a*e*U-a*a*g*r0
    return a*a*(b*P5-c*P4)-b*b*(a*P4-b*P3)


def rho_gradient(v,fourth=False):
    return rho_polynomial([Dual(x,[arb(i==j) for i in range(13)]) for j,x in enumerate(v)],fourth).grad


def shape(model,cp,kp,pred,driver='nu',fourth=False):
    scale=model.F[3].mid();require(scale>0,'Invalid derivative scale')
    if driver=='nu':
        variables=[('G',n) for n in range(3,12 if fourth else 11)]
        fn,gradient=(N4nu,gradN4nu) if fourth else (Nnu,gradNnu)
    else:
        variables=[('G',n) for n in range(3,10)]+[('K',n) for n in range(6)]
        fn=lambda v:rho_polynomial(v,fourth)
        gradient=lambda v:rho_gradient(v,fourth)
    d=[(cp if kind=='G' else kp)[n]/scale for kind,n in variables]
    polynomials=[pred[n][0 if kind=='G' else 1]* (1/scale) for kind,n in variables]
    errors=[upper(pred[n][2 if kind=='G' else 3]/scale) for kind,n in variables]
    poly=fn(polynomials);bound=poly.bound(model.h,model.rho)
    grad=gradient([v+zero_ball(e) for v,e in zip(d,errors)])
    jet_error=upper(sum((abs(a)*e for a,e in zip(grad,errors)),arb(0)))
    grad=gradient(d)
    chain=[sum((g*(cp if kind=='G' else kp)[n+shift]*factor/scale for g,(kind,n) in zip(grad,variables)),arb(0)) for shift,factor in ((1,arb(1)),(2,-arb(1)/4),(4,arb(1)/16))]
    root_error=upper(sum((abs(v)*r for v,r in zip(chain,model.tight)),arb(0)))
    N=bound+zero_ball(jet_error+root_error);a,b=cp[3]/scale,cp[4]/scale
    if fourth:value=(-2 if driver=='nu' else -128)*N/(a*a*a*b*b*b*b)
    else:value=N/((64 if driver=='nu' else 1)*a*a*b*b*b)
    return {'value':value,'N':N,'polynomial_bound':bound,'jet_error':jet_error,'root_error':root_error,
            'spatial_gradient':chain,'jet_remainders':errors,'scale':scale}


def rho_tangent(cp,kp):
    mp=-16*kp[0]/cp[4]
    lp=(4*kp[1]+cp[5]*mp/4)/cp[3]
    tp=(-kp[2]+cp[4]*lp/4-cp[6]*mp/16)/cp[3]
    return [tp,lp,mp]


def certify(raw,geo,width,cache,rho):
    model=Plane(raw,geo,width,cache,rho);contract=model.contraction()
    cp,kp,_,_=model.enclose(upto=15)
    require(cp[3]>0 and cp[4]<0 and cp[6]<0,'Plane cusp signs failed')
    vnu=cusp_tangent(cp);vrho=rho_tangent(cp,kp)
    require(vnu[2]>arb('0.26') and vnu[2]<arb('0.34'),'Plane mu monotonicity failed')
    pred=model.predictor_polys(upto=15)
    openings={d:shape(model,cp,kp,pred,d) for d in ('nu','rho')}
    require(all(s['value']<0 for s in openings.values()),'Opening derivative sign failed')
    limits=[arb(2)**-8,arb(2)**-12,arb(2)**-19]
    b,kb,_,_=model.enclose(limits,upto=10)
    geometry=local_geometry(cp,b,limits,arb(3)/1000,arb('1e-6'),arb('2e-9'))
    fourth={d:shape(model,cp,kp,pred,d,True) for d in ('nu','rho')}
    S=arb(3)/4000;extra=[2*S,arb('2.22')*S*S,arb('2.10')*S*S*S]
    fd,fk,_,_=model.enclose(extra,upto=26)
    fd[0]=fd[1]=arb(0);fd[2]=zero_ball(upper(geometry['wprime'])*S)
    jets={};transport={}
    for driver in ('nu','rho'):
        if driver=='nu':jet,l,m=transport_jet(fd,vnu[1],K=5)
        else:
            l,m=implicit_fold(fd,5);g2=compose(fd,2,l,m,5);g4=compose(fd,4,l,m,5);k0=compose(fk,0,l,m,5)
            jet=divide([4*vrho[1]*x-16*y for x,y in zip(g2,k0)],g4,5)
        M5=upper(120*abs(jet[5]));M4=upper(abs(fourth[driver]['value']))
        third=-32*openings[driver]['value']+zero_ball(M4*S+M5*S*S/2)
        require(third>0,'Finite fold transport sign failed for '+driver)
        low=(third/(3*arb('2.21')*arb('2.21').sqrt())).lower()
        high=(third/(3*arb('1.80')*arb('1.80').sqrt())).upper()
        transport[driver]={'M4':M4,'M5':M5,'third':third,'rate_lower':low,'rate_upper':high,'jet':jet}
    return pack({'index':model.index,'rho':model.rho,'alpha':model.alpha,'beta':model.beta,
        'rho_predictor':model.u,'contraction':contract,'cusp_derivatives':cp,'K_cusp_derivatives':kp,
        'nu_tangent':vnu,'rho_tangent':vrho,'opening':openings,'neighborhood_derivatives':b,
        'geometry':geometry,'fourth':fourth,'fold_derivatives':fd,'K_fold_derivatives':fk,'transport':transport})
