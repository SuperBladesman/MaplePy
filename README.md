# MaplePy

**Automated MAPLE (Madelung Part of Lattice Energy) calculation from crystallographic information files.**

MaplePy computes per-site and total MAPLE values from CIF files using the Ewald summation, enabling database-scale validation of Hoppe's additivity theorem for ternary oxides.

## What is MAPLE?

MAPLE (Madelung Part of Lattice Energy) is the electrostatic contribution to the lattice energy of an ionic crystal, computed from the Ewald sum over the full three-dimensional charge distribution. Unlike bond valence sum (BVS) analysis, which assesses local bonding geometry, MAPLE captures the long-range electrostatic environment of every ion in the structure. Hoppe's additivity theorem predicts that the MAPLE of a ternary oxide should equal the weighted sum of its binary oxide components to within approximately ±1%.

## Features

- **Automated MAPLE calculation** from CIF files via pymatgen's Ewald summation
- **Per-site MAPLE contributions** including partial Madelung constants and reduced MAPLE
- **Robust oxidation state assignment** with a five-level priority chain that fails loudly rather than silently
- **Mean-field charge approximation** for disordered (mixed-occupancy) sites
- **Origin-choice correction** for space group 62 (*Pnma*) O2 sublattice artefacts
- **Batch processing** of entire directories of CIF files
- **Binary oxide reference table** (112 entries) for additivity analysis
- **Validation benchmarks**: NaCl, TiO₂ polymorphs, BaTiO₃

## Installation

```bash
pip install pymatgen numpy pandas matplotlib
```

Clone this repository:

```bash
git clone https://github.com/SuperBladesman/MaplePy.git
cd MaplePy
```

## Quick Start

### Single structure
```python
from maplepy import load_structure, compute_maple

structure = load_structure("path/to/your/file.cif")
result = compute_maple(structure, verbose=True)
```

### Batch processing
```python
from maplepy import batch_maple

batch_maple("path/to/cif/directory/", output_dir="results/")
```

### Additivity analysis

The additivity analysis notebook (`hopper.ipynb`) consumes MaplePy's CSV outputs and applies the seven-category failure classification described in the associated publication. See the notebook for full documentation.

## Binary Oxide Reference Table

The file `binary_oxide_maple_reference.json` contains 112 reference MAPLE values for binary oxides, calibrated from ICSD median values where available. Each entry includes:

- MAPLE value (kcal/mol per formula unit)
- Structure type and space group
- Source classification (ICSD median / validation / estimated)
- Number of qualifying ICSD entries and range
- Confidence rating (high / medium / low)

See the JSON file's `_metadata` and `_field_descriptions` sections for full documentation.

## Output Files

MaplePy generates timestamped output directories containing:

| File | Contents |
|------|----------|
| `maple_results.csv` | Per-site MAPLE, partial Madelung constants, reduced MAPLE, coordinates |
| `maple_summary.csv` | Per-structure totals, Madelung factors, reference bond lengths |
| `maple_failed.csv` | Structures that could not be processed, with error messages |

## Failure Classification

The additivity analysis applies a seven-category classification to distinguish genuine structural violations from artefacts:

| Type | Label | Description |
|------|-------|-------------|
| 1.1 | Missing binary reference | Binary oxide absent from reference table |
| 2.1 | Oxidation state error | Incorrect charge assignment |
| 2.2 | *Z* = 1 artefact | Compositional reduction inflates MAPLE |
| 2.3 | Disorder / mean-field | Mixed-occupancy site approximation |
| 2.4 | Oxygen non-stoichiometry | Oxygen count mismatch in decomposition |
| 2.5 | Coordinate error | Unphysical interatomic distances from wrong coordinates |
| 3.1 | Genuine violation | Real deviation from ionic additivity |

## Citation

If you use MaplePy in your research, please cite:

> P. Gross, N. Reeves-McLaren, "Database-Scale Validation of Hoppe's MAPLE Additivity Theorem for Perovskite and Pyrochlore Oxides", (in press)

## Acknowledgements

MaplePy was developed with LLM-assisted coding (Claude, Anthropic; Opus 4.6) for data processing. All scientific interpretation and validation was performed by the authors.

## Licence

Code: MIT License (see `LICENSE`)
Binary oxide reference table: CC-BY-4.0
