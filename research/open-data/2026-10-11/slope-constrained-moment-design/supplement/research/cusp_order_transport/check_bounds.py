#!/usr/bin/env python3
"""R31 independent outward-rational reconstruction; no Arb import."""
import sys
sys.dont_write_bytecode=True
import argparse,gzip,hashlib,json
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/'theta_fourth_order'))
from rational_intervals import RI,restore,BITS

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def unpack(x):
    if isinstance(x,dict):
        if 'mid_man_exp' in x:return restore(x)
        return {k:unpack(v) for k,v in x.items()}
    if isinstance(x,list):return [unpack(v) for v in x]
    return x
def overlap(a,b):return a.lo<=b.hi and b.lo<=a.hi
def pair(x):return [str(x.lo),str(x.hi)]
def run(cover):
    index=read(cover/'certificate.json');p=cover/'finite_cover.json.gz';assert sha(p)==index['payload_sha256']
    data=unpack(json.loads(gzip.decompress(p.read_bytes())))
    caps={k:RI(*map(F,v)) for k,v in index['caps'].items()};a0=F(1,16384);c=F(1,50)
    checks=[]
    def ck(name,value):
        assert value,name
        checks.append(name)
    ck('exact_driver_domain',index['driver_interval']==['-1/64','0'] and index['a0']=='1/16384')
    parent=RESEARCH/'cusp_motion_continuation/results/cover';old=read(parent/'certificate.json')
    ck('R29_input_identity',sha(parent/'certificate.json')==index['R29_cover_sha256'])
    ck('R29_driver_identity',old['driver_interval']==index['driver_interval'] and len(old['cells'])==32)
    remainder=RESEARCH/'cusp_finite_design_comparison/results/cover';rem=read(remainder/'certificate.json')
    parameter_rows=[];maxamp=F(0);mindelta=F(1)
    ck('recorded_parameter_cell_count',len(data['parameter_checks'])==32)
    for i,row in enumerate(old['cells']):
        q=parent/row['file'];ck('R29_cell_identity_'+str(i),sha(q)==row['sha256']==data['parameter_checks'][i]['input_sha256'])
        z=unpack(json.loads(gzip.decompress(q.read_bytes())));arc=z['cell']['arc'];co=z['cell']['coefficients'];v=arc['refined_velocity'];par=arc['parameter_box'];D=arc['derivatives']
        fp=v[0]*D[4]-v[1]*D[5]/4+v[2]*D[7]/16-D[9]/64
        ck('f_prime_reconstruction_'+str(i),overlap(fp,z['motion']['derivatives']['f']))
        values={'kappa':-v[0]/par[0],'f_log_derivative':fp/co['f'],'lambda':par[1],'mu':par[2],'lambda_prime':v[1],'mu_prime':v[2]}
        for key,val in values.items():
            ck('cap_'+str(i)+'_'+key,caps[key].lo<val.lo<=val.hi<caps[key].hi)
            ck('recorded_cap_'+str(i)+'_'+key,overlap(val,data['parameter_checks'][i]['values'][key]))
        ck('positive_f_tau_'+str(i),co['f'].lo>0 and par[0].lo>0)
        delta=co['f']/co['D'];ck('amplitude_lower_'+str(i),delta.lo>F('9.17e-10'));mindelta=min(mindelta,delta.lo)
        rr=rem['cells'][i];q=remainder/rr['file'];ck('R30_cell_identity_'+str(i),sha(q)==rr['sha256'])
        r=unpack(json.loads(gzip.decompress(q.read_bytes())))['remainder'];A=r['amplitude_upper'].hi;maxamp=max(maxamp,A)
        ck('amplitude_upper_'+str(i),A<F('9.181e-10') and A/F('2e-5')<a0)
        parameter_rows.append({'index':i,'bounds':{k:pair(vv) for k,vv in values.items()},'delta_lower':str(delta.lo),'amplitude_upper':str(A)})
    rows=data['finite_cells'];n=index['subdivisions'];ck('whole_u_domain',n==1024 and len(rows)==n)
    out=[];peak=None
    for i,row in enumerate(rows):
        ck('dyadic_partition_'+str(i),row['index']==i and row['left'].lo==row['left'].hi==F(i,n) and row['right'].lo==row['right'].hi==F(i+1,n) and row['interval'].lo<=F(i,n)<=F(i+1,n)<=row['interval'].hi)
        u=RI(F(i,n),F(i+1,n));t=row['theta'];x=t['x'];ck('positive_theta_domain_'+str(i),x.lo>F(157,50))
        ell=9+12/(2*x-3)-4*x;ellp=-16*x-96*x/(2*x-3)**2
        S=[RI(0)]*3;ck('finite_theta_terms_'+str(i),[t0['n'] for t0 in t['terms']]==list(range(2,13)))
        for tr in t['terms']:
            # A positive exponential may have an outward ball crossing zero.
            # Retain the entire enclosure; its lower endpoint need not be positive.
            j=tr['n'];e=tr['exponential'];ck('exponential_range_consistent_'+str(i)+'_'+str(j),0<e.hi<1)
            R=j*j*(2*j*j*x-3)/(2*x-3)*e;L=9+12/(2*j*j*x-3)-4*j*j*x;Lp=-16*j*j*x-96*j*j*x/(2*j*j*x-3)**2
            dl=L-ell;S[0]+=R;S[1]+=R*dl;S[2]+=R*(dl**2+Lp-ellp)
        E0=t['tail_errors'][0].hi;ck('theta_tail_error_'+str(i),F(0)<E0<F('1e-140'))
        # E0 encloses 4*13^4*exp(-504), rounded out on a 2^-512 grid.
        # The grid enlarges this tiny input to about 7.46e-155; keep it.
        # The acceptance threshold -1/50 below is never relaxed.
        E1=15*13**2*E0;E2=450*13**4*E0
        S[0]+=RI(0,E0);S[1]+=RI(-E1,E1);S[2]+=RI(-E2,E2)
        Lphi=ell+S[1]/(1+S[0]);Lphip=ellp+S[2]/(1+S[0])-(S[1]/(1+S[0]))**2
        k,flog,lam,mu,nu,lp,mp=[caps[key] for key in ['kappa','f_log_derivative','lambda','mu','nu','lambda_prime','mu_prime']]
        L=Lphi+2*lam*u+4*mu*u**3+6*nu*u**5;Lp=Lphip+2*lam+12*mu*u**2+30*nu*u**4
        r=-flog+4*k+lp*u**2+mp*u**4+u**6+k*u*L
        ru=2*lp*u+4*mp*u**3+6*u**5+k*(L+u*Lp)
        bound=(r+k+a0*ru.abs_upper()).hi
        ck('finite_strict_dissipativity_'+str(i),bound<-c)
        ck('Arb_strict_dissipativity_'+str(i),row['dissipativity_upper'].hi<-c)
        ck('generator_reconstruction_'+str(i),overlap(r,row['generator']) and overlap(ru,row['generator_u']))
        peak=bound if peak is None else max(peak,bound)
        out.append({'index':i,'left':str(F(i,n)),'right':str(F(i+1,n)),'dissipativity_upper':str(bound)})
    alg=read(HERE/'results/algebra.json');ck('exact_tail_algebra',alg['status']=='R31_exact_transport_and_tail_algebra_passed' and all(q['passed'] for q in alg['checks']))
    ck('whole_tail_dissipativity',F(alg['tail_dissipativity_upper_at_one'])<-c and F(alg['tail_derivative_margin'])>0)
    ck('finite_amplitude_class',maxamp/F('2e-5')<a0)
    ck('positive_actual_value_growth',mindelta*(c+caps['kappa'].lo)>F('2.07e-11'))
    return {'status':'R31_rational_generator_and_transport_inputs_passed','rounding_bits':BITS,'check_count':len(checks),'checks':checks,
      'parameters':parameter_rows,'finite_cells':out,'maximum_finite_upper':str(peak),'tail_upper':alg['tail_dissipativity_upper_at_one'],
      'amplitude_upper':str(maxamp),'delta_lower':str(mindelta),'strict_rate':'1/50','all_u_and_all_nu':True,
      'source_sha256':sha(__file__),'rational_helper_sha256':sha(RESEARCH/'theta_fourth_order/rational_intervals.py'),
      'cover_sha256':sha(cover/'certificate.json'),'algebra_sha256':sha(HERE/'results/algebra.json'),
      'R30_cover_sha256':sha(remainder/'certificate.json'),
      'trust_boundary':'Exact dyadic outward reconstruction with recorded Arb transcendental enclosures as explicit inputs. Tail inequalities are analytic plus exact rational checks. Fresh Arb replay checks transcendental generation. This is not formal verification of the analytic argument.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cover-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    result=run(args.cover_dir);args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['check_count']);print('peak',float(F(result['maximum_finite_upper'])))
if __name__=='__main__':main()
