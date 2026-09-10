# Figure 1 Data

`Fig1_source_data.csv` contains the exact displayed coordinates of nine
curves (1,884 rows): three observables M, I and U in each panel.
These are deterministic numerical calculations, not experimental replicates.

Columns:

- `panel`: a, b or c.
- `quantity`: rescaled observable M, I or U.
- `x`, `normalized_y`: displayed coordinates.
- `x_variable`: horizontal-axis variable.
- `kBT_over_t1`: dimensionless temperature.
- `g_fixed`: fixed g in panel (a); blank otherwise.
- `central_difference_half_step`: delta g in panel (c); blank otherwise.
- `M_reference`: common zero-temperature normalization at g = 0.8.

Multiply normalized_y by M_reference to recover the rescaled moment in
panels (a,b), or the negative central derivative estimate in panel (c).
The stored reference is 0.16258811206509494.

Load the NPZ archives with NumPy (`numpy.load`). Moment columns are ordered
I, M, U, M-minus-I, which differs from the figure legend order.

- `thermal_extended.npz`: temperature grid, unnormalized moments and reference.
- `plot_data.npz`: phase scan, central slopes, reference and plotting settings.
- `local_moments.npz`: unnormalized moment pairs used for central differences.

Some additional arrays in the original archives are convergence diagnostics,
not displayed curves. The scripts use the final uniform 2400 x 2400 data.

The source data match the displayed arrays exactly. Full recalculation also
agrees to floating-point precision; central-difference slopes show the largest
absolute difference, approximately 2e-13 in the tested environment.

Creator: Guangyue Ji. Data reuse license: CC BY 4.0; see `LICENSE`.
These numerical files are not covered by the software MIT license.
