"""Scientific regression checks; run with python -m unittest discover -s code."""
import contextlib
import io
import json
from pathlib import Path
import unittest

import numpy as np
from scipy.optimize import brentq


def load_model():
    notebook = json.loads(Path(__file__).with_name('cost_scaling.ipynb').read_text())
    namespace = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for cell in notebook['cells']:
            if cell['cell_type'] != 'code':
                continue
            source = ''.join(cell['source'])
            if 'fig, ax = subplots()' in source:
                continue
            source = '\n'.join(line for line in source.splitlines() if not line.startswith('%'))
            exec(source, namespace)
    return namespace


class ScientificCorrections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_model()

    def test_rate_against_radiometer_equation_in_si_units(self):
        m = self.model
        for alpha in [-1., -1.5, -2.]:
            area = np.array([0.5, 10., 42.7])
            frequency = np.array([400., 800., 1600.])
            count = np.array([1000., 600., 265.])
            duration_s = 0.002
            bandwidth_hz = 0.66 * frequency * 1e6
            fluence_si = 10 * 1.380649e-23 * 50 * duration_s / (
                2 * count * area * np.sqrt(bandwidth_hz * duration_s))
            sky_fraction = (299792458 / (frequency * 1e6))**2 / (4 * np.pi * area)
            expected_per_year = 1700 * 365.25 * (fluence_si / (2e-29))**alpha * sky_fraction
            np.testing.assert_allclose(m['frbrate'](area, frequency, count, alpha),
                                       expected_per_year, rtol=2e-14)

    def test_each_grid_count_is_the_largest_affordable_integer(self):
        m = self.model
        for counts, collector in [(m['n'], 0.029 * m['Ael']**1.25),
                                  (m['n_array'], 0.067 * m['m'])]:
            def cost(count):
                return count * collector + (0.0023 + 0.00023 * np.log2(count)) * 0.66 * m['nu'][:, None] * count
            self.assertTrue(np.all(counts == np.floor(counts)))
            self.assertTrue(np.all(cost(counts) <= 2000))
            self.assertTrue(np.all(cost(counts + 1) > 2000))

    def test_dish_cutoff_corresponds_to_five_wavelengths(self):
        m = self.model
        diameter = 2 * np.sqrt(m['dish_min_area'] / (0.5 * np.pi))
        np.testing.assert_allclose(diameter / (299792458 / (m['nu'] * 1e6)), 5.)
        # Check that the plot cells actually use the tested physical thresholds.
        nb = json.loads(Path(__file__).with_name('cost_scaling.ipynb').read_text())
        for cell in nb['cells']:
            source = ''.join(cell['source'])
            if cell['cell_type'] == 'code' and 'fig, ax = subplots()' in source:
                for j in range(3):
                    self.assertIn(f'i{j} = np.where(Ael >= dish_min_area[{j}])', source)

    def test_optimum_is_not_limited_by_plot_window(self):
        m = self.model
        area, count, rate = m['optimal_dish'](2000., 1600., -2.)
        self.assertEqual(count, 265)
        self.assertAlmostEqual(area, 42.67616691555218, places=9)
        self.assertGreater(area, 30.)
        self.assertLess(area, np.max(m['Ael']))
        # Independent root inversion for every affordable count; no inverse-power formula.
        candidates = []
        for n in range(1, 439):
            def residual(a):
                return n * (0.029 * a**1.25 + (0.0023 + 0.00023 * np.log2(n)) * 0.66 * 1600) - 2000
            if residual(0.1) <= 0:
                a = brentq(residual, 0.1, 1e5)
                candidates.append((m['frbrate'](a, 1600., float(n), -2.), a, n))
        best_rate, best_area, best_n = max(candidates)
        self.assertEqual(best_n, count)
        self.assertAlmostEqual(best_area, area, places=8)
        self.assertAlmostEqual(best_rate / rate, 1., places=12)

    def test_frequency_preference_survives_the_corrections(self):
        m = self.model
        for alpha in [-1., -1.5, -2.]:
            dish = np.array([m['optimal_dish'](2000., f, alpha)[2] for f in m['nu']])
            aperture = np.array([np.max(m['frbrate'](m['Aeff'][i], f, m['n_array'][i], alpha))
                                 for i, f in enumerate(m['nu'])])
            self.assertTrue(np.all(dish[1:] / dish[:-1] < 0.25))
            self.assertTrue(np.all(aperture[1:] / aperture[:-1] < 0.25))
            if alpha < -1:
                self.assertTrue(np.all(dish > aperture))

    def test_survey_error_bars_are_distances_at_all_three_slopes(self):
        nb = json.loads(Path(__file__).with_name('scaley_kmb_mod.ipynb').read_text())
        cells = [''.join(c['source']) for c in nb['cells']
                 if c['cell_type'] == 'code' and 'yerr_up' in ''.join(c['source'])]
        self.assertEqual(len(cells), 3)
        # Canonical (index, rate, lower uncertainty, upper uncertainty, fluence).
        measurements = [(1, 10000, 5000, 6000, 3), (4, 4400, 3100, 5200, 4),
                        (5, 7000, 3000, 5000, 1.5), (6, 3300, 2200, 3700, 3.8),
                        (7, 5, 4.7, 18.7, 69), (8, 1700, 900, 1500, 2),
                        (9, 37, 8, 8, 26), (10, 98, 39, 59, 8)]
        for source, exponent in zip(cells, [1.5, 1., 2.]):
            ns = {'np': np}
            exec(source.split('fig, ax = subplots(')[0], ns)
            for i, rate, low, high, fluence in measurements:
                np.testing.assert_allclose(
                    [ns['rates'][i], ns['yerr_low'][i], ns['yerr_up'][i]],
                    np.array([rate, low, high]) * fluence**exponent, rtol=1e-14)
            # Limit arrow lengths are presentational; central upper bounds stay intact.
            for i, rate, fluence in [(2, 150, 107*.66), (3, 700, 700), (12, 3620, 3.15)]:
                self.assertTrue(ns['uplims'][i])
                self.assertAlmostEqual(ns['rates'][i] / (rate * fluence**exponent), 1.)
                self.assertEqual(ns['yerr_up'][i], 0.)
                self.assertGreater(ns['yerr_low'][i], 0.)
                self.assertLess(ns['yerr_low'][i], ns['rates'][i])


if __name__ == '__main__':
    unittest.main()
