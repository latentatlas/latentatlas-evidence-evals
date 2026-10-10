"""R10: fourth-order-zero-centered Taylor model in original controls."""
import hashlib,json,sys
from pathlib import Path
from math import factorial
sys.dont_write_bytecode=True
from flint import arb,arb_mat,ctx
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'cusp_shape_design'
sys.path.insert(0,str(BASE))
from shape_model import restore,pack,upper,zero_ball
from validated_flow import absolute_derivative_bounds,midpoint_inverse,matmul,matvec,norm_mat,norm_vec


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,msg):
    if not v:raise ArithmeticError(msg)
def verify():
    old=json.loads((BASE/'manifest.json').read_text())
    need(sha(BASE/'manifest.json')=='6f2ae4a0518eb3ebf974d0e53ed9ea0aef07aa816336375b46befda74102d642','R09 manifest changed')
    for row in old['files']:need(sha(BASE/row['path'])==row['sha256'],'R09 file changed '+row['path'])
    return {'package':'cusp_shape_design','files':len(old['files']),'manifest_sha256':sha(BASE/'manifest.json')}


class Model:
    def __init__(self,data):
        self.c=list(map(restore,data['normalized_exact_Q_derivatives']))
        self.B=list(map(restore,data['normalized_absolute_bounds']))
        self.domain=list(map(restore,data['domain']))
        self.order=8;self.terms=[]
        for a in range(9):
            for b in range(9-a):
                for c in range(9-a-b):
                    for d in range(9-a-b-c):
                        self.terms.append(((a,b,c,d),a+2*b+4*c+6*d,
                            arb(1)/(factorial(a)*factorial(b)*factorial(c)*factorial(d))))
    def derivatives(self,x,upto=8):
        x=list(map(arb,x));need(len(x)==4,'Four coordinates required')
        need(all(upper(abs(v))<=r for v,r in zip(x,self.domain)),'Taylor request leaves certified domain')
        need(upto<=12,'Derivative request exceeds recorded jet')
        u=[x[0],-x[1]/4,x[2]/16,-x[3]/64]
        powers=[[v**j for j in range(9)] for v in u]
        value=[arb(0) for _ in range(upto+1)];rem=[arb(0) for _ in value]
        for exps,shift,coeff in self.terms:
            for p,k in zip(powers,exps):coeff*=p[k]
            if sum(exps)<8:
                for n in range(upto+1):value[n]+=coeff*self.c[n+shift]
            else:
                mag=upper(abs(coeff))
                for n in range(upto+1):rem[n]+=mag*self.B[n+shift]
        return [v+zero_ball(r) for v,r in zip(value,rem)]


def controls(ds,orders=(0,1,2)):
    return [[-ds[n+2]/4,ds[n+4]/16,-ds[n+6]/64] for n in orders]
def inverse(ds,orders=(0,1,2)):
    return midpoint_inverse(controls(ds,orders))
def contraction(Y,J,f,r):
    need(not arb_mat(Y).det().contains(0),'Singular contraction preconditioner')
    yj=matmul(Y,J)
    q=norm_mat([[(arb(i==j)-yj[i][j])*r[j]/r[i] for j in range(len(r))] for i in range(len(r))])
    eta=norm_vec([v/rr for v,rr in zip(matvec(Y,f),r)])
    need(q+eta<1,'Contraction inequality failed')
    return q,eta
