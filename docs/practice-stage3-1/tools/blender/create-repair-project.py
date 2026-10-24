"""Editable Stage 3.1 C hand study. NOT an approved instructional pose.
Author hand ©2026 Emma L. D. Lieker / CC BY-NC 4.0.
No Fretline application or catalog edits. Run with Blender --background.
"""
import bpy,json,math,os,struct,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Euler
ASSETS=Path(os.environ.get('FRETLINE_STAGE3_SOURCE','/tmp/fretline-stage3-assets'))
OUT=Path(os.environ.get('FRETLINE_STAGE31_BLENDER','/tmp/fretline-stage31-assets/blender'))
POSE=Path(os.environ.get('FRETLINE_C_POSE',str(ASSETS/'c-pose-offset-attempt-0.json')))
OUT.mkdir(parents=True,exist_ok=True)
pose=json.loads(POSE.read_text());source=json.loads(Path(os.environ.get('FRETLINE_FK_SOURCE',str(ASSETS/'fk-source-gltf-compatible.json'))).read_text())
bpy.ops.wm.open_mainfile(filepath=str(ASSETS/'anatomical-hand.blend'))
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
for ob in list(bpy.context.scene.objects):
 if ob.animation_data:ob.animation_data_clear()
 if ob!=rig and ob.name not in ('Hand','Nails'):bpy.data.objects.remove(ob,do_unlink=True)
rig.name='C_MAJOR_REPAIR_RIG';rig.show_in_front=True;rig.data.display_type='STICK'
for bone in rig.pose.bones:
 bone.rotation_mode='XYZ';bone.location=(0,0,0);bone.scale=(1,1,1)
 bone.rotation_euler=pose['angles'][bone.name]
 for constraint in bone.constraints:constraint.mute=True
 bone['note']='Explicit experimental pose; source constraints retained muted for inspection, not a physiological certification.'
for meshdata in source['meshes']:
 ob=bpy.data.objects[meshdata['name']]
 assert len(ob.data.vertices)==len(meshdata['verts'])
 for mod in list(ob.modifiers):
  if mod.type=='ARMATURE':mod.use_deform_preserve_volume=False
  else:ob.modifiers.remove(mod)
 for group in list(ob.vertex_groups):ob.vertex_groups.remove(group)
 groups=[ob.vertex_groups.new(name=b['name']) for b in source['bones']]
 for vi,v in enumerate(meshdata['verts']):
  for group,w in zip(groups,v['weights']):
   if w:group.add([vi],w,'REPLACE')
 for polygon in ob.data.polygons:polygon.use_smooth=True
 ob['weight_authority']='Actual exported GLB normalized top4 weights; not native six-influence skin.'
q=pose['q'];rig.matrix_world=Matrix.Scale(.001,4)@Matrix.Translation(Vector(q[3:6]))@Euler(q[:3],'XYZ').to_matrix().to_4x4()@Matrix.Diagonal((-1,1,1,1))@Matrix.Scale(q[6],4)
rig['pose_status']='UNVALIDATED_STAGE_3_1_C_MAJOR';rig['pose_file']=str(POSE.name)
# Original optimized embedded images, without creative image changes.
raw=(ASSETS/'anatomical-hand-optimized.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+length]);binary=raw[28+length:]
texdir=OUT/'textures';texdir.mkdir(exist_ok=True);images={}
for im in g['images']:
 view=g['bufferViews'][im['bufferView']];a=view.get('byteOffset',0);data=binary[a:a+view['byteLength']]
 name=im['name'];path=texdir/(name+'.png');path.write_bytes(data)
 image=bpy.data.images.load(str(path),check_existing=True);image.pack();images[name]=image

def hand_material(name,skin):
 material=bpy.data.materials.new(name);material.use_nodes=True;nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
 out=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeBsdfPrincipled');links.new(shader.outputs['BSDF'],out.inputs['Surface'])
 shader.inputs['IOR'].default_value=1.4;shader.inputs['Roughness'].default_value=.48
 if skin:
  for image_name,input_name in [('skin_light','Base Color'),('skin_roughness','Roughness')]:
   image=images[image_name]
   if input_name!='Base Color':image.colorspace_settings.name='Non-Color'
   tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(tex.outputs['Color'],shader.inputs[input_name])
  images['skin_bump'].colorspace_settings.name='Non-Color';tex=nodes.new('ShaderNodeTexImage');tex.image=images['skin_bump'];bump=nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00008;links.new(tex.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],shader.inputs['Normal'])
  shader.inputs['Subsurface Weight'].default_value=.04;shader.inputs['Subsurface Radius'].default_value=(.001,.0006,.0003)
 else:shader.inputs['Base Color'].default_value=(.434154,.165132,.135633,1)
 return material
for name in ('Hand','Nails'):
 ob=bpy.data.objects[name];ob.data.materials.clear();ob.data.materials.append(hand_material('ActualGLB_'+name,name=='Hand'))
