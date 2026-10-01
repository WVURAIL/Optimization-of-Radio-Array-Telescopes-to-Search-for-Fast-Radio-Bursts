"""Compare the original notebooks with the corrected version."""
from pathlib import Path
import contextlib
import csv
import difflib
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile

import matplotlib
matplotlib.use('Agg')
import numpy as np

repo = Path(__file__).resolve().parents[1]
before_commit = '95d7ed56d345e4a4d7bd12fece20bbbf6e56615c'
paper_commit = 'c74d910faa1dffde60868d0f05260b2a8b1cf5f5'
out = repo / 'comparison'
out.mkdir(exist_ok=True)
snapshots = tempfile.TemporaryDirectory(prefix='frb-comparison-')
history = Path(snapshots.name)
for commit, folder in [(before_commit, 'before'), (paper_commit, 'before-paper-source')]:
    dest = history / folder
    dest.mkdir(exist_ok=True)
    archive = subprocess.check_output(['git', 'archive', commit], cwd=repo)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(dest, filter='data')


def model(path):
    ns = {'__name__': 'model'}
    with contextlib.redirect_stdout(io.StringIO()):
        for cell in json.loads(path.read_text())['cells']:
            s = ''.join(cell['source'])
            if cell['cell_type'] != 'code' or 'fig, ax = subplots()' in s:
                continue
            exec('\n'.join(l for l in s.splitlines() if not l.startswith('%')), ns)
    return ns


old = model(history / 'before/code/cost_scaling.ipynb')
new = model(repo / 'code/cost_scaling.ipynb')
rows, grid_rows, scale_rows = [], [], []
for a in new['alpha']:
    factor = float(365.25 * (1380.649 / 1830.64)**a)
    scale_rows.append({'alpha': float(a), 'day_to_year': 365.25,
                       'boltzmann': factor / 365.25, 'combined': factor})
    for kind in ['dish', 'aperture']:
        for j, freq in enumerate(new['nu']):
            area = old['Ael'] if kind == 'dish' else old['Aeff'][j]
            n0 = old['n'][j] if kind == 'dish' else old['n_array'][j]
            n1 = new['n'][j, :len(area)] if kind == 'dish' else new['n_array'][j]
            old_rates = old['frbrate'](area, freq, n0, a)
            new_rates = new['frbrate'](area, freq, n1, a)
            fixed_design = new['frbrate'](area, freq, n0, a)
            np.testing.assert_allclose(fixed_design / old_rates, factor, rtol=2e-14)
            i = int(np.argmax(old_rates))
            if kind == 'dish':
                best_a, best_n, best_r = new['optimal_dish'](2000., freq, a)
            else:
                k = int(np.argmax(new_rates))
                best_a, best_n, best_r = float(area[k]), int(n1[k]), float(new_rates[k])
            rows.append({'kind': kind, 'alpha': float(a), 'frequency_MHz': float(freq),
                'before_area_m2': float(area[i]), 'before_n': int(n0[i]),
                'before_rate_as_printed': float(old_rates[i]),
                'after_area_m2': best_a, 'after_n': best_n, 'after_rate_per_year': best_r,
                'normalization_factor': factor,
                'optimum_ratio_after_removing_normalization': best_r / (float(old_rates[i]) * factor)})
            for k in range(len(area)):
                grid_rows.append({'kind': kind, 'alpha': float(a), 'frequency_MHz': float(freq),
                    'area_m2': float(area[k]), 'dipoles_per_tile': int(new['m'][k]) if kind == 'aperture' else None,
                    'before_n': int(n0[k]), 'after_n': int(n1[k]),
                    'before_rate_as_printed': float(old_rates[k]), 'after_rate_per_year': float(new_rates[k]),
                    'ratio_after_removing_normalization': float(new_rates[k] / old_rates[k] / factor)})

ratios = []
for a in new['alpha']:
    for kind in ['dish', 'aperture']:
        subset = [r for r in rows if r['kind'] == kind and r['alpha'] == a]
        for lo, hi in zip(subset[:-1], subset[1:]):
            ratios.append({'kind': kind, 'alpha': float(a), 'from_MHz': lo['frequency_MHz'],
                'to_MHz': hi['frequency_MHz'],
                'before': hi['before_rate_as_printed'] / lo['before_rate_as_printed'],
                'after': hi['after_rate_per_year'] / lo['after_rate_per_year']})


def survey_data(path):
    cells = json.loads(path.read_text())['cells']
    ns = {'np': np}
    source = next(''.join(c['source']) for c in cells
                  if c['cell_type'] == 'code' and 'yerr_up' in ''.join(c['source']))
    exec(source.split('fig, ax = subplots(')[0], ns)
    return ns


