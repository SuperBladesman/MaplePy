# Changelog

maplepy is the package; MaplePy and Hopper are its two engines, each a notebook with a version of its own (`MAPLEPY_VERSION`, `HOPPER_VERSION`). A release names all three. Each engine version below records what was wrong, what changed and what it does to results; the per-version notes and the version records in the code (`# v1.3.2: ...`) give the measurements behind each.

## maplepy

### maplepy 1.4.0 – 16th November 2026

The first packaged release, running MaplePy 1.3.6 and Hopper 1.3.0: the code of the revised *J. Appl. Cryst.* manuscript (ui5052).

- `maplepy FOLDER` runs `batch_maple()` on a folder of CIFs; `maplepy FILE.cif` prints one structure; `maplepy --validate` runs the notebook's three known answers. `hopper RESULTS` runs Hopper on a MaplePy run.
- A Python interface: `maplepy.compute()`, `run_folder()`, `additivity()` and `validate()`, and the two engines' own functions through `maplepy.engine()` and `maplepy.hopper_engine()`.
- The engines are the notebooks' cells, copied by `tools/build_engine.py`; CI fails if they drift. `tools/equivalence.py` compares the notebooks' output with the package's on a folder of CIFs.
- Tests: the three sourced targets asserted independently, each of MaplePy's decisions on constructed structures, Hopper's classification of the examples, the command lines, and the release metadata; CI on Linux with Python 3.11 to 3.13 under pandas 2 and 3, and on Windows and macOS with Python 3.13.
- Constructed example CIFs, none from the ICSD.
- The notebooks' prose corrected where it still described earlier versions: in MaplePy, the validation tolerance, brookite (given for reference, not computed), the batch cell's picker and output folder, the definition of `disordered`, and the docstring of `batch_maple()`; in Hopper, see 1.2.9. No MaplePy code changed, so it keeps 1.3.6.
- The reference data in `data/`: the binary oxide table (1.3.0), `maple_library.json` (1.0.1) and `common_oxidation_states.json`. The May 2026 repository had only the binary table, so its oxidation-state chain lost two levels.
- `tools/alternative_assignments.py` writes the evidence Hopper 1.3.0 needs for Type 2.1 (see 1.3.0).

Checked against the study: Hopper 1.3.0, run on the MaplePy 1.3.6 results for the 938 perovskites and 472 pyrochlores of the *J. Appl. Cryst.* manuscript with the study's two evidence files, gives every structure the classification the revised manuscript reports (714 and 299 additive). Without the evidence files it gives the same codes except 2.1 and the anion-contact 2.5, and says which test did not run.

## Hopper

### 1.3.0 – 16th November 2026

The classification of the revised *J. Appl. Cryst.* manuscript. Results change: on the study's MaplePy 1.3.6 results, 714 of 938 perovskites and 299 of 472 pyrochlores are additive, against 636 and 293 under 1.2.9.

