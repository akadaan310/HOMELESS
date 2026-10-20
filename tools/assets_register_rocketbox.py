#!/usr/bin/env python3
"""Record converted source rigs without asserting scene/contact acceptance."""
import json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,metrics,sha,write_json,catalog,SOURCES
collection=json.loads((ASSETS/'originals/rocketbox/source-manifest.json').read_text())
(ASSETS/'runtime/ROCKETBOX-LICENSE.txt').write_bytes((ASSETS/'originals/rocketbox/LICENSE.md').read_bytes())
for name in collection['selected_characters']:
 asset_id='rocketbox_'+name.lower();runtime=ASSETS/'runtime'/(asset_id+'.glb');converted=ASSETS/'converted'/runtime.name
 if not converted.exists() or not runtime.exists():continue
 source=metrics(converted);target=metrics(runtime)
 if not target['passed']:raise RuntimeError('geometry failed '+asset_id)
 if source['triangles']!=target['triangles'] or source['bones']!=target['bones']:raise RuntimeError('source rig mismatch '+asset_id)
 prefix='/'+name+'/'
 files=[f for f in collection['files'] if prefix in f['path'] or '/Animations/' in f['path'] or f['path'].endswith(('LICENSE.md','README.md'))]
 fbx='assets/originals/rocketbox/Assets/Avatars/Adults/'+name+'/Export/'+name+'.fbx'
 e={'id':asset_id,'canonical_id':'world://asset/'+asset_id,'category':'realistic-rigged-human','url':'https://github.com/microsoft/Microsoft-Rocketbox','license':'MIT','attribution':'Microsoft and Rocketbox contributors; assets/runtime/ROCKETBOX-LICENSE.txt','status':'verified','source_file':str(converted.relative_to(ROOT)),'source_master':fbx,'files':files,'source_metrics':source,'variants':{'unreal-source':{'path':fbx,'status':'source-ready; import pending'},'rendezvous-medium':{'path':str(runtime.relative_to(ROOT)),'url':'/assets/runtime/'+runtime.name,'sha256':sha(runtime),'bytes':runtime.stat().st_size,'metrics':target,'texture_limit':2048,'topology_deviation':0,'scale_m':1,'render_status':'not-rendered','material_conversion':'Original diffuse+normal images retained. Legacy specular map archived; roughness0.72 approximation requires BRDF lookdev.'}},'source_claim':'professional authored Rocketbox civilian with licensed rig, textures, matched source animation','animation_sets':['Idle','Walking','Talking'],'retarget':'named publisher Biped bones, in-place XY matrix bake; contact QA pending','import_status':'not-imported','cook_status':'not-cooked','scene_test':'not-rendered','quality_gate':'source/rig verified; contact, material and actual scene art review pending'}
 prior=ASSETS/'extras'/(asset_id+'.json')
 if prior.exists():
  old=json.loads(prior.read_text())
  if old.get('variants',{}).get('rendezvous-low'):e['variants']['rendezvous-low']=old['variants']['rendezvous-low']
 motion=ROOT/'evidence/assets_motion_qa.json'
 if motion.exists():
  qa=json.loads(motion.read_text())
  matching=next((r for r in qa.get('results',[]) if r.get('asset')==asset_id and r.get('sha256')==e['variants']['rendezvous-medium']['sha256']),None)
  if matching:
   e['motion_smoke']={'status':'passed-sampled-rig-smoke','evidence':'evidence/assets_motion_qa.json','scope':'actual CPU lookdev and sampled deformed meshes; continuous foot contact, BRDF and device gates pending'}
   e['variants']['rendezvous-medium']['render_status']='CPU sampled-rig smoke rendered; final PlayCanvas/device acceptance separate'
 write_json(ASSETS/'extras'/(asset_id+'.json'),e)
existing=json.loads((ASSETS/'catalog.json').read_text())['assets']
# Refresh publisher metadata corrected from authoritative license credits.
for e in existing:
 for s in SOURCES:
  if e['id']==s['id'] and s.get('attribution'):e['attribution']=s['attribution']
# Include newest supplemental records rather than a stale catalog copy.
extra_ids={p.stem for p in (ASSETS/'extras').glob('*.json')}
catalog([e for e in existing if e['id'] not in extra_ids])
print('Registered: '+', '.join(sorted(extra_ids)))
