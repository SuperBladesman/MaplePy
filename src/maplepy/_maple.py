"""The MaplePy engine: the code of MaplePy.ipynb, cell by cell, in this
module's namespace (see _loader). Every function the notebook defines, such
as load_structure(), compute_maple() and batch_maple(), is an attribute of
this module. Use the interface in maplepy.api; this module is its machinery.
"""

from . import _loader, _manifest

_MAPLEPY_DATA_DIR = _loader.data_dir()

IMPORT_LOG = _loader.load(globals(), 'maplepy',
                          _manifest.MAPLEPY_ENGINE_CELLS)



def reset_state():
    _loader.reset(globals(), _LOADED_NAMES, _LOADED_STATE)


def run_plots():
    """Section 8: the three diagnostic plots of the last batch_maple() run."""
    _loader.run(globals(), 'maplepy', _manifest.MAPLEPY_RUN_CELLS['plots'])


def run_checks():
    """Section 2, the three validation targets, in notebook order. Returns
    {flag: bool} for every pass flag the cells set; the namespace is reset
    afterwards."""
    flags = {}
    try:
        for name, names in _manifest.MAPLEPY_CHECK_CELLS:
            _loader.run(globals(), 'maplepy', name)
            for f in names:
                flags[f] = bool(globals()[f])
    finally:
        reset_state()
    return flags


# The state a fresh notebook session has once every definition has run,
# this module's own functions included; reset_state() returns to it.
_LOADED_NAMES, _LOADED_STATE = _loader.snapshot(globals())
_LOADED_NAMES = _LOADED_NAMES | {'_LOADED_NAMES', '_LOADED_STATE'}
