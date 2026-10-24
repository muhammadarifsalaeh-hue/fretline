import os
"""Independent evaluated mesh audit in canonical millimetres (scratch only)."""
import bpy, json, math, time, sys
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
from pathlib import Path
P=Path(os.environ.get('FRETLINE_STAGE3_DIR', '/tmp/fretline-stage3-assets'));start=time.time()
source=json.loads((P/'fk-source.json').read_text());pose=json.loads((P/'c-pose-offset-attempt-0.json').read_text())
names=[b['name'] for b in source['bones']];rest=[Matrix(b['matrix']) for b in source['bones']];world=[]
for i,b in enumerate(source['bones']):
 parent=names.index(b['parent']) if b['parent'] else -1
 relative=rest[parent].inverted()@rest[i] if parent>=0 else rest[i]
 basis=Euler(pose['angles'][b['name']],'XYZ').to_matrix().to_4x4()
 world.append((world[parent]@relative if parent>=0 else relative)@basis)
skin=[w@r.inverted() for w,r in zip(world,rest)]
q=pose['q'];globalmm=Matrix.Translation(Vector(q[3:6]))@Euler(q[:3],'XYZ').to_matrix().to_4x4()@Matrix.Diagonal((-1,1,1,1))@Matrix.Scale(q[6],4)
meshes={}
runtime='--runtime' in sys.argv
for m in source['meshes']:
 verts=[]
 for v in m['verts']:
  co=Vector(v['co']);out=Vector((0,0,0))
  for weight,matrix in zip(v['weights'],skin):
   if weight:out+=(matrix@co)*weight
  verts.append(globalmm@out)
 nativeMap=list(range(len(verts)))
 # Reflection reverses orientation. Reverse winding to retain outward normals.
 triangles=[(t[0],t[2],t[1]) for t in m['triangles']]
 if runtime:
  import numpy as np
  runtimeData=np.load(P/('hand-runtime-transfer-points.npz' if m['name']=='Hand' else 'nails-runtime-transfer-points.npz'))
  verts=[Vector(v) for v in runtimeData['gltfPosedMM']]
  triangles=[(int(t[0]),int(t[2]),int(t[1])) for t in runtimeData['triangles']]
  nativeMap=[int(v) for v in runtimeData['nativeMap']]
 meshes[m['name']]={'vertices':verts,'faces':triangles,'nativeMap':nativeMap,'bvh':BVHTree.FromPolygons(verts,triangles,all_triangles=True,epsilon=0)}
wire=lambda fret:648*(1-2**(-fret/12))
top=lambda z:-z*z/700
half=lambda x:21.5+5.5*min(1,max(0,x/324))
back=lambda x,z:-5-z*z/700-16*math.sqrt(max(0,1-(z/half(x))**2))
def wood_depth(p):
 x,y,z=p
 return max(0,min(top(z)-y,y-back(x,z),half(x)-abs(z),x,324-x))
def fret_depth(p):
 x,y,z=p
 if x<0 or x>324 or abs(z)>half(x):return 0
 return max([0]+[max(0,1-math.sqrt(((x-wire(n))/1.1)**2+((y-top(z)-.5)/.5)**2))*.5 for n in range(1,13)])
def sample_surfaces(step):
 out={}
 for name,m in meshes.items():
  bestwood=(0,None,None,None);bestfret=(0,None,None,None);npoints=0;badwood=set();badfret=set()
  for ti,face in enumerate(m['faces']):
   a,b,c=[m['vertices'][i] for i in face];div=max(1,math.ceil(max((a-b).length,(a-c).length,(b-c).length)/step))
   for i in range(div+1):
    for j in range(div+1-i):
     p=a+(b-a)*(i/div)+(c-a)*(j/div);npoints+=1;wd=wood_depth(p);fd=fret_depth(p)
     bary=[1-i/div-j/div,i/div,j/div]
     if wd>bestwood[0]:bestwood=(wd,list(p),ti,bary)
     if fd>bestfret[0]:bestfret=(fd,list(p),ti,bary)
     if wd>.1:badwood.add(ti)
     if fd>.1:badfret.add(ti)
  out[name]={'sampleCount':npoints,'maxWoodDepthMm':bestwood[0],'woodWitnessMM':bestwood[1],'woodTriangle':bestwood[2],'woodWitnessBarycentric':bestwood[3],'woodTriangleVertexIndices':list(m['faces'][bestwood[2]]) if bestwood[2] is not None else None, 'maxFretConservativeDepthMm':bestfret[0],'fretWitnessMM':bestfret[1],'fretTriangle':bestfret[2],'fretWitnessBarycentric':bestfret[3],'woodOver01MmTriangles':len(badwood),'fretOver01MmTriangles':len(badfret)}
  print('SURFACE',name,json.dumps(out[name]),flush=True)
 return out
def string_z(x,n):return (n-3.5)*(35+17*x/648)/5
radii={6:.66,5:.455,4:.33,3:.23,2:.165,1:.125};pressed={2:(1,pose['pressOffsetsBeforeWireMM'][0]),4:(2,pose['pressOffsetsBeforeWireMM'][1]),5:(3,pose['pressOffsetsBeforeWireMM'][2])}
def open_y(x,n):
 return top(string_z(0,n))+1.4+radii[n]+(top(string_z(324,n))+3+radii[n]-(top(string_z(0,n))+1.4+radii[n]))*x/324
def string_y(x,n):
 if n not in pressed:return open_y(x,n)
 f,offset=pressed[n];px=wire(f)-offset;fz=string_z(wire(f),n)
 nodes=[(0,open_y(0,n)),(px,top(string_z(px,n))+.75),(wire(f),top(fz)+1+radii[n]),(324,open_y(324,n))]
 for (xa,ya),(xb,yb) in zip(nodes,nodes[1:]):
  if xa<=x<=xb:return ya+(yb-ya)*(x-xa)/(xb-xa)
 return open_y(x,n)
