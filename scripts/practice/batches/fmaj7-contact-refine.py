#!/usr/bin/env python3
"""Refine real saved Fmaj7 ring contact; no musical edits or approval."""
import argparse,copy,hashlib,importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('a',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.c.m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'docs/practice-hand-batch-3/Fmaj7/refined.json');args=ap.parse_args()
 seedfile=ROOT/'docs/practice-hand-batch-3/Fmaj7/candidate.json';seed=json.loads(seedfile.read_text());base=json.loads((ROOT/'docs/practice-hand-batch-2/presentation/C-natural-arm.json').read_text())
 r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');params=np.array(base['authoringSource']['sourceSolverParameters'])
 assert hashlib.sha256((ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb').read_bytes()).hexdigest()==r.data['sha256']==seed['assetSha256']
 chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORD_BY_ID}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.Fmaj7))"],cwd=ROOT));assert chord['frets']==[None,None,3,2,1,0] and chord['fingers']==[None,None,3,2,1,None]
 for st in seed['authoringSource']['stages']:
  slot=slice(6+4*m.FINGERS.index(st['finger']),10+4*m.FINGERS.index(st['finger']));params[slot]+=np.deg2rad(st['angularDeltaDegrees'])
 slot=slice(14,18);original=params[slot].copy();q=r.rotations(params)
 assert max(abs(q[r.by_name[n]]-seed['bones'][n]['quaternion']).max() for n in ['finger4-1.L','finger4-2.L','finger4-3.L'])<1e-10
 export=args.output.parent/'runtime-guitar.json';subprocess.run(['node',str(ROOT/'scripts/practice/export-guitar-collision-mesh.mjs'),'Fmaj7',str(export)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 guitar=json.loads(export.read_text());line=np.array(next(s for s in guitar['strings'] if s['number']==4)['controlPointsMm']);radius=next(s for s in guitar['strings'] if s['number']==4)['radiusMm']
 target=next(t for t in seed['targets'] if t['finger']=='ring');tx,tz=np.array(target['positionMm'])[[0,2]]
 def pose(angles):
  p=copy.deepcopy(seed);cur=params.copy();cur[slot]=angles;quats=r.rotations(cur)
  for j in range(1,4):
   n=f'finger4-{j}.L';p['bones'][n]['quaternion']=quats[r.by_name[n]].tolist()
  return p
 w=a.world_from_pose(r,seed);v=r.skin(w);capstart=v[r.patch_ids['ring']].mean(0)
 def lift_res(angles):
  v=r.skin(a.world_from_pose(r,pose(angles)));cap=v[r.patch_ids['ring']].mean(0);hit=r.lower_surface(v,'ring',tx,tz);y=hit['positionMm'][1] if hit else cap[1]
  return np.r_[(cap[[0,2]]-capstart[[0,2]])*.6,(y-target['positionMm'][1]-.6)*20,(angles-original)*.08]
 lift=least_squares(lift_res,original,bounds=(original-np.deg2rad(5),original+np.deg2rad(5)),max_nfev=45,ftol=1e-10,xtol=1e-10,gtol=1e-10)
 def residual(angles):
  v=r.skin(a.world_from_pose(r,pose(angles)));cap=v[r.patch_ids['ring']].mean(0);clear=a.c.line_clearance(v[r.finger_triangles['ring']],line,radius)
  return np.r_[(cap[[0,2]]-capstart[[0,2]])*.6,(clear-.008)*20,(angles-original)*.08]
 fit=least_squares(residual,lift.x,bounds=(original-np.deg2rad(5),original+np.deg2rad(5)),max_nfev=70,ftol=1e-11,xtol=1e-11,gtol=1e-11,diff_step=1e-5)
 p=pose(fit.x);p['authoringSource']={'seed':str(seedfile.relative_to(ROOT)),'sha256':hashlib.sha256(seedfile.read_bytes()).hexdigest(),'method':'Actual ring skin lower-surface lift then exact runtime polyline/triangle contact refinement; root,wrist,otherdigits unchanged','ringAngularDeltaDegrees':np.rad2deg(fit.x-original).tolist(),'liftEvaluations':lift.nfev,'contactEvaluations':fit.nfev,'originalAngles':original.tolist(),'finalAngles':fit.x.tolist()}
 p['reason']={'th':'ต้นแบบ Fmaj7 ปรับผิวปลายนิ้วนางให้สัมผัสสายจริง รอผลตรวจหลายมุม','en':'Fmaj7 real-skin ring contact refined; exact mesh and independent anatomical review pending.'}
 args.output.write_text(json.dumps(p,indent=2)+'\n');library=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());library['poses']['Fmaj7']=p;(args.output.parent/'refined-library.json').write_text(json.dumps(library))
 print(json.dumps(p['authoringSource'],indent=2),flush=True)
if __name__=='__main__':main()
