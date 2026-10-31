"""Bounded per-joint skin polish with interval contacts and exact crossing evidence.
This optimizer authors candidates only. Full original post-audit remains required.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)

def polish(context,chord,seed,folder,evidence,digits=None,bound=8,seconds=100,lift_start=.6):
 folder.mkdir(parents=True,exist_ok=True);r=context['rig'];a=f.a;m=f.m;guitar=f.previous.runtime_guitar(chord,folder);lines={v['number']:v for v in guitar['strings']};contacts=f.gate.contacts(chord)
 fingers=digits or [m.FINGERS[n-1]for n in sorted({t['finger']for t in contacts})];names=[f'finger{m.NUMBERS[d]}-{j}.L'for d in fingers for j in range(1,4)]
 base=np.array([Rotation.from_quat(seed['bones'][b['name']]['quaternion']).as_matrix()for b in r.bones]);scales=np.array([b['scale']for b in r.bones]);local=r.rest_local.copy();root=np.eye(4);root[:3,:3]=Rotation.from_quat(seed['root']['quaternion']).as_matrix()*1000;root[:3,3]=seed['root']['positionMm'];order=[]
 def visit(i):
  if i in order:return
  if r.parents[i]>=0:visit(r.parents[i])
  order.append(i)
 for i in range(len(r.bones)):visit(i)
 def world(x):
  rot=base.copy()
  for i,name in enumerate(names):rot[r.by_name[name]]=base[r.by_name[name]]@Rotation.from_rotvec(x[1+i*3:1+i*3+3]).as_matrix()
  l=local.copy();l[:,:3,:3]=rot*scales[:,None,:];w=np.empty_like(l)
  for i in order:w[i]=w[r.parents[i]]@l[i]if r.parents[i]>=0 else l[i]
  outer=root.copy();outer[1,3]+=x[0];return outer@w,rot,outer
 x0=np.zeros(1+3*len(names));x0[0]=lift_start;seed_world,_,_=world(x0);seed_points=r.skin(seed_world);tri=seed_points[r.triangles];cent=tri.mean(1);radius=np.linalg.norm(tri-cent[:,None,:],axis=2).max(1)
 near={n:r.triangles[m.polyline_distance(cent,np.array(line['controlPointsMm']))<=radius+18]for n,line in lines.items()}
 for n in near:
  if not len(near[n]):near[n]=r.triangles[np.argsort(m.polyline_distance(cent,np.array(lines[n]['controlPointsMm']))-radius)[:64]]
 with(gzip.open(evidence,'rt')if str(evidence).endswith('.gz')else open(evidence))as stream:raw=json.load(stream)
 assert raw['poseTransformSha256']==f.gate.transform_hash(seed)
 self_ids=np.array([p['vertices']for p in raw['self']['pairs']],dtype=int);guitar_ids=np.array([p['vertices']for p in raw.get('guitar',{}).get('pairs',[])],dtype=int);guitar_points=np.array(guitar['positions']);total=sum(len(v['positions'])for v in r.data['meshes'])
 if len(guitar_ids):guitar_ids[:,1]-=total;assert guitar_ids[:,1].min()>=0
 started=time.monotonic();calls=0;iterations=0
 def residual(x):
  nonlocal calls
  calls+=1;w,_,_=world(x);points=r.skin(w);tri=points[r.triangles];sample=np.vstack([points,tri.mean(1),*(tri[:,i]*.5+tri[:,(i+1)%3]*.5 for i in range(3))]);res=[m.wood_depth(sample)*65]
  for t in contacts:
   finger=m.FINGERS[t['finger']-1];faces=context['faces'][finger,'barre'if t['kind']=='barre'else'tip'];line=lines[t['string']];wire=m.fret_x(t['fret']);value=f.gate.clearance(points[faces],f.gate.clip_line(np.array(line['controlPointsMm']),wire-6,wire-1.1),line['radiusMm']);res.append(np.array([max(0,.025-value)*100,max(0,value-.095)*100]))
  for n,line in lines.items():
   pts=np.array(line['controlPointsMm']);value=f.gate.clearance(points[near[n]],list(zip(pts[:-1],pts[1:])),line['radiusMm']);margin=.24 if chord['frets'][6-n]==0 else .008;res.append(np.array([max(0,margin-value)*100]))
  if len(self_ids)or len(guitar_ids):
   combined=np.vstack([points if mesh is r.mesh else r.skin_mesh(w,mesh)for mesh in r.data['meshes']])
   if len(self_ids):res.append(np.maximum(0,.04-f.triangle_gaps(combined[self_ids[:,0]],combined[self_ids[:,1]]))*100)
   if len(guitar_ids):res.append(np.maximum(0,.03-f.triangle_gaps(combined[guitar_ids[:,0]],guitar_points[guitar_ids[:,1]]))*100)
  res.append(x[1:]*.03);res.append(x[:1]*.002)
  return np.concatenate(res)
 def callback(intermediate_result):
  nonlocal iterations
  iterations+=1
  if iterations%5==0:print(json.dumps({'id':chord['id'],'iteration':iterations,'cost':float(intermediate_result.cost),'seconds':time.monotonic()-started}),flush=True)
  if time.monotonic()-started>seconds or intermediate_result.cost<.0001:raise StopIteration
 lo=np.r_[-1.5,np.full(len(x0)-1,-np.deg2rad(bound))];hi=-lo
 from scipy.optimize._numdiff import approx_derivative
 steps=np.r_[.001,np.full(len(x0)-1,1e-4)]
 jac=lambda x:approx_derivative(residual,x,method='3-point',abs_step=steps,bounds=(lo,hi))
 result=least_squares(residual,x0,jac=jac,bounds=(lo,hi),max_nfev=150,x_scale='jac',ftol=1e-10,xtol=1e-10,gtol=1e-10,callback=callback)
 w,rot,outer=world(result.x);p=copy.deepcopy(seed);p['root']['positionMm']=outer[:3,3].tolist()
 for name in names:p['bones'][name]['quaternion']=Rotation.from_matrix(rot[r.by_name[name]]).as_quat().tolist()
 p['audit']={k:False for k in f.previous.GATES};p['status']='needs-review';p['reviewed']=False;p.pop('solverParameters',None)
 metrics={'id':chord['id'],'fingers':fingers,'cost':float(result.cost),'evaluations':result.nfev,'calls':calls,'seconds':time.monotonic()-started,'maximumJointDeltaDegrees':float(np.max(abs(np.rad2deg(result.x[1:])))),'rootVerticalShiftMm':float(result.x[0]),'notAnAcceptanceGate':True}
 p['authoringSource']={'method':'Small bounded local joint rotations, actual owned palmar contact intervals and exact crossing-pair constraints','seedTransformSHA256':f.gate.transform_hash(seed),'solverSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'deltaJointRotationVectors':result.x.tolist(),'metrics':metrics};(folder/'candidate.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');(folder/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics),flush=True);return p
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--seed',required=True,type=Path);ap.add_argument('--evidence',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--digits');ap.add_argument('--bound',type=float,default=8);ap.add_argument('--seconds',type=int,default=100);ap.add_argument('--lift-start',type=float,default=.6);args=ap.parse_args();context=f.load_context();seed=json.loads(args.seed.read_text());p=polish(context,context['chords'][seed['chordId']],seed,args.out,args.evidence,args.digits.split(',')if args.digits else None,args.bound,args.seconds,args.lift_start);lib=copy.deepcopy(context['library']);lib['poses'][p['chordId']]=p;(args.out/'proposal-library.json').write_text(f.previous.frozen_json(lib))
