"""The two command lines.

    maplepy FOLDER        every CIF in FOLDER through MaplePy's batch_maple()
    maplepy FILE.cif      one structure, printed
    maplepy --validate    the three known answers (Section 2 of the notebook)

    hopper RESULTS        Hopper on a MaplePy run folder (or a CIF folder
                          holding outputs_* runs: the latest is used)
"""

import argparse
import sys
from pathlib import Path


def _utf8_output():
    """The notebooks print ✓ and ✗ as they go. A Windows console
    redirected to a file or a pipe encodes as cp1252, which cannot write
    them, so the run would stop on its first progress line. Write UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):     # pragma: no cover
            pass


def _versions():
    from . import HOPPER_VERSION, MAPLEPY_VERSION, __version__
    try:
        from pymatgen.core import __version__ as pmg
    except Exception:          # pragma: no cover
        pmg = 'not found'
    return (f'maplepy {__version__} (MaplePy {MAPLEPY_VERSION}, '
            f'Hopper {HOPPER_VERSION}; pymatgen {pmg})')


def _parse_ox(text):
    """'Ba=2,Ti=4,O=-2' -> {'Ba': 2, 'Ti': 4, 'O': -2}"""
    out = {}
    for part in filter(None, (p.strip() for p in text.split(','))):
        el, _, v = part.partition('=')
        if not _ or not el.strip():
            raise argparse.ArgumentTypeError(
                f'--ox expects Element=charge pairs, e.g. Ba=2,Ti=4,O=-2; '
                f'got {part!r}')
        try:
            out[el.strip()] = float(v) if '.' in v else int(v)
        except ValueError:
            raise argparse.ArgumentTypeError(f'not a charge: {v!r} in {part!r}')
    return out


def main_maplepy(argv=None):
    _utf8_output()
    ap = argparse.ArgumentParser(
        prog='maplepy',
        description='MAPLE (Madelung Part of Lattice Energy) from CIF files. '
                    'Give a folder to run every CIF in it, or one CIF.')
    ap.add_argument('path', nargs='?', help='a folder of CIFs, or one CIF')
    ap.add_argument('--ox', type=_parse_ox, metavar='EL=Q,...',
                    help='oxidation states for every structure, e.g. '
                         'Ba=2,Ti=4,O=-2 (otherwise the CIF\'s own are used, '
                         'then the bundled tables)')
    ap.add_argument('--out', metavar='DIR',
                    help='where a folder run writes its CSVs (default: a '
                         'timestamped outputs_ folder inside FOLDER)')
    ap.add_argument('--workers', metavar='N',
                    help="worker processes: 'auto' (the default), 1 for "
                         "serial, or a number")
    ap.add_argument('--plots', action='store_true',
                    help='draw the three diagnostic plots of Section 8')
    ap.add_argument('--additivity', action='store_true',
                    help='run Hopper on the results afterwards')
    ap.add_argument('--validate', action='store_true',
                    help='run the three known-answer validations and exit')
    ap.add_argument('-v', '--verbose', action='store_true',
                    help="print the notebook's own output as well")
    ap.add_argument('--version', action='version', version=_versions())
    a = ap.parse_args(argv)

    from . import api
    if a.validate:
        import contextlib
        import io
        said = io.StringIO()
        try:
            with contextlib.redirect_stdout(said):
                flags = api.engine().run_checks()
        except Exception as e:
            print(said.getvalue())
            print(f'Validation could not run: {type(e).__name__}: {e}')
            return 1
        if a.verbose or not all(flags.values()):
            print(said.getvalue())
        names = {'pass_na': 'NaCl  PMC(Na+) = 0.8738', 'pass_cl': 'NaCl  PMC(Cl-) = 0.8738',
                 'pass_mf': 'NaCl  Madelung factor = 1.7476',
                 'pass_sym': 'NaCl  PMC(Na+) = PMC(Cl-)',
                 'pass_r': 'TiO2  rutile within 50 kcal/mol of Hoppe (1995)',
                 'pass_a': 'TiO2  anatase within 50 kcal/mol of Hoppe (1995)',
                 'pass_diff': 'TiO2  rutile and anatase within 15 kcal/mol',
                 'pass_add': 'BaTiO3  additive to within 1%'}
        for k, ok in flags.items():
            print(f"  {'pass' if ok else 'FAIL'}  {names.get(k, k)}")
        bad = [k for k, ok in flags.items() if not ok]
        print(f'\n{len(flags) - len(bad)} of {len(flags)} passed.')
        return 1 if bad else 0

    if not a.path:
        ap.print_usage()
        print('maplepy: give a folder of CIFs or one CIF, or --validate')
        return 2
    p = Path(a.path)
    if p.is_file():
        try:
            r = api.compute(p, oxidation_states=a.ox)
        except Exception as e:
            print(f'{p.name}: {e}')
            return 1
        print(r.summary())
        return 0
    if not p.is_dir():
        print(f'maplepy: no such file or folder: {p}')
        return 2
    workers = a.workers
    if workers not in (None, 'auto'):
        try:
            workers = int(workers)
        except ValueError:
            print(f"maplepy: --workers takes 'auto' or a number, not {workers!r}")
            return 2
    try:
        out = api.run_folder(p, output_dir=a.out, oxidation_states=a.ox,
                             workers=workers, plots=a.plots,
                             verbose=a.verbose)
    except FileNotFoundError as e:
        print(f'maplepy: {e}')
        return 1
    print(f'\nResults: {out}')
    if a.additivity:
        df = api.additivity(out)
        print(f"Hopper: {len(df)} structures classified; "
              f"{out / 'additivity_classified.csv'}")
    else:
        print(f'Next:    hopper "{out}"')
    return 0


def main_hopper(argv=None):
    _utf8_output()
    ap = argparse.ArgumentParser(
        prog='hopper',
        description="Hoppe's additivity theorem on a MaplePy run: "
                    'decomposition into binary oxides, the residual, the '
                    'classification, and the export.')
    ap.add_argument('results', nargs='?',
                    help='a MaplePy run folder (maple_summary.csv and '
                         'maple_results.csv), or a CIF folder holding '
                         'outputs_* runs')
    ap.add_argument('--figures', action='store_true',
                    help='draw the paper figures into the run folder as well')
    ap.add_argument('--version', action='version', version=_versions())
    a = ap.parse_args(argv)
    if not a.results:
        ap.print_usage()
        return 2
    from . import api
    try:
        df = api.additivity(a.results, figures=a.figures)
    except FileNotFoundError as e:
        print(f'hopper: {e}')
        return 1
    run = Path(df.attrs['run_folder'])
    counts = df['classification'].value_counts()
    print(f'\n{len(df)} structures from {run}')
    from . import hopper_engine
    for code in hopper_engine().CODE_ORDER:
        n = int(counts.get(code, 0))
        if n:
            print(f'  {code:9s} {n:5d}  {hopper_engine()._label_for_code(code) if code != "Additive" else "Additive (residual below 1%)"}')
    print(f"\nWritten: {run / 'additivity_classified.csv'}")
    for k, why in df.attrs.get('figures_skipped', {}).items():
        print(f'  figure {k} not drawn: {why}')
    return 0


if __name__ == '__main__':      # pragma: no cover
    sys.exit(main_maplepy())
