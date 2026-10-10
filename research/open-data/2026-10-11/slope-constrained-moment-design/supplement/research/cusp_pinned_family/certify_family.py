#!/usr/bin/env python3
"""Full two-parameter domain, including both sets of branch joins."""
import argparse,json,time
from pathlib import Path
from flint import arb,ctx
from pinned_model import HERE,Kernel,verify_inputs,sha,restore,pack,upper,zero_ball
from plane_model import Plane,certify,require


def affine(raw,row,nu,rho):
    return [restore(x)+restore(v)*(nu-restore(raw['driver_center']))+restore(u)*rho
            for x,v,u in zip(raw['center'],raw['predictor'],row['rho_predictor'])]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=100;start=time.monotonic();inputs=verify_inputs();kernel=Kernel()
    paths=[HERE.parent/p/'results'/n for p,n in (('cusp_connection','connection_certificate.json'),('cusp_geometry','geometry_certificate.json'),('cusp_width','width_certificate.json'))]
    data=[json.loads(p.read_text()) for p in paths];old=data[0]
    cache_index=json.loads((HERE/'cache/index.json').read_text())
    for item in cache_index['files']:require(sha(HERE/'cache'/item['file'])==item['sha256'],'Changed H jet')
    alpha=restore(kernel.pinned['moment_response'][3])/restore(kernel.q['root_derivative_enclosures'][3])
    physical=zero_ball(arb(1)/2);factor=1+alpha*physical
    require(factor>0,'Physical normalization is not positive')
    mapped=[e/(1+alpha*e) for e in (-arb(1)/2,arb(1)/2)]
    require(mapped[0]>-arb(1)/2 and mapped[1]<arb(3)/4,'Physical amplitude leaves rho cover')
    slabs=[]
    for j in range(4):
        left=-arb(1)/2+arb(5)*j/16;right=left+arb(5)/16;rho=left.union(right)
        rows=[]
        for i in range(58):
            cache=json.loads((HERE/'cache'/f'cell_{i:02}.json').read_text())
            row=certify(*(d['cells'][i] for d in data),cache,rho)
            model=Plane(*(d['cells'][i] for d in data),cache,rho)
            row['preconditioner']=pack(model.Y)
            for driver in ('nu','rho'):
                require(restore(row['transport'][driver]['rate_lower'])>arb('0.0003'), 'Readable lower rate failed')
                require(restore(row['transport'][driver]['rate_upper'])<arb('0.003'), 'Readable upper rate failed')
            rows.append(row)
            if i%10==0 or i==57:print('Full family slab',j+1,'of 4, cell',i+1,'of 58 passed',flush=True)
        slabs.append({'index':j,'left':pack(left),'right':pack(right),'rho':pack(rho),'cells':rows})
    nu_joins=[]
    for slab in slabs:
        rho=restore(slab['rho'])
        for i in range(57):
            a,b=old['cells'][i:i+2];nu=restore(a['driver_left'])
            require(nu==restore(b['driver_right']),'Gap in nu cover')
            ca=affine(a,slab['cells'][i],nu,rho);cb=affine(b,slab['cells'][i+1],nu,rho)
            # Preserve the common rho correlation before bounding the
            # difference; subtracting two independent affine balls is wider.
            delta=[restore(xa)+restore(va)*(nu-restore(a['driver_center']))-restore(xb)-restore(vb)*(nu-restore(b['driver_center']))+(restore(ua)-restore(ub))*rho for xa,va,ua,xb,vb,ub in zip(a['center'],a['predictor'],slab['cells'][i]['rho_predictor'],b['center'],b['predictor'],slab['cells'][i+1]['rho_predictor'])]
            ratio=[upper((abs(d)+restore(r))/restore(R)) for d,r,R in zip(delta,slab['cells'][i]['contraction']['tight'],b['radii'])]
            require(all(x<1 for x in ratio),'Nu root-containment join failed')
            nu_joins.append(pack({'slab':slab['index'],'left_index':i,'nu':nu,'ratios':ratio}))
    rho_joins=[]
    for j in range(3):
        require(slabs[j]['right']==slabs[j+1]['left'],'Gap in rho cover')
        for i in range(58):
            a,b=slabs[j]['cells'][i],slabs[j+1]['cells'][i]
            require(a['rho_predictor']==b['rho_predictor'],'Rho-boundary uniqueness boxes differ')
            rho_joins.append({'left_slab':j,'cell':i,'shared_rho':slabs[j]['right'],
                              'reason':'Same exact affine predictor and same original uniqueness radii for every nu in this cell; uniqueness identifies both solutions.'})
    endpoint=[];qcenter=list(map(restore,kernel.q['center_exact_dyadic']));qr=restore(kernel.q['radius'])
    for slab in slabs:
        rho=restore(slab['rho']);first=slab['cells'][0];last=slab['cells'][-1]
        aq=affine(old['cells'][0],first,arb(0),rho)
        ratios=[upper((abs(x-y)+qr)/restore(r)) for x,y,r in zip(qcenter,aq,old['cells'][0]['radii'])]
        require(all(r<1 for r in ratios),'Pinned Q not identified with cusp sheet')
        amu=affine(old['cells'][-1],last,arb(-29),rho)[2]+zero_ball(restore(last['contraction']['tight'][2]))
        require(amu<0 and qcenter[2]-qr>0,'Unique sextic crossing signs failed')
        endpoint.append(pack({'slab':slab['index'],'Q_containment_ratios':ratios,'mu_at_minus_29':amu}))
    result={'schema':'R08-cusp-sheet-and-two-direction-fold-transport-v1','status':'arb_full_two_parameter_domain_passed',
        'physical_epsilon':pack(physical),'alpha':pack(alpha),'positive_normalization':pack(factor),'rho_endpoints_for_physical_epsilon':pack(mapped),
        'normalized_family':'G=F+rho K, K=H-alpha F, alpha=H_ttt(Q)/F_ttt(Q), rho=epsilon/(1+alpha epsilon).',
        'scope':'One analytic cusp sheet for every nu in [-29,0], physical epsilon in [-1/2,1/2], containing the exact fixed Q edge; the same finite local root window and strict fold nesting in each of nu and rho.',
        'input_packages':inputs,'input_certificates':{str(p.relative_to(HERE.parent)):sha(p) for p in paths},
        'H_cache_index_sha256':sha(HERE/'cache/index.json'),'kernel_certificate_sha256':sha(kernel.pinned_path),
        'source_sha256':{n:sha(HERE/n) for n in ('pinned_model.py','plane_model.py','certify_family.py')},
        'slabs':slabs,'nu_joins':nu_joins,'rho_joins':rho_joins,'Q_and_sextic_identification':endpoint,
        'readable_normalized_rate_bounds':{'nu':['0.0003','0.003'],'rho':['0.0003','0.003']},
        'trust_boundary':'Analytic proof plus frozen F jets/majorants and new rigorously integrated H jets; no claim of external or formal proof-assistant verification.',
        'elapsed_seconds':time.monotonic()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('232 cells, 228 nu joins and 174 rho joins passed',flush=True)


if __name__=='__main__':main()
