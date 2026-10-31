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
  chord=context['chords'][key]
  def prefer(parent,fallback):
   path=args.out/parent/'selected.json';result=args.out/parent/'result.json'
   if result.exists():
    info=json.loads(result.read_text())
    if info.get('selected')and info.get('supportPassed'):return path
   return source_root/fallback
  dz=0.;dx=0.;retarget={}
  if key=='A':source=source_root/'robust-open/Esus4/selected.json';dz=-7.5
  elif key=='Asus4':
   source=prefer('A','robust-open/Esus4/selected.json');dz=-7.5 if 'Esus4'in str(source)else 0
  elif key=='D7':source=source_root/'thumb-final/B7/selected.json';dz=-15
  elif key=='Bm':source=source_root/'family/Bmaj7/selected.json'
  elif key=='Cm':source=prefer('Bm','family/Bmaj7/selected.json');dx=f.m.fret_x(3)-f.m.fret_x(2)
  elif key=='Bm7':source=prefer('Bm','family/Bmaj7/selected.json')
  elif key=='Cm7':source=prefer('Bm7','family/Bmaj7/selected.json');dx=f.m.fret_x(3)-f.m.fret_x(2)
  elif key=='Csus2':
   source=prefer('Cm','family/Bmaj7/selected.json');dx=0 if '/Cm/'in str(source)else f.m.fret_x(3)-f.m.fret_x(2)
  elif key=='Emaj7':source=source_root/'thumb-final/B7/selected.json';retarget={'middle':'ring','ring':'middle'}
  elif key=='G':source=source_root/'thumb-final/Gmaj7/selected.json';retarget={'index':'middle','middle':'ring','ring':'index'}
  elif key=='Dmaj7':source=source_root/'thumb-contact-polish/Gm/trials/selected.json';dx=f.m.fret_x(2)-f.m.fret_x(3)
  else:raise ValueError(key)
  original_seed=json.loads(source.read_text());seed=copy.deepcopy(original_seed);origin=seed['chordId'];assert meter.measure(seed)['thumbSupportPassed'];rig=context['rig']
  if retarget:
   from scipy.spatial.transform import Rotation
   source_world=f.a.world_from_pose(rig,original_seed)
   def rotation(matrix):return Rotation.from_matrix(matrix[:3,:3]).as_matrix()
   for target_digit,source_digit in retarget.items():
    for segment in range(1,4):
     target_name=f'finger{f.m.NUMBERS[target_digit]}-{segment}.L';old_name=f'finger{f.m.NUMBERS[source_digit]}-{segment}.L';ti=rig.by_name[target_name];oi=rig.by_name[old_name];desired=rotation(source_world[oi])@rotation(rig.rest_world[oi]).T@rotation(rig.rest_world[ti]);current=f.a.world_from_pose(rig,seed);parent=rig.parents[ti];seed['bones'][target_name]['quaternion']=Rotation.from_matrix(rotation(current[parent]).T@desired).as_quat().tolist()
  seed['root']['positionMm']=(np.array(seed['root']['positionMm'])+np.array([dx,0,dz])).tolist()
  if key=='G':
   points=rig.skin(f.a.world_from_pose(rig,seed));shifts=[]
   for t in f.effective_contacts(chord):
    digit=f.m.FINGERS[t['finger']-1];x=f.m.fret_x(t['fret'])-4;z=f.m.string_z(t['string'],x);goal=np.array([x,f.m.board_top(z)+1.1,z]);shifts.append(goal-points[rig.patch_ids[digit]].mean(0))
   delta=np.clip(np.mean(shifts,axis=0),[-20,-10,-20],[20,10,20]);seed['root']['positionMm']=(np.array(seed['root']['positionMm'])+delta).tolist()
  source_contacts=f.effective_contacts(context['chords'][origin]);offsets={}
  for t in f.effective_contacts(chord):
   digit=f.m.FINGERS[t['finger']-1];source_digit=retarget.get(digit,digit);finger=f.m.FINGERS.index(source_digit)+1;matches=[v for v in source_contacts if v['finger']==finger];near=min(matches,key=lambda v:abs(v['string']-t['string'])*3+abs(v['fret']-t['fret']))if matches else None;off=original_seed.get('pressOffsetsMm',{}).get(f"{near['string']}:{near['fret']}",4)if near else 4;off=float(np.clip(off,1.5,min(24,f.m.fret_x(t['fret'])-f.m.fret_x(t['fret']-1)-5)));offsets[f"{t['string']}:{t['fret']}"]=off
  seed['chordId']=key;seed['pressOffsetsMm']=offsets;seed['status']='needs-review';seed['reviewed']=False;seed['audit']={v:False for v in f.previous.GATES};seed.pop('thumbSupport',None);seed.pop('technicalReview',None);seed['transferSeed']={'source':str(source.relative_to(ROOT)),'sourceChord':origin,'sourceSHA256':sha(source),'rootShiftMm':[dx,0,dz],'retargetedDigits':retarget,'notTargetApproval':True};(folder/'seed.json').write_text(json.dumps(seed,indent=2)+'\n');history=[];row=None;evidence=None;started=time.monotonic();print('NEARBY',key,'from',origin,'rootShift',[dx,0,dz],'retarget',retarget,flush=True)
  for i in range(2):
   trial=folder/('global-'+str(i))
   if(trial/'candidate.json').exists():candidate=json.loads((trial/'candidate.json').read_text())
   else:candidate,_=f.fit(context,chord,seed,trial,iterations=100,root_free=True,evidence=evidence,radius=None if i==0 else 14,exact_polish=bool(row and row['skinAndClothSelfCrossingPairs']==0),max_seconds=95,all_fingers=True,full_polish=True)
   report,file=batch.audit(base,candidate,trial)if not(trial/'audit/summary.json').exists()else(json.loads((trial/'audit/summary.json').read_text()),trial/'proposal-library.json');row=report['rows'][0];evidence=file.parent/'audit'/row['rawEvidence'];history.append({'phase':'global','row':row,'report':str((file.parent/'audit/summary.json').relative_to(ROOT))});seed=candidate;print('FAMILY-AUDIT',key,'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'contacts',sum(t['passed']for t in row['contacts']),'/',len(row['contacts']),'passed',row['geometricPassed'],flush=True)
   if row['geometricPassed']:break
  for i in range(1):
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
