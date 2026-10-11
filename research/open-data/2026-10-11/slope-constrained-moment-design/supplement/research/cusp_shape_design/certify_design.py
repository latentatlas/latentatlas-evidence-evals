#!/usr/bin/env python3
"""Exact cofactor direction and finite-dictionary primal/dual certificate."""
import argparse,json,sys,time
from pathlib import Path
from flint import arb,arb_mat,ctx
sys.dont_write_bytecode=True
from moment_dictionary import HERE,sha,restore,pack,upper,zero_ball,verify


def need(ok,msg):
    if not ok:raise ArithmeticError(msg)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    ctx.dps=110;start=time.monotonic();inputs=verify()
    dp=HERE/'results/dictionary_16.json';data=json.loads(dp.read_text())
    qp=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';q=json.loads(qp.read_text())
    M=[[restore(row['moments'][n]) for row in data['rows']] for n in range(9)]
    f=list(map(restore,q['root_derivative_enclosures']))
    support=[10,13,15,16];inds=[j-1 for j in support]
    cof=[(-1)**j*arb_mat([[M[n][inds[k]] for k in range(4) if k!=j] for n in range(3)]).det() for j in range(4)]
    need(all(not v.contains(0) for v in cof),'Unresolved cofactor signs')
    z=sum((abs(v) for v in cof),arb(0));w=[v/z for v in cof]
    response=[sum((w[j]*M[n][inds[j]] for j in range(4)),arb(0)) for n in range(9)]
    orientation=1
    if response[4]/f[4]-response[3]/f[3]<0:
        orientation=-1;w=[-v for v in w];response=[-v for v in response]
    a,b=response[3]/f[3],response[4]/f[4];score=b-a
    need(score>0,'Wrong orientation')
    signs=[1 if v>0 else -1 for v in w]
    scales=[max(upper(abs(v)) for v in row) for row in M[:3]]
    A=[[v/s for v in row] for row,s in zip(M[:3],scales)]
    d=[M[4][j]/f[4]-M[3][j]/f[3] for j in range(16)]
    L=arb_mat([[A[n][j] for n in range(3)]+[arb(s)] for j,s in zip(inds,signs)])
    need(not L.det().contains(0),'Singular dual equations')
    dual=L.solve(arb_mat([[d[j]] for j in inds]))
    y=[dual[i,0] for i in range(3)];bound=dual[3,0]
    need(bound>0 and (bound-score).contains(0),'Dual/primal disagreement')
    reduced=[d[j]-sum((A[n][j]*y[n] for n in range(3)),arb(0)) for j in range(16)]
    gaps=[]
    for j in range(16):
        if j in inds:continue
        gap=bound-abs(reduced[j]);need(gap>0,'Dual inactive inequality not strict');gaps.append(gap)
    tau=arb(1)/128
    d3factor=1+zero_ball(tau*abs(a));d4factor=1+zero_ball(tau*abs(b))
    need(d3factor>0 and d4factor>0,'Chosen safe amplitude not nondegenerate')
    ratio=((1+tau*a)*(1-tau*b))/((1+tau*b)*(1-tau*a))
    need(ratio>0 and ratio<1,'Finite leading opening ordering failed')
    eta4=-1/a
    need(eta4>0 and eta4<arb(1)/2,'Quartic-root amplitude outside positive-kernel interval')
    crit=[f[n]+eta4*response[n] for n in range(9)];crit[:4]=[arb(0)]*4
    need(crit[4]<0,'Quartic-root order not exactly four')
    # Rows G,G_t,G_tt against the three original controls lambda,mu,nu.
    controls=[[-crit[n+2]/4,crit[n+4]/16,-crit[n+6]/64] for n in range(3)]
    det=arb_mat(controls).det()
    need(not det.contains(0),'Quartic-root control rank unresolved')
    baseline=json.loads((HERE.parent/'cusp_robustness/results/pinned_cusp_certificate.json').read_text())
    aa=restore(baseline['moment_response'][3])/f[3];bb=restore(baseline['moment_response'][4])/f[4]
    oldscore=bb-aa
    oldratio=((1+tau*aa)*(1-tau*bb))/((1+tau*bb)*(1-tau*aa))
    result={'status':'exact_pinned_direction_dual_optimality_and_quartic_boundary_certified',
        'input_packages':inputs,'dictionary_sha256':sha(dp),'quartic_certificate_sha256':sha(qp),
        'source_sha256':sha(__file__),'frequencies':support,'orientation':orientation,
        'cofactors':pack(cof),'normalizing_sum':pack(z),'weights':pack(w),'moment_response':pack(response),
        'definition':'Exact alternating 3x3 minors of the 3x4 moment matrix at the exact Q, divided by sum of absolute minors, with the recorded orientation.',
        'normalization':'sum |w|=1 exactly; therefore ||h||_infinity<=1. Equality of the supremum norm is not asserted.',
        'a':pack(a),'b':pack(b),'score':pack(score),'linear_gain_over_R07':pack(score/oldscore),
        'optimization':{'class':'h=sum_{j=1}^{16} w_j cos(2ju), A w=0, sum|w_j|<=1',
            'objective':'maximize S=-d_epsilon log C(Q,epsilon)|epsilon=0 = H4/F4-H3/F3',
            'scope':'Unique global maximizer in this finite coefficient-budget class. Not an optimum over all bounded measurable h or for finite width at a nonzero offset.',
            'row_scales':pack(scales),'dual_matrix':pack([[L[i,j] for j in range(4)] for i in range(4)]),
            'dual_y':pack(y),'dual_bound':pack(bound),'reduced_costs':pack(reduced),'inactive_gaps':pack(gaps),
            'proof':'Solve the exact four support equations d_j-A_j^T y=z sign(w_j). Strict |d_j-A_j^Ty|<z off the support and Aw=0 give d.w<=z||w||_1<=z. The cofactor direction attains equality exactly. Strict off-support inequalities and rank three give uniqueness.'},
        'safe_amplitude':pack(tau),'D3_factor':pack(d3factor),'D4_factor':pack(d4factor),
        'C_plus_over_C_minus':pack(ratio),'C_percent_change':pack(100*(ratio-1)),
        'baseline_same_amplitude_C_percent_change':pack(100*(oldratio-1)),
        'quartic_boundary':{'amplitude':pack(eta4),'kernel_multiplier_lower':pack(1-eta4),
            'derivatives':pack(crit),'control_matrix':pack(controls),'control_determinant':pack(det),
            'scope':'At the exact Q and nu=0 the deformed integral has a zero of exactly order four; the (lambda,mu,nu) parameter jets of orders 0,1,2 have rank three. No global catastrophe-set classification follows.'},
        'trust_boundary':'Exact cofactor/duality identities plus saved rigorous moment enclosures; separate rational verification is required.',
        'elapsed_seconds':time.monotonic()-start}
    with args.output.open('x') as f0:json.dump(result,f0,indent=2);f0.write('\n')
    print(json.dumps({k:(v['enclosure'] if isinstance(v,dict) and 'enclosure' in v else v) for k,v in result.items() if k in ('a','b','score','linear_gain_over_R07','C_percent_change','baseline_same_amplitude_C_percent_change')},indent=2))
    print('Quartic zero amplitude',eta4,'control determinant',det,flush=True)


if __name__=='__main__':main()
