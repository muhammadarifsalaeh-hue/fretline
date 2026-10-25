#!/usr/bin/env python3
"""One bounded C-pose forearm direction experiment, not an anatomical approval.

Keep the wrist anchor and every descendant bone world transform while rotating
its existing forearm. No new geometry and no inverse-kinematics claim are made.
The optional mesh output is in millimetres for the actual collision auditor.
"""
import json,numpy as np,hashlib
from pathlib import Path
from scipy.spatial.transform import Rotation as R
base=Path(__file__).resolve().parents[3];source=base/'docs/practice-trainer/pose-solver/C-contact-refined.json';pose=json.loads(source.read_text());rig=json.loads((base/'docs/practice-trainer/models/authoring/rig-data.json').read_text());bones=rig['boneRestData'];by={b['name']:i for i,b in enumerate(bones)};local=np.array([b['localMatrix'] for b in bones]);parents=[by.get(b['parentName'],-1) for b in bones]
for i,b in enumerate(bones):local[i,:3,:3]=R.from_quat(pose['bones'][b['name']]['quaternion']).as_matrix()*np.array(b['scale'])[None,:]
def fk(loc):
 world=np.zeros_like(loc);done=set()
 def visit(i):
  if i in done:return
  p=parents[i]
  if p<0:world[i]=loc[i]
  else:visit(p);world[i]=world[p]@loc[i]
  done.add(i)
 for i in range(len(bones)):visit(i)
 return world
w=fk(local);oldroot=R.from_quat(pose['root']['quaternion']);oldpos=np.array(pose['root']['positionMm']);wi=by['wrist.L'];pi=parents[wi];anchor=oldpos+oldroot.apply(w[wi,:3,3]*1000)
# Positive world-X tilt turns the forearm downward in the default reference view.
A=R.from_rotvec(np.array([1.,0,0])*np.radians(25));newroot=A*oldroot;parent_global=oldroot*R.from_matrix(w[pi,:3,:3]);oldwrist=R.from_quat(pose['bones']['wrist.L']['quaternion']);newwrist=parent_global.inv()*A.inv()*parent_global*oldwrist
pose['root']['quaternion']=newroot.as_quat().tolist();pose['root']['positionMm']=(anchor-newroot.apply(w[wi,:3,3]*1000)).tolist();pose['bones']['wrist.L']['quaternion']=newwrist.as_quat().tolist();local[wi,:3,:3]=newwrist.as_matrix()*np.array(bones[wi]['scale'])[None,:];after=fk(local)
# Every joint from wrist onward must retain exactly the same world transform.
hand_indices=[i for i,b in enumerate(bones) if not b['name'].startswith('lowerarm')]
G=np.eye(4);G[:3,:3]=oldroot.as_matrix();G[:3,3]=oldpos/1000;H=np.eye(4);H[:3,:3]=newroot.as_matrix();H[:3,3]=np.array(pose['root']['positionMm'])/1000
oldworld=G@w;newworld=H@after;error=float(np.max(abs(oldworld[hand_indices]-newworld[hand_indices])))
assert error<1e-6,error
pose['status']='needs-review';pose['reviewed']=False
pose['authoringSource']={'file':str(source.relative_to(base)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceSolverParameters':pose.pop('solverParameters',None),'note':'Only source parameters. Actual variant is authored by root and wrist quaternions; these source parameters do not reproduce the variant.'}
pose['audit']={'collisionPassed':False,'contactPassed':False,'anatomyPassed':False,'multiViewReviewed':False,'forearmFeasibility':{'method':'Rotate forearm/root world-X by +25 degrees; counter-rotate wrist local quaternion; preserve wrist anchor and every descendant joint world transform. Source arm mesh/weights unchanged.','sourcePoseSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'wristCounterAngleDegrees':25,'maxHandWorldMatrixDifference':error,'maxHandJointPositionDifferenceMm':float(np.max(np.linalg.norm(oldworld[hand_indices,:3,3]-newworld[hand_indices,:3,3],axis=1)))*1000,'comparisonScope':'all wrist/metacarpal/finger bones; skin vertices weighted partly to forearm may move at wrist transition'}}
pose['reason']={'th':'ต้นแบบปรับแนวแขน ยังต้องตรวจการชนและท่าข้อมือ','en':'Forearm direction prototype; collision and wrist anatomy review pending.'}
output=base/'docs/practice-trainer/pose-solver/C-arm-variant.json';output.write_text(json.dumps(pose,indent=2)+'\n');print(output,error)
positions=[];triangles=[];labels=[];differences=[]
for mesh in rig['meshes']:
 ph=np.column_stack((np.array(mesh['positions']),np.ones(len(mesh['positions']))));jointnames=mesh['skinJointNames'];joints=np.array(mesh['joints']);weights=np.array(mesh['weights']);ibm=np.array(mesh['inverseBindMatrices']);joint_bones=np.array([by[n] for n in jointnames]);bound=np.einsum('nvij,nj->nvi',ibm[joints],ph)
 oldmesh=np.einsum('nv,nvi->ni',weights,np.einsum('nvij,nvj->nvi',oldworld[joint_bones[joints]],bound))[:,:3]*1000
 newmesh=np.einsum('nv,nvi->ni',weights,np.einsum('nvij,nvj->nvi',newworld[joint_bones[joints]],bound))[:,:3]*1000
 offset=len(positions);positions.extend(newmesh.tolist());triangles.extend((np.array(mesh['indices']).reshape(-1,3)+offset).tolist());labels.extend([mesh['name']]*len(ph))
 if 'Hand' in mesh['name']:
  forearmweight=np.sum(np.where(np.isin(joints,[jointnames.index('lowerarm01.L'),jointnames.index('lowerarm02.L')]),weights,0),axis=1)
  distances=np.linalg.norm(newmesh-oldmesh,axis=1);differences=[float(distances[forearmweight==0].max()),float(distances.max())]
Path('/tmp/C-arm-variant-combined.json').write_text(json.dumps({'positions':positions,'indices':triangles,'dominantBones':labels},separators=(',',':')))
pose['audit']['forearmFeasibility'].update({'maxSkinDifferenceMmExcludingForearmWeightedTransition':differences[0],'maxWholeSkinDifferenceMm':differences[1]});output.write_text(json.dumps(pose,indent=2)+'\n');print('skin delta',differences)
