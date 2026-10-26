#!/usr/bin/env python3
"""Bounded D/G real-skin IK experiment; never changes musical/runtime files.

Only an authoring candidate: exact combined-mesh and contact audit is mandatory.
Keeps audited C thumb/little local rotations, a strict bounded finger prior and
actual flesh barycentric contacts, rather than arbitrary bone-end targets.
"""
import argparse, copy, hashlib, importlib.util, json, subprocess, time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('audit_contacts',ROOT/'docs/practice-trainer/pose-solver/audit_c_contacts.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);m=a.c.m

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('chord',choices=['D','G']);ap.add_argument('--evaluations',type=int,default=85)
 ap.add_argument('--seed',type=Path);ap.add_argument('--label',default='bounded-1');ap.add_argument('--signed',action='store_true');args=ap.parse_args()
 out=ROOT/'docs/practice-hand-batch-3'/args.chord;out.mkdir(parents=True,exist_ok=True)
 r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
 lib=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text())
 seedpath=args.seed or ROOT/'docs/practice-hand-batch-2/presentation/C-natural-little0.json'
 seed=json.loads(seedpath.read_text());original=np.array(seed['solverParameters'])
 assert sha(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb')==r.data['sha256']==seed['assetSha256']
 chord=json.loads(subprocess.check_output(['node','--input-type=module','-e',f"import{{PRACTICE_CHORD_BY_ID as c}}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(c.{args.chord}))"],cwd=ROOT))
 targets=[]
 for i,fret in enumerate(chord['frets']):
  if fret:
   finger=['index','middle','ring','little'][chord['fingers'][i]-1];s=6-i;x=m.fret_x(fret)-4;z=m.string_z(s,x)
   targets.append({'finger':finger,'string':s,'fret':fret,'positionMm':[x,m.board_top(z)+1+m.GAUGES[s-1]+.033,z]})
 targets.sort(key=lambda t:m.FINGERS.index(t['finger']))
 contact_report=json.loads((ROOT/'docs/practice-hand-batch-2/presentation/C-natural-arm-clearances.json').read_text())
 bindings={f:next(s for s in contact_report['strings']if s['string']==num)for f,num in[('index',2),('middle',4),('ring',5)]}
 ids=[np.array(bindings[t['finger']]['triangleVertexIndices'])for t in targets]
 barys=[np.array(bindings[t['finger']]['barycentric'])for t in targets]
 expected=[np.array(t['positionMm'])for t in targets]
 samples=np.unique(np.r_[np.arange(0,len(r.positions),8),*ids])
 finger_samples={f:vs[::4]for f,vs in r.finger_vertex_ids.items()if f!='thumb'}
 slots=np.r_[np.arange(6),np.arange(6,18)].astype(int)
 lo=original[slots].copy();hi=lo.copy();lo[:3]=[-45,-100,-145];hi[:3]=[170,20,-40]
 lo[3:6]=original[3:6]-np.deg2rad(55);hi[3:6]=original[3:6]+np.deg2rad(55)
 for i in range(3):lo[6+4*i:10+4*i]=np.deg2rad([0,-28,5,0]);hi[6+4*i:10+4*i]=np.deg2rad([70,28,100,70])
 start=np.clip(original[slots],lo+1e-8,hi-1e-8);calls=0;begin=time.monotonic()
 def residual(v):
  nonlocal calls
  calls+=1;p=original.copy();p[slots]=v;w,*_=r.fk(p);pts=r.skin(w);o=[]
  for vi,b,target,f in zip(ids,barys,expected,[t['finger']for t in targets]):
   point=b@pts[vi];normal=b@r.skin_normals(w,vi)
   o.extend((point-target)*5);o.extend((normal-[0,-1,0])*1.5)
  sp=pts[samples];o.extend(m.wood_depth(sp)*8)
  for s in range(1,7):
   margin=.38 if chord['frets'][6-s]==0 else .03
   dist=m.polyline_distance(sp,m.string_polyline(s,targets))-m.GAUGES[s-1]/2
   o.extend(np.maximum(0,margin-dist)*5)
  # Conservative surface proximity prior for separate digit meshes. It is
  # not an intersection proof; the exact post-fit audit remains authoritative.
  for f,g in [('index','middle'),('middle','ring'),('ring','little'),('index','ring')]:
   tree=cKDTree(pts[finger_samples[g]]);dist,nearest=tree.query(pts[finger_samples[f]])
   o.extend(np.maximum(0,1.8-dist)*3)
   if args.signed:
    nearest_ids=finger_samples[g][nearest];normals=r.skin_normals(w,nearest_ids)
    sign=np.einsum('ij,ij->i',pts[finger_samples[f]]-pts[nearest_ids],normals)
    o.extend(np.maximum(0,1.-sign)*(dist<10)*12)
  o.extend((p[:3]-original[:3])*.002);o.extend((p[3:6]-original[3:6])*.15)
  for i in range(3):
   q=p[6+4*i:10+4*i];o.append((q[3]-q[2]*.55)*.5);o.append(q[1]*1.5);o.append(max(0,q[0]+q[2]+q[3]-np.deg2rad(160))*4)
  return np.array(o)
 result=least_squares(residual,start,bounds=(lo,hi),max_nfev=args.evaluations,x_scale='jac',ftol=1e-7,xtol=1e-7,gtol=1e-7)
 p=original.copy();p[slots]=result.x;w,q,rootrot=r.fk(p)
 pose=copy.deepcopy(seed);pose.update({'chordId':args.chord,'root':{'positionMm':p[:3].tolist(),'quaternion':Rotation.from_matrix(rootrot).as_quat().tolist()},'bones':{b['name']:{'quaternion':q[i].tolist()}for i,b in enumerate(r.bones)},'solverParameters':p.tolist(),'targets':targets,'status':'needs-review','reviewed':False,'audit':{'collisionPassed':False,'contactPassed':False,'anatomyPassed':False,'multiViewReviewed':False},'reason':{'en':'Bounded real-skin IK candidate; exact collision/contact and independent anatomy review pending.','th':'ต้นแบบ IK บนผิวมือจริง ยังรอการตรวจเมชและท่าจับหลายมุม'}})
 pose['authoringSource']={'file':str(seedpath.relative_to(ROOT)),'sha256':sha(seedpath),'script':'scripts/practice/batches/d-g-fit.py','note':'Actual saved TRS and solver vector agree; C thumb/little fixed. No musical data changed.'}
 pts=r.skin(w);summary={'chord':args.chord,'voicing':chord['voicing'],'seedSha256':sha(seedpath),'assetSha256':r.data['sha256'],'sourceChordSha256':sha(ROOT/'src/features/practice/data/chords.js'),'evaluations':result.nfev,'residualCalls':calls,'seconds':time.monotonic()-begin,'optimizerSuccess':bool(result.success),'cost':float(result.cost),'termination':result.message,'anchorErrorsMm':[float(np.linalg.norm(b@pts[vi]-target))for vi,b,target in zip(ids,barys,expected)],'anglesRestRelativeDegrees':{f:np.rad2deg(p[6+4*i:10+4*i]).tolist()for i,f in enumerate(m.FINGERS)},'scope':'Barycentric real skin anchors; sampled collision priors only. Exact audit not yet run.','status':'needs-review'}
 (out/(args.label+'.json')).write_text(json.dumps(pose,indent=2)+'\n');(out/(args.label+'-fit.json')).write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
