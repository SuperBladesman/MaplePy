# MaplePy

**MAPLE (Madelung Part of Lattice Energy) from CIF files, and Hoppe's additivity theorem tested at database scale.**

[![Licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![maplepy 1.4.0](https://img.shields.io/badge/maplepy-1.4.0-green.svg)
[![tests](https://github.com/SuperBladesman/MaplePy/actions/workflows/tests.yml/badge.svg)](https://github.com/SuperBladesman/MaplePy/actions/workflows/tests.yml)

MaplePy reads a folder of CIF files and computes the electrostatic (Madelung) part of the lattice energy of each structure, per site and in total, with the Ewald summation in *pymatgen*. Hopper takes the results and asks of each ternary oxide whether its MAPLE equals the weighted sum of its binary oxides, as Hoppe's additivity theorem predicts to within about 1%, and, where it does not, why not.

The second question is the hard one. A residual above 1% can mean covalency the point-charge model cannot see; it can equally mean a wrong oxidation state, a disorder model averaged into one charge, a binary oxide that does not exist, or coordinates that no ionic solid could have. Hopper separates these into twelve codes in three tiers, so that a residual is interpreted rather than merely reported.

Both tools were written for a study of 1,410 perovskite and pyrochlore structures from the Inorganic Crystal Structure Database (ICSD), now under review at *J. Appl. Cryst.* This release, maplepy 1.4.0, runs the versions behind that study: MaplePy 1.3.6, unchanged, and Hopper 1.2.9, which adds one column to 1.2.8. Run on the study's MaplePy results, it reproduces the classification of all 1,410 structures.

## What MaplePy reports

For each structure: MAPLE per formula unit (kcal/mol), the Madelung factor, the reference distance *d*<sub>ref</sub> (the shortest cation–anion distance), *Z*, and for each site its MAPLE, partial Madelung constant and reduced MAPLE. Four decisions come before the sum, and each is recorded beside the result.

| Decision | How MaplePy makes it |
|---|---|
| **Oxidation states** | In order: states you give; the per-site states in the CIF; the CIF's `_atom_type_oxidation_number` loop; a formula override in `data/maple_library.json`; a single common state per element. If none settles it, MaplePy stops and names the elements, rather than guessing. Which source was used is printed for every structure. |
| ***Z*** | The greatest common divisor of the number of sites holding each element, not the reduced composition, which returns *Z* = 1 for a non-stoichiometric refinement and inflates MAPLE per formula unit by the true *Z*. |
| **Disorder** | A shared or partly occupied site carries the occupancy-weighted mean charge of its species. The structure is flagged, with the kind of disorder and the sublattice it is on. |
| **Geometry** | The shortest contact in the cell, *d*<sub>min</sub>, is written for every structure. Below 0.5 Å two sites are one position split by a disorder model, and the Ewald sum over them is not an energy (`split_site`); below 1.6 Å the contact is shorter than any cation–anion bond these families produce (`short_contact`). The first threshold sits in an empty band of the measured distribution; the second is a judgement, and the code says so. |

MaplePy never edits a structure. Versions before 1.3.6 corrected an origin-choice artefact of the O2 sublattice in space group 62 (*Pnma*), choosing between two candidate structures by their Ewald energy, the quantity under test. It changed 44 of 938 perovskites, and in none of them turned a failing geometry into a sound one, so 1.3.6 removed it; a structure that cannot carry a Madelung energy is now reported, not repaired. The record of that decision is in the notebook, where the function used to be.

## What Hopper reports

Hopper decomposes each structure into binary oxides from the per-site oxidation states (ABO<sub>3</sub> with two trivalent cations becomes ½ A<sub>2</sub>O<sub>3</sub> + ½ B<sub>2</sub>O<sub>3</sub>; a 2+/4+ pair becomes AO + BO<sub>2</sub>), checks that the oxygen balances, and computes Δ = |MAPLE(ternary) − Σ MAPLE(binaries)| / MAPLE(ternary). Every structure then gets one code.

| Code | Tier | Meaning |
|---|---|---|
| Additive | 0 | Δ < 1% |
| 1.1 | 1 | The binary oxide exists and the reference table lacks it |
| 1.2 | 1 | MaplePy could not compute a MAPLE value (listed in `maple_failed.csv`, so always zero here) |
| 1.3 | 1 | The oxidation state is real and has no ambient binary oxide (Fe(IV), Co(IV), ...) |
| 1.4 | 1 | The charge asked for is not an oxidation state: a mean over a shared or disproportionated site |
| 2.1 | 2 | Δ > 10% in an ordered, oxygen-balanced structure: an oxidation state is probably wrong |
| 2.2 | 2 | *Z* taken as 1 when the cell holds more (cannot arise from MaplePy; kept for other calculators) |
| 2.3 | 2 | Cation disorder, through the mean-field approximation |
| 2.4 | 2 | The oxygen of the decomposition does not balance (Co<sub>3</sub>O<sub>4</sub> standing in for Co<sub>2</sub>O<sub>3</sub>) |
| 2.5 | 2 | Coordinate error: *d*<sub>min</sub> < 1.6 Å, or a spread of oxygen-site MAPLE values (CV > 0.05) that no sound *Pnma* perovskite has |
| 2.6 | 2 | Anion vacancies: fractional occupancy on the anion sublattice only |
| 2.7 | 2 | Split-site disorder model: two sites closer than 0.5 Å |
| 3.1 | 3 | Δ ≥ 1% with nothing above to explain it: a genuine violation |

Tier 1 has no residual to interpret, Tier 2 has one that should not be taken at face value, and Tier 3 has one that should. The codes are assigned in a fixed order, built on one rule: a caveat must not mask a defect. So Tier 1 comes first; then the structural defects, 2.7 and then 2.5, whatever the residual; then the additive test; then the other Tier 2 caveats; then 3.1. A disordered structure that agrees with its binaries is additive; a structure with impossible coordinates is 2.5 even when its residual is small.

From Hopper 1.2.9, every decomposition that uses an estimated or unsourced reference value says which (`estimated_binaries`). Nothing is reclassified on that account.

## Getting started

You need Python 3.11 or later. MaplePy is tested on Linux with Python 3.11 to 3.13 under pandas 2 and 3, and on Windows and macOS with Python 3.13.

```bash
pip install "git+https://github.com/SuperBladesman/MaplePy.git@v1.4.0"
maplepy --validate
```

`--validate` runs the notebook's three known answers: NaCl (partial Madelung constants 0.8738 and Madelung factor 1.7476; Hoppe, 1966), rutile and anatase TiO<sub>2</sub> against Hoppe (1995), and BaTiO<sub>3</sub> additive to within 1% (Hoppe, 1995; MaplePy gives 0.348%).

### One structure

```bash
maplepy examples/BaTiO3_cubic.cif
```

```
BaTiO3_cubic.cif  ·  BaTiO3  ·  Pm-3m

  MAPLE            4108.22 kcal/mol per formula unit  (17188.8 kJ/mol)
  Madelung factor  4.1259
  Z, d_ref         1, 2.0009 Å
  Geometry         ok: shortest contact 2.001 A
  Disorder         ordered
  Oxidation states (CIF (per-site, charge-neutral)): Ba=+2, O=-2, Ti=+4
```

Most Rietveld programs write element symbols without charges, and MaplePy does not guess where the chemistry is ambiguous. Give the states with `--ox`:

```bash
maplepy examples/SrFeO3_no_states.cif --ox Sr=2,Fe=4,O=-2
```

### A folder, then Hopper

```bash
maplepy examples/          # writes examples/outputs_YYYYMMDD_HHMMSS/
hopper examples/           # reads the latest run and classifies it
```

`maplepy FOLDER` runs the notebook's `batch_maple()` on every file ending `.cif` in the folder (lower case, and not in subfolders), on several processes where there are several cores (`--workers 1` for serial; the results are identical). `--plots` draws the notebook's three diagnostic plots; `--additivity` runs Hopper straight after. `hopper RESULTS --figures` draws the paper's figures into the run folder too, and says which, if any, the data cannot support.

The examples are constructed structures, none from the ICSD: the validation structures as CIFs, SrTiO<sub>3</sub>, an idealised pyrochlore, a disordered (Ba,Sr)TiO<sub>3</sub>, BaTiO<sub>3</sub> with its lattice parameter mistyped (Hopper: 2.5), and SrFeO<sub>3</sub> without oxidation states (MaplePy stops and asks). [examples/make_examples.py](examples/make_examples.py) writes them.

### From Python

```python
import maplepy

r = maplepy.compute('examples/BaTiO3_cubic.cif')
r.total_maple, r.madelung_factor, r.geometry_flag     # (4108.22, 4.1259, 'ok')
r.sites                                               # the per-site table

run = maplepy.run_folder('my_cifs/')                  # MaplePy's batch_maple()
df = maplepy.additivity(run)                          # Hopper on that run
df['classification'].value_counts()
```

`maplepy.engine()` and `maplepy.hopper_engine()` give every function the two notebooks define (`load_structure`, `compute_maple`, `decompose_ternary`, `classify_additivity`, ...), with the notebooks' behaviour.

### The notebooks

`MaplePy.ipynb` and `Hopper.ipynb` are the source of the code, and still run as before:

```bash
git clone https://github.com/SuperBladesman/MaplePy.git
cd MaplePy
pip install -r requirements.txt jupyterlab
jupyter lab MaplePy.ipynb
```

The package is built from their cells by `tools/build_engine.py`, and the tests fail if the two drift apart; [docs/PACKAGE.md](docs/PACKAGE.md) explains how.

## Output files

| File | Written by | One row per |
|---|---|---|
| `maple_results.csv` | MaplePy | site, in every structure: element, oxidation state, fractional coordinates, MAPLE, partial Madelung constant, reduced MAPLE |
| `maple_summary.csv` | MaplePy | structure: MAPLE, Madelung factor, *d*<sub>ref</sub>, *Z*, disorder, *d*<sub>min</sub>, geometry flag, MaplePy version |
| `maple_failed.csv` | MaplePy | CIF that could not be processed, with the reason |
| `additivity_classified.csv` | Hopper | structure: binary sum, Δ, oxygen balance, missing and estimated binaries, code, tier, label, Hopper version |

Hopper also writes two subsets, chosen by space group alone: `additivity_perovskites.csv` (nine space groups, *Pnma* among them) and `additivity_pyrochlores.csv` (*Fd*3̄*m* and *Fm*3̄*m*, so a rock-salt oxide lands among the pyrochlores). `binary_oxide_reference.csv` is the notebook's inline table of 104 binaries; the values Hopper used are those of the 112-entry table below, which agrees with the inline table wherever both hold a formula (Hopper stops if they do not).

## The binary oxide reference table

[data/binary_oxide_maple_reference.json](data/binary_oxide_maple_reference.json) contains 112 binary oxides. 88 values are medians of MaplePy MAPLE over qualifying ICSD entries at ambient conditions (273–303 K, < 0.15 MPa), each with the number of entries and their range; 23 are estimates, interpolated within a structure type or set by hand, with no published or computed source (`"sourced": false`); 1, Cu<sub>2</sub>O, was recorded as a MaplePy validation value and does not reproduce (MaplePy gives 797.9 kcal/mol for cuprite, not 730.0), so it is marked unsourced too. The table contains derived statistics only: no coordinates and no CIF content. It is released under CC-BY 4.0. Three entries carry a note saying they need re-deriving: CuO and ZnO, which rest on high-pressure rock-salt phases, and Cu<sub>2</sub>O. [data/README.md](data/README.md) describes the three data files.

## Limitations

- **Oxides.** The anion is identified by the sign of its charge, and by oxygen where no charges are yet assigned; the reference table and Hopper's decompositions are for oxides only.
- **Molecular anions.** Where covalent groups (SO<sub>4</sub><sup>2−</sup>, PO<sub>4</sub><sup>3−</sup>) are present, the additivity theorem needs increments rather than molecular binary oxides; Hopper does not implement them.
- **Shared sites in Hopper.** A site shared by two cations is decomposed as its majority species, at the mean charge. Such structures are flagged (2.3, or 1.4 where the mean is not an oxidation state), but their residuals are against an approximate sum.
- **Estimates.** In the study, 82 of the 1,380 decomposed structures rest on an estimated value (none on Cu<sub>2</sub>O), 43 of them on Ni<sub>2</sub>O<sub>3</sub>, which has no ambient phase to measure. `estimated_binaries` names them.
- **A user-supplied binary table.** Hopper's `BINARY_CSV` option reads your own binary values, but the bundled table then overrides any formula it also holds. To use your own values throughout, edit or replace the JSON.

## Tests

`maplepy --validate` runs the notebook's own validation. The test suite (`pytest`) asserts the three sourced targets independently, then tests each decision above on constructed structures, the classification of the examples, the command lines, the agreement of the package's cells with the notebooks, and the release metadata. On every push, CI runs it on Linux with Python 3.11, 3.12 and 3.13 under pandas 2 and 3, and on Windows and macOS with Python 3.13. [tools/equivalence.py](tools/equivalence.py) runs both notebooks headless on a folder of CIFs and compares their output with the package's, file by file and cell by cell.

No ICSD file is distributed here or used in the tests. ICSD CIFs are licensed by FIZ Karlsruhe.

## Citation

If you use MaplePy or Hopper, please cite the release you used (`CITATION.cff`; GitHub's "Cite this repository" reads it) and the paper describing the method:

> N. Reeves-McLaren and P. Gross, "Database-Scale Validation of Hoppe's MAPLE Additivity Theorem for Perovskite and Pyrochlore Oxides", *J. Appl. Cryst.*, under review.

## Contributing

A structure MaplePy or Hopper gets wrong is the most useful report there is. [CONTRIBUTING.md](CONTRIBUTING.md) says what to include, and how to change the code.

## Acknowledgements and AI disclosure

MaplePy and Hopper were developed with one generative AI tool, Claude (Anthropic). Nik Reeves-McLaren framed the problems and made the design decisions; Claude wrote the code to that specification; every change was audited, and correctness was checked independently of the code, against Hoppe's published values and by manual review of the structures flagged in the study.

## Licence

Code: MIT ([LICENSE](LICENSE)). The data tables in `data/`, the binary oxide reference table among them: CC-BY 4.0.
