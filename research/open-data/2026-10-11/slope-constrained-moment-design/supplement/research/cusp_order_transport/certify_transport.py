#!/usr/bin/env python3
"""R31 pointwise generator bounds for exact moment-preserving transport."""
import sys
sys.dont_write_bytecode=True
import argparse,gzip,hashlib,json
from pathlib import Path
from flint import arb,ctx
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/'cusp_uniform_remainder'))
from model import restore,pack,rational,symmetric,upper,absup,sm
CAPS={'kappa':['.00259','.00260'],'f_log_derivative':['.0437','.0451'],
  'lambda':['-3.651','-3.645'],'mu':['8.330','8.336'],'nu':['-1/64','0'],
  'lambda_prime':['.3260','.3264'],'mu_prime':['.2939','.2942']}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def box(bounds):
    a,b=map(rational,bounds);return (a+b)/2+symmetric((b-a)/2)
def unbox(x):
    if isinstance(x,dict):
        if 'mid_man_exp' in x:return restore(x)
        return {k:unbox(v) for k,v in x.items()}
    if isinstance(x,list):return [unbox(v) for v in x]
    return x
def caps():
    parent=RESEARCH/'cusp_motion_continuation/results/cover';index=read(parent/'certificate.json');records=[]
    for row in index['cells']:
        p=parent/row['file'];assert sha(p)==row['sha256'];c=unbox(json.loads(gzip.decompress(p.read_bytes())))
        a=c['cell']['arc'];par=a['parameter_box'];v=a['refined_velocity'];co=c['cell']['coefficients']
        values={'kappa':-v[0]/par[0],'f_log_derivative':c['motion']['derivatives']['f']/co['f'],
          'lambda':par[1],'mu':par[2],'lambda_prime':v[1],'mu_prime':v[2]}
        for k,val in values.items():
            lo,hi=map(rational,CAPS[k]);assert lo<val and val<hi,(row['index'],k,val)
        records.append({'index':row['index'],'input_sha256':sha(p),'values':values})
    return records
def theta_log_jet(u):
    x=arb.pi()*(4*u).exp();terms=[];R=[arb(0)]*3
    l1=9+12/(2*x-3)-4*x;d1=-16*x-96*x/(2*x-3)**2
    for n in range(2,13):
        e=(-(n*n-1)*x).exp();r=n*n*(2*n*n*x-3)/(2*x-3)*e
        ln=9+12/(2*n*n*x-3)-4*n*n*x;dn=-16*n*n*x-96*n*n*x/(2*n*n*x-3)**2
        delta=ln-l1;R[0]+=r;R[1]+=r*delta;R[2]+=r*(delta*delta+dn-d1)
        terms.append({'n':n,'exponential':e})
    n=13;e=arb(-3*(n*n-1)).exp()
    error=[upper(4*n**4*e),upper(60*n**6*e),upper(1800*n**8*e)]
    R[0]+=error[0]/2+symmetric(error[0]/2)
    for j in [1,2]:R[j]+=symmetric(error[j])
    L=l1+R[1]/(1+R[0]);L2=d1+R[2]/(1+R[0])-(R[1]/(1+R[0]))**2
    return {'x':x,'terms':terms,'tail_errors':error,'relative_tail_jets':R,'log_derivative':L,'log_second_derivative':L2}
def generator(u,theta):
    b={k:box(v) for k,v in CAPS.items()};k=b['kappa'];flog=b['f_log_derivative']
    lam,mu,nu=[b[x] for x in ['lambda','mu','nu']];lp,mp=[b[x] for x in ['lambda_prime','mu_prime']]
    L=theta['log_derivative']+2*lam*u+4*mu*u**3+6*nu*u**5
    L2=theta['log_second_derivative']+2*lam+12*mu*u*u+30*nu*u**4
    r=-flog+4*k+lp*u*u+mp*u**4+u**6+k*u*L
    ru=2*lp*u+4*mp*u**3+6*u**5+k*(L+u*L2)
    dissipativity=r+k+rational('1/16384')*absup(ru)
    return {'weight_log_derivative':L,'weight_log_second_derivative':L2,'generator':r,
      'generator_u':ru,'dissipativity_upper':upper(dissipativity)}
def certify(output,subdivisions):
    assert __debug__;ctx.dps=120;assert not output.exists();output.mkdir(parents=True)
    parameters=caps();rows=[];h=arb(1)/subdivisions
    for i in range(subdivisions):
        lo=i*h;hi=(i+1)*h;u=(lo+hi)/2+symmetric(h/2);theta=theta_log_jet(u);g=generator(u,theta)
        rows.append({'index':i,'left':lo,'right':hi,'interval':u,'theta':theta,**g})
    peak=max(x['dissipativity_upper'] for x in rows);worst=max(range(len(rows)),key=lambda i:float(rows[i]['dissipativity_upper']))
    raw=(json.dumps(pack({'parameter_checks':parameters,'finite_cells':rows}),sort_keys=True,separators=(',',':'))+'\n').encode()
    payload=output/'finite_cover.json.gz';payload.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
    data={'status':'R31_generator_cover_computed','dps':120,'driver_interval':['-1/64','0'],
      'finite_u_interval':['0','1'],'subdivisions':subdivisions,'theta_terms':12,'a0':'1/16384','caps':CAPS,
      'maximum_finite_dissipativity_upper':peak,'worst_cell':worst,'payload_sha256':sha(payload),
      'source_sha256':sha(__file__),'R29_cover_sha256':sha(RESEARCH/'cusp_motion_continuation/results/cover/certificate.json'),
      'trust_boundary':'Full parameter caps from frozen R29 cells. Fresh transcendental interval evaluation of log-theta jets on a gap-free u cover. Infinite theta-series and u>=1 bounds require the separate analytic/rational tail proof.'}
    (output/'certificate.json').write_text(json.dumps(pack(data),indent=2)+'\n')
    print('subdivisions',subdivisions,'peak upper',float(peak),'worst cell',worst,flush=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--subdivisions',type=int,default=1024);args=ap.parse_args()
    assert args.subdivisions>0 and args.subdivisions&(args.subdivisions-1)==0;certify(args.output_dir,args.subdivisions)
if __name__=='__main__':main()
