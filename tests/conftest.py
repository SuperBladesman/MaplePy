import os
import shutil
from pathlib import Path

import pytest

os.environ.setdefault('MPLBACKEND', 'Agg')

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples'


@pytest.fixture
def examples(tmp_path):
    """A copy of the example CIFs, so that runs write outside the repository."""
    d = tmp_path / 'cifs'
    d.mkdir()
    for f in EXAMPLES.glob('*.cif'):
        shutil.copy2(f, d / f.name)
    return d


@pytest.fixture(scope='session')
def example_run(tmp_path_factory):
    """One MaplePy run over the examples, then Hopper on it, shared by the
    tests that only read the results."""
    import maplepy
    d = tmp_path_factory.mktemp('run') / 'cifs'
    d.mkdir()
    for f in EXAMPLES.glob('*.cif'):
        shutil.copy2(f, d / f.name)
    out = maplepy.run_folder(d, workers=1)
    df = maplepy.additivity(out)
    return out, df
