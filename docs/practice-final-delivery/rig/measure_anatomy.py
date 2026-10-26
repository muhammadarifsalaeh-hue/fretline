#!/usr/bin/env python3
"""Measure actual rig frames and skin, without changing model/pose/music data.

Axis angles include abduction and source rest flexion; they are not clinical
joint flexion measurements. No numerical output here approves a teaching pose.
"""
from pathlib import Path
import hashlib,importlib.util,json,struct
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('audit_contacts',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);m=a.c.m

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unit(v):return v/np.linalg.norm(v)
def angle(x,y):return float(np.rad2deg(np.arccos(np.clip(unit(x)@unit(y),-1,1))))
def frame_measurements(r,w):
 wrist=r.by_name['wrist.L'];pre=r.by_name['lowerarm02.L'];middle=r.by_name['finger3-1.L']
 normal=unit(w[wrist,:3,:3]@np.linalg.inv(r.rest_world[wrist,:3,:3])@r.palmar)
 fingers={}
 for finger in ['index','middle','ring','little']:
  ids=[r.by_name[f'finger{m.NUMBERS[finger]}-{j}.L']for j in range(1,4)];par=r.parents[ids[0]]
  fingers[finger]={'mcpHeadMm':w[ids[0],:3,3].tolist(),'geometricAxesAngleDegrees':{'mcp':angle(w[par,:3,1],w[ids[0],:3,1]),'pip':angle(w[ids[0],:3,1],w[ids[1],:3,1]),'dip':angle(w[ids[1],:3,1],w[ids[2],:3,1])}}
 return {'wristHeadMm':w[wrist,:3,3].tolist(),'palmarWorldNormal':normal.tolist(),'forearmToPalmAxisAngleDegrees':angle(w[wrist,:3,3]-w[pre,:3,3],w[middle,:3,3]-w[wrist,:3,3]),'fingers':fingers}

def main():
 rigpath=ROOT/'docs/practice-trainer/models/authoring/rig-data.json';model=ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb';librarypath=ROOT/'src/features/practice/assets/hand-poses.json'
 r=m.Rig(rigpath);lib=json.loads(librarypath.read_text());assert digest(model)==r.data['sha256']==lib['assetSha256']
 meshes=[]
 for mesh in r.data['meshes']:
  weights=np.array(mesh['weights']);sums=weights.sum(1)
  meshes.append({'name':mesh['name'],'vertices':len(weights),'triangles':len(mesh['indices'])//3,'weightSumMinMax':[float(sums.min()),float(sums.max())],'nonfiniteWeights':int((~np.isfinite(weights)).sum()),'negativeWeights':int((weights<0).sum()),'zeroSumVertices':int((sums==0).sum()),'influencesMinMax':[int((weights>0).sum(1).min()),int((weights>0).sum(1).max())]})
 sign=[]
 for name,axis in r.flex_axes.items():
  i=r.by_name[name];R=r.rest_world[i,:3,:3];initial=R[:,1];rot=R@Rotation.from_rotvec(axis*np.deg2rad(1)).as_matrix();delta=rot[:,1]-initial
  sign.append({'bone':name,'positiveOneDegreeDirectionDotPalmar':float(delta@r.palmar),'correctCurlSign':bool(delta@r.palmar>0)})
 dom=r.joint_bones[r.joints[np.arange(len(r.joints)),r.weights.argmax(1)]];widths={}
 for finger in ['index','middle','ring','little']:
  bi=r.by_name[f'finger{m.NUMBERS[finger]}-3.L'];local=r.ph@np.linalg.inv(r.rest_world[bi]).T;ids=np.flatnonzero((dom==bi)&(local[:,1]>.007)&(local[:,1]<.017));pts=local[ids,:3]*1000
  widths[finger]={'sampleVertices':len(ids),'sliceAlongDistalBoneMm':[7,17],'spanInRestBoneFrameXYZMm':np.ptp(pts,0).tolist(),'central80PercentCrossSectionXZMm':(np.quantile(pts[:,[0,2]],.9,axis=0)-np.quantile(pts[:,[0,2]],.1,axis=0)).tolist()}
 raw=model.read_bytes();length,kind=struct.unpack_from('<II',raw,12);gltf=json.loads(raw[20:20+length])
 result={'baseline':'96e0449','assetSha256':digest(model),'rigSha256':digest(rigpath),'librarySha256':digest(librarypath),'bones':len(r.bones),'restWristHeadMeters':r.rest_world[r.by_name['wrist.L'],:3,3].tolist(),'initialBasisDeterminant':float(np.linalg.det(r.initial_rot)),'sourcePalmarNormal':r.palmar.tolist(),'meshes':meshes,'oneDegreeCurlSignChecks':sign,'rest':frame_measurements(r,r.rest_world* np.array([[1,1,1,1000],[1,1,1,1000],[1,1,1,1000],[1,1,1,1]])),'runtime':{key:frame_measurements(r,a.world_from_pose(r,lib['poses'][key]))for key in ['C','Dm','Em7','E7','Fmaj7']},'distalWidths':widths,'gltfMaterials':gltf.get('materials',[]),'gltfExtensionsUsed':gltf.get('extensionsUsed',[]),'noAnatomicalApproval':True,'scope':'Actual exported weights/rest frames/current saved TRS. Axis angles include spread and source rest bend; no clinical, collision, pressure or physical iPad certification.'}
 target=Path(__file__).with_name('measurements.json');target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'report':str(target.relative_to(ROOT)),'bones':len(r.bones),'curlSignsAllCorrect':all(x['correctCurlSign']for x in sign),'weightsFinite':all(x['nonfiniteWeights']==0 for x in meshes),'modelUnchanged':True}))
if __name__=='__main__':main()
