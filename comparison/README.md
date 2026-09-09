# Comparison of the original and corrected results

Start with the [errata: what changed and how it affected the results](../ERRATA.md).
The [six-page comparison report](results-comparison.pdf) contains the complete
optimum tables, frequency ratios and before/after figures. It accompanies the
[corrected paper](../paper/frbarray.pdf); it is not another paper version.

## Files

| File | Contents |
|---|---|
| `results-comparison.pdf` | The complete correction comparison. |
| `paper-before.pdf` | Rebuilt last retained pre-Dylan manuscript, `c74d910`. |
| `comparison-data.json` | Numerical results, assumptions and source hashes. |
| `optima-comparison.csv` | All 18 optimized designs before and after. |
| `grid-comparison.csv` | Matched original-grid designs at all three slopes. |
| `survey-comparison.csv` | All 13 canonical survey centers and plotted error extents. |
| `*-source.diff` | Notebook source changes without embedded output images. |
| `pdf-manifest.json` | SHA-256 hashes and page counts of the distributed PDFs. |
| `before-figures/` | Historical Figure 1 images from `95d7ed5` and Figure 2 from `c74d910`. |

The numerical baseline is `95d7ed5`, the last original-repository commit before
Dylan Gormley's archival work. All of Dylan's August work and the September extension
belong to the corrected state. Since `95d7ed5` removed the manuscript, the before PDF
uses the earlier retained source, `c74d910`. Its processing-cost approximation differs
from the May notebook. The report explains why a paper-to-paper text diff includes
draft history as well as corrections.

The before PDF retains historical scientific text and images. Rebuilding required
removing the redundant `amssymb` load, removing an unsupported table-placement option,
and adding an empty `series` field to the first bibliography entry. Its generated
preprint date is the rebuild date, not a new publication date.

## Regenerate the numerical comparison

Use Python 3.12 and a full clone containing the historical commits. From the
repository root, create an environment and install the pinned analysis dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Then run the checks and numerical comparison:

```bash
python -m unittest discover -s code -v
python code/compare_corrections.py
```

The comparison script reads the historical notebooks from Git and compares them
with the current notebooks. It rewrites the JSON, CSVs and notebook source diffs
in this directory. It does not execute the plotting cells or rebuild the PDFs.

To regenerate the corrected figures, restart and run all cells in both notebooks,
then build the paper:

```bash
cd paper
latexmk -pdf frbarray.tex
```

`cost_scaling.ipynb` produces the three Figure 1 panels in `paper/`.
`scaley_kmb_mod.ipynb` produces Figure 2 and two exploratory plots; its early
frequency-fit cell is retained scratch work, with the canonical survey data in
the later plotting cells. The Excel template is a legacy artifact predating the
N log N processing term and does not reproduce the corrected notebook.

The retained PDFs record the reviewed September 2026 correction. If model inputs
change in future, regenerate and review both the figures and comparison report
before treating those PDFs as descriptions of the changed model.

To rebuild the comparison report after regenerating the numerical data, return to
the repository root and install its additional rendering dependencies:

```bash
python -m pip install -r comparison/requirements.txt
python comparison/build_report.py
```

The report builder uses the historical images in `before-figures/` and the corrected
images in `paper/`. Its explanatory text documents this particular revision and
must be updated if the scientific conclusions change. Render and visually inspect
the regenerated PDFs before distributing them. Rebuilding the report also updates
`pdf-manifest.json` for the two papers and the report.
