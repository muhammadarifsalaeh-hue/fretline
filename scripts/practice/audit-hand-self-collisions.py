#!/usr/bin/env python3
"""Find nonadjacent skinned triangle crossings in review-only hand candidates.

This is a rejection diagnostic. A runtime pose includes skin; --mesh can also
include the garment. Coplanar interior overlaps are checked separately.
"""
import argparse, importlib.util, json, numpy as np, collections
from pathlib import Path
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('candidate');ap.add_argument('--output');ap.add_argument('--mesh',action='store_true',help='Read arbitrary positions/indices mesh JSON instead of a runtime pose');ap.add_argument('--against',help='Test only crossings against a second positions/indices mesh JSON');ap.add_argument('--rig',default=str(ROOT/'docs/practice-trainer/models/authoring/rig-data.json'));args=ap.parse_args()
spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/practice/solve-hand-poses.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
d=json.load(open(args.candidate))
if args.mesh:
 p=np.array(d['positions']);tri=np.array(d['indices'],dtype=int).reshape(-1,3);labels=np.array(d.get('dominantBones',['unknown']*len(p)))
else:
 r=m.Rig(args.rig);local=r.rest_local.copy()
 for i,b in enumerate(r.bones):local[i,:3,:3]=Rotation.from_quat(d['bones'][b['name']]['quaternion']).as_matrix()*np.array(b['scale'])[None,:]
 w=np.zeros_like(local);done=set()
 def visit(i):
  if i in done:return
  parent=r.parents[i]
  if parent>=0:visit(parent);w[i]=w[parent]@local[i]
  else:w[i]=local[i]
  done.add(i)
 for i in range(len(w)):visit(i)
 root=np.eye(4);root[:3,:3]=Rotation.from_quat(d['root']['quaternion']).as_matrix()*1000;root[:3,3]=d['root']['positionMm'];w=root@w
 p=r.skin(w);tri=r.triangles;dom=r.joint_bones[r.joints[np.arange(len(r.joints)),r.weights.argmax(1)]];names=np.array([b['name'] for b in r.bones]);labels=names[dom]
triangle_groups=np.zeros(len(tri),dtype=int)
if args.against:
 other=json.load(open(args.against));other_p=np.array(other['positions']);other_tri=np.array(other['indices'],dtype=int).reshape(-1,3)
 triangle_groups=np.r_[triangle_groups,np.ones(len(other_tri),dtype=int)]
 labels=np.r_[labels,np.array(other.get('dominantBones',['obstacle']*len(other_p)))]
 tri=np.vstack((tri,other_tri+len(p)));p=np.vstack((p,other_p))
# Normalize numerical tolerances so native metre meshes and runtime millimetre
# meshes receive the same geometric test. Uniform scaling preserves crossings.
input_centres=p[tri].mean(axis=1)
p=p*(100/max(float(np.ptp(p,axis=0).max()),1e-12))
tp=p[tri];cent=tp.mean(1)
rad=np.linalg.norm(tp-cent[:,None,:],axis=2).max(1);tree=cKDTree(cent);boxlo=tp.min(1);boxhi=tp.max(1);pairs=[]
for i in range(len(tri)):
 if args.against and triangle_groups[i]==1:continue
 j=np.asarray(tree.query_ball_point(cent[i],rad[i]+rad.max()),dtype=int);j=j[j>i]
 if not len(j):continue
 j=j[np.all(boxlo[i]<=boxhi[j]+1e-7,axis=1)&np.all(boxhi[i]>=boxlo[j]-1e-7,axis=1)]
 if args.against:j=j[triangle_groups[i]!=triangle_groups[j]]
 if not len(j):continue
 j=j[~(tri[i,None,:,None]==tri[j,None,:]).any(axis=(1,2))]
 if len(j):pairs.extend((i,int(k)) for k in j)
