"""Build the public controller-foundation snapshot from local experiment receipts."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path('/home/linjiw/lucid-sonic/experiments')

def read(relative):
    return json.loads((ROOT / relative).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    release = read('released_origin_path_screen_20260907_a/status.json')
    shadow = read('path_input_shadow_gates_20260907_a/status.json')
    released = {}
    for key, cell in release['cells'].items():
        if cell.get('state') != 'complete':
            raise ValueError('released origin comparison incomplete')
        for name, expected in cell.get('artifact_hashes', {}).items():
            if sha(Path(name)) != expected:
                raise ValueError('changed evidence')
        released[key] = {k: v for k, v in cell.items() if k in ['state', 'summary', 'wandb_url']}
    shadow_pairs = {}
    gate = ROOT/'path_input_shadow_gates_20260907_a/gate.json'
    if gate.exists():
        shadow_pairs = json.loads(gate.read_text())
    pilot_path = ROOT/'path_repair_pilot_s8762_20260907_b/status.json'
    pilot = json.loads(pilot_path.read_text()) if pilot_path.exists() else {'state': 'not_started'}
    init_path = ROOT/'path_repair_pilot_s8762_20260907_b/train/initialization.json'
    init = json.loads(init_path.read_text()) if init_path.exists() else {}
    exposure = ROOT/'path_repair_pilot_s8762_20260907_b/train/exposure.jsonl'
    iteration = json.loads(exposure.read_text().splitlines()[-1])['iteration'] if exposure.exists() else 0
    value = dict(training_iteration=iteration, snapshot_utc=datetime.now(timezone.utc).isoformat(),
                 released_cells=released, shadow_state=shadow['state'], shadow_gate=shadow_pairs,
                 failed_cross_process_gates={name:read(f'path_input_native_gates_20260907_{name}/gate.json') for name in ['a','b']},
                 gpu_diagnostic=read('path_input_gpu_diagnostic_20260907_a/receipt.json'),
                 pilot={k:v for k,v in pilot.items() if k in ['state','plan_sha256','runtime','result']},
                 pilot_initialization=init,
                 limits=['Development motions and one shared origin; no curriculum advantage demonstrated.',
                         'Broad qualification thresholds are not high-quality competence or recovery guarantees.',
                         'Original cross-process gates remain failed; same-state gate is a documented amendment.',
                         'Path position is privileged simulation input until deployment measurement is established.'])
    target=Path(__file__).resolve().parents[1]/'site/data/controller-progress-2026-09-07.json'
    target.write_text(json.dumps(value,indent=2)+'\n')

if __name__ == '__main__':
    build()
