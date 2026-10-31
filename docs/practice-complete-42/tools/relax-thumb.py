"""Authoring only: free a thumb that a saved root placement pushes into the neck.
Does not edit runtime data, weaken the exact checker, or certify teaching poses.
"""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('fitter',ROOT/'scripts/practice/fit-missing-poses.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
a=f.a;m=f.m

def relax(seed,folder):
 folder.mkdir(parents=True,exist_ok=True);r=f.load_context()['rig'];names=[f'finger1-{i}.L'for i in range(1,4)]
 rest=f.a.world_from_pose(r,seed);base_points=r.skin(rest);base_pad=base_points[r.patch_ids['thumb']].mean(0)
 ids=np.unique(np.concatenate([r.finger_vertex_ids['thumb'],r.triangles[np.any(np.isin(r.triangles,r.finger_vertex_ids['thumb']),axis=1)].reshape(-1)]))
 faces=r.finger_triangles['thumb'];base=np.array([Rotation.from_quat(seed['bones'][b['name']]['quaternion']).as_matrix()for b in r.bones]);local=r.rest_local.copy()
 root=np.eye(4);root[:3,:3]=Rotation.from_quat(seed['root']['quaternion']).as_matrix()*1000;root[:3,3]=seed['root']['positionMm'];order=[]
 def visit(i):
  if i in order:return
  if r.parents[i]>=0:visit(r.parents[i])
  order.append(i)
 for i in range(len(r.bones)):visit(i)
 def pose(x):
  rotations=base.copy()
  for j,name in enumerate(names):rotations[r.by_name[name]]=base[r.by_name[name]]@Rotation.from_rotvec(x[j*3:j*3+3]).as_matrix()
  l=local.copy();l[:,:3,:3]=rotations*np.array([b['scale']for b in r.bones])[:,None,:];w=np.empty_like(l)
  for i in order:w[i]=w[r.parents[i]]@l[i]if r.parents[i]>=0 else l[i]
  return root@w,rotations
 def residual(x):
  world,_=pose(x);points=r.skin(world);tri=points[faces];samples=np.vstack([points[ids],tri.mean(1),*(tri[:,i]*.5+tri[:,(i+1)%3]*.5 for i in range(3))]);pad=points[r.patch_ids['thumb']].mean(0)
  # Preserve a usable supporting position instead of translating the whole hand.
  return np.r_[m.wood_depth(samples)*100,(pad-base_pad)*.015,x*.03]
 result=least_squares(residual,np.zeros(9),bounds=(-np.deg2rad(14),np.deg2rad(14)),max_nfev=140,ftol=1e-10,xtol=1e-10,gtol=1e-10,diff_step=1e-5)
 world,rot=pose(result.x);p=copy.deepcopy(seed)
 for name in names:p['bones'][name]['quaternion']=Rotation.from_matrix(rot[r.by_name[name]]).as_quat().tolist()
 p['audit']={k:False for k in f.previous.GATES};p['status']='needs-review';p['reviewed']=False;p.pop('solverParameters',None)
 p['authoringSource']={'method':'Thumb-only bounded local rotations; all four fretting fingers and hand root unchanged','seedTransformSHA256':f.gate.transform_hash(seed),'deltaRotationVectorsRadians':result.x.tolist(),'solverSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (folder/'candidate.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
 metrics={'id':p['chordId'],'cost':float(result.cost),'iterations':result.nfev,'thumbMovementDegrees':np.rad2deg(result.x).tolist(),'originalPadMm':base_pad.tolist(),'newPadMm':r.skin(world)[r.patch_ids['thumb']].mean(0).tolist(),'notAcceptanceGate':True}
 (folder/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics),flush=True);return p
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();p=relax(json.loads(args.seed.read_text()),args.out)
 lib=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());lib['poses'][p['chordId']]=p;(args.out/'proposal-library.json').write_text(f.previous.frozen_json(lib))
