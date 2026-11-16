"""The package's cells are the notebooks' cells."""
import json
import re
import subprocess
import sys
from pathlib import Path

import maplepy

ROOT = Path(__file__).resolve().parents[1]


def test_the_cells_match_the_notebooks():
    p = subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_engine.py'),
                        '--check'], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr


def _version(nb, name):
    src = '\n'.join(''.join(c['source']) for c in json.loads(
        (ROOT / nb).read_text(encoding='utf-8'))['cells'])
    return re.search(rf"^{name} = '([^']+)'", src, re.M).group(1)


def test_the_versions_are_the_notebooks():
    assert maplepy.MAPLEPY_VERSION == _version('MaplePy.ipynb', 'MAPLEPY_VERSION')
    assert maplepy.HOPPER_VERSION == _version('Hopper.ipynb', 'HOPPER_VERSION')
    assert maplepy.engine().MAPLEPY_VERSION == maplepy.MAPLEPY_VERSION
    assert maplepy.hopper_engine().HOPPER_VERSION == maplepy.HOPPER_VERSION


def test_the_notebooks_carry_no_outputs_or_local_paths():
    for nb in ('MaplePy.ipynb', 'Hopper.ipynb'):
        text = (ROOT / nb).read_text(encoding='utf-8')
        d = json.loads(text)
        assert all(not c.get('outputs') for c in d['cells']), nb
        for pat in (r'[A-Z]:\\\\', r'/Users/', r'[\\/]Downloads[\\/]',
                    r'/home/[a-z]', r'My Drive'):
            assert not re.search(pat, text), (nb, pat)
