"""Final local constraint pass for unresolved chords. Acceptance is never inferred.
Two bounded repairs per target, followed by unchanged full mesh and support gates.
"""
import argparse,collections,copy,gzip,importlib.util,json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v5.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
s=importlib.util.spec_from_file_location('m',Path(__file__).with_name('measure-pose.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ap=argparse.ArgumentParser();ap.add_argument('--chords',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--family',action='store_true');args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True);context=f.load_context();meter=m.Measurements();inventory={r['id']:r for r in json.loads((ROOT/'docs/practice-complete-42/tests/candidate-inventory.json').read_text())};owners=[]
for mesh in context['rig'].data['meshes']:
 joints=np.array(mesh['joints']);weights=np.array(mesh['weights']);ids=joints[np.arange(len(joints)),weights.argmax(1)];owners.extend(mesh['skinJointNames'][i]for i in ids)
for key in args.chords.split(','):
 folder=args.out/key;folder.mkdir(exist_ok=True)
 if(folder/'result.json').exists():continue
 record=inventory[key];file=ROOT/record['source'];report_file=ROOT/record['audit']
 if args.family:
  family=ROOT/'.local-preview/practice-complete-42/family'/key;file=family/'global-1/proposal-library.json';report_file=family/'global-1/audit/summary.json'
 seed=json.loads(file.read_text())['poses'][key];row=next(r for r in json.loads(report_file.read_text())['rows']if r['id']==key);history=[]
 for i in range(2):
  if row['geometricPassed']:break
  with gzip.open(report_file.parent/row['rawEvidence'],'rt')as stream:raw=json.load(stream)
  counts=collections.Counter()
  for kind in ['self','guitar']:
   for pair in raw.get(kind,{}).get('pairs',[]):
    for v in pair['vertices'][0]+(pair['vertices'][1]if kind=='self'else[]):
     for digit in f.m.FINGERS:
      if owners[v].startswith('finger'+str(f.m.NUMBERS[digit])+'-'):counts[digit]+=1
  for t in row['contacts']:
   if not t['passed']:counts[f.m.FINGERS[t['finger']-1]]+=200
  if not counts:break
  digit=counts.most_common(1)[0][0];trial=folder/('round-'+str(i)+'-'+digit);input_file=folder/('seed-'+str(i)+'.json');input_file.write_text(json.dumps(seed));print('LOCAL-PASS',key,i,digit,flush=True)
  if not(trial/'audit/summary.json').exists():
   with(folder/('round-'+str(i)+'.log')).open('w')as log:subprocess.run(['python',str(Path(__file__).with_name('repair-contact-v4.py')),'--seed',str(input_file),'--audit',str(report_file),'--digit',digit,'--allow-released','--out',str(trial)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  file=trial/'proposal-library.json';report_file=trial/'audit/summary.json';row=json.loads(report_file.read_text())['rows'][0];seed=json.loads((trial/'candidate.json').read_text());history.append({'row':row,'report':str(report_file.relative_to(ROOT)),'digit':digit});print('LOCAL-AUDIT',key,row['geometricPassed'],'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'contacts',sum(t['passed']for t in row['contacts']),'/',len(row['contacts']),flush=True)
 if row['geometricPassed']:
  support=meter.measure(seed)
  if not support['thumbSupportPassed']or not support['jointPlausibilityPassed']:
   out=folder/'support'
   if not(out/'result.json').exists():
    with(folder/'support.log').open('w')as log:subprocess.run(['python',str(Path(__file__).with_name('thumb-batch-v2.py')),'--seed',str(file.parent/'candidate.json'),'--out',str(out)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
   t=json.loads((out/'result.json').read_text())
   if t['selected']:file=ROOT/t['proposalFile'];report_file=ROOT/t['auditReport'];row=json.loads(report_file.read_text())['rows'][0];seed=json.loads(file.read_text())['poses'][key]
 result={'id':key,'selected':row['geometricPassed'],'support':meter.measure(seed),'teachingApproved':False,'history':history,'proposalFile':str(file.relative_to(ROOT)),'auditReport':str(report_file.relative_to(ROOT))};(folder/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('LOCAL-RESULT',key,result['selected'],result['support']['thumbSupportPassed'],flush=True)
