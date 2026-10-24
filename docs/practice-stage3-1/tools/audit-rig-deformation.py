import bpy,json,math,time
from pathlib import Path
from mathutils import Vector,Matrix,Euler
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
P=Path('/tmp/fretline-stage3-assets');O=Path('/tmp/fretline-stage31-assets');O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'anatomical-hand.blend'))
a=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');h=bpy.data.objects['Hand'];nails=bpy.data.objects['Nails'];pose=json.loads((P/'c-pose-offset-attempt-0.json').read_text());top4=json.loads((P/'fk-source-gltf-compatible.json').read_text());source=json.loads((P/'fk-source.json').read_text());names=[b['name'] for b in source['bones']]
for o in [a,h,nails]:
 if o.animation_data:o.animation_data_clear()
for ob in [h,nails]:
 for m in ob.modifiers:
  if m.type!='ARMATURE':m.show_viewport=False;m.show_render=False
q=pose['q'];globalmm=Matrix.Translation(Vector(q[3:6]))@Euler(q[:3],'XYZ').to_matrix().to_4x4()@Matrix.Diagonal((-1,1,1,1))@Matrix.Scale(q[6],4);a.matrix_world=globalmm
constraints=[]
for pb in a.pose.bones:
 pb.rotation_mode='XYZ'
 for c in pb.constraints:
  c.mute=True
  d={k:getattr(c,k,None) for k in ['name','type','influence','owner_space','target_space','subtarget','mix_mode','use_x','use_y','use_z','invert_x','invert_y','invert_z','use_offset']};d['bone']=pb.name;d['target']=c.target.name if hasattr(c,'target') and c.target else None;constraints.append(d)
armmods=[m for m in h.modifiers if m.type=='ARMATURE'];origweights={o.name:[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices] for o in [h,nails]}
def setweights(top=False):
 for ob in [h,nails]:
  for group in ob.vertex_groups:group.remove(list(range(len(ob.data.vertices))))
  if top:
   mesh=next(m for m in top4['meshes'] if m['name']==ob.name)
   for vi,v in enumerate(mesh['verts']):
    for bi,w in enumerate(v['weights']):
     if w:ob.vertex_groups[names[bi]].add([vi],w,'REPLACE')
  else:
   for vi,weights in enumerate(origweights[ob.name]):
    for gi,w in weights:ob.vertex_groups[gi].add([vi],w,'REPLACE')
def selfcross(verts,faces):
 tree=BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0);pairs=[];regions={}
 for ia,ib in tree.overlap(tree):
  if ia>=ib or set(faces[ia])&set(faces[ib]):continue
  va=[verts[i] for i in faces[ia]];vb=[verts[i] for i in faces[ib]];na=(va[1]-va[0]).cross(va[2]-va[0]).normalized();nb=(vb[1]-vb[0]).cross(vb[2]-vb[0]).normalized();da=[(v-va[0]).dot(na) for v in vb];db=[(v-vb[0]).dot(nb) for v in va]
  if not(min(da)<-.0001 and max(da)>.0001 and min(db)<-.0001 and max(db)>.0001):continue
  hit=False
  for f,t in [(va,vb),(vb,va)]:
   for j in range(3):
    ori=f[j];end=f[(j+1)%3];d=end-ori;pt=intersect_ray_tri(*t,d,ori,True)
    if pt is not None and 1e-5<(pt-ori).dot(d)/d.length_squared<1-1e-5:hit=True
  if hit:
   pairs.append([ia,ib]);keys=[]
   for fi in [ia,ib]:
    weights=[sum(source['meshes'][0]['verts'][vi]['weights'][bi] for vi in faces[fi])/3 for bi in range(len(names))];keys.append(names[max(range(len(names)),key=lambda bi:weights[bi])])
   key=' | '.join(sorted(keys));regions[key]=regions.get(key,0)+1
 return len(pairs),dict(sorted(regions.items(),key=lambda kv:-kv[1]))
def points_and_faces(ob):
 dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);em=eo.to_mesh();verts=[ob.matrix_world@v.co for v in em.vertices];faces=[]
 for p in em.polygons:
  for i in range(1,len(p.vertices)-1):faces.append([p.vertices[0],p.vertices[i],p.vertices[i+1]])
 eo.to_mesh_clear();return verts,faces
out=[]
for weights in ['native6','export4']:
 setweights(weights=='export4')
 for case in ['rest','oldC','coupledC','sourceConstraintsC']:
  for dq in [False,True]:
   for pb in a.pose.bones:
    pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0) if case=='rest' else pose['angles'][pb.name]
    for c in pb.constraints:c.mute=case!='sourceConstraintsC'
   if case=='coupledC':
    for key in ['index','midd','ring','pinky']:
     pip=min(100,max(25,math.degrees(a.pose.bones[key+'_midd'].rotation_euler.z)));dip=.65*pip
     if key=='pinky':
      a.pose.bones[key+'_prox'].rotation_euler=(0,0,math.radians(20));pip=25;dip=16
     a.pose.bones[key+'_midd'].rotation_euler.z=math.radians(pip);a.pose.bones[key+'_dist'].rotation_euler.z=math.radians(dip)
   for ob in [h,nails]:
    for m in ob.modifiers:
     if m.type=='ARMATURE':m.use_deform_preserve_volume=dq
   bpy.context.view_layer.update();v,f=points_and_faces(h);count,regions=selfcross(v,f)
   row={'weights':weights,'case':case,'dualQuaternion':dq,'selfCrossingPairs':count,'regions':regions,'actualRotationDegrees':{pb.name:[math.degrees(x) for x in pb.matrix_basis.to_euler()] for pb in a.pose.bones}}
   out.append(row);print('CASE',weights,case,dq,count,regions,flush=True)
(O/'rig-deformation-audit.json').write_text(json.dumps({'sourceConstraints':constraints,'cases':out},indent=2))
