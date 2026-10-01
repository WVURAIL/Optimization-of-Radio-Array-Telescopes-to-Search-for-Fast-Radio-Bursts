"""Independent unit and budget checks for the original plotting grid."""

import ast
import json
from pathlib import Path

import numpy as np
import pytest
import scipy.constants as const

ROOT = Path(__file__).resolve().parents[1]


def load_model():
    notebook = json.loads((ROOT / "code/cost_scaling.ipynb").read_text())
    namespace = {"np": np, "const": const}
    for index in (2, 3, 5, 6, 7):
        module = ast.parse("".join(notebook["cells"][index]["source"]))
        for node in module.body:
            if isinstance(node, ast.FunctionDef):
                node.decorator_list = []
        exec(compile(module, "cost-model", "exec"), namespace)
    return namespace, notebook


@pytest.fixture(scope="module")
def model():
    return load_model()[0]


@pytest.mark.parametrize("slope", [-1, -1.5, -2])
def test_rates_match_si_fluence_and_annual_sky_rate(model, slope):
    # Derive the fluence in SI units, independently of the notebook's
    # combined MHz, millisecond, and Jy powers. 2 Jy ms = 2e-29 J/m^2/Hz.
    area = np.array([0.5, 10.0, 29.9])
    frequency_hz = np.array([400e6, 800e6, 1600e6])
    count = np.array([1000, 600, 300])
    duration_s = 0.002
    bandwidth_hz = 0.66 * frequency_hz
    fluence = 10 * 1.380649e-23 * 50 * duration_s / (
        2 * count * area * np.sqrt(bandwidth_hz * duration_s)
    )
    sky_fraction = (299792458 / frequency_hz)**2 / (4 * np.pi * area)
    expected = 1700 * 365.25 * (fluence / 2e-29)**slope * sky_fraction
    actual = model["frbrate"](area, frequency_hz / 1e6, count, slope)
    np.testing.assert_allclose(actual, expected, rtol=2e-14)


@pytest.mark.parametrize("kind", ["dish", "aperture"])
def test_every_plotted_count_is_largest_affordable_integer(model, kind):
    if kind == "dish":
        collector = 0.029 * model["Ael"]**1.25
        counts = model["n"]
    else:
        collector = 0.067 * model["m"]
        counts = model["n_array"]
    for frequency, n in zip([400, 800, 1600], counts):
        def price(number):
            return number * (
                collector + (0.0023 + 0.00023 * np.log2(number)) * 0.66 * frequency
            )
        np.testing.assert_array_equal(n, np.floor(n))
        assert np.all(price(n) <= 2000)
        assert np.all(price(n + 1) > 2000)


@pytest.mark.parametrize("name,collector,size", [
    ("findn", 0.029 * 10**1.25, 10),
    ("findn_array", 0.067 * 100, 100),
])
def test_budget_boundaries_include_zero_and_exact_cost(model, name, collector, size):
    def price(n):
        return n * (collector + (0.0023 + 0.00023 * np.log2(n)) * 0.66 * 400)
    find_count = model[name]
    assert find_count(0, 400, size) == 0
    assert find_count(price(1) * 0.999, 400, size) == 0
    assert find_count(price(10), 400, size) == 10
    # The previous tolerance returned an over-budget design at this boundary.
    assert find_count(price(10) * (1 - 1e-5), 400, size) == 9
    assert find_count(price(10) * (1 + 1e-5), 400, size) == 10


def test_physical_cutoff_uses_effective_area_in_all_three_plots(model):
    wavelength = 299792458 / np.array([400e6, 800e6, 1600e6])
    diameter = 2 * np.sqrt(model["dish_min_area"] / (0.5 * np.pi))
    np.testing.assert_allclose(diameter / wavelength, 5, rtol=1e-14)
    _, notebook = load_model()
    # Execute the actual plot-index assignments, including exact thresholds.
    areas = np.sort(np.concatenate([
        model["dish_min_area"] * (1 - 1e-6),
        model["dish_min_area"],
        model["dish_min_area"] * (1 + 1e-6),
    ]))
    for index in (9, 10, 11):
        module = ast.parse("".join(notebook["cells"][index]["source"]))
        module.body = [node for node in module.body if isinstance(node, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id in ("i0", "i1", "i2")
                               for t in node.targets)]
        namespace = dict(model, Ael=areas)
        exec(compile(module, "plot-cutoffs", "exec"), namespace)
        assert len(module.body) == 3
        for frequency_index in range(3):
            expected = np.flatnonzero(2 * np.sqrt(areas / (0.5 * np.pi))
                                     >= 5 * wavelength[frequency_index])
            np.testing.assert_array_equal(namespace[f"i{frequency_index}"][0], expected)
