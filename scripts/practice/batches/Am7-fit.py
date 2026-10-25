#!/usr/bin/env python3
"""Relax C's unused ring finger for real Am7 x02010 without moving its contacts.

This is a repeatable actual-TRS authoring operation, never an approval gate.
Read the pinned seed, not a future changed production pose. All chord data is
loaded from the immutable central database, and its chosen fingering is asserted.
"""
import argparse, copy, hashlib, importlib.util, json, subprocess
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/practice-hand-batch-2/Am7'
spec=importlib.util.spec_from_file_location('audit_contacts',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
m=a.c.m

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ring-pip',type=float,default=25);ap.add_argument('--ring-dip',type=float,default=25)
 ap.add_argument('--output',type=Path,default=OUT/'candidate.json');ap.add_argument('--mesh',type=Path,default=Path('/tmp/Am7-batch-mesh.json'));args=ap.parse_args()
 chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORD_BY_ID}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.Am7))"],cwd=ROOT))
 assert chord['frets']==[None,0,2,0,1,0] and chord['fingers']==[None,None,2,None,1,None]
 seed_path=OUT/'seed-C-runtime.json';seed=json.loads(seed_path.read_text());pose=copy.deepcopy(seed)
 r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
 actual_asset=sha(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb')
 assert actual_asset==seed['assetSha256']==r.data['sha256']
 params=np.array(seed['authoringSource']['sourceSolverParameters']);original=params[14:18].copy();params[16:18]=np.deg2rad([args.ring_pip,args.ring_dip]);q=r.rotations(params)
 # Ring angles change only the real ring-chain rotations; the authored root,
 # counter-rotated wrist and all other digits remain byte-for-byte unchanged.
 for name in ['finger4-1.L','finger4-2.L','finger4-3.L']:
  pose['bones'][name]['quaternion']=q[r.by_name[name]].tolist()
 pose['chordId']='Am7';pose['targets']=[t for t in m.c_targets() if t['finger']!='ring']
 pose.pop('solverParameters',None)
 pose['authoringSource']={'file':str(seed_path.relative_to(ROOT)),'sha256':sha(seed_path),'sourceSolverParameters':seed['authoringSource']['sourceSolverParameters'],'note':'Seed is actual C-arm runtime TRS; sourceSolverParameters describe historical pre-counterwrist authoring only, not this saved pose. Only ring PIP/DIP are relaxed.','operation':{'ringOriginalMcpSpreadPipDipDegrees':np.rad2deg(original).tolist(),'ringNewMcpSpreadPipDipDegrees':np.rad2deg(params[14:18]).tolist()}}
 pose['status']='needs-review';pose['reviewed']=False
 pose['audit']={'collisionPassed':False,'contactPassed':False,'anatomyPassed':False,'multiViewReviewed':False}
 pose['reason']={'th':'ต้นแบบ Am7 ปรับนิ้วนางที่ไม่ใช้ให้พ้นสายเปิด รอผลตรวจเมชและภาพหลายมุม','en':'Am7 candidate relaxes the unused ring finger away from open strings. Actual mesh and multi-view review are pending.'}
 world=a.world_from_pose(r,pose);points=r.skin(world);tri=points[r.triangles]
 clear=[]
 for string in range(1,7):
  line=m.string_polyline(string,pose['targets']);value=a.c.line_clearance(tri,line,m.GAUGES[string-1]/2)
  clear.append({'string':string,'state':'muted' if chord['frets'][6-string] is None else 'open' if chord['frets'][6-string]==0 else 'fretted','minimumWholeSkinTriangleClearanceMm':value})
 positions=[];indices=[];labels=[]
 for mesh in r.data['meshes']:
  vertices=r.skin_mesh(world,mesh);offset=len(positions);positions.extend(vertices.tolist());indices.extend((np.array(mesh['indices'])+offset).tolist());labels.extend([mesh['name']]*len(vertices))
 sample=np.array(positions);faces=np.array(indices).reshape(-1,3)
 sample=np.vstack([sample,sample[faces].mean(1),*((sample[faces[:,j]]+sample[faces[:,(j+1)%3]])/2 for j in range(3))])
 depth=m.wood_depth(sample)
 # Directly establish that the actual index and middle distal flesh vertices
 # retain the geometrically audited C contacts, rather than only reusing labels.
 before=r.skin(a.world_from_pose(r,seed));contact_ids=np.r_[r.patch_ids['index'],r.patch_ids['middle']]
 delta=float(abs(points[contact_ids]-before[contact_ids]).max())
 transform={'root':pose['root'],'bones':pose['bones']}
 report={'assetSha256':actual_asset,'seedSha256':sha(seed_path),'poseTransformSha256':hashlib.sha256(json.dumps(transform,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'voicing':chord['voicing'],'fingers':chord['fingers'],'sourceChordSha256':sha(ROOT/'src/features/practice/data/chords.js'),'unchangedAssignedDistalFleshMaximumCoordinateDeltaMm':delta,'wholeSkinTriangleStringClearances':clear,'denseWoodSamples':len(sample),'woodSamplesInside':int((depth>1e-6).sum()),'maximumWoodPenetrationMm':float(depth.max()),'status':'needs-review','scope':'Whole-skin closed triangle distance to physical circumcircle string tubes and dense skin/clothing wood sampling. Exact self/guitar triangle audits and visual review remain separate.'}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(pose,indent=2)+'\n')
 (args.output.parent/'contact-report.json').write_text(json.dumps(report,indent=2)+'\n')
 args.mesh.parent.mkdir(parents=True,exist_ok=True);args.mesh.write_text(json.dumps({'positions':positions,'indices':indices,'dominantBones':labels})+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
