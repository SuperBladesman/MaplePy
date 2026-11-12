---
title: 'MaplePy and Hopper: Madelung energies from crystal structures, and Hoppe''s additivity theorem tested at database scale'
tags:
  - Python
  - crystallography
  - Madelung energy
  - MAPLE
  - crystal structure validation
  - ICSD
authors:
  - name: Nik Reeves-McLaren
    orcid: 0000-0002-1061-1230
    corresponding: true
    affiliation: 1
  - name: Peter Gross
    affiliation: 1
affiliations:
  - name: School of Chemical, Materials and Biological Engineering, University of Sheffield, United Kingdom
    index: 1
    ror: 05krs5044
date: (set on submission)
bibliography: paper.bib
---

<!-- Before submission: Peter's ORCID; the date; the Zenodo DOI of the
release in the Research impact statement; the AI model versions (marked). -->

# Summary

The lattice energy of an ionic crystal is dominated by its electrostatic, or Madelung, part. Hoppe called this the Madelung Part of Lattice Energy (MAPLE), split it into contributions from each crystallographic site, and showed that the MAPLE of a ternary oxide should equal the weighted sum of the MAPLE values of its binary oxides, usually to within 1% [@Hoppe1966; @Hoppe1970; @Hoppe1995]. A residual above 1% says that something about the structure, or its description, departs from the ionic picture.

`MaplePy` computes per-site and total MAPLE from crystallographic information files (CIFs) with the Ewald summation in `pymatgen` [@Ewald1921; @Ong2013]. `Hopper` decomposes each ternary oxide into binary oxides, computes the additivity residual against a 112-entry reference table, and assigns every structure one of twelve codes in three tiers, so that a residual is interpreted rather than merely reported. Both run as Jupyter notebooks, or as the Python package `maplepy`, with the command lines `maplepy` and `hopper`.

# Statement of need

Crystal structure databases such as the Inorganic Crystal Structure Database (ICSD) [@Zagorac2019] are the starting point for much of materials science, and increasingly the training data for machine learning, which inherits whatever errors they hold [@ReevesMcLaren2026Integrity]. Local checks, such as bond valence sums [@Brown2009], have been automated at database scale [@ReevesMcLaren2026Dalton]. Hoppe's global electrostatic check has remained a manual exercise, applied one structure or one family at a time.

The obstacle is not the arithmetic: an Ewald sum takes a second. It is what must be decided before the sum can be taken. Every ion needs a charge, and CIFs often carry none, or inconsistent ones. Disordered sites need a charge that no single ion has; the number of formula units per cell must be derived, not trusted; and some deposited coordinates cannot carry a Madelung energy at all. A tool that makes these decisions silently reports a plausible number.

`MaplePy` and `Hopper` are for curators and crystallographers checking sets of structures, for those assembling training sets, and for solid-state chemists applying Hoppe's diagnostics to their own refinements.

# State of the field

Hoppe's laboratory computed MAPLE with its own program [@Hubenthal1993]. General Ewald implementations exist, among them `pymatgen`'s `EwaldSummation` [@Ong2013], and lattice-energy codes such as `GULP` [@Gale1997] include the electrostatic term within full force-field models. None assigns oxidation states with a record of where each came from, derives *Z* from the crystallography, says when a structure cannot carry a Madelung energy, or tests additivity across a database.

We built on `pymatgen` rather than reimplementing the Ewald sum, and added the decision layer and the classification as a separate tool, because its defaults are the opposite of a general-purpose library's: it refuses to guess an oxidation state where the chemistry is ambiguous, or to take *Z* from the reduced composition, which gives *Z* = 1 for a non-stoichiometric refinement.

# Software design

`MaplePy` fails loudly. Oxidation states come from a fixed chain (the user's, the CIF's per-site states, the CIF's element-level states, a formula override, a single common state), and where none settles the question the calculation stops and names the elements. The source used is printed for every structure. *Z* is the greatest common divisor of the number of sites holding each element. Shared or partly occupied sites carry an occupancy-weighted mean charge, and the structure is flagged with the kind of disorder and the sublattice it is on.

`MaplePy` reports what it finds and leaves the structure as deposited. It flags two sites closer than 0.5 Å as a split site, and a contact below 1.6 Å as unphysical; the first threshold lies in an empty band of the measured distribution, and the second is a judgement, documented as one. Earlier versions corrected an origin-choice artefact in space group *Pnma* by keeping whichever of two candidate structures had the lower Ewald energy, the quantity under test. It changed 44 of 938 perovskites and turned no failing geometry into a sound one, so version 1.3.6 removed it; the record of that decision stays in the notebook, where the function was.

`Hopper` assigns its codes in a fixed order, built on one rule: a caveat must not mask a defect (\autoref{fig:order}). A structure with impossible coordinates is reported as such even when its residual is small; a disordered structure that agrees with its binaries is additive. Twenty-three reference values are estimates with no source, kept so that published results can be reproduced, and every decomposition that uses one says so.

![What `MaplePy` decides before the Ewald sum, and the order in which `Hopper` assigns its codes; the first code that applies is the one reported.\label{fig:order}](order.png){ width=85% }

The notebooks are the source of the code, because they are where a reader follows how a number was reached. The package is built from their cells, every edit listed; continuous integration fails if the two drift apart, and a script compares their outputs on any folder of CIFs. The tests assert three known answers independently of the notebooks (NaCl's Madelung factor, 1.7476; rutile and anatase against Hoppe's values; BaTiO~3~ additive to within 1%) and test each decision on constructed structures; no ICSD file is distributed or used.

# Research impact statement

`MaplePy` and `Hopper` underpin the first database-scale test of Hoppe's additivity theorem, on 1,410 perovskite and pyrochlore structures from the ICSD, now under review [@Gross2026Maple]. The release described here reproduces that study's classification of every structure from its `MaplePy` results, and is archived on Zenodo. The binary oxide reference table, with entry counts and ranges for every value derived from the ICSD, is released under CC-BY 4.0 for use with other calculators. Because the residual and the Madelung factor need only a structure and its charges, they can also screen structures proposed by calculation or generative models.

# AI usage disclosure

`MaplePy` and `Hopper` were developed with one generative AI tool, Claude (Anthropic), using Claude Opus 4.6 and later Opus models <!-- confirm the model versions -->, from the first version of each notebook (March and April 2026) to the release described here. N.R.-M. framed each problem and made the design decisions described above (failing loudly on oxidation states, deriving *Z* from the site counts, reporting rather than repairing geometry and removing the origin correction, the order of the codes, flagging the estimates, the notebooks as the source); Claude wrote the code, tests and documentation to that specification. Every change was audited, and correctness was checked independently of the code: against Hoppe's published values, by manual review of the structures flagged in the study, and by comparing each version's results with the last. This paper was drafted with Claude Opus 5.5 and revised by the authors. The authors have reviewed, modified and validated all AI-generated content.

# Acknowledgements

This work received no specific funding.

# References
