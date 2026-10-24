"""Exact triangle-crossing audit of actual exported study-neck meshes and actual GLB hand.
Run in Blender; surface tangency is permitted, strict crossings are not.
"""
import sys,argparse,json,time,hashlib
import numpy as np
from collections import Counter
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
sys.path.insert(0,str(Path(__file__).resolve().parent))
from skin_from_glb import evaluate
from audit_candidate import winding


def cross_pairs(a,b):
    pairs=a['bvh'].overlap(b['bvh']);cross=[]
    for ia,ib in pairs:
        va=[a['vertices'][i]for i in a['faces'][ia]];vb=[b['vertices'][i]for i in b['faces'][ib]];na=(va[1]-va[0]).cross(va[2]-va[0]);nb=(vb[1]-vb[0]).cross(vb[2]-vb[0]);hits=[]
        if na.length<1e-10 or nb.length<1e-10:continue
        na.normalize();nb.normalize();da=[(p-va[0]).dot(na)for p in vb];db=[(p-vb[0]).dot(nb)for p in va]
        if not(min(da)<-1e-5 and max(da)>1e-5 and min(db)<-1e-5 and max(db)>1e-5):continue
        for vfrom,vto in[(va,vb),(vb,va)]:
            for edge in range(3):
                origin=vfrom[edge];delta=vfrom[(edge+1)%3]-origin;hit=intersect_ray_tri(*vto,delta,origin,True)
                if hit is None:continue
                t=(hit-origin).dot(delta)/delta.length_squared
                if 1e-5<t<1-1e-5:hits.append(list(hit))
        if hits:cross.append({'triangleA':ia,'triangleB':ib,'hitsMm':hits})
    return {'bvhPairs':len(pairs),'confirmedTrianglePairs':len(cross),'evidence':cross[:30],'evidenceTruncated':len(cross)>30}


def mesh(vertices,triangles):
    v=[Vector(p)for p in vertices];t=[tuple(int(i)for i in f)for f in triangles];return{'vertices':v,'faces':t,'bvh':BVHTree.FromPolygons(v,t,all_triangles=True,epsilon=0)}



def containment(a,b):
    """Finite handvertex/trianglecenter tests against watertight actual guitar solid."""
    bv=np.array([list(v)for v in b['vertices']]);bt=np.array(b['faces']);_,canonical=np.unique(np.round(bv,6),axis=0,return_inverse=True);edges=Counter()
    for tri in bt:
        ids=canonical[tri]
        for i,j in [(ids[0],ids[1]),(ids[1],ids[2]),(ids[2],ids[0])]:edges[tuple(sorted((int(i),int(j))))]+=1
    open_edges=sum(count!=2 for count in edges.values())
    if open_edges:return {'watertight':False,'nonManifoldOrBoundaryEdges':open_edges,'notAssumedClear':True}
    av=np.array([list(v)for v in a['vertices']]);at=np.array(a['faces']);points=np.concatenate([av,av[at].mean(1)]);lo=bv.min(0);hi=bv.max(0);mask=((points>=lo)&(points<=hi)).all(1);points=points[mask]
    wn=winding(points,bv,bt);inside=[];best=(0,None)
    for point,w in zip(points,wn):
        if w<.8:continue
        near,normal,ti,distance=b['bvh'].find_nearest(Vector(point))
        if distance>1e-4:
            inside.append(point.tolist())
            if distance>best[0]:best=(distance,point.tolist())
    return {'watertight':True,'samplesInBoundingBox':len(points),'interiorSamples':len(inside),'maxInteriorSurfaceDistanceMm':best[0],'interiorWitnessMm':best[1],'windingThreshold':.8}


def main():
    p=argparse.ArgumentParser();p.add_argument('--glb',required=True,type=Path);p.add_argument('--pose',required=True,type=Path);p.add_argument('--source',type=Path,default=Path('/tmp/fretline-stage3-assets/fk-source-gltf-compatible.json'));p.add_argument('--guitar',required=True,type=Path);p.add_argument('--out',required=True,type=Path);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:]);start=time.time()
    hand,meta=evaluate(args.glb,args.pose,args.source);hands={n:mesh(m['positions'],m['triangles'])for n,m in hand.items()};guitar=json.loads(args.guitar.read_text());rows=[]
    for g in guitar['meshes']:
        solid=mesh(g['vertices'],g['triangles'])
        for name,m in hands.items():
            result=cross_pairs(m,solid);inside=containment(m,solid) if g['role']!='string' else {'notApplied':'Open-ended stringtube; centerline/handdistance audit is separate.'};row={'handMesh':name,'guitarMesh':g['name'],'guitarRole':g['role'],'containment':inside,**result};rows.append(row)
            if result['confirmedTrianglePairs']:print('CROSS',name,g['name'],result['confirmedTrianglePairs'],flush=True)
    count=sum(r['confirmedTrianglePairs']for r in rows);insideCount=sum(r['containment'].get('interiorSamples',0)for r in rows);meta.pop('poseData',None);out={'status':'FAIL actual crossing or containment'if count or insideCount else'NO STRICT CROSSINGS FOUND; tangency/contact and containment still need separate audit','meta':meta,'guitarSHA256':hashlib.sha256(args.guitar.read_bytes()).hexdigest(),'confirmedTrianglePairs':count,'interiorSamples':insideCount,'rows':rows,'elapsedSeconds':time.time()-start,'limitations':['Exact edge-triangle witness counterexamples, not BVH bounding boxes alone.','Tangential touching is permitted; finite handvertex/centroid containment is tested against watertight actual wood/fret/nut solids. Open-ended stringtubes need separate centerline/handdistance audit.','Number counts triangle pairs, not distinct anatomical incidents.']};args.out.write_text(json.dumps(out,indent=2));print('RESULT',out['status'],count,round(out['elapsedSeconds'],3),flush=True)

if __name__=='__main__':main()