s0 = survey_data(history / 'before/code/scaley_kmb_mod.ipynb')
s1 = survey_data(repo / 'code/scaley_kmb_mod.ipynb')
survey_rows = []
for i, label in enumerate(s1['surveys']):
    r = {'survey': label, 'frequency_MHz': s1['freq'][i], 'upper_limit': bool(s1['uplims'][i])}
    for prefix, s in [('before', s0), ('after', s1)]:
        r[prefix+'_central'] = float(s['rates'][i])
        r[prefix+'_lower_distance'] = float(s['yerr_low'][i])
        r[prefix+'_upper_distance'] = float(s['yerr_up'][i])
        r[prefix+'_lower_endpoint'] = float(s['rates'][i] - s['yerr_low'][i])
        r[prefix+'_upper_endpoint'] = float(s['rates'][i] + s['yerr_up'][i])
    survey_rows.append(r)

# Check error magnitudes against independently transcribed canonical survey inputs.
raw = [(1, 10000, 5000, 6000, 3), (4, 4400, 3100, 5200, 4),
       (5, 7000, 3000, 5000, 1.5), (6, 3300, 2200, 3700, 3.8),
       (7, 5, 4.7, 18.7, 69), (8, 1700, 900, 1500, 2),
       (9, 37, 8, 8, 26), (10, 98, 39, 59, 8)]
for i, rate, low, high, fluence in raw:
    np.testing.assert_allclose([s1['rates'][i], s1['yerr_low'][i], s1['yerr_up'][i]],
                              np.array([rate, low, high]) * fluence**1.5, rtol=1e-14)
np.testing.assert_allclose(np.asarray(s0['rates'])[s0['uplims']], np.asarray(s1['rates'])[s1['uplims']])

budget_rows = []
for kind in ['dish', 'aperture']:
    for j, freq in enumerate(new['nu']):
        x = old['Ael'] if kind == 'dish' else old['m']
        collector = 0.029 * x**1.25 if kind == 'dish' else 0.067 * x
        n0 = old['n'][j] if kind == 'dish' else old['n_array'][j]
        n1 = new['n'][j, :len(x)] if kind == 'dish' else new['n_array'][j]
        def cost(n):
            return n * (collector + (0.0023 + 0.00023 * np.log2(n)) * 0.66 * freq)
        c0, c1 = cost(n0), cost(n1)
        assert np.all(c1 <= 2000) and np.all(cost(n1 + 1) > 2000)
        budget_rows.append({'kind': kind, 'frequency_MHz': float(freq), 'points': len(x),
            'before_over_budget': int(np.sum(c0 > 2000)), 'after_over_budget': int(np.sum(c1 > 2000)),
            'before_cost_min': float(c0.min()), 'before_cost_max': float(c0.max()),
            'before_max_overspend_percent': float((c0.max()/2000-1)*100)})

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
data = {'comparison_definition': 'Original version (95d7ed5) versus the corrected version.',
        'original_tag': 'original',
        'baseline_commit': before_commit, 'before_paper_commit': paper_commit,
        'after_revision': 'Current corrected notebook sources, identified by source_hashes',
        'paper_provenance_note': 'Numerical comparisons use 95d7ed5. The historical paper uses c74d910 because 95d7ed5 contains no manuscript; its processing-cost approximation differs.',
        'scales': scale_rows, 'optima': rows, 'frequency_ratios': ratios,
        'grid_comparisons_file': 'grid-comparison.csv', 'budget_audit': budget_rows, 'survey_comparison': survey_rows,
        'figure_2_unchanged': False,
        'old_cutoffs_m2': (np.pi*(2.5*old['c']/(old['nu']*1e6))**2/0.5).tolist(),
        'new_cutoffs_m2': new['dish_min_area'].tolist(),
        'new_grid_points': int(new['n'].size + new['n_array'].size),
        'source_hashes': {str(p.relative_to(repo)): sha(p) for p in
                          [repo/'code/cost_scaling.ipynb', repo/'code/scaley_kmb_mod.ipynb', repo/'paper/frbarray.tex']}}
(out/'comparison-data.json').write_text(json.dumps(data, indent=2))
for name, records in [('optima-comparison', rows), ('grid-comparison', grid_rows), ('survey-comparison', survey_rows)]:
    with (out/f'{name}.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
for name in ['cost_scaling', 'scaley_kmb_mod']:
    texts = []
    for parent in [history/'before', repo]:
        nb = json.loads((parent/'code'/f'{name}.ipynb').read_text())
        texts.append('\n\n'.join(''.join(c['source']) for c in nb['cells']))
    (out/f'{name}-source.diff').write_text('\n'.join(difflib.unified_diff(
        texts[0].splitlines(), texts[1].splitlines(), fromfile=f'95d7ed5/{name}',
        tofile=f'corrected/{name}'))+'\n')

snapshots.cleanup()
print(f'Wrote {len(rows)} optimum comparisons, {len(grid_rows)} matched-grid rows, '
      f'and {len(survey_rows)} survey comparisons to {out}.')
