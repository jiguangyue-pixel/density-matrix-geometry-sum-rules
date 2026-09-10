"""Recompute all Figure 1 curves from the Hamiltonian on the published mesh."""
import argparse
import json
import time
from pathlib import Path

import numpy as np
from haldane_model import Mesh, eigenvector_check

HERE = Path(__file__).resolve().parent


def calculate(output):
    output = Path(output).resolve()
    if output == (HERE / 'data').resolve():
        raise ValueError('Use a separate output directory; reference data must not be overwritten.')
    output.mkdir(parents=True, exist_ok=True)
    settings = json.loads((HERE / 'sampling.json').read_text())
    n = settings['mesh_size']
    temperatures = np.asarray(settings['temperatures'])
    phase_g = np.asarray(settings['phase_g'])
    slope_g = np.asarray(settings['slope_g'])
    local_g = np.asarray(settings['local_g'])
    temperature, half_step = settings['temperature_bc'], settings['half_step']
    start = time.monotonic()
    kernel_error = eigenvector_check()
    mesh = Mesh(n, settings['mesh_shift'])
    zero = mesh.moments(.8, [0])[0]
    reference = float(zero[1])
    np.testing.assert_allclose(zero[:3], reference, atol=2e-14, rtol=0)
    print(f'Computing on {n} x {n} mesh; reference={reference:.17g}', flush=True)
    thermal = mesh.moments(.8, temperatures)
    selected = mesh.moments(.8, [temperature])[0]

    def scan(grid, label):
        values = []
        for i, g in enumerate(grid):
            values.append(mesh.moments(g, [temperature])[0])
            if i % 50 == 0 or i == len(grid) - 1:
                print(f'{label}: {i+1}/{len(grid)}; {time.monotonic()-start:.1f}s', flush=True)
        return np.asarray(values)

    phase = scan(phase_g, 'Panel b')
    local = scan(local_g, 'Panel c moment pairs')
    positions = [np.searchsorted(local_g, np.round(slope_g + sign * half_step, 8))
                 for sign in (-1, 1)]
    for sign, indices in zip((-1, 1), positions):
        np.testing.assert_allclose(local_g[indices], slope_g + sign * half_step,
                                   atol=2e-12, rtol=0)
    slopes = -(local[positions[1]] - local[positions[0]]) / (2 * half_step * reference)
    np.savez_compressed(output / 'thermal_extended.npz', T=temperatures,
                        moments=thermal, reference=reference, Nk=n)
    np.savez_compressed(output / 'local_moments.npz', g=local_g, moments=local,
                        reference=reference, Nk=n)
    np.savez_compressed(output / 'plot_data.npz', g=slope_g, slopes=slopes,
                        reference=reference, T=temperature, h=half_step,
                        selected_T_values=selected, phase_g=phase_g,
                        phase_moments=phase, Nk=n)
    report = {'mesh_size': n, 'kernel_max_absolute_error': kernel_error,
              'reference': reference, 'elapsed_seconds': time.monotonic() - start,
              'all_moments_recomputed': True}
    (output / 'calculation_report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def compare(output):
    errors = {}
    for name, keys in {
        'thermal_extended.npz': ['T', 'moments', 'reference'],
        'local_moments.npz': ['g', 'moments', 'reference'],
        'plot_data.npz': ['g', 'slopes', 'reference', 'selected_T_values', 'phase_g', 'phase_moments'],
    }.items():
        with np.load(HERE / 'data' / name) as expected, np.load(Path(output) / name) as actual:
            for key in keys:
                np.testing.assert_allclose(actual[key], expected[key], atol=5e-12, rtol=5e-12)
                errors[f'{name}/{key}'] = float(np.max(abs(actual[key] - expected[key])))
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE / 'output/recomputed')
    args = parser.parse_args()
    report = calculate(args.output)
    report['comparison_max_absolute_errors'] = compare(args.output)
    (args.output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
