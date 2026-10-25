#!/usr/bin/env python3
"""Reframe the genuine forearm while retaining all natural-C hand joint worlds."""
import copy,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('contacts',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
r=a.c.m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');source=HERE/'C-natural-little0.json';pose=json.load(open(source));old=a.world_from_pose(r,pose)
rootmat=np.eye(4);oldrot=Rotation.from_quat(pose['root']['quaternion']).as_matrix();rootmat[:3,:3]=oldrot*1000;rootmat[:3,3]=pose['root']['positionMm'];asset=np.linalg.inv(rootmat)@old
wrist=r.by_name['wrist.L'];parent=r.parents[wrist];newrot=Rotation.from_rotvec(np.array([np.deg2rad(25),0,0])).as_matrix()@oldrot
parentrot=Rotation.from_matrix(asset[parent,:3,:3]).as_matrix();desired=Rotation.from_matrix(old[wrist,:3,:3]).as_matrix()
newwrist=Rotation.from_matrix(np.linalg.inv(parentrot)@np.linalg.inv(newrot)@desired).as_quat();newpos=old[wrist,:3,3]-newrot@asset[wrist,:3,3]*1000
p=copy.deepcopy(pose);p['root']={'positionMm':newpos.tolist(),'quaternion':Rotation.from_matrix(newrot).as_quat().tolist()};p['bones']['wrist.L']['quaternion']=newwrist.tolist()
p['authoringSource']={'file':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceSolverParameters':p.pop('solverParameters'),'wristCounterAngleDegrees':25,'note':'Source vector describes pre-counterwrist pose only. Actual root and local bone quaternions are authoritative.'}
p['audit']={'collisionPassed':False,'contactPassed':False,'anatomyPassed':False,'multiViewReviewed':False};p['status']='needs-review';p['reviewed']=False;p['reason']={'th':'ต้นแบบ C งอข้อโคนนิ้วเพิ่มและปรับแนวแขน รอการตรวจเมชและภาพจริง','en':'C prototype with increased proximal flexion and reframed forearm. Actual mesh and visual review pending.'}
new=a.world_from_pose(r,p);handids=[i for i,b in enumerate(r.bones)if not b['name'].startswith('lowerarm')]
report={'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'assetSha256':r.data['sha256'],'forearmCounterWristDegrees':25,'maxHandJointPositionDifferenceMm':float(np.linalg.norm(old[handids,:3,3]-new[handids,:3,3],axis=1).max()),'maximumHandWorldMatrixCoordinateDifference':float(abs(old[handids]-new[handids]).max()),'allReviewGatesRemainFalse':True}
(HERE/'C-natural-arm.json').write_text(json.dumps(p,indent=2)+'\n');(HERE/'C-natural-arm-reframe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
