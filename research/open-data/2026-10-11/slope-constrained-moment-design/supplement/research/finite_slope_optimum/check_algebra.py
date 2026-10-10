#!/usr/bin/env python3
"""Independent Laurent-polynomial identities and rational certificate checks."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
from exact_interval import QI,poly_integral,five_piece_moment

HERE=Path(__file__).resolve().parent
ZERO=(0,0,0)
class P:
    def __init__(self,value=0):
        self.p=(value.p.copy() if isinstance(value,P) else
                {e:F(v) for e,v in value.items() if v} if isinstance(value,dict) else
                {ZERO:F(value)} if value else {})
    def __add__(self,o):
        out=self.p.copy()
        for e,v in P(o).p.items():out[e]=out.get(e,F(0))+v
        return P(out)
    __radd__=__add__
    def __neg__(self):return P({e:-v for e,v in self.p.items()})
    def __sub__(self,o):return self+-P(o)
    def __rsub__(self,o):return P(o)+-self
    def __mul__(self,o):
        out={}
        for e,v in self.p.items():
            for h,w in P(o).p.items():
                key=tuple(a+b for a,b in zip(e,h));out[key]=out.get(key,F(0))+v*w
        return P(out)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=P(o);assert len(o.p)==1
        e,v=next(iter(o.p.items()))
        return self*P({tuple(-a for a in e):1/v})
    def __rtruediv__(self,o):return P(o)/self
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        ans=P(1)
        for _ in range(n):ans=ans*self
        return ans
    def __eq__(self,o):return self.p==P(o).p
    def derivative(self,i):
        out={}
        for e,v in self.p.items():
            if e[i]:
                k=list(e);k[i]-=1;out[tuple(k)]=v*e[i]
        return P(out)
def var(i):
    e=[0,0,0];e[i]=1;return P({tuple(e):1})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def check(certificate):
    groups=[]
    def record(name,ok,reason):
        assert ok,name
        groups.append({'name':name,'passed':True,'reason':reason})
    d,a,beta=[var(i) for i in range(3)];cm=d-F(1,2);cp=d+F(1,2)
    q=[P(F(-1,4)),-beta/4,P(1),beta]
    Fbal=2*d+3*beta*d**2+beta*a**2
    b=d**2+beta*d**3+beta*d/2+a**2/3+beta*d*a**2
    T=F(1,2)-2*d**2-2*beta*d**3-F(2,3)*a**2-2*beta*d*a**2
    record('five_piece_lower_moment',five_piece_moment([P(1)],cm,cp,a)==0,
           'Exact five-piece integration; centers separated by one preserve the lower moment.')
    record('five_piece_target',five_piece_moment(q,cm,cp,a)==T,
           'Direct polynomial antiderivatives; no assumed target formula in the integration.')
    left=poly_integral(q,cm-a,cm+a)/(2*a)
    right=poly_integral(q,cp-a,cp+a)/(2*a)
    record('two_balance_equations',right-left==Fbal and (left+right)/2==b,
           'Both cell averages equal b exactly when the center-shift equation vanishes.')
    record('target_stationarity',T.derivative(0)==-2*Fbal,
           'Differentiating the independently integrated target recovers the balance equation.')
    gain=T-(F(1,2)-F(2,3)*a**2)
    record('positive_gain_identity',gain-2*d**2*(1+2*beta*d)==-2*d*Fbal,
           'Exact identity modulo the balance equation; no asymptotic truncation.')
    # Base constants and general movement formulas are evaluated from q and its derivatives.
    beta0=F(1,4);q0=[F(-1,4),-beta0/4,F(1),beta0]
    roots=[F(-1,2),F(1,2)];qp=[2*x+beta0*(3*x*x-F(1,4)) for x in roots]
    qpp=[2+6*beta0*x for x in roots];sig=[-1,1]
    D=poly_integral(q0,F(-1),roots[0])-poly_integral(q0,*roots)+poly_integral(q0,roots[1],F(1))
    G=2*sum(1/abs(v) for v in qp);B=sum(s*q2/q1 for s,q1,q2 in zip(sig,qp,qpp))/3
    b2=B/G;kappa=[(b2-q2/6)/q1 for q1,q2 in zip(qp,qpp)]
    Gamma=sum(abs(v) for v in qp);delta=F(1,8)/D;C=delta**3*Gamma/(3*D)
    record('base_constants_and_general_shifts',
           (D,G,B,b2,Gamma,delta,C)==(F(1,2),F(256,63),F(244,189),F(61,192),F(2),F(1,4),F(1,48))
           and kappa==[F(-1,8),F(-1,8)],
           'Differentiate q at the two roots, then apply the general G inverse B and center formulas.')
    # Exact scalar sufficient bounds used in the analytic uniform-example proof.
    dl=F(-1,100);amax=F(1,5)
    values={'F_left_max':2*dl+3*beta0*dl*dl+beta0*amax*amax,
            'F_d_min':2+6*beta0*dl,
            'qprime_left_max':2*F(-3,10)+beta0*(3*F(-3,10)**2-F(1,4)),
            'qprime_right_min':2*F(29,100)+beta0*(3*F(29,100)**2-F(1,4)),
            'qsecond_min':2-6*beta0,
            'T_lower':F(1,2)-2*dl*dl-F(2,3)*amax*amax,
            'T_plus_aTprime_lower':F(1,2)-2*dl*dl-2*amax*amax,
            'gain_factor_lower':1+2*beta0*dl,
            'cell_gap_lower':1-2*amax}
    record('uniform_geometric_and_monotonicity_bounds',
           values['F_left_max']<0 and values['F_d_min']>0 and values['qprime_left_max']<0
           and values['qprime_right_min']>0 and values['qsecond_min']>0
           and values['T_lower']>F(47,100) and values['T_plus_aTprime_lower']>0
           and values['gain_factor_lower']>0 and values['cell_gap_lower']>0,
           'Rational inequalities for every 0<a<=1/5, combined with the symbolic identities and analytic proof.')
    cert=json.loads(Path(certificate).read_text());rows=[]
    for row in cert['rows']:
        width=F(row['a']);iv={k:QI.from_data(v) for k,v in row['intervals'].items()}
        center=iv['center_shift'];Fnum=lambda x:2*x+3*beta0*x*x+beta0*width*width
        assert Fnum(center.lo)<=0<=Fnum(center.hi)
        assert center.hi-center.lo<=F(1,100*2**210)
        assert [str(Fnum(center.lo)),str(Fnum(center.hi))]==row['root_endpoint_sign_values']
        cmq=iv['left_center'];cpq=iv['right_center']
        direct0=five_piece_moment([F(1)],cmq,cpq,width)
        direct1=five_piece_moment(q0,cmq,cpq,width)
        assert direct0.lo<=0<=direct0.hi and direct1.overlaps(iv['unit_target'])
        assert direct0.hi-direct0.lo<F('1e-55') and direct1.hi-direct1.lo<F('1e-55')
        for c in [cmq,cpq]:
            avg=poly_integral(q0,c-width,c+width)/(2*width)
            assert avg.overlaps(iv['dual_coefficient'])
        assert (iv['amplitude']*direct1).lo<=F(1,8)<=(iv['amplitude']*direct1).hi
        assert (iv['amplitude']/width).overlaps(iv['slope_budget'])
        rows.append({'a':str(width),'root_bracket_passed':True,'direct_moments_passed':True,
                     'direct_cell_balances_passed':True})
    record('six_rational_certificates_direct_integrals',len(rows)==6,
           'Read rational root brackets, integrate all five pieces and both balance cells independently of the producer target formula. Interval overlap is corroboration, not an independent optimality proof.')
    return {'status':'exact_algebra_and_certificate_crosschecks_passed','check_groups':len(groups),
            'checks':groups,'rows':rows,'uniform_rational_bounds':{k:str(v) for k,v in values.items()},
            'constants':{'D':str(D),'Gamma':str(Gamma),'G':str(G),'B':str(B),'b2':str(b2),
                         'center2':[str(v) for v in kappa],'delta0':str(delta),'C':str(C)},
            'source_sha256':sha(Path(__file__)),'interval_substrate_sha256':sha(HERE/'exact_interval.py'),
            'certificate_sha256':sha(certificate),
            'trust_boundary':'Exact finite polynomial algebra and rational interval checks. Analytic theorem, uniqueness and literature novelty are not mechanically proved.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,default=HERE/'results/certificate.json');ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    out=check(args.certificate);args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'check_groups':out['check_groups']}))
if __name__=='__main__':main()