def closest_skin(point,name='Hand'):
 near,normal,index,distance=meshes[name]['bvh'].find_nearest(point)
 sign=1 if (point-near).dot(normal)>=0 else -1
 return distance*sign,near,normal,index
strings={}
for n in range(1,7):
 best=(1e9,None,None,None);penetrations=[]; nearContact=[];signedNearBest=(1e9,None,None,None)
 for i in range(3241):
  x=i/10;p=Vector((x,string_y(x,n),string_z(x,n)));dist,near,normal,ti=closest_skin(p);gap=abs(dist)-radii[n]
  if abs(dist)<radii[n]+2 and dist-radii[n]<signedNearBest[0]:signedNearBest=(dist-radii[n],list(p),list(near),ti)
  if gap<best[0]:best=(gap,list(p),list(near),ti)
  if gap<-.1:penetrations.append(x)
  if abs(gap)<.2:nearContact.append(x)
 strings[str(n)]={'minUnsignedSurfaceGapMm':best[0],'nearSurfaceSignedGapMm':signedNearBest[0] if signedNearBest[0]<1e8 else None,'nearSignedWitnessMM':signedNearBest[1],'stringWitnessMM':best[1],'skinWitnessMM':best[2],'skinTriangle':best[3],'samplesIntersectingSurfaceOver01Mm':len(penetrations),'intersectingXRangeMm':[min(penetrations),max(penetrations)] if penetrations else None,'nearContactXRangeMm':[min(nearContact),max(nearContact)] if nearContact else None,'radiusMm':radii[n]}
 print('STRING',n,json.dumps(strings[str(n)]),flush=True)
contacts={}
for n,(f,offset) in pressed.items():
 x=wire(f)-offset;p=Vector((x,string_y(x,n),string_z(x,n)));dist,near,normal,ti=closest_skin(p)
 contacts[str(n)]={'fret':f,'pressOffsetMM':offset,'skinSignedDistanceToStringCenterMm':dist,'gapFromStringSurfaceMm':dist-radii[n],'stringCenterMM':list(p),'closestSkinMM':list(near),'nearestSkinTriangle':ti}
print('CONTACTS',json.dumps(contacts),flush=True)
surface=sample_surfaces(.6)
hand=meshes['Hand'];overlap=hand['bvh'].overlap(hand['bvh']);candidates=[];properCrossings=[];exactSegmentCrossings=[]
for a,b in overlap:
 if a>=b or set(hand['nativeMap'][i] for i in hand['faces'][a])&set(hand['nativeMap'][i] for i in hand['faces'][b]):continue
 candidates.append([a,b])
 va=[hand['vertices'][i] for i in hand['faces'][a]];vb=[hand['vertices'][i] for i in hand['faces'][b]]
 na=(va[1]-va[0]).cross(va[2]-va[0]).normalized();nb=(vb[1]-vb[0]).cross(vb[2]-vb[0]).normalized()
 da=[(v-va[0]).dot(na) for v in vb];db=[(v-vb[0]).dot(nb) for v in va]
 if min(da)<-.0001 and max(da)>.0001 and min(db)<-.0001 and max(db)>.0001:
  properCrossings.append([a,b])
  hits=[]
  for vfrom,vto in [(va,vb),(vb,va)]:
   for edge in range(3):
    orig=vfrom[edge];end=vfrom[(edge+1)%3];delta=end-orig;hit=intersect_ray_tri(*vto,delta,orig,True)
    if hit is not None:
     t=(hit-orig).dot(delta)/delta.length_squared
     if 1e-5<t<1-1e-5:hits.append(list(hit))
  if hits:exactSegmentCrossings.append({'pair':[a,b],'edgeTriangleIntersectionsMM':hits})
regions=[]
for a,b in properCrossings:
 labels=[]
 for ti in [a,b]:
  weights=[sum(source['meshes'][0]['verts'][hand['nativeMap'][vi]]['weights'][bi] for vi in hand['faces'][ti])/3 for bi in range(len(names))]
  labels.append(names[max(range(len(names)),key=lambda i:weights[i])])
 regions.append(labels)
from collections import Counter
regionCounts=Counter(tuple(sorted(pair)) for pair in regions)
out={'status':'FAILED scratch pose: wood and nail penetration. Unsigned string tube/surface gaps are reliable distances; signed local nearest normals are diagnostic only, not closed-mesh inside classification. Confirmed edgeTriangle intersections listed separately from BVH candidates. Not a verified instructional pose.','geometry':'original top4-weight GLB mesh' if runtime else 'native fullweights Blender mesh','pose':'c-pose-offset-attempt-0.json','openStringActionBottomMm':[1.4,3.0],'stringSamplingStepMm':.1,'surfaceSamplingMaxEdgeStepMm':.6,'meshes':surface,'strings':strings,'activeFingerContacts':contacts,'nonAdjacentSelfOverlapCandidates':len(candidates),'selfOverlapPairs':candidates,'nonAdjacentPlaneCrossings':len(properCrossings),'crossingRegions':[{'bones':list(pair),'count':n} for pair,n in regionCounts.most_common()],'properCrossingPairs':properCrossings,'confirmedEdgeTriangleIntersections':len(exactSegmentCrossings),'exactSegmentCrossingEvidence':exactSegmentCrossings,'elapsedSeconds':time.time()-start}
(P/('pose-surface-runtime-audit.json' if runtime else 'pose-surface-audit.json')).write_text(json.dumps(out,indent=2));print('COMPLETE',out['elapsedSeconds'],len(candidates),'confirmed',len(exactSegmentCrossings),flush=True)
