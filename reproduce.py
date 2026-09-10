"""Redraw Figure 1 and verify every displayed data coordinate."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
import plot_figure
from haldane_model import eigenvector_check

HERE = Path(__file__).resolve().parent


def verify_source_data(actual_path, exact):
    with (HERE / 'data/Fig1_source_data.csv').open(newline='') as stream:
        expected = list(csv.DictReader(stream))
    with Path(actual_path).open(newline='') as stream:
        actual = list(csv.DictReader(stream))
    assert len(actual) == len(expected)
    max_error = 0.
    for wanted, found in zip(expected, actual):
        assert wanted.keys() == found.keys()
        for key in wanted:
            if key in ('panel', 'quantity', 'x_variable') or wanted[key] == '':
                assert found[key] == wanted[key], (key, found, wanted)
            else:
                a, b = float(found[key]), float(wanted[key])
                if exact:
                    assert a == b, (key, a, b)
                else:
                    np.testing.assert_allclose(a, b, atol=5e-11, rtol=5e-11)
                max_error = max(max_error, abs(a - b))
    return {'source_data_rows': len(actual), 'source_data_max_absolute_error': max_error,
            'exact_stored_data_reproduction': exact}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=HERE / 'data')
    parser.add_argument('--output', type=Path, default=HERE / 'output')
    args = parser.parse_args()
    if args.output.resolve() == args.data.resolve():
        raise ValueError('Output and input directories must differ.')
    plot_figure.DATA = args.data.resolve()
    plot_figure.OUT = args.output.resolve() / 'pdf'
    report = plot_figure.main_figure()
    report.update(verify_source_data(args.output / 'Fig1_source_data.csv',
                  exact=args.data.resolve() == (HERE / 'data').resolve()))
    report['eigenvector_kernel_max_absolute_error'] = eigenvector_check()
    (args.output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
