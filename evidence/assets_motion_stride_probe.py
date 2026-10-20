import bpy,pathlib,json
ROOT=pathlib.Path('/workspace/HOMELESS');out=[]
for g in ['m','f']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30
 path=ROOT/'assets/originals/rocketbox/Assets/Animations/all_animations_max_motextr_xy'/(g+'_walk_neutral_01.max.fbx')
 bpy.ops.import_scene.fbx(filepath=str(path));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');start,end=rig.animation_data.action.frame_range
 points=[]
 for f in [start,end]:
  bpy.context.scene.frame_set(int(f));p=rig.matrix_world @ rig.pose.bones['Bip01 Pelvis'].head;points.append(p.copy())
 delta=points[1]-points[0];seconds=(end-start)/30
 out.append({'gender_prefix':g,'source':str(path.relative_to(ROOT)),'source_clip_frame_range':[start,end],'fps':30,'duration_s':seconds,'pelvis_world_displacement_m':list(delta),'nominal_planar_speed_mps':(delta.x**2+delta.y**2)**.5/seconds,'scope':'authored source root path; match playback rate to actual actor speed to reduce foot slide'})
(ROOT/'evidence/assets_motion_stride.json').write_text(json.dumps(out,indent=2)+'\n');print('SOURCE_STRIDE',json.dumps(out))
