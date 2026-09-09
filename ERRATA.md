# Errata: what changed and how it affected the results

**The tested design preferences survive the corrections, while the absolute predicted
rates change substantially.** Lower observing frequencies remain more cost efficient
under the model's assumptions. Dish arrays remain preferred at the tested slopes
α = −1.5 and −2; at α = −1, the optimal aperture tile remains a single dipole.

This is **one combined archival revision**: Dylan Gormley's August 2026 work and its
September extension. The numerical comparison starts at the last pre-Dylan commit,
[`95d7ed5`](https://github.com/WVURAIL/Optimization-of-Radio-Array-Telescopes-to-Search-for-Fast-Radio-Bursts/commit/95d7ed56d345e4a4d7bd12fece20bbbf6e56615c).

Read the [corrected paper](paper/frbarray.pdf) or the
[detailed comparison with paired figures](comparison/results-comparison.pdf).

## Corrections and their effects

| Correction | What changed | Effect on the results |
|---|---|---|
| Daily versus annual normalization | Convert the Parkes normalization from 1700/sky/day to 620,925/sky/year. | All fixed-design model rates gain a factor of 365.25; Figure 1 now has consistent annual units. |
| Boltzmann constant | Replace 1830.64 with 1380.649 Jy m² K⁻¹. | Additional rate factors of 1.32593, 1.52679 and 1.75808 for α = −1, −1.5 and −2. |
| Aperture costs and budget counts | Replace the incorrect dish collector term `D₀ m^1.25` with the aperture term `A₀ m`; return the largest affordable integer count in both solvers. | Changes curve shapes and some optimum designs. All 1,917 corrected grid counts are within budget and maximal. |
| Dish feasibility markings | Multiply geometric area by aperture efficiency 0.5 instead of dividing by it. | Dashed-to-solid thresholds become one-quarter the previous effective areas. This affects line styles, not calculated rates. |
| Truncated dish grid | Extend the plot to 60 m² and optimize over every affordable integer count independently of the grid. | The α = −2, 1600 MHz optimum moves from the old 29.9 m² boundary to 42.676 m². |
| Survey uncertainties | Give Matplotlib positive error distances rather than absolute interval endpoints. | Figure 2's plotted intervals change. For Thornton et al., the scaled interval becomes 25,981–83,138 instead of 25,981–135,100. |
| Parkes 2016 measurement | Use 4 Jy ms consistently and correct Table 1 uncertainties to +5200/−3100. | The scaled Figure 2 center changes from 40,610 to 35,200; its corrected interval is 10,400–76,800. |
| Manuscript and figure layout | Reconcile cost prose, update yields and optima, repair the TeX build, and move Figure 2's legend above the axes. | The paper matches the corrected calculations and all upper-limit markers are visible. |

Figure 2's example survey rates above are per sky per **day**, scaled to a common
1 Jy ms threshold. They are distinct from Figure 1's annual model predictions.

## Separating rate normalization from design changes

The daily-to-annual conversion and Boltzmann correction together multiply the rate
at fixed area, frequency and element count by:

| Source-count slope α | Combined multiplier |
|---|---:|
| −1 | 484.29489 |
| −1.5 | 557.66029 |
| −2 | 642.13975 |

After dividing out those common multipliers, the changes in the optimized rates are:

| Comparison across the modeled slopes and frequencies | Change |
|---|---:|
| Dish-array optimum rate | −0.4% to +4.3% |
| Aperture-tile optimum rate | −12.0% to +14.2% |
| Largest dish optimum, at 1600 MHz and α = −2 | 29.9 → 42.676 m² |
| Dish optimum-rate ratio, 800 → 1600 MHz at α = −2 | 0.220916 → 0.231127 |

All tested optimum-rate ratios for a doubling in frequency remain below 0.25.
Fixed-tile changes can be larger than changes in the optimum: after removing the
normalization, aperture rates across the original grid change by factors of
0.84683–6.25. The largest increase is at 400 MHz, 1444 dipoles per tile and α = −2,
where the count changes from 8 to 20. That point lies outside the displayed area window.

These results preserve the sampled qualitative conclusions, but they do **not** make
the absolute-yield corrections small. They also do not establish the preferred design
for every possible slope or validate the historical population extrapolations.

## Before and after provenance

The numerical tables and before Figure 1 panels in the report use `95d7ed5`.
That commit deleted the manuscript. The [before paper](comparison/paper-before.pdf)
therefore uses the last retained pre-Dylan manuscript,
[`c74d910` / `v1.0`](https://github.com/WVURAIL/Optimization-of-Radio-Array-Telescopes-to-Search-for-Fast-Radio-Bursts/tree/v1.0).
It has an earlier processing-cost approximation, whereas the May notebook includes
an explicit N log N term. The corrected paper also contains the later working draft
restored during archiving. A paper-to-paper text comparison consequently includes
that draft history as well as the corrections. The report identifies these differences.

The tagged `v1.0` source remains unchanged. The corrected paper is an unpublished
working draft; these repository corrections are not a new arXiv submission.

## Evidence and reproduction

Six scientific regression tests pass, both notebooks execute successfully, and the
corrected manuscript builds with resolved citations and no overfull boxes. The paper
and comparison PDF pages were visually checked.

- [All 18 optimum comparisons](comparison/optima-comparison.csv)
- [Matched original-grid comparisons](comparison/grid-comparison.csv)
- [All 13 survey centers and plotted error extents](comparison/survey-comparison.csv)
- [Numerical results and source hashes](comparison/comparison-data.json)
- [Reproduction instructions](comparison/README.md)

Sources: [Bhandari et al. (2018)](https://academic.oup.com/mnras/article/475/2/1427/4668427)
for the daily normalization; [NIST constants](https://physics.nist.gov/cuu/Constants/Table/allascii.txt)
for the Boltzmann constant; [NRAO, equation 84](https://science.nrao.edu/opportunities/courses/era/lecture-summaries)
for aperture efficiency; [Rane et al.](https://academic.oup.com/mnras/article/455/2/2207/1115567)
for the Parkes measurement; and [Matplotlib's error-bar documentation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.errorbar.html)
for the uncertainty convention.
