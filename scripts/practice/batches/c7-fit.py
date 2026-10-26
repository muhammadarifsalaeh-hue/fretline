#!/usr/bin/env python3
"""Bounded little-finger-only IK from audited C, real skin contact; no approval."""
import copy,importlib.util,json,hashlib,subprocess,argparse
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('a',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.c.m

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'docs/practice-hand-batch-3/C7/candidate.json');ap.add_argument('--seed',type=Path,default=ROOT/'docs/practice-hand-batch-2/presentation/C-natural-arm.json');ap.add_argument('--start',default='25,-15,60,30');args=ap.parse_args()
 r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');p=json.loads(args.seed.read_text());seed=copy.deepcopy(p)
 c=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORD_BY_ID}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.C7))"],cwd=ROOT));assert c['voicing']=='x32310'
 params=np.array(p['authoringSource']['sourceSolverParameters']);x=np.deg2rad(np.array(list(map(float,args.start.split(',')))))
 target=np.array([m.fret_x(3)-4,m.board_top(m.string_z(3,m.fret_x(3)-4))+1+m.GAUGES[2],m.string_z(3,m.fret_x(3)-4)])
 def pose(q):
  current=copy.deepcopy(seed);params[18:22]=q;rots=r.rotations(params)
  for j in range(1,4):
   n=f'finger5-{j}.L';current['bones'][n]['quaternion']=rots[r.by_name[n]].tolist()
  return current
 def residual(q):
  current=pose(q);w=a.world_from_pose(r,current);v=r.skin(w);cap=v[r.patch_ids['little']].mean(0);hit=r.lower_surface(v,'little',target[0],target[2]);lower=hit['positionMm'][1] if hit else cap[1]
  n=r.skin_normals(w,r.patch_ids['little']).mean(0)
  return np.r_[(cap[[0,2]]-target[[0,2]])*2,(lower-target[1]-.3)*3,(n-[0,-1,0])*2,m.wood_depth(v[r.finger_vertex_ids['little']])*3,(q-np.deg2rad([35,-10,60,30]))*.02]
 result=least_squares(residual,x,bounds=(np.deg2rad([0,-35,5,0]),np.deg2rad([90,35,105,75])),max_nfev=130,ftol=1e-8,diff_step=1e-5)
 x=result.x;cap0=r.skin(a.world_from_pose(r,pose(x)),r.patch_ids['little']).mean(0)
 targets=m.c_targets()+[{'finger':'little','string':3,'fret':3,'positionMm':target.tolist()}];line=m.string_polyline(3,targets)
 def contact(q):
  current=pose(q);w=a.world_from_pose(r,current);v=r.skin(w);cap=v[r.patch_ids['little']].mean(0)
  clear=a.c.line_clearance(v[r.finger_triangles['little']],line,m.GAUGES[2]/2)
  return np.r_[(cap[[0,2]]-cap0[[0,2]])*.6,(clear-.008)*20,(q-x)*.04]
 refined=least_squares(contact,x,bounds=(x-np.deg2rad(4),x+np.deg2rad(4)),max_nfev=65,ftol=1e-10,diff_step=1e-5)
 p=pose(refined.x);p['chordId']='C7';p['targets']=targets;p['status']='needs-review';p['reviewed']=False;p['audit']={k:False for k in ['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed']};p.pop('solverParameters',None)
 p['reason']={'th':'ต้นแบบ C7 จาก IK บนผิวมือจริง รอการตรวจเมชและภาพหลายมุม','en':'C7 bounded real-skin IK candidate; exact mesh and anatomical review pending.'}
 p['authoringSource']={'file':str(args.seed.relative_to(ROOT)),'sha256':hashlib.sha256(args.seed.read_bytes()).hexdigest(),'method':'Fixed root/wrist/thumb/index/middle/ring, little4DOF constrained local IK then actual triangle string contact refinement','littleMcpSpreadPipDipDegrees':np.rad2deg(refined.x).tolist(),'fitEvaluations':result.nfev,'contactEvaluations':refined.nfev,'cost':result.cost}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(p,indent=2)+'\n')
 print(json.dumps(p['authoringSource']),flush=True)
 lib=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());lib['poses']['C7']=p;(args.output.parent/'library.json').write_text(json.dumps(lib))
if __name__=='__main__':main()
