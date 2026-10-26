#!/usr/bin/env python3
"""Bounded actual-TRS single-chain refinements from audited C-family seeds.
Musical central data and model weights are immutable. Outputs need exact audits.
"""
import argparse,copy,hashlib,importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('a',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
m=a.c.m

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('chord',choices=['Am','Em','Em7']);ap.add_argument('--seed',type=Path);ap.add_argument('--output',type=Path);ap.add_argument('--iterations',type=int,default=70);ap.add_argument('--trial',type=int,default=0);args=ap.parse_args()
 out=args.output or ROOT/f'docs/practice-hand-batch-3/{args.chord}/candidate.json';out.parent.mkdir(parents=True,exist_ok=True)
 lib_path=ROOT/'src/features/practice/assets/hand-poses.json';lib=json.loads(lib_path.read_text());seed_path=args.seed
 seed=copy.deepcopy(json.loads(seed_path.read_text()) if seed_path else lib['poses']['Am7'])
 chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',f"import{{PRACTICE_CHORD_BY_ID}}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.{args.chord}))"],cwd=ROOT))
 assert chord['voicing']=={'Am':'x02210','Em':'022000','Em7':'020000'}[args.chord]
 r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
 assert digest(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb')==r.data['sha256']==seed['assetSha256']
 source=seed.get('authoringSource',{}).get('sourceSolverParameters')
 if source is None:source=lib['poses']['Am7']['authoringSource']['sourceSolverParameters']
 params=np.array(source).copy();params[16:18]=np.deg2rad([25,25])
 if 'fitParameters' in seed.get('authoringSource',{}):params=np.array(seed['authoringSource']['fitParameters'])
 changes=['ring'] if args.chord=='Am' else ['index','middle','ring']
 if args.chord in ['Em','Em7']:params[8:10]=np.deg2rad([45,25])
 targets=[]
 for i,fret in enumerate(chord['frets']):
  if fret:
   finger=m.FINGERS[chord['fingers'][i]-1];s=6-i;x=m.fret_x(fret)-4;z=m.string_z(s,x)
   targets.append({'finger':finger,'string':s,'fret':fret,'positionMm':[x,m.board_top(z)+1+m.GAUGES[s-1],z]})
 pose=copy.deepcopy(seed);pose['chordId']=args.chord;pose['targets']=targets;pose.pop('solverParameters',None)
 def make(p):
  q=r.rotations(p);pose2=copy.deepcopy(pose)
  for finger in changes:
   for j in range(1,4):
    name=f'finger{m.NUMBERS[finger]}-{j}.L';pose2['bones'][name]['quaternion']=q[r.by_name[name]].tolist()
  return pose2
 # Keep thumb/wrist and untouched chains completely fixed.
 logs=[]
 for finger in changes:
  slot=slice(6+4*m.FINGERS.index(finger),10+4*m.FINGERS.index(finger));original=params[slot].copy()
  target=next((t for t in targets if t['finger']==finger),None)
  if target is None:
   continue
  wanted=np.array(target['positionMm']);start=original.copy()
  if args.trial:start+=np.deg2rad(([10,-6,-10,5],[-10,6,15,-10],[20,0,-20,10])[((args.trial-1)%3)])
  bounds=np.deg2rad(([0,-40,5,0],[80,40,115,85]));start=np.clip(start,bounds[0]+1e-5,bounds[1]-1e-5)
  world=a.world_from_pose(r,make(params));fixed=r.skin(world)
  dense=r.sample_ids
  def residual(angles):
   current=params.copy();current[slot]=angles;world=a.world_from_pose(r,make(current));points=r.skin(world)
   cap=points[r.patch_ids[finger]].mean(0)
   n=r.skin_normals(world,r.patch_ids[finger]).mean(0)
   # Actual surface patch, anatomically limited interphalangeal deltas.
   own=points[r.finger_vertex_ids[finger]]
   return np.r_[(cap-wanted)*3,(n-[0,-1,0])*3,m.wood_depth(own)*3,(angles-original)*.08]
  fit=least_squares(residual,start,bounds=bounds,max_nfev=args.iterations,ftol=1e-8,diff_step=1e-5)
  params[slot]=fit.x
  # Lift and refine exact closed-triangle contact to prevent flat unsigned zero minima.
  line=m.string_polyline(target['string'],targets);radius=m.GAUGES[target['string']-1]/2
  baseline=fit.x.copy();world=a.world_from_pose(r,make(params));points=r.skin(world);cap0=points[r.patch_ids[finger]].mean(0)
  def refine(angles,lift):
   current=params.copy();current[slot]=angles;world=a.world_from_pose(r,make(current));points=r.skin(world)
   cap=points[r.patch_ids[finger]].mean(0)
   hit=r.lower_surface(points,finger,wanted[0],wanted[2]);lower=hit['positionMm'][1] if hit else cap[1]
   y=(lower-wanted[1]-.6) if lift else a.c.line_clearance(points[r.finger_triangles[finger]],line,radius)-.008
   return np.r_[(cap[[0,2]]-wanted[[0,2]])*.6,y*20,(angles-baseline)*.06,m.wood_depth(points[r.finger_vertex_ids[finger]])*2]
  low=np.maximum(bounds[0],baseline-np.deg2rad(15));high=np.minimum(bounds[1],baseline+np.deg2rad(15))
  lifted=least_squares(lambda q:refine(q,True),baseline,bounds=(low,high),max_nfev=45,ftol=1e-9,diff_step=1e-5)
  refined=least_squares(lambda q:refine(q,False),lifted.x,bounds=(low,high),max_nfev=55,ftol=1e-10,diff_step=1e-5)
  params[slot]=refined.x;logs.append({'finger':finger,'cost':fit.cost,'anglesDegrees':np.rad2deg(refined.x).tolist(),'fitEvaluations':fit.nfev,'refineEvaluations':refined.nfev})
  print(json.dumps(logs[-1]),flush=True)
 candidate=make(params);candidate['reviewed']=False;candidate['status']='needs-review';candidate['audit']={k:False for k in ['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed']}
 candidate['reason']={'en':'Bounded actual skinned-surface IK candidate; independent collision and anatomical review pending.','th':'ต้นแบบ IK จากผิวโมเดลจริง รอตรวจการชนและกายวิภาค'}
 candidate['authoringSource']={'seed':str(seed_path.relative_to(ROOT)) if seed_path and seed_path.is_relative_to(ROOT) else str(seed_path or lib_path.relative_to(ROOT)),'sourceSha256':digest(seed_path or lib_path),'fitParameters':params.tolist(),'sourceSolverParameters':source,'operation':'Only selected local finger quaternions; audited root, wrist, thumb, source weights and anatomy retained.','logs':logs}
 out.write_text(json.dumps(candidate,indent=2)+'\n')
 print(str(out),flush=True)
if __name__=='__main__':main()
