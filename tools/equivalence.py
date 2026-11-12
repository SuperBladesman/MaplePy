"""Show that the package gives the notebooks' results on a folder of CIFs.

    python tools/equivalence.py my_cifs/ [--ox Ba=2,Ti=4,O=-2] [--keep DIR]

Copies the folder twice. On one copy it runs MaplePy.ipynb and then
Hopper.ipynb headless, top to bottom, with two edits only: MAPLE_CIF_DIR and
MAPLE_DIR_OVERRIDE are set to the folders, so that no dialog opens. On the
other it runs `maplepy.run_folder()` and `maplepy.additivity()`. Then it
compares the MaplePy CSVs (results, summary, failures) and Hopper's
additivity_classified.csv cell by cell. One thing is normalised: the order
of the elements listed in an oxidation-state error, which comes from a set
and so differs from one Python process to the next.

Where Tk is not installed (a headless Linux Python, for one), a stand-in
`tkinter` module is put in place before the notebooks run: with the folders
set, neither notebook calls it.

Needs nbclient, nbformat and ipykernel (pip install nbclient ipykernel).
Exits 0 when everything matches. The CIFs are only read.
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TK_STAND_IN = '''import sys, types
try:
    import tkinter
except ImportError:      # tools/equivalence.py: the folders are set, so the
    _tk = types.ModuleType("tkinter")       # dialogs are never called
    _tk.filedialog = types.ModuleType("tkinter.filedialog")
    sys.modules["tkinter"] = _tk
    sys.modules["tkinter.filedialog"] = _tk.filedialog
'''


def _set(nb, old, new):
    hits = [c for c in nb.cells if c.cell_type == 'code' and old in c.source]
    assert len(hits) == 1, f'{old!r} found in {len(hits)} cells'
    hits[0].source = hits[0].source.replace(old, new, 1)


def run_notebooks(cif_dir, work, ox):
    import nbformat
    from nbclient import NotebookClient
    shutil.copytree(ROOT / 'data', work / 'data', dirs_exist_ok=True)
    mp = nbformat.read(ROOT / 'MaplePy.ipynb', as_version=4)
    _set(mp, 'MAPLE_CIF_DIR = None ', f'MAPLE_CIF_DIR = {str(cif_dir)!r} ')
    if ox:
        _set(mp, 'OXIDATION_STATES = {}\n', f'OXIDATION_STATES = {ox!r}\n')
    mp.cells.insert(0, nbformat.v4.new_code_cell(TK_STAND_IN))
    NotebookClient(mp, timeout=None, kernel_name='python3',
                   resources={'metadata': {'path': str(work)}}).execute()
    run = sorted(cif_dir.glob('outputs_*'))[-1]
    hp = nbformat.read(ROOT / 'Hopper.ipynb', as_version=4)
    _set(hp, 'MAPLE_DIR_OVERRIDE = None ', f'MAPLE_DIR_OVERRIDE = {str(run)!r} ')
    hp.cells.insert(0, nbformat.v4.new_code_cell(TK_STAND_IN))
    NotebookClient(hp, timeout=None, kernel_name='python3',
                   resources={'metadata': {'path': str(work)}}).execute()
    return run


def run_package(cif_dir, ox):
    import maplepy
    run = maplepy.run_folder(cif_dir, oxidation_states=ox)
    maplepy.additivity(run)
    return run


def _sorted_lists(col):
    import re
    return col.astype(str).map(lambda t: re.sub(
        r"\[([^\]]*)\]",
        lambda m: '[' + ', '.join(sorted(m.group(1).split(', '))) + ']', t))


def compare(a, b):
    import pandas as pd
    bad = []
    for name in ('maple_results.csv', 'maple_summary.csv', 'maple_failed.csv',
                 'additivity_classified.csv'):
        fa, fb = a / name, b / name
        if not fa.exists() and not fb.exists():
            continue
        if fa.exists() != fb.exists():
            bad.append(f'{name}: written by only one of the two')
            continue
        da, db = pd.read_csv(fa), pd.read_csv(fb)
        if name == 'maple_failed.csv':
            # load_structure() lists the elements it could not assign from a
            # set, whose order differs from one Python process to the next
            da['error'], db['error'] = _sorted_lists(da['error']), \
                _sorted_lists(db['error'])
        if list(da.columns) != list(db.columns) or da.shape != db.shape:
            bad.append(f'{name}: columns or shape differ')
            continue
        diff = ~((da == db) | (da.isna() & db.isna()))
        n = int(diff.values.sum())
        print(f'  {name:28s} {da.shape[0]:5d} rows  '
              f'{"identical" if not n else f"{n} cells differ"}')
        if n:
            bad.append(f'{name}: {n} cells differ')
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('folder')
    ap.add_argument('--ox', help='oxidation states for every CIF, e.g. '
                                 'Ba=2,Ti=4,O=-2')
    ap.add_argument('--keep', help='keep the two runs in this folder')
    a = ap.parse_args(argv)
    from maplepy.cli import _parse_ox
    ox = _parse_ox(a.ox) if a.ox else None
    src = Path(a.folder).resolve()
    tmp = Path(a.keep) if a.keep else Path(tempfile.mkdtemp())
    nb_dir, pk_dir = tmp / 'notebook', tmp / 'package'
    for d in (nb_dir, pk_dir):
        d.mkdir(parents=True, exist_ok=True)
        for f in src.glob('*.cif'):
            shutil.copy2(f, d / f.name)
    print(f'{len(list(src.glob("*.cif")))} CIFs from {src}')
    print('running the notebooks ...')
    ra = run_notebooks(nb_dir, tmp, ox)
    print('running the package ...')
    rb = run_package(pk_dir, ox)
    bad = compare(ra, rb)
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    print('The package matches the notebooks.' if not bad
          else 'DIFFERENCES:\n  ' + '\n  '.join(bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
