#!/usr/bin/env python3
"""Reproduce the R20 exposition revision from frozen R19, without changing R19."""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'manuscript_core'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    out = args.output_dir.absolute()
    if out.exists():
        raise SystemExit('Use a new output directory; frozen files must not be overwritten.')
    assert sha(SOURCE/'manuscript.tex') == '9a9b2a79e743968b1fb557cf8f6d1addab5a37a768f9acb40ec46144d3ac56ab'
    tex = (SOURCE/'manuscript.tex').read_text()
    changes = []
    def replace(key, before, after):
        nonlocal tex
        assert tex.count(before) == 1, key
        tex = tex.replace(before, after)
        changes.append(key)

    replace('revision_identifier', 'Manuscript core for mathematical review',
            'Revised manuscript for mathematical review (R20)')
    replace('early_geometric_motivation',
        'increase its multiplicity while the kernel remains positive.',
        r'''increase its multiplicity while the kernel remains positive.
In the example below, an exact triple zero $Q$ of a theta transform is
held fixed. Three homogeneous moments preserve its first three vanishing
derivatives, and a fourth moment cancels its nonzero third derivative.
The optimization quantifies the smallest relative kernel change needed
for this operation under a prescribed slope bound.''')
    replace('fortet_mourier_comparison',
        'Its flat-metric and Wasserstein-type context is developed in\n\\cite{piccoli,schmitzer}.',
        r'''Its flat-metric and Wasserstein-type context is developed in
\cite{piccoli,schmitzer}. With the corresponding metric scaling it is also
the Fortet--Mourier dual norm: the test-function norm uses a maximum of
the amplitude and Lipschitz bounds, not their sum. Hille and Theewis
give finite-dimensional reductions when one measure is atomic
\cite[Theorem 2.1]{hille2023} and norming sets of extreme test functions
\cite[Theorem 5.1 and Corollary 5.1]{hille2024}. These results describe
the support functional; the exact-moment large-$M$ coefficient below
requires an additional argument.''')
    replace('anchor_preserves_amplitude',
        'Since $\\ds<1$ (Table~\\ref{tab:cert}), approximate $h_*$ by bounded smooth\ncompactly supported functions in the weighted moments through order seven.',
        r'''Since $\ds<1$ (Table~\ref{tab:cert}), first cut off $h_*$ and then
mollify its even extension using nonnegative kernels. The resulting
smooth compactly supported functions have amplitude at most $\ds$ and
converge in the weighted moments through order seven. The strict gap
between $\ds$ and one leaves room for the following corrections.''')
    replace('fixed_local_convex_part',
        'roots in $[0,1]$ and excludes other roots there by a sign cover. Integrate\nthe first positive theta summand only over fixed neighborhoods containing\nthose roots. The Hessian of that part of $D$ is',
        r'''roots in $[0,1]$ and excludes other roots there by a sign cover.
Let $I_k$ be fixed disjoint neighborhoods containing these root boxes,
with no other zero of any residual in the coefficient cube. If $w_1$ is
the first positive theta summand times the deformation factor, define
\begin{equation}
 D_{\rm loc}(a)=\int_{\bigcup_{k=1}^{28}I_k}w_1(u)|r_a(u)|\dd.
 \label{eq:localD}
\end{equation}
Its Hessian is''')
    replace('local_convex_complement',
        'where $w_1$ is that summand times the deformation factor. Positive leading\nprincipal minors certify $H-(1/200)I\\succ0$ uniformly. The rest of $D$ is\nconvex, so $D$ is strongly convex on the cube.',
        r'''Positive leading principal minors certify $H-(1/200)I\succ0$
uniformly. The difference $D-D_{\rm loc}$ is an integral of $|r_a|$
against a nonnegative density on a fixed set, hence is convex. Therefore
$D$ is strongly convex on the cube.''')
    replace('gamma_tail_global_monotonicity',
        'The logarithmic decay rate times $3/85$ exceeds 16 and $e^4>50$;\nhence the geometric denominator covers the entire infinite tail.',
        r'''For this envelope the logarithmic derivative is
$3/u+9+4\mu_+u^3-4\pi e^{4u}$. After division by $e^{4u}$,
each positive term is decreasing for $u\ge1$. Thus its value at one
bounds the decay rate throughout the tail. That rate times $3/85$
exceeds 16 and $e^4>50$, giving the displayed geometric denominator.''')
    replace('finite_center_cost_derivation',
        r'''$L\ge0$. Equations \eqref{eq:bounds}--\eqref{eq:stepremainder}, including
the finite center shifts, give''',
        r'''$L\ge0$. Put $\Delta_k=c_k-z_k$. Since $q_r(z_k)=0$, the
unsmoothed center displacement satisfies
\begin{equation}
 \left|\int q_r(s_c-s_z)\dd\right|
 \le\sum_{k=1}^3 R_{1k}|\Delta_k|^2.
 \label{eq:shiftloss}
\end{equation}
Indeed the jump has magnitude two and
$|q_r(z_k+x)|\le R_{1k}|x|$. Differentiating \eqref{eq:step} in $c$
also gives $|\partial_c I_{q_r}|\le a^2R_{2k}/6$, and hence
\begin{equation}
 |d_k[I_{q_r}(c_k,a)-I_{q_r}(z_k,a)]|
 \le a^2R_{2k}|\Delta_k|/3.
 \label{eq:smoothshift}
\end{equation}
Using $|\Delta_k|\le a^2V_k$ produces exactly the finite sum $A_4$.
At the original centers, summing \eqref{eq:stepremainder} produces
$A_3$. Therefore''')
    replace('named_upper_constants',
        r'''Let $f_-$ be the certified lower bound for $f_3$, and $U_\delta$ the upper
bound for $\ds$. Define''',
        r'''Let $f_-$ be the certified lower bound for $f_3$, and let
$U_\delta$, $\Gamma_+$ and $C_+$ denote certified upper bounds for
$\ds$, $\Gamma$ and $\Cs$, respectively. Define''')
    replace('budget_scale_interpretation',
        r'''The theorem applies to the
smooth nondegenerate class as an infimum by Proposition~\ref{prop:smooth}.''',
        r'''The theorem applies to the
smooth nondegenerate class as an infimum by Proposition~\ref{prop:smooth}.
Here ``large slope'' is relative to the amplitude: at $M_0$ the leading
transition half-width $\ds/M_0$ is approximately $4.5894\times10^{-5}$
in the original $u$ coordinate, well below the switch separation.''')
    replace('derivative_tail_global_monotonicity',
        r'''least $c=4\pi e^{4u_0}-4\mu_+u_0^3-17-9/(1+u_0)$ throughout $u\ge u_0$.
Since $c(3/85)>16$,''',
        r'''least $c=4\pi e^{4u_0}-4\mu_+u_0^3-17-9/(1+u_0)$ throughout $u\ge u_0$.
To see why a bound at $u_0$ suffices, divide the logarithmic derivative
$9/(1+u)+17+4\mu_+u^3-4\pi e^{4u}$ by $e^{4u}$.
All three positive terms are decreasing for $u\ge u_0>3/4$.
The logarithmic derivative is consequently at most
$-c e^{4(u-u_0)}\le-c$. Since $c(3/85)>16$,''')
    replace('new_review_provenance',
        r'''Reproduction commands and the complete source map are in the companion
\texttt{manuscript\_core/README.md} and \texttt{CLAIM\_SOURCE\_MAP.md}.''',
        r'''The original claim-to-source map remains in
\texttt{manuscript\_core/CLAIM\_SOURCE\_MAP.md}. Fresh producer replays,
the equation review and reproduction commands for this revision are in
\texttt{manuscript\_review/README.md}. The recorded replay reproduces
the mathematical endpoints of 7,010 stored balls; repeated occurrences
are counted separately. It does not constitute an independent
implementation of every enclosure.''')
    replace('additional_primary_bibliography',
        r'''\bibitem{sion} M. Sion, On general minimax theorems,''',
        r'''\bibitem{hille2023} S. C. Hille and E. S. Theewis, Explicit expressions
and computational methods for the Fortet--Mourier distance of positive
measures to finite weighted sums of Dirac measures,
\emph{J. Approx. Theory} 294 (2023), 105947.
\href{https://doi.org/10.1016/j.jat.2023.105947}{doi:10.1016/j.jat.2023.105947}.
\bibitem{hille2024} S. C. Hille and E. S. Theewis, Norming and dense sets
of extreme points of the unit ball in spaces of bounded Lipschitz functions,
\emph{J. Math. Anal. Appl.} 536 (2024), 128200.
\href{https://doi.org/10.1016/j.jmaa.2024.128200}{doi:10.1016/j.jmaa.2024.128200}.
\bibitem{sion} M. Sion, On general minimax theorems,''')
    out.mkdir(parents=True)
    (out/'manuscript.tex').write_text(tex)
    for name in ['certified_constants.tex','build_pdf.py']:
        shutil.copyfile(SOURCE/name,out/name)
    shutil.copytree(SOURCE/'figures',out/'figures')
    (out/'revision.json').write_text(json.dumps({
        'source_tex_sha256':sha(SOURCE/'manuscript.tex'),
        'revised_tex_sha256':sha(out/'manuscript.tex'),
        'source_constants_sha256':sha(SOURCE/'certified_constants.tex'),
        'script_sha256':sha(Path(__file__)),
        'changes':changes,
        'numerical_constants_changed':False,
        'main_theorem_statements_changed':False,
    },indent=2)+'\n')
    print(json.dumps({'output_dir':str(out),'changes':changes}))

if __name__ == '__main__':
    main()
