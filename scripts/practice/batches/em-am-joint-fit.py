#!/usr/bin/env python3
"""Bounded root plus digit actual-TRS IK; never mutates runtime or chord data."""
import argparse,copy,importlib.util,json,subprocess,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('a',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);m=a.c.m
ap=argparse.ArgumentParser();ap.add_argument('chord',choices=['Am','Em']);ap.add_argument('--iterations',type=int,default=65);ap.add_argument('--trial',type=int,default=0);args=ap.parse_args();out=ROOT/f'docs/practice-hand-batch-3/{args.chord}/joint-trial{args.trial}';out.mkdir(parents=True,exist_ok=True)
lib=json.load(open(ROOT/'src/features/practice/assets/hand-poses.json'));seed=copy.deepcopy(lib['poses']['Am7']);r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',f"import{{PRACTICE_CHORD_BY_ID}}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORD_BY_ID.{args.chord}))"],cwd=ROOT))
params=np.array(seed['authoringSource']['sourceSolverParameters']);params[16:18]=np.deg2rad([25,25]);targets=[]
for i,fret in enumerate(chord['frets']):
 if fret:
  f=m.FINGERS[chord['fingers'][i]-1];s=6-i;x=m.fret_x(fret)-4;z=m.string_z(s,x);targets.append({'finger':f,'string':s,'fret':fret,'positionMm':[x,m.board_top(z)+1+m.GAUGES[s-1],z]})
if args.chord=='Em':params[8:10]=np.deg2rad([45,25])
slots=list(range(6,18));base=seed['root'];baseq=Rotation.from_quat(base['quaternion']);basepos=np.array(base['positionMm']);x0=np.r_[np.zeros(6),params[slots]]
lo=np.r_[[-35]*3,np.deg2rad([-38]*3),np.tile(np.deg2rad([0,-40,5,0]),3)];hi=np.r_[[35]*3,np.deg2rad([38]*3),np.tile(np.deg2rad([75,40,115,85]),3)]
if args.trial:x0[3:6]=np.deg2rad(([0,15,-10],[5,-15,15],[10,0,-20])[((args.trial-1)%3)])
x0=np.clip(x0,lo+1e-5,hi-1e-5)
def make(x):
 p=copy.deepcopy(seed);p['root']={'positionMm':(basepos+x[:3]).tolist(),'quaternion':(Rotation.from_rotvec(x[3:6])*baseq).as_quat().tolist()};pars=params.copy();pars[slots]=x[6:];q=r.rotations(pars)
 for finger in ['index','middle','ring']:
  for j in range(1,4):
   name=f'finger{m.NUMBERS[finger]}-{j}.L';p['bones'][name]['quaternion']=q[r.by_name[name]].tolist()
 return p
sampleids=r.sample_ids
opens=chord['openStrings'];radius=m.GAUGES
calls=0
def residual(x):
 global calls
 world=a.world_from_pose(r,make(x));points=r.skin(world,sampleids);res=[]
 for t in targets:
  cap=r.skin(world,r.patch_ids[t['finger']]).mean(0);normal=r.skin_normals(world,r.patch_ids[t['finger']]).mean(0)
  res.extend((cap-np.array(t['positionMm']))*4);res.extend((normal-[0,-1,0])*3)
 res.extend(m.wood_depth(points)*3)
 for s in opens:
  dist=m.polyline_distance(points,m.string_polyline(s,targets))-radius[s-1]/2
  res.extend(np.maximum(0,.35-dist)*2)
 res.extend(x[:3]*.015);res.extend(x[3:6]*.1);res.extend((x[6:]-x0[6:])*.08)
 calls+=1
 return np.array(res)
fit=least_squares(residual,x0,bounds=(lo,hi),max_nfev=args.iterations,ftol=1e-7,diff_step=1e-5)
p=make(fit.x);p['chordId']=args.chord;p['targets']=targets;p['status']='needs-review';p['reviewed']=False;p['audit']={k:False for k in ['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed']};p.pop('solverParameters',None)
p['authoringSource']={'seed':'runtime Am7 @74c2076','sourceSolverParameters':params.tolist(),'fitParameters':(np.r_[params[:6],fit.x[6:],params[18:]]).tolist(),'jointRootDelta':fit.x[:6].tolist(),'jointFit':{'cost':fit.cost,'evaluations':fit.nfev,'residualCalls':calls},'note':'Actual root and bone quaternions authoritative; source params historical only.'}
(out/'candidate.json').write_text(json.dumps(p,indent=2)+'\n');print(json.dumps({'output':str(out),'cost':fit.cost,'evaluations':fit.nfev,'angles':np.rad2deg(fit.x[6:]).tolist(),'rootDelta':fit.x[:6].tolist()}),flush=True)
