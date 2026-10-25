#!/usr/bin/env python3
"""Release the unused index on Cmaj7, keeping the audited C wrist/other digits.

Authoring only: no musical data edits and no automatic anatomical approval.
"""
import copy, hashlib, importlib.util, json, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/practice-hand-batch-2/Cmaj7'
spec=importlib.util.spec_from_file_location('contact_audit',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
m=a.c.m;r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
seed_path=OUT/'seed-C-runtime.json'
seed=json.loads(seed_path.read_text())
assert hashlib.sha256((ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb').read_bytes()).hexdigest()==seed['assetSha256']==r.data['sha256']
params=np.array(seed['authoringSource']['sourceSolverParameters']);trials=[]
targets=[t for t in seed['targets'] if t['finger']!='index']
base_world=a.world_from_pose(r,seed);base_points=r.skin(base_world)
# Conservative vertex screen; selected candidates then require all-triangle audits.
for reduction in [4,7,10,14,20,30]:
 for dip_reduction in [0,5,10,15]:
  p=params.copy();p[8]-=math.radians(reduction);p[9]-=math.radians(dip_reduction)
  q=r.rotations(p);candidate=copy.deepcopy(seed)
  for segment in range(1,4):
   name=f'finger2-{segment}.L';candidate['bones'][name]['quaternion']=q[r.by_name[name]].tolist()
  world=a.world_from_pose(r,candidate);points=r.skin(world)
  wood=m.wood_depth(points);clears={}
  for string in [1,2,3]:
   clears[string]=float(m.polyline_distance(points,m.string_polyline(string,targets)).min()-m.GAUGES[string-1]/2)
  # Prefer a small natural release with >=1mm vertex clearance to all open tubes.
  deficit=sum(max(0,1-v)**2 for v in clears.values())+float((np.maximum(0,wood-.02)**2).sum())
  trials.append((deficit,reduction+dip_reduction*.25,candidate,{'pipReleaseDegrees':reduction,'dipReleaseDegrees':dip_reduction,'minimumVertexClearanceMm':clears,'woodVertices':int((wood>.02).sum()),'maximumWoodDepthMm':float(wood.max())}))
trials.sort(key=lambda t:(t[0],t[1]));_,_,candidate,metrics=trials[0]
candidate['chordId']='Cmaj7';candidate['targets']=targets;candidate['status']='needs-review';candidate['reviewed']=False
candidate['audit']={'collisionPassed':False,'contactPassed':False,'anatomyPassed':False,'multiViewReviewed':False,'metrics':metrics}
candidate['reason']={'th':'ต้นแบบ Cmaj7 ปล่อยนิ้วชี้จากสาย B รอการตรวจเมชและภาพหลายมุม','en':'Cmaj7 candidate releases the index from open B; exact mesh and multi-view review remain required.'}
candidate['authoringSource']={'seed':str(seed_path.relative_to(ROOT)),'seedSha256':hashlib.sha256(seed_path.read_bytes()).hexdigest(),'seedTransformSha256':hashlib.sha256(json.dumps({'root':seed['root'],'bones':seed['bones']},sort_keys=True,separators=(',',':')).encode()).hexdigest(),'indexChange':metrics,'musicalVoicing':'x32000','unchangedPhysicalContacts':['middle:D2','ring:A3'],'note':'Only original finger2-1/2/3 local rotations changed; wrist/root/other digits retained. No musical data edited.'}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'candidate.json').write_text(json.dumps(candidate,indent=2)+'\n')
(OUT/'screening.json').write_text(json.dumps({'selectionRule':'Minimize conservative wood/open-string vertex deficits, then angular change; not a verification gate.','trials':[t[3]|{'screeningDeficit':t[0]} for t in trials]},indent=2)+'\n')
print(json.dumps(metrics));print(OUT/'candidate.json')
