#!/usr/bin/env python3
"""Actual exported anatomy measurements; no model/pose mutation or approval."""
import importlib.util,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('contacts',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
r=a.c.m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
posefile=ROOT/'docs/practice-trainer/pose-solver/C-arm-variant.json';pose=json.load(open(posefile));w=a.world_from_pose(r,pose)
def norm(x):return x/np.linalg.norm(x)
def flex_angle(parent,child,palmar):
 axis=norm(np.cross(parent,palmar));p=norm(parent-axis*np.dot(parent,axis));q=norm(child-axis*np.dot(child,axis))
 return float(np.rad2deg(np.arctan2(np.dot(axis,np.cross(p,q)),np.dot(p,q))))
def angle(p,q):return float(np.rad2deg(np.arccos(np.clip(np.dot(norm(p),norm(q)),-1,1))))
restpalm=r.palmar;wrist=r.by_name['wrist.L'];posedpalm=norm(w[wrist,:3,:3]@np.linalg.inv(r.rest_world[wrist,:3,:3])@restpalm)
rows=[]
for finger,num in [('index',2),('middle',3),('ring',4),('little',5)]:
 names=[f'finger{num}-{i}.L'for i in range(1,4)];ids=[r.by_name[n]for n in names];meta=r.parents[ids[0]]
 lengths=[np.linalg.norm(np.array(r.bones[i]['tailWorldMeters'])-np.array(r.bones[i]['headWorldMeters']))*1000 for i in ids]
 mcp=np.array(r.bones[ids[0]]['headWorldMeters'])*1000
 rows.append({'finger':finger,'boneLengthsMm':lengths,'sumMcpToTipBoneLengthsMm':sum(lengths),'wristToMcpDistanceMm':float(np.linalg.norm(mcp)),
  'restMcpProjectedFlexDegrees':flex_angle(r.rest_world[meta,:3,1],r.rest_world[ids[0],:3,1],restpalm),
  'posedMcpProjectedFlexDegrees':flex_angle(w[meta,:3,1],w[ids[0],:3,1],posedpalm),
  'restAngleBetweenCarpalAndProximalDegrees':angle(r.rest_world[meta,:3,1],r.rest_world[ids[0],:3,1]),
  'posedAngleBetweenCarpalAndProximalDegrees':angle(w[meta,:3,1],w[ids[0],:3,1]),
  'posedPipRelativeSegmentBendDegrees':angle(w[ids[0],:3,1],w[ids[1],:3,1]),
  'posedDipRelativeSegmentBendDegrees':angle(w[ids[1],:3,1],w[ids[2],:3,1])})
points=r.positions*1000;forward=r.forward
palmforward=points@forward;bodyprojs=np.r_[palmforward[r.finger_vertex_ids['middle']],palmforward[r.finger_vertex_ids['index']]]
report={'assetSha256':r.data['sha256'],'sourcePose':str(posefile.relative_to(ROOT)),'sourcePoseSha256':hashlib.sha256(posefile.read_bytes()).hexdigest(),'unit':'mm and degrees','fingers':rows,'mostDistalSkinProjectionFromWristMm':float(bodyprojs.max()),'wholeMeshDimensionsMm':np.ptp(points,axis=0).tolist(),'forearmCutExists':True,
 'limitations':['Authoring parameters are deltas from exported rest rotations, not clinical/anatomical zero angles.','Bone-axis measurements are proxy joint angles; no medical or ergonomic acceptance is inferred.','Native Blender source contains cropped forearm only. Original complete body/shirt inputs are not present locally.']}
Path(__file__).with_name('measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
