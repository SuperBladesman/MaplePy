"""The three sourced validation targets, asserted here independently of the
notebook's own PASS/FAIL cells (which maplepy.validate() runs, below)."""
import pytest
from pymatgen.core import Lattice, Structure

import maplepy

m = maplepy.engine()


def rock_salt(a, A, X, qa, qx):
    s = Structure.from_spacegroup('Fm-3m', Lattice.cubic(a), [A, X],
                                  [[0, 0, 0], [0.5, 0.5, 0.5]])
    s.add_oxidation_state_by_element({A: qa, X: qx})
    return s


def test_nacl_partial_madelung_constants_and_madelung_factor():
    # Hoppe (1966): PMC(Na+) = PMC(Cl-) = 0.8738, MF = 1.7476 for rock salt
    r = m.compute_maple(rock_salt(5.6402, 'Na', 'Cl', 1, -1), verbose=False)
    pmc = {s['element']: s['pmc'] for s in r['per_site']}
    assert pmc['Na'] == pytest.approx(0.8738, abs=5e-4)
    assert pmc['Cl'] == pytest.approx(0.8738, abs=5e-4)
    assert pmc['Na'] == pytest.approx(pmc['Cl'], abs=1e-6)   # exact by symmetry
    assert r['madelung_factor'] == pytest.approx(1.7476, abs=1e-4)


@pytest.mark.parametrize('a', [4.2112, 4.8105, 5.1408, 5.5391])
def test_madelung_factor_is_invariant_across_rock_salts(a):
    r = m.compute_maple(rock_salt(a, 'Mg', 'O', 2, -2), verbose=False)
    assert r['madelung_factor'] == pytest.approx(1.7476, abs=1e-4)


def test_tio2_rutile_and_anatase_against_hoppe_1995():
    # Hoppe (1995), Table 5: rutile 3254.6, anatase 3260.7 kcal/mol
    rutile = Structure.from_spacegroup(136, Lattice.tetragonal(4.5933, 2.9592),
                                       ['Ti', 'O'], [[0, 0, 0], [0.3048, 0.3048, 0]])
    anatase = Structure.from_spacegroup(141, Lattice.tetragonal(3.7845, 9.5143),
                                        ['Ti', 'O'], [[0, 0, 0], [0, 0, 0.2082]])
    for s in (rutile, anatase):
        s.add_oxidation_state_by_element({'Ti': 4, 'O': -2})
    r = m.compute_maple(rutile, verbose=False)['total_maple_kcal']
    a = m.compute_maple(anatase, verbose=False)['total_maple_kcal']
    assert abs(r - 3254.6) < 50 and abs(a - 3260.7) < 50
    assert abs(r - a) < 15          # the near-degeneracy is the result
    assert r == pytest.approx(3255.8, abs=0.05)   # regression: MaplePy 1.3.6
    assert a == pytest.approx(3262.74, abs=0.05)


def test_batio3_is_additive_to_within_one_percent():
    # Hoppe (1995), p. 560: MAPLE(BaTiO3) = MAPLE(BaO) + MAPLE(TiO2) to 0.07%
    bao = rock_salt(5.5391, 'Ba', 'O', 2, -2)
    rutile = Structure.from_spacegroup(136, Lattice.tetragonal(4.5933, 2.9592),
                                       ['Ti', 'O'], [[0, 0, 0], [0.3048, 0.3048, 0]])
    rutile.add_oxidation_state_by_element({'Ti': 4, 'O': -2})
    bt = Structure.from_spacegroup('Pm-3m', Lattice.cubic(4.0019), ['Ba', 'Ti', 'O'],
                                   [[0, 0, 0], [0.5, 0.5, 0.5], [0.5, 0.5, 0]])
    bt.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    rb, rr, rt = (m.compute_maple(s, verbose=False) for s in (bao, rutile, bt))
    out = m.check_additivity(rt, [(rb, 1), (rr, 1)], verbose=False)
    assert out['delta_pct'] < 1.0
    assert out['delta_pct'] == pytest.approx(0.348, abs=0.001)   # as reported


def test_validate_runs_the_notebook_section_2_and_passes():
    flags = maplepy.validate()
    assert set(flags) == {'pass_na', 'pass_cl', 'pass_mf', 'pass_sym',
                          'pass_r', 'pass_a', 'pass_diff', 'pass_add'}
    assert all(flags.values())


def test_validate_leaves_the_engine_as_it_was():
    names = set(vars(m))
    maplepy.validate()
    assert set(vars(m)) == names
