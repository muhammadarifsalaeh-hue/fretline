import bpy,json,os
from pathlib import Path
P=Path(os.environ.get("FRETLINE_STAGE3_DIR", "/tmp/fretline-stage3-assets"))
bpy.ops.wm.open_mainfile(filepath=str(P/'anatomical-hand.blend'))
a=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
a.animation_data_clear()
for b in a.pose.bones:
 b.rotation_mode='XYZ';b.rotation_euler=(0,0,0)
 for c in b.constraints:c.mute=True
bones=[]
for b in a.data.bones:
 bones.append({'name':b.name,'parent':b.parent.name if b.parent else None,'matrix':[list(row) for row in b.matrix_local],'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length})
names=[b['name'] for b in bones]
meshes=[]
for obj in bpy.context.scene.objects:
 if obj.type!='MESH' or obj.name not in ['Hand','Nails']:continue
 groups={g.index:g.name for g in obj.vertex_groups}
 verts=[]
 for v in obj.data.vertices:
  weights=[0.]*len(bones)
  for g in v.groups:
   if groups[g.group] in names:weights[names.index(groups[g.group])]=g.weight
  total=sum(weights)
  if total:weights=[w/total for w in weights]
  verts.append({'co':list(v.co),'weights':weights})
 tris=[]
 for p in obj.data.polygons:
  for i in range(1,len(p.vertices)-1):tris.append([p.vertices[0],p.vertices[i],p.vertices[i+1]])
 meshes.append({'name':obj.name,'matrix_world':[list(row) for row in obj.matrix_world],'verts':verts,'triangles':tris})
open(P/'fk-source.json','w').write(json.dumps({'bones':bones,'meshes':meshes,'armature_world':[list(row) for row in a.matrix_world]}))
print('EXTRACTED',len(bones),[(m['name'],len(m['verts']),len(m['triangles'])) for m in meshes])
