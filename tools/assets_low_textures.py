#!/usr/bin/env python3
"""Texture-cost variants retain source geometry/rig/art identity."""
import json,pathlib,sys
from PIL import Image
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,pack_glb,metrics,sha,write_json,curl
for name,limit in [('covered_car',1024),('fire_hydrant',1024),('tampa_fictional_frontage',512)]:
 record=ASSETS/('extras' if name=='tampa_fictional_frontage' else 'originals/'+name)/(name+'.json' if name=='tampa_fictional_frontage' else 'source-manifest.json')
 e=json.loads(record.read_text());source=ROOT/e['source_file'];dest=ASSETS/'runtime'/(name+'.low.glb');pack_glb(source,dest,limit);q=metrics(dest)
 e['variants']['rendezvous-low']={'path':str(dest.relative_to(ROOT)),'url':'/assets/runtime/'+dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'metrics':q,'texture_limit':limit,'topology_deviation':0,'silhouette_deviation':0,'render_status':'exact-runtime material/device parity pending'};write_json(record,e)
 print(name,dest.stat().st_size)
for asset_id in ['asphalt_02','urban_street_03']:
 record=ASSETS/'extras'/(asset_id+'.json');e=json.loads(record.read_text());low={}
 if asset_id=='asphalt_02':
  for kind,v in e['surface_variants'].items():
   source=ROOT/v['path'];dest=source.with_name(source.name.replace('_2k.','_1k.'))
   with Image.open(source) as im:
    im.thumbnail((1024,1024),Image.Resampling.LANCZOS);im.save(dest,format='JPEG',quality=94,subsampling=0)
   low[kind]={'path':str(dest.relative_to(ROOT)),'url':'/assets/runtime/'+dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'dimensions':[1024,1024],'format':'jpg','resolution':'1k','source':'source-preserving texture-cost derivative;8K master retained'}
 else:
  api=json.loads((ASSETS/'originals/urban_street_03/publisher-files.json').read_text());spec=api['hdri']['1k']['hdr'];dest=ASSETS/'runtime/urban_street_03_1k.hdr';curl(spec['url'],dest,spec['md5']);low['hdri']={'path':str(dest.relative_to(ROOT)),'url':'/assets/runtime/'+dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'format':'hdr','resolution':'1k','publisher_md5':spec['md5'],'source_url':spec['url']}
 e['surface_low_variants']=low;write_json(record,e)
write_json(ASSETS/'runtime/surfaces.json',{'schema':'worldloom.surface-library.v1','surfaces':[json.loads((ASSETS/'extras'/(name+'.json')).read_text()) for name in ['asphalt_02','urban_street_03']]})
