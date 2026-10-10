#!/usr/bin/env python3
"""Independent rational Cramer check, without FLINT or generating imports."""
import argparse
import hashlib
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
GRID = 2**512


def need(value, message):
    if not value:
        raise ArithmeticError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def down(x):
    return Q((x.numerator*GRID)//x.denominator, GRID)


def up(x):
    return -down(-x)


class I:
    def __init__(self, low, high=None):
        self.lo, self.hi = down(Q(low)), up(Q(low if high is None else high))
        need(self.lo <= self.hi, 'Invalid interval')

    def __add__(self, b):
        b = b if isinstance(b, I) else I(b)
        return I(self.lo+b.lo, self.hi+b.hi)

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, b):
        return self + -(b if isinstance(b, I) else I(b))

    def __mul__(self, b):
        b = b if isinstance(b, I) else I(b)
        values = [x*y for x in (self.lo,self.hi) for y in (b.lo,b.hi)]
        return I(min(values), max(values))

    __rmul__ = __mul__

    def __truediv__(self, b):
        b = b if isinstance(b, I) else I(b)
        need(b.lo > 0 or b.hi < 0, 'Interval denominator includes zero')
        return self*I(1/b.hi,1/b.lo)

    def absolute(self):
        if self.lo >= 0:
            return self
        if self.hi <= 0:
            return -self
        return I(0,max(-self.lo,self.hi))

    def nonzero(self):
        return self.lo > 0 or self.hi < 0

    def pair(self):
        return [str(self.lo),str(self.hi)]


def restore(v):
    m,e = v['mid_man_exp']
    r,f = v['rad_man_exp']
    mid, rad = Q(m)*Q(2)**e, Q(r)*Q(2)**f
    need(rad >= 0, 'Negative serialized radius')
    return I(mid-rad,mid+rad)


def determinant(A):
    answer = I(0)
    for permutation in itertools.permutations(range(len(A))):
        inversions = sum(permutation[i] > permutation[j] for i in range(len(A)) for j in range(i+1,len(A)))
        term = I((-1)**inversions)
        for i,j in enumerate(permutation):
            term = term*A[i][j]
        answer = answer + term
    return answer


def decimal(value, places, upper=False):
    scale = 10**places
    n = -((-value.numerator*scale)//value.denominator) if upper else value.numerator*scale//value.denominator
    sign = '-' if n < 0 else ''
    n = abs(n)
    return f'{sign}{n//scale}.{n%scale:0{places}d}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), 'Refuse to overwrite recorded result')
    cp = HERE/'results/candidate_certificate.json'
    data = json.loads(cp.read_text())
    jp = HERE.parent/'cusp_shape_design/results/local_jets.json'
    jets = json.loads(jp.read_text())
    need(data['input_sha256']['R09_local_jets'] == sha(jp), 'Stale base derivatives')
    need(data['frequencies'] == [40,41,42,43], 'Different candidate identity')
    M = [[restore(row['moments'][n]) for row in data['dictionary']] for n in range(9)]
    f = list(map(restore,jets['F_at_exact_Q']))[:9]
    f[:3] = [I(0)]*3
    need(f[3].lo > 0, 'Base third derivative sign')
    A = M[:4]
    det = determinant(A)
    need(det.nonzero(), 'Design matrix singular or unresolved')
    b = [I(0),I(0),I(0),-f[3]]
    w = []
    for j in range(4):
        Aj = [[b[i] if k == j else A[i][k] for k in range(4)] for i in range(4)]
        w.append(determinant(Aj)/det)
    for own, stored in zip(w,data['weights']):
        other = restore(stored)
        need(max(own.lo,other.lo) <= min(own.hi,other.hi), 'Independent coefficient mismatch')
    g = [f[n]+sum((M[n][j]*w[j] for j in range(4)),I(0)) for n in range(9)]
    need(all(v.lo <= 0 <= v.hi for v in g[:4]), 'Exact defining equations inconsistent')
    g[:4] = [I(0)]*4
    need(g[4].nonzero(), 'Order exactly four unresolved')
    J = [[-g[n+2]/4,g[n+4]/16,-g[n+6]/64] for n in range(3)]
    rank = determinant(J)
    closed_form = g[4]*(g[4]*g[7]-g[5]*g[6])/4096
    need(rank.nonzero() and closed_form.nonzero(), 'Control rank unresolved')
    need(max(rank.lo,closed_form.lo) <= min(rank.hi,closed_form.hi), 'Control determinant formula mismatch')
    cost = sum((v.absolute() for v in w),I(0))
    need(cost.hi < 1, 'Positivity not secured')
    moment = restore(data['positive_moment_3_at_exact_Q'])
    need(moment.lo > 0, 'Positive moment unresolved')
    lower = f[3]/moment
    need(lower.lo > Q('3.96e-10') and cost.hi < Q('2.381e-7'), 'Readable universal bracket failed')
    report = {
        'status':'independent_rational_pinned_design_rank_and_norm_bracket_passed',
        'certificate_sha256':sha(cp), 'R09_jets_sha256':sha(jp), 'source_sha256':sha(__file__),
        'matrix_determinant':det.pair(), 'weights':[v.pair() for v in w],
        'modified_derivatives':[v.pair() for v in g], 'three_control_determinant':rank.pair(),
        'universal_lower_bound_interval':lower.pair(), 'feasible_l1_cost_interval':cost.pair(),
        'readable_minimum_norm_bracket':[decimal(lower.lo,20),decimal(cost.hi,20,True)],
        'fourth_derivative_times_1e13':[decimal(g[4].lo*10**13,10),decimal(g[4].hi*10**13,10,True)],
        'control_determinant_times_1e40':[decimal(rank.lo*10**40,10),decimal(rank.hi*10**40,10,True)],
        'method':'Separate permutation determinants and Cramer rule with rational endpoints rounded outwards at 512 bits. Full 3x3 control determinant and reduced formula both checked.',
        'trust_boundary':'Integral enclosures, exact-Q identification and the positive moment enclosure are trusted inputs. This does not independently repeat the analytic quadrature or the general optimality proof.',
    }
    with args.output.open('x') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps({k:report[k] for k in ['status','readable_minimum_norm_bracket','fourth_derivative_times_1e13','control_determinant_times_1e40']},indent=2))


if __name__ == '__main__':
    main()
