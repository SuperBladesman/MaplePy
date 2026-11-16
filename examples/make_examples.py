"""Write the example CIFs in this folder.

Every structure here is constructed, from a space group, a lattice parameter
and ideal or rounded positions; none is a deposited refinement, and none
comes from the ICSD. Lattice parameters are the ones MaplePy's own
validation section uses where it has one (Section 2 of MaplePy.ipynb), and
round literature values otherwise. Run it to regenerate the files:

    python examples/make_examples.py
"""

from pathlib import Path

from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifWriter

HERE = Path(__file__).resolve().parent


def cubic_perovskite(a, A, B, X='O'):
    return Structure.from_spacegroup('Pm-3m', Lattice.cubic(a), [A, B, X],
                                     [[0, 0, 0], [0.5, 0.5, 0.5],
                                      [0.5, 0.5, 0]])


def write(s, name, states=True, note=''):
    path = HERE / name
    try:
        CifWriter(s, symprec=0.01).write_file(path)
    except Exception:          # symmetry not found: write it in P1
        CifWriter(s, symprec=None).write_file(path)
    text = path.read_text()
    head = ('# Constructed example for MaplePy; not a refinement, not from '
            'the ICSD.\n')
    if note:
        head += ''.join(f'# {line}\n' for line in note.splitlines())
    path.write_text(head + text)
    print('wrote', name, '(with oxidation states)' if states else '')


def main():
    # The validation structures of Section 2, as CIFs
    s = Structure.from_spacegroup('Fm-3m', Lattice.cubic(5.5391), ['Ba', 'O'],
                                  [[0, 0, 0], [0.5, 0.5, 0.5]])
    s.add_oxidation_state_by_element({'Ba': 2, 'O': -2})
    write(s, 'BaO_rocksalt.cif', note='a = 5.5391 A, as in Section 2.3.')

    s = Structure.from_spacegroup(136, Lattice.tetragonal(4.5933, 2.9592),
                                  ['Ti', 'O'], [[0, 0, 0], [0.3048, 0.3048, 0]])
    s.add_oxidation_state_by_element({'Ti': 4, 'O': -2})
    write(s, 'TiO2_rutile.cif', note='a = 4.5933 A, c = 2.9592 A, '
                                     'u = 0.3048, as in Section 2.2.')

    s = cubic_perovskite(4.0019, 'Ba', 'Ti')
    s.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    write(s, 'BaTiO3_cubic.cif', note='a = 4.0019 A, as in Section 2.3.')

    s = cubic_perovskite(3.905, 'Sr', 'Ti')
    s.add_oxidation_state_by_element({'Sr': 2, 'Ti': 4, 'O': -2})
    write(s, 'SrTiO3_cubic.cif', note='a = 3.905 A.')

    # An ordered pyrochlore A2B2O7, Fd-3m (origin choice 2): A on 16d, B on
    # 16c, O on 48f (x, 1/8, 1/8) and 8b (3/8, 3/8, 3/8)
    s = Structure.from_spacegroup(
        'Fd-3m:2', Lattice.cubic(10.185), ['Gd', 'Ti', 'O', 'O'],
        [[0.5, 0.5, 0.5], [0, 0, 0], [0.330, 0.125, 0.125],
         [0.375, 0.375, 0.375]])
    s.add_oxidation_state_by_element({'Gd': 3, 'Ti': 4, 'O': -2})
    write(s, 'Gd2Ti2O7_pyrochlore.cif',
          note='a = 10.185 A, x(48f) = 0.330, origin choice 2.')

    # A mixed A site: the mean-field charge approximation
    s = cubic_perovskite(3.95, 'Ba', 'Ti')
    s.replace_species({'Ba': {'Ba': 0.5, 'Sr': 0.5}})
    s.add_oxidation_state_by_element({'Ba': 2, 'Sr': 2, 'Ti': 4, 'O': -2})
    write(s, 'Ba0.5Sr0.5TiO3_disordered.cif',
          note='a = 3.95 A; Ba and Sr share the A site at 0.5 each.')

    # A geometry fault: BaTiO3 with its lattice parameter mistyped, as a
    # transcription error might give it. Ti-O 1.50 A is shorter than any
    # cation-anion bond in an oxide, and MaplePy says so.
    s = cubic_perovskite(3.0019, 'Ba', 'Ti')
    s.add_oxidation_state_by_element({'Ba': 2, 'Ti': 4, 'O': -2})
    write(s, 'BaTiO3_wrong_cell.cif',
          note='a = 3.0019 A: the 4.0019 A of BaTiO3_cubic.cif with its first '
               'digit mistyped.')

    # No oxidation states, and an element with more than one common state:
    # MaplePy stops and asks, rather than guessing Fe(II) or Fe(III)
    s = cubic_perovskite(3.85, 'Sr', 'Fe')
    write(s, 'SrFeO3_no_states.cif', states=False,
          note='a = 3.85 A; no oxidation states. Run with '
               '--ox Sr=2,Fe=4,O=-2.')


if __name__ == '__main__':
    main()
