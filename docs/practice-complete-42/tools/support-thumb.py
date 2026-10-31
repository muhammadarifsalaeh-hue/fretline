"""Fit a genuine thumb support without changing fretting fingers or root.
Skin contact, joint measurements and full mesh post-audit remain separate gates.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,subprocess,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)

def support(context,chord,seed,folder,evidence=None):
 folder.mkdir(parents=True,exist_ok=True);r=context['rig'];names=[f'finger1-{i}.L'for i in range(1,4)];source=folder/'input.json';source.write_text(json.dumps(seed));export=folder/'guitar.json';subprocess.run(['node',str(Path(__file__).with_name('export-guitar.mjs')),chord['id'],str(export),str(source)],cwd=ROOT,check=True);guitar=json.loads(export.read_text());gp=np.array(guitar['positions']);gi=np.array(guitar['indices']).reshape(-1,3);labels=np.array(guitar['dominantBones']);neck=gp[gi[np.all(labels[gi]=='d-section-neck-back',axis=1)]]
 base_world=f.a.world_from_pose(r,seed);base_points=r.skin(base_world);pad=base_points[r.patch_ids['thumb']].mean(0);min_x=max(8,f.m.fret_x(max(0,min(t['fret']for t in f.gate.contacts(chord))-2))+4);max_x=f.m.fret_x(max(t['fret']for t in f.gate.contacts(chord)))+5
 x=float(np.clip(pad[0],min_x,max_x));z=float(np.clip(pad[2],-17,17));q=np.array([[x,f.m.back_y(x,z),z]]);closest,norm,_=f.nearest_surface(q,neck,k=min(64,len(neck)));normal=norm[0];normal*=1 if normal[1]<0 else -1;target=np.array(seed.get('thumbSupport',{}).get('targetMm',closest[0]+normal*.22))
 base=np.array([Rotation.from_quat(seed['bones'][b['name']]['quaternion']).as_matrix()for b in r.bones]);local=r.rest_local.copy();scales=np.array([b['scale']for b in r.bones]);root=np.eye(4);root[:3,:3]=Rotation.from_quat(seed['root']['quaternion']).as_matrix()*1000;root[:3,3]=seed['root']['positionMm'];order=[]
 def visit(i):
  if i in order:return
  if r.parents[i]>=0:visit(r.parents[i])
  order.append(i)
 for i in range(len(r.bones)):visit(i)
 def world(x):
  rot=base.copy()
  for j,name in enumerate(names):rot[r.by_name[name]]=base[r.by_name[name]]@Rotation.from_rotvec(x[j*3:j*3+3]).as_matrix()
  l=local.copy();l[:,:3,:3]=rot*scales[:,None,:];w=np.empty_like(l)
  for i in order:w[i]=w[r.parents[i]]@l[i]if r.parents[i]>=0 else l[i]
  return root@w,rot
 faces=context['faces']['thumb','barre'];finger_samples=r.finger_vertex_ids['thumb'][::2];obstacles=np.concatenate([r.finger_triangles[d]for d in f.m.FINGERS[:4]])
 self_ids=[];guitar_ids=[]
 if evidence:
  with gzip.open(evidence,'rt')as stream:raw=json.load(stream)
  assert raw['poseTransformSha256']==f.gate.transform_hash(seed)
  self_ids=np.array([p['vertices']for p in raw['self']['pairs']],dtype=int);guitar_ids=np.array([p['vertices']for p in raw.get('guitar',{}).get('pairs',[])],dtype=int)
  if len(guitar_ids):guitar_ids[:,1]-=sum(len(mesh['positions'])for mesh in r.data['meshes'])
 started=time.monotonic();calls=0
 def residual(x):
  nonlocal calls
  calls+=1;w,_=world(x);points=r.skin(w);tri=points[r.finger_triangles['thumb']];samples=np.vstack([points[r.finger_vertex_ids['thumb']],tri.mean(1),*(tri[:,i]*.5+tri[:,(i+1)%3]*.5 for i in range(3))]);nearest,_,_=f.nearest_surface(target[None,:],points[faces],k=min(64,len(faces)));res=[(nearest[0]-target)*40,f.m.wood_depth(samples)*100]
  # Open finger subsets do not define a reliable signed interior. Exact saved
  # triangle crossings constrain repair; the unchanged full post-audit catches
  # every newly introduced collision before this candidate can be selected.
  if len(self_ids)or len(guitar_ids):
   combined=np.vstack([points if mesh is r.mesh else r.skin_mesh(w,mesh)for mesh in r.data['meshes']])
   if len(self_ids):res.append(np.maximum(0,.04-f.triangle_gaps(combined[self_ids[:,0]],combined[self_ids[:,1]]))*100)
   if len(guitar_ids):res.append(np.maximum(0,.03-f.triangle_gaps(combined[guitar_ids[:,0]],gp[guitar_ids[:,1]]))*100)
  res.append(x*np.r_[[.025]*3,[.12]*6]);return np.concatenate(res)
 def callback(intermediate_result):
  if time.monotonic()-started>90:raise StopIteration
 limit=np.deg2rad([75]*3+[30]*6);result=least_squares(residual,np.zeros(9),bounds=(-limit,limit),max_nfev=130,diff_step=1e-5,ftol=1e-10,xtol=1e-10,gtol=1e-10,x_scale='jac',callback=callback)
 w,rot=world(result.x);p=copy.deepcopy(seed)
 for name in names:p['bones'][name]['quaternion']=Rotation.from_matrix(rot[r.by_name[name]]).as_quat().tolist()
 p['audit']={k:False for k in f.previous.GATES};p['status']='needs-review';p['reviewed']=False;p.pop('solverParameters',None)
 points=r.skin(w);skin=points[faces];query=np.vstack([skin.mean(1),skin.reshape(-1,3)]);nearest,norm,signed=f.nearest_surface(query,neck,k=min(32,len(neck)));distance=float(abs(signed).min());target_distance=float(np.linalg.norm(f.nearest_surface(target[None,:],points[faces],k=min(64,len(faces)))[0][0]-target));metrics={'id':chord['id'],'cost':float(result.cost),'seconds':time.monotonic()-started,'targetMm':target.tolist(),'supportTargetErrorMm':target_distance,'minimumPalmarThumbToNeckBackMm':distance,'frettingBonesAndRootIdentical':True,'notTeachingApproval':True}
 p['thumbSupport']={'targetMm':target.tolist(),'measurements':metrics};p['authoringSource']={'method':'Thumb-only actual-palmar-surface support; original fretting bones and root preserved','seedTransformSHA256':f.gate.transform_hash(seed),'solverSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rotationsRadians':result.x.tolist()};(folder/'candidate.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');(folder/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');lib=copy.deepcopy(context['library']);lib['poses'][chord['id']]=p;(folder/'proposal-library.json').write_text(f.previous.frozen_json(lib));print(json.dumps(metrics),flush=True);return p
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--evidence',type=Path);args=ap.parse_args();context=f.load_context();seed=json.loads(args.seed.read_text());support(context,context['chords'][seed['chordId']],seed,args.out,args.evidence)
