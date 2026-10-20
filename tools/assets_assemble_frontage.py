#!/usr/bin/env python3
"""Arrange acquired architectural modules; preserve source artistic geometry.

This fictional frontage is a game composition, not a measured Tampa facade.
"""
import copy,json,pathlib,sys,os
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,pack_glb,metrics,sha,write_json
source=ASSETS/'originals/modular_factory_facade/modular_factory_facade_8k.gltf'
doc=json.loads(source.read_text());original={n.get('name'):n for n in doc['nodes']};nodes=[]
def place(source_name,x,y,z=0):
    node=copy.deepcopy(original[source_name]);node['translation']=[x,y,z];node['name']='frontage_'+str(len(nodes))+'_'+source_name;nodes.append(node)
for bay in range(6):
    x=3+bay*3
    door=bay in (1,4)
    place('wall_door_centered_large_01' if door else 'wall_window_centered_large_01',x,0)
    place('door_centered_large_01' if door else 'window_centered_large_01',x,0)
    place('wall_window_centered_large_01',x,3)
    place('window_centered_large_01',x,3)
    place('cornice01_standard_standard_01',x,6)
doc['nodes']=nodes;doc['scenes']=[{'name':'Fictional source-module commercial frontage','nodes':list(range(len(nodes)))}];doc['scene']=0
# Remove unreferenced source kit meshes, accessors and texture material sets.
used_meshes=sorted({n['mesh'] for n in nodes});meshmap={old:new for new,old in enumerate(used_meshes)};doc['meshes']=[doc['meshes'][i] for i in used_meshes]
for n in nodes:n['mesh']=meshmap[n['mesh']]
used_mats=sorted({p['material'] for m in doc['meshes'] for p in m['primitives'] if 'material' in p});matmap={old:new for new,old in enumerate(used_mats)};doc['materials']=[doc['materials'][i] for i in used_mats]
for m in doc['meshes']:
 for p in m['primitives']:
  if 'material' in p:p['material']=matmap[p['material']]
def texinfos(value):
 if isinstance(value,dict):
  for k,v in value.items():
   if k.endswith('Texture') and isinstance(v,dict) and 'index' in v:yield v
   else:yield from texinfos(v)
 elif isinstance(value,list):
  for v in value:yield from texinfos(v)
infos=list(texinfos(doc['materials']));used_tex=sorted({v['index'] for v in infos});texmap={old:new for new,old in enumerate(used_tex)};doc['textures']=[doc['textures'][i] for i in used_tex]
for v in infos:v['index']=texmap[v['index']]
used_img=sorted({t['source'] for t in doc['textures']});imgmap={old:new for new,old in enumerate(used_img)};doc['images']=[doc['images'][i] for i in used_img]
for t in doc['textures']:t['source']=imgmap[t['source']]
recipe=ASSETS/'recipes/tampa_fictional_frontage.gltf';recipe.parent.mkdir(parents=True,exist_ok=True)
for b in doc.get('buffers',[]):b['uri']=os.path.relpath(source.parent/b['uri'],recipe.parent)
for i in doc.get('images',[]):i['uri']=os.path.relpath(source.parent/i['uri'],recipe.parent)
write_json(recipe,doc)
output=ASSETS/'runtime/tampa_fictional_frontage.glb';pack_glb(recipe,output,1024);qa=metrics(output)
entry={'id':'tampa_fictional_frontage','canonical_id':'world://asset/tampa-fictional-frontage','category':'assembled-source-commercial-frontage','url':'https://polyhaven.com/a/modular_factory_facade','license':'CC0-1.0','status':'verified','source_file':str(recipe.relative_to(ROOT)),'files':[],'source_claim':'constructed fictional arrangement of acquired source mesh modules; not measured Tampa facade','variant_identity':'source meshes/materials retained; arrangement changed by recipe','variants':{'rendezvous-medium':{'path':str(output.relative_to(ROOT)),'url':'/assets/runtime/'+output.name,'sha256':sha(output),'bytes':output.stat().st_size,'metrics':qa,'texture_limit':1024,'world_bounds':{'min':[0,0,-.21],'max':[18,6.16,.07]},'recommended_transform':{'position':[6,0,-5],'rotation_degrees':[0,0,0],'scale':[1,1,1]},'render_status':'not-rendered'}},'import_status':'not-imported','cook_status':'not-cooked','scene_test':'not-rendered','source_mesh_pieces':len(nodes),'quality_gate':'art direction, collision and rendered fixture pending'}
write_json(ASSETS/'extras/tampa_fictional_frontage.json',entry)
print(json.dumps({'id':entry['id'],'bytes':output.stat().st_size,'triangles':qa['triangles'],'transform':entry['variants']['rendezvous-medium']['recommended_transform']}))
