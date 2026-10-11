# A quartic cusp and its local real-root transition

Research note, 20 September 2026. Computational results have been generated and
checked locally. This is not a peer-reviewed paper or a proof-assistant
verification. Priority in the literature has not been established.

## 1. Objects and conventions

We use exactly the kernel and frequency convention of the supplied manuscript:

\[
\Phi(u)=\sum_{k\ge1}(2\pi^2k^4e^{9u}-3\pi k^2e^{5u})e^{-\pi k^2e^{4u}},
\quad
F(t;a)=\int_0^\infty\Phi(u)e^{\sum_j a_j u^{2j}}\cos(2tu)\,du.
\]

Every finite real polynomial is admissible. On compact complex parameter and
t sets, double exponential decay dominates the polynomial exponential and
the growth of the cosine. Uniform convergence and dominated differentiation
give a jointly analytic family. In particular,

\[
F_{a_j}=(-1)^j4^{-j}F_{t^{2j}},\qquad F_\lambda=-F_{tt}/4.
\]

Here **cusp** means a triple zero of the equilibrium equation F=0 with two
transverse controls. In catastrophe notation this is A3 for a local potential
V satisfying V_t=F. We do not call the function germ F itself an A3 germ under
the different convention that indexes x^(k+1) as Ak.

The quartic family has a1=lambda, a2=mu, all other parameters zero. The sextic
slice has a1=lambda, a3=nu, all other parameters zero.

## 2. Analytic bounds used by the computation

For u>=0 put C=4*pi^2+6*pi. The absolute value of the kth kernel summand is
at most (2*pi^2+3*pi) exp(9u) k^4 exp(-pi*k^2*exp(4u)). Successive terms of
the positive majorant have ratio at most 16 exp(-3*pi)<1/2. Therefore

\[
|\Phi(u)|\le C\exp(9u-\pi e^{4u}).                 \tag{1}
\]

Let P+(u)=sum max(0,sup a_j) u^(2j) on a real parameter box. For a cut-off U>0,
assume U >= (2j-1)/4 for each positive coefficient bound, and set

\[
c_n=4\pi e^{4U}-9-n/U-(P^+)'(U)>0.
\]

For u>=U, each u^(2j-1) exp(-4u) in the positive derivative majorant is
nonincreasing. So are exp(-4u) and exp(-4u)/u. It follows, on the ENTIRE tail,
that E_n'(u)<=-c_n, where E_n=9u+n log u+P+(u)-pi exp(4u). Consequently

\[
\int_U^\infty |\partial_t^n(\Phi(u)e^{P(u)}\cos(2tu))|du
\le {C(2U)^n\over c_n}\exp(9U+P^+(U)-\pi e^{4U}). \tag{2}
\]

This includes the 2^n factor and does not infer a global tail estimate merely
from the sign of a derivative at one point.

For the kernel series truncated after N terms, let K=N+1 and
C_U=2*pi^2 exp(9U)+3*pi exp(5U). On the real segment [0,U], its integrated
nth-derivative error is at most

\[
E_{N,n}=2UC_U K^4e^{-\pi K^2}(2U)^n e^{P^+(U)}.  \tag{3}
\]

