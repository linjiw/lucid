"""Read-only replication watcher; summarize complete receipts without new GPU work."""
import hashlib
import json
from pathlib import Path
from statistics import fmean
import time
from datetime import datetime, timezone

ROOT=Path('/home/linjiw/lucid-sonic/experiments/retention_second_seed_20260907_b')
PLAN_SHA='f2ca969140d232579c70c8127df2c6ee775cf00917f3667ce976d9a17afd3f86'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def summarize():
    path=ROOT/'pilot/plan.json'
    if digest(path)!=PLAN_SHA:raise ValueError('Frozen plan changed')
    plan=json.loads(path.read_text())
    receipt=json.loads((ROOT/'pilot/receipt.json').read_text())
    if receipt['status']!='complete':raise ValueError('Incomplete replication')
    rows=[]
    for cell in plan['cells']:
        if cell['kind']!='evaluation':continue
        validation=receipt['cells'][cell['id']]['validation']
        source=Path(validation['metrics_path'])
        if digest(source)!=validation['metrics_sha256']:raise ValueError('Changed metrics')
        values=json.loads(source.read_text())['eval/qualified/episodes']
        if len(values)!=512:raise ValueError('Incomplete evaluation aliases')
        rows.append({'arm':cell['arm'],'iteration':cell['checkpoint_iteration'],'preset':cell['preset'],
          **{key:fmean(r[key] for r in values) for key in ['global_mpjpe_mm','local_mpjpe_mm','completed','tracking_qualified']},
          'metrics_sha256':digest(source)})
    report=[]
    for arm in ('R0','R1'):
        for step in (250,500,1000,1500,2000):
            checks=[]
            for preset in ('phys_000','phys_100'):
                origin=next(r for r in rows if r['arm']=='origin' and r['preset']==preset)
                target=next(r for r in rows if r['arm']==arm and r['iteration']==step and r['preset']==preset)
                checks.append({'preset':preset,
                  'global_increase_pct':100*(target['global_mpjpe_mm']/origin['global_mpjpe_mm']-1),
                  'local_increase_pct':100*(target['local_mpjpe_mm']/origin['local_mpjpe_mm']-1),
                  'completion_delta_pp':100*(target['completed']-origin['completed'])})
            hard=fmean(r['tracking_qualified'] for r in rows if r['arm']==arm and r['iteration']==step and r['preset'] in ('ch_push_350','ch_push_fric_350_150'))
            report.append({'arm':arm,'iteration':step,'retention':checks,'hard_qualification_pct':100*hard,
              'empirical_retained':all(c['global_increase_pct']<=10 and c['local_increase_pct']<=10 and c['completion_delta_pp']>=-2 for c in checks)})
    payload={'plan_sha256':PLAN_SHA,'scope':'same-origin continuation seed 8601; empirical gates, not simultaneous inference','rows':rows,'trajectory':report}
    (ROOT/'analysis.json').write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Second continuation-seed replication','',payload['scope'],'',
           '| Arm | Iteration | Nominal global increase | Hard qualification | Retention |',
           '|---|---:|---:|---:|---|']
    for r in report:
        lines.append(f"| {r['arm']} | {r['iteration']} | {r['retention'][0]['global_increase_pct']:+.2f}% | {r['hard_qualification_pct']:.2f}% | {r['empirical_retained']} |")
    (ROOT/'report.md').write_text('\n'.join(lines)+'\n')
    import wandb
    run=wandb.init(entity='16726',project='lucid-sonic',mode='online',group=ROOT.name,
                   name='retention/replication/s8601/analysis',job_type='analysis',dir=str(ROOT),
                   config={'plan_sha256':PLAN_SHA,'scope':payload['scope']})
    for r in report:
        run.log({f"{r['arm']}/hard_qualification_pct":r['hard_qualification_pct'],
                 f"{r['arm']}/empirical_retained":r['empirical_retained'],'iteration':r['iteration']})
    run.summary.update({'complete':True,'report_sha256':digest(ROOT/'report.md')})
    run.finish()
    return payload

if __name__=='__main__':
    deadline=datetime(2026,9,10,tzinfo=timezone.utc)
    while datetime.now(timezone.utc)<deadline:
        path=ROOT/'pilot/receipt.json'
        if path.exists():
            try:receipt=json.loads(path.read_text())
            except json.JSONDecodeError:
                time.sleep(30);continue
            if receipt['status']=='complete':
                summarize();print('Complete: analysis.json and report.md',flush=True);break
            if receipt['status']=='failed':
                print('Replication failed; preserve receipt, no automatic retry.',flush=True);break
        time.sleep(30)
    else:print('Evidence cutoff reached; no new experiments launched.',flush=True)
