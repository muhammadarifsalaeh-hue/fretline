#!/usr/bin/env python3
"""One bounded actual-skin IK problem for all 42 Fretline musical voicings.

This offline authoring solver never edits runtime/product data. Its numerical
objective is deliberately NOT an acceptance gate: only the original exact mesh
checker can select a new endpoint, and anatomy/teaching remain unapproved.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,subprocess,tempfile,time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('gate',ROOT/'scripts/practice/check-hand-geometry.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
a=gate.a;m=a.c.m
PRIORITY=['C','G','D','Em','Am','F','E','Dm']
GATES=['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed']

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def transform_hash(p):return gate.transform_hash(p)
def frozen_json(data):return json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'

def closest_triangle_point(tri,point):
    """Exact point/closed-triangle nearest point, not nearest bone/vertex."""
    A=tri[:,0];u=tri[:,1]-A;v=tri[:,2]-A;w=point-A
    uu=np.einsum('ij,ij->i',u,u);uv=np.einsum('ij,ij->i',u,v);vv=np.einsum('ij,ij->i',v,v)
    wu=np.einsum('ij,ij->i',w,u);wv=np.einsum('ij,ij->i',w,v);den=uu*vv-uv*uv
    s=np.divide(vv*wu-uv*wv,den,out=np.zeros(len(tri)),where=abs(den)>1e-16);t=np.divide(uu*wv-uv*wu,den,out=np.zeros(len(tri)),where=abs(den)>1e-16)
    inside=(abs(den)>1e-16)&(s>=0)&(t>=0)&(s+t<=1)
    candidates=[A+s[:,None]*u+t[:,None]*v];barys=[np.column_stack((1-s-t,s,t))];dist=[np.where(inside,np.sum((candidates[0]-point)**2,axis=1),np.inf)]
    for i in range(3):
        start=tri[:,i];edge=tri[:,(i+1)%3]-start;ee=np.einsum('ij,ij->i',edge,edge)
        q=np.clip(np.divide(np.einsum('ij,ij->i',point-start,edge),ee,out=np.zeros(len(tri)),where=ee>1e-16),0,1)
        candidate=start+q[:,None]*edge;bary=np.zeros((len(tri),3));bary[:,i]=1-q;bary[:,(i+1)%3]=q
        candidates.append(candidate);barys.append(bary);dist.append(np.sum((candidate-point)**2,axis=1))
    distances=np.stack(dist);which,index=np.unravel_index(np.argmin(distances),distances.shape)
    return candidates[which][index],index,barys[which][index]

def sample_polyline(points,step=2.5):
    out=[]
    for start,end in zip(points[:-1],points[1:]):
        count=max(1,int(np.ceil(np.linalg.norm(end-start)/step)));out.extend(start+(end-start)*t for t in np.linspace(0,1,count,endpoint=False))
    out.append(points[-1]);return np.array(out)

def line_point(line,x):
    for start,end in zip(line[:-1],line[1:]):
        if min(start[0],end[0])-1e-8<=x<=max(start[0],end[0])+1e-8 and abs(end[0]-start[0])>1e-9:
            return start+(end-start)*(x-start[0])/(end[0]-start[0])
    raise ValueError('Actual runtime string does not contain contact x')

def load_context(output=None):
    path=ROOT/'src/features/practice/assets/hand-poses.json';library=json.loads(path.read_text());rig=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
    model_sha=digest(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb');assert model_sha==rig.data['sha256']==library['assetSha256']
    chords=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"],cwd=ROOT))
    assert len(chords)==42 and {c['id']for c in chords}==set(library['poses'])
    prior=json.loads((ROOT/'docs/practice-hand-batch-3/geometry/summary.json').read_text());accepted={r['id']for r in prior['rows']if r['geometricPassed'] is True}
    assert prior['librarySnapshotSha256']==digest(path),'Pin a new source audit before fitting a changed library'
    assert prior['assetSha256']==model_sha and prior['sourceChordSha256']==digest(ROOT/'src/features/practice/data/chords.js')
    assert prior['count']==42 and len(prior['rows'])==42 and {r['id']for r in prior['rows']}==set(library['poses'])
    assert all(r['poseTransformSha256']==transform_hash(library['poses'][r['id']])for r in prior['rows'])
    assert prior['testSuitePassed'] is True and not prior['errors'] and accepted
    dominant=rig.joint_bones[rig.joints[np.arange(len(rig.joints)),rig.weights.argmax(1)]];palmar=rig.normals[rig.triangles].mean(1)@rig.palmar>.05
    faces={}
    for f in m.FINGERS:
        names=[rig.by_name[f'finger{m.NUMBERS[f]}-{i}.L']for i in range(1,4)]
        owned=np.isin(dominant[rig.triangles],names).all(1)&palmar
        faces[f,'barre']=rig.triangles[owned];faces[f,'tip']=rig.triangles[owned&(dominant[rig.triangles]==names[-1]).any(1)]
    ctx={'library':library,'library_sha':digest(path),'model_sha':model_sha,'chord_sha':digest(ROOT/'src/features/practice/data/chords.js'),'rig_sha':digest(ROOT/'docs/practice-trainer/models/authoring/rig-data.json'),'rig':rig,'chords':{c['id']:c for c in chords},'accepted':accepted,'faces':faces,'dominant':dominant}
    if output:
        out=Path(output);out.mkdir(parents=True,exist_ok=True);(out/'source-library.json').write_text(frozen_json(library));(out/'sources.json').write_text(json.dumps({k:ctx[k]for k in ['library_sha','model_sha','chord_sha','rig_sha']},indent=2)+'\n')
    return ctx

def choose_seed(context,chord):
    """Select by original finger/string/fret topology, never chord-name patches."""
    if chord['id'] in context['accepted']:return copy.deepcopy(context['library']['poses'][chord['id']]),chord['id']
    def score(key):
        source=context['chords'][key];cost=0
        for i,fret in enumerate(chord['frets']):
            if not fret:continue
            finger=chord['fingers'][i];choices=[(abs(i-j)*6+abs(fret-other)*3)for j,other in enumerate(source['frets']) if other and source['fingers'][j]==finger]
            cost+=min(choices)if choices else 18
        cost+=sum(chord['fingers'].count(f)!=source['fingers'].count(f)for f in range(1,5))
        return cost,key
    key=min(context['accepted'],key=score);return copy.deepcopy(context['library']['poses'][key]),key

def seed_angles(rig,seed):
    angles={}
    for f in m.FINGERS:
        n=f'finger{m.NUMBERS[f]}-1.L';i=rig.by_name[n];delta=Rotation.from_quat(rig.rest_q[i]).inv()*Rotation.from_quat(seed['bones'][n]['quaternion'])
        def error(v):
            q=Rotation.from_rotvec(rig.spread_axes[n]*v[1])*Rotation.from_rotvec(rig.flex_axes[n]*v[0])*Rotation.from_rotvec(np.array([0.,1.,0.])*v[2])
            return (q.inv()*delta).as_rotvec()
        fit=least_squares(error,[.2,0,0],max_nfev=30)
        rest=[]
        for j in [2,3]:
            name=f'finger{m.NUMBERS[f]}-{j}.L';bi=rig.by_name[name];d=Rotation.from_quat(rig.rest_q[bi]).inv()*Rotation.from_quat(seed['bones'][name]['quaternion']);rest.append(float(d.as_rotvec()@rig.flex_axes[name]))
        angles[f]=np.array([fit.x[0],fit.x[1],*rest,fit.x[2]])
    return angles

def runtime_guitar(chord,out):
    target=Path(out)/(chord['id']+'-guitar.json');subprocess.run(['node',str(ROOT/'scripts/practice/export-guitar-collision-mesh.mjs'),chord['id'],str(target)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    return json.loads(target.read_text())

def controlled_digits(context,chord,seed,guitar):
    """Release only previously fretted or actually obstructing unused chains.

    Keeping a seed's fretted digit fixed after that digit becomes unused can
    silently mute a newly open string. Conversely, making every unused joint
    free recreates the original generator's unstable thumb/little folds.
    """
    rig=context['rig'];contacts=gate.contacts(chord)
    active=sorted({m.FINGERS[t['finger']-1]for t in contacts},key=m.FINGERS.index)
    seed_chord=context['chords'][seed['chordId']]
    formerly_fretted={m.FINGERS[t['finger']-1]for t in gate.contacts(seed_chord)}
    points=rig.skin(a.world_from_pose(rig,seed));lines={s['number']:s for s in guitar['strings']}
    released=[];reasons={}
    for finger in m.FINGERS[:4]:
        if finger in active:continue
        why=[]
        if finger in formerly_fretted:why.append('formerly-fretted-in-seed')
        for string in chord['openStrings']:
            line=lines[string];pts=np.array(line['controlPointsMm'])
            clearance=gate.clearance(points[rig.finger_triangles[finger]],list(zip(pts[:-1],pts[1:])),line['radiusMm'])
            if clearance<.35:why.append({'initialOpenString':string,'actualFingerSurfaceClearanceMm':clearance})
        if why:released.append(finger);reasons[finger]=why
    return active,released,reasons

def solve_chord(context,chord,seed,max_evaluations=35,output=None,placement_weight=.45):
    if type(max_evaluations) is not int or max_evaluations<1:
        raise ValueError('max_evaluations must be a positive integer')
    if not math.isfinite(placement_weight) or placement_weight<0:
        raise ValueError('placement_weight must be finite and nonnegative')
    rig=context['rig'];folder=Path(output or tempfile.mkdtemp(prefix='central-hand-'));folder.mkdir(parents=True,exist_ok=True);guitar=runtime_guitar(chord,folder);lines={s['number']:s for s in guitar['strings']}
    contacts=gate.contacts(chord);active,released,release_reasons=controlled_digits(context,chord,seed,guitar)
    controls=active+released+['thumb']
    angles=seed_angles(rig,seed);basepos=np.array(seed['root']['positionMm']);baserot=Rotation.from_quat(seed['root']['quaternion'])
    release_priors={}
    for finger in released:
        neutral=angles[finger].copy()
        neutral[2]=min(neutral[2],np.deg2rad(35));neutral[3]=min(neutral[3],np.deg2rad(20))
        release_priors[finger]=neutral;angles[finger]=neutral
    # Original physical fret region permits staggered contacts; one shared x
    # variable per barre keeps a straight finger rather than six independent fits.
    groups=[];group_for=[]
    for t in contacts:
        key=(t['finger'],t['fret'],'barre'if t['kind']=='barre'else t['string'])
        if key not in groups:groups.append(key)
        group_for.append(groups.index(key))
    group_start=[]
    for finger,fret,kind in groups:
        same=[g for g in groups if g[1]==fret and g[2]!='barre'];rank=sorted(g[0]for g in same).index(finger)if same and kind!='barre'else 0
        offset=4 if len(same)<2 else float(np.linspace(2.,5.5,len(same))[rank]);group_start.append(m.fret_x(fret)-offset)
    q0=np.concatenate([angles[f]for f in controls]);x0=np.r_[np.zeros(6),q0,group_start];lo=np.r_[[-35,-30,-20],np.deg2rad([-28]*3)];hi=np.r_[[35,22,38],np.deg2rad([28]*3)]
    for f in controls:
        lower=np.deg2rad([-15,-35,-10,-8,-12]if f=='thumb'else[0,-32,3,0,-12]);upper=np.deg2rad([65,35,65,65,12]if f=='thumb'else[85,32,100,72,12])
        if f in release_priors:
            lower=angles[f]-np.deg2rad([8,6,10,8,4]);upper=angles[f]+np.deg2rad([8,6,10,8,4])
        lo=np.r_[lo,np.minimum(lower,angles[f]-1e-5)];hi=np.r_[hi,np.maximum(upper,angles[f]+1e-5)]
    lo=np.r_[lo,[m.fret_x(g[1])-5.9 for g in groups]];hi=np.r_[hi,[m.fret_x(g[1])-1.25 for g in groups]];x0=np.clip(x0,lo+1e-7,hi-1e-7)
    sample_ids=np.unique(np.r_[np.arange(0,len(rig.positions),3),*rig.patch_ids.values()]);neighbor_ids={f:rig.finger_vertex_ids[f][::4]for f in m.FINGERS}
    normals_base=rig.normals;string_samples={s:sample_polyline(np.array(line['controlPointsMm']))for s,line in lines.items()};calls=0;start=time.monotonic()
    def pose(x):
        p=copy.deepcopy(seed);p['root']={'positionMm':(basepos+x[:3]).tolist(),'quaternion':(Rotation.from_rotvec(x[3:6])*baserot).as_quat().tolist()}
        for j,f in enumerate(controls):
            flex,spread,pip,dip,twist=x[6+5*j:11+5*j]
            for seg,angle in enumerate([flex,pip,dip],1):
                n=f'finger{m.NUMBERS[f]}-{seg}.L';bi=rig.by_name[n];d=Rotation.from_rotvec(rig.flex_axes[n]*angle)
                if seg==1:d=Rotation.from_rotvec(rig.spread_axes[n]*spread)*d*Rotation.from_rotvec(np.array([0.,1.,0.])*twist)
                p['bones'][n]['quaternion']=(Rotation.from_quat(rig.rest_q[bi])*d).as_quat().tolist()
        return p
    def residual(x):
        nonlocal calls
        calls+=1;p=pose(x);world=a.world_from_pose(rig,p);points=rig.skin(world);normals=rig.skin_normals(world,np.arange(len(points)));out=[]
        cx=x[6+5*len(controls):]
        for i,t in enumerate(contacts):
            f=m.FINGERS[t['finger']-1];kind='barre'if t['kind']=='barre'else'tip';faces=context['faces'][f,kind];line=lines[t['string']]
            center=line_point(np.array(line['controlPointsMm']),cx[group_for[i]]);target=center+np.array([0,line['radiusMm']+.018,0]);point,face,bary=closest_triangle_point(points[faces],target)
            out.extend((point-target)*7);n=bary@normals[faces[face]];out.append(max(0,n[1]+.45)*2)
        sampled=points[sample_ids];out.extend(m.wood_depth(sampled)*14)
        # Actual fret crown ellipse parameters are the study model's 2.2 x1mm.
        for fret in range(1,13):
            dx=sampled[:,0]-m.fret_x(fret);dy=sampled[:,1]-m.board_top(sampled[:,2])-.5
            ellipse=np.sqrt((dx/1.1)**2+(dy/.5)**2);inside=np.maximum(0,1.035-ellipse)*.5
            half=(43+11*np.clip(sampled[:,0]/324,0,1))/2;inside*=abs(sampled[:,2])<=half+.2;out.extend(inside*12)
        # Signed skin-side string samples detect a line inside a finger even
        # when every mesh vertex is outside the tiny string radius. This fixes
        # the flat-zero unsigned-contact failure of earlier per-chord scripts.
        tree=cKDTree(points[sample_ids]);skin_normals=normals[sample_ids]
        for s,query in string_samples.items():
            dist,nearest=tree.query(query);signed=np.einsum('ij,ij->i',query-points[sample_ids[nearest]],skin_normals[nearest]);margin=.28 if chord['frets'][6-s]==0 else .012
            out.extend(np.maximum(0,margin-signed)*np.clip((10-dist)/3,0,1)*5)
            vertex_distance=m.polyline_distance(sampled,np.array(lines[s]['controlPointsMm']))-lines[s]['radiusMm'];out.extend(np.maximum(0,.006-vertex_distance)*6)
        for f,g in [('index','middle'),('middle','index'),('middle','ring'),('ring','middle'),('ring','little'),('little','ring'),('thumb','index')]:
            qi=neighbor_ids[f];ri=neighbor_ids[g];dist,near=cKDTree(points[ri]).query(points[qi]);signed=np.einsum('ij,ij->i',points[qi]-points[ri[near]],normals[ri[near]])
            # Exclude the joined MCP web, but retain real PIP/distal neighbors.
            own=context['dominant'][qi];prox=rig.by_name[f'finger{m.NUMBERS[f]}-1.L'];mask=own!=prox
            out.extend(np.maximum(0,.30-signed)*np.clip((9-dist)/3,0,1)*mask*7)
        mcps=np.array([world[rig.by_name[f'finger{m.NUMBERS[f]}-1.L'],:3,3]for f in active])
        out.extend(np.maximum(0,-42-mcps[:,2])*placement_weight);out.extend(np.maximum(0,mcps[:,2]+27)*placement_weight)
        out.extend(np.maximum(0,mcps[:,1]-18)*placement_weight*.5);out.extend(np.maximum(0,-3-mcps[:,1])*placement_weight*.5)
        thumb=points[rig.patch_ids['thumb']].mean(0);tx=float(np.mean(cx))-5;tz=0.;ty=float(m.back_y(tx,tz))-2
        out.extend((thumb-[tx,ty,tz])*np.array([.05,.2,.12]));out.extend(x[:3]*.003);out.extend(x[3:6]*.12)
        for j,f in enumerate(controls):
            q=x[6+5*j:11+5*j]
            if f in release_priors:out.extend((q-release_priors[f])*12)
            if f!='thumb':out.append((q[3]-.55*q[2])*1.5);out.append(max(0,q[0]+q[2]+q[3]-np.deg2rad(175))*3)
            out.append(q[4]*.5)
        out.extend((cx-np.array(group_start))*.015)
        return np.array(out)
    initial_cost=float(np.sum(residual(x0)**2)/2)
    result=least_squares(residual,x0,bounds=(lo,hi),max_nfev=max_evaluations,ftol=2e-6,xtol=2e-6,gtol=2e-6,diff_step=2e-5,x_scale='jac')
    candidate=pose(result.x);candidate.pop('solverParameters',None);candidate['chordId']=chord['id'];candidate['status']='needs-review';candidate['reviewed']=False;candidate['audit']={g:False for g in GATES}
    candidate['targets']=[dict(t,finger=m.FINGERS[t['finger']-1],positionMm=(line_point(np.array(lines[t['string']]['controlPointsMm']),result.x[6+5*len(controls)+group_for[i]])+np.array([0,lines[t['string']]['radiusMm'],0])).tolist())for i,t in enumerate(contacts)]
    metrics={'chord':chord['id'],'voicing':chord['voicing'],'maxEvaluations':max_evaluations,'evaluations':result.nfev,'residualCalls':calls,'seconds':time.monotonic()-start,'initialCost':initial_cost,'finalCost':float(result.cost),'optimizerConverged':bool(result.success),'rootDelta':result.x[:6].tolist(),'activeDigits':active,'releasedUnusedDigits':released,'releaseReasons':release_reasons,'contactXmm':result.x[6+5*len(controls):].tolist(),'note':'Sampled fitting priors only. Original exact acceptance and independent anatomical review remain mandatory.'}
    candidate['authoringSource']={'solver':'scripts/practice/final_solver/solve.py','solverSourceSha256':digest(Path(__file__)),'librarySha256':context['library_sha'],'sourceRigSha256':context['rig_sha'],'sourceChordSha256':context['chord_sha'],'seedTransformSha256':transform_hash(seed),'parameters':result.x.tolist(),'metrics':metrics}
    candidate['reason']={'en':'Central actual-skin IK candidate; exact geometry and independent natural-hand review pending.','th':'ต้นแบบจาก Solver กลางบนผิวมือจริง ยังรอการตรวจเมชและความเป็นธรรมชาติ'}
    (folder/'candidate.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n');(folder/'fit.json').write_text(json.dumps(metrics,indent=2)+'\n');return candidate,metrics

def select_audited_replacements(base_library,proposal_library,report,library_sha256,model_sha256,chord_sha256,expected_ids=None):
    """Fail closed on stale evidence; never weaken the original geometry gate."""
    assert hashlib.sha256(frozen_json(proposal_library).encode()).hexdigest()==library_sha256, 'Proposal bytes differ from their declared hash'
    assert report['librarySnapshotSha256']==library_sha256 and report['assetSha256']==model_sha256 and report['sourceChordSha256']==chord_sha256
    assert base_library['assetSha256']==proposal_library['assetSha256']==model_sha256
    assert set(base_library['poses'])==set(proposal_library['poses']) and len(base_library['poses'])==42
    changed_ids={key for key,p in proposal_library['poses'].items()if transform_hash(p)!=transform_hash(base_library['poses'][key])}
    expected=set(changed_ids if expected_ids is None else expected_ids)
    rows=report['rows'];row_ids=[row['id']for row in rows]
    assert report['count']==len(rows)==len(expected) and len(row_ids)==len(set(row_ids)) and set(row_ids)==expected, 'Missing, duplicate or unrelated audit rows'
    assert report.get('errors')==[] and report.get('testSuitePassed') is True, 'Exact audit did not complete cleanly'
    assert report['geometricPassed']==sum(row['geometricPassed'] is True for row in rows), 'Inconsistent audited pass count'
    chord_records=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"],cwd=ROOT))
    chords={c['id']:c for c in chord_records}
    assert set(base_library['poses'])==set(chords) and changed_ids<=expected
    result=copy.deepcopy(base_library);decisions=[]
    for row in report['rows']:
        key=row['id'];p=proposal_library['poses'][key];chord=chords[key]
        assert row['poseTransformSha256']==transform_hash(p),'Stale or wrong chord transform'
        expected_contacts=sorted((t['finger'],t['string'],t['fret'],t['kind'])for t in gate.contacts(chord))
        actual_contacts=sorted((t['finger'],t['string'],t['fret'],t['kind'])for t in row['contacts'])
        actual_strings={s['number']:s for s in row['strings']}
        contacts_valid=actual_contacts==expected_contacts and all(t['passed'] is True and math.isfinite(t['actualOwnerPalmarSkinClearanceMm']) and -.00001<=t['actualOwnerPalmarSkinClearanceMm']<=.12 for t in row['contacts'])
        strings_valid=len(row['strings'])==6 and set(actual_strings)==set(range(1,7)) and all(s['fret']==chord['frets'][6-number] and math.isfinite(s['wholeSkinClearanceMm']) and (s['openStringPassed'] is True and s['wholeSkinClearanceMm']>=.2 if s['fret']==0 else s['openStringPassed'] is None)for number,s in actual_strings.items())
        valid=row['voicing']==chord['voicing'] and row['geometricPassed'] is True and type(row['skinAndClothSelfCrossingPairs']) is int and row['skinAndClothSelfCrossingPairs']==0 and type(row['woodSamplesInsideOver002Mm']) is int and row['woodSamplesInsideOver002Mm']==0 and math.isfinite(row['maximumWoodDepthMm']) and row['maximumWoodDepthMm']<=.02 and row['woodSamples']>0 and row['guitar'].get('status')=='tested' and type(row['guitar'].get('crossingPairs'))is int and row['guitar']['crossingPairs']==0 and contacts_valid and strings_valid
        changed=transform_hash(p)!=transform_hash(base_library['poses'][key])
        if valid and changed:
            p=copy.deepcopy(p);p['status']='needs-review';p['reviewed']=False;p['audit']={'collisionPassed':True,'contactPassed':True,'anatomyPassed':False,'multiViewReviewed':False};result['poses'][key]=p
        decisions.append({'id':key,'geometricPassed':valid,'changed':changed,'selected':valid and changed,'teachingApproved':False,'preservedOriginal':not(valid and changed)})
    return result,decisions

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--chords',default='all');ap.add_argument('--max-evaluations',type=int,default=35);ap.add_argument('--output',type=Path,default=ROOT/'docs/practice-final-delivery/solver');ap.add_argument('--refit-passing',action='store_true');ap.add_argument('--audit',action='store_true');ap.add_argument('--placement-weight',type=float,default=.45);args=ap.parse_args()
    if args.max_evaluations<1:ap.error('--max-evaluations must be positive')
    if not math.isfinite(args.placement_weight)or args.placement_weight<0:ap.error('--placement-weight must be finite and nonnegative')
    if args.output.exists()and any(args.output.iterdir()):ap.error('Use a fresh output directory so earlier evidence is preserved')
    ctx=load_context();ids=PRIORITY+[k for k in ctx['chords']if k not in PRIORITY]if args.chords=='all'else args.chords.split(',')
    if len(ids)!=len(set(ids))or not set(ids)<=set(ctx['chords']):ap.error('--chords must contain unique known chord IDs')
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'source-library.json').write_text(frozen_json(ctx['library']))
    (args.output/'sources.json').write_text(json.dumps({k:ctx[k]for k in ['library_sha','model_sha','chord_sha','rig_sha']},indent=2)+'\n')
    proposal=copy.deepcopy(ctx['library']);runs=[];attempted=[]
    for key in ids:
        if key in ctx['accepted'] and not args.refit_passing:runs.append({'id':key,'action':'preserve-exact-audited-seed'});print(key,'PRESERVED',flush=True);continue
        seed,seedid=choose_seed(ctx,ctx['chords'][key]);candidate,metrics=solve_chord(ctx,ctx['chords'][key],seed,args.max_evaluations,args.output/key,args.placement_weight);proposal['poses'][key]=candidate;attempted.append(key);runs.append({'id':key,'seed':seedid,'action':'bounded-central-fit','metrics':metrics});print(key,json.dumps(metrics),flush=True)
        (args.output/'progress.json').write_text(json.dumps({'sources':{k:ctx[k]for k in ['library_sha','model_sha','chord_sha','rig_sha']},'completedRuns':runs,'attempted':attempted,'runtimeWritten':False},indent=2)+'\n')
    proposal_file=args.output/'proposal-library.json';proposal_file.write_text(frozen_json(proposal));final=copy.deepcopy(ctx['library']);decisions=[]
    if args.audit and attempted:
        subprocess.run(['python',str(ROOT/'scripts/practice/check-hand-geometry.py'),'--library',str(proposal_file),'--chords',','.join(attempted),'--require','','--output',str(args.output/'exact-audit')],cwd=ROOT,check=True)
        report=json.loads((args.output/'exact-audit/summary.json').read_text());final,decisions=select_audited_replacements(ctx['library'],proposal,report,digest(proposal_file),ctx['model_sha'],ctx['chord_sha'],attempted)
    (args.output/'final-library.json').write_text(frozen_json(final));manifest={'solver':'one central actual-skin IK for42 immutable chord definitions','solverSourceSha256':digest(Path(__file__)),'sources':{k:ctx[k]for k in ['library_sha','model_sha','chord_sha','rig_sha']},'runs':runs,'decisions':decisions,'existingPassingPoses':sorted(ctx['accepted']),'teachingApprovals':0,'runtimeWritten':False,'auditRequiredForReplacement':True,'physicalAnimationValidated':False}
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
