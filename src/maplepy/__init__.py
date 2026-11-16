"""maplepy: MAPLE (Madelung Part of Lattice Energy) from CIF files with
MaplePy, and Hoppe's additivity theorem tested on the results with Hopper.

    import maplepy
    r = maplepy.compute('examples/BaTiO3_cubic.cif')
    r.total_maple, r.madelung_factor, r.geometry_flag

    out = maplepy.run_folder('my_cifs/')        # MaplePy's batch_maple()
    df = maplepy.additivity(out)                 # Hopper, on that run

    maplepy.validate()                           # the three known answers

The engines are the notebooks MaplePy.ipynb and Hopper.ipynb, copied cell by
cell (see docs/PACKAGE.md).
"""

from ._manifest import HOPPER_VERSION, MAPLEPY_VERSION

__version__ = '1.4.0'

from .api import (MapleResult, additivity, compute, engine,  # noqa: E402
                  hopper_engine, run_folder, validate)

__all__ = ['__version__', 'MAPLEPY_VERSION', 'HOPPER_VERSION', 'MapleResult',
           'compute', 'run_folder', 'additivity', 'validate', 'engine',
           'hopper_engine']
