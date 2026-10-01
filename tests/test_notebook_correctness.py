import ast
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]

def cells(name):
    return json.loads((ROOT / "code" / name).read_text())["cells"]

def execute(source, namespace, functions_only=False):
    module = ast.parse(source)
    if functions_only:
        module.body = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            node.decorator_list = []
    exec(compile(ast.fix_missing_locations(module), "notebook-cell", "exec"), namespace)

def test_aperture_array_uses_its_own_cost_model():
    notebook = cells("cost_scaling.ipynb")
    namespace = {"np": np}
    for index in (2, 5):
        execute("".join(notebook[index]["source"]), namespace)
    execute("".join(notebook[6]["source"]), namespace, functions_only=True)
    execute("".join(notebook[7]["source"]), namespace)
    # A0=0.067, 100 dipoles/group and 400 MHz place the 2000-unit
    # budget between 256 and 257 groups. The dish model gives 196.
    # Allow either adjacent integer so this does not require overspending.
    assert namespace["m"][9] == 100
    assert namespace["n_array"][0, 9] in (256, 257)

@pytest.mark.parametrize("cell_index,exponent", [(3, 1.5), (5, 1.0), (7, 2.0)])
def test_errorbars_are_uncertainty_sizes(cell_index, exponent):
    source = "".join(cells("scaley_kmb_mod.ipynb")[cell_index]["source"])
    module = ast.parse(source)
    # Evaluate original numeric preparation only, stopping before plotting.
    nodes = []
    for node in module.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Tuple) for t in node.targets):
            break
        nodes.append(node)
    namespace = {"np": np}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), "survey-data", "exec"), namespace)
    low, high = namespace["yerr_low"], namespace["yerr_up"]
    # Farah: 98 (+59/-39), with the same fluence scaling for the value
    # and its uncertainty. Rane uses fluence 4.4 for both as well.
    assert low[10] == pytest.approx(39 * 8**exponent)
    assert high[10] == pytest.approx(59 * 8**exponent)
    assert low[4] == pytest.approx(3100 * 4.4**exponent)
    assert high[4] == pytest.approx(5200 * 4.4**exponent)
    assert np.all(low >= 0) and np.all(high >= 0)
    # Upper-limit arrows keep their previous lengths.
    np.testing.assert_array_equal(low[[2, 3, 12]], [8.5e4, 1.29e7, 2e4])
    np.testing.assert_array_equal(high[[2, 3, 12]], [0, 0, 0])
