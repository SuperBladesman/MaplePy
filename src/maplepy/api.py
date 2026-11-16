"""The Python interface to the two engines.

Everything here calls the notebooks' own functions: load_structure(),
compute_maple() and batch_maple() from MaplePy, and Hopper's pipeline from
loading a run to the export. Nothing is recomputed differently.
"""

from dataclasses import dataclass, field
from pathlib import Path

__all__ = ['MapleResult', 'compute', 'run_folder', 'additivity', 'validate',
           'engine', 'hopper_engine']


def engine():
    """The MaplePy engine module: every function MaplePy.ipynb defines."""
    from . import _maple
    return _maple


def hopper_engine():
    """The Hopper engine module: every function Hopper.ipynb defines."""
    from . import _hopper
    return _hopper


@dataclass
class MapleResult:
    """One structure through load_structure() and compute_maple().

    `result` is compute_maple()'s dictionary, `sites` the per-site table of
    results_to_dataframe(), and `log` what MaplePy printed, which includes
    where the oxidation states came from: the only record of that anywhere.
    """
    source: str
    result: dict
    sites: object
    log: str = ''
    total_maple: float = field(init=False)
    madelung_factor: float = field(init=False)
    Z: int = field(init=False)
    d_ref: float = field(init=False)
    disordered: bool = field(init=False)
    geometry_flag: str = field(init=False)
    geometry_status: str = field(init=False)

    def __post_init__(self):
        r = self.result
        self.total_maple = float(r['total_maple_kcal'])
        self.madelung_factor = (None if r['madelung_factor'] is None
                                else float(r['madelung_factor']))
        self.Z = int(r['Z'])
        self.d_ref = float(r['d_ref'])
        self.disordered = bool(r['disordered'])
        self.geometry_flag = r['geometry_flag']
        self.geometry_status = r['geometry_status']

    def summary(self):
        s = self.result['structure']
        mf = ('n/a' if self.madelung_factor is None
              else f'{self.madelung_factor:.4f}')
        lines = [
            f'{Path(self.source).name}  ·  {s.composition.reduced_formula}  '
            f'·  {s.get_space_group_info()[0]}',
            '',
            f'  MAPLE            {self.total_maple:.2f} kcal/mol per formula '
            f'unit  ({self.total_maple * 4.184:.1f} kJ/mol)',
            f'  Madelung factor  {mf}',
            f'  Z, d_ref         {self.Z}, {self.d_ref:.4f} Å',
            f'  Geometry         {self.geometry_status}',
            f'  Disorder         {self.result["disorder_status"]}'
            + ('' if self.result['partial_sublattice'] in ('none', None)
               else f' ({self.result["partial_sublattice"]} sublattice; '
                    f'mean-field charges)'),
        ]
        prov = [l.strip() for l in self.log.splitlines()
                if l.strip().startswith(('Oxidation states', 'WARNING'))]
        lines += [f'  {p}' for p in prov]
        return '\n'.join(lines)


def compute(cif, oxidation_states=None):
    """MAPLE for one CIF: MaplePy's load_structure() then compute_maple().

    oxidation_states, e.g. {'Ba': 2, 'Ti': 4, 'O': -2}, is level 1 of the
    oxidation-state chain; without it the CIF's own states are used, then the
    bundled tables, and a ValueError names the elements that need one.
    """
    import contextlib
    import io
    m = engine()
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        s = m.load_structure(str(cif), oxidation_states=oxidation_states)
        r = m.compute_maple(s, verbose=False)
        df = m.results_to_dataframe(r)
    return MapleResult(str(cif), r, df, log.getvalue())


def run_folder(folder, output_dir=None, oxidation_states=None, workers=None,
               plots=False, verbose=False):
    """Every CIF in a folder through MaplePy's batch_maple(), as the
    notebook's batch section and GUI do. Writes maple_results.csv,
    maple_summary.csv and maple_failed.csv to output_dir, or to a
    timestamped outputs_ folder inside `folder`, and returns that folder.

    oxidation_states applies one assignment to every CIF in the folder, as
    the GUI's OXIDATION_STATES does. plots draws Section 8's three
    diagnostic plots into the same folder.
    """
    m = engine()
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f'not a folder: {folder}')
    oxi = ({p.stem: oxidation_states for p in folder.glob('*.cif')}
           if oxidation_states else None)
    m.LAST_OUTPUT_DIR = None          # so a folder with no CIFs cannot
    #                                   return the previous run's folder
    m.batch_maple(folder, output_dir=output_dir, oxidation_states_map=oxi,
                  verbose=verbose, workers=workers)
    out = m.LAST_OUTPUT_DIR
    if out is None:
        raise FileNotFoundError(f'no CIF files in {folder}')
    if plots:
        import matplotlib
        matplotlib.use('Agg', force=False)
        m.run_plots()
    return Path(out)


def additivity(results, figures=False):
    """Hopper on a MaplePy run: decomposition into binary oxides, the
    additivity residual, the classification, and the export.

    `results` is a folder holding maple_summary.csv and maple_results.csv,
    or a folder of CIFs with outputs_* runs inside, in which case the latest
    is used, as in the notebook. Writes additivity_classified.csv (and the
    perovskite and pyrochlore subsets, and the reference table) into the run
    folder and returns the classified table. figures draws the paper figures
    as well; any that cannot be drawn from this data are reported.
    """
    h = hopper_engine()
    skipped = h.run_pipeline(results, figures=figures)
    df = h.df_classified.copy()
    df.attrs['run_folder'] = str(h.MAPLE_DIR)
    df.attrs['figures_skipped'] = skipped
    return df


def validate():
    """MaplePy's three known answers, as Section 2 of the notebook runs them:
    NaCl (partial Madelung constants 0.8738, Madelung factor 1.7476; Hoppe,
    1966), rutile and anatase TiO2 against Hoppe (1995), Table 5, and BaTiO3
    additivity to within 1% (Hoppe, 1995, p. 560). Returns the pass flags;
    raises AssertionError naming any that failed."""
    flags = engine().run_checks()
    failed = [k for k, v in flags.items() if not v]
    if failed:
        raise AssertionError('MaplePy validation failed: ' + ', '.join(failed))
    return flags
