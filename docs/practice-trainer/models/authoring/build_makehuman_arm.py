"""Author a continuous CC0 MakeHuman left arm and licensed fitted sleeve.
Run with Blender --background --factory-startup --python this_file.py.
Source paths are passed through FRETLINE_MODEL_SOURCE (default /tmp/fretline-trainer-assets).
No hand/chord pose in this source is certified by exporting or building it.
"""
import bpy, json, math, os, sys, hashlib
from pathlib import Path
from mathutils import Vector
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
SOURCE=Path(os.environ.get('FRETLINE_MODEL_SOURCE','/tmp/fretline-trainer-assets'))
OUT=Path(os.environ.get('FRETLINE_MODEL_OUTPUT',str(ROOT/'src/features/practice/assets')))
AUTHOR=ROOT/'docs/practice-trainer/models/authoring'
OUT.mkdir(parents=True,exist_ok=True)
BASE=SOURCE/'makehuman'

def obj_data(path):
    vertices=[];uvs=[];faces=[];faceuvs=[];groups=[];group=''
    for line in path.read_text().splitlines():
        bits=line.split()
        if not bits:continue
        if bits[0]=='v':vertices.append(tuple(map(float,bits[1:4])))
        elif bits[0]=='vt':uvs.append(tuple(map(float,bits[1:3])))
        elif bits[0]=='g':group=' '.join(bits[1:])
        elif bits[0]=='f':
            entries=[b.split('/') for b in bits[1:]]
            faces.append([int(e[0])-1 for e in entries]);faceuvs.append([int(e[1])-1 if len(e)>1 and e[1] else -1 for e in entries]);groups.append(group)
    return np.array(vertices),uvs,faces,faceuvs,groups

verts,uvs,faces,faceuvs,groups=obj_data(BASE/'base.obj')
rig=json.loads((BASE/'default.mhskel').read_text());weights=json.loads((BASE/'default_weights.mhw').read_text())['weights']
selected_bones=['lowerarm01.L','lowerarm02.L','wrist.L']+[f'metacarpal{i}.L' for i in range(1,5)]+[f'finger{i}-{j}.L' for i in range(1,6) for j in range(1,4)]
W=np.zeros((len(verts),len(selected_bones)),dtype=float)
for bi,name in enumerate(selected_bones):
    for vi,value in weights.get(name,[]):W[vi,bi]=value
leftweight=W.sum(axis=1)
joint=lambda name:Vector(verts[rig['joints'][name]].mean(axis=0))
wrist_source=joint(rig['bones']['wrist.L']['head'])
# MakeHuman Y-up units are 100mm. Blender uses Z-up metres; glTF restores Y-up.
def point(p):
    v=(Vector(p)-wrist_source)*.1
    return Vector((v.x,-v.z,v.y))
def direction(v):return Vector((v[0],-v[2],v[1]))

def skin_object(name,vertices,uvdata,faces0,uvfaces0,keepfaces,skinweights,material):
    used=sorted({vi for fi in keepfaces for vi in faces0[fi]});new={old:i for i,old in enumerate(used)}
    mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata([point(vertices[i]) for i in used],[],[[new[i] for i in faces0[fi]] for fi in keepfaces]);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material)
    layer=mesh.uv_layers.new(name='SourceUV')
    for poly,fi in zip(mesh.polygons,keepfaces):
        for li,uvindex in zip(poly.loop_indices,uvfaces0[fi]):
            layer.data[li].uv=uvdata[uvindex] if uvindex>=0 else (0,0)
        poly.use_smooth=True
    for bi,bone in enumerate(selected_bones):
        vg=obj.vertex_groups.new(name=bone)
        for old in used:
            row=skinweights[old].copy();row[row<1e-6]=0
            indices=np.argsort(row)[-4:];limited=np.zeros(len(row));limited[indices]=row[indices]
            total=limited.sum()
            if not total:limited[0]=1;total=1
            value=limited[bi]/total
            if value>0:vg.add([new[old]],float(value),'REPLACE')
    obj['preSubdivisionSourceVertexIndices']=used
    obj['anatomicalPoseStatus']='unavailable'
    return obj

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('HumanSkin_PBR_CC0');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.48,.245,.15,1);bs.inputs['Roughness'].default_value=.52;bs.inputs['Subsurface Weight'].default_value=.07;bs.inputs['Subsurface Radius'].default_value=(1,.4,.22)
skin_path=SOURCE/'garment/skins/young_caucasian_male/young_lightskinned_male_diffuse.png'
if skin_path.exists():
    image=bpy.data.images.load(str(skin_path))
    # Keep the licensed 2048px source detail while removing unnecessary PNG cost.
    bpy.context.scene.render.image_settings.file_format='JPEG';bpy.context.scene.render.image_settings.color_mode='RGB';bpy.context.scene.render.image_settings.quality=88
    optimized=SOURCE/'makehuman/skin-2048-optimized.jpg';image.save_render(str(optimized),scene=bpy.context.scene);bpy.data.images.remove(image)
    image=bpy.data.images.load(str(optimized));image.pack();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
