"""Export the editable project current hand to canonical-mm GLB for independent audit.
The model remains UNAPPROVED until actual exported mesh/contact review passes.
"""
import bpy,os
from pathlib import Path
from mathutils import Matrix
root=Path(os.environ.get('FRETLINE_STAGE31_BLENDER','/tmp/fretline-stage31-assets/blender'))
project=Path(os.environ.get('FRETLINE_REPAIR_BLEND',str(root/'Fretline-C-Major-Repair.blend')))
target=Path(os.environ.get('FRETLINE_REPAIR_GLB',str(root/'current-hand-UNAPPROVED.glb')))
bpy.ops.wm.open_mainfile(filepath=str(project))
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');before=rig.matrix_world.copy()
try:
 rig.matrix_world=Matrix.Scale(1000,4)@before
 bpy.ops.object.select_all(action='DESELECT')
 for o in (rig,bpy.data.objects['Hand'],bpy.data.objects['Nails']):o.select_set(True)
 bpy.context.view_layer.objects.active=rig;bpy.context.view_layer.update()
 bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_yup=False,export_skins=True,export_animations=False,export_current_frame=True,export_rest_position_armature=False,export_materials='EXPORT',export_copyright='Hand ©2026 Emma L. D. Lieker; CC BY-NC 4.0; https://creativecommons.org/licenses/by-nc/4.0/; Fretline experimental C repair, NOT approved for teaching.')
 print('EXPORTED_UNAPPROVED_GLTF',str(target),flush=True)
finally:
 rig.matrix_world=before;bpy.context.view_layer.update()
