"""The evidence for Hopper's Type 2.1: does a different assignment of oxidation
states make a structure additive?

For each structure that a first Hopper run leaves neither additive nor a
structural defect (2.5, 2.7), every charge-balanced combination of the common
oxidation states of its cations (data/common_oxidation_states.json) is tried.
MaplePy recomputes the ternary MAPLE with those states, as level (1) of its
oxidation-state chain, and the binary sum is taken from the released reference
table. The best combination, and every one tried, are written to
alternative_assignments.csv in the run folder. Hopper reads that file on its
next run and assigns 2.1 where the best combination differs from the deposited
states and gives a residual below 1%, unless the chemistry contradicts it
(ASSIGNMENT_CHEMISTRY_REJECTED in the classification cell).

    hopper RUN                                         # first pass
    python tools/alternative_assignments.py RUN CIFS   # the evidence
    hopper RUN                                         # second pass: 2.1

RUN is a MaplePy run folder holding additivity_classified.csv from the first
pass; CIFS is the folder of CIF files MaplePy was run on. This is the
procedure of the J. Appl. Cryst. study (ui5052, revision 1), which used
MaplePy 1.3.6 and reference table 1.3.0.
"""
import argparse
import contextlib
import io
import itertools
import json
import os
import sys
from pathlib import Path

import pandas as pd

import maplepy

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {1: ('{}2O', 2), 2: ('{}O', 1), 3: ('{}2O3', 2), 4: ('{}O2', 1),
            5: ('{}2O5', 2), 6: ('{}O3', 1), 7: ('{}2O7', 2)}


def _load(data_dir):
    ref = {e['formula']: e['maple_kcal_mol'] for e in json.load(open(
        data_dir / 'binary_oxide_maple_reference.json', encoding='utf-8'))['entries']}
    common = {k: v for k, v in json.load(open(
        data_dir / 'common_oxidation_states.json', encoding='utf-8')).items()
        if not k.startswith('_')}
    return ref, common


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def binary_sum(comp, states, ref):
    """Sum of binary MAPLE for one assignment, or (None, the missing binary)."""
    total = 0.0
    for el, n in comp.items():
        if el == 'O':
            continue
        formula, n_cat = PATTERNS[states[el]]
        formula = formula.format(el)
        if formula not in ref:
            return None, formula
        total += n / n_cat * ref[formula]
    return total, None


def test_structure(cif, ref, common):
    """Every charge-balanced assignment of common states, with its residual."""
    r0 = _quiet(maplepy.compute, cif)
    st = r0.result['structure']
    comp = {str(k): v for k, v in
            st.composition.reduced_composition.get_el_amt_dict().items()}
    n_o = comp.get('O', 0)
    cations = [e for e in comp if e != 'O']
    deposited = {}
    for site in st:
        for sp in site.species:
            if sp.symbol != 'O':
                deposited.setdefault(sp.symbol, set()).add(
                    int(round(getattr(sp, 'oxi_state', 0) or 0)))
    alts = []
    for combo in itertools.product(*[common.get(e, []) for e in cations]):
        states = dict(zip(cations, combo))
        if abs(sum(comp[e] * states[e] for e in cations) - 2 * n_o) > 1e-3:
            continue
        bsum, missing = binary_sum(comp, states, ref)
        if bsum is None:
            alts.append(dict(states=states, missing=missing))
            continue
        r = _quiet(maplepy.compute, cif, oxidation_states={**states, 'O': -2})
        alts.append(dict(states=states, maple=round(r.total_maple, 1),
                         binsum=round(bsum, 1),
                         delta=round(abs(r.total_maple - bsum) / r.total_maple * 100, 3)))
    return dict(deposited={k: sorted(v) for k, v in deposited.items()}, alts=alts)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('run', type=Path, help='MaplePy run folder after a first Hopper pass')
    ap.add_argument('cifs', type=Path, help='folder of the CIF files MaplePy was run on')
    ap.add_argument('--data', type=Path, default=ROOT / 'data',
                    help='folder holding the reference tables (default: data/)')
    a = ap.parse_args(argv)
    ref, common = _load(a.data)
    classified = pd.read_csv(a.run / 'additivity_classified.csv')
    todo = classified[~classified['classification'].astype(str).isin(
        ['Additive', '2.5', '2.7'])]
    rows = []
    for _, r in todo.iterrows():
        cif = a.cifs / os.path.basename(str(r['source_cif']))
        try:
            t = test_structure(cif, ref, common)
        except Exception as e:          # recorded, not fatal: one bad CIF
            rows.append(dict(source_cif=r['source_cif'], err=repr(e)[:120]))
            continue
        scored = [x for x in t['alts'] if 'delta' in x]
        best = min(scored, key=lambda x: x['delta'], default=None)
        rows.append(dict(
            source_cif=r['source_cif'], compound=r.get('compound'),
            icsd_code=r.get('icsd_code'), cls=r['classification'],
            delta=r.get('delta_pct'), deposited=json.dumps(t['deposited']),
            best_states=json.dumps(best['states']) if best else '',
            best_delta=best['delta'] if best else None,
            n_alts=len(t['alts']), alts=json.dumps(t['alts'])))
    out = a.run / 'alternative_assignments.csv'
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f'{len(rows)} structures tested; written to {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
