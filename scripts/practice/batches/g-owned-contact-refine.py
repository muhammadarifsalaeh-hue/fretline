#!/usr/bin/env python3
"""One bounded G refinement: real owned palmar triangles and all runtime strings."""
import argparse,copy,hashlib,importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('gate',ROOT/'scripts/practice/check-hand-geometry.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);a=g.a;m=a.c.m
out=ROOT/'docs/practice-hand-batch-3/G';source=out/'bounded-signed-2.json';seed=json.loads(source.read_text());seed['root']['positionMm'][1]+=1.5;r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');params=np.array(seed['solverParameters']);records=[]
subprocess.run(['node',str(ROOT/'scripts/practice/export-guitar-collision-mesh.mjs'),'G','/tmp/G-owned-guitar.json'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);guitar=json.load(open('/tmp/G-owned-guitar.json'));strings={s['number']:s for s in guitar['strings']}
dom=r.joint_bones[r.joints[np.arange(len(r.joints)),r.weights.argmax(1)]];palmar=r.normals[r.triangles].mean(1)@r.palmar>.05
for finger,string,fret in [('index',5,2),('middle',6,3),('ring',1,3)]:
 num=m.NUMBERS[finger];bn=[r.by_name[f'finger{num}-{j}.L'] for j in range(1,4)];owned=np.isin(dom[r.triangles],bn).all(1)&palmar&(dom[r.triangles]==bn[-1]).any(1);faces=r.triangles[owned];slot=slice(6+4*m.FINGERS.index(finger),10+4*m.FINGERS.index(finger));q0=params[slot].copy();before=r.skin(a.world_from_pose(r,seed));cap0=before[r.patch_ids[finger]].mean(0);wire=m.fret_x(fret);st=strings[string];segments=g.clip_line(np.array(st['controlPointsMm']),wire-6,wire-1.1);contactx=wire-4;contactz=m.string_z(string,contactx);contacty=m.board_top(contactz)+1+m.GAUGES[string-1]+.025
 def make(q):
  p=copy.deepcopy(seed);pars=params.copy();pars[slot]=q;rots=r.rotations(pars)
  for j in range(1,4):
   n=f'finger{num}-{j}.L';p['bones'][n]['quaternion']=rots[r.by_name[n]].tolist()
  return p
 def lower(v):
  tri=v[faces];A=tri[:,1][:,[0,2]]-tri[:,0][:,[0,2]];B=tri[:,2][:,[0,2]]-tri[:,0][:,[0,2]];C=np.array([contactx,contactz])-tri[:,0][:,[0,2]];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];u=np.divide(C[:,0]*B[:,1]-C[:,1]*B[:,0],det,out=np.zeros(len(det)),where=abs(det)>1e-9);w=np.divide(A[:,0]*C[:,1]-A[:,1]*C[:,0],det,out=np.zeros(len(det)),where=abs(det)>1e-9);valid=(abs(det)>1e-9)&(u>=0)&(w>=0)&(u+w<=1);ys=tri[:,0,1]+u*(tri[:,1,1]-tri[:,0,1])+w*(tri[:,2,1]-tri[:,0,1]);return float(ys[valid].min()) if valid.any() else float(v[r.patch_ids[finger]].mean(0)[1])
 ids=r.finger_vertex_ids[finger];wholefaces=r.finger_triangles[finger]
 def residual(q,lift=False):
  p=make(q);v=r.skin(a.world_from_pose(r,p));cap=v[r.patch_ids[finger]].mean(0);o=list((cap[[0,2]]-cap0[[0,2]])*.3)
  if lift:o.append((lower(v)-contacty-.35)*20)
  else:o.append((g.clearance(v[faces],segments,st['radiusMm'])-.012)*30)
  o.extend((q-q0)*.1);o.extend(m.wood_depth(v[ids])*8)
  # Every actual runtime string participates, including strings assigned to
  # another digit. Whole-finger triangle distance remains a conservative
  # unsigned prior; the final exact mesh checker must reject any crossing.
  if not lift:
   tri=v[wholefaces]
   for no,line in strings.items():
    points=np.array(line['controlPointsMm']);clear=g.clearance(tri,list(zip(points[:-1],points[1:])),line['radiusMm']);o.append(max(0,.004-clear)*20)
  return np.array(o)
 bounds=(q0-np.deg2rad(3),q0+np.deg2rad(3));lift=least_squares(lambda q:residual(q,True),q0,bounds=bounds,max_nfev=22,diff_step=1e-5,ftol=1e-8)
 fit=least_squares(residual,lift.x,bounds=bounds,max_nfev=32,diff_step=1e-5,ftol=1e-9)
 seed=make(fit.x);params[slot]=fit.x;after=r.skin(a.world_from_pose(r,seed));records.append({'finger':finger,'string':string,'fret':fret,'ownedPalmarClearanceBeforeMm':g.clearance(before[faces],segments,st['radiusMm']),'ownedPalmarClearanceAfterMm':g.clearance(after[faces],segments,st['radiusMm']),'deltaDegrees':np.rad2deg(fit.x-q0).tolist(),'evaluations':[lift.nfev,fit.nfev]});print(json.dumps(records[-1]),flush=True)
seed.pop('solverParameters',None);seed['authoringSource']={'file':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rootLiftMm':1.5,'method':'One bounded3degree/dof refinement of actual assigned-owner palmar triangles; every runtime string participates; exact acceptance unchanged','script':'scripts/practice/batches/g-owned-contact-refine.py','records':records}
(out/'owned-contact-trial1.json').write_text(json.dumps(seed,indent=2)+'\n');lib=json.load(open(ROOT/'src/features/practice/assets/hand-poses.json'));lib['poses']['G']=seed;(out/'owned-contact-trial1-library.json').write_text(json.dumps(lib))
