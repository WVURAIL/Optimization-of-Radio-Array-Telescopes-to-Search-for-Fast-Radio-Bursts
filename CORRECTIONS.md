# Archival corrections

The `v1.0` tag remains the unchanged source snapshot corresponding to arXiv v1. The
corrections below apply only to the later working draft and notebooks on the default
branch. They were made during repository maintenance in August 2026 and are not a
journal correction or a new version of the arXiv paper.

## Aperture-array cost calculation

`code/cost_scaling.ipynb` defined separate dish and aperture-array solvers, but the
aperture-array loop called the dish solver. As a result, the historical notebook used
the dish collector term `D0 * m^1.25` for aperture-array points instead of the stated
`A0 * m` model.

The loop now calls `findn_array()`. In addition, both solvers now return the largest
integer element count that remains within the fixed budget rather than the first count
over budget. Across the modeled grid, the corrected calculated costs do not exceed the
2000-unit budget.

Before correction, intended and calculated aperture element counts differed by as much
as 2.625× and individual modeled rates by as much as 6.89×. The corrected Figure 1
panels were regenerated from the notebook.

## FRB-rate error bars

`code/scaley_kmb_mod.ipynb` historically passed absolute interval endpoints to
Matplotlib as `yerr` magnitudes. Matplotlib interpreted those values as distances from
the central value, making the upper error bars too large. For example, an intended
scaled interval of 25,981–83,138 was displayed as 25,981–135,100.

The notebook now passes positive lower and upper distances, uses proportional arrow
lengths for upper-limit observations, and consistently uses the cited Parkes 2016
threshold of 4.0 Jy ms. The manuscript table uncertainties for that result were also
corrected from `+520/-310` to `+5200/-3100`. Figure 2 was regenerated.

## Reproducibility and manuscript build

- Direct Python dependencies are pinned to the versions used for regeneration under
  Python 3.12.
- Both notebooks use the inline plotting backend and have clean sequential execution
  counts.
- The redundant `amssymb` package load was removed because it conflicted with
  `newtxmath` on current TeX Live. The later manuscript now builds successfully with
  its bibliography.
- Internal author annotations and publication placeholders were removed from the
  rendered working draft, which is explicitly labelled as unpublished.

The Excel template predates the manuscript's N log N signal-processing term and is
retained as a labelled legacy artifact rather than as a reproduction of the corrected
notebook.
