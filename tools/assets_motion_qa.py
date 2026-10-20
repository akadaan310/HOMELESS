"""Read-only Blender CPU render and numerical QC for sourced rig derivatives.
Run blender -b --python tools/assets_motion_qa.py. No cinematic acceptance.
"""
import bpy,json,pathlib,math,statistics,hashlib,sys
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence'; results=[]

def inspect(name):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(ROOT/'assets/runtime'/(name+'.glb')))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
 meshes=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.visible_get()]
 for t in rig.animation_data.nla_tracks:t.mute=True
 actions={a.name:a for a in bpy.data.actions}
 print('QC ACTIONS',name,[(k,list(v.frame_range)) for k,v in actions.items()],flush=True)
 result={'asset':name,'sha256':hashlib.sha256((ROOT/'assets/runtime'/(name+'.glb')).read_bytes()).hexdigest(),'bones':len(rig.data.bones),'animations':{},'renderer':'Blender4.3.2 Cycles CPU','scope':'format/skin deformation/sampled contact diagnostics; no device or cinematic acceptance','numeric_method':'scene-visible mesh polygon vertices; hidden importer helper excluded'}
 for key in ['Idle','Walking','Talking']:
  action=next((a for n,a in actions.items() if n.split('.')[0]==key or n.endswith('_'+key)),None)
  if not action:
   action=next((a for n,a in actions.items() if key in n),None)
  if not action:result['animations'][key]={'error':'action absent'};continue
  rig.animation_data.action=action
  start,end=action.frame_range
  rows=[]
  samples=[int(start+(end-start)*f) for f in [0,.125,.25,.375,.5,.625,.75,.875,1]]
  for frame in samples:
   bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();coords=[]
   for ob in meshes:
    evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh()
    used={v for face in mesh.polygons for v in face.vertices};coords.extend([evaluated.matrix_world @ mesh.vertices[v].co for v in used]);evaluated.to_mesh_clear()
   mins=[min(v[i] for v in coords) for i in range(3)];maxs=[max(v[i] for v in coords) for i in range(3)]
   feet={}
   for bn in ['Bip01 L Foot','Bip01 R Foot','Bip01 L Toe0','Bip01 R Toe0']:
    if bn in rig.pose.bones:
     p=rig.matrix_world @ rig.pose.bones[bn].head;feet[bn]=list(p)
   rows.append({'frame':frame,'mesh_world_min':mins,'mesh_world_max':maxs,'height_m':maxs[2]-mins[2],'feet_world':feet})
  result['animations'][key]={'frames':[start,end],'sampled_frames':rows,'min_mesh_floor_z_m':min(r['mesh_world_min'][2] for r in rows),'max_mesh_floor_z_m':max(r['mesh_world_min'][2] for r in rows),'sampled_height_range_m':[min(r['height_m'] for r in rows),max(r['height_m'] for r in rows)],'catastrophic_extent':any(r['height_m']>2.5 or r['height_m']<.7 for r in rows),'upright_human_bounds_warning':any(r['height_m']>2.05 for r in rows),'ground_penetration_warning':any(r['mesh_world_min'][2]<-.03 for r in rows)}
 # Render a representative sourced walking frame, actual textured skin.
 action=next((a for n,a in actions.items() if 'Walking' in n),next(iter(actions.values())))
 rig.animation_data.action=action;bpy.context.scene.frame_set(int(sum(action.frame_range)/2))
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=False
 scene.render.resolution_x=256;scene.render.resolution_y=384;scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new('QCWorld');scene.world.color=(.12,.12,.12)
 bpy.ops.object.camera_add(location=(2.6,-5,1.9));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.3;scene.camera=cam
 for location,energy,size in [((2,-4,4),450,4),((-3,-2,2),250,3),((0,3,3),400,3)]:
  bpy.ops.object.light_add(type='AREA',location=location);light=bpy.context.object;light.data.energy=energy;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
 scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/('assets_motion_'+name+'.png'));bpy.ops.render.render(write_still=True)
 result['preview']=str(pathlib.Path(scene.render.filepath).relative_to(ROOT))
 return result

selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['rocketbox_male_adult_01','rocketbox_male_adult_05','rocketbox_female_adult_03']
for name in selected:
 entry=inspect(name);results.append(entry)
 (OUT/('assets_motion_'+name+'.json')).write_text(json.dumps(entry,indent=2)+'\n')
 (OUT/'assets_motion_qa.json').write_text(json.dumps({'status':'sampled-rig-smoke-pass' if not any(c.get('catastrophic_extent') or c.get('upright_human_bounds_warning') or c.get('ground_penetration_warning') or c.get('error') for r in results for c in r['animations'].values()) else 'failed','results':results,'source_stride_ref':'evidence/assets_motion_stride.json','sampling':'9 frames per clip, visible polygon-referenced vertices only; actual walking Cycles CPU preview per model','contact_acceptance':'UNVERIFIED: sparse geometry samples bound penetration but do not prove continuous foot contact or footslide','material_acceptance':'UNVERIFIED: BRDF, normal orientation, skin and multi-light lookdev pending','device_acceptance':'UNVERIFIED: PlayCanvas/Samsung tests separate','cinematic_acceptance':False},indent=2)+'\n')
print('HOMELESS_MOTION_QA',json.dumps([{'asset':r['asset'],'clips':{k:{p:v for p,v in q.items() if p!='sampled_frames'} for k,q in r['animations'].items()}} for r in results]),flush=True)