keep=[i for i,f in enumerate(faces) if groups[i]=='body' and min(leftweight[v] for v in f)>.36]
body=skin_object('MakeHuman_Left_Hand_Forearm',verts,uvs,faces,faceuvs,keep,W,mat)

arm=bpy.data.armatures.new('Fretline_Left_Hand_Rig');arm_obj=bpy.data.objects.new('Fretline_Left_Hand_Rig',arm);bpy.context.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active=arm_obj;arm_obj.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for name in selected_bones:
    data=rig['bones'][name];bone=arm.edit_bones.new(name);bone.head=point(joint(data['head']));bone.tail=point(joint(data['tail']))
    plane=rig['planes'].get(data.get('rotation_plane'))
    if plane:
        points=[joint(n) for n in plane];normal=(points[1]-points[0]).cross(points[2]-points[0])
        if normal.length>1e-6:bone.align_roll(direction(normal))
for name in selected_bones:
    parent=rig['bones'][name]['parent']
    if parent in selected_bones:arm.edit_bones[name].parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');arm_obj.show_in_front=True
body.parent=arm_obj;mod=body.modifiers.new('AnatomicalSkinning','ARMATURE');mod.object=arm_obj;mod.use_deform_preserve_volume=False

# The source mesh supplies anatomical topology. One true subdivision level is
# applied before skinning, transferring UVs and skin weights, not primitive fingers.
bpy.context.view_layer.objects.active=body
sub=body.modifiers.new('AnatomicalSurfaceRefinement','SUBSURF');sub.levels=1;sub.render_levels=1
bpy.ops.object.modifier_move_up(modifier=sub.name);bpy.ops.object.modifier_apply(modifier=sub.name)

cloth_path=SOURCE/'garment/clothes/elvs_male_shirt_untucked_bd1'
if cloth_path.exists() and os.environ.get('FRETLINE_SKIP_SLEEVE')!='1':
    garment_obj=cloth_path/'mens_shirt_untuck_elvbhp1f.obj';garment_mhclo=cloth_path/'elvs_male_shirt_untucked_bd1.mhclo'
    cv,cuv,cf,cfuv,cg=obj_data(garment_obj)
    mappings=[];active=False
    for line in garment_mhclo.read_text().splitlines():
        bits=line.split()
        if not bits or bits[0].startswith('#'):continue
        if bits[0]=='verts':active=True;continue
        if active:
            if not bits[0][0].isdigit():break
            if len(bits)>=9:mappings.append(([int(x) for x in bits[:3]],[float(x) for x in bits[3:6]],[float(x) for x in bits[6:9]]))
    assert len(mappings)==len(cv),(len(mappings),len(cv))
    garment_weights=np.zeros((len(cv),len(selected_bones)))
    for index,(ref,bary,offset) in enumerate(mappings):
        cv[index]=(verts[ref]*np.array(bary)[:,None]).sum(axis=0)+np.array(offset)
        garment_weights[index]=(W[ref]*np.array(bary)[:,None]).sum(axis=0)
    csum=garment_weights.sum(axis=1)
    ckeep=[i for i,f in enumerate(cf) if min(csum[v] for v in f)>.33]
    clothmat=bpy.data.materials.new('Black_Cotton_LongSleeve_Elvaerwyn');clothmat.use_nodes=True
    # glTF's exported white sheen color overwhelms this dark source albedo.
    # Keep the rough cotton response without a white sheen layer.
    p=clothmat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.009,.01,.012,1);p.inputs['Roughness'].default_value=.88;p.inputs['Sheen Weight'].default_value=0
    tex=cloth_path/'shirttietex1.png'
    if tex.exists():
        im=bpy.data.images.load(str(tex));im.pack();node=clothmat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
        # The source albedo is already charcoal black; use it directly so native and glTF renders agree.
        clothmat.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    cloth=skin_object('Black_LongSleeve_Forearm',cv,cuv,cf,cfuv,ckeep,garment_weights,clothmat)
    cloth.parent=arm_obj;cm=cloth.modifiers.new('SleeveSkinning','ARMATURE');cm.object=arm_obj
    bpy.context.view_layer.objects.active=cloth;ss=cloth.modifiers.new('SourceClothSurface','SUBSURF');ss.levels=1;ss.render_levels=1;bpy.ops.object.modifier_move_up(modifier=ss.name);bpy.ops.object.modifier_apply(modifier=ss.name)
    # Correct source garment intersections against actual refined anatomical mesh.
    # This preserves the real shirt topology/folds; no primitive sleeve is invented.
    from mathutils.bvhtree import BVHTree
    body_mesh=body.data
    bvh=BVHTree.FromPolygons([v.co for v in body_mesh.vertices],[tuple(p.vertices) for p in body_mesh.polygons],all_triangles=False)
    corrected=0
    for iteration in range(3):
        for v in cloth.data.vertices:
            hit=bvh.find_nearest(v.co)
            if hit and hit[0] is not None:
                pos,normal,fi,distance=hit
                signed=(v.co-pos).dot(normal)
                if signed<.001:
                    v.co+=normal*(.001-signed);corrected+=1
    cloth.data.update();cloth['clearanceFitCorrections']=corrected
    # Retain the complete continuous forearm cloth panel. Four disconnected
    # ornamental cuff/button parts in this source intersected one another and
    # the cloth at rest. Identify the sleeve by spatial extent, not vertex count:
    # one tiny ornament has more vertices than the actual cloth panel.
    graph=[set() for _ in cloth.data.vertices]
    for edge in cloth.data.edges:
        a,b=edge.vertices;graph[a].add(b);graph[b].add(a)
    unseen=set(range(len(graph)));components=[]
    while unseen:
        pending=[unseen.pop()];component=[]
        while pending:
            v=pending.pop();component.append(v)
            for adjacent in graph[v]:
                if adjacent in unseen:unseen.remove(adjacent);pending.append(adjacent)
        components.append(component)
    def extent(component):
        points=[cloth.data.vertices[i].co for i in component]
        return sum((max(p[c] for p in points)-min(p[c] for p in points))**2 for c in range(3))
    keep_panel=set(max(components,key=extent))
    import bmesh
    bm=bmesh.new();bm.from_mesh(cloth.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep_panel],context='VERTS')
    bm.to_mesh(cloth.data);bm.free();cloth.data.update()
    cloth['author']='Elvaerwyn';cloth['license']='CC-BY';cloth['modifications']='Fitted to hm08 neutral body with MHCLO barycentric map; cropped to left forearm; tinted black; subdivided once; weights transferred from the same CC0 body.'
    cloth['modifications']+=' Removed four separate overlapping ornamental cuff/button components; retained the entire continuous forearm cloth panel for a plain black sleeve.'

