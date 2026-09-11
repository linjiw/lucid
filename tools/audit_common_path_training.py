"""Read-only final-checkpoint and delivered-exposure audit of the bounded pilot."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import sys

import torch
import wandb
from gear_sonic.trl.trainer import ppo_trainer  # noqa: F401

ROOT=Path('/home/linjiw/lucid-sonic/experiments/path_repair_pilot_s8762_20260907_b')
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=False)
plan=json.loads((ROOT/'plan.json').read_text());status=json.loads((ROOT/'status.json').read_text());assert status['state']=='complete'
files=[ROOT/'plan.json',ROOT/'status.json',ROOT/'train/final_checkpoint.pt',ROOT/'train/initialization.json',ROOT/'train/practice_initialization.json',ROOT/'train/exposure.jsonl',ROOT/'train/push_events.jsonl',Path(plan['initial_checkpoint']),Path(__file__)]
def sha(p):
 with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
binding=dict(inputs={str(p):sha(p) for p in files},kind='read_only_common_path_training_audit_v1',source_commit=plan['commit'])
(OUT/'plan.json').write_text(json.dumps(binding,indent=2))
run=wandb.init(entity='16726',project='lucid-sonic',mode='online',group=ROOT.name,id='path-training-audit-'+sha(OUT/'plan.json')[:12],name='controller-repair/path-input/final-checkpoint-exposure-audit/s8762',dir=str(OUT),config=binding)
try:
 a=torch.load(plan['initial_checkpoint'],map_location='cpu',weights_only=False)['policy_state_dict']
 b=torch.load(ROOT/'train/final_checkpoint.pt',map_location='cpu',weights_only=False)['policy_state_dict']
 assert set(a)==set(b)
 changed=[]
 for k in a:
  if not torch.equal(a[k],b[k]):changed.append(k)
 key='actor_module.decoders.g1_dyn.module.0.weight'
 assert set(changed)=={key,'std'}
 assert torch.equal(a[key][:,:994],b[key][:,:994])
 assert torch.isfinite(b[key]).all() and torch.count_nonzero(b[key][:,994:])==4096
 init=json.loads((ROOT/'train/practice_initialization.json').read_text());names=init['motion_keys']
 counts=Counter();directions=Counter();max_error=0.;events=0
 for line in (ROOT/'train/push_events.jsonl').read_text().splitlines():
  r=json.loads(line)
  for idx,env_id in enumerate(r['env_ids']):
   assert (env_id//4)%2==1
   expected=r['delta_velocity_xy'][idx]
   assert sum(v*v for v in expected)==.25
   before,after=r['before'][idx],r['after'][idx]
   assert before[2:]==after[2:]
   error=max(abs(after[j]-before[j]-expected[j]) for j in range(2));max_error=max(error,max_error)
   assert error<1e-6
   counts[names[r['motion_ids'][idx]]]+=1;directions[str(expected)]+=1;events+=1
 exposure=[json.loads(l) for l in (ROOT/'train/exposure.jsonl').read_text().splitlines()]
 assert [r['iteration'] for r in exposure]==list(range(1,129))
 assert all(r['envs_per_motion']==[64]*4 for r in exposure)
 report=dict(complete=True,changed_actor_state_keys=changed,old_decoder_columns_exact=True,
             new_coordinates_nonzero=4096,delivered_push_events=events,pushes_per_motion=dict(counts),
             push_direction_counts=dict(directions),max_velocity_write_roundoff_m_s=max_error,
             verified_motion_transitions_each=128*64*24,scope='checkpoint/exposure audit; efficacy requires paired evaluation',
             wandb_url=run.url)
 (OUT/'receipt.json').write_text(json.dumps(report,indent=2));run.log(dict(delivered_push_events=events,new_coordinates_nonzero=4096,max_velocity_write_roundoff_m_s=max_error))
 art=wandb.Artifact('path-training-audit-'+sha(OUT/'plan.json')[:12],type='training-audit')
 for p in [OUT/'plan.json',OUT/'receipt.json']:art.add_file(str(p))
 run.log_artifact(art);run.finish();print(json.dumps(report))
except Exception as e:
 run.summary['failure']=str(e);run.finish(exit_code=1);raise
