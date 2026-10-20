#!/usr/bin/env python3
"""Publish a consistent registry snapshot from completed per-asset records."""
import json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,SOURCES,catalog,write_json
entries=[]
for src in SOURCES:
 file=ASSETS/'originals'/src['id']/'source-manifest.json'
 if file.exists():
  entry=json.loads(file.read_text())
  if src.get('attribution'):entry['attribution']=src['attribution']
  entries.append(entry)
catalog(entries)
ids={e['id'] for e in json.loads((ASSETS/'catalog.json').read_text())['assets']}
coverage=[
 {'category':'modern-commercial-storefronts','required':20,'obtained_source_kits':sum(i in ids for i in ['modular_factory_facade','modular_urban_apartments_facade']),'assembled_frontage_bays':6 if 'tampa_fictional_frontage' in ids else 0,'distinct_complete_storefronts':1 if 'tampa_fictional_frontage' in ids else 0,'status':'FAIL','reason':'Two professional source architecture kits and one fictional composed frontage are not20 distinct complete modern storefront modules.'},
 {'category':'roadside-asset-classes','required':10,'obtained':sum(i in ids for i in ['street_lamp_01','fire_hydrant','modular_street_seating','concrete_road_barrier','metal_trash_can','modular_chainlink_fence','modular_electricity_poles','utility_box_01','water_manhole_cover']),'status':'FAIL','reason':'Nine acquired classes; traffic signal/road-sign system still unfilled.'},
 {'category':'detailed-passenger-vehicle','obtained':int('car_concept' in ids),'other_fixture':'covered_car is static covered artwork, not a moving vehicle replacement','status':'SOURCE-VERIFIED; road-contact/rig/glass/headlight render gate pending'},
 {'category':'rigged-authored-human','obtained':sum(i.startswith('rocketbox_') for i in ids),'status':'SOURCE-VERIFIED; final continuous contact/material/face-quality acceptance pending'},
 {'category':'retail-cafe-fixture','obtained':int('CoffeeCart_01' in ids),'status':'SOURCE-VERIFIED; complete cafe interior still unfilled'},
 {'category':'natural-environment','obtained_vegetation':int('jacaranda_tree' in ids),'obtained_hdr':int('urban_street_03' in ids),'status':'SOURCE-VERIFIED; regional palm set/rain assets unfilled'},
 {'category':'aircraft','obtained':int('aerobatic_plane' in ids),'status':'SOURCE-VERIFIED; airline/airport/balloon absent'},
 {'category':'water-transport','obtained':0,'status':'FAIL','reason':'No acquired boats/ferries/cargo/cruise/yachts with maritime rig/audio.'},
 {'category':'surface-PBR','obtained':int('asphalt_02' in ids),'status':'SOURCE-VERIFIED; BRDF buffer fixture pending'},
 {'category':'KTX2-GPU-compression','obtained_runtime_verified':0,'status':'FAIL','reason':'Baseline JPEG/PNG GLB is shipped; no exact-runtime KTX2/BasisU importer roundtrip completed.'},
]
write_json(ROOT/'evidence/assets_coverage.json',{'visual_content_acceptance':'FAIL','engine_render_acceptance':'BLOCKED: UE SDK/GPU missing','real_device_acceptance':'BLOCKED: device unavailable','categories':coverage,'source_rule':'Retrieved/verified/imported/cooked/rendered are separate claims. Candidate listings never count as installed.'})
print(json.dumps({'assets':len(ids),'visual_content_acceptance':'FAIL','runtime_total_bytes':sum(p.stat().st_size for p in (ASSETS/'runtime').iterdir() if p.is_file()),'largest_file_bytes':max(p.stat().st_size for p in (ASSETS/'runtime').iterdir() if p.is_file())}))
