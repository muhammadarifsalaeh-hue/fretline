"""Re-author related barres from genuinely audited full-barre seed geometry.
Every target receives independent real-mesh audits, including local repairs.
No borrowed seed is ever accepted as a target without checking it.
"""
import argparse,collections,copy,gzip,hashlib,importlib.util,json,subprocess,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('batch',Path(__file__).with_name('template-batch-v4.py'));batch=importlib.util.module_from_spec(s);s.loader.exec_module(batch)
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v5.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
s=importlib.util.spec_from_file_location('measure',Path(__file__).with_name('measure-pose.py'));measure=importlib.util.module_from_spec(s);s.loader.exec_module(measure)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--chords',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True);context=f.load_context();base=copy.deepcopy(context['library']);meter=measure.Measurements();owners=[]
 for mesh in context['rig'].data['meshes']:
  joints=np.array(mesh['joints']);weights=np.array(mesh['weights']);ids=joints[np.arange(len(joints)),weights.argmax(1)];owners.extend(mesh['skinJointNames'][i]for i in ids)
 source_root=ROOT/'.local-preview/practice-complete-42';sources={'F':source_root/'thumb-final/F/selected.json','Gm':source_root/'thumb-contact-polish/Gm/trials/selected.json'}
 for key in args.chords.split(','):
  folder=args.out/key;folder.mkdir(exist_ok=True)
  if(folder/'result.json').exists():print('RESUME',key,flush=True);continue
  chord=context['chords'][key];origin='Gm'if key=='Csus2'else'F';source=sources[origin];seed=json.loads(source.read_text());assert meter.measure(seed)['thumbSupportPassed'];before=context['chords'][origin];string_shift=-1;fret_shift=0 if key=='Csus2'else 1 if key=='Bm'else 2;matches=[];low=[];high=[]
  for t in f.effective_contacts(chord):
   match=next((v for v in f.effective_contacts(before)if v['finger']==t['finger']and v['string']+string_shift==t['string']and v['fret']+fret_shift==t['fret']),None);assert match,'A transfer requires the exact same canonical finger/string/fret relationship';sx=f.m.fret_x(match['fret'])-seed.get('pressOffsetsMm',{}).get(f"{match['string']}:{match['fret']}",4);wire=f.m.fret_x(t['fret']);max_off=min(24,wire-f.m.fret_x(t['fret']-1)-5);low.append(wire-max_off-sx);high.append(wire-3-sx);matches.append((t,match,sx))
  assert max(low)<=min(high);desired=float(np.mean([f.m.fret_x(t['fret'])-f.m.fret_x(v['fret'])for t,v,_ in matches]));dx=float(np.clip(desired,max(low),min(high)));offsets={f"{t['string']}:{t['fret']}":float(f.m.fret_x(t['fret'])-(sx+dx))for t,v,sx in matches};guitar=f.export_source(chord,folder);radii={v['number']:v['radiusMm']for v in guitar['strings']};dz=float(np.median([f.m.string_z(t['string'],sx+dx)-f.m.string_z(v['string'],sx)for t,v,sx in matches]));dy=float(np.median([f.m.board_top(f.m.string_z(t['string'],sx+dx))+2*radii[t['string']]-f.m.board_top(f.m.string_z(v['string'],sx))-2*radii[v['string']]for t,v,sx in matches]));seed['root']['positionMm']=(np.array(seed['root']['positionMm'])+np.array([dx,dy,dz])).tolist();seed['chordId']=key;seed['pressOffsetsMm']=offsets;seed['status']='needs-review';seed['reviewed']=False;seed['audit']={v:False for v in f.previous.GATES};seed.pop('thumbSupport',None);seed.pop('technicalReview',None);seed['transferSeed']={'source':str(source.relative_to(ROOT)),'sourceSHA256':sha(source),'canonicalStringShift':string_shift,'canonicalFretShift':fret_shift,'measuredRootTranslationMm':[dx,dy,dz],'preservedSourceContactX':True,'notTargetApproval':True};(folder/'seed.json').write_text(json.dumps(seed,indent=2)+'\n');history=[];row=None;evidence=None;started=time.monotonic();print('SPATIAL-TRANSFER',key,'from',origin,'root',[dx,dy,dz],flush=True)
  raw_folder=folder/'raw-transpose';raw_folder.mkdir(exist_ok=True);(raw_folder/'candidate.json').write_text(json.dumps(seed,indent=2)+'\n');report,file=batch.audit(base,seed,raw_folder)if not(raw_folder/'audit/summary.json').exists()else(json.loads((raw_folder/'audit/summary.json').read_text()),raw_folder/'proposal-library.json');row=report['rows'][0];evidence=file.parent/'audit'/row['rawEvidence'];history.append({'phase':'raw-spatial-transfer','row':row,'report':str((file.parent/'audit/summary.json').relative_to(ROOT))});print('RAW-TRANSFER',key,row['geometricPassed'],'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'contacts',sum(t['passed']for t in row['contacts']),'/',len(row['contacts']),flush=True)
  for i in range(2):
   if row['geometricPassed']:break
   trial=folder/('global-'+str(i))
   if(trial/'candidate.json').exists():candidate=json.loads((trial/'candidate.json').read_text())
   else:candidate,_=f.fit(context,chord,seed,trial,iterations=100,root_free=True,evidence=evidence,radius=None if i==0 else 14,exact_polish=bool(row and row['skinAndClothSelfCrossingPairs']==0),max_seconds=95,all_fingers=True,full_polish=True)
   report,file=batch.audit(base,candidate,trial)if not(trial/'audit/summary.json').exists()else(json.loads((trial/'audit/summary.json').read_text()),trial/'proposal-library.json');row=report['rows'][0];evidence=file.parent/'audit'/row['rawEvidence'];history.append({'phase':'global','row':row,'report':str((file.parent/'audit/summary.json').relative_to(ROOT))});seed=candidate;print('FAMILY-AUDIT',key,'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'contacts',sum(t['passed']for t in row['contacts']),'/',len(row['contacts']),'passed',row['geometricPassed'],flush=True)
   if row['geometricPassed']:break
  for i in range(2):
   if row['geometricPassed']:break
   with gzip.open(evidence,'rt')as stream:raw=json.load(stream)
   count=collections.Counter()
   for kind in ['self','guitar']:
    for pair in raw.get(kind,{}).get('pairs',[]):
     for v in pair['vertices'][0]+(pair['vertices'][1]if kind=='self'else[]):
      name=owners[v]
      for digit in f.m.FINGERS:
       if name.startswith('finger'+str(f.m.NUMBERS[digit])+'-'):count[digit]+=1
   for t in row['contacts']:
    if not t['passed']:count[f.m.FINGERS[t['finger']-1]]+=200
   if not count:break
   digit=count.most_common(1)[0][0];trial=folder/('local-'+str(i)+'-'+digit);source=folder/('local-input-'+str(i)+'.json');source.write_text(json.dumps(seed));prior=file.parent/'audit/summary.json'
   if not(trial/'audit/summary.json').exists():
    with(folder/('local-'+str(i)+'.log')).open('w')as log:subprocess.run(['python',str(Path(__file__).with_name('repair-contact-v4.py')),'--seed',str(source),'--audit',str(prior),'--digit',digit,'--allow-released','--out',str(trial)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
   file=trial/'proposal-library.json';report=json.loads((trial/'audit/summary.json').read_text());row=report['rows'][0];seed=json.loads((trial/'candidate.json').read_text());evidence=trial/'audit'/row['rawEvidence'];history.append({'phase':'local','digit':digit,'row':row,'report':str((trial/'audit/summary.json').relative_to(ROOT))});print('FAMILY-LOCAL',key,digit,'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'passed',row['geometricPassed'],flush=True)
  if row['geometricPassed']:
   thumb_folder=folder/'support'
   if not(thumb_folder/'result.json').exists():
    with(folder/'support.log').open('w')as log:subprocess.run(['python',str(Path(__file__).with_name('thumb-batch-v2.py')),'--seed',str(file.parent/'candidate.json'),'--out',str(thumb_folder)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
   thumb_result=json.loads((thumb_folder/'result.json').read_text())
   if thumb_result['selected']:file=ROOT/thumb_result['proposalFile'];report=json.loads((ROOT/thumb_result['auditReport']).read_text());row=report['rows'][0];seed=json.loads(file.read_text())['poses'][key]
  selected,decision=batch.selector.select(f,base,json.loads(file.read_text()),report,sha(file),context['model_sha'],context['chord_sha'],[key]);support=meter.measure(seed);result={'id':key,'selected':decision[0]['selected'],'supportPassed':support['thumbSupportPassed']and support['jointPlausibilityPassed'],'teachingApproved':False,'history':history,'proposalFile':str(file.relative_to(ROOT)),'auditReport':str((file.parent/'audit/summary.json').relative_to(ROOT)),'secondsIncludingAudits':time.monotonic()-started}
  if result['selected']:(folder/'selected.json').write_text(json.dumps(selected['poses'][key],indent=2)+'\n')
  (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('FAMILY-RESULT',key,result['selected'],result['supportPassed'],flush=True)
if __name__=='__main__':main()
