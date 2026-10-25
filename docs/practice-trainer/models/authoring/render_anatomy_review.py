import bpy,json,os
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];OUT=Path('/tmp/fretline-trainer-assets/review');OUT.mkdir(parents=True,exist_ok=True)
if os.environ.get('FRETLINE_REVIEW_GLB')=='1':
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb'))
else:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'docs/practice-trainer/models/authoring/MakeHuman_Left_Arm_Source_UNPOSED.blend'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False
scene.render.resolution_x=768;scene.render.resolution_y=768;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
if scene.world is None:scene.world=bpy.data.worlds.new('ReviewWorld')
scene.world.color=(.13,.13,.13);scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-2.5
meta=json.loads((ROOT/'src/features/practice/assets/makehuman-left-arm.metadata.json').read_text());bones={x['name']:x for x in meta['bones']}
def conv(v):return Vector((v[0],-v[2],v[1]))
F=conv(Vector(bones['finger3-1.L']['sourceRestHeadMeters'])).normalized();W=conv(Vector(bones['finger5-1.L']['sourceRestHeadMeters'])-Vector(bones['finger2-1.L']['sourceRestHeadMeters'])).normalized();normal=F.cross(W).normalized()
target=conv(Vector(bones['finger3-1.L']['sourceRestHeadMeters'])*.8)
camera_data=bpy.data.cameras.new('AnatomyReviewCamera');camera=bpy.data.objects.new('AnatomyReviewCamera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO';camera_data.ortho_scale=.25
if os.environ.get('FRETLINE_REVIEW_MARKERS')=='1':
 for finger,landmark in meta['fingerSurfaceLandmarks'].items():
  for side,color in [('Positive',(1,.02,.01,1)),('Negative',(.01,.5,1,1))]:
   material=bpy.data.materials.new(f'{finger}_{side}');material.diffuse_color=color;material.use_nodes=True
   shader=material.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=color;shader.inputs['Emission Color'].default_value=color;shader.inputs['Emission Strength'].default_value=4
   bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.0016,location=conv(landmark[f'surfaceSide{side}']['centerMeters']))
   bpy.context.object.data.materials.append(material)
for label,d in [('positive-cross',normal),('negative-cross',-normal)]:
 up=(F-d*F.dot(d)).normalized();right=(-d).cross(up).normalized();up=d.cross(right).normalized();rotation=Matrix((right,up,d)).transposed();camera.rotation_euler=rotation.to_euler();camera.location=target+d*.65
 lights=[]
 for name,offset,energy,size in [('key',d*.5+F*.24+W*.2,40,.4),('fill',d*.35-F*.3-W*.25,20,.35),('rim',-d*.25+F*.2,25,.3)]:
  ld=bpy.data.lights.new(name,'AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;obj=bpy.data.objects.new(name,ld);scene.collection.objects.link(obj);obj.location=target+offset;obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler();lights.append(obj)
 scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
 for obj in lights:bpy.data.objects.remove(obj,do_unlink=True)
print('REVIEW_SAVED',str(OUT))
