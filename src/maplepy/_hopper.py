"""The Hopper engine: the code of Hopper.ipynb, cell by cell, in this
module's namespace (see _loader). Imported on first use, because the
notebook's set-up cell changes matplotlib's rcParams, as it does in Jupyter.
Use maplepy.additivity(); this module is its machinery.
"""

from pathlib import Path as _P

from . import _loader, _manifest

_HOPPER_REFERENCE_PATH = str(_P(_loader.data_dir())
                             / 'binary_oxide_maple_reference.json')

IMPORT_LOG = _loader.load(globals(), 'hopper', _manifest.HOPPER_ENGINE_CELLS)



def reset_state():
    _loader.reset(globals(), _LOADED_NAMES, _LOADED_STATE)


def run_pipeline(directory, figures=False):
    """Hopper's actions on one MaplePy output folder, from Section 0 to
    Section 8, as Restart & Run All would after picking that folder. With
    figures, the paper figures (Sections 5 and 10) are drawn as well, after
    the export; a figure that cannot be drawn from this data is reported and
    skipped. Returns {figure: error} for the skipped ones."""
    reset_state()
    globals()['_HOPPER_RUN_DIRECTORY'] = str(_P(directory).resolve())
    for key in _manifest.HOPPER_PIPELINE:
        _loader.run(globals(), 'hopper', _manifest.HOPPER_RUN_CELLS[key])
    skipped = {}
    if figures:
        import matplotlib.pyplot as plt
        for key in _manifest.HOPPER_FIGURES:
            try:
                _loader.run(globals(), 'hopper',
                            _manifest.HOPPER_RUN_CELLS[key])
            except Exception as e:      # reported, never hidden
                skipped[key] = f'{type(e).__name__}: {e}'
                print(f'  figure step {key!r} skipped: {skipped[key]}')
            finally:
                plt.close('all')
    return skipped


# The state a fresh notebook session has once every definition has run,
# this module's own functions included; reset_state() returns to it.
_LOADED_NAMES, _LOADED_STATE = _loader.snapshot(globals())
_LOADED_NAMES = _LOADED_NAMES | {'_LOADED_NAMES', '_LOADED_STATE'}
