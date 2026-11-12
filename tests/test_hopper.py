"""Hopper on MaplePy runs: decomposition, residual, classification, and the
estimate flag of 1.2.9."""
import json
from pathlib import Path

import pandas as pd
import pytest
from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifWriter

import maplepy

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / 'data' / 'binary_oxide_maple_reference.json'


def by_cif(df):
    return df.set_index('source_cif')


def test_the_examples_classify_as_documented(example_run):
    _, df = example_run
    c = by_cif(df)['classification'].to_dict()
    assert c['BaTiO3_cubic.cif'] == 'Additive'
    assert c['Gd2Ti2O7_pyrochlore.cif'] == 'Additive'
    assert c['BaO_rocksalt.cif'] == 'Additive'
    assert c['TiO2_rutile.cif'] == 'Additive'
    assert c['BaTiO3_wrong_cell.cif'] == '2.5'     # the short Ti-O contact
    assert c['Ba0.5Sr0.5TiO3_disordered.cif'] == '2.3'
    assert c['SrTiO3_cubic.cif'] == '3.1'
    assert 'SrFeO3_no_states.cif' not in c           # failed upstream (1.2)


def test_the_residual_is_the_one_hoppe_defines(example_run):
    _, df = example_run
    r = by_cif(df).loc['BaTiO3_cubic.cif']
    table = {e['formula']: e['maple_kcal_mol']
             for e in json.loads(TABLE.read_text())['entries']}
    assert r['maple_binary_sum'] == pytest.approx(table['BaO'] + table['TiO2'])
    expected = 100 * abs(r['maple_ternary'] - r['maple_binary_sum']) / r['maple_ternary']
    assert r['delta_pct'] == pytest.approx(expected, abs=1e-3)


def test_the_export_is_written_beside_the_run(example_run):
    out, df = example_run
    disk = pd.read_csv(out / 'additivity_classified.csv')
    assert len(disk) == len(df)
    assert set(disk['hopper_version']) == {maplepy.HOPPER_VERSION}
    assert {'classification', 'classification_tier', 'estimated_binaries'} <= set(disk)


def _run(tmp_path, structures, ox=None):
    d = tmp_path / 'cifs'
    d.mkdir()
    for name, s in structures.items():
        CifWriter(s).write_file(d / name)
    return maplepy.additivity(maplepy.run_folder(d, workers=1,
                                                 oxidation_states=ox))


def perovskite(a, A, B):
    return Structure.from_spacegroup('Pm-3m', Lattice.cubic(a), [A, B, 'O'],
                                     [[0, 0, 0], [0.5, 0.5, 0.5], [0.5, 0.5, 0]])


def test_a_residual_resting_on_an_estimate_says_so(tmp_path):
    # PbO's reference value is an estimate, with no source; TiO2's is an
    # ICSD median. The residual is computed and classified as before.
    s = perovskite(3.97, 'Pb', 'Ti')
    s.add_oxidation_state_by_element({'Pb': 2, 'Ti': 4, 'O': -2})
    t = Structure.from_spacegroup('Pm-3m', Lattice.cubic(4.0019), ['Ba', 'Ti', 'O'],
                                  [[0, 0, 0], [0.5, 0.5, 0.5], [0.5, 0.5, 0]])
    t.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    df = by_cif(_run(tmp_path, {'PbTiO3.cif': s, 'BaTiO3.cif': t}))
    assert df.loc['PbTiO3.cif', 'estimated_binaries'] == 'PbO'
    assert pd.isna(df.loc['BaTiO3.cif', 'estimated_binaries']) or \
        df.loc['BaTiO3.cif', 'estimated_binaries'] == ''
    assert df.loc['PbTiO3.cif', 'success']


def test_an_oxidation_state_with_no_binary_oxide_is_tier_1(tmp_path):
    # Fe(IV) has no ambient binary oxide: nothing to sum against (code 1.3)
    s = perovskite(3.85, 'Sr', 'Fe')
    df = _run(tmp_path, {'SrFeO3.cif': s}, ox={'Sr': 2, 'Fe': 4, 'O': -2})
    r = df.iloc[0]
    assert r['classification'] == '1.3'
    assert pd.isna(r['delta_pct'])          # no number without a meaning


def test_the_reference_table_and_its_flags():
    d = json.loads(TABLE.read_text())
    e = d['entries']
    assert len(e) == d['_metadata']['n_entries'] == 112
    est = {x['formula'] for x in e if x['source'] == 'estimated'}
    assert len(est) == 23
    # Cu2O's recorded validation source does not reproduce (797.9, not 730.0)
    unsourced = {x['formula'] for x in e if not x['sourced']}
    assert unsourced == est | {'Cu2O'}
    assert all('review_note' in x for x in e if x['formula'] in ('CuO', 'ZnO', 'Cu2O'))
    assert maplepy.hopper_engine().ESTIMATED_BINARIES == unsourced
    assert 'J. Appl. Cryst.' in d['_metadata']['citation']


def test_the_inline_fallback_never_disagrees_with_the_released_table():
    h = maplepy.hopper_engine()
    table = {x['formula']: x['maple_kcal_mol']
             for x in json.loads(TABLE.read_text())['entries']}
    for f, (v, _t, _s) in h.BINARY_MAPLE_FALLBACK.items():
        assert table[f] == pytest.approx(v), f


def test_hopper_reads_the_bundled_table():
    h = maplepy.hopper_engine()
    assert Path(h._binary_source).resolve() == TABLE.resolve() or \
        Path(h._binary_source).name == TABLE.name


def test_a_folder_without_maplepy_output_fails_loudly(tmp_path):
    with pytest.raises(FileNotFoundError, match='maple_summary.csv'):
        maplepy.additivity(tmp_path)


def test_the_recorded_cu2o_value_does_not_reproduce(tmp_path):
    # The table records 730.0 for cuprite as a MaplePy validation value.
    # MaplePy gives 797.9 at a = 4.270 A (Cu-O 1.849 A), so the entry is
    # marked unsourced and Hopper names it wherever it is used.
    s = Structure(Lattice.cubic(4.270), ['O', 'O', 'Cu', 'Cu', 'Cu', 'Cu'],
                  [[0, 0, 0], [.5, .5, .5], [.25, .25, .25], [.75, .75, .25],
                   [.75, .25, .75], [.25, .75, .75]])
    s.add_oxidation_state_by_element({'Cu': 1, 'O': -2})
    CifWriter(s).write_file(tmp_path / 'cu2o.cif')
    r = maplepy.compute(tmp_path / 'cu2o.cif')
    assert r.total_maple == pytest.approx(797.9, abs=0.1)
    cu2o = next(x for x in json.loads(TABLE.read_text())['entries']
                if x['formula'] == 'Cu2O')
    assert cu2o['maple_kcal_mol'] == 730.0 and cu2o['sourced'] is False

