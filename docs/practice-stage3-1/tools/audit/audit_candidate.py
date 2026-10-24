"""Independent actual-GLB C Major collision research, run with Blender Python.
No app adoption. A successful script run does not imply an instructional pose passes.
"""
import argparse,json,math,sys,time
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
sys.path.insert(0,str(Path(__file__).resolve().parent))
from skin_from_glb import evaluate


def self_intersections(mesh, evidence_limit=1000):
    v=mesh['vertices'];faces=mesh['faces'];canon=mesh['canonicalIds'];bvh=mesh['bvh'];candidates=[];confirmed=[];coplanar=[]
    for a,b in bvh.overlap(bvh):
        if a>=b or set(canon[i] for i in faces[a])&set(canon[i] for i in faces[b]):continue
        candidates.append([a,b]);va=[v[i]for i in faces[a]];vb=[v[i]for i in faces[b]];na=(va[1]-va[0]).cross(va[2]-va[0]);nb=(vb[1]-vb[0]).cross(vb[2]-vb[0])
        if na.length<1e-9 or nb.length<1e-9:continue
        na.normalize();nb.normalize();da=[(p-va[0]).dot(na) for p in vb];db=[(p-vb[0]).dot(nb)for p in va];hits=[]
        if min(da)<-1e-5 and max(da)>1e-5 and min(db)<-1e-5 and max(db)>1e-5:
            for vfrom,vto in [(va,vb),(vb,va)]:
                for edge in range(3):
                    orig=vfrom[edge];delta=vfrom[(edge+1)%3]-orig;hit=intersect_ray_tri(*vto,delta,orig,True)
                    if hit is None:continue
                    t=(hit-orig).dot(delta)/delta.length_squared
                    if 1e-5<t<1-1e-5:hits.append(list(hit))
        if hits:confirmed.append({'pair':[a,b],'hitsMM':hits})
        elif abs(na.dot(nb))>.999999 and max(abs(d)for d in da)<1e-5:
            # Candidate is coplanar: retain explicitly rather than call it a verified clear region.
            coplanar.append([a,b])
    return {'bvhCandidates':len(candidates),'confirmedCrossingTrianglePairs':len(confirmed),'unresolvedCoplanarPairs':len(coplanar),'confirmedEvidence':confirmed[:evidence_limit],'coplanarCandidates':coplanar[:evidence_limit],'evidenceTruncated':len(confirmed)>evidence_limit}


def winding(points,vertices,triangles):
    """Generalized solid-angle winding; hand wrist is open, so values remain diagnostic."""
    tri=vertices[triangles];values=[]
    for start in range(0,len(points),40):
        p=np.array(points[start:start+40]);a=tri[None,:,0]-p[:,None];b=tri[None,:,1]-p[:,None];c=tri[None,:,2]-p[:,None];la=np.linalg.norm(a,axis=2);lb=np.linalg.norm(b,axis=2);lc=np.linalg.norm(c,axis=2)
        numerator=np.einsum('pti,pti->pt',a,np.cross(b,c));denominator=la*lb*lc+np.einsum('pti,pti->pt',a,b)*lc+np.einsum('pti,pti->pt',b,c)*la+np.einsum('pti,pti->pt',c,a)*lb
        values.extend(np.arctan2(numerator,denominator).sum(1)/(2*np.pi))
    return np.abs(values)


def neck_depth(p):
    x,y,z=p;half=21.5+5.5*min(1,max(0,x/324));top=-z*z/700;back=top-5-16*math.sqrt(max(0,1-(z/half)**2));return max(0,min(top-y,y-back,half-abs(z),x,330-x))


def fret_depth(p):
    x,y,z=p
    if x<0 or x>324 or abs(z)>21.5+5.5*x/324:return 0
    top=-z*z/700
    return max([0]+[max(0,1-math.sqrt(((x-wire(n))/1.1)**2+((y-top-.5)/.5)**2))*.5 for n in range(1,13)])


