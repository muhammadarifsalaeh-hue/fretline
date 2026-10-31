"""Local real-surface refinement without moving an already fitted palm or peers.
Small local joint rotations author a candidate; full unchanged mesh audit decides.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,subprocess,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v5.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=Path,required=True);ap.add_argument('--audit',type=Path,required=True);ap.add_argument('--digit',required=True);ap.add_argument('--allow-released',action='store_true');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();folder=args.out.resolve();folder.mkdir(parents=True,exist_ok=True);context=f.load_context();r=context['rig'];seed=json.loads(args.seed.read_text());key=seed['chordId'];chord=context['chords'][key];digit=args.digit;names=[f'finger{f.m.NUMBERS[digit]}-{i}.L'for i in range(1,4)]
 source=folder/'seed.json';source.write_text(json.dumps(seed));gfile=folder/'guitar.json';subprocess.run(['node',str(Path(__file__).with_name('export-guitar.mjs')),key,str(gfile),str(source)],cwd=ROOT,check=True);guitar=json.loads(gfile.read_text());gp=np.array(guitar['positions']);lines={t['number']:t for t in guitar['strings']};report=json.loads(args.audit.read_text());row=next(x for x in report['rows']if x['id']==key);assert row['poseTransformSha256']==f.gate.transform_hash(seed)
 with gzip.open(args.audit.parent/row['rawEvidence'],'rt')as stream:raw=json.load(stream)
 self_ids=np.array([p['vertices']for p in raw['self']['pairs']],dtype=int);guitar_ids=np.array([p['vertices']for p in raw.get('guitar',{}).get('pairs',[])],dtype=int)
 if len(guitar_ids):guitar_ids[:,1]-=sum(len(mesh['positions'])for mesh in r.data['meshes'])
 base=np.array([Rotation.from_quat(seed['bones'][b['name']]['quaternion']).as_matrix()for b in r.bones]);scales=np.array([b['scale']for b in r.bones]);root=np.eye(4);root[:3,:3]=Rotation.from_quat(seed['root']['quaternion']).as_matrix()*1000;root[:3,3]=seed['root']['positionMm'];order=[]
 def visit(i):
  if i in order:return
  if r.parents[i]>=0:visit(r.parents[i])
  order.append(i)
 for i in range(len(r.bones)):visit(i)
 def world(x):
  rot=base.copy()
  for j,name in enumerate(names):rot[r.by_name[name]]=base[r.by_name[name]]@Rotation.from_rotvec(x[j*3:j*3+3]).as_matrix()
  local=r.rest_local.copy();local[:,:3,:3]=rot*scales[:,None,:];w=np.empty_like(local)
  for i in order:w[i]=w[r.parents[i]]@local[i]if r.parents[i]>=0 else local[i]
  return root@w,rot
 assigned=[t for t in f.effective_contacts(chord)if f.m.FINGERS[t['finger']-1]==digit];assert assigned or args.allow_released;physical=[]
 for t in assigned:
  off=seed.get('pressOffsetsMm',{}).get(f"{t['string']}:{t['fret']}",4);x=f.m.fret_x(t['fret'])-off;line=lines[t['string']];points=np.array(line['controlPointsMm']);center=f.previous.line_point(points,x);target=center+np.array([0,line['radiusMm']+.035,0]);faces=context['faces'][digit,'barre'if t['kind']=='barre'else'tip'];physical.append((faces,f.gate.clip_line(points,x-.5,x+.5),line['radiusMm'],target))
 triangles=r.finger_triangles[digit];vertices=r.finger_vertex_ids[digit]
 dom=context['dominant'];distal={d:r.finger_vertex_ids[d][np.isin(dom[r.finger_vertex_ids[d]],[r.by_name[f'finger{f.m.NUMBERS[d]}-{n}.L']for n in [2,3]])][::2]for d in f.m.FINGERS}
 calls=0;started=time.monotonic()
 def residual(x):
  nonlocal calls
  calls+=1;w,_=world(x);points=r.skin(w);tri=points[triangles];samples=np.vstack([points[vertices],tri.mean(1),*(tri[:,i]*.5+tri[:,(i+1)%3]*.5 for i in range(3))]);res=[f.m.wood_depth(samples)*500]
  for faces,segments,radius,target in physical:
   res.append(np.array([(f.gate.clearance(points[faces],segments,radius)-.035)*220]));nearest,_,_=f.nearest_surface(target[None,:],points[faces],k=min(24,len(faces)));res.append((nearest[0]-target)*20)
  for number,line in lines.items():
   p=np.array(line['controlPointsMm']);gap=f.gate.clearance(points[triangles],list(zip(p[:-1],p[1:])),line['radiusMm']);margin=.24 if not assigned or chord['frets'][6-number]==0 else .018;res.append(np.array([max(0,margin-gap)*160]))
  if len(self_ids)or len(guitar_ids):
   combined=np.vstack([points if mesh is r.mesh else r.skin_mesh(w,mesh)for mesh in r.data['meshes']])
   if len(self_ids):res.append(np.maximum(0,.04-f.triangle_gaps(combined[self_ids[:,0]],combined[self_ids[:,1]]))*500)
   if len(guitar_ids):res.append(np.maximum(0,.035-f.triangle_gaps(combined[guitar_ids[:,0]],gp[guitar_ids[:,1]]))*500)
  for other in f.m.FINGERS:
   if other==digit:continue
   for first,second in [(digit,other),(other,digit)]:
    _,_,signed=f.nearest_surface(points[distal[first]],points[r.finger_triangles[second]],k=8);near=np.clip((6-np.abs(signed))/2,0,1);res.append(np.maximum(0,.20-signed)*near*150)
  res.append(x*.02);return np.concatenate(res)
 def callback(intermediate_result):
  if time.monotonic()-started>125:raise StopIteration
 limits=np.deg2rad([16]*3+[8]*6 if assigned else [35]*3+[10]*6);initial=float(np.sum(residual(np.zeros(9))**2)/2);result=least_squares(residual,np.zeros(9),bounds=(-limits,limits),max_nfev=120,diff_step=1e-5,ftol=1e-10,xtol=1e-10,gtol=1e-10,x_scale='jac',callback=callback);w,rot=world(result.x);p=copy.deepcopy(seed)
 for name in names:p['bones'][name]['quaternion']=Rotation.from_matrix(rot[r.by_name[name]]).as_quat().tolist()
 p['status']='needs-review';p['reviewed']=False;p['audit']={k:False for k in f.previous.GATES};p['authoringSource']={'method':'Bounded local contact/wood repair; palm and all other digits unchanged','digit':digit,'localBoundsDegrees':[16,8,8]if assigned else[35,10,10],'sampledNeighbourAvoidance':True,'parametersRadians':result.x.tolist(),'seedTransformSHA256':f.gate.transform_hash(seed),'solverSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'notAnAcceptanceGate':True};metrics={'chord':key,'digit':digit,'initialCost':initial,'finalCost':float(result.cost),'seconds':time.monotonic()-started,'calls':calls,'notAnAcceptanceGate':True};(folder/'candidate.json').write_text(json.dumps(p,indent=2)+'\n');(folder/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');lib=copy.deepcopy(context['library']);lib['poses'][key]=p;(folder/'proposal-library.json').write_text(f.previous.frozen_json(lib));print(json.dumps(metrics),flush=True)
 with(folder/'audit.log').open('w')as log:subprocess.run(['python',str(Path(__file__).with_name('check-geometry.py')),'--library',str(folder/'proposal-library.json'),'--chords',key,'--require','','--output',str(folder/'audit')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('LOCAL',key,json.loads((folder/'audit/summary.json').read_text())['rows'][0]['geometricPassed'],flush=True)
if __name__=='__main__':main()
