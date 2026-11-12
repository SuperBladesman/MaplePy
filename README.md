# MaplePy

**MAPLE (Madelung Part of Lattice Energy) from crystallographic information files, and a test of Hoppe's additivity theorem at database scale.**

> **Status.** This repository holds the two notebooks as they were uploaded on 21st May 2026. They are unversioned and predate the versions used for the manuscript below (MaplePy 1.3.6 and Hopper 1.2.8). Those versions will be released here as a tested, installable package with a Zenodo DOI. Until then, treat these notebooks as a record of the method in May 2026, not as the code behind the manuscript's numbers.

## What is here

| File | What it is |
|---|---|
| `MaplePy.ipynb` | Computes per-site and total MAPLE values from CIF files with the Ewald summation in *pymatgen*, for one structure or a folder of them |
| `Hopper.ipynb` | Reads MaplePy's CSV output, decomposes each ternary oxide into its binary oxides, computes the additivity residual and classifies each structure |
| `binary_oxide_maple_reference.json` | 112 reference MAPLE values for binary oxides, in kcal/mol per formula unit (CC-BY 4.0) |

There is no Python package here yet: the notebooks are run cell by cell, and the `from maplepy import ...` interface that an earlier version of this README described does not exist.

## MAPLE and the additivity theorem

MAPLE is the electrostatic contribution to the lattice energy of an ionic crystal, computed from the Ewald sum over the full three-dimensional charge distribution. Bond valence sums assess local bonding geometry; MAPLE depends on the long-range electrostatic environment of every ion. Hoppe's additivity theorem predicts that the MAPLE of a ternary oxide equals the weighted sum of the MAPLE values of its binary oxides, typically to within 1%.

## MaplePy.ipynb (May 2026)

- MAPLE per formula unit, per-site MAPLE, partial Madelung constants, reduced MAPLE and the Madelung factor, from pymatgen's `EwaldSummation`;
- oxidation states from a priority chain that raises an error rather than assigning a charge it cannot justify;
- a mean-field charge on sites shared by more than one species;
- a correction for an origin-choice artefact of the O2 sublattice in space group 62 (*Pnma*);
- batch processing: `batch_maple()` writes `maple_results.csv` and `maple_failed.csv`, and the GUI cell (Section 7), which takes a hand-picked set of CIFs, also writes the `maple_summary.csv` that Hopper reads, each to a timestamped folder beside the CIFs;
- three validation calculations: NaCl (Madelung factor 1.7476; Hoppe, 1966), rutile and anatase TiO₂, and the additivity of BaTiO₃ to within 1% (Hoppe, 1995).

Two limitations of this copy matter. The oxidation-state chain looks for `maple_library.json` and `common_oxidation_states.json`, which are not in the repository, so for a CIF without oxidation states it stops and asks for them. And this version takes the number of formula units per cell, *Z*, from the reduced composition, which returns *Z* = 1 for many non-stoichiometric refinements and inflates MAPLE per formula unit by the true *Z*. Later versions take *Z* from the site multiplicities, and no longer apply the space group 62 correction; both changes will be documented with the release.

To run it:

```bash
git clone https://github.com/SuperBladesman/MaplePy.git
cd MaplePy
pip install pymatgen numpy pandas matplotlib jupyterlab
jupyter lab MaplePy.ipynb
```

Run the three validation sections first. The GUI cell (Section 7) opens a Tk file dialog; the diagnostic plots (Section 8) need `CIF_DIR` set to the folder you processed.

## Hopper.ipynb (May 2026)

Hopper reads `maple_summary.csv` and `maple_results.csv`, decomposes each structure into binary oxides using the per-site oxidation states, and reports the residual Δ = |MAPLE(ternary) − Σ MAPLE(binaries)| / MAPLE(ternary). Each structure is then classified: additive (Δ < 1%), or one of six codes in three tiers, with three more numbered and reserved (Tier 1, the decomposition is incomplete; Tier 2, the residual exists but an artefact bears on it; Tier 3, a genuine violation). The version used for the manuscript has twelve codes; the release will document the scheme in full.

## The reference table

`binary_oxide_maple_reference.json` holds 112 binary oxides. Of these, 88 are medians of MaplePy values over qualifying entries in the Inorganic Crystal Structure Database (ICSD) at ambient conditions, given with the number of entries and their range; 23 are estimates by interpolation within a structure type and carry no source; and 1 comes from a MaplePy validation structure. The file's own metadata still cites an earlier submission of the manuscript; that, and its entry counts, will be corrected with the release.

No ICSD CIF files are, or will be, distributed here.

## Citation

The manuscript describing the method and its application to 1,410 perovskite and pyrochlore structures is under review:

> N. Reeves-McLaren and P. Gross, "Database-Scale Validation of Hoppe's MAPLE Additivity Theorem for Perovskite and Pyrochlore Oxides", *J. Appl. Cryst.*, under review.

`CITATION.cff` gives the same details in machine-readable form, and GitHub's "Cite this repository" reads it.

## Acknowledgements

MaplePy and Hopper were developed with an AI coding assistant (Claude, Anthropic). Scientific interpretation and validation were carried out by the authors.

## Licence

Code: MIT ([LICENSE](LICENSE)). Binary oxide reference table: CC-BY 4.0.
