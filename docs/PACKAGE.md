# How the package relates to the notebooks

`MaplePy.ipynb` and `Hopper.ipynb` are the source of the code. They are what a reader opens to see how a number was reached, cell by cell, and what most users of MaplePy have run. The package, maplepy, runs the same code at scale, from a command line or from Python, and is what the tests exercise.

## The build

`tools/build_engine.py` copies the code cells of each notebook into `src/maplepy/_cells/maplepy/` and `src/maplepy/_cells/hopper/`, one file per cell. Each file starts with a header naming the notebook and cell it came from. A plan in the script lists every cell: the ones copied, the role each plays, and the ones left out, each with its reason. It also lists every edit the build makes, and each edit must match the notebook exactly once, so a change to an edited line stops the build rather than going unnoticed. There are four edits, in three cells:

| Notebook | Cell | Edit |
|---|---|---|
| MaplePy | 4 | `DEFAULT_DATA_DIR` is the package's data folder, not `data/` in the working directory |
| Hopper | 4 | the folder is passed in (`MAPLE_DIR_OVERRIDE`), so no dialog opens; and `tkinter` is not imported (two edits) |
| Hopper | 6 | the reference table is the package's copy (`BINARY_REFERENCE_PATH`) |

One more change touches no line: Hopper's cells that act on a run (Section 3 onwards) are split where the action starts, so that their definitions load with the engine and their actions run when asked for.

Left out: the commented pip installs; MaplePy's version print (cell 3), its demonstration on NaCl (cell 20), its application to the alkaline earth oxides (Section 6), and its GUI (Section 7), a Tk folder picker in front of `batch_maple()`, which the package calls directly.

`python tools/build_engine.py --check` fails if the copied cells or `src/maplepy/_manifest.py` differ from what the notebooks would produce. CI runs it on every push, and `tests/test_build.py` runs it too.

## The engines

`maplepy._maple` and `maplepy._hopper` are modules whose namespaces play the part of a notebook kernel: the copied cells are executed in them, in notebook order, so every function a notebook defines is an attribute of its engine, with the notebook's behaviour. `maplepy.engine()` and `maplepy.hopper_engine()` return them. Three things differ from a notebook session, and only three:

- what the cells print while loading goes to the engine's `IMPORT_LOG`, because MaplePy's worker processes import the engine;
- the actions run when asked for, and each Hopper run starts from the state the engine had on loading, as "Restart & Run All" would;
- `display()`, which Jupyter provides, prints a table as text.

Hopper loads on first use, because its set-up cell changes matplotlib's `rcParams`, as it does in Jupyter.

MaplePy's validation cells (Section 2) are not run on loading. `maplepy.validate()` and `maplepy --validate` run them, in notebook order, and read the pass flags each sets.

## Showing they agree

`python tools/equivalence.py FOLDER` runs both notebooks headless on a copy of a folder of CIFs, with the folders set so that no dialog opens, runs the package on another copy, and compares `maple_results.csv`, `maple_summary.csv`, `maple_failed.csv` and `additivity_classified.csv` cell by cell. Run it after any change, on a folder whose results you know. On the examples, every file is identical.

## Changing the code

Edit the notebook, never the copied cells, then `python tools/build_engine.py`. [CONTRIBUTING.md](../CONTRIBUTING.md) gives the whole sequence.
