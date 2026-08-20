# Optimization of Radio Array Telescopes to Search for Fast Radio Bursts

Cost-optimization analysis and manuscript source accompanying:

> **Peterson, J. B., Bandura, K., & Sanghavi, P.**<br>
> *Optimization of Radio Array Telescopes to Search for Fast Radio Bursts*<br>
> [arXiv:2001.06526](https://arxiv.org/abs/2001.06526) ·
> [doi:10.48550/arXiv.2001.06526](https://doi.org/10.48550/arXiv.2001.06526)

This repository is preserved as the read-only project archive. Its name and URL are
kept stable because the manuscript links here directly.

## Version and publication status

- Tag [`v1.0`](https://github.com/WVURAIL/Optimization-of-Radio-Array-Telescopes-to-Search-for-Fast-Radio-Bursts/releases/tag/v1.0)
  is the source snapshot corresponding to arXiv version 1, submitted on January 17,
  2020. It is retained unchanged as the historical preprint release.
- `paper/frbarray.tex` on the default branch is a later working draft from April–May
  2020, with clearly documented archival corrections made in 2026. It is not identified
  by this archive as an accepted manuscript or version of record.
- As of August 20, 2026, neither the arXiv record nor the project metadata reviewed for
  this archive lists a journal citation or publisher DOI.

For scientific citation, use the arXiv paper above. See [`CITATION.cff`](CITATION.cff)
for machine-readable metadata and [`CORRECTIONS.md`](CORRECTIONS.md) for changes made
during archival review.

## What the analysis asks

Given a fixed budget, what telescope should be built to detect the most fast radio
bursts? The analysis compares dish arrays with dipole aperture arrays across survey
frequency, element size, and assumed FRB fluence-distribution slope α.

The model finds that cost efficiency falls at least as fast as the inverse square of
survey frequency under its assumptions. Its hardware and cost inputs date from roughly
2019–2020 and should not be treated as current procurement estimates.

## Repository layout

```text
code/
  cost_scaling.ipynb      Main cost analysis; produces the three panels of Figure 1.
  scaley_kmb_mod.ipynb    Published FRB rates rescaled to a common fluence threshold;
                          produces Figure 2 for α = -3/2.
  rate_over_cost.xltx     Legacy, pre-review Excel model; it does not include N log N.
paper/
  frbarray.tex            Unpublished post-referee working draft (MNRAS format).
  papers.bib              Bibliography.
  mnras.cls, mnras.bst    Third-party MNRAS class and bibliography style.
  *.png                   Four current figures and three retained v1 alternatives.
```

## Reproducing the analysis

The archived environment was tested with Python 3.12. Direct dependencies are pinned in
`requirements.txt`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab code/cost_scaling.ipynb
```

Both notebooks use the portable inline Matplotlib backend and contain all numerical
inputs; they do not download data. Restart the kernel and run all cells to regenerate
the figures. `cost_scaling.ipynb` writes the three canonical `ratevsaeff_*.png` panels
to `paper/`; `scaley_kmb_mod.ipynb` writes `paper/frbrate_alpha15.png` and two ignored
exploratory plots in `code/`. Its first frequency-fit cell is retained as historical
scratch work; the later labelled cell produces the canonical manuscript figure.

To build the later manuscript draft:

```bash
cd paper
latexmk -pdf frbarray.tex
```

## Model summary

For `n` elements of effective area `A_el` at survey frequency `ν`, the FRB rate scales
as:

```text
R(>F_min) ∝ A_el^(-α-1) · ν^(-α/2-2) · n^(-α)
```

The modeled costs are:

| Term | Model |
|---|---|
| Dish array | `C_d = D₀ · A_el^1.25 · n` |
| Aperture array | `C_a = A₀ · m · n` |
| Signal processing | `C_s = (S₀ + r·S₀·log₂ n) · f · ν · n` |

Constants and assumptions are defined near the top of `code/cost_scaling.ipynb`.

## History and preservation

The former companion `-Draft` repository had five commits from April and May 2020. Its
final nonconfidential manuscript, bibliography, publication-support files, figures,
and notebook state were retained here during consolidation in 2026. Subsequent changes
to those materials are recorded in [`CORRECTIONS.md`](CORRECTIONS.md). Git metadata
identifies Pranav Sanghavi as the author of the five Draft commits and the original
repository's three commits.

The Draft ancestry is held in restricted preservation storage rather than attached to
the public branch because it included confidential editorial correspondence. That
correspondence is intentionally absent from this public snapshot. The public branch
retains the original repository's three 2020 commits unchanged, followed by one
archival-maintenance commit; the `v1.0` tag is also unchanged.

## Rights and reuse

This archive contains materials from multiple authors and third parties. No single
license is asserted for the repository as a whole. Files containing their own license
notices remain subject to those notices. No additional permission to reuse other
materials is granted by this archive beyond rights provided by applicable law. See
[`NOTICE`](NOTICE).
