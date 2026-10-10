#!/usr/bin/env python3
"""Small diagnostic before a full finite-width certificate."""
import json
import sys
from pathlib import Path
from flint import arb,ctx
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'cusp_geometry'))
from geometry_model import CorrelatedCell,restore,upper,zero_ball,verify_inputs
from certify_connection import cusp_tangent
from fold_jets import transport_jet

def main():
    ctx.dps=110
    verify_inputs()
    r03=json.loads((HERE.parent/'cusp_connection/results/connection_certificate.json').read_text())
    r04=json.loads((HERE.parent/'cusp_geometry/results/geometry_certificate.json').read_text())
    for i in (0,28,57):
        cell=CorrelatedCell(r03['cells'][i],i)
        cp=list(map(restore,r04['cells'][i]['cusp_derivatives']))
        v=cusp_tangent(cp)
        for sv in ('0.001','0.0001','0.00001'):
            S=arb(sv)
            extra=[2*S,arb('2.22')*S*S,arb('2.10')*S*S*S]
            d,_=cell.enclose(extra,upto=14)
            d.extend(zero_ball(b) for b in cell.B[15:23])
            d[0]=d[1]=arb(0)
            wp=restore(r04['cells'][i]['uniform_fold']['wprime'])
            d[2]=zero_ball(upper(wp)*S)
            jet,_,_=transport_jet(d,v[1])
            M4=upper(abs(jet[4]))*24
            B3=-32*restore(r04['cells'][i]['opening_shape']['kprime'])
            lower=B3.lower()-M4*S
            print(i,sv,'M4',M4.str(10),'B3lower',B3.lower().str(10),'margin',lower.str(10),flush=True)

if __name__=='__main__':main()
