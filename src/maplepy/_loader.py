"""How the package runs a notebook's cells: the machinery behind _maple and
_hopper, kept here so that the two engines load in the same way.

A notebook runs its cells, top to bottom, in one namespace. Each engine is a
module whose namespace plays that part: the cells tools/build_engine.py
copied from the notebook are executed in it, in notebook order, so every
function a notebook defines is an attribute of its engine module, with the
behaviour it has in the notebook. Three things differ from a notebook
session, and only three:

* what the cells print while loading is kept in the engine's IMPORT_LOG
  rather than shown, because MaplePy's worker processes import the engine;
* the actions run when asked for rather than when the module loads, and each
  run starts from the state the module had on loading, as "Restart & Run
  All" would;
* `display`, which Jupyter provides, prints a table as text.
"""

import contextlib
import copy
import io
import os
from pathlib import Path

CELL_DIR = Path(__file__).resolve().parent / '_cells'


def data_dir():
    """The reference tables: $MAPLEPY_DATA_DIR, the installed copy, or
    data/ at the root of a source checkout (an editable install)."""
    env = os.environ.get('MAPLEPY_DATA_DIR')
    here = Path(__file__).resolve().parent
    candidates = ([Path(env)] if env else []) + [here / 'data',
                                                 here.parents[1] / 'data']
    for c in candidates:
        if (c / 'binary_oxide_maple_reference.json').exists():
            return str(c)
    raise FileNotFoundError(
        'maplepy cannot find its reference tables '
        '(binary_oxide_maple_reference.json and two others). Looked in: '
        + ', '.join(str(c) for c in candidates)
        + '. Reinstall maplepy, or set MAPLEPY_DATA_DIR to the folder '
        'holding them.')


def display(*objs, **_kw):
    """Jupyter's display(), as text."""
    for o in objs:
        print(o.to_string() if hasattr(o, 'to_string') else o)


def compile_cell(engine, name):
    path = CELL_DIR / engine / name
    return compile(path.read_text(encoding='utf-8'), str(path), 'exec',
                   dont_inherit=True)


def load(g, engine, cells):
    """Execute an engine's cells in namespace g; return what they printed."""
    g.setdefault('display', display)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        for name in cells:
            exec(compile_cell(engine, name), g)
    return log


def snapshot(g):
    """What reset() returns the namespace to: the names it holds, and a copy
    of every container kept at module level by a private name."""
    names = frozenset(g)
    state = {k: copy.deepcopy(v) for k, v in g.items()
             if k.startswith('_') and not k.startswith('__')
             and type(v) in (dict, list, set)}
    return names, state


def reset(g, names, state, keep=()):
    """Forget every name a previous run created and restore the containers.
    Names in `keep` survive."""
    for k in [k for k in g if k not in names and k not in keep]:
        del g[k]
    for k, v in state.items():
        cur = g.get(k)
        if type(cur) is not type(v):
            g[k] = copy.deepcopy(v)
        elif isinstance(cur, list):
            cur[:] = copy.deepcopy(v)
        else:
            cur.clear()
            cur.update(copy.deepcopy(v))


def run(g, engine, name):
    """Run one cell file in namespace g, printing as it goes."""
    exec(compile_cell(engine, name), g)
