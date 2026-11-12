# Reference data

MaplePy and Hopper read three files from this folder. The notebooks find it as `data/` beside them; the package carries a copy.

| File | Read by | What it holds | Licence |
|---|---|---|---|
| `binary_oxide_maple_reference.json` | Hopper | MAPLE of 112 binary oxides, kcal/mol per formula unit, with how each was determined | CC-BY 4.0 |
| `maple_library.json` | MaplePy | Formula overrides for oxidation states (level 4 of the chain); Hoppe's reference values and isostructural constants, for reference | CC-BY 4.0 |
| `common_oxidation_states.json` | MaplePy | Common oxidation states of 80 elements (level 5 of the chain: used only where an element has one) | CC-BY 4.0 |

## binary_oxide_maple_reference.json

Each entry gives the formula, the value, the structure type and space group, and `source`:

- `icsd_median` (88 entries): the median MAPLE that MaplePy computes over qualifying entries of the Inorganic Crystal Structure Database at ambient conditions (273–303 K, < 0.15 MPa), excluding high-pressure entries (identified by anomalously short *d*<sub>ref</sub>), failed calculations and non-stoichiometric compositions. `n_icsd_entries`, `icsd_range_min` and `icsd_range_max` give the number of entries and their range. The median is used for its robustness to the occasional misindexed entry.
- `estimated` (23 entries): interpolated within a structure type family, or set by hand. These have no published or computed source, and say so (`"sourced": false`). They are kept so that results made with them can be reproduced, and Hopper reports every decomposition that uses one.
- `validation` (1 entry): Cu<sub>2</sub>O, from a MaplePy validation structure.

`confidence` is `high` for a median over 10 or more entries, `medium` for 2 to 9 entries or a validation value, and `low` for an estimate or an entry flagged for re-deriving (`review_note`).

The table holds derived statistics only: no coordinates, and no content of any CIF. Eight of the 112 entries are molecular or non-metal oxides (SO<sub>3</sub>, P<sub>2</sub>O<sub>5</sub>, B<sub>2</sub>O<sub>3</sub>, As<sub>2</sub>O<sub>5</sub>, Sb<sub>2</sub>O<sub>3</sub>, SeO<sub>3</sub>, Cl<sub>2</sub>O<sub>7</sub>, H<sub>2</sub>O), added for work beyond perovskites and pyrochlores; Hopper's inline fallback table holds the other 104, and the notebook stops if a value ever differs between the two.

### Versions

- **1.1.1** (this release): the citation names the journal the manuscript is under review at (it named an earlier submission); each entry says whether it has a source (`sourced`); CuO and ZnO are marked for re-deriving. No value has changed.
- **1.1.0** (24th August 2026): entry counts and source classifications computed from the entries, rather than written by hand.
- **1.0.0** (21st May 2026): the first release, uploaded with the notebooks.

## Changing the data

A new or changed value needs a source: the ICSD query and the run that produced a median, or a published value. Change the JSON, raise its version, describe the change above and in `CHANGELOG.md`, and run the tests, which check that Hopper's inline table and the JSON still agree. Never commit the CIFs a median was computed from.
