"""Audit the editable source, packed images and continuous anatomical topology."""
import bpy,json,hashlib,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
native=ROOT/'docs/practice-trainer/models/authoring/MakeHuman_Left_Arm_Source_UNPOSED.blend'
bpy.ops.wm.open_mainfile(filepath=str(native))
arm=bpy.data.objects['Fretline_Left_Hand_Rig']
result={'nativeFile':str(native.relative_to(ROOT)),'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'bytes':native.stat().st_size,'boneCount':len(arm.data.bones),'allPoseTransformsIdentity':all(p.matrix_basis.is_identity for p in arm.pose.bones),'guitarPoseVerified':False,'meshes':[],'packedImages':[]}
for image in bpy.data.images:
    if image.source!='FILE':continue
    assert image.packed_file is not None,image.name
    result['packedImages'].append({'name':image.name,'dimensions':list(image.size),'packedBytes':image.packed_file.size,'sha256':hashlib.sha256(image.packed_file.data).hexdigest()})
for obj in bpy.data.objects:
    if obj.type!='MESH':continue
    mesh=obj.data
    assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
    graph=[set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a,b=edge.vertices;graph[a].add(b);graph[b].add(a)
    unseen=set(range(len(graph)));components=[]
    while unseen:
        pending=[unseen.pop()];count=0
        while pending:
            v=pending.pop();count+=1
            for adjacent in graph[v]:
                if adjacent in unseen:unseen.remove(adjacent);pending.append(adjacent)
        components.append(count)
    weights=[sum(g.weight for g in v.groups) for v in mesh.vertices]
    assert weights and min(weights)>.99999 and max(weights)<1.00001,obj.name
    entry={'name':obj.name,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'connectedComponentSizes':sorted(components,reverse=True),'allVerticesFinite':True,'weightSumRange':[min(weights),max(weights)],'armatureModifiers':[m.object.name for m in obj.modifiers if m.type=='ARMATURE'],'materialNames':[m.name for m in mesh.materials]}
    if 'Hand_Forearm' in obj.name:assert len(components)==1,'Hand and forearm must be one continuous surface'
    result['meshes'].append(entry)
assert len(arm.data.bones)==22
assert result['allPoseTransformsIdentity']
target=native.parent/'native-audit.json';target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
