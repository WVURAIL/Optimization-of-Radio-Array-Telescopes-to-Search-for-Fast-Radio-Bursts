# Comparison of the original and corrected results

Start with the [errata: what changed and how it affected the results](../ERRATA.md).
The [errata report](results-comparison.pdf) compares the original and corrected
results with optimum tables, frequency ratios and paired figures.

## Files

| File | Contents |
|---|---|
| `results-comparison.pdf` | Errata report. |
| `paper-before.pdf` | Original manuscript retained at `c74d910`. |
| `comparison-data.json` | Numerical results, assumptions and source hashes. |
| `optima-comparison.csv` | All 18 optimized designs before and after. |
| `grid-comparison.csv` | Matched original-grid designs at all three slopes. |
| `survey-comparison.csv` | All 13 canonical survey centers and plotted error extents. |
| `*-source.diff` | Notebook source changes without embedded output images. |
| `pdf-manifest.json` | SHA-256 hashes and page counts of the distributed PDFs. |
| `before-figures/` | Historical Figure 1 images from `95d7ed5` and Figure 2 from `c74d910`. |

See the [comparison baseline note](../ERRATA.md#comparison-baseline) for the
calculation and manuscript versions used.

## Regenerate the numerical comparison

Use Python 3.12 and a full clone containing the historical commits. From the
repository root, create an environment and install the pinned analysis dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s code -v
python code/compare_corrections.py
```

The comparison script reads the original notebooks from Git and updates the JSON,
CSVs and source diffs. Figures and PDFs are regenerated separately.

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

To rebuild the errata report, return to the repository root:

```bash
python -m pip install -r comparison/requirements.txt
python comparison/build_report.py
```

The report uses original images in `before-figures/` and corrected images in
`paper/`, and updates `pdf-manifest.json`. If model inputs change, update the
report's text and check the regenerated PDFs.
