# Optimization of Radio Array Telescopes to Search for Fast Radio Bursts

Cost-optimization analysis and manuscript source for:

> **Peterson, J. B., Bandura, K., & Sanghavi, P.** — *Optimization of Radio Array
> Telescopes to Search for Fast Radio Bursts*
> [arXiv:2001.06526](https://arxiv.org/abs/2001.06526)

<!-- TODO: if this was published, add the journal reference and DOI here. The repo
     contains referee responses, so it went through review — someone on the author
     list will know the outcome. -->

## What the paper asks

Given a fixed budget, what telescope should you build to detect the most fast radio
bursts? The analysis compares **dish arrays** against **dipole aperture arrays** across
survey frequency, element size, and assumed FRB fluence distribution slope α.

The headline result — that **cost efficiency falls at least as fast as the inverse
square of survey frequency** — is the reason to reach for this code. It gives a quick
quantitative answer when someone proposes an FRB search at high frequency.

## Layout

```
code/
  cost_scaling.ipynb      Main analysis. Produces Figures 1-3 of the paper.
  scaley_kmb_mod.ipynb    Published FRB rates rescaled to a common fluence threshold.
  rate_over_cost.xltx     Excel template for the cost model.
paper/
  frbarray.tex            Manuscript (MNRAS format)
  reviewer-comments.tex   Referee report with point-by-point responses
  papers.bib              Bibliography
  mnras.cls, mnras.bst    MNRAS LaTeX class and bibliography style
  *.png                   Figures
```

## Running the analysis

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
jupyter lab code/cost_scaling.ipynb
```

`cost_scaling.ipynb` needs **numba** — it JIT-compiles the two solvers that numerically
find how many elements fit a fixed budget. Without it the notebook fails at the first
cell with a bare `ModuleNotFoundError`, which is why the dependency is pinned here.

Both notebooks use the `%matplotlib notebook` backend, which needs `ipympl` in
JupyterLab. Swap to `%matplotlib inline` if you would rather not install it.

## The model, in brief

**FRB rate** above a fluence threshold, for `n` elements of effective area `A_el` at
survey frequency `ν`:

```
R(>F_min) ∝ A_el^(-α-1) · ν^(-α/2-2) · n^(-α)
```

**Cost**, split three ways:

| Term | Model |
|---|---|
| Dish array | `C_d = D₀ · A_el^1.25 · n` |
| Aperture array | `C_a = A₀ · m · n` |
| Signal processing | `C_s = (S₀ + r·S₀·log₂ n) · f · ν · n` |

The `log₂ n` term is the FX correlator's N log N scaling — added during review, at the
referee's insistence that "factors of 2 matter when real dollars are involved."

Constants (`D₀`, `A₀`, `S₀`, and the assumed `R₀`, `T_sys`, SNR threshold) are set at
the top of `cost_scaling.ipynb` and are the first thing to revisit if you are adapting
this to present-day hardware costs.

## History

This repository absorbed a second repo, `...-Fast-Radio-Bursts-Draft`, which held the
manuscript while the code lived here. Both histories are preserved in this repo; the
`-Draft` repo is archived.

## Licence

<!-- TODO: add a LICENSE file. MIT or BSD-3-Clause is conventional for analysis code. -->
