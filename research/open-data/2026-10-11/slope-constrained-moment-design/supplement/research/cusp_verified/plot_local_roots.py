#!/usr/bin/env python3
"""Illustration from midpoint Taylor evaluations; proof lives in JSON and PROOF.md."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flint import arb,ctx
from local_roots import TaylorEnclosure,restore

HERE=Path(__file__).resolve().parent
ctx.dps=110
data=json.loads((HERE/"results/quartic_cusp_certificate.json").read_text())
x=[restore(v) for v in data["center_exact_dyadic"]]
model=TaylorEnclosure(x,"0.0031","0.00000101")
eps=arb(1)/1000000
rows=[]
fig,axes=plt.subplots(1,2,figsize=(10.5,4.2),layout="constrained")
for ax,sign,color,title in zip(axes,[-1,1],["#b45309","#1d4ed8"],
                              ["λ₀ − 10⁻⁶: bir gerçek kök","λ₀ + 10⁻⁶: üç gerçek kök"]):
    xx,yy=[],[]
    for k in range(401):
        s=(arb(k)-200)/100000
        value,remainder=model.evaluate(0,s,sign*eps)
        xx.append(float(s.mid())*1000)
        yy.append(float(value.mid())*1e22)
        rows.append([sign,float(s.mid()),float(value.mid()),float(value.rad())])
    ax.plot(xx,yy,color=color,lw=2.3)
    ax.axhline(0,color="#334155",lw=.9)
    ax.axvline(0,color="#cbd5e1",lw=.7)
    ax.set_title(title,fontsize=12,fontweight="bold",pad=12)
    ax.set_xlabel("1000 × (t − t₀)")
    ax.set_ylabel("F(t) / 10⁻²²")
    ax.grid(alpha=.15)
    ax.spines[["top","right"]].set_visible(False)
fig.suptitle("Dördüncü derece deformasyonda yerel kök geçişi",fontsize=15,fontweight="bold")
fig.supxlabel("μ = μ₀ sabit. Kesin kök sayımı |t − t₀| ≤ 0.003 için; çizimde merkezdeki ±0.002 gösteriliyor.",fontsize=9)
fig.savefig(HERE/"results/local_root_transition.png",dpi=180)
fig.savefig(HERE/"results/local_root_transition.svg")
with (HERE/"results/plot_samples.csv").open("w",newline="") as f:
    w=csv.writer(f);w.writerow(["lambda_offset_sign","t_offset","F_midpoint","F_radius"]);w.writerows(rows)