arm_obj['source']='MakeHuman a8bc2d54ff0ac92e78ff71431b1023eda42bf482';arm_obj['millimetresPerAssetUnit']=1000;arm_obj['anatomicalPoseStatus']='unavailable';arm_obj['guitarPoseVerified']=False
for obj in bpy.context.selected_objects:obj.select_set(False)
arm_obj.select_set(True);body.select_set(True)
if bpy.data.objects.get('Black_LongSleeve_Forearm'):bpy.data.objects['Black_LongSleeve_Forearm'].select_set(True)
bpy.context.view_layer.objects.active=arm_obj
blend_path=AUTHOR/'MakeHuman_Left_Arm_Source_UNPOSED.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
glb_path=OUT/('makehuman-left-arm-unposed.glb' if os.environ.get('FRETLINE_SKIP_SLEEVE')=='1' else 'makehuman-left-arm-sleeved.glb');bpy.ops.export_scene.gltf(filepath=str(glb_path),export_format='GLB',use_selection=True,export_skins=True,export_animations=False,export_yup=True,export_apply=False,export_extras=True,export_def_bones=True)
metadata={'source':'MakeHuman hm08 base, default rig and authored weights','license':'CC0','millimetresPerAssetUnit':1000,'anatomicalPoseStatus':'unavailable','coordinateSystem':'GLB Y-up; MakeHuman X left-positive / Y vertical / Z front; wrist.L head is origin; no reflection','wrist':'wrist.L','forearm':['lowerarm01.L','lowerarm02.L'],'fingerChains':{name:[f'finger{i}-{j}.L' for j in range(1,4)] for name,i in [('thumb',1),('index',2),('middle',3),('ring',4),('little',5)]},'sourceWristMakeHumanUnits':list(wrist_source),'bones':[],'skinVertices':len(body.data.vertices),'skinPolygons':len(body.data.polygons),'sleeveIncluded':bool(bpy.data.objects.get('Black_LongSleeve_Forearm'))}
for name in selected_bones:
    b=arm.bones[name];local=b.matrix_local if not b.parent else b.parent.matrix_local.inverted()@b.matrix_local
    # This Blender-space matrix is auxiliary; actual GLB data follows in rig-data.json.
    metadata['bones'].append({'name':name,'parent':b.parent.name if b.parent else None,'blenderRestMatrixColumnMajor':[v for col in local.transposed() for v in col],'sourceRestHeadMeters':list((joint(rig['bones'][name]['head'])-wrist_source)*.1),'sourceRestTailMeters':list((joint(rig['bones'][name]['tail'])-wrist_source)*.1)})
metadata.update({'schemaVersion':1,'assetFile':glb_path.name,'assetSha256':hashlib.sha256(glb_path.read_bytes()).hexdigest(),'assetBytes':glb_path.stat().st_size,'expectedBoneNames':selected_bones,'rigSignature':'|'.join(sorted(selected_bones)),'license':'CC0 body, rig, weights and skin; CC-BY sleeve (version unspecified by source)' if metadata['sleeveIncluded'] else 'CC0','provenanceDocument':'docs/practice-trainer/models/README.md'})
(OUT/'makehuman-left-arm.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('FRETLINE_ASSET',json.dumps({'glb':str(glb_path),'blend':str(blend_path),'vertices':len(body.data.vertices),'polygons':len(body.data.polygons),'bones':len(arm.bones),'sleeve':metadata['sleeveIncluded']}))