def sample_surfaces(mesh,step):
    v=mesh['vertices'];bestwood=(0,None,None,None);bestfret=(0,None,None,None);badwood=set();badfret=set();samples=0
    for ti,face in enumerate(mesh['faces']):
        a,b,c=[v[i]for i in face];div=max(1,math.ceil(max((a-b).length,(a-c).length,(b-c).length)/step))
        for i in range(div+1):
            for j in range(div+1-i):
                p=a+(b-a)*(i/div)+(c-a)*(j/div);samples+=1;wd=neck_depth(p);fd=fret_depth(p);bary=[1-i/div-j/div,i/div,j/div]
                if wd>bestwood[0]:bestwood=(wd,list(p),ti,bary)
                if fd>bestfret[0]:bestfret=(fd,list(p),ti,bary)
                if wd>.05:badwood.add(ti)
                if fd>.03:badfret.add(ti)
    return {'samples':samples,'maxWoodDepthMm':bestwood[0],'woodWitnessMm':bestwood[1],'woodTriangle':bestwood[2],'woodBarycentric':bestwood[3],'maxFretDepthMm':bestfret[0],'fretWitnessMm':bestfret[1],'fretTriangle':bestfret[2],'fretBarycentric':bestfret[3],'woodOver05MmTriangles':len(badwood),'fretOver03MmTriangles':len(badfret)}


wire=lambda n:648*(1-2**(-n/12))
string_z=lambda x,n:(n-3.5)*(35+17*x/648)/5
radii={6:.66,5:.455,4:.33,3:.23,2:.165,1:.125}

def string_y(x,n,offsets):
    def op(x):return -string_z(0,n)**2/700+1.4+radii[n]+((-string_z(324,n)**2/700+3+radii[n])-(-string_z(0,n)**2/700+1.4+radii[n]))*x/324
    if n not in [2,4,5]:return op(x)
    fret={2:1,4:2,5:3}[n];offset=offsets[{2:0,4:1,5:2}[n]];px=wire(fret)-offset
    nodes=[(0,op(0)),(px,-string_z(px,n)**2/700+.75),(wire(fret),-string_z(wire(fret),n)**2/700+1+radii[n]),(330,op(330))]
    for (xa,ya),(xb,yb)in zip(nodes,nodes[1:]):
        if xa<=x<=xb:return ya+(yb-ya)*(x-xa)/(xb-xa)
    return op(x)


