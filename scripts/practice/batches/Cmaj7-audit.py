#!/usr/bin/env python3
"""Audit actual Cmaj7 skin triangles against all six physical string paths."""
import hashlib,importlib.util,json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/practice-hand-batch-2/Cmaj7';TEMP=Path('/tmp/fretline-Cmaj7-batch');TEMP.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('contacts',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
r=a.c.m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');candidate=json.load(open(OUT/'candidate.json'))
chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORD_BY_ID}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.Cmaj7))"],cwd=ROOT))
assert chord['frets']==[None,3,2,0,0,0] and chord['fingers']==[None,3,2,None,None,None]
actual=hashlib.sha256((ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb').read_bytes()).hexdigest();assert actual==candidate['assetSha256']==r.data['sha256']
world=a.world_from_pose(r,candidate);skin=r.skin(world);tri=skin[r.triangles]
strings=[]
for s in range(1,7):
 line=a.c.m.string_polyline(s,candidate['targets']);distance=min(float(a.c.segment_triangle_distances(tri,x,y).min()) for x,y in zip(line[:-1],line[1:]));clear=distance-a.c.m.GAUGES[s-1]/2
 strings.append({'string':s,'fret':chord['frets'][6-s],'clearanceMm':clear})
meshes=[];positions=[];indices=[];labels=[]
for mesh in r.data['meshes']:
 p=r.skin_mesh(world,mesh);offset=len(positions);faces=np.array(mesh['indices']).reshape(-1,3);samples=np.vstack((p,p[faces].mean(axis=1),*(p[faces[:,i]]*.5+p[faces[:,(i+1)%3]]*.5 for i in range(3))))
 depth=a.c.m.wood_depth(samples)
 meshes.append({'mesh':mesh['name'],'sampleCount':len(samples),'interiorSamples':int((depth>.02).sum()),'maxDepthMm':float(depth.max())})
 positions.extend(p.tolist());indices.extend((np.array(mesh['indices'])+offset).tolist());labels.extend([mesh['name']]*len(p))
(TEMP/'combined-mesh.json').write_text(json.dumps({'positions':positions,'indices':indices,'dominantBones':labels}))
transform={'root':candidate['root'],'bones':candidate['bones']};report={'chordId':'Cmaj7','voicing':'x32000','sourceChordDataSha256':hashlib.sha256((ROOT/'src/features/practice/data/chords.js').read_bytes()).hexdigest(),'assetSha256':actual,'poseTransformSha256':hashlib.sha256(json.dumps(transform,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'source':'ActualexportedGLBweights+restTRS; actualsavedroot+22localbonequats','triangleCount':len(tri),'stringDistanceScope':'Analytic segment/triangle distance over ALL skin triangles, physical piecewise circular-tube paths; positive clearance is outside conservative circumscribed six-sided runtime string tube.','strings':strings,'woodSamples':meshes,'combinedMeshTransient':str(TEMP/'combined-mesh.json'),'anatomicalApproval':False}
(OUT/'contact-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
