#!/usr/bin/env python3
"""One bounded legal contact-stagger trial, actual owned distal palmar surfaces."""
import copy,importlib.util,json,hashlib,subprocess
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('a',ROOT/'scripts/practice/check-hand-geometry.py');gate=importlib.util.module_from_spec(s);s.loader.exec_module(gate);a=gate.a;m=a.c.m
out=ROOT/'docs/practice-hand-batch-3/Dm';seedpath=out/'refined.json';seed=json.loads(seedpath.read_text());p=copy.deepcopy(seed);r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');guitar=json.loads((out/'runtime-guitar.json').read_text());params=np.zeros(27)
assert hashlib.sha256((ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb').read_bytes()).hexdigest()==r.data['sha256']==seed['assetSha256']
chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORD_BY_ID}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.Dm))"],cwd=ROOT));assert chord['frets']==[None,None,0,2,3,1] and chord['fingers']==[None,None,None,2,3,1]
params[:]=json.loads((ROOT/'docs/practice-hand-batch-2/presentation/C-natural-arm.json').read_text())['authoringSource']['sourceSolverParameters']
for st in seed['authoringSource']['stages']:
 sl=slice(6+4*m.FINGERS.index(st['finger']),10+4*m.FINGERS.index(st['finger']));params[sl]=st['finalAngles']
palmar=r.normals[r.triangles].mean(axis=1)@r.palmar>.05;dominant=r.joint_bones[r.joints[np.arange(len(r.joints)),r.weights.argmax(axis=1)]];history=[]
for finger in ['ring','index']:
 fi=m.FINGERS.index(finger);slot=slice(6+4*fi,10+4*fi);original=params[slot].copy();start=copy.deepcopy(p);n=m.NUMBERS[finger];names=[r.by_name[f'finger{n}-{j}.L'] for j in range(1,4)];owned=np.isin(dominant[r.triangles],names).all(axis=1)&palmar;owned&=(dominant[r.triangles]==names[-1]).any(axis=1);target=next(t for t in p['targets'] if t['finger']==finger);string=next(s for s in guitar['strings'] if s['number']==target['string']);line=np.array(string['controlPointsMm']);radius=string['radiusMm'];wire=m.fret_x(target['fret']);segments=gate.clip_line(line,wire-6,wire-1.1);cap0=r.skin(a.world_from_pose(r,start),r.patch_ids[finger]).mean(0);desired=cap0.copy()
 if finger=='ring':desired[0]-=2
 def make(x):
  cur=copy.deepcopy(start);pa=params.copy();pa[slot]=x;q=r.rotations(pa)
  for j in range(1,4):
   name=f'finger{n}-{j}.L';cur['bones'][name]['quaternion']=q[r.by_name[name]].tolist()
  return cur
 def residual(x):
  v=r.skin(a.world_from_pose(r,make(x)));cap=v[r.patch_ids[finger]].mean(0);dist=gate.clearance(v[r.triangles][owned],segments,radius);whole=a.c.line_clearance(v[r.finger_triangles[finger]],line,radius)
  if finger=='ring':return np.r_[(cap[[0,2]]-desired[[0,2]])*2,(dist-.01)*20,max(0,.005-whole)*50,(x-original)*.03]
  return np.r_[(cap[[0,2]]-desired[[0,2]])*.03,(dist-.06)*20,max(0,.005-whole)*60,(x-original)*.03]
 fit=least_squares(residual,original,bounds=(original-np.deg2rad(5),original+np.deg2rad(5)),max_nfev=65,ftol=1e-10,xtol=1e-10,gtol=1e-10,diff_step=1e-5);p=make(fit.x);params[slot]=fit.x;v=r.skin(a.world_from_pose(r,p));history.append({'finger':finger,'evaluations':fit.nfev,'deltaDegrees':np.rad2deg(fit.x-original).tolist(),'finalAngles':fit.x.tolist(),'capPositionMm':v[r.patch_ids[finger]].mean(0).tolist(),'ownerPalmarClearanceMm':gate.clearance(v[r.triangles][owned],segments,radius),'wholeDigitClearanceMm':a.c.line_clearance(v[r.finger_triangles[finger]],line,radius)})
p['authoringSource']={'seed':str(seedpath.relative_to(ROOT)),'sha256':hashlib.sha256(seedpath.read_bytes()).hexdigest(),'method':'One bounded actual-palmar distal contact stagger, ring2mmnutwardwithinunchangedfretregion, strictwhole-stringrejectunchanged','stages':history};(out/'surgical.json').write_text(json.dumps(p,indent=2)+'\n');lib=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());lib['poses']['Dm']=p;(out/'surgical-library.json').write_text(json.dumps(lib));print(json.dumps(history,indent=2),flush=True)
