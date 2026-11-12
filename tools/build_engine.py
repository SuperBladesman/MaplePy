"""Build the maplepy package's engines from MaplePy.ipynb and Hopper.ipynb.

The notebooks are the source of the code. This script copies their code
cells into src/maplepy/_cells/maplepy/ and src/maplepy/_cells/hopper/, one
file per cell, so that the package runs the same code the notebooks run, in
the same order, each notebook in a namespace of its own. It changes nothing
else, and everything it does change is listed in the two plans below:

* cells that only install packages, print a version, demonstrate a call or
  carry the analysis of one study are left out, each with the reason;
* MaplePy's three validation targets (Section 2) are not run on import; they
  run when maplepy.validate() is called;
* the reference tables are read from the package's data folder rather than
  from ./data in the working directory;
* the cells that open a folder dialog are replaced by the folder passed in:
  MaplePy's GUI cell (Section 7) is left out, because maplepy.run_folder()
  calls the batch_maple() it fronts, and Hopper's loading cell takes the
  folder instead of a dialog;
* Hopper's cells that act on a MaplePy run (Section 3 onwards) are split
  into the definitions, which load with the engine, and the action, which
  runs when maplepy.additivity() is called, in notebook order.

Each edit must match the notebook exactly once, so a change to the notebook
that touches an edited line stops the build rather than going unnoticed.

    python tools/build_engine.py            # write src/maplepy/_cells/
    python tools/build_engine.py --check    # fail if they are out of date
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / 'src' / 'maplepy' / '_cells'
MANIFEST = ROOT / 'src' / 'maplepy' / '_manifest.py'

# One entry per notebook cell, in notebook order.
#   name   file stem, or None to leave the cell out (with `why`)
#   role   'engine' (loads with the package), 'run' (an action, run on a
#          folder), 'check' (run by maplepy.validate()), or 'split' (both
#          engine and run)
#   split  for 'split', the text the run part starts with
#   run    for 'run' and 'split', the key the package runs it under
#   flags  for 'check', the pass/fail names the cell sets
#   edits  (old, new) pairs, each of which must match exactly once
MAPLEPY_PLAN = [
    dict(cell=0, name=None, why='markdown: title and references'),
    dict(cell=1, name=None, why='markdown'),
    dict(cell=2, name=None, why='a commented pip install; the package '
                                'declares its dependencies'),
    dict(cell=3, name=None, why='prints the pymatgen version; '
                                'maplepy --version reports it'),
    dict(cell=4, name='c04_constants_and_version', role='engine',
         edits=[('DEFAULT_DATA_DIR = _default_data_dir()\n',
                 'DEFAULT_DATA_DIR = _MAPLEPY_DATA_DIR'
                 '   # maplepy package: the bundled tables\n')]),
    dict(cell=5, name=None, why='markdown'),
    dict(cell=6, name='c06_core_functions', role='engine'),
    dict(cell=7, name=None, why='markdown'),
    dict(cell=8, name=None, why='markdown'),
    dict(cell=9, name='c09_nacl', role='check'),
    dict(cell=10, name='c10_nacl_checks', role='check',
         flags=['pass_na', 'pass_cl', 'pass_mf', 'pass_sym']),
    dict(cell=11, name=None, why='markdown'),
    dict(cell=12, name='c12_tio2_structures', role='check'),
    dict(cell=13, name='c13_tio2', role='check'),
    dict(cell=14, name='c14_tio2_checks', role='check',
         flags=['pass_r', 'pass_a', 'pass_diff']),
    dict(cell=15, name=None, why='markdown'),
    dict(cell=16, name='c16_batio3_structures', role='check'),
    dict(cell=17, name='c17_batio3', role='check'),
    dict(cell=18, name='c18_batio3_checks', role='check',
         flags=['pass_add']),
    dict(cell=19, name=None, why='markdown'),
    dict(cell=20, name=None, why='a demonstration on the NaCl result; '
                                'the README shows the same call'),
    dict(cell=21, name=None, why='markdown'),
    dict(cell=22, name='c22_additivity_checker', role='engine'),
    dict(cell=23, name='c23_batio3_additivity_example', role='check'),
    dict(cell=24, name=None, why='markdown'),
    dict(cell=25, name='c25_batch_processing', role='engine'),
    dict(cell=26, name=None, why='markdown'),
    dict(cell=27, name=None, why='Section 6, an application to the alkaline '
                                 'earth oxides, is analysis rather than engine'),
    dict(cell=28, name=None, why='Section 6, as above'),
    dict(cell=29, name=None, why='Section 6, as above'),
    dict(cell=30, name=None, why='markdown'),
    dict(cell=31, name=None, why='the GUI: a Tk folder picker in front of '
                                 'batch_maple(), which the package calls '
                                 'directly with the folder passed in'),
    dict(cell=32, name=None, why='markdown'),
    dict(cell=33, name='c33_diagnostic_plots', role='run', run='plots'),
    dict(cell=34, name=None, why='markdown: notes and limitations'),
]

HOPPER_PLAN = [
    dict(cell=0, name=None, why='markdown: purpose'),
    dict(cell=1, name=None, why='a commented pip install'),
    dict(cell=2, name=None, why='markdown'),
    dict(cell=3, name='c03_setup_and_version', role='engine'),
    dict(cell=4, name='c04_load_maplepy_output', role='run', run='load',
         edits=[('import tkinter as tk\nfrom tkinter import filedialog\n',
                 '# maplepy package: no folder dialog; the folder is passed '
                 'in\n'),
                ('MAPLE_DIR_OVERRIDE = None ',
                 'MAPLE_DIR_OVERRIDE = _HOPPER_RUN_DIRECTORY'
                 '   # maplepy package: the folder passed in\n# ')]),
    dict(cell=5, name=None, why='markdown'),
    dict(cell=6, name='c06_binary_reference_table', role='engine',
         edits=[('BINARY_REFERENCE_PATH = None ',
                 'BINARY_REFERENCE_PATH = _HOPPER_REFERENCE_PATH'
                 '   # maplepy package: the bundled table\n# ')]),
    dict(cell=7, name=None, why='markdown'),
    dict(cell=8, name='c08_decomposition', role='engine'),
    dict(cell=9, name=None, why='markdown'),
    dict(cell=10, name='c10_batch_additivity', role='split', run='batch',
         split='# ── Run the batch'),
    dict(cell=11, name=None, why='markdown'),
    dict(cell=12, name='c12_classification', role='split', run='classify',
         split='# ── Classify ─'),
    dict(cell=13, name=None, why='markdown'),
    dict(cell=14, name='c14_residual_histogram', role='split',
         run='figure_residuals', split='# ── Plot ─'),
    dict(cell=15, name='c15_madelung_factor_clustering', role='split',
         run='figure_madelung', split='# ── Plot ─'),
    dict(cell=16, name=None, why='markdown'),
    dict(cell=17, name='c17_perovskites', role='run', run='perovskites'),
    dict(cell=18, name=None, why='markdown'),
    dict(cell=19, name='c19_pyrochlores', role='run', run='pyrochlores'),
    dict(cell=20, name=None, why='markdown'),
    dict(cell=21, name='c21_export', role='run', run='export'),
    dict(cell=22, name=None, why='markdown: notes and limitations'),
    dict(cell=23, name='c23_series_figures', role='split',
         run='figures_series', split='# ── Generate Figures ─'),
    dict(cell=24, name=None, why='empty'),
]

NOTEBOOKS = {
    'maplepy': dict(notebook='MaplePy.ipynb', plan=MAPLEPY_PLAN,
                    version='MAPLEPY_VERSION'),
    'hopper': dict(notebook='Hopper.ipynb', plan=HOPPER_PLAN,
                   version='HOPPER_VERSION'),
}

# The order the package runs each engine's actions in: the notebook's order,
# top to bottom. Hopper's figures run only when asked for.
PIPELINES = {
    'maplepy': [],
    'hopper': ['load', 'batch', 'classify', 'perovskites', 'pyrochlores',
               'export'],
}
FIGURES = {
    'maplepy': ['plots'],
    'hopper': ['figure_residuals', 'figure_madelung', 'figures_series'],
}

HEADER = ('# Generated by tools/build_engine.py from {nb}, cell {cell}.\n'
          '# Edit the notebook, not this file, then rebuild.\n'
          '{note}\n')


def _apply(src, edits, where):
    for old, new in edits or []:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f'{where}: edit expected once, found {n} times:\n'
                             f'  {old!r}')
        src = src.replace(old, new)
    return src


def _version(cells, name, nbname):
    for c in cells:
        m = re.search(rf"^{name} = '([^']+)'", ''.join(c['source']), re.M)
        if m:
            return m.group(1)
    raise SystemExit(f'{nbname}: no {name} found')


def build_one(key):
    spec = NOTEBOOKS[key]
    nbpath = ROOT / spec['notebook']
    nb = json.loads(nbpath.read_text(encoding='utf-8'))
    cells, plan = nb['cells'], spec['plan']
    if len(cells) != len(plan):
        raise SystemExit(f"{spec['notebook']} has {len(cells)} cells and the "
                         f"plan describes {len(plan)}. Update the plan.")
    version = _version(cells, spec['version'], spec['notebook'])
    files, engine, runs, checks, order = {}, [], {}, [], []
    for p, c in zip(plan, cells):
        where = f"{spec['notebook']} cell {p['cell']}"
        if p['name'] is None:
            continue
        if c['cell_type'] != 'code':
            raise SystemExit(f'{where} is {c["cell_type"]}, expected code')
        src = ''.join(c['source'])
        first = src.splitlines()[0] if src.strip() else ''
        if not first.startswith(('#', 'import', 'from', 'def', 'nacl', 'result',
                                 'maple', 'check')):
            raise SystemExit(f'{where}: unexpected first line {first!r}; '
                             f'has a cell moved?')
        src = _apply(src, p.get('edits'), where)
        role = p['role']
        hdr = dict(nb=spec['notebook'], cell=p['cell'])
        if role == 'split':
            k = src.count(p['split'])
            if k != 1:
                raise SystemExit(f'{where}: split point found {k} times')
            i = src.index(p['split'])
            head, tail = src[:i].rstrip() + '\n', src[i:]
            ename, rname = 'e' + p['name'][1:], 'r' + p['name'][1:]
            files[ename + '.py'] = HEADER.format(
                note=f'# The action at the end of this cell is in {rname}.py.',
                **hdr) + head
            files[rname + '.py'] = HEADER.format(
                note=f'# The action at the end of the cell; its definitions '
                     f'are in {ename}.py.', **hdr) + tail
            engine.append(ename + '.py')
            runs[p['run']] = rname + '.py'
            order += [ename + '.py', rname + '.py']
        else:
            prefix = {'engine': 'e', 'run': 'r', 'check': 'k'}[role]
            fname = prefix + p['name'][1:] + '.py'
            files[fname] = HEADER.format(note='', **hdr) + src
            order.append(fname)
            if role == 'engine':
                engine.append(fname)
            elif role == 'run':
                runs[p['run']] = fname
            else:
                checks.append((fname, p.get('flags', [])))
    # Line endings normalised, so a Windows checkout (CRLF) hashes the same.
    sha = hashlib.sha256(nbpath.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
    return files, dict(version=version, sha=sha, engine=engine, runs=runs,
                       checks=checks, order=order)


def build():
    files, parts = {}, {}
    for key in NOTEBOOKS:
        f, parts[key] = build_one(key)
        files.update({f'{key}/{n}': s for n, s in f.items()})
    lines = ['"""Generated by tools/build_engine.py. Do not edit."""', '']
    for key in NOTEBOOKS:
        p, K = parts[key], key.upper()
        lines += [f'# {NOTEBOOKS[key]["notebook"]}',
                  f'{K}_VERSION = {p["version"]!r}',
                  f'{K}_NOTEBOOK_SHA256 = {p["sha"]!r}',
                  '',
                  '# Loaded, in this order, into one namespace when the engine '
                  'starts.',
                  f'{K}_ENGINE_CELLS = [']
        lines += [f'    {n!r},' for n in p['engine']] + [']', '']
        lines += ['# The actions, by the name the package runs them under.',
                  f'{K}_RUN_CELLS = {{']
        lines += [f'    {k!r}: {v!r},' for k, v in p['runs'].items()] + ['}', '']
        lines += [f'{K}_PIPELINE = {PIPELINES[key]!r}',
                  f'{K}_FIGURES = {FIGURES[key]!r}', '',
                  '# Run by maplepy.validate(), with the pass flags each sets.',
                  f'{K}_CHECK_CELLS = [']
        lines += [f'    ({n!r}, {fl!r}),' for n, fl in p['checks']] + [']', '']
        lines += ['# Every packaged cell in notebook order.',
                  f'{K}_NOTEBOOK_ORDER = [']
        lines += [f'    {n!r},' for n in p['order']] + [']', '']
    return files, '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--check', action='store_true',
                    help='exit 1 if src/maplepy/_cells/ is out of date')
    a = ap.parse_args(argv)
    files, manifest = build()
    on_disk = {str(p.relative_to(CELLS)).replace('\\', '/')
               for p in CELLS.glob('*/*.py')}
    if a.check:
        stale = [n for n, s in files.items()
                 if not (CELLS / n).exists()
                 or (CELLS / n).read_text(encoding='utf-8') != s]
        extra = sorted(on_disk - set(files))
        if not MANIFEST.exists() or MANIFEST.read_text(encoding='utf-8') != manifest:
            stale.append('_manifest.py')
        if stale or extra:
            print('src/maplepy/_cells/ is out of date with the notebooks:')
            for n in stale:
                print(f'  changed  {n}')
            for n in extra:
                print(f'  extra    {n}')
            print('Run: python tools/build_engine.py')
            return 1
        print(f'src/maplepy/_cells/ matches MaplePy.ipynb and Hopper.ipynb '
              f'({len(files)} cells).')
        return 0
    for n in on_disk - set(files):
        (CELLS / n).unlink()
    for n, s in files.items():
        (CELLS / n).parent.mkdir(parents=True, exist_ok=True)
        (CELLS / n).write_text(s, encoding='utf-8', newline='\n')
    MANIFEST.write_text(manifest, encoding='utf-8', newline='\n')
    print(f'Wrote {len(files)} cells to {CELLS.relative_to(ROOT)} '
          f'and {MANIFEST.relative_to(ROOT)}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
