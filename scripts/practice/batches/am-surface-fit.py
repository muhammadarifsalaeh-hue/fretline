#!/usr/bin/env python3
"""Bounded real-skin neighboring-surface IK authoring. Acceptance is separate."""
import argparse,copy,importlib.util,json,hashlib,subprocess,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('a',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);m=a.c.m
ap=argparse.ArgumentParser();ap.add_argument('--iterations',type=int,default=100);args=ap.parse_args();out=ROOT/'docs/practice-hand-batch-3/Am/surface-trial1';out.mkdir(parents=True,exist_ok=True)
seedfile=ROOT/'docs/practice-hand-batch-2/Am7/seed-C-runtime.json';seed=json.load(open(seedfile));r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json');params=np.array(seed['authoringSource']['sourceSolverParameters']);params[16:18]=np.deg2rad([25,25]);params[18:22]=np.deg2rad([0,10,15,5])
chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORD_BY_ID}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.Am))"],cwd=ROOT));assert chord['voicing']=='x02210'
targets=[]
for i,fret in enumerate(chord['frets']):
 if fret:
  s=6-i;finger=m.FINGERS[chord['fingers'][i]-1];x=m.fret_x(fret)-({'index':4,'middle':1.5,'ring':6}[finger]);z=m.string_z(s,x);targets.append({'finger':finger,'string':s,'fret':fret,'positionMm':[x,m.board_top(z)+1+m.GAUGES[s-1]+.08,z]})
baseq=Rotation.from_quat(seed['root']['quaternion']);basepos=np.array(seed['root']['positionMm']);x0=np.r_[np.zeros(6),params[6:18]]
lo=np.r_[[-70]*3,np.deg2rad([-70]*3),np.tile(np.deg2rad([0,-28,10,5]),3)];hi=np.r_[[70]*3,np.deg2rad([70]*3),np.tile(np.deg2rad([85,28,90,60]),3)];x0=np.clip(x0,lo+1e-6,hi-1e-6)
# Wider palm orientation and distributed curl seed avoids reproducing the old straight-MCP local minimum.
x0[3:6]=np.deg2rad([0,-25,10]);x0[6:]=np.deg2rad([25,10,45,25,35,-8,60,30,45,15,65,30])
dominant=r.joint_bones[r.joints[np.arange(len(r.joints)),r.weights.argmax(1)]]
ids={f:r.finger_vertex_ids[f][::4] for f in ['index','middle','ring','little']}
# Ignore the joined MCP web when treating separate fingers as independent solids.
distal={f:np.flatnonzero(np.isin(dominant,[r.by_name[f'finger{m.NUMBERS[f]}-{s}.L'] for s in (2,3)]))[::3] for f in ids}
samples=r.sample_ids;calls=0;start=time.monotonic()
def make(x):
 p=copy.deepcopy(seed);p['root']={'positionMm':(basepos+x[:3]).tolist(),'quaternion':(Rotation.from_rotvec(x[3:6])*baseq).as_quat().tolist()};pars=params.copy();pars[6:18]=x[6:];q=r.rotations(pars)
 for f in ['index','middle','ring','little']:
  for j in range(1,4):
   n=f'finger{m.NUMBERS[f]}-{j}.L';p['bones'][n]['quaternion']=q[r.by_name[n]].tolist()
 return p

def residual(x):
 global calls
 calls+=1;w=a.world_from_pose(r,make(x));pts=r.skin(w);res=[]
 for t in targets:
  cap=pts[r.patch_ids[t['finger']]].mean(0);normal=r.skin_normals(w,r.patch_ids[t['finger']]).mean(0)
  res.extend((cap-np.array(t['positionMm']))*3);res.extend((normal-[0,-1,0])*3)
 res.extend(m.wood_depth(pts[samples])*8)
 for s in chord['openStrings']:
  clearance=m.polyline_distance(pts[samples],m.string_polyline(s,targets))-m.GAUGES[s-1]/2
  res.extend(np.maximum(0,.4-clearance)*6)
 for f,g in [('index','middle'),('middle','ring'),('ring','middle'),('ring','little'),('little','ring')]:
  ref=ids[g];qry=distal[f];dist,near=cKDTree(pts[ref]).query(pts[qry]);nearest=ref[near];normal=r.skin_normals(w,nearest)
  signed=np.einsum('ij,ij->i',pts[qry]-pts[nearest],normal)
  # Conservative signed nearest-surface prior, not exact certification.
  res.extend(np.maximum(0,1.0-signed)*(dist<18)*10)
  res.extend(np.maximum(0,2.-dist)*4)
 res.extend(x[:3]*.005);res.extend(x[3:6]*.1)
 for j in range(3):
  mcp,spread,pip,dip=x[6+4*j:10+4*j];res.append((dip-.55*pip)*.5);res.append(max(0,mcp+pip+dip-np.deg2rad(160))*3)
 return np.array(res)
fit=least_squares(residual,x0,bounds=(lo,hi),max_nfev=args.iterations,ftol=1e-6,x_scale='jac',diff_step=1e-5)
p=make(fit.x);p['chordId']='Am';p['targets']=targets;p.pop('solverParameters',None);p['status']='needs-review';p['reviewed']=False;p['audit']={k:False for k in ['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed']};p['reason']={'en':'Neighbor-surface constrained IK experiment, not approved.','th':'ต้นแบบ IK จำกัดผิวระหว่างนิ้ว ยังไม่ได้รับรอง'}
p['authoringSource']={'seed':str(seedfile.relative_to(ROOT)),'seedSha256':hashlib.sha256(seedfile.read_bytes()).hexdigest(),'parameters':fit.x.tolist(),'sourceSolverParameters':params.tolist(),'evaluations':fit.nfev,'calls':calls,'cost':fit.cost,'seconds':time.monotonic()-start,'scope':'Sampled signed neighboring skin surfaces and anatomical bounds; exact skin/guitar checks remain mandatory.'};(out/'candidate.json').write_text(json.dumps(p,indent=2)+'\n');print(json.dumps(p['authoringSource']),flush=True)
