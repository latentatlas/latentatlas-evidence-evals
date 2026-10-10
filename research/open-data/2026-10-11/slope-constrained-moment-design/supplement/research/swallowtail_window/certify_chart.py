#!/usr/bin/env python3
"""Certified 0/2/4-color cells; unresolved cells remain explicitly blank."""
import argparse,json,time
from pathlib import Path
import numpy as np
from chart import *


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=90;start=time.monotonic();mp=HERE/'results/model_v2.json';wp=HERE/'results/window_certificate.json'
    data=json.loads(mp.read_text());cert=json.loads(wp.read_text());c=Chart(data,cert)
    inflections=[c.r*(arb('-0.71').union(arb('-0.70'))),c.r*(arb('0.70').union(arb('0.71')))]
    ir=[]
    for k,z in enumerate(inflections):
        v=[c.value(s,c.alpha,c.beta,2) for s in (z.lower(),z.upper())]
        signs=(1,-1) if k==0 else (-1,1)
        need(all(sign*x>0 for sign,x in zip(signs,v)),'Uniform inflection bracket failed')
        ir.append(v)
    stripes=[];grid=[];counts={0:0,2:0,4:0,'unresolved':0}
    for i in range(64):
        left=-arb(4)+arb(i)/8;right=left+arb(1)/8;a=left.union(right)
        candidates=sorted(float(z.real) for z in np.roots([4,0,-6,float(a.mid())]) if abs(z.imag)<1e-10)
        critical=[];ok=True
        for x in candidates:
            h=max(.009,2.0*.0625/max(abs(12*x*x-6),.05))
            found=False
            for trial in range(6):
                lo=(c.r*arb(str(x-h))).mid();hi=(c.r*arb(str(x+h))).mid();z=lo.union(hi)
                if not abs(z)<3*c.r:break
                vl,vr=c.value(lo,a,c.beta,1),c.value(hi,a,c.beta,1)
                d2=c.value(z,a,c.beta,2)
                sign=1 if 12*x*x-6>0 else -1
                if sign*vl<0 and sign*vr>0 and sign*d2>0:
                    critical.append({'left':lo,'right':hi,'s_box':z,'g1_left':vl,'g1_right':vr,'g2_box':d2,'derivative_sign':sign});found=True;break
                h*=1.4
            if not found:ok=False;break
        if ok and len(critical)==3:
            ok=all(critical[j]['right']<critical[j+1]['left'] for j in range(2))
        inf_values=[c.value(z,a,c.beta,1) for z in inflections]
        if ok and len(critical)==1:ok=(inf_values[0]<0 or inf_values[1]>0)
        if len(candidates) not in (1,3):ok=False
        stripes.append({'index':i,'alpha_left':left,'alpha_right':right,'alpha_box':a,
            'critical_graph_certified':bool(ok),'critical_points':critical,'inflection_G1_values':inf_values})
        cells=[]
        for j in range(56):
            bl=-arb(3)/2+arb(j)/8;br=bl+arb(1)/8;b=bl.union(br)
            if ok:
                vals=[c.value(z['s_box'],a,b,0) for z in critical]
                signs=[1]+[1 if v>0 else -1 if v<0 else 0 for v in vals]+[1]
                count=sum(x!=y for x,y in zip(signs,signs[1:])) if 0 not in signs else None
                need(count in (None,0,2,4),'Impossible root parity')
            else:vals=[];count=None
            counts['unresolved' if count is None else count]+=1
            cells.append({'row':j,'beta_left':bl,'beta_right':br,'count':count,'critical_values':vals})
        grid.append(cells)
        if i%16==0:print('Certified control stripes',i+1,'of 64',flush=True)
    need(all(counts[k]>0 for k in (0,2,4)),'Missing root-count region')
    out=pack({'status':'certified_chart_cells_with_explicit_unresolved_band',
        'input_sha256':{'model_v2.json':sha(mp),'window_certificate.json':sha(wp)},
        'source_sha256':{n:sha(HERE/n) for n in ('certify_chart.py','chart.py','model_v2.py')},
        'lambda_section':c.L,'root_scale':c.r,'affine_matrix':c.E,
        'definition':'(mu-muQ,nu)=E*(L^2*(beta-3/4),L^(3/2)*alpha). E is the recorded exact dyadic matrix. This is an explicit affine display chart of original controls, not an asserted exact quartic normal form.',
        'alpha_domain':c.alpha,'beta_domain':c.beta,'physical_control_magnitudes':c.maxp,
        'second_remainder_derivative_bounds':c.bounds,'inflection_boxes':inflections,'inflection_bracket_G2':ir,
        'stripes':stripes,'cells':grid,'counts':counts,
        'scope':'Every colored closed cell is proved to have its declared number of simple real zeros for all its parameters, in the same physical root window. Gray cells are unresolved by this grid certificate; they are not assigned a count. The separate global critical-value theorem still applies.',
        'elapsed_seconds':time.monotonic()-start})
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print('Certified chart counts',counts,flush=True)


if __name__=='__main__':main()
