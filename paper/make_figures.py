"""Build the figure of the JOSS paper.

    python paper/make_figures.py

Draws order.png: what MaplePy decides before the Ewald sum,
and the order in which Hopper assigns its codes. Every box in a column has
the same width and every label the same offset, so nothing depends on a
layout engine. Needs matplotlib only.
"""
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt                       # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
INK, MUTED = '#17212b', '#4a5866'
STEP = ('#ffffff', '#17212b')
OUT = {  # fill, border
    'none': ('#eaedf0', '#586776'),
    'defect': ('#f9e0de', '#b0271f'),
    'additive': ('#dcefe0', '#2c6b3f'),
    'caveat': ('#fcebd0', '#9a5800'),
    'violation': ('#e3e0f5', '#3b2c8f'),
}

# main column: (title, description lines, outcome key or None, outcome lines)
STEPS = [
    ('CIF', [], None, None),
    ('MaplePy', ['Oxidation states: given, then the CIF\'s own, then the',
                 'bundled tables; if none settles it, stop and name them.',
                 'Z from the site counts. Mean-field charge on shared sites.',
                 'Shortest contact measured; nothing edited.'], None, None),
    ('Ewald sum (pymatgen)', ['MAPLE per site and per formula unit,',
                              'Madelung factor, d_ref, d_min, flags.'], None, None),
    ('Hopper: decomposition', ['Binary oxides from the per-site states;',
                               'oxygen balance; Δ against the table.'],
     'none', ['Tier 1: no residual', '1.1 table lacks the binary',
              '1.3 no binary oxide exists', '1.4 charge is not a state']),
    ('Defect?', ['Coordinates no ionic solid could have,',
                 'whatever the residual.'],
     'defect', ['2.7 split site, d_min < 0.5 Å',
                '2.5 coordinate error, d_min < 1.6 Å', '     or O-site CV > 0.05']),
    ('Δ < 1%?', ['Hoppe\'s criterion.'], 'additive', ['Additive']),
    ('Caveat?', ['Something bears on the residual.'],
     'caveat', ['2.1 Δ > 10%, ordered: a state is wrong',
                '2.6 anion vacancies', '2.3 cation disorder',
                '2.4 oxygen does not balance']),
    ('Nothing above', [], 'violation', ['3.1 genuine violation']),
]

W_MAIN, X_MAIN = 5.2, 0.4
W_OUT, X_OUT = 3.9, 6.6
LINE_H, PAD, GAP = 0.27, 0.22, 0.32


def box_height(lines, title=True):
    return PAD * 2 + LINE_H * (len(lines) + (1 if title else 0))


def draw():
    heights = []
    for title, desc, key, out in STEPS:
        h = box_height(desc)
        if out:
            h = max(h, box_height(out, title=False))
        heights.append(h)
    total = sum(heights) + GAP * (len(STEPS) - 1)
    fig = plt.figure(figsize=(10.8, total * 0.98 + 0.3))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10.8)
    ax.set_ylim(-total - 0.15, 0.15)
    ax.axis('off')
    y = 0
    prev_bottom = None
    for (title, desc, key, out), h in zip(STEPS, heights):
        hm = box_height(desc)
        top = y - (h - hm) / 2
        ax.add_patch(FancyBboxPatch((X_MAIN, top - hm), W_MAIN, hm,
                                    boxstyle='round,pad=0,rounding_size=0.08',
                                    fc=STEP[0], ec=STEP[1], lw=1.1))
        ax.text(X_MAIN + 0.18, top - PAD - LINE_H / 2, title, color=INK,
                fontsize=10.5, fontweight='bold', va='center')
        for i, line in enumerate(desc):
            ax.text(X_MAIN + 0.18, top - PAD - LINE_H * (i + 1.5), line,
                    color=MUTED, fontsize=9, va='center')
        if prev_bottom is not None:
            ax.add_patch(FancyArrowPatch((X_MAIN + W_MAIN / 2, prev_bottom),
                                         (X_MAIN + W_MAIN / 2, top),
                                         arrowstyle='-|>', mutation_scale=11,
                                         color=INK, lw=1.0))
        prev_bottom = top - hm
        if out:
            fc, ec = OUT[key]
            ho = box_height(out, title=False)
            to = y - (h - ho) / 2
            ax.add_patch(FancyBboxPatch((X_OUT, to - ho), W_OUT, ho,
                                        boxstyle='round,pad=0,rounding_size=0.08',
                                        fc=fc, ec=ec, lw=1.1))
            for i, line in enumerate(out):
                ax.text(X_OUT + 0.18, to - PAD - LINE_H * (i + 0.5), line,
                        color=INK, fontsize=9,
                        fontweight='bold' if i == 0 and key == 'none' else None,
                        va='center')
            ax.add_patch(FancyArrowPatch((X_MAIN + W_MAIN, top - hm / 2),
                                         (X_OUT, to - ho / 2),
                                         arrowstyle='-|>', mutation_scale=11,
                                         color=ec, lw=1.0))
        y -= h + GAP
    fig.savefig(HERE / 'order.png', dpi=200)
    print('wrote order.png')


if __name__ == '__main__':
    draw()
