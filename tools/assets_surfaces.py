#!/usr/bin/env python3
"""Actual high resolution PolyHaven PBR/HDR masters and mobile variants."""
import concurrent.futures,json,pathlib,shutil,sys
from PIL import Image
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,curl,archive,sha,write_json
sources=[('asphalt_02','pbr-road-surface',[('Diffuse','jpg'),('nor_gl','jpg'),('Rough','jpg')]),('urban_street_03','hdr-environment',[('hdri','hdr')])]
entries=[]
for asset_id,category,maps in sources:
 out=ASSETS/'originals'/asset_id;api=out/'publisher-files.json';curl('https://api.polyhaven.com/files/'+asset_id,api);data=json.loads(api.read_text());files=[];variants={}
 for map_id,fmt in maps:
  for resolution in ['8k','2k']:
   spec=data[map_id][resolution][fmt];dest=out/pathlib.PurePosixPath(spec['url']).name;curl(spec['url'],dest,spec['md5']);files.append({**archive(dest),'url':spec['url'],'publisher_md5':spec['md5']})
   if resolution=='2k':
    runtime=ASSETS/'runtime'/dest.name;shutil.copyfile(dest,runtime)
    variants[map_id]={'path':str(runtime.relative_to(ROOT)),'url':'/assets/runtime/'+runtime.name,'sha256':sha(runtime),'bytes':runtime.stat().st_size,'resolution':resolution,'format':fmt,'source':'publisher-authored 2K derivative;8K source retained'}
    if fmt=='jpg':
     with Image.open(runtime) as im:variants[map_id]['dimensions']=[im.width,im.height];im.verify()
 entry={'id':asset_id,'canonical_id':'world://asset/'+asset_id,'category':category,'url':'https://polyhaven.com/a/'+asset_id,'license':'CC0-1.0','status':'verified','files':files,'source_file':files[0]['path'],'surface_variants':variants,'variants':{},'import_status':'not-imported','cook_status':'not-cooked','scene_test':'not-rendered','normal_map_convention':'OpenGL +Y','color_space':{'Diffuse':'sRGB','nor_gl':'linear','Rough':'linear','hdri':'linear HDR radiance'},'quality_gate':'source bytes validated; rendered BRDF/exposure gate pending'}
 write_json(ASSETS/'extras'/(asset_id+'.json'),entry);entries.append(entry)
write_json(ASSETS/'runtime/surfaces.json',{'schema':'worldloom.surface-library.v1','surfaces':entries})
print(json.dumps({'files':sum(len(e['files']) for e in entries),'assets':[e['id'] for e in entries]}))
