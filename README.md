# Density Matrix Geometry and Sum Rules

Portable calculation and plotting code for Figure 1 of the manuscript.
Repository: https://github.com/jiguangyue-pixel/density-matrix-geometry-sum-rules

## Install

Python 3.10 or later is required. From this directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The code was tested with Python 3.12, NumPy 2.3.5 and Matplotlib 3.11.1 on
macOS. Other versions within the declared ranges have not been tested.
No GPU, external service, SciPy or manuscript workspace is required.

## Redraw the Published Curves

```sh
python reproduce.py
```

Outputs are written to `output/`: the PDF and PNG figure in `pdf/`,
`Fig1_source_data.csv`, and `verification.json`. The script checks every
displayed coordinate against the supplied source data and checks the
geometric kernel against a direct eigenvector calculation.

The figure requests Arial and STIX math fonts. Matplotlib will substitute
an available font if Arial is absent; typography may differ without changing
the numerical curves. Fonts are not redistributed.

## Recompute From the Hamiltonian

```sh
python recompute.py
python reproduce.py --data output/recomputed --output output/recomputed_figure
```

The first command recomputes every curve on the uniform 2400 x 2400 midpoint
mesh and compares the results with the archived arrays. It reads scan
coordinates from `sampling.json`; archived moment values are used only for
verification. Original data are not overwritten.

Full recalculation took approximately 67 seconds on the preparation machine;
runtime depends on hardware. The mesh contains 5.76 million points and
creates several large intermediate arrays. Allow several GB of free memory.
Redrawing stored data is substantially cheaper.

## Model and Conventions

Energies are in units of t1, t2/t1 = 1/3, chemical potential is zero, and
g = Delta/(3 sqrt(3) t2). The band energies are +/-E. The lower-band Berry
curvature convention is +2 Im<partial_kx u_-|partial_ky u_->.
All panels use the same shifted reciprocal primitive-cell mesh.

The three rescaled moments integrate E times the lower-band Berry curvature,
with the thermal weights stated in the Supplemental Material. At zero
temperature their weights are unity. For numerical stability, the M weight
is evaluated as (1 + tanh(E/(2T))^2)/2, algebraically equivalent to
tanh(E/(2T)) coth(E/T) at T > 0.

Panel (a) varies temperature at g = 0.8. Panels (b,c) use kBT/t1 = 1.
Panel (c) shows negative central derivatives with half-step delta g = 0.005,
not magnetic susceptibilities. All panels are normalized to the common
zero-temperature moment at g = 0.8.

## Files

- `haldane_model.py`: Bloch Hamiltonian, derivatives, quadrature and checks.
- `figure_style.py`, `plot_figure.py`: figure styling and drawing.
- `recompute.py`: full calculation and reference-array comparison.
- `reproduce.py`: redraw and source-data verification.
- `sampling.json`: mesh settings and all scan coordinates.
- `data/`: reference arrays and source data; see `data/README.md`.

The numerical kernel was extracted from the final figure workflow without
changing its formulas. Local paths and historical comparison dependencies
were removed from the plotting wrapper. Agreement verifies this extraction
and numerical reproduction; it is not an independent proof of the physics.

## License and Citation

Software and its documentation are licensed under the MIT License; see
`LICENSE` and the [OSI license text](https://opensource.org/license/mit).
The numerical files in `data/` are separately licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); see `data/LICENSE`.

The software and data creator is Guangyue Ji. Citation metadata are in
`CITATION.cff`. Version 1.0.0 is archived on Zenodo at
[doi:10.5281/zenodo.22696116](https://doi.org/10.5281/zenodo.22696116).
The archive preserves commit `393f423d9353bf85c42062213355add528f8ce79`.
DOI metadata were added to the main branch after archival publication; the
calculation code and numerical data are unchanged.
