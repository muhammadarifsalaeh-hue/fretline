#!/usr/bin/env python3
"""Fixed-root-lift then constrained real flesh/string contact fit for Dsus2."""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('a',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.c.m
ap=argparse.ArgumentParser();ap.add_argument('--lift',type=float,default=2);args=ap.parse_args()
folder=ROOT/'docs/practice-hand-batch-3/Dsus2';source=folder/'bounded-signed-1.json';seed=json.loads(source.read_text());seed['root']['positionMm'][1]+=args.lift;r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');params=np.array(seed['solverParameters']);records=[]
for finger,string in [('index',3),('ring',2)]:
 slot=slice(6+4*m.FINGERS.index(finger),10+4*m.FINGERS.index(finger));q0=params[slot].copy();cap0=r.skin(a.world_from_pose(r,seed),r.patch_ids[finger]).mean(0);line=m.string_polyline(string,seed['targets']);radius=m.GAUGES[string-1]/2
 def make(q):
  p=copy.deepcopy(seed);current=params.copy();current[slot]=q;rots=r.rotations(current)
  for j in range(1,4):
   n=f'finger{m.NUMBERS[finger]}-{j}.L';p['bones'][n]['quaternion']=rots[r.by_name[n]].tolist()
  return p
 def residual(q):
  p=make(q);v=r.skin(a.world_from_pose(r,p));cap=v[r.patch_ids[finger]].mean(0);clear=a.c.line_clearance(v[r.finger_triangles[finger]],line,radius)
  return np.r_[(cap[[0,2]]-cap0[[0,2]])*.4,(clear-.012)*30,(q-q0)*.08,m.wood_depth(v[r.finger_vertex_ids[finger]])*4]
 before=a.c.line_clearance(r.skin(a.world_from_pose(r,seed))[r.finger_triangles[finger]],line,radius)
 fit=least_squares(residual,q0,bounds=(q0-np.deg2rad(8),q0+np.deg2rad(8)),max_nfev=75,ftol=1e-10,xtol=1e-10,gtol=1e-10,diff_step=1e-5)
 seed=make(fit.x);params[slot]=fit.x;after=a.c.line_clearance(r.skin(a.world_from_pose(r,seed))[r.finger_triangles[finger]],line,radius);records.append({'finger':finger,'before':before,'after':after,'deltaDegrees':np.rad2deg(fit.x-q0).tolist(),'evaluations':fit.nfev})
seed.pop('solverParameters',None);seed['authoringSource']={'file':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'rootYlift then real triangle clearance constrained per-digit local IK','liftMm':args.lift,'contactRefinements':records,'script':'scripts/practice/batches/d-suspended-contact.py'}
name='contact-lift-'+str(args.lift);(folder/(name+'.json')).write_text(json.dumps(seed,indent=2)+'\n');lib=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());lib['poses']['Dsus2']=seed;(folder/(name+'-library.json')).write_text(json.dumps(lib));print(json.dumps(records),flush=True)
