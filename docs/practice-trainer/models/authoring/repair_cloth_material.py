"""Remove a white exported cloth sheen without changing model geometry.

Run using Blender --background --python this_file.py. This updates the editable
source and exports the runtime model, preserving geometry and skin weights.
"""
import bpy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
native=ROOT/'docs/practice-trainer/models/authoring/MakeHuman_Left_Arm_Source_UNPOSED.blend'
bpy.ops.wm.open_mainfile(filepath=str(native))
material=bpy.data.materials['Black_Cotton_LongSleeve_Elvaerwyn']
material.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=0
bpy.ops.object.select_all(action='DESELECT')
for name in ('Fretline_Left_Hand_Rig','MakeHuman_Left_Hand_Forearm','Black_LongSleeve_Forearm'):
    bpy.data.objects[name].select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['Fretline_Left_Hand_Rig']
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb'),export_format='GLB',use_selection=True,export_skins=True,export_animations=False,export_yup=True,export_apply=False,export_extras=True,export_def_bones=True)
print('CLOTH_MATERIAL_UPDATED_WITHOUT_GEOMETRY_EDITS')
