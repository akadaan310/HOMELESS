"""Blender 4.3 batch conversion of licensed Rocketbox source art.
Run: blender -b --python tools/assets_rocketbox_convert.py
No mesh art is generated. Source rig motion is baked onto matched authored bones.
"""
import bpy,json,pathlib,sys,math
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/originals/rocketbox'
NAMES=['Male_Adult_01','Male_Adult_05','Female_Adult_03']
reports=[]
for name in NAMES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps=30
    folder=BASE/'Assets/Avatars/Adults'/name
    bpy.ops.import_scene.fbx(filepath=str(folder/'Export'/(name+'.fbx')),use_anim=False)
    target=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    for mesh in meshes:
        mesh.hide_render=False;mesh.hide_set(False)
    # Repair the original 3dsMax absolute texture paths using publisher files.
    texture_root=folder/'Textures'
    mats=[]
    for mat in bpy.data.materials:
        mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links
        prefix=mat.name
        if '.' in prefix:prefix=prefix.split('.')[0]
        color=texture_root/(prefix+'_color.tga')
        normal=texture_root/(prefix+'_normal.tga')
        if not color.exists():continue
        nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');pbr=nodes.new('ShaderNodeBsdfPrincipled');links.new(pbr.outputs['BSDF'],out.inputs['Surface'])
        pbr.inputs['Metallic'].default_value=0;pbr.inputs['Roughness'].default_value=.72
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(color),check_existing=True);links.new(tex.outputs['Color'],pbr.inputs['Base Color'])
        if 'opacity' in prefix:
            links.new(tex.outputs['Alpha'],pbr.inputs['Alpha']);mat.surface_render_method='DITHERED';mat.use_transparency_overlap=False
        if normal.exists():
            nt=nodes.new('ShaderNodeTexImage');nt.image=bpy.data.images.load(str(normal),check_existing=True);nt.image.colorspace_settings.name='Non-Color'
            nm=nodes.new('ShaderNodeNormalMap');links.new(nt.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],pbr.inputs['Normal'])
        mats.append({'material':mat.name,'color':str(color.relative_to(ROOT)),'normal':str(normal.relative_to(ROOT)) if normal.exists() else None,'conversion':'source diffuse+normal retained; legacy specular archived; dielectric roughness0.72 approximation pending lookdev'})
    clips=[];gender='f' if name.startswith('Female') else 'm'
    animations=[('Idle','all_animations_max_motextr_static',gender+'_idle_neutral_01.max.fbx'),('Walking','all_animations_max_motextr_xy',gender+'_walk_neutral_01.max.fbx'),('Talking','all_animations_max_motextr_static',gender+'_gestic_talk_neutral_01.max.fbx')]
    # Original source skeleton meshes are already in meters via FBX root .01.
    for clip,sub,file in animations:
        path=BASE/'Assets/Animations'/sub/file
        if not path.exists():raise RuntimeError('required authored clip absent: '+str(path))
        existing=set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(path))
        imported=set(bpy.data.objects)-existing
        source=next(o for o in imported if o.type=='ARMATURE')
        source_action=source.animation_data.action
        start,end=(int(v) for v in source_action.frame_range)
        matched=[b.name for b in target.data.bones if b.name in source.pose.bones]
        if len(matched)<70:raise RuntimeError('rig bone matching failed')
        # Both publisher skeletons share named Biped bones. Bake absolute source
        # pose matrices, preserving skin rest bindings; contact QA remains separate.
        baked=bpy.data.actions.new(clip);target.animation_data_create();target.animation_data.action=baked
        for frame in range(start,end+1,2):
            bpy.context.scene.frame_set(frame)
            matrices={n:source.pose.bones[n].matrix.copy() for n in matched}
            pelvis=matrices['Bip01 Pelvis'].translation
            for matrix in matrices.values():matrix.translation-=Vector((pelvis.x,pelvis.y,0))
            for bone in target.pose.bones:
                if bone.name not in matrices:continue
                kwargs={}
                if bone.parent and bone.parent.name in matrices:
                    kwargs={'parent_matrix':matrices[bone.parent.name],'parent_matrix_local':bone.parent.bone.matrix_local}
                # Explicit parent pose avoids dependency-graph evaluation order:
                # a child must never use the previous frame's parent transform.
                bone.matrix_basis=bone.bone.convert_local_to_pose(matrices[bone.name],bone.bone.matrix_local,invert=True,**kwargs)
                bone.rotation_mode='QUATERNION'
                bone.keyframe_insert('location',frame=frame-start)
                bone.keyframe_insert('rotation_quaternion',frame=frame-start)
                bone.keyframe_insert('scale',frame=frame-start)
        clips.append({'name':clip,'frames':end-start+1,'source':str(path.relative_to(ROOT)),'matched_bones':len(matched),'target_bones':len(target.data.bones),'retarget':'named publisher Biped matrix bake; in-place XY root; contact and art review pending'})
        target.animation_data.action=None
        track=target.animation_data.nla_tracks.new();track.name=clip;strip=track.strips.new(clip,0,baked);strip.name=clip
        for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
        for action in list(bpy.data.actions):
            if action!=baked and action.users==0:bpy.data.actions.remove(action)
    bpy.context.scene.frame_set(0)
    bpy.ops.object.select_all(action='DESELECT');target.select_set(True)
    for m in meshes:m.select_set(True)
    bpy.context.view_layer.objects.active=target
    # Exclude imported footstep helpers, preserve all authored visible geometry.
    dest=ROOT/'assets/runtime'/('rocketbox_'+name.lower()+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_skins=True,export_morph=True,export_materials='EXPORT',export_image_format='AUTO')
    reports.append({'id':'rocketbox_'+name.lower(),'path':str(dest.relative_to(ROOT)),'source_fbx':str((folder/'Export'/(name+'.fbx')).relative_to(ROOT)),'mesh_objects':[m.name for m in meshes],'materials':mats,'clips':clips,'blender_version':bpy.app.version_string,'units':'meters; +Y up glTF export','quality_state':'converted; rendered art/contact review pending'})
(ROOT/'evidence/assets_rocketbox_conversion.json').write_text(json.dumps(reports,indent=2)+'\n')
print('HOMELESS_ROCKETBOX_CONVERTED',json.dumps(reports))
