# Optimization of Radio Array Telescopes to Search for Fast Radio Bursts

This repository contains the **corrected version** of the analysis and working paper.
The original version is tagged [`original` (`95d7ed5`)](https://github.com/WVURAIL/Optimization-of-Radio-Array-Telescopes-to-Search-for-Fast-Radio-Bursts/tree/original).

- [Corrected paper](paper/frbarray.pdf)
- [Errata report](comparison/results-comparison.pdf) and [summary](ERRATA.md): what changed and how it affected the results
- [Analysis notebooks](code/) and [manuscript source](paper/frbarray.tex)
- [Reproduction instructions and comparison data](comparison/README.md)

See [CITATION.cff](CITATION.cff) and [NOTICE](NOTICE) for citation and rights information.

## Check the corrected analysis

With Python 3.12 in a virtual environment, run:

```sh
python -m pip install -r requirements.txt
MPLBACKEND=Agg python -m unittest discover -s code -v
```

Pushes and pull requests run the same six correction regressions against the
current notebooks. They check the radiometer-equation rate, affordable integer
counts, dish cutoff, optimum, frequency preference, and survey uncertainties.
This does not regenerate or certify every figure and PDF; follow the comparison
instructions above for a complete regeneration.

Actions receive weekly grouped minor/patch dependency updates. The tested
archival Python requirements stay pinned and are updated through deliberate
reproduction work rather than automatic version-update pull requests.
