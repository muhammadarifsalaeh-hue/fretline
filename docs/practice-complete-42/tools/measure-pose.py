"""Read-only actual-skin support witnesses and geometric joint angles.
These plausibility measurements do not certify anatomy or teaching accuracy.
"""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v4.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
class Measurements:
 def __init__(self):
  self.context=f.load_context();self.rig=self.context['rig'];file=ROOT/'.local-preview/practice-complete-42/reference-guitar.json'
  if not file.exists():subprocess.run(['node',str(Path(__file__).with_name('export-guitar.mjs')),'C',str(file)],cwd=ROOT,check=True)
  guitar=json.loads(file.read_text());indices=np.array(guitar['indices']).reshape(-1,3);labels=np.array(guitar['dominantBones']);self.back=np.array(guitar['positions'])[indices[np.all(labels[indices]=='d-section-neck-back',axis=1)]]
 def measure(self,pose):
  r=self.rig;world=f.a.world_from_pose(r,pose);points=r.skin(world);thumb=points[self.context['faces']['thumb','barre']];query=np.vstack([thumb.mean(1),thumb.reshape(-1,3)]);chord=self.context['chords'][pose['chordId']];max_x=f.m.fret_x(max(t['fret']for t in f.effective_contacts(chord)))+5;query=query[(query[:,0]>=0)&(query[:,0]<=max_x)&(query[:,1]<-3)]
  witness=None;distance=None
  if len(query):
   near,_,signed=f.nearest_surface(query,self.back,k=min(64,len(self.back)));eligible=np.flatnonzero(near[:,0]>=0);i=int(eligible[np.argmin(abs(signed[eligible]))]) if len(eligible) else None;distance=float(abs(signed[i])) if i is not None else None;witness={'palmarSkinPointMm':query[i].tolist(),'neckBackPointMm':near[i].tolist(),'distanceMm':distance} if i is not None else None
  joints={}
  for finger in f.m.FINGERS:
   vectors=[]
   for segment in range(1,4):
    i=r.by_name[f'finger{f.m.NUMBERS[finger]}-{segment}.L'];v=np.array(r.bones[i]['tailWorldMeters'])-np.array(r.bones[i]['headWorldMeters']);v=np.linalg.inv(r.rest_world[i][:3,:3])@v;v=world[i][:3,:3]@v;vectors.append(v/np.linalg.norm(v))
   joints[finger]={'PIPDegrees':float(np.degrees(np.arccos(np.clip(vectors[0]@vectors[1],-1,1)))),'DIPDegrees':float(np.degrees(np.arccos(np.clip(vectors[1]@vectors[2],-1,1))))}
  joint_ok=all(v['PIPDegrees']<=115 and v['DIPDegrees']<=90 for v in joints.values())
  return {'id':pose['chordId'],'supportRegion':'actual-neck-back-at-or-after-nut','thumbSupportWitness':witness,'thumbSupportPassed':distance is not None and distance<=.8,'jointAngles':joints,'jointPlausibilityPassed':joint_ok,'independentTeachingApproval':False}
