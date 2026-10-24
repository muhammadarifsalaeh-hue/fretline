"""Check C contact arcs against actual posed GLB finger-pad skin, never a bone landmark alone."""
import argparse,sys,json,math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from skin_from_glb import evaluate
from audit_candidate import string_y,string_z,radii,wire


def main():
    p=argparse.ArgumentParser();p.add_argument('--glb',required=True);p.add_argument('--pose',required=True);p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else sys.argv[1:]);meshes,meta=evaluate(a.glb,a.pose,a.source);pose=meta.pop('poseData');offsets=pose.get('pressOffsetsBeforeWireMM',pose.get('pressOffsetsMm',[4,4,4]));paths=pose.get('stringPathsMm');bvhs={n:BVHTree.FromPolygons([Vector(v)for v in m['positions']],m['triangles'].tolist(),all_triangles=True)for n,m in meshes.items()}
    def point(x,n):
        if paths and paths.get(str(n)):
            for aa,bb in zip(paths[str(n)],paths[str(n)][1:]):
                if aa[0]<=x<=bb[0] and bb[0]>aa[0]:return Vector([aa[k]+(bb[k]-aa[k])*(x-aa[0])/(bb[0]-aa[0])for k in range(3)])
            raise ValueError(f'String{n}custompathdoesnotcover{x}')
        return Vector((x,string_y(x,n,offsets),string_z(x,n)))
    def closest(pt):
        best=(1e9,None,None,None,None)
        for name,bvh in bvhs.items():
            near,normal,ti,distance=bvh.find_nearest(pt)
            if distance<best[0]:best=(distance,name,ti,near,normal)
        distance,name,ti,near,normal=best;m=meshes[name];inds=m['triangles'][ti];tot=np.zeros(len(m['boneNames']));np.add.at(tot,m['jointIndices'][inds].ravel(),m['jointWeights'][inds].ravel());labels=sorted(zip(m['boneNames'],tot/3),key=lambda row:-row[1]);return {'distanceMm':distance,'mesh':name,'triangle':ti,'skinPointMm':list(near),'normal':list(normal),'boneWeights':[[n,float(w)]for n,w in labels[:4]],'dominantBone':labels[0][0]}
    rows={}
    for n,fret,key in[(2,1,'index'),(4,2,'midd'),(5,3,'ring')]:
        xa,xb=wire(fret-1),wire(fret);pa=point(xa,n);pb=point(xb,n);maxdepth=(-1,None);contact_labels={};contact_points=[]
        for x in np.arange(xa+.01,xb-.01,.04):
            pp=point(float(x),n);line=pa.y+(pb.y-pa.y)*(x-xa)/(xb-xa);depth=line-pp.y
            if depth>maxdepth[0]:maxdepth=(depth,pp)
            near=closest(pp);gap=near['distanceMm']-radii[n]
            if abs(gap)<.05:
                contact_labels[near['dominantBone']]=contact_labels.get(near['dominantBone'],0)+1;contact_points.append([x,gap,near['dominantBone']])
        depth,pp=maxdepth;near=closest(pp);gap=near['distanceMm']-radii[n];rows[str(n)]={'expectedFinger':key,'fret':fret,'maxPressureBelowSupportLineMm':depth,'pressurePointMm':list(pp),'distanceBeforeTargetWireMm':xb-pp.x,'skinGapAtPressureMm':gap,'actualClosestSkin':near,'associationCorrect':near['mesh']=='Hand'and near['dominantBone'].startswith(key+'_'),'pressureNormalPointsTowardBoard':near['normal'][1]<-.2,'nearContactDominantBoneCounts':contact_labels,'nearContactXRangeMm':[contact_points[0][0],contact_points[-1][0]]if contact_points else None}
    result={'meta':meta,'status':'Contact-association evidence only; full self/wood/string gates and visual anatomy remain separate','strings':rows};Path(a.out).write_text(json.dumps(result,indent=2));print(json.dumps(rows,indent=2),flush=True)

if __name__=='__main__':main()
