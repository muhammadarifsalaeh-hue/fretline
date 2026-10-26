#!/usr/bin/env python3
"""Bounded Dm variant from real Fmaj7 skin, no musical/runtime edits."""
import argparse,copy,hashlib,importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('a',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.c.m
ap=argparse.ArgumentParser();ap.add_argument('--lift',type=float,default=.6);ap.add_argument('--label',default='candidate');args=ap.parse_args()
out=ROOT/'docs/practice-hand-batch-3/Dm';out.mkdir(parents=True,exist_ok=True)
seedfile=ROOT/'docs/practice-hand-batch-3/Fmaj7/refined.json';seed=json.loads(seedfile.read_text());initial=json.loads((ROOT/'docs/practice-hand-batch-3/Fmaj7/candidate.json').read_text());base=json.loads((ROOT/'docs/practice-hand-batch-2/presentation/C-natural-arm.json').read_text());r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');params=np.array(base['authoringSource']['sourceSolverParameters'])
assert hashlib.sha256((ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb').read_bytes()).hexdigest()==r.data['sha256']==seed['assetSha256']
for st in initial['authoringSource']['stages']:
 slot=slice(6+4*m.FINGERS.index(st['finger']),10+4*m.FINGERS.index(st['finger']));params[slot]+=np.deg2rad(st['angularDeltaDegrees'])
params[14:18]=seed['authoringSource']['finalAngles']
chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORD_BY_ID}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.Dm))"],cwd=ROOT));assert chord['frets']==[None,None,0,2,3,1] and chord['fingers']==[None,None,None,2,3,1]
targets=[]
for i,fret in enumerate(chord['frets']):
 if fret:
  st=6-i;fi=m.FINGERS[chord['fingers'][i]-1];x=m.fret_x(fret)-4;z=m.string_z(st,x);targets.append({'finger':fi,'string':st,'fret':fret,'positionMm':[x,m.board_top(z)+1+m.GAUGES[st-1],z]})
subprocess.run(['node',str(ROOT/'scripts/practice/export-guitar-collision-mesh.mjs'),'Dm',str(out/'runtime-guitar.json')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);guitar=json.loads((out/'runtime-guitar.json').read_text())
p=copy.deepcopy(seed);history=[]
for finger in ['index','ring']:
 slot=slice(6+4*m.FINGERS.index(finger),10+4*m.FINGERS.index(finger));original=params[slot].copy();start=copy.deepcopy(p);target=next(t for t in targets if t['finger']==finger);desired=np.array(target['positionMm']);desired[1]+=.4;ss=next(s for s in guitar['strings'] if s['number']==target['string']);line=np.array(ss['controlPointsMm']);radius=ss['radiusMm'];lo=original-np.deg2rad([28,28,28,28]);hi=original+np.deg2rad([28,28,28,28])
 def pose(x):
  cur=copy.deepcopy(start);pa=params.copy();pa[slot]=x;q=r.rotations(pa)
  for j in range(1,4):
   n=f'finger{m.NUMBERS[finger]}-{j}.L';cur['bones'][n]['quaternion']=q[r.by_name[n]].tolist()
  return cur
 def fit_res(x):
  w=a.world_from_pose(r,pose(x));v=r.skin(w);tip=v[r.patch_ids[finger]].mean(0);depth=m.wood_depth(v[r.finger_vertex_ids[finger]])
  return np.r_[(tip-desired)*3,depth*5,(x-original)*.08]
 fit=least_squares(fit_res,original,bounds=(lo,hi),max_nfev=45,ftol=1e-9,diff_step=1e-5);x0=fit.x;cap0=r.skin(a.world_from_pose(r,pose(x0)),r.patch_ids[finger]).mean(0)
 def lift_res(x):
  w=a.world_from_pose(r,pose(x));v=r.skin(w);cap=v[r.patch_ids[finger]].mean(0);hit=r.lower_surface(v,finger,desired[0],desired[2]);y=hit['positionMm'][1] if hit else cap[1]
  return np.r_[(cap[[0,2]]-cap0[[0,2]])*.6,(y-target['positionMm'][1]-args.lift)*20,(x-x0)*.08]
 lifted=least_squares(lift_res,x0,bounds=(x0-np.deg2rad(8),x0+np.deg2rad(8)),max_nfev=40,ftol=1e-10,diff_step=1e-5)
 def touch_res(x):
  v=r.skin(a.world_from_pose(r,pose(x)));cap=v[r.patch_ids[finger]].mean(0);clear=a.c.line_clearance(v[r.finger_triangles[finger]],line,radius)
  return np.r_[(cap[[0,2]]-cap0[[0,2]])*.6,(clear-.008)*20,(x-x0)*.08]
 touched=least_squares(touch_res,lifted.x,bounds=(x0-np.deg2rad(8),x0+np.deg2rad(8)),max_nfev=55,ftol=1e-10,diff_step=1e-5);p=pose(touched.x);params[slot]=touched.x;history.append({'finger':finger,'fitEvaluations':fit.nfev,'liftEvaluations':lifted.nfev,'contactEvaluations':touched.nfev,'finalAngles':touched.x.tolist(),'deltaDegrees':np.rad2deg(touched.x-original).tolist()})
p['chordId']='Dm';p['targets']=targets;p['status']='needs-review';p['reviewed']=False;p['audit']={k:False for k in ['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed']};p['reason']={'th':'ต้นแบบ Dm จาก IK ผิวจริง รอการตรวจหลายมุม','en':'Dm real-skin IK candidate; collision and anatomical review pending.'};p['authoringSource']={'seed':str(seedfile.relative_to(ROOT)),'sha256':hashlib.sha256(seedfile.read_bytes()).hexdigest(),'method':'Fixed root/wrist/thumb/middle/little; bounded index and ring real-skin IK, lift, physical string contact','stages':history,'contactLiftMm':args.lift,'trialLabel':args.label}
(out/(args.label+'.json')).write_text(json.dumps(p,indent=2)+'\n');lib=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());lib['poses']['Dm']=p;(out/(args.label+'-library.json')).write_text(json.dumps(lib));print(json.dumps(history,indent=2),flush=True)
