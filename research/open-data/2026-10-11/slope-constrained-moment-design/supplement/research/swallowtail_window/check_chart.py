#!/usr/bin/env python3
"""Independent rational reconstruction of all colored chart cells."""
import argparse,json,time
from pathlib import Path
from check_window import *


class RationalChart:
    def __init__(self,model,cert):
        self.m=model;self.L=Q(2)**-24;self.r=Q(2)**-12
        self.E=[list(map(exact,row)) for row in cert['affine_matrix']]
        self.a=D(-4,4);self.b=D(-Q(3,2),Q(11,2));self.cache={}
        maxp=[v.abs_upper() for v in self.params(self.a,self.b)]
        assert all(v<Q(2)**-34 for v in maxp)
        self.bounds=self.m.derivatives([sym(3*self.r),self.L]+[sym(v) for v in maxp],12)
        for n in (13,14):
            rad=3*self.r*self.m.B[n+1]+self.L*self.m.B[n+2]/4+maxp[0]*self.m.B[n+4]/16+maxp[1]*self.m.B[n+6]/64
            self.bounds.append(self.m.c[n]+sym(rad))
    def params(self,a,b):return mv(self.E,[self.L**2*(b-Q(3,4)),self.r**3*a])
    def axis(self,s):
        key=(s.lo,s.hi)
        if key not in self.cache:self.cache[key]=self.m.derivatives([s,self.L,0,0],8)
        return self.cache[key]
    def value(self,s,a,b,n=0):
        s,a,b=map(D.of,(s,a,b));assert s.abs_upper()<=3*self.r and n<=2
        base=self.axis(s)
        ca=self.r**3*(self.E[0][1]*base[n+4]/16-self.E[1][1]*base[n+6]/64)
        cb=self.L**2*(self.E[0][0]*base[n+4]/16-self.E[1][0]*base[n+6]/64)
        v=base[n]+ca*a+cb*(b-Q(3,4));p=self.params(a,b)
        u=p[0].abs_upper()/16;w=p[1].abs_upper()/64
        rem=(u*u*self.bounds[n+8].abs_upper()+2*u*w*self.bounds[n+10].abs_upper()+w*w*self.bounds[n+12].abs_upper())/2
        return v+sym(rem)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.monotonic();mp=HERE/'results/model_v2.json';cp=HERE/'results/chart_certificate.json'
    data=json.loads(mp.read_text());cert=json.loads(cp.read_text())
    for n,h in cert['source_sha256'].items():assert sha(HERE/n)==h
    for n,h in cert['input_sha256'].items():assert sha(HERE/'results'/n)==h
    c=RationalChart(Taylor(data),cert);inf=list(map(read,cert['inflection_boxes']))
    for i,z in enumerate(inf):
        for s,sign in zip((z.lo,z.hi),(1,-1) if i==0 else (-1,1)):
            assert (sign*c.value(s,c.a,c.b,2)).lo>0
    counts={0:0,2:0,4:0,'unresolved':0};graphs=0
    assert len(cert['stripes'])==64 and len(cert['cells'])==64
    for i,(stripe,cells) in enumerate(zip(cert['stripes'],cert['cells'])):
        left=-Q(4)+Q(i,8);right=left+Q(1,8);a=D(left,right)
        assert exact(stripe['alpha_left'])==left and exact(stripe['alpha_right'])==right and len(cells)==56
        critical=stripe['critical_points'];ok=stripe['critical_graph_certified']
        if ok:
            assert len(critical) in (1,3);graphs+=1
            for z in critical:
                lo,hi=exact(z['left']),exact(z['right']);assert lo<hi
                box=read(z['s_box']);assert box.lo<=lo<hi<=box.hi
                sign=z['derivative_sign'];assert sign in (-1,1)
                assert (sign*c.value(lo,a,c.b,1)).hi<0
                assert (sign*c.value(hi,a,c.b,1)).lo>0
                assert (sign*c.value(box,a,c.b,2)).lo>0
            if len(critical)==3:
                assert all(exact(critical[j]['right'])<exact(critical[j+1]['left']) for j in (0,1))
            else:assert c.value(inf[0],a,c.b,1).hi<0 or c.value(inf[1],a,c.b,1).lo>0
        for j,cell in enumerate(cells):
            bl=-Q(3,2)+Q(j,8);br=bl+Q(1,8);b=D(bl,br)
            assert exact(cell['beta_left'])==bl and exact(cell['beta_right'])==br
            count=cell['count']
            if count is None:counts['unresolved']+=1;continue
            assert ok and count in (0,2,4)
            vals=[c.value(read(z['s_box']),a,b,0) for z in critical]
            assert all(away(v) for v in vals)
            signs=[1]+[1 if v.lo>0 else -1 for v in vals]+[1]
            assert sum(x!=y for x,y in zip(signs,signs[1:]))==count
            counts[count]+=1
        if i%16==0:print('Rational control stripe',i+1,'of 64',flush=True)
    assert {str(k):v for k,v in counts.items()}==cert['counts']
    out={'status':'independent_rational_2804_colored_cells_passed','counts':counts,'stationary_graph_stripes':graphs,
        'certificate_sha256':sha(cp),'model_sha256':sha(mp),'source_sha256':sha(__file__),
        'trust_boundary':'R09 integral balls and R10 unnormalized positive majorants are inputs. Affine directional combinations, all new Taylor remainders, inflection/critical brackets and every colored-cell critical-value sign are rebuilt with rational endpoints. Unresolved cells remain unclassified.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(out['status'],counts,flush=True)


if __name__=='__main__':main()
