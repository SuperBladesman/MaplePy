# Contributing to MaplePy

MaplePy and Hopper are maintained by Nik Reeves-McLaren at the University of Sheffield, alongside research and teaching. Issues and pull requests are read and answered as time allows; there is no guaranteed response time.

## Reporting a structure MaplePy or Hopper gets wrong

A structure that comes out wrong is the most useful report there is; most of the changelog began as one. Please open an issue with:

- the versions: `maplepy --version` names the package and both engines; from the notebooks, `MAPLEPY_VERSION` and `HOPPER_VERSION`;
- your Python and pandas versions (`python -c "import sys, pandas; print(sys.version, pandas.__version__)"`);
- the structure. For an ICSD entry, give its collection code rather than attaching the CIF: ICSD files are licensed by FIZ Karlsruhe and should not be posted publicly. For your own refinement, attach the CIF if you are free to share it, with the oxidation states you used (`--ox`);
- what MaplePy or Hopper reported (the MAPLE, the flags, the code, or the error) and what you expected, and why.

Questions about what a code means are welcome as issues too; the README's table of codes answers most of them.

## Changing the code

`MaplePy.ipynb` and `Hopper.ipynb` are the source of the code. The package's cells in `src/maplepy/_cells/` are copied from them by `tools/build_engine.py`, and CI fails if the two differ, so edit the notebooks, never the copied cells. [docs/PACKAGE.md](docs/PACKAGE.md) explains how they relate.

1. Edit the notebook and raise its version (`MAPLEPY_VERSION` or `HOPPER_VERSION`). Record the change where it is made, as the code already does (`# v1.3.7: ...`): what was wrong, what you measured, what changed. Add a test in `tests/` that fails before your change and passes after it.
2. For MaplePy, run Section 2 in the notebook: all three validations must pass.
3. Copy the cells into the package: `python tools/build_engine.py`.
4. Install and test under pandas 2 and pandas 3: `pip install -e ".[test]"`, then `maplepy --validate` and `python -m pytest`.
5. Show that the notebooks and the package still agree on a folder of CIFs you know: `python tools/equivalence.py FOLDER`.
6. Describe the change in `CHANGELOG.md`, under the new version: what was wrong, what changed, and what it does to results.

A change to a reference value needs a source, named in [data/README.md](data/README.md), and the tests check that Hopper's inline table and the JSON still agree.

Never commit files that cannot be redistributed: ICSD CIFs, or results tables made from them. `.gitignore` refuses CIFs outside `examples/`, and the tests use constructed structures for this reason.

## Releases

Each release is tagged (`v1.4.0`) and published as a GitHub release, which Zenodo archives with its own DOI. Before tagging, date the changelog entries, update `version` and `date-released` in `CITATION.cff` and `version` in `.zenodo.json`; after Zenodo has archived the release, add its DOI to `CITATION.cff` and the README. `tests/test_release.py` checks that they agree.

## Licence

By contributing you agree that your contribution is released under the [MIT licence](LICENSE), or for the data tables in `data/`, under CC-BY 4.0.