- **Type 2.1 on evidence.** A structure is 2.1 when a different charge-balanced assignment of common oxidation states, recomputed through MaplePy, makes it additive and the chemistry agrees (`ASSIGNMENT_CHEMISTRY_REJECTED` lists the exceptions, with reasons). Hopper reads the evidence from `alternative_assignments.csv` in the run folder, which `tools/alternative_assignments.py` writes. The rule it replaces, Δ > 10% in an ordered, oxygen-balanced structure, assigned 2.1 to a large residual whatever caused it: 29 structures in the study, against 4 on evidence. 2.1 is now tested first, because a wrong deposited state can ask for a binary that does not exist.
- **A third Type 2.5 detector:** the shortest anion–anion contact below 2.35 Å (`ANION_ANION_MIN_ANG`), measured by Eir 2.0.46 or later and read from `eir_structures.csv` in the run folder. It finds misplaced oxygen sublattices that neither of MaplePy's geometry screens sees: 35 perovskites and all 28 pyrochlore 2.5s in the study, among them 18 of the 22 pyrochlores whose oxygen parameter was quoted for the wrong origin setting (the other four have contacts above 2.35 Å and are 3.1). Each label names the detectors that fired.
- **Reference table 1.3.0** (109 entries). Bi<sub>2</sub>O<sub>3</sub>, PbO, HgO, TcO<sub>2</sub> and Tl<sub>2</sub>O, which decompositions use, are ICSD medians (17, 10, 3, 2 and 2 ambient entries); the hand-set values were in error by up to 26% (Bi<sub>2</sub>O<sub>3</sub>). Ni<sub>2</sub>O<sub>3</sub> is re-estimated and Co<sub>2</sub>O<sub>3</sub> added by scaling six calibrated corundum sesquioxides by the ratio of cation–oxygen radius sums (Shannon radii, low-spin Ni<sup>3+</sup> 0.56 Å and Co<sup>3+</sup> 0.545 Å). Bi<sub>2</sub>O<sub>5</sub>, Ru<sub>2</sub>O<sub>5</sub>, RuO<sub>3</sub> and Re<sub>2</sub>O<sub>5</sub> are removed, because no ambient binary oxide of those states exists, so structures that need one are 1.3.
- Co<sup>3+</sup> decomposes to Co<sub>2</sub>O<sub>3</sub> like any other M<sup>3+</sup>, rather than to ⅓ Co<sub>3</sub>O<sub>4</sub>, which left the oxygen unbalanced and made every Co<sup>3+</sup> structure a 2.4.
- The classification summary prints each code's registry label, rather than the first structure's (which for 2.1 and 2.5 carries that structure's states or detectors), and counts the 2.5 structures each detector found.

### 1.2.9 – not released separately

- Every decomposition that uses an estimated or unsourced reference value names it, in a new column, `estimated_binaries`, and the batch summary counts them. 23 of the 112 values are estimates with no source, and the source recorded for a 24th, Cu<sub>2</sub>O, does not reproduce (table 1.1.1). In the study, no structure uses Cu<sub>2</sub>O, and 82 of the 1,380 decomposed structures rest on one: 52 perovskites (43 of them on Ni<sub>2</sub>O<sub>3</sub>) and 30 pyrochlores. Nothing is reclassified.
- The inline fallback labels "Estimated, to be updated" read "Estimated, unsourced".
- Prose that still described the first version corrected: the table of codes and their order in section 4 and the header of the classification cell (seven codes, ascending order), a usage example naming a function that does not exist, and two notes in section 9 (that the reference values "must be replaced", and that a *Z* fix was "in progress"; MaplePy has had it since 1.1). No result changes.
- A local path in a comment generalised.

### 1.2.8 – 25th August 2026

- The classification waterfall (Figure 7) places each label at the highest row where it clears its neighbour, measured from its own width, rather than alternating rows; narrow slices no longer overprint. No result changes.

### 1.2.7 – 25th August 2026

- The figures read the classification registry instead of hand-written maps of seven codes, which dropped codes 1.3, 1.4, 2.6 and 2.7 from every scatter and raised `KeyError` on the first structure carrying one of the other five. Figure 2's panel (b), which zoomed on a *Z* = 1 cluster that no longer exists, is drawn only when there is a cluster.

### 1.2.6 – 25th August 2026

- Codes 1.2 (upstream failure) and 2.2 (*Z* = 1 artefact) are defined and reported as zero, rather than reserved and absent; the order of the codes is derived from the registry.
- `OXI_ROUNDING_TOL` re-measured over all 29,226 sites rather than the 30 with a missing binary: there is no empty band, so the tolerance is documented as a judgement.

### 1.2.5 – 25th August 2026

- The rounding of a non-integer mean charge is carried in the `missing_binaries` string, which reaches the classifier and the CSV; the parallel list it used to live in never did. This found a third route to code 1.4: means over a non-stoichiometric refinement (Nd<sub>4</sub>Cu<sub>4</sub>O<sub>11.724</sub>, Nd<sub>4</sub>Ru<sub>3.544</sub>O<sub>12</sub>).
- The folder dialog no longer hides behind the browser when the notebook is run twice in one kernel; `MAPLE_DIR_OVERRIDE` skips it.

### 1.2.4 – 25th August 2026

- Lookups by structure use an index built once instead of a scan of the whole frame per structure; on the perovskite run the three loops concerned had taken about 12 s between them. No result changes.

### 1.2.3 – 25th August 2026

- Code 1.1 meant four different things. It now means only that the table lacks a binary that exists; 1.3 (no binary end-member exists) and 1.4 (the charge is not an oxidation state) take the rest, from a registry of every missing binary with the reason.
- The decomposition records where it had to round a mean charge to choose a binary (Y<sub>3</sub>NbO<sub>7</sub>: Y asked for at +3.5).

### 1.2.2 – 24th August 2026

- Code 2.5 has a second detector, the shortest contact below MaplePy's `SHORT_CONTACT_ANG`, beside the oxygen-site CV test, which only a 20-site *Pnma* cell can take. Each catches structures the other cannot.
- Code 2.6 (anion vacancy disorder) is assigned, from the sublattice MaplePy 1.3.3 reports; it is tested before 2.3.
- Code 2.7 (split-site disorder model) is read from MaplePy's `geometry_flag`.

### 1.2.1 – 24th August 2026

- A decomposition missing a binary no longer writes a residual: 30 structures had sums missing a whole component, with residuals up to 93%, and sat in Figure 1's tail as if measured.
- Hoppe's 1% criterion is one constant, `ADDITIVE_THRESHOLD_PCT`, rather than four literals; Figure 1 and the classifier now count the same population (they disagreed by one, 662 against 661).
- `hopper_version` is written into the classified export.

### 1.2 – 24th August 2026

- The released JSON table is read first, and a guard stops the run if any value differs from the inline table; the inline table had 104 of the JSON's 112 entries.

### 1.1 – 24th August 2026

- A residual of exactly zero, the result the theorem predicts, was written out as missing (`if delta_abs` is false for 0.0).
- Counts removed from code descriptions, which had drifted from the data (32, 19 and 31 for one population); the notebook prints the populations it finds.
- The oxygen-balance tolerance measured over 101 decompositions and left alone: nothing lies inside its gap.

### Hopper.ipynb – 21st May 2026

The version uploaded to this repository: six codes in use beside Additive, in three tiers, and three more reserved (1.2, 2.5, 2.6).

## MaplePy

### 1.3.6 – 25th August 2026

- The space group 62 origin correction is removed. It chose between the deposited structure and one with the O2 sublattice shifted by (½, ½, 0) by their Ewald energy, the quantity under test; it changed 44 of 938 perovskites, by up to 8.1%, made one shortest contact worse, and in none of the 44 turned a failing geometry into a sound one. MAPLE is now computed on the structure as deposited, and the geometry flags do the work. The reasons are kept in the notebook where the function was.

The release copy of 1.3.6 differs from the working copy only in prose: its notes cell, which said that mixed-occupancy sites were not handled (they have been since 1.1) and cited the WAGII paper and Eir out of date; four markdown cells and a docstring that described earlier versions; and a local path in a comment. No code differs.

### 1.3.5 – 25th August 2026

- The GUI is a folder picker in front of `batch_maple()`, rather than a file picker with its own copy of the batch.

### 1.3.4 – 25th August 2026

- One function, `process_one_cif()`, processes a CIF, serially or on a pool of workers (`MAPLE_WORKERS`); every value is identical either way. Its printed output, which is the only record of where the oxidation states came from, is captured and printed by the caller, so a parallel run reports it too.

### 1.3.3 – 24th August 2026

- A second geometry threshold, `SHORT_CONTACT_ANG` (1.6 Å), for coordinate errors: 26 perovskites have a shortest contact between 1.0 and 1.6 Å. Unlike the split-site threshold it lies in a continuum, and is documented as a judgement.
- The split-site threshold confirmed on the whole dataset: the band from 0.5 to 1.0 Å is empty.
- The disorder flag says which sublattice carries the fractional occupancy.

### 1.3.2 – 24th August 2026

- A geometry test: `d_min_ang` for every structure, and two sites closer than 0.5 Å flagged as a split site. Four structures in the 1,410 had Ewald sums up to ten times the family median and were reported as ordinary results.
- Partly occupied single-species sites count as disordered: 12 of 97 probed structures had been labelled ordered.

### 1.3.1 – 24th August 2026

- `batch_maple()` writes `maple_summary.csv`, which Hopper reads; only the GUI used to.
- The data directory is resolved once; the batch and the GUI had each overridden it, silently dropping two levels of the oxidation-state chain.
- The plotting cell's path to another machine's Downloads folder replaced by the run just made.
- `maplepy_version` is written into the results and summary CSVs.

### 1.3 – 24th August 2026

- The cell is pinned to the primitive cell explicitly; a deprecated default had been doing it. MAPLE per formula unit, *d*<sub>ref</sub> and the Madelung factor are the same in either cell.

### 1.2 – 24th August 2026

- The data directory defaults to `data/`, where the data are, rather than the working directory.

### 1.1 – 24th August 2026

- *Z* from the site counts, not the reduced composition. Composition reduction had returned *Z* = 1 for 172 of the 1,410 structures, 165 of them with a fractional subscript, and inflated their MAPLE per formula unit by the true *Z*.
- *d*<sub>ref</sub> is the shortest cation–anion distance; when a structure has no cation or no anion MaplePy says so, instead of returning the distance from site 0 to anything.
- Each tolerance named once (two had been written twice, with different values); a missing data file and an unreadable one are different errors.
- The site-mean convention of the Madelung factor written down.

### MaplePy.ipynb – 21st May 2026

The version uploaded to this repository.
