#!/usr/bin/env python3
"""Independent piecewise quadrature and local jets; no complex closed-moment formula."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
import mpmath as mp
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dy(x):return mp.mpf(x[0])*mp.power(2,x[1])
def contains(rec,x):return dy(rec['lower'])<x<dy(rec['upper'])
def solve(a_string,dps):
    mp.mp.dps=dps;a=mp.mpf(a_string);fac=1-mp.exp(-1);z=mp.mpf('0.5')
    q1=lambda x:mp.exp(-x)*mp.cos(mp.pi*x)
    qsin=lambda x:mp.exp(-x)*mp.sin(mp.pi*x)
    D=(mp.quad(q1,[0,z])-mp.quad(q1,[z,1]))/fac
    Isin=(mp.quad(qsin,[0,z])-mp.quad(qsin,[z,1]))/fac
    c=Isin/D;q0=lambda x:qsin(x)-c*q1(x)
    def moment(q,d):
        center=z+d;l=center-a;r=center+a
        return (mp.quad(q,[0,l])+mp.quad(lambda x:q(x)*(center-x)/a,[l,r])-mp.quad(q,[r,1]))/fac
    d=mp.findroot(lambda x:moment(q0,x),(0,mp.mpf('0.01')),tol=mp.power(10,-dps+10))
    center=z+d;ql=mp.quad(q0,[center-a,center+a]);qtarget=mp.quad(q1,[center-a,center+a]);b=qtarget/ql
    S=moment(q1,d);delta=mp.mpf(1)/4;f=D*delta;A=f/S;M=A/a
    r=mp.diff(q1,z);t=mp.diff(q1,z,2);u=mp.diff(q1,z,3);p=q0(z);pd=mp.diff(q0,z)
    Gamma=abs(r)/fac;G=2*p*p/abs(r)/fac;B=-(p*t/r-pd)/(3*fac)
    R=(t*t/(36*abs(r))+u/60)/fac;P=B*B/(2*G);Xi=R-P;v=B/G
    C2=delta**3*Gamma/(3*D);C4=delta**5*(Gamma**2/(3*D**2)-Xi/D)
    leading=A-delta-C2/M**2;fourth=leading-C4/M**4
    values={'d':d,'b':b,'S':S,'A':A,'M':M,'scaled_fourth_residual':leading*M**4,
            'leading_error':leading,'fourth_error':fourth,'error_ratio':fourth/leading}
    co={'D':D,'c':c,'f':f,'delta':delta,'Gamma':Gamma,'G':G,'B':B,'v':v,'R':R,'P':P,'Xi':Xi,'C2':C2,'C4':C4}
    residual=max(abs(moment(q0,d)),abs(A*S-f),abs(qtarget-b*ql))
    assert residual<mp.power(10,-dps+15)
    return {'dps':dps,'values':{k:mp.nstr(x,dps-8) for k,x in values.items()},
      'coefficients':{k:mp.nstr(x,dps-8) for k,x in co.items()},'max_residual':mp.nstr(residual,30)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert __debug__
    if args.output.exists():raise FileExistsError(args.output)
    cert=json.loads(args.certificate.read_text());rows=[];comparisons=0;maxdiff=mp.mpf(0)
    for cr in cert['rows']:
        low=solve(cr['a'],80);high=solve(cr['a'],120);checks={}
        for key,value in high['values'].items():
            value=mp.mpf(value);diff=abs(value-mp.mpf(low['values'][key]));maxdiff=max(maxdiff,diff)
            assert contains(cr['intervals'][key],value),(cr['a'],key)
            assert diff<mp.mpf('1e-70'),(key,diff)
            checks[key]={'inside':True,'precision_difference':mp.nstr(diff,30)};comparisons+=1
        for key,value in high['coefficients'].items():
            # delta is exactly 1/4, so its interval is a singleton.
            rec=cert['coefficients'][key];value=mp.mpf(value)
            assert dy(rec['lower'])<=value<=dy(rec['upper']),key
            assert abs(value-mp.mpf(low['coefficients'][key]))<mp.mpf('1e-70')
        rows.append({'a':cr['a'],'low':low,'high':high,'checks':checks})
        print('Independent half-line integral check',cr['a'],'passed',flush=True)
    data={'status':'R23_independent_integrals_passed','precisions':[80,120],'rows':rows,
        'sample_value_comparisons':comparisons,'coefficient_comparisons':len(rows)*13,
        'maximum_sample_precision_difference':mp.nstr(maxdiff,35),
        'source_sha256':sha(__file__),'certificate_sha256':sha(args.certificate),
        'trust_boundary':'Nonrigorous arbitrary-precision quadrature and numerical differentiation at two precisions. Entire tail included by exact periodicity. Distinct from the Arb enclosures and analytic theorem.'}
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(data['status'])
if __name__=='__main__':main()
