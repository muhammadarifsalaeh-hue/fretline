#!/usr/bin/env python3
"""Side-pad IK authoring against the unchanged skinned hand and real strings.

Outputs candidates only. The independent exact mesh gate remains authoritative;
neither optimizer convergence nor a sampled distance approves a runtime pose.
"""
import argparse, copy, gzip, hashlib, importlib.util, json, time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('previous',ROOT/'scripts/practice/final_solver/solve.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
gate=previous.gate;a=gate.a;m=previous.m
context_spec=importlib.util.spec_from_file_location('source_context',ROOT/'scripts/practice/source-pose-context.py')
source_context=importlib.util.module_from_spec(context_spec);context_spec.loader.exec_module(source_context)
SOURCE_BYTES=Path(__file__).read_bytes()
CONTEXT_LOADER_SHA256=hashlib.sha256((ROOT/'scripts/practice/source-pose-context.py').read_bytes()).hexdigest()

def load_context():
    return source_context.load_source_context(previous)


def nearest_surface(query, triangles, k=8, tree=None):
    """Closed-triangle nearest points, with oriented surface signed distance."""
    count=min(k,len(triangles));_,ids=(tree if tree is not None else cKDTree(triangles.mean(axis=1))).query(query,k=count)
    ids=np.asarray(ids).reshape(len(query),count)
    tri=triangles[ids];point=query[:,None,:];A=tri[:,:,0];u=tri[:,:,1]-A;v=tri[:,:,2]-A;w=point-A
    uu=np.sum(u*u,2);uv=np.sum(u*v,2);vv=np.sum(v*v,2);wu=np.sum(w*u,2);wv=np.sum(w*v,2);den=uu*vv-uv*uv
    s=np.divide(vv*wu-uv*wv,den,out=np.zeros_like(den),where=abs(den)>1e-15)
    t=np.divide(uu*wv-uv*wu,den,out=np.zeros_like(den),where=abs(den)>1e-15)
    candidates=[A+s[:,:,None]*u+t[:,:,None]*v]
    distances=[np.where((abs(den)>1e-15)&(s>=0)&(t>=0)&(s+t<=1),np.sum((candidates[0]-point)**2,2),np.inf)]
    for i in range(3):
        start=tri[:,:,i];edge=tri[:,:,(i+1)%3]-start;ee=np.sum(edge*edge,2)
        q=np.clip(np.divide(np.sum((point-start)*edge,2),ee,out=np.zeros_like(ee),where=ee>1e-15),0,1)
        p=start+q[:,:,None]*edge;candidates.append(p);distances.append(np.sum((p-point)**2,2))
    dist=np.stack(distances,axis=2);flat=dist.reshape(len(query),-1).argmin(1);face=flat//4;kind=flat%4
    closest=np.stack(candidates,axis=2)[np.arange(len(query)),face,kind]
    normal=np.cross(u[np.arange(len(query)),face],v[np.arange(len(query)),face]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
    delta=query-closest;length=np.linalg.norm(delta,axis=1)
    signed=length*np.where(np.sum(delta*normal,axis=1)>=0,1,-1)
    return closest,normal,signed


def triangle_gaps(first, second):
    """SAT separating distance for actual triangle pairs, including coplanar axes."""
    e=np.roll(first,-1,axis=1)-first;f=np.roll(second,-1,axis=1)-second
    n=np.cross(e[:,0],e[:,1]);m=np.cross(f[:,0],f[:,1])
    axes=np.concatenate([n[:,None,:],m[:,None,:],np.cross(e[:,:,None,:],f[:,None,:,:]).reshape(-1,9,3),np.cross(e,n[:,None,:]),np.cross(f,m[:,None,:])],axis=1)
    length=np.linalg.norm(axes,axis=2);axes=axes/np.maximum(length[:,:,None],1e-14)
    p=np.einsum('nvi,nai->nav',first,axes);q=np.einsum('nvi,nai->nav',second,axes)
    gap=np.maximum(p.min(2)-q.max(2),q.min(2)-p.max(2))
    return np.where(length>1e-12,gap,-np.inf).max(1)


def fit(context,chord,seed,folder,iterations=100,yaw=0,root_free=True,evidence=None,radius=None,contact_weight=40,exact_polish=False,max_seconds=180,all_fingers=False,full_polish=False):
    folder.mkdir(parents=True,exist_ok=True)
    source_bytes=SOURCE_BYTES;(folder/'solver-source.py.txt').write_bytes(source_bytes)
    r=context['rig'];guitar=previous.runtime_guitar(chord,folder);lines={s['number']:s for s in guitar['strings']}
    contacts=gate.contacts(chord);used={m.FINGERS[t['finger']-1] for t in contacts}
    before=context['chords'][seed['chordId']]
    previous_contacts=gate.contacts(before)
    changed={f for f in used if {(t['string'],t['fret']) for t in contacts if m.FINGERS[t['finger']-1]==f}
        !={(t['string'],t['fret']) for t in previous_contacts if m.FINGERS[t['finger']-1]==f}}
    # Same-fret neighbours must be allowed to make genuine side-of-pad contacts;
    # forcing both pad centroids onto adjacent strings folds the digits together.
    for target in contacts:
        if any(other['fret']==target['fret'] and m.FINGERS[other['finger']-1] in changed for other in contacts):
            changed.add(m.FINGERS[target['finger']-1])
    if yaw:changed=used.copy()
    released={m.FINGERS[t['finger']-1] for t in previous_contacts}-used
    controls=list(m.FINGERS[:4]) if all_fingers else [f for f in m.FINGERS[:4] if f in changed|released]
    if not controls:controls=sorted(used,key=m.FINGERS.index)
    angles=previous.seed_angles(r,seed)
    base_rot=Rotation.from_quat(seed['root']['quaternion']);base_pos=np.array(seed['root']['positionMm'])
    seed_world=a.world_from_pose(r,seed);seed_points=r.skin(seed_world)
    if yaw:
        R=Rotation.from_euler('y',yaw,degrees=True)
        pivot=np.mean([seed_points[r.patch_ids[f]].mean(0) for f in used],axis=0)
        desired=np.mean([previous.line_point(np.array(lines[t['string']]['controlPointsMm']),m.fret_x(t['fret'])-3.5) for t in contacts],axis=0)
        base_pos=pivot+R.apply(base_pos-pivot)+(desired-pivot)+np.array([0,3,0])
        base_rot=R*base_rot
    groups=[];group_for=[]
    for target in contacts:
        key=(target['finger'],target['fret'],'barre' if target['kind']=='barre' else target['string'])
        if key not in groups:groups.append(key)
        group_for.append(groups.index(key))
    group_start=np.array([m.fret_x(group[1])-3.5 for group in groups])
    root_n=6 if root_free else 0
    width=5
    x0=np.r_[np.zeros(root_n),np.concatenate([angles[f] for f in controls]),group_start]
    lo=np.r_[[-65,-40,-65],np.deg2rad([-35]*3)] if root_free else np.array([])
    hi=np.r_[[65,40,65],np.deg2rad([35]*3)] if root_free else np.array([])
    for finger in controls:
        lower=np.deg2rad([-8,-50,0,-5,-15]);upper=np.deg2rad([100,50,110,85,15])
        if any(t['kind']=='barre' and t['finger']==m.FINGERS.index(finger)+1 for t in contacts) and sum(t['finger']==m.FINGERS.index(finger)+1 for t in contacts)>=4:
            upper=np.deg2rad([75,50,45,35,15])
        lo=np.r_[lo,np.minimum(lower,angles[finger]-1e-6)];hi=np.r_[hi,np.maximum(upper,angles[finger]+1e-6)]
    lo=np.r_[lo,[m.fret_x(g[1])-5.9 for g in groups]];hi=np.r_[hi,[m.fret_x(g[1])-1.25 for g in groups]]
    x0=np.clip(x0,lo+1e-7,hi-1e-7)
    if radius is not None:
        widths=np.r_[np.r_[[radius]*3,np.deg2rad([radius]*3)] if root_free else [],np.deg2rad([radius]*(width*len(controls))),[4.8]*len(groups)]
        lo=np.maximum(lo,x0-widths);hi=np.minimum(hi,x0+widths)
    crossing_self=[];crossing_guitar=[]
    if evidence:
        with (gzip.open(evidence,'rt') if str(evidence).endswith('.gz') else open(evidence)) as stream:raw=json.load(stream)
        assert raw['assetSha256']==context['model_sha']
        assert raw['poseTransformSha256']==gate.transform_hash(seed),'Collision evidence must match the exact seed transforms'
        crossing_self=raw['self']['pairs']
        crossing_guitar=raw.get('guitar',{}).get('pairs',[])
    self_ids=np.array([p['vertices'] for p in crossing_self],dtype=int)
    guitar_ids=np.array([p['vertices'] for p in crossing_guitar],dtype=int)
    guitar_points=np.array(guitar['positions'])
    if len(guitar_ids):
        # The exact two-object audit reports vertex indices in the combined
        # hand+guitar namespace, whereas the guitar export is a separate mesh.
        guitar_ids[:,1]-=sum(len(mesh['positions']) for mesh in r.data['meshes'])
        assert guitar_ids[:,1].min()>=0 and guitar_ids[:,1].max()<len(guitar_points)
    template=np.array([Rotation.from_quat(seed['bones'][bone['name']]['quaternion']).as_matrix() for bone in r.bones])
    scales=np.array([bone['scale'] for bone in r.bones]);order=[]
    offsets={}
    for f in controls:
        flex,spread,pip,dip,twist=angles[f]
        for segment,angle in enumerate([flex,pip,dip],1):
            name=f'finger{m.NUMBERS[f]}-{segment}.L';bi=r.by_name[name]
            delta=Rotation.from_rotvec(r.flex_axes[name]*angle)
            if segment==1:delta=Rotation.from_rotvec(r.spread_axes[name]*spread)*delta*Rotation.from_rotvec(np.array([0.,1.,0.])*twist)
            decomposed=(Rotation.from_quat(r.rest_q[bi])*delta).as_matrix()
            # A numeric Euler-like inverse can be ill-conditioned near a bent
            # MCP. Anchor the actual saved rotation exactly, not its fit.
            offsets[bi]=template[bi]@decomposed.T
    def visit(i):
        if i in order:return
        if r.parents[i]>=0:visit(r.parents[i])
        order.append(i)
    for i in range(len(r.bones)):visit(i)
    def world(x):
        local=r.rest_local.copy();rot=template.copy()
        for j,f in enumerate(controls):
            flex,spread,pip,dip,twist=x[root_n+width*j:root_n+width*j+width]
            for segment,angle in enumerate([flex,pip,dip],1):
                name=f'finger{m.NUMBERS[f]}-{segment}.L';bi=r.by_name[name]
                delta=Rotation.from_rotvec(r.flex_axes[name]*angle)
                if segment==1:delta=Rotation.from_rotvec(r.spread_axes[name]*spread)*delta*Rotation.from_rotvec(np.array([0.,1.,0.])*twist)
                rot[bi]=offsets[bi]@(Rotation.from_quat(r.rest_q[bi])*delta).as_matrix()
        local[:,:3,:3]=rot*scales[:,None,:];w=np.empty_like(local)
        for i in order:w[i]=w[r.parents[i]]@local[i] if r.parents[i]>=0 else local[i]
        root=np.eye(4);root[:3,:3]=((Rotation.from_rotvec(x[3:6])*base_rot) if root_free else base_rot).as_matrix()*1000
        root[:3,3]=base_pos+(x[:3] if root_free else 0)
        return root@w,rot,root
    if yaw==0:
        reconstructed,_,_=world(x0)
        assert np.max(abs(reconstructed-seed_world))<1e-7,'Authoring must start from exact saved TRS'
    dom=context['dominant'];sample_ids=np.unique(np.r_[np.arange(0,len(r.positions),4),*r.patch_ids.values()])
    # Keep paired point counts fixed throughout least-squares iterations.
    finger_samples={f:r.finger_vertex_ids[f][np.isin(dom[r.finger_vertex_ids[f]],[r.by_name[f'finger{m.NUMBERS[f]}-{n}.L'] for n in [2,3]])][::3] for f in m.FINGERS[:4]}
    pairs=[('index','middle'),('middle','index'),('middle','ring'),('ring','middle'),('ring','little'),('little','ring')]
    string_samples={no:previous.sample_polyline(np.array(s['controlPointsMm']),2.) for no,s in lines.items()}
    near_faces={}
    if exact_polish:
        tri=seed_points[r.triangles];center=tri.mean(1);radii=np.linalg.norm(tri-center[:,None,:],axis=2).max(1)
        for number,line in lines.items():
            keep=m.polyline_distance(center,np.array(line['controlPointsMm']))<=radii+16
            # A distant open string may have no nearby seed faces. Keep a
            # conservative authoring neighbourhood; the full independent gate
            # still checks every face before any runtime endpoint is approved.
            if not keep.any():keep[np.argsort(m.polyline_distance(center,np.array(line['controlPointsMm']))-radii)[:64]]=True
            near_faces[number]=r.triangles[keep]
    count=0;started=time.monotonic()
    def residual(x):
        nonlocal count
        count+=1;w,_,_=world(x);points=r.skin(w);res=[];contact_x=x[root_n+width*len(controls):]
        for i,target in enumerate(contacts):
            f=m.FINGERS[target['finger']-1];faces=context['faces'][f,'barre' if target['kind']=='barre' else 'tip'];line=lines[target['string']]
            point=previous.line_point(np.array(line['controlPointsMm']),contact_x[group_for[i]])+np.array([0,line['radiusMm']+.025,0])
            if exact_polish:
                wire=m.fret_x(target['fret']);segments=gate.clip_line(np.array(line['controlPointsMm']),wire-6,wire-1.1)
                clearance=gate.clearance(points[faces],segments,line['radiusMm'])
                res.append((clearance-.035)*70)
            else:
                nearest,_,_=nearest_surface(point[None,:],points[faces],k=min(24,len(faces)))
                res.extend((nearest[0]-point)*contact_weight)
        sampled=points[sample_ids];res.extend(m.wood_depth(sampled)*35)
        for fret in range(1,13):
            dx=sampled[:,0]-m.fret_x(fret);dy=sampled[:,1]-m.board_top(sampled[:,2])-.5
            ellipse=np.sqrt((dx/1.1)**2+(dy/.5)**2);inside=np.maximum(0,1.02-ellipse)*.5
            half=(43+11*np.clip(sampled[:,0]/324,0,1))/2
            res.extend(inside*(abs(sampled[:,2])<=half+.1)*25)
        all_triangles=points[r.triangles]
        all_tree=cKDTree(all_triangles.mean(axis=1))
        # Exact local closed-triangle projections replace signed nearest-vertex
        # normals, which can face the wrong phalange across a narrow gap.
        for number,query in string_samples.items():
            if exact_polish:
                line=np.array(lines[number]['controlPointsMm']);segments=list(zip(line[:-1],line[1:]))
                value=gate.clearance(points[near_faces[number]],segments,lines[number]['radiusMm'])
                margin=.26 if chord['frets'][6-number]==0 else .012
                res.append(max(0,margin-value)*70)
            else:
                _,_,signed=nearest_surface(query,all_triangles,k=6,tree=all_tree)
                margin=.28+lines[number]['radiusMm'] if chord['frets'][6-number]==0 else .008+lines[number]['radiusMm']
                res.extend(np.maximum(0,margin-signed)*12)
        for f,g in pairs:
            query=points[finger_samples[f]];_,_,signed=nearest_surface(query,points[r.finger_triangles[g]],k=8)
            # Finger subsets have open boundaries at the palm. A signed normal
            # far from that subset is not an inside test and must not pull an
            # otherwise valid hand into a folded configuration.
            near=np.clip((6-np.abs(signed))/2,0,1)
            res.extend(np.maximum(0,.20-signed)*near*16)
        if crossing_self or crossing_guitar:
            combined=np.vstack([points if mesh is r.mesh else r.skin_mesh(w,mesh) for mesh in r.data['meshes']])
            if crossing_self:
                gaps=triangle_gaps(combined[self_ids[:,0]],combined[self_ids[:,1]])
                res.extend(np.maximum(0,.04-gaps)*100)
            if crossing_guitar:
                gaps=triangle_gaps(combined[guitar_ids[:,0]],guitar_points[guitar_ids[:,1]])
                res.extend(np.maximum(0,.025-gaps)*100)
        # Physical sampled fitting is independent from teaching certification.
        for j,f in enumerate(controls):
            q=x[root_n+width*j:root_n+width*j+width]
            res.extend((q-angles[f])*.025)
            res.append(max(0,q[0]+q[2]+q[3]-np.deg2rad(180))*2)
        if root_free:res.extend(x[:3]*.001);res.extend(x[3:6]*.05)
        res.extend((contact_x-group_start)*.002)
        return np.array(res)
    initial=float(np.sum(residual(x0)**2)/2)
    print(json.dumps({'starting':chord['id'],'yaw':yaw,'rootFree':root_free,'variables':len(x0),'initialCost':initial}),flush=True)
    indices=np.arange(len(x0))
    if exact_polish:
        # Preserve the nearly valid palm/MCP placement; polish tip flexion and
        # axial roll plus a common vertical lift instead of all root freedoms.
        indices=np.arange(root_n+width*len(controls)) if full_polish else np.array(([1] if root_free else [])+[root_n+width*j+n for j in range(len(controls)) for n in [2,3,4]])
    def expand(values):
        x=x0.copy();x[indices]=values;return x
    iterations_done=0;stopped_for_audit=False;stopped_for_budget=False
    def callback(intermediate_result):
        nonlocal iterations_done,stopped_for_audit,stopped_for_budget
        iterations_done+=1;seconds=time.monotonic()-started;cost=float(intermediate_result.cost)
        if iterations_done%10==0:
            checkpoint={'parameters':expand(intermediate_result.x).tolist(),'cost':cost,'seconds':seconds,'iterations':iterations_done,'notAnAcceptanceGate':True}
            (folder/'checkpoint.json').write_text(json.dumps(checkpoint)+'\n');print(json.dumps({'progress':chord['id'],'cost':cost,'seconds':round(seconds,1),'iterations':iterations_done}),flush=True)
        stopped_for_audit=cost<.001
        stopped_for_budget=seconds>=max_seconds
        if stopped_for_audit or stopped_for_budget:raise StopIteration
    result=least_squares(lambda values:residual(expand(values)),x0[indices],bounds=(lo[indices],hi[indices]),max_nfev=iterations,diff_step=1e-5,x_scale='jac',ftol=1e-8,xtol=1e-8,gtol=1e-8,callback=callback)
    result.x=expand(result.x)
    w,rot,root=world(result.x);p=copy.deepcopy(seed);p['root']={'positionMm':root[:3,3].tolist(),'quaternion':Rotation.from_matrix(root[:3,:3]/1000).as_quat().tolist()}
    for f in controls:
        for segment in range(1,4):
            name=f'finger{m.NUMBERS[f]}-{segment}.L';p['bones'][name]['quaternion']=Rotation.from_matrix(rot[r.by_name[name]]).as_quat().tolist()
    p['chordId']=chord['id'];p['status']='needs-review';p['reviewed']=False;p['audit']={k:False for k in previous.GATES};p.pop('solverParameters',None)
    p['reason']={'th':'ท่าที่กำลังตรวจบนผิวโมเดลจริง ยังไม่ถือว่าผ่านจนกว่าจะตรวจเมชเต็ม','en':'Actual-skin authoring candidate. Only the independent full mesh audit can accept it.'}
    p['targets']=[dict(t,finger=m.FINGERS[t['finger']-1],positionMm=previous.line_point(np.array(lines[t['string']]['controlPointsMm']),result.x[root_n+width*len(controls)+group_for[i]]).tolist()) for i,t in enumerate(contacts)]
    metrics={'chord':chord['id'],'seedChord':seed['chordId'],'yawDegrees':yaw,'rootFree':root_free,'controlledDigits':controls,'optimizedVariables':len(indices),'evaluations':result.nfev,'residualCalls':count,'seconds':time.monotonic()-started,'initialCost':initial,'finalCost':float(result.cost),'converged':bool(result.success),'stoppedForAudit':stopped_for_audit,'stoppedForBudget':stopped_for_budget,'sampledResidualMax':float(abs(result.fun).max()),'exactSelfPairsUsedForRefinement':len(crossing_self),'exactGuitarPairsUsedForRefinement':len(crossing_guitar),'exactDistancePolish':exact_polish,'fullExactDegreesOfFreedom':full_polish,'allDigitsAvailable':all_fingers,'notAnAcceptanceGate':True}
    p['authoringSource']={'method':'real closed-triangle side-pad IK; original exact post-fit gate required','sourceLibrarySHA256':context['library_sha'],'seedTransformSHA256':gate.transform_hash(seed),'solverSHA256':hashlib.sha256(source_bytes).hexdigest(),'contextLoaderSHA256':CONTEXT_LOADER_SHA256,'parameters':result.x.tolist(),'metrics':metrics}
    (folder/'candidate.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n');(folder/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps(metrics),flush=True)
    return p,metrics


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--chords',required=True);parser.add_argument('--yaw',type=float,default=0);parser.add_argument('--iterations',type=int,default=100);parser.add_argument('--fixed-root',action='store_true');parser.add_argument('--seed');parser.add_argument('--seed-file',type=Path);parser.add_argument('--collision-evidence',type=Path);parser.add_argument('--radius',type=float);parser.add_argument('--exact-polish',action='store_true');parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--all-fingers',action='store_true');parser.add_argument('--full-polish',action='store_true')
    args=parser.parse_args();context=load_context();proposal=copy.deepcopy(context['library']);runs=[]
    if args.output.exists() and any(args.output.iterdir()):parser.error('Use a fresh output directory to preserve prior results')
    for key in args.chords.split(','):
        chord=context['chords'][key];seed,_=previous.choose_seed(context,chord)
        if args.seed:seed=copy.deepcopy(context['library']['poses'][args.seed])
        if args.seed_file:seed=json.loads(args.seed_file.read_text())
        candidate,metrics=fit(context,chord,seed,args.output/key,args.iterations,args.yaw,not args.fixed_root,args.collision_evidence,args.radius,exact_polish=args.exact_polish,all_fingers=args.all_fingers,full_polish=args.full_polish)
        proposal['poses'][key]=candidate;runs.append(metrics)
        (args.output/'proposal-library.json').write_text(previous.frozen_json(proposal));(args.output/'runs.json').write_text(json.dumps(runs,indent=2)+'\n')

if __name__=='__main__':main()
