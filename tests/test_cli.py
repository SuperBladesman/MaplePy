import subprocess
import sys
from pathlib import Path

import maplepy

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=None, env=None):
    p = subprocess.run([sys.executable, '-c',
                        'import sys; from maplepy.cli import main_maplepy, '
                        'main_hopper; f = main_hopper if sys.argv[1] == '
                        '"hopper" else main_maplepy; '
                        'raise SystemExit(f(sys.argv[2:]))', *args],
                       capture_output=True, text=True, cwd=cwd,
                       env={'MPLBACKEND': 'Agg', **__import__('os').environ,
                            **(env or {})})
    return p.returncode, p.stdout + p.stderr


def test_version_names_both_engines():
    code, out = run('maplepy', '--version')
    assert code == 0
    assert f'MaplePy {maplepy.MAPLEPY_VERSION}' in out
    assert f'Hopper {maplepy.HOPPER_VERSION}' in out


def test_validate_passes():
    code, out = run('maplepy', '--validate')
    assert code == 0, out
    assert '8 of 8 passed.' in out


def test_one_cif():
    code, out = run('maplepy', str(ROOT / 'examples' / 'BaTiO3_cubic.cif'))
    assert code == 0, out
    assert 'MAPLE            4108.22 kcal/mol' in out
    assert 'Madelung factor  4.1259' in out


def test_one_cif_that_needs_states():
    p = str(ROOT / 'examples' / 'SrFeO3_no_states.cif')
    code, out = run('maplepy', p)
    assert code == 1 and 'Could not determine oxidation states' in out
    code, out = run('maplepy', p, '--ox', 'Sr=2,Fe=4,O=-2')
    assert code == 0, out


def test_a_folder_then_hopper(examples):
    code, out = run('maplepy', str(examples), '--workers', '1')
    assert code == 0, out
    runs = sorted(examples.glob('outputs_*'))
    assert len(runs) == 1
    assert (runs[0] / 'maple_summary.csv').exists()
    code, out = run('hopper', str(examples))       # finds the latest run
    assert code == 0, out
    assert (runs[0] / 'additivity_classified.csv').exists()
    assert '2.5' in out and 'Structural coordinate error' in out


def test_bad_arguments():
    assert run('maplepy', '--ox', 'Ba2')[0] != 0
    assert run('maplepy', 'no/such/folder')[0] == 2
    assert run('maplepy')[0] == 2


def test_a_console_that_cannot_write_unicode(examples):
    # A Windows console redirected to a file encodes as cp1252, and the
    # notebook prints check marks as it goes
    code, out = run('maplepy', str(examples), '--workers', '1',
                    env={'PYTHONIOENCODING': 'cp1252'})
    assert code == 0, out
