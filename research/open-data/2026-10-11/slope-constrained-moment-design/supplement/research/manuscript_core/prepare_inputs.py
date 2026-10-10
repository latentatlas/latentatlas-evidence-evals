#!/usr/bin/env python3
"""Prepare manuscript constants and unchanged figures from frozen evidence.

Run before freezing this package. Refuses to edit a frozen manuscript package.
"""
import sys
sys.dont_write_bytecode = True
from decimal import Decimal
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(rel):
    return json.loads((RESEARCH / rel).read_text())

def main():
    if (HERE / 'manifest.json').exists():
        raise SystemExit('Frozen package: use a disposable copy without its manuscript manifest.')
    paths = [
        'cusp_verified/PROOF.md',
        'cusp_verified/results/quartic_cusp_certificate.json',
        'kernel_design_principle/PROOF.md',
        'kernel_norm_threshold/PROOF.md',
        'kernel_norm_threshold/results/threshold_certificate.json',
        'kernel_norm_threshold/results/threshold_check.json',
        'kernel_slope_budget/PROOF.md',
        'kernel_slope_asymptotics/PROOF.md',
        'kernel_slope_asymptotics/results/asymptotic_certificate.json',
        'kernel_slope_asymptotics/results/asymptotic_check.json',
        'kernel_slope_remainder/PROOF.md',
        'kernel_slope_remainder/results/remainder_certificate.json',
        'kernel_slope_remainder/results/remainder_check.json',
        'slope_chain_review/PROOF_ADDENDUM.md',
        'slope_chain_review/LITERATURE.md',
        'slope_equivalence_review/EQUIVALENCE_MAP.md',
        'slope_equivalence_review/LITERATURE.md',
        'slope_equivalence_review/sources.json',
    ]
    figures = {
        'linear_transition_loss.png': 'kernel_slope_asymptotics/figures/linear_transition_loss.png',
        'switch_contributions.png': 'kernel_slope_asymptotics/figures/switch_contributions.png',
        'remainder_envelope.png': 'kernel_slope_remainder/figures/remainder_envelope.png',
    }
    paths += list(figures.values())
    prior = {}
    entries = 0
    for p in sorted(RESEARCH.glob('*/manifest.json')):
        prior[str(p.relative_to(RESEARCH))] = sha(p)
        for row in json.loads(p.read_text())['files']:
            assert sha(p.parent / row['path']) == row['sha256'], str(p.parent / row['path'])
            entries += 1
    assert len(prior) == 19 and entries == 859, (len(prior), entries)
    (HERE / 'inputs.json').write_text(json.dumps({
        'prior_manifest_sha256': prior,
        'prior_frozen_entries': entries,
        'source_sha256': {rel: sha(RESEARCH / rel) for rel in paths},
        'figures_copied_unchanged': figures,
    }, indent=2) + '\n')
    c2 = read('kernel_norm_threshold/results/threshold_check.json')
    c3 = read('kernel_slope_asymptotics/results/asymptotic_check.json')
    c4 = read('kernel_slope_remainder/results/remainder_check.json')
    macros = {
        'DeltaLower': str(Decimal(c2['readable_minimum_norm_bracket'][0]) * Decimal('1e10')),
        'DeltaUpper': str(Decimal(c2['readable_minimum_norm_bracket'][1]) * Decimal('1e10')),
        'GammaLower': c3['gamma_readable_bracket'][0],
        'GammaUpper': c3['gamma_readable_bracket'][1],
        'CLower': str(Decimal(c3['coefficient_readable_bracket'][0]) * Decimal('1e25')),
        'CUpper': str(Decimal(c3['coefficient_readable_bracket'][1]) * Decimal('1e25')),
        'KMinus': c4['lower_remainder_constant_readable'].replace('e-33', r'\times10^{-33}'),
        'KPlus': c4['upper_remainder_constant_readable'].replace('e-32', r'\times10^{-32}'),
        'MZero': r'2\times10^{-5}',
    }
    (HERE / 'certified_constants.tex').write_text(
        '% Generated from frozen certificate checker outputs by prepare_inputs.py.\n' +
        '\n'.join('\\newcommand{\\' + k + '}{' + v + '}' for k,v in macros.items()) + '\n')
    (HERE / 'figures').mkdir(exist_ok=True)
    for name, rel in figures.items():
        shutil.copyfile(RESEARCH / rel, HERE / 'figures' / name)
    # Independent endpoint arithmetic checks the printed threshold and error percentage.
    M = Q('0.00002')
    dl,du = map(Q,c2['readable_minimum_norm_bracket'])
    cl,cu = map(Q,c3['coefficient_readable_bracket'])
    km,kp = Q(c4['lower_remainder_constant_readable']), Q(c4['upper_remainder_constant_readable'])
    lower = dl + cl/M**2 - km/M**3
    upper = du + cu/M**2 + kp/M**3
    assert lower == Q('0.00000000091787309568619750')
    assert upper == Q('0.00000000091787309964331750')
    assert kp/(cl*M) < Q('0.001178')
    (HERE / 'data_checks.json').write_text(json.dumps({
        'status': 'source_constants_and_exact_endpoint_arithmetic_passed',
        'threshold_lower_exact': str(lower), 'threshold_upper_exact': str(upper),
        'relative_excess_error_upper_exact': str(kp/(cl*M)),
        'macros': macros,
        'producer_sha256': sha(Path(__file__)),
        'scientific_results_changed': False,
    }, indent=2) + '\n')
    print('Prepared exact-source constants, three unchanged figures, and rational endpoint checks.')

if __name__ == '__main__':
    main()