The complex quadrature callback evaluates only the finite entire sum. Error
(3) is added after integration on the real segment. Thus no infinite complex
kernel tail is silently assigned only to the real component. The callback
returns nonfinite on unsuitable complex evaluation boxes, as permitted by
the [FLINT integration contract](https://flintlib.org/doc/acb_calc.html).
All powers in the callback are integer powers.

For uniform derivative bounds B_n, divide [0,U] into exact dyadic intervals
[l,r]. On each interval bound the logarithm in (1) by

\[
9r+\sum_j \max\{\sup(a_j l^{2j}),\sup(a_j r^{2j})\}
                 -\pi e^{4l}.
\]

Multiply its exponential by C(r-l)(2r)^n, sum, and add (2). This bounds
|F_{t^n}| for every real t and all parameters in the box. The implemented
partition has U=2 and 128 pieces. It needs neither oscillatory cancellation
nor a numerical quadrature theorem. All maxima compare exact outward upper
bounds, not overlapping Arb balls. The resulting constants are conservative
upper bounds, not asserted exact suprema.

## 3. Root certificate

Put G=(F,F_t,F_tt), x=(t,lambda,a_j) with j=2 or 3. Let x0 and the matrix Y
be the exact dyadic numbers recorded in the certificate, and let
X={x: ||x-x0||_infinity<=R}, R approximately 10^(-24) (the exact value is
recorded). The matrix Y is fixed and its determinant excludes zero.

With shifts s=(1,2,2j) and factors f=(1,-1/4,(-1)^j/4^j), the Jacobian and
Hessian entries are

\[
DG_{ip}=f_p F_{t^{i+s_p}},\qquad
D^2G_{ipq}=f_pf_q F_{t^{i+s_p+s_q}},\quad i=0,1,2.
\]

The uniform bound M2=max_i sum_(p,q) |f_p f_q| B_(i+s_p+s_q) includes BOTH
Hessian indices. Define

\[
\eta=\|YG(x_0)\|_\infty,\quad
q_0=\|I-YDG(x_0)\|_\infty,\quad
q=q_0+\|Y\|_\infty M_2 R.
\]

The map T(x)=x-YG(x) is a contraction on X if q<1. It maps X into its
interior if eta+qR<R. Banach's theorem then yields a unique zero x* of G in X.
Furthermore

\[
\|x_*-x_0\|_\infty\le\eta/(1-q).              \tag{4}
\]

Both tests pass for the two certificates. This argument uses a Hessian bound
on the ENTIRE claimed uniqueness box. No larger Kantorovich uniqueness ball
is inferred. The root derivative enclosures follow by the mean value theorem
using the same B_n bounds on the segment from x0 to x*.

**Computer-assisted result Q.** In the quartic family there is a unique zero
of G in the recorded box about

\[
(t_*,\lambda_*,\mu_*)\simeq
(41.4003413586842508894,\,-3.64569206160491909881,\,8.33512049891860723771).
\]

The exact center is the dyadic vector in `quartic_cusp_certificate.json`;
these displayed decimals are only a locator. At 110 decimal working precision
q<5.408e-13 and the distance to that exact center is <9.099e-88. At the root,

\[
3.33563055\cdot10^{-13}<F_{ttt}<3.33563057\cdot10^{-13},
\]
\[
-9.71679534\cdot10^{-13}<F_{tttt}<-9.71679532\cdot10^{-13}.
\]

The two-control rank determinant is

\[
\det D_{(\lambda,\mu)}(F,F_t)
= F_\mu F_{ttt}/4
=F_{tttt}F_{ttt}/64\in(-5.065,-5.064)\cdot10^{-27}.
\]

Thus the triple zero is nondegenerate and the controls are transverse.
Quartic deformation is SUFFICIENT. This result does not prove that quartic
degree is minimal, nor a classification of all cusps.

**Reference result S.** The supplied sextic cusp is also recovered by this
new calculation. It lies within 1.125e-70 of its recorded exact dyadic center;
q<2.769e-12 and F_ttt>0. This certificate replaces only that local reference
claim. It does not repair any old continuum continuation certificate.

## 4. Local fold geometry forced by the heat identity

**Proposition.** Let an analytic family F(t,lambda,b) satisfy
F_lambda=-F_tt/4. Suppose at c=(t*,lambda*,b*) that

\[
F=F_t=F_{tt}=0,\qquad D=F_{ttt}\ne0,\qquad B=F_b\ne0.
\]

There are unique local analytic functions lambda(s), b(s), where t=t*+s,
parameterizing F=F_t=0. Writing E=F_tttt and C1=F_tb at c,

\[
\lambda(s)=\lambda_*+2s^2+
 {4\over3}\left({C_1\over B}-{E\over D}\right)s^3+O(s^4),             \tag{5}
\]
\[
b(s)=b_*+{D\over3B}s^3+O(s^4).                                   \tag{6}
\]

**Proof.** At c the control matrix of H=(F,F_t) is

\[
M=\begin{pmatrix}0&B\\-D/4&C_1\end{pmatrix},\qquad\det M=BD/4\ne0.
\]

Apply the analytic implicit-function theorem. Differentiating H=0 gives
p'(0)=0 for p=(lambda,b). A second differentiation gives
Mp''=-(0,D), hence p''=(4,0). A third differentiation gives

\[
Mp'''=-H_{ttt}-3H_{tp}p''=2(D,E),
\]

using the heat identity. Thus b'''=2D/B and
lambda'''=8(C1/B-E/D). Taylor's theorem proves (5)--(6).
Since b''' is nonzero, det(p'',p''')=8D/B is nonzero. This is an ordinary
semicubical cusp of the discriminant curve in control space.
Also F_tt along the fold curve has derivative D at s=0, so its points for
s nonzero and sufficiently small are nondegenerate folds. QED.

For the quartic result Q, the recorded derivative enclosures give

\[
\lambda(s)=\lambda_*+2s^2+(1.908384250199\ldots)s^3+O(s^4),
\]
\[
\mu(s)=\mu_*-(1.830853594008\ldots)s^3+O(s^4),
\]

and the ratio (mu(s)-mu*)^2/(lambda(s)-lambda*)^3 tends to
0.4190031103367... as s->0. The certificate contains enclosures for the
coefficients. The coefficient 2 is exact in the stated t and lambda
normalization. We make no claim of novelty for the general proposition,
and no finite error constant is supplied for the O(s^4) terms here.

## 5. Two explicit real-root counts

Let (t0,lambda0,mu0) be the exact dyadic center of result Q, I=[t0-3/1000,
t0+3/1000], and epsilon=1/1000000. The second control here is mu0, not
silently rounded decimals or the unknown exact mu*.

**Computer-assisted result R.** The function F(t;lambda0-epsilon,mu0) has
exactly one real zero in I. The function F(t;lambda0+epsilon,mu0) has exactly
three distinct real zeros in I. All these zeros are simple.

To verify function signs on intervals without destroying oscillatory
cancellation, use a Taylor polynomial about the exact center. For the active
displacements (h,l) in t and lambda, the directional derivative is
L=h D_t-l D_t^2/4. Truncating at total degree k-1 gives

\[
F_{t^n}(x_0+(h,l,0))=
\sum_{p+q<k}{h^p(-l/4)^q\over p!q!}F_{t^{n+p+2q}}(x_0)+R_k,
\]

\[
|R_k|\le {(|h|+|l|/4)^k\over k!}
            \max_{n\le m\le n+2k} B_m.                           \tag{7}
\]

Bounds B_m cover all intervening parameters; k=8 and derivative bounds up to
order 19 are used. Everything in (7), including the remainder, is computed
with outward ball arithmetic. No floating-point safety multiplier is used.

For the minus case, F has negative/positive endpoint signs and F_t>0 on
32 closed subintervals whose exact endpoints cover I. Strict monotonicity
and the intermediate-value theorem give exactly one simple zero.

For the plus case, the signs at t offsets (-0.002,-0.0005,0.0005,0.002) are
(-,+,-,+), so three distinct zeros exist. The calculation also gives F_ttt>0
throughout I. Four distinct zeros would contradict Rolle's theorem. A
multiple zero together with the other two zeros would also force F_ttt to
vanish by Rolle's theorem with multiplicities. Thus there are exactly three
simple zeros. Neither endpoint of I can be an additional zero.

All sign intervals, the derivative cover, the exact input center, and the
certificate hash are in `local_root_counts.json`. The plot illustrates this
result; it is not its proof.

## 6. Checks, scope, and remaining research

The implementation is separate from the old engine. Ten regression tests
exercise previously identified norm and tail errors and validate nonnegligible
series truncation. Independent mpmath quadrature (115 digits, twelve terms,
sixteen real subsegments) agrees for derivatives 0 through 4 at both centers,
with absolute differences below 1e-111. This is independent numerical support,
not a second rigorous implementation. A second quartic certificate uses
130 digits, twenty terms and sixteen pieces; its root enclosure is checked
to lie in the 110-digit certificate's uniqueness box.

The results concern a polynomially deformed kernel, not the undeformed zeta
zeros. They give no statement about RH, Lambda, a physical model, a global
absence of A4 points, or membership in a named original zero pair.

The next research questions are (i) quantitative fold arcs and root-region
boundaries on an explicit control neighborhood, (ii) a certified continuation
identifying the folds that meet at Q, and (iii) a careful comparison with
primary literature. Existing long continuation logs remain unvalidated.

The closest established context located in the limited search includes
[Rodgers--Tao](https://arxiv.org/abs/1801.05914),
[Polymath](https://arxiv.org/abs/1904.12438), and
[Romik's orthogonal-polynomial expansions](https://arxiv.org/abs/1902.06330).
Their presence does not establish the novelty or significance of Q. A limited
keyword search failing to locate the same cusp is not a priority claim.
