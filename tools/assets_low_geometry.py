#!/usr/bin/env python3
"""Measured bounded geometry variants; original art topology remains archived."""
import json,pathlib,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,pack_glb,metrics,sha,write_json
for name,ratio,limit in [('car_concept',.2,1024),('street_lamp_01',.4,1024)]:
 source=ASSETS/'runtime'/(name+'.glb');intermediate=ASSETS/'converted'/(name+'.low.simplified.glb');dest=ASSETS/'runtime'/(name+'.low.glb')
 subprocess.run(['npx','--yes','@gltf-transform/cli@4.2.1','simplify',str(source),str(intermediate),'--ratio',str(ratio),'--error','0.005'],check=True)
 pack_glb(intermediate,dest,limit);q=metrics(dest);before=metrics(source)
 maxbound=max(abs(before['mesh_space_bounds'][which][i]-q['mesh_space_bounds'][which][i]) for which in ('min','max') for i in range(3))
 e=json.loads((ASSETS/'originals'/name/'source-manifest.json').read_text())
 e['variants']['rendezvous-low']={'path':str(dest.relative_to(ROOT)),'url':'/assets/runtime/'+dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'metrics':q,'texture_limit':limit,'topology_deviation':1-q['triangles']/before['triangles'],'simplifier':{'tool':'@gltf-transform/cli4.2.1 meshoptimizer','target_ratio':ratio,'mesh_radius_error_limit':.005,'actual_triangle_ratio':q['triangles']/before['triangles'],'mesh_space_bounds_max_difference':maxbound},'silhouette_deviation':'image-space comparison pending; source geometry simplification constrained to0.5% radius','render_status':'exact PlayCanvas importer/device check pending'}
 write_json(ASSETS/'originals'/name/'source-manifest.json',e)
 print(json.dumps({'id':name,'bytes':dest.stat().st_size,'triangles_before':before['triangles'],'triangles_after':q['triangles'],'bounds_max_delta':maxbound}))