a=np.array(pairs,dtype=int).reshape(-1,2);P=tp[a[:,0]];Q=tp[a[:,1]]
def intersect(A,B,C,D,E):
 direction=B-A;e1=D-C;e2=E-C;h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h);mask=abs(det)>1e-10;inv=np.divide(1.,det,out=np.zeros_like(det),where=mask);v=A-C;u=np.einsum('ij,ij->i',v,h)*inv;q=np.cross(v,e1);z=np.einsum('ij,ij->i',direction,q)*inv;t=np.einsum('ij,ij->i',e2,q)*inv
 return mask&(u>1e-6)&(z>1e-6)&(u+z<1-1e-6)&(t>1e-6)&(t<1-1e-6)
mask=np.zeros(len(a),bool)
for k in range(3):mask|=intersect(P[:,k],P[:,(k+1)%3],Q[:,0],Q[:,1],Q[:,2]);mask|=intersect(Q[:,k],Q[:,(k+1)%3],P[:,0],P[:,1],P[:,2])
coplanar=np.zeros(len(a),bool)
def area(poly):
 if len(poly)<3:return 0.
 arr=np.array(poly);return .5*np.sum(arr[:,0]*np.roll(arr[:,1],-1)-arr[:,1]*np.roll(arr[:,0],-1))
def overlap_area(subject,clip):
 if area(clip)<0:clip=clip[::-1]
 poly=list(subject)
 for k in range(3):
  if not poly:return 0.
  start,end=clip[k],clip[(k+1)%3];edge=end-start
  def signed(p):return edge[0]*(p[1]-start[1])-edge[1]*(p[0]-start[0])
  result=[];prev=poly[-1];prev_d=signed(prev)
  for point in poly:
   distance=signed(point)
   if (distance>=-1e-10)!=(prev_d>=-1e-10):result.append(prev+(point-prev)*(prev_d/(prev_d-distance)))
   if distance>=-1e-10:result.append(point)
   prev=point;prev_d=distance
  poly=result
 return abs(area(poly))
if len(a):
 pn=np.cross(P[:,1]-P[:,0],P[:,2]-P[:,0]);qn=np.cross(Q[:,1]-Q[:,0],Q[:,2]-Q[:,0]);pl=np.linalg.norm(pn,axis=1);ql=np.linalg.norm(qn,axis=1)
 pn=np.divide(pn,pl[:,None],out=np.zeros_like(pn),where=pl[:,None]>1e-12);qn=np.divide(qn,ql[:,None],out=np.zeros_like(qn),where=ql[:,None]>1e-12)
 possible=(pl>1e-10)&(ql>1e-10)&(np.linalg.norm(np.cross(pn,qn),axis=1)<1e-7)&(abs(np.einsum('ij,ij->i',Q[:,0]-P[:,0],pn))<1e-7)
 for index in np.flatnonzero(possible):
  axes=[i for i in range(3) if i!=np.argmax(abs(pn[index]))]
  coplanar[index]=overlap_area(P[index][:,axes],Q[index][:,axes])>1e-8
mask|=coplanar
found=a[mask];out={'candidate':str(args.candidate),'against':args.against,'scope':'All supplied mesh triangles (skin only for a runtime pose), nonadjacent index sets, inclusive AABB broad phase, bidirectional segment/triangle crossings and coplanar interior-area overlaps. Original skin seams are not welded.','broadphasePairs':len(a),'crossingPairCount':len(found),'coplanarOverlapPairCount':int(coplanar.sum()),'pairs':[]}
for i,j in found:
 out['pairs'].append({'triangles':[int(i),int(j)],'vertices':[tri[i].tolist(),tri[j].tolist()],'dominantBones':[labels[tri[i]].tolist(),labels[tri[j]].tolist()],'centresInputUnits':[input_centres[i].tolist(),input_centres[j].tolist()]})
groups=collections.Counter(tuple(sorted('|'.join(sorted(set(b))) for b in pair['dominantBones'])) for pair in out['pairs']);out['categoryCounts']=[{'bones':list(k),'crossingPairs':v} for k,v in groups.most_common()];dest=args.output or str(Path(args.candidate).with_name(Path(args.candidate).stem+'-self-triangles.json'));Path(dest).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'output':dest,'crossingPairCount':len(found),'broadphasePairs':len(a),'categoryCounts':out['categoryCounts'][:12]},indent=2))
