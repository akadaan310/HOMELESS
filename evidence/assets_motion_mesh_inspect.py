import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/workspace/HOMELESS/assets/runtime/rocketbox_male_adult_01.glb')
for o in bpy.data.objects:
 if o.type=='MESH':print('MESH',o.name,o.hide_render,o.hide_viewport,o.visible_get(),o.dimensions[:],len(o.data.polygons))
