#!/usr/bin/env python3
"""R10 provenance closure. This audit does not replace the arithmetic proofs."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
from xml.etree import ElementTree

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R09 = HERE.parent / 'cusp_shape_design'
PREVIOUS = {
    'cusp_verified': '345ef0004aad060f9d7746f6a085126b4e857937384dbe29dc298be3578c7b96',
    'cusp_region': '62da00f67be0c34236b8529f2377258991c0320ee9bc7f1ab882c39e3cfafbe5',
    'cusp_connection': '45ee9d3d287fad9bbf6752d144de9bd6257c07649ba8e4c9f57a3ca2e387fdd1',
    'cusp_geometry': 'b3a1846431be58d2f3c5d45749f218aa4efebaca431e3ebd2ffe454ff7e22621',
    'cusp_width': 'eb7847154285acfa09fecb73aece53863409e29c62ed8045bde87f4974cf6dc8',
    'cusp_literature': '2d48fc9cfa5e40c376e1adf8f09b6ff62f9312dc515787d4dba37745d1bf40ab',
    'cusp_robustness': '0036bd2da3d52098743149eb645e934a088bb7a437d72cfa8e97ef7d326489c6',
    'cusp_pinned_family': 'b8119dd3f334ab697a7cf3f31ba18c515c0315bcf70a5a706b25dbb406a95aad',
    'cusp_shape_design': '6f2ae4a0518eb3ebf974d0e53ed9ea0aef07aa816336375b46befda74102d642',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(condition, message):
    if not condition:
        raise ArithmeticError(message)


def read(path):
    return json.loads((HERE / path).read_text())


def sources(data, scalar_name=None):
    values = data['source_sha256']
    if not isinstance(values, dict):
        need(scalar_name is not None, 'Missing scalar source identity')
        values = {scalar_name: values}
    for name, digest in values.items():
        need(sha(HERE / name) == digest, 'Changed source ' + name)


def inputs(data, base=None):
    base = HERE / 'results' if base is None else base
    for name, digest in data['input_sha256'].items():
        need(sha(base / name) == digest, 'Changed input ' + str(base / name))


def pair(data, key, path):
    need(data[key] == sha(path), 'Stale input ' + key)


def dyadic(value):
    mantissa, exponent = value
    need(isinstance(mantissa, int) and isinstance(exponent, int), 'Invalid dyadic')
    return Q(mantissa) * Q(2) ** exponent


def bounds(value):
    mid, radius = dyadic(value['mid_man_exp']), dyadic(value['rad_man_exp'])
    need(radius >= 0, 'Negative interval radius')
    return mid - radius, mid + radius


def point(value):
    low, high = bounds(value)
    need(low == high, 'Expected exact dyadic point')
    return low


def overlaps(a, b):
    return max(a[0], b[0]) <= min(a[1], b[1])


def inside(outer, inner):
    return outer[0] <= inner[0] <= inner[1] <= outer[1]


def own_files():
    return [p for p in sorted(HERE.rglob('*')) if p.is_file()
            and p.name != 'manifest.json' and '__pycache__' not in p.parts]


def audit():
    packages = []
    for name, digest in PREVIOUS.items():
        base = HERE.parent / name
        need(sha(base / 'manifest.json') == digest, 'Changed frozen manifest ' + name)
        manifest = json.loads((base / 'manifest.json').read_text())
        for row in manifest['files']:
            need(sha(base / row['path']) == row['sha256'], 'Changed frozen file ' + name + '/' + row['path'])
        packages.append({'package': name, 'files': len(manifest['files']), 'manifest_sha256': digest})
    originals = json.loads((HERE.parent / 'cusp_verified/manifest.json').read_text())['original_files']
    for row in originals:
        need(sha(row['path']) == row['sha256'], 'Changed original ' + row['path'])
    prior = subprocess.run([sys.executable, str(R09 / 'audit_snapshot.py')],
                           capture_output=True, text=True, check=True)
    need(json.loads(prior.stdout)['status'] == 'r09_evidence_links_and_preservation_checks_passed',
         'Previous chain audit failed')

    model = read('results/model_v2.json')
    sources(model)
    inputs(model, R09 / 'results')
    need(model['status'] == 'normalized_quartic_jet_and_three_control_majorants_recorded', 'Model status')
    need(model['frozen_R09'] == packages[-1], 'Frozen R09 input identity')
    jets = json.loads((R09 / 'results/local_jets.json').read_text())
    need(model['center'] == jets['center'] and model['Q_radius'] == jets['root_radius'], 'Exact Q identity')
    need(len(model['normalized_exact_Q_derivatives']) == 55, 'Missing exact-Q jets')
    need(all(point(v) == 0 for v in model['normalized_exact_Q_derivatives'][:4]), 'Lost exact zero identities')
    need(point(model['normalized_exact_Q_derivatives'][4]) == 24, 'Wrong normalization')
    need(bounds(model['normalizing_multiplier'])[1] < 0, 'Multiplier sign')
    need(0 < bounds(model['epsilon4'])[0] <= bounds(model['epsilon4'])[1] < Q('0.02'), 'Amplitude scope')
    for key in ('unnormalized_absolute_bounds', 'normalized_absolute_bounds'):
        need(len(model[key]) == 61 and all(bounds(v)[0] > 0 for v in model[key]), 'Missing positive majorants ' + key)
    for actual, exact in zip(model['domain'], map(Q, ('0.02', '0.001', '0.0001', '0.0001'))):
        need(inside(bounds(actual), (exact, exact)), 'Majorant domain mismatch')

    window = read('results/window_certificate.json')
    sources(window)
    pair(window, 'model_sha256', HERE / 'results/model_v2.json')
    need(window['status'] == 'finite_physical_window_complete_discriminant_and_open_0_2_4_boxes_passed', 'Window status')
    T, Pl, Pm, L = Q(2) ** -7, Q(2) ** -17, Q(2) ** -34, Q(2) ** -24
    need(point(window['global_box']['T']) == T, 'Root window identity')
    need(list(map(point, window['global_box']['parameter_radii'])) == [Pl, Pm, Pm], 'Control box identity')
    need(list(map(point, window['auxiliary_radii'])) == [4*T*T, 32*T**3, 32*T**3], 'Auxiliary box identity')
    ends = window['global_box']['endpoints']
    need(all(bounds(v[0])[0] > Q('1e-9') for v in ends), 'Root boundary signs')
    need(bounds(ends[0][1])[1] < -Q('1e-6') and bounds(ends[1][1])[0] > Q('1e-6'), 'Derivative boundary signs')
    for key in ('fold_surface', 'cusp_curve'):
        need(bounds(window[key]['q'])[1] + bounds(window[key]['eta'])[1] < 1, 'Generator contraction ' + key)
    rat = read('results/window_check.json')
    sources(rat, 'check_window.py')
    pair(rat, 'model_sha256', HERE / 'results/model_v2.json')
    pair(rat, 'certificate_sha256', HERE / 'results/window_certificate.json')
    need(rat['status'] == 'independent_rational_finite_window_surface_cusp_and_0_2_4_boxes_passed', 'Window checker status')
    need(22 < Q(rat['g4_bounds'][0]) <= Q(rat['g4_bounds'][1]) < 26, 'Rational fourth derivative')
    need(16 < Q(rat['cusp_g3_slope'][0]) <= Q(rat['cusp_g3_slope'][1]) < 32, 'Cusp monotonicity')
    need(Q('0.8') < Q(rat['cusp_lambda_quadratic_bounds'][0]) <= Q(rat['cusp_lambda_quadratic_bounds'][1]) < 4,
         'Quadratic cusp bounds')
    for kind in ('fold', 'cusp'):
        need(0 <= Q(rat[kind + '_q']) and 0 <= Q(rat[kind + '_eta'])
             and Q(rat[kind + '_q']) + Q(rat[kind + '_eta']) < 1, 'Rational uniform contraction ' + kind)
    need([(v['name'], v['count']) for v in rat['witnesses']] == [('zero', 0), ('two', 2), ('four', 4)], 'Witness identity')
    need(all(v['original_control_box_checked'] for v in rat['witnesses']), 'Witness containment')
    for v, center in zip(window['open_witnesses'], ((-L, 0, 0), (-L, -L*L, 0), (L, 0, 0))):
        need(tuple(map(point, v['center'])) == center, 'Witness center identity')
        need(list(map(point, v['radii'])) == [L/128, L*L/256, L*L/256], 'Witness radii identity')

    samples = read('results/sample_certificate.json')
    sources(samples)
    pair(samples, 'model_sha256', HERE / 'results/model_v2.json')
    pair(samples, 'window_certificate_sha256', HERE / 'results/window_certificate.json')
    need(samples['status'] == '2_cusps_double_fold_81_fold_samples_and_6_simple_roots_certified', 'Sample status')
    need(point(samples['lambda_section']) == L and point(samples['root_scale'])**2 == L, 'Sample section identity')
    need([v['branch'] for v in samples['cusps']] == [-1, 1], 'Cusp sample identity')
    need([v['index'] for v in samples['fold_samples']] == list(range(81)), 'Fold sample identity')
    need([(v['name'], v['count'], len(v['roots'])) for v in samples['simple_roots']] == [('two', 2, 2), ('four', 4, 4)], 'Simple-root sample identity')
    sc = read('results/sample_check.json')
    sources(sc, 'check_samples.py')
    pair(sc, 'model_sha256', HERE / 'results/model_v2.json')
    pair(sc, 'certificate_sha256', HERE / 'results/sample_certificate.json')
    need(sc['status'] == 'independent_rational_90_geometric_sample_contractions_passed', 'Sample checker status')
    need((sc['cusps'], sc['double_fold_intersections'], sc['fold_curve_points'], sc['simple_roots']) == (2, 1, 81, 6), 'Sample checker totals')
    labels = ['cusp_-1', 'cusp_1', 'two_double_roots'] + [f'fold_{i}' for i in range(81)]
    labels += [f'{name}_root_{i}' for name, count in [('two', 2), ('four', 4)] for i in range(count)]
    need([v['name'] for v in sc['records']] == labels, 'Missing or duplicate rational sample')
    records = {v['name']: v for v in sc['records']}
    for v in sc['records']:
        need(0 <= Q(v['q']) and 0 <= Q(v['eta']) and Q(v['q']) + Q(v['eta']) < 1, 'Sample contraction ' + v['name'])
        need(all(Q(a) <= Q(b) for a, b in v['root_enclosures']), 'Invalid sample enclosure')

    chart = read('results/chart_certificate.json')
    sources(chart)
    inputs(chart)
    need(chart['status'] == 'certified_chart_cells_with_explicit_unresolved_band', 'Chart status')
    need(point(chart['lambda_section']) == L, 'Chart section identity')
    need(chart['affine_matrix'] == window['fold_surface']['Y'], 'Affine chart identity')
    E = [list(map(point, row)) for row in chart['affine_matrix']]
    need(E[0][0]*E[1][1] - E[0][1]*E[1][0] != 0, 'Singular affine chart')
    need(all(bounds(v)[1] < Pm for v in chart['physical_control_magnitudes']), 'Chart exceeds physical box')
    need(len(chart['second_remainder_derivative_bounds']) == 15, 'Chart derivative bound scope')
    need(len(chart['stripes']) == 64 and len(chart['cells']) == 64, 'Chart stripe count')
    actual_counts = Counter()
    for i, (stripe, cells) in enumerate(zip(chart['stripes'], chart['cells'])):
        need(stripe['index'] == i and len(cells) == 56, 'Chart stripe ordering')
        need(point(stripe['alpha_left']) == -4+Q(i, 8) and point(stripe['alpha_right']) == -4+Q(i+1, 8), 'Chart alpha coverage')
        for j, cell in enumerate(cells):
            need(cell['row'] == j, 'Chart row ordering')
            need(point(cell['beta_left']) == -Q(3, 2)+Q(j, 8) and point(cell['beta_right']) == -Q(3, 2)+Q(j+1, 8), 'Chart beta coverage')
            count = cell['count']
            need(count in (None, 0, 2, 4), 'Invalid cell count')
            if count is not None:
                need(stripe['critical_graph_certified'], 'Colored cell without stationary graph')
            actual_counts['unresolved' if count is None else str(count)] += 1
    expected_counts = {'0': 430, '2': 2184, '4': 190, 'unresolved': 780}
    need(dict(actual_counts) == chart['counts'] == expected_counts, 'Chart count mismatch')
    cc = read('results/chart_check.json')
    sources(cc, 'check_chart.py')
    pair(cc, 'model_sha256', HERE / 'results/model_v2.json')
    pair(cc, 'certificate_sha256', HERE / 'results/chart_certificate.json')
    need(cc['status'] == 'independent_rational_2804_colored_cells_passed' and cc['counts'] == expected_counts, 'Chart checker status/counts')
    need(cc['stationary_graph_stripes'] == sum(v['critical_graph_certified'] for v in chart['stripes']) == 60, 'Stationary graph scope')

    cross = read('results/integral_crosscheck.json')
    sources(cross)
    inputs(cross)
    pair(cross, 'R09_kernel_source_sha256', R09 / 'shape_model.py')
    need(cross['status'] == '27_rigorous_direct_integrals_and_9_two_precision_numerical_checks_passed', 'Direct integral status')
    need([v['index'] for v in cross['rows']] == list(range(9)), 'Direct integral sample identity')
    need([v['index'] for v in cross['mpmath_checks']] == list(range(9)), 'Mpmath sample identity')
    for v in cross['rows']:
        need(len(v['direct_derivatives']) == len(v['Taylor_derivatives']) == 3, 'Direct integral order count')
        need(all(overlaps(bounds(a), bounds(b)) for a, b in zip(v['direct_derivatives'], v['Taylor_derivatives'])), 'Direct integral mismatch')
    for v in cross['mpmath_checks']:
        need(v['order'] == 0 and v['precisions'] == [90, 115] and v['inside_direct_interval'], 'Separate numerical scope')
        need(0 <= Q(v['precision_difference']) < Q('1e-68'), 'Separate numerical precision mismatch')

    summary = read('results/key_results.json')
    sources(summary, 'summarize_results.py')
    inputs(summary)
    need(summary['status'] == 'exact_integer_outward_summary' and summary['sample_contractions'] == 90, 'Summary status')
    need(summary['chart_counts'] == expected_counts, 'Summary chart counts')
    need({k: Q(v) for k, v in summary['global_domain'].items()} == {'T': T, 'lambda_radius': Pl, 'mu_and_nu_radius': Pm}, 'Summary domain')
    need(Q(summary['lambda_section']) == L and list(map(Q, summary['open_region_radii'])) == [L/128, L*L/256, L*L/256], 'Summary witness scope')
    for a, b in [('g4_interval', 'g4_bounds'), ('cusp_g3_slope_interval', 'cusp_g3_slope')]:
        need(inside(tuple(map(Q, summary[a])), tuple(map(Q, rat[b]))), 'Wrong outward decimal bound ' + a)
    proof = (HERE / 'PROOF.md').read_text().replace('\u2212', '-')
    tex = (HERE / 'THEOREM_APPENDIX.tex').read_text().replace('\u2212', '-')
    for entry in summary['special_points']:
        rows = records[entry['name']]['root_enclosures']
        fields = [('s', 1), ('mu_shift_times_1e12', 10**12), ('nu_times_1e12', 10**12)]
        if entry['name'] == 'two_double_roots':
            fields = [('s_left', 1), ('s_right', 1), ('mu_shift_times_1e15', 10**15), ('nu_times_1e15', 10**15)]
        for (field, scale), row in zip(fields, rows):
            need(inside(tuple(map(Q, entry[field])), tuple(Q(v)*scale for v in row)), 'Summary sample enclosure ' + field)
            if field.startswith('s'):
                need(all(number in proof and number in tex for number in entry[field]), 'Copied theorem number mismatch')

    failed = read('diagnostics/window_v1_failure.json')
    sources(failed)
    need(failed['status'] == 'evaluation_failed_before_certificate', 'Missing failed probe history')
    v1 = read('diagnostics/model_v1.json')
    sources(v1)
    inputs(v1, R09 / 'results')
    need(v1['frozen_R09'] == packages[-1], 'Historical model identity')
    probe = read('diagnostics/window_v2.json')
    sources(probe, 'probe_window_v2.py')
    pair(probe, 'model_sha256', HERE / 'results/model_v2.json')
    need(probe['status'] == 'feasibility_probe_only', 'Probe promoted to theorem')
    need(not (HERE / 'results/model.json').exists(), 'Ambiguous primary model file')

    plot = read('figures/metadata.json')
    sources(plot, 'plot_results.py')
    inputs(plot)
    need(plot['status'] == 'scientific_figures_from_certified_data', 'Plot source role')
    for name, digest in plot['files'].items():
        need(sha(HERE / 'figures' / name) == digest, 'Changed figure ' + name)
    visual = read('figures/visual_review.json')
    need(visual['status'] == 'visually_reviewed' and visual['external_review'] is False, 'Visual review identity')
    expected_dims = {'finite_root_regimes': [2394, 1026], 'certified_swallowtail_section': [1805, 1349]}
    need(plot['png_dimensions'] == expected_dims, 'Plot dimension metadata')
    oldplot = read('diagnostics/plot_escape_fix.json')
    need(oldplot['status'] == 'cosmetic_source_warning_corrected', 'Plot warning history')
    need(oldplot['prior_source_sha256'] == oldplot['prior_figure_metadata']['source_sha256'], 'Historical plot identity')
    for name, dims in expected_dims.items():
        png = HERE / 'figures' / (name + '.png')
        need(list(struct.unpack('>II', png.read_bytes()[16:24])) == dims, 'PNG dimensions')
        need(ElementTree.parse(HERE / 'figures' / (name + '.svg')).getroot().tag.endswith('svg'), 'Invalid SVG')
        need(visual['files'][png.name] == sha(png), 'Stale visual review')
        need(oldplot['prior_figure_metadata']['files'][png.name] == sha(png), 'Cosmetic plot edit changed PNG')

    links = 0
    for path in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^\n]+?)\)', path.read_text()):
            if target.startswith(('https://', 'http://', '#')):
                continue
            linked = path.parent / target.split('#', 1)[0]
            need(linked.exists() or linked in (HERE / 'manifest.json', HERE / 'audit_report.json'), 'Broken local link ' + str(linked))
            links += 1
    for path in HERE.glob('*.tex'):
        depth = 0
        for char in path.read_text():
            depth += (char == '{') - (char == '}')
            need(depth >= 0, 'TeX brace ordering ' + path.name)
        need(depth == 0, 'TeX braces ' + path.name)
    for path in HERE.glob('*.py'):
        compile(path.read_text(), str(path), 'exec')
    need(not list(HERE.rglob('__pycache__')), 'Unrecorded Python cache')
    runtime = read('runtime.json')
    need(runtime['assertions_enabled'] and runtime['bytecode_disabled'], 'Runtime check configuration')

    return {
        'status': 'r10_evidence_links_and_preservation_checks_passed',
        'preserved_packages': packages,
        'preserved_scientific_files': sum(v['files'] for v in packages),
        'preserved_original_files': len(originals),
        'previous_chain_audit': 'passed',
        'reused_exact_Q_F_H_jets_per_function': 55,
        'new_positive_majorants_including_nu': 61,
        'uniform_graph_contractions': 2,
        'open_control_boxes': 3,
        'certified_chart_cells': 2804,
        'unresolved_chart_cells': 780,
        'geometric_sample_contractions': 90,
        'direct_rigorous_integral_comparisons': 27,
        'separate_mpmath_values_two_precisions': 9,
        'rational_checker_reports': 3,
        'figures_visually_reviewed': 2,
        'local_links_checked': links,
        'latex_compiled': False,
        'external_mathematical_review': False,
        'literature_priority_established': False,
        'scope': 'Fixed modified R09 kernel at exact epsilon4. Original-control finite box, complete multiple-root graph, cusp curve, open 0/2/4 regions and a partially certified 2D section. Root counts only in the stated t window.',
        'trust_boundary': 'The three rational checkers take R09 integral enclosures and new unnormalized positive majorants as inputs. This provenance audit checks recorded evidence and source identities; it does not replace arithmetic reruns or expert review of the analytic proof.',
        'audit_source_sha256': sha(__file__),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    need(not (args.freeze and args.preflight), 'Choose freeze or preflight')
    manifest_path = HERE / 'manifest.json'
    if args.freeze:
        need(not manifest_path.exists(), 'R10 is already frozen')
    report = audit()
    if args.freeze:
        (HERE / 'audit_report.json').write_text(json.dumps(report, indent=2) + '\n')
        data = {
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'scope': report['scope'],
            'audit': report,
            'files': [{'path': str(p.relative_to(HERE)), 'sha256': sha(p)} for p in own_files()],
        }
        with manifest_path.open('x') as stream:
            json.dump(data, stream, indent=2)
            stream.write('\n')
    elif not args.preflight:
        data = json.loads(manifest_path.read_text())
        need(data['audit'] == report and read('audit_report.json') == report, 'Audit report changed')
        expected = {v['path']: v['sha256'] for v in data['files']}
        need(len(expected) == len(data['files']), 'Duplicate manifest path')
        need(expected == {str(p.relative_to(HERE)): sha(p) for p in own_files()}, 'Unrecorded or changed R10 files')
    print(json.dumps(report, indent=2))
