#!/usr/bin/env python3
import json
from flint import arb,ctx
from transport_model import *
from fold_jets import transport_jet
from certify_connection import cusp_tangent

def main():
    ctx.dps=110;verify_inputs()
    old=json.loads((HERE.parent/'cusp_connection/results/connection_certificate.json').read_text())
    geo=json.loads((HERE.parent/'cusp_geometry/results/geometry_certificate.json').read_text())
    for i in (0,28,57):
        cell=ExtendedCell(old['cells'][i],geo['cells'][i],i)
        cp,_=cell.enclose(upto=15);v=cusp_tangent(cp)
        fourth=fourth_at_cusp(cell,cp)
        for val in ('0.001','0.00075','0.0005','0.0001'):
            S=arb(val);d,_=cell.enclose([2*S,arb('2.22')*S*S,arb('2.10')*S*S*S])
            d[0]=d[1]=arb(0)
            d[2]=zero_ball(upper(restore(geo['cells'][i]['uniform_fold']['wprime']))*S)
            jet,_,_=transport_jet(d,v[1],K=5);M5=120*upper(abs(jet[5]))
            B3=-32*restore(geo['cells'][i]['opening_shape']['kprime'])
            margin=B3.lower()-upper(abs(fourth['B4']))*S-M5*S*S/2
            print(i,val,'B4',fourth['B4'].str(10),'M5',M5.str(10),'margin',margin.str(10),flush=True)

if __name__=='__main__':main()