def string_audit(meshes,offsets,step,custom_paths=None):
    def point_at(x,n):
        if custom_paths:
            points=custom_paths.get(str(n), custom_paths.get(n))
            if points:
                for a,b in zip(points,points[1:]):
                    if a[0]<=x<=b[0] and b[0]>a[0]:
                        t=(x-a[0])/(b[0]-a[0]);return Vector([a[i]+(b[i]-a[i])*t for i in range(3)])
                raise ValueError(f'Custom string{n} path does not spanx{x}')
        return Vector((x,string_y(x,n,offsets),string_z(x,n)))
    out={}
    for n in range(1,7):
        best=(1e9,None,None,None,None);intersection=[];allpoints=[];nearest=[]
        for i in range(math.ceil(330/step)+1):
            x=min(330,i*step);point=point_at(x,n);row=(1e9,None,None,None)
            for name,mesh in meshes.items():
                near,normal,ti,distance=mesh['bvh'].find_nearest(point)
                if distance<row[0]:row=(distance,name,ti,list(near))
            gap=row[0]-radii[n]
            if gap<best[0]:best=(gap,list(point),row[3],row[1],row[2])
            if gap<-.03:intersection.append(x)
            allpoints.append(list(point));nearest.append(row[0])
        # Sample winding at .5mm or existing finer step, diagnostics only (open wrist).
        stride=max(1,round(.5/step));pp=allpoints[::stride];wn=np.zeros(len(pp))
        for name,mesh in meshes.items():
            if name.lower().startswith('hand'):wn=np.maximum(wn,winding(pp,mesh['positions'],mesh['triangles']))
        deeply_inside=[pp[i][0] for i,w in enumerate(wn)if w>.8 and nearest[::stride][i]>radii[n]+.05]
        out[str(n)]={'role':'open'if n in[1,3]else'notStrummed'if n==6 else'fretted','minTubeSurfaceGapMm':best[0],'stringWitnessMm':best[1],'meshWitnessMm':best[2],'mesh':best[3],'triangle':best[4],'intersectionSamplesOver03Mm':len(intersection),'intersectionXRangeMm':[min(intersection),max(intersection)]if intersection else None,'strongWindingInsideSamples':len(deeply_inside),'strongWindingInsideXRangeMm':[min(deeply_inside),max(deeply_inside)]if deeply_inside else None}
        print('STRING',n,json.dumps(out[str(n)]),flush=True)
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--glb',type=Path,default=Path('/tmp/fretline-stage3-assets/anatomical-hand-optimized.glb'));parser.add_argument('--pose',type=Path);parser.add_argument('--source',type=Path,default=Path('/tmp/fretline-stage3-assets/fk-source-gltf-compatible.json'));parser.add_argument('--out',type=Path,required=True);parser.add_argument('--rest',action='store_true');parser.add_argument('--self-only',action='store_true');parser.add_argument('--baked-mm',action='store_true');parser.add_argument('--surface-step',type=float,default=.6);parser.add_argument('--string-step',type=float,default=.1)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:]);start=time.time();data,meta=evaluate(args.glb,args.pose,args.source,args.rest,args.baked_mm);meshes={}
    for name,m in data.items():
        vv=[Vector(p)for p in m['positions']];tt=[tuple(int(x)for x in t)for t in m['triangles']];meshes[name]={**m,'vertices':vv,'faces':tt,'bvh':BVHTree.FromPolygons(vv,tt,all_triangles=True,epsilon=0)}
    selves={name:self_intersections(m)for name,m in meshes.items()};print('SELF',json.dumps({n:{k:v for k,v in x.items()if k not in ['confirmedEvidence','coplanarCandidates']}for n,x in selves.items()}),flush=True)
    offsets=meta.get('poseData',{}).get('pressOffsetsBeforeWireMM',meta.get('poseData',{}).get('pressOffsetsMm',[4.,4.,4.]))if meta.get('poseData')else[4.,4.,4.]
    surfaces={}if args.self_only else{name:sample_surfaces(m,args.surface_step)for name,m in meshes.items()};strings={}if args.self_only else string_audit(meshes,offsets,args.string_step,meta.get('poseData',{}).get('stringPathsMm') if meta.get('poseData') else None)
    failed_self=any(x['confirmedCrossingTrianglePairs']or x['unresolvedCoplanarPairs']for x in selves.values());failed_hard=any(x['maxWoodDepthMm']>.05 or x['maxFretDepthMm']>.03 for x in surfaces.values());failed_string=any(x['minTubeSurfaceGapMm']<-.03 or x['strongWindingInsideSamples']for x in strings.values())
    meta.pop('poseData',None);report={'status':'FAIL numerical collision gate'if failed_self or failed_hard or failed_string else'PROVISIONAL CLEAR at sampled resolution; visual/anatomical review still required','meta':meta,'scope':'self-only control'if args.self_only else'actual GLB deformed geometry against generic canonical study neck and C string paths','tolerancesMm':{'wood':.05,'fret':.03,'tubeOverlap':.03},'surfaceSamplingStepMm':args.surface_step,'stringSamplingStepMm':args.string_step,'selfIntersections':selves,'surfaceCollisions':surfaces,'strings':strings,'elapsedSeconds':time.time()-start,'limitations':['Wood/fret analytic distances use canonical study design; final actual guitar triangle review still required for a positive result.','Finite sampling can find counterexamples but cannot prove absence of all collisions.','Hand wrist is open: winding magnitudes and nearest normals are diagnostics, never treated as reliable closed-mesh inside proof.','C point contact and human anatomy require separate finger association and visual review.','Numerical joint limits do not establish anatomically natural pose.']};args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2));print('RESULT',report['status'],round(report['elapsedSeconds'],2),str(args.out),flush=True)


if __name__=='__main__':main()
