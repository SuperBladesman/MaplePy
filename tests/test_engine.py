"""MaplePy's decisions: where the oxidation states come from, Z, disorder,
and geometry. Each on a constructed structure."""
import pytest
from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifWriter

import maplepy

m = maplepy.engine()


def perovskite(a=4.0019, A='Ba', B='Ti'):
    return Structure.from_spacegroup('Pm-3m', Lattice.cubic(a), [A, B, 'O'],
                                     [[0, 0, 0], [0.5, 0.5, 0.5], [0.5, 0.5, 0]])


def write(s, path):
    CifWriter(s).write_file(path)
    return path


def test_states_written_in_the_cif_are_used(tmp_path):
    s = perovskite()
    s.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    r = maplepy.compute(write(s, tmp_path / 'bt.cif'))
    assert 'CIF (per-site, charge-neutral)' in r.log
    assert r.total_maple == pytest.approx(4108.22, abs=0.01)


def test_the_bundled_library_supplies_states_the_cif_lacks(tmp_path):
    # TiO2 carries no states here; Ti has two common states, so only the
    # formula override in maple_library.json can settle it (level 4)
    s = Structure.from_spacegroup(136, Lattice.tetragonal(4.5933, 2.9592),
                                  ['Ti', 'O'], [[0, 0, 0], [0.3048, 0.3048, 0]])
    r = maplepy.compute(write(s, tmp_path / 'rutile.cif'))
    assert 'maple_library.json (TiO2)' in r.log
    assert r.total_maple == pytest.approx(3255.8, abs=0.05)


ATOM_TYPE_CIF = """data_CaO
_symmetry_space_group_name_H-M 'F m -3 m'
_symmetry_Int_Tables_number 225
_cell_length_a 4.81
_cell_length_b 4.81
_cell_length_c 4.81
_cell_angle_alpha 90
_cell_angle_beta 90
_cell_angle_gamma 90
loop_
 _space_group_symop_operation_xyz
 'x, y, z'
 'x, y+1/2, z+1/2'
 'x+1/2, y, z+1/2'
 'x+1/2, y+1/2, z'
loop_
 _atom_type_symbol
 _atom_type_oxidation_number
 Ca2+ 2
 O2- -2
loop_
 _atom_site_label
 _atom_site_type_symbol
 _atom_site_fract_x
 _atom_site_fract_y
 _atom_site_fract_z
 Ca1 Ca 0 0 0
 O1 O 0.5 0.5 0.5
"""


def test_the_atom_type_loop_is_parsed():
    # Level 3 reads the loop itself, element by element
    import tempfile, pathlib
    p = pathlib.Path(tempfile.mkdtemp()) / 'cao.cif'
    p.write_text(ATOM_TYPE_CIF)
    assert m._extract_cif_oxidation_states(p) == {'Ca': 2, 'O': -2}


def test_the_atom_type_loop_is_used_when_pymatgen_assigns_nothing(tmp_path, monkeypatch):
    # Level 3. Current pymatgen reads this loop itself (level 2), so level 3
    # is reached only when its own assignment fails; that is simulated here.
    p = tmp_path / 'cao.cif'
    p.write_text(ATOM_TYPE_CIF)
    assert 'CIF (per-site, charge-neutral)' in maplepy.compute(p).log
    monkeypatch.setattr(m, '_has_native_oxi_states', lambda s: False)
    r = maplepy.compute(p)
    assert 'CIF (_atom_type, element-level fallback)' in r.log
    assert r.madelung_factor == pytest.approx(1.7476, abs=1e-4)


def test_single_state_elements_need_no_library_entry(tmp_path):
    # Level 5: Ca and O each have one common state, and CaO has no formula
    # override, so common_oxidation_states.json settles it
    s = Structure.from_spacegroup('Fm-3m', Lattice.cubic(4.81), ['Ca', 'O'],
                                  [[0, 0, 0], [0.5, 0.5, 0.5]])
    r = maplepy.compute(write(s, tmp_path / 'cao.cif'))
    assert 'common_oxidation_states.json' in r.log
    assert r.madelung_factor == pytest.approx(1.7476, abs=1e-4)


def test_an_ambiguous_state_stops_the_calculation(tmp_path):
    # Fe could be 2+ or 3+ (or, here, 4+): MaplePy asks rather than guesses
    p = write(perovskite(3.85, 'Sr', 'Fe'), tmp_path / 'sfo.cif')
    with pytest.raises(ValueError, match='Could not determine oxidation states'):
        maplepy.compute(p)
    r = maplepy.compute(p, oxidation_states={'Sr': 2, 'Fe': 4, 'O': -2})
    assert r.log.count('Oxidation states (user)') == 1


def test_z_comes_from_the_site_counts_not_the_composition():
    # Two cells of BaTiO3 with a part-occupied Ti site: the composition does
    # not reduce, but there are two formula units in the cell
    s = perovskite()
    s.make_supercell([2, 1, 1])
    s.replace_species({'Ti': {'Ti': 0.98}})
    s.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    _, z_comp = s.composition.get_reduced_composition_and_factor()
    assert round(z_comp) == 1
    assert m._derive_Z(s) == 2


def test_a_shared_site_takes_the_mean_charge_and_is_flagged():
    s = perovskite(3.95)
    s.replace_species({'Ba': {'Ba': 0.5, 'Sr': 0.5}})
    s.add_oxidation_state_by_element({'Ba': 2, 'Sr': 2, 'Ti': 4, 'O': -2})
    r = m.compute_maple(s, verbose=False)
    assert r['disordered'] and r['disorder_status'] == 'mixed occupancy'
    assert r['partial_sublattice'] == 'none'


def test_a_partly_occupied_anion_site_is_named():
    s = perovskite()
    s.replace_species({'O': {'O': 0.9}})
    s.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    kind, where = m._disorder_detail(s)
    assert kind == 'partial occupancy' and where == 'anion'


@pytest.mark.parametrize('a, flag', [(4.0019, 'ok'), (3.0019, 'short_contact')])
def test_short_contacts_are_reported_never_repaired(a, flag):
    s = perovskite(a)
    s.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    before = s.copy()
    r = m.compute_maple(s, verbose=False)
    assert r['geometry_flag'] == flag
    assert s == before              # the structure is not edited
    assert r['total_maple_kcal'] > 0


def test_two_sites_closer_than_half_an_angstrom_are_a_split_site():
    s = perovskite()
    s.replace_species({'Ba': {'Ba': 0.5}})
    s.append({'Ba': 0.5}, [0.05, 0, 0])
    s.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    d, flag, _ = m._geometry_status(s)
    assert d < 0.5 and flag == 'split_site'


def test_the_shortest_cation_anion_distance_is_d_ref():
    s = perovskite()
    s.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    assert m._find_d_ref(s) == pytest.approx(4.0019 / 2, abs=1e-6)


def test_a_structure_without_anions_has_no_d_ref():
    s = Structure(Lattice.cubic(3), ['Ba'], [[0, 0, 0]])
    s.add_oxidation_state_by_element({'Ba': 2})
    with pytest.raises(ValueError, match='cannot determine d_ref'):
        m._find_d_ref(s)
