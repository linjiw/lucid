"""Two-seed replication figure for the project page. Reads completed campaign receipts only."""
import json, hashlib
from pathlib import Path
from statistics import fmean
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('/home/linjiw/lucid/site/img/recovery')
S8600 = Path('/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_c/analysis')
S8601 = Path('/home/linjiw/lucid-sonic/experiments/retention_second_seed_20260907_c')

# --- seed 8600 from the completed campaign analysis
import csv
rows0 = list(csv.DictReader(open(S8600 / 'all_cells.csv')))
def g0(arm, it, preset, col):
    for r in rows0:
        if r['arm'] == arm and r['preset'] == preset and int(float(r['iteration'])) == it:
            return float(r[col])
    raise KeyError((arm, it, preset))

# --- seed 8601 from the completed replication analysis
rep = json.loads((S8601 / 'analysis.json').read_text())
assert rep['plan_sha256'] == '57fbff80fbcd47f740f0e7bff9f7f84e7bef7892a92b50fd61396cb4ce7827cd'
rows1 = rep['rows']
def g1(arm, it, preset, col):
    for r in rows1:
        if r['arm'] == arm and r['preset'] == preset and int(r['iteration']) == it:
            return r[col]
    raise KeyError((arm, it, preset))

o0 = g0('origin', 0, 'phys_000', 'global_mpjpe_mm')
o1 = g1('origin', 0, 'phys_000', 'global_mpjpe_mm')
assert abs(o0 - o1) < 1e-6, (o0, o1)   # same frozen origin, must reproduce
CKPTS = [250, 500, 1000, 1500, 2000]

fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.3))
for ax, (label, gf, tag) in zip(axs, [('Seed 8600', g0, 'first'), ('Seed 8601', g1, 'second')]):
    for arm, colour, mk, ls in [('R0', '#ba4a3d', 's', '--'), ('R1', '#247b88', 'o', '-')]:
        col_g = 'global_mpjpe_mm'
        ys = [100 * (gf(arm, it, 'phys_000', col_g) / o0 - 1) for it in CKPTS]
        ax.plot(CKPTS, ys, marker=mk, ls=ls, color=colour, label=arm)
        print(label, arm, [round(y, 2) for y in ys])
    ax.axhline(10, color='gray', ls=':')
    ax.axhline(0, color='#bbbbbb', lw=.6)
    ax.annotate('10% retention budget', (250, 10), xytext=(2, 4),
                textcoords='offset points', fontsize=8, color='gray')
    ax.set_title(f'{label} continuation', fontsize=11)
    ax.set_xlabel('Continuation iteration')
    ax.set_ylim(-6, 82)
    ax.set_xticks(CKPTS)
axs[0].set_ylabel('Nominal global error increase (%)')
axs[0].legend(frameon=False)
fig.tight_layout()
for ext in ('svg', 'png', 'pdf'):
    fig.savefig(OUT / f'two_seed.{ext}', bbox_inches='tight', dpi=200)
print('Wrote', OUT / 'two_seed.svg')
