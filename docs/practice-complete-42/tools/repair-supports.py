"""Process newly measured poses, preserving roots and every fretting bone."""
import argparse,importlib.util,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('metrics',Path(__file__).with_name('measure-pose.py'));metrics=importlib.util.module_from_spec(s);s.loader.exec_module(metrics)
ap=argparse.ArgumentParser();ap.add_argument('--chords',required=True);args=ap.parse_args();meter=metrics.Measurements();rows=[]
for key in args.chords.split(','):
 target=ROOT/'.local-preview/practice-complete-42/thumb-final'/key
 if(target/'result.json').exists()and json.loads((target/'result.json').read_text()).get('selected'):print('PRESERVED',key,flush=True);continue
 choices=[]
 for file in(ROOT/'.local-preview/practice-complete-42').rglob('selected.json'):
  pose=json.loads(file.read_text())
  if pose['chordId']==key:choices.append((int('thumb-final'in str(file)),file.stat().st_mtime,file))
 seed=max(choices)[2]if choices else ROOT/'.local-preview/practice-complete-42/thumb-input'/(key+'.json')
 if not seed.exists():print('NOT-YET-MESH-PASSING',key,flush=True);continue
 pose=json.loads(seed.read_text());measurement=meter.measure(pose);rows.append(measurement)
 if measurement['thumbSupportPassed']and measurement['jointPlausibilityPassed']:print('SUPPORT-ALREADY-VALID',key,measurement['thumbSupportWitness']['distanceMm'],flush=True);continue
 print('REPAIR-SUPPORT',key,measurement['thumbSupportWitness'],flush=True)
 subprocess.run(['python',str(Path(__file__).with_name('thumb-batch.py')),'--seed',str(seed),'--out',str(target)],cwd=ROOT,check=True)
(ROOT/'docs/practice-complete-42/tests/support-repair-inputs.json').write_text(json.dumps({'rows':rows},indent=2)+'\n')
