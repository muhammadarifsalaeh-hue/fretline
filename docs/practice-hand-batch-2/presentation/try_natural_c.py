#!/usr/bin/env python3
"""One bounded authoring experiment: flex proximal joints, preserve C pad anchors.

The result is NOT an approved pose. No production or chord data is changed.
"""
import copy,hashlib,importlib.util,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('c_contacts',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
m=a.c.m;r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');seed_path=ROOT/'docs/practice-trainer/pose-solver/C-contact-refined.json';seed=json.load(open(seed_path));original=np.array(seed['solverParameters']);world,*_=r.fk(original)
report=json.load(open(ROOT/'docs/practice-trainer/pose-solver/C-contact-refined-clearances.json'))
contacts=[next(x for x in report['strings']if x['string']==s)for s in[2,4,5]]
contact_ids=[np.array(x['triangleVertexIndices'])for x in contacts];barys=[np.array(x['barycentric'])for x in contacts]
expected=[b@r.skin(world,ids)for b,ids in zip(barys,contact_ids)]
thumb_id=5190;expected_thumb=r.skin(world,[thumb_id])[0]
normal_targets=[(b@r.skin_normals(world,ids))for b,ids in zip(barys,contact_ids)]
slots=np.r_[np.arange(6),np.arange(6,18),np.arange(22,26)].astype(int)
lo=original[slots].copy();hi=lo.copy();lo[:3]-=20;hi[:3]+=20;lo[3:6]-=np.deg2rad(20);hi[3:6]+=np.deg2rad(20)
for i in range(3):lo[6+4*i:10+4*i]=np.deg2rad([15,-35,5,0]);hi[6+4*i:10+4*i]=np.deg2rad([55,35,110,75])
lo[18:22]=np.deg2rad([-2,-26,-20,-15]);hi[18:22]=np.deg2rad([38,14,15,15])
start=np.clip(original[slots],lo+1e-8,hi-1e-8)
samples=np.unique(np.r_[np.arange(0,len(r.positions),18),*contact_ids,thumb_id])
count=0

def residual(x):
 global count
 count+=1;p=original.copy();p[slots]=x;w,*_=r.fk(p);out=[]
 for ids,bary,target,norm in zip(contact_ids,barys,expected,normal_targets):
  point=bary@r.skin(w,ids);n=bary@r.skin_normals(w,ids);out.extend((point-target)*5);out.extend((n-norm)*3)
 out.extend((r.skin(w,[thumb_id])[0]-expected_thumb)*2)
 pts=r.skin(w,samples);out.extend(m.wood_depth(pts)*4)
 for s in[1,3]:out.extend(np.maximum(0,.3-(m.polyline_distance(pts,m.string_polyline(s,m.c_targets()))-m.GAUGES[s-1]/2))*4)
 out.extend((p[:3]-original[:3])*.005);out.extend((p[3:6]-original[3:6])*.1)
 for i in range(3):
  v=p[6+4*i:10+4*i];out.extend((v-original[6+4*i:10+4*i])*.1);out.append((v[0]-np.deg2rad(25))*.4)
 return np.array(out)

begin=time.monotonic();result=least_squares(residual,start,bounds=(lo,hi),max_nfev=50,ftol=1e-7,xtol=1e-7,gtol=1e-7,x_scale='jac')
p=original.copy();p[slots]=result.x;w,quats,root_rot=r.fk(p);pose=copy.deepcopy(seed);pose['root']={'positionMm':p[:3].tolist(),'quaternion':Rotation.from_matrix(root_rot).as_quat().tolist()};pose['bones']={b['name']:{'quaternion':quats[i].tolist()}for i,b in enumerate(r.bones)};pose['solverParameters']=p.tolist();pose['audit']={'collisionPassed':False,'contactPassed':False,'anatomyPassed':False,'multiViewReviewed':False};pose['status']='needs-review';pose['reviewed']=False;pose['reason']={'th':'ท่าทดลองงอข้อโคนนิ้วเพิ่ม ยังไม่ผ่านการตรวจเมชและภาพ','en':'Experimental proximal-joint flexion candidate; mesh and visual acceptance are pending.'}
(HERE/'C-natural-experiment.json').write_text(json.dumps(pose,indent=2)+'\n')
points=r.skin(w);summary={'sourcePoseSha256':hashlib.sha256(seed_path.read_bytes()).hexdigest(),'assetSha256':r.data['sha256'],'maxEvaluations':50,'functionEvaluations':result.nfev,'residualCalls':count,'elapsedSeconds':time.monotonic()-begin,'optimizerSuccess':bool(result.success),'termination':result.message,'padAnchorErrorsMm':[float(np.linalg.norm(b@points[ids]-target))for ids,b,target in zip(contact_ids,barys,expected)],'thumbAnchorErrorMm':float(np.linalg.norm(r.skin(w,[thumb_id])[0]-expected_thumb)),'actualSkinWoodVertices':int((m.wood_depth(points)>1e-6).sum()),'maximumWoodDepthMm':float(m.wood_depth(points).max()),'anglesDeltaFromRestDegrees':{finger:np.rad2deg(p[6+4*i:10+4*i]).tolist()for i,finger in enumerate(m.FINGERS)},'status':'needs-review','limitations':['Bone angle parameters are rest-relative, not medical zero angles.','No self-collision or actual guitar triangle pass is inferred from fitting.','Native forearm remains cropped.']}
(HERE/'C-natural-experiment-metrics.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
