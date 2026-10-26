#!/usr/bin/env python3
"""One bounded C7 self-collision refinement; actual mesh gate remains unchanged."""
import copy,importlib.util,json,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('a',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.c.m
out=ROOT/'docs/practice-hand-batch-3/C7';seedfile=out/'candidate.json';seed=json.loads(seedfile.read_text());r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
params=np.array(json.loads((ROOT/'docs/practice-hand-batch-2/presentation/C-natural-arm.json').read_text())['authoringSource']['sourceSolverParameters'])
x0=np.r_[np.deg2rad(seed['authoringSource']['littleMcpSpreadPipDipDegrees']),0.]
ringids=r.finger_vertex_ids['ring'];littleids=r.finger_vertex_ids['little'][::3];w0=a.world_from_pose(r,seed);fixed=r.skin(w0);tree=cKDTree(fixed[ringids]);nr=r.skin_normals(w0,ringids)
target=next(t for t in seed['targets']if t['finger']=='little');tp=np.array(target['positionMm']);line=m.string_polyline(3,seed['targets'])
def pose(x):
 p=copy.deepcopy(seed);params[18:22]=x[:4];q=r.rotations(params)
 for j in range(1,4):
  n=f'finger5-{j}.L';rot=Rotation.from_quat(q[r.by_name[n]])
  if j==1:rot=rot*Rotation.from_rotvec(np.array([0,1,0])*x[4])
  p['bones'][n]['quaternion']=rot.as_quat().tolist()
 return p

def residual(x):
 w=a.world_from_pose(r,pose(x));v=r.skin(w);cap=v[r.patch_ids['little']].mean(0);hit=r.lower_surface(v,'little',tp[0],tp[2]);lower=hit['positionMm'][1]if hit else cap[1]
 dist,near=tree.query(v[littleids]);signed=np.einsum('ij,ij->i',v[littleids]-fixed[ringids[near]],nr[near])
 # Near actual skin only; signed separation rejects embedded neighboring flesh.
 penalty=np.maximum(0,.25-signed)*np.clip((7-dist)/3,0,1)
 clear=a.c.line_clearance(v[r.finger_triangles['little']],line,m.GAUGES[2]/2)
 return np.r_[(cap[[0,2]]-tp[[0,2]])*.7,(lower-tp[1]-.3)*2,(clear-.015)*15,penalty*12,m.wood_depth(v[littleids])*5,(x-x0)*.02]
lo=x0-np.deg2rad([20,20,6,9,20]);hi=x0+np.deg2rad([20,8,35,35,20]);lo[:4]=np.maximum(lo[:4],np.deg2rad([0,-35,0,0]));hi[:4]=np.minimum(hi[:4],np.deg2rad([90,35,105,75]))
fit=least_squares(residual,np.clip(x0,lo+1e-6,hi-1e-6),bounds=(lo,hi),max_nfev=55,ftol=1e-8,diff_step=1e-5)
p=pose(fit.x);p['authoringSource']={'file':str(seedfile.relative_to(ROOT)),'sha256':hashlib.sha256(seedfile.read_bytes()).hexdigest(),'method':'Bounded little4DOF +20degreeaxial freedom with signed ring-surface repulsion and actual little/string surface contact','anglesDegrees':np.rad2deg(fit.x).tolist(),'cost':fit.cost,'evaluations':fit.nfev};(out/'refined.json').write_text(json.dumps(p,indent=2)+'\n')
lib=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());lib['poses']['C7']=p;(out/'refined-library.json').write_text(json.dumps(lib));print(json.dumps(p['authoringSource']),flush=True)