# Exactly the study guitar meshes used by the runtime diagnostic; mm -> metres.
data=json.loads((OUT/'study-guitar-meshes.json').read_text());collection=bpy.data.collections.new('GENERIC_STUDY_GUITAR');bpy.context.scene.collection.children.link(collection)
materials={}
for item in data['meshes']:
 coords=item['positions'];verts=[tuple(v*.001 for v in coords[i:i+3]) for i in range(0,len(coords),3)];idx=item['indices'];faces=[tuple(idx[i:i+3]) for i in range(0,len(idx),3)]
 mesh=bpy.data.meshes.new(item['name']);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(item['name'],mesh);collection.objects.link(ob)
 if item['uv']:
  uv=mesh.uv_layers.new(name='UVMap');uvs=item['uv']
  for loop in mesh.loops:uv.data[loop.index].uv=uvs[loop.vertex_index*2:loop.vertex_index*2+2]
 for polygon in mesh.polygons:polygon.use_smooth=True
 m=item['material'];key=tuple(m['color'])+(m['metalness'],m['roughness'])
 if key not in materials:
  material=bpy.data.materials.new('Study_'+item['name']);material.use_nodes=True;shader=material.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*m['color'],1);shader.inputs['Metallic'].default_value=m['metalness'];shader.inputs['Roughness'].default_value=m['roughness'];materials[key]=material
  if m['metalness']<.1 and max(m['color'])<.5:
   nodes=material.node_tree.nodes;links=material.node_tree.links;tex=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2,60,8);links.new(tex.outputs['Generated'],mapping.inputs[0]);noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=2;links.new(mapping.outputs[0],noise.inputs['Vector']);bump=nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00008;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],shader.inputs['Normal'])
 ob.data.materials.append(materials[key])
# Named contact guide empties, hidden in renders only (not any hand geometry).
guides=bpy.data.collections.new('C_MAJOR_CONTACT_GUIDES_NOT_HAND');bpy.context.scene.collection.children.link(guides)
offsets=pose.get('pressOffsetsBeforeWireMM',[4,4,4])
for finger,string,fret,offset in [(1,2,1,offsets[0]),(2,4,2,offsets[1]),(3,5,3,offsets[2])]:
 x=648*(1-2**(-fret/12))-offset;z=(string-3.5)*(35+17*x/648)/5
 ob=bpy.data.objects.new(f'Finger_{finger}_string_{string}_fret_{fret}',None);guides.objects.link(ob);ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=.004;ob.location=(x*.001,(-z*z/700+.75)*.001,z*.001);ob['instruction']=f'Finger {finger}, string {string}, fret {fret}; visual guide, not approved contact.'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Neutral_studio');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.045,.045,.045,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.35
for name,loc,energy,size in [('Key',(.05,.35,.22),25,.35),('Fill',(.1,.12,-.3),12,.3),('Back_rim',(.16,-.25,.1),15,.25)]:
 light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=size;ob=bpy.data.objects.new(name,light);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((.065,-.025,0))-ob.location).to_track_quat('-Z','Y').to_euler()
for name,loc,target in [('FRONT',(.065,.42,.005),(.065,-.025,0)),('SIDE',(.12,.02,.40),(.065,-.025,0)),('BACK',(.065,-.43,.01),(.065,-.025,0)),('PLAYER',(.10,.23,-.34),(.065,-.025,0))]:
 data=bpy.data.cameras.new(name);data.lens=42;cam=bpy.data.objects.new(name,data);scene.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
scene.camera=bpy.data.objects['FRONT'];scene['stage_status']='UNVALIDATED C MAJOR; independently inspect geometry before adopting.';scene['original_source']='https://github.com/emmalieker/anatomical-hand-model/tree/f27f19f55f8270b3108ea0b53ce5aa81c543ff7c';scene['license']='CC BY-NC 4.0, copyright 2026 Emma L. D. Lieker'
notes=bpy.data.texts.new('READ_ME_BEFORE_EDITING');notes.write('FRETLINE STAGE 3.1 — C MAJOR REPAIR WORKSPACE\nStatus: candidate only. No claim of a collision-free instructional hand.\nHuman hand: ©2026 Emma L. D. Lieker, CC BY-NC 4.0.\nOriginal pinned source: f27f19f55f8270b3108ea0b53ce5aa81c543ff7c\nhttps://github.com/emmalieker/anatomical-hand-model\nModifications: left reflection, candidate joint rotations, actual GLB four-weight authority, PBR height binding, packed textures, generic study guitar and named cameras.\nThe source artist rest mesh and all 21 anatomical bones are retained. Finger primitives and hidden finger substitutes are not used.\nSelect C_MAJOR_REPAIR_RIG > Pose Mode. Hand/Nails are the visible skinned source meshes. Constraints from the original are retained muted because candidate rotations are explicit; joint limits alone are not a safety guarantee.\nThe general study guitar is millimetres converted to metres; 648mm scale, 43mm nut, 350mm board radius, 21mm total neck depth. Never change its shape just to hide a failed hand collision.\nC: index B2 fret1, middle D4 fret2, ring A5 fret3. G3 and high e1 stay open. Low E6 is not strummed. Thumb pad belongs behind the neck, nail facing away.\nChoose FRONT/SIDE/BACK/PLAYER cameras. Examine both shaded geometry and wireframe, contact skin and full string path. Do not approve selected fingertip landmark distances alone.\nFor skin-weight edits: use max4 influences, normalize, preserve separate nail weights, compare exported GLB rather than assuming six-weight native skin is identical. Save a separate revision, then rerun the independent actual-GLB collision audit.\nThis file is a preparation artifact for repair and review; it does not modify the Fretline website or database.\n')
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_start=.001;area.spaces.active.clip_end=10
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Fretline-C-Major-Repair.blend'))
print('SAVED_EDITABLE_PROJECT',str(OUT/'Fretline-C-Major-Repair.blend'),flush=True)
