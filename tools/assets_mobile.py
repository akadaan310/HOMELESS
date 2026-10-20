#!/usr/bin/env python3
"""Reproducible portable variants. Archival raw FBX/8K art is never overwritten."""
import json,pathlib,shutil,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,load_gltf,pack_glb,metrics,sha,write_json
for name in ['rocketbox_male_adult_01','rocketbox_male_adult_05','rocketbox_female_adult_03']:
 runtime=ASSETS/'runtime'/(name+'.glb')
 if not runtime.exists():continue
 converted=ASSETS/'converted'/runtime.name;converted.parent.mkdir(parents=True,exist_ok=True)
 doc,_=load_gltf(runtime)
 if not str(doc.get('asset',{}).get('generator','')).startswith('HOMELESS'):
  shutil.copyfile(runtime,converted)
 if not converted.exists():raise RuntimeError('Run Blender source conversion first')
 pack_glb(converted,runtime,2048);low=ASSETS/'runtime'/(name+'.low.glb');pack_glb(converted,low,1024)
 extra=ASSETS/'extras'/(name+'.json');entry=json.loads(extra.read_text()) if extra.exists() else {'id':name,'variants':{}}
 entry.setdefault('variants',{})['rendezvous-low']={'path':str(low.relative_to(ROOT)),'url':'/assets/runtime/'+low.name,'sha256':sha(low),'bytes':low.stat().st_size,'metrics':metrics(low),'texture_limit':1024,'topology_deviation':0,'silhouette_deviation':0,'rig_deviation':0,'render_status':'needs actual importer/render QA'};write_json(extra,entry)
# Static kit variants retain exact topology; texture tier alone changes.
for name,limit in [('sponza',512),('modular_factory_facade',1024),('modular_urban_apartments_facade',1024)]:
 subprocess.run([sys.executable,str(ROOT/'tools/assets.py'),'build','--ids',name,'--max-texture',str(limit)],check=True)
# Tree geometry is source-derived LOD; two bounded simplification passes are
# recorded separately. Settings are not an image-space visual equivalence proof.
file=ASSETS/'originals/jacaranda_tree/source-manifest.json'
if file.exists():
 entry=json.loads(file.read_text());runtime=ASSETS/'runtime/jacaranda_tree.glb'
 first=ASSETS/'converted/jacaranda_tree_simplified.glb';weld=ASSETS/'converted/jacaranda_tree_weld.glb';mobile=ASSETS/'converted/jacaranda_tree_mobile.glb'
 if not mobile.exists():
  for args in [('simplify',runtime,first,'--ratio','0.025','--error','0.01'),('weld',first,weld),('simplify',weld,mobile,'--ratio','0.2','--error','0.01')]:subprocess.run(['npx','--yes','@gltf-transform/cli@4.2.1',*[str(a) for a in args]],check=True)
 pack_glb(mobile,runtime,1024);q=metrics(runtime);ratio=q['triangles']/entry['source_metrics']['triangles']
 entry['variants']['rendezvous-medium']={'path':str(runtime.relative_to(ROOT)),'url':'/assets/runtime/'+runtime.name,'sha256':sha(runtime),'bytes':runtime.stat().st_size,'metrics':q,'texture_limit':1024,'topology_deviation':1-ratio,'simplifier':{'tool':'gltf-transform4.2.1/meshoptimizer','steps':['simplify ratio0.025 error0.01','weld','simplify ratio0.2 error0.01'],'mesh_radius_error_limit':.01,'actual_triangle_ratio':ratio,'cumulative_error_limit':'two passes each1% mesh radius; image-space deviation unmeasured'},'render_status':'image-space identity and device test pending'};write_json(file,entry)
subprocess.run([sys.executable,str(ROOT/'tools/assets_register_rocketbox.py')],check=True)
for p in (ASSETS/'runtime').iterdir():
 if p.is_file() and p.stat().st_size>25*1024*1024:raise RuntimeError('Portable bundle file exceeds25MiB: '+p.name)
print('Portable files are within25MiB. Source art parity/device gates remain separate.')
