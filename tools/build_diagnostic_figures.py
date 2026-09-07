"""Build diagnostic figures from receipted scalar outputs; no new experiments."""
import hashlib
import json
from pathlib import Path
from statistics import fmean
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper/figures'
OUT.mkdir(exist_ok=True)
inputs = {}
def read(path):
    path = Path(path)
    inputs[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())
def save(fig, name):
    fig.tight_layout()
    for suffix in ('pdf', 'svg', 'png'):
        fig.savefig(OUT / f'{name}.{suffix}', dpi=180, bbox_inches='tight')
    plt.close(fig)
plt.rcParams.update({'font.size': 9, 'pdf.fonttype': 42, 'ps.fonttype': 42,
                     'axes.spines.top': False, 'axes.spines.right': False})
v = read(ROOT/'receipts/analysis/lucid_return_inversion_20260901.json')['pairs']
fig, ax = plt.subplots(figsize=(3.4,2.4))
for collapsed, label, color in [(False,'Range-holding','#247b88'),(True,'Collapsed','#ba4a3d')]:
    rows=[r for r in v if r['evacuated']==collapsed]
    ax.scatter([r['terminal_return'] for r in rows],[100*r['frontier_success_auc'] for r in rows],label=label,color=color)
ax.set(xlabel='Terminal training return',ylabel='Frontier success AUC (%)', title='Return–robustness inversion: 12 runs')
ax.legend(frameon=False,fontsize=8)
save(fig,'return_inversion')
fig,ax=plt.subplots(figsize=(3.4,2.4))
for mode in ('fixed','lucid_ratchet_rg'):
    rows=[r for r in v if r['mode']==mode]
    if rows:
        rows.sort(key=lambda r:r['seed'])
        ax.plot([r['seed']-8600 for r in rows],[100*r['frontier_success_auc'] for r in rows],'o-',label='Never-shrink' if mode=='lucid_ratchet_rg' else 'Fixed')
ax.set(xlabel='Training seed offset (from 8600)',ylabel='Frontier success AUC (%)',xticks=[0,1,2])
ax.legend(frameon=False)
save(fig,'paired_seeds')
v=read(ROOT/'receipts/analysis/lucid_signal_audit_20260901.json')['fixed_difficulty_arms']
fig,ax=plt.subplots(figsize=(3.4,2.4))
for i,(key,name) in enumerate([('latent_gap_p90','Mismatch'),('time_out_rate','Survival'),('mean_return','Return')]):
    values=[s['spearman_vs_iteration'] for r in v for s in r['signals'] if s['signal']==key]
    ax.scatter([i]*len(values),values,color='#247b88')
    ax.plot([i-.2,i+.2],[fmean(values)]*2,color='#ba4a3d')
ax.axhline(0,color='gray',lw=.5);ax.set(xticks=[0,1,2],xticklabels=['Mismatch','Survival','Return'],ylabel='Rank correlation with iteration',ylim=(-1,1.05))
save(fig,'signal_audit')
p=Path('/home/linjiw/lucid-sonic/experiments/retention_screen_campaign_20260906_c/analysis')
receipt=read(p/'receipt.json')
assert receipt['complete']
for path,digest in receipt['input_hashes'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
v=read(p/'analysis.json')['rows']
origin=next(r for r in v if r['arm']=='origin' and r['preset']=='phys_000')['global_mpjpe_mm']
fig,axs=plt.subplots(1,2,figsize=(7,2.7))
for arm,color in [('R0','#ba4a3d'),('R1','#247b88'),('R2','#a47a28')]:
    rows=sorted([r for r in v if r['arm']==arm and r['preset']=='phys_000'],key=lambda r:r['iteration'])
    xs=[r['iteration'] for r in rows];ys=[100*(r['global_mpjpe_mm']/origin-1) for r in rows]
    axs[0].plot(xs,ys,'o-',color=color,label=arm)
    hard=[100*fmean(r['tracking_success_rate'] for r in v if r['arm']==arm and r['iteration']==step and r['preset'] in ('ch_push_350','ch_push_fric_350_150')) for step in xs]
    axs[1].plot(ys,hard,'o-',color=color,label=arm)
    axs[1].annotate(arm,(ys[-1],hard[-1]),xytext=(4,3),textcoords='offset points')
base=100*fmean(r['tracking_success_rate'] for r in v if r['arm']=='origin' and r['preset'] in ('ch_push_350','ch_push_fric_350_150'))
axs[1].scatter([0],[base],marker='*',s=70,color='black',label='Origin')
axs[0].axhline(10,color='gray',ls='--');axs[1].axvline(10,color='gray',ls='--')
axs[0].set(xlabel='Continuation iteration',ylabel='Nominal global error increase (%)')
axs[1].set(xlabel='Nominal global error increase (%)',ylabel='Hard tracking qualification (%)')
axs[0].legend(frameon=False)
save(fig,'retention_trajectory')
base=Path('/home/linjiw/lucid-sonic/artifacts/mujoco_sweep_nopush_20260902/runs')
fig,ax=plt.subplots(figsize=(3.4,2.4))
for arm,label in [('off_s8600','No DR'),('lucid_collapsed_s8601','Collapsed'),('ratchet_s8601','Never-shrink'),('fixed_s8601','Fixed (paired)')]:
    rates=[]
    for lam in ('1','1.5','2'):
        paths=sorted((base/arm/f'lam{lam}').glob('seed*.json'))
        assert len(paths)==32,(arm,lam,len(paths))
        results=[read(path)['result'] for path in paths]
        rates.append(100*fmean(not r['fell'] for r in results))
    ax.plot([1,1.5,2],rates,'o-',label=label)
    print('MuJoCo physics-only',arm,rates)
ax.set(xlabel='Physics scale (no pushes)',ylabel='Survival (%)',xticks=[1,1.5,2])
ax.legend(frameon=False,fontsize=7)
save(fig,'mujoco_ladder')
provenance=Path('/home/linjiw/lucid-sonic/outputs/diagnostic_figure_provenance.json')
provenance.write_text(json.dumps({'inputs':inputs,'scope':'development; no second-seed results'},indent=2)+'\n')
print('Wrote',OUT)
