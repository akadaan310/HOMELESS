"""Reproducible real-source acquisition and OSM normalization; never creates geometry."""
from pathlib import Path
import hashlib,json,urllib.request,xml.etree.ElementTree as ET,shutil,datetime
from email.utils import parsedate_to_datetime
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/geo'
CITIES={
 'tampa':[-82.516,27.952,-82.498,27.967],
 'marina':[-118.461,33.978,-118.449,33.986],
 'london':[-.131,51.505,-.123,51.511],
}

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, obj): path.write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')
def response_time(name):
 lines=(DATA/'raw'/f'{name}.headers').read_text().splitlines()
 date=[l[5:].strip() for l in lines if l.lower().startswith('date:')][-1]
 return parsedate_to_datetime(date).isoformat().replace('+00:00','Z')

def build(refresh=False):
 sources=[]
 for city,bbox in CITIES.items():
  url='https://www.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,bbox))
  path=DATA/'raw'/f'{city}.osm'
  if refresh or not path.exists():
   req=urllib.request.Request(url,headers={'User-Agent':'HOMELESS-WorldLoom/1.0 (source research fixture)'})
   with urllib.request.urlopen(req,timeout=60) as res:
    path.write_bytes(res.read()); (DATA/'raw'/f'{city}.headers').write_text(str(res.headers))
  root=ET.parse(path).getroot()
  def tags(e): return {t.attrib['k']:t.attrib['v'] for t in e.findall('tag')}
  nodes={n.attrib['id']:{'lat':float(n.attrib['lat']),'lon':float(n.attrib['lon']),'tags':tags(n),'version':int(n.attrib['version']),'timestamp':n.attrib['timestamp']} for n in root.findall('node')}
  ways=[]; buildings=[]; water=[]
  for w in root.findall('way'):
   t=tags(w); ids=[x.attrib['ref'] for x in w.findall('nd')]
   if not all(n in nodes for n in ids): continue
   row={'id':w.attrib['id'],'nodes':ids,'tags':t,'version':int(w.attrib['version']),'timestamp':w.attrib['timestamp']}
   if t.get('highway'): ways.append(row)
   if t.get('building') and t['building']!='no' and len(ids)>3 and ids[0]==ids[-1]: buildings.append(row)
   if t.get('natural')=='water' or t.get('waterway') or t.get('leisure')=='marina': water.append(row)
  relevant={n for w in ways+buildings+water for n in w['nodes']}
  data={'city':city,'bbox':bbox,'source_sha256':digest(path),'nodes':{n:v for n,v in nodes.items() if n in relevant},'ways':ways,'buildings':buildings,'water':water,'relations':[{'id':r.attrib['id'],'tags':tags(r),'members':[m.attrib for m in r.findall('member')]} for r in root.findall('relation') if tags(r).get('type')=='restriction']}
  write(DATA/f'{city}.json',data)
  sources.append({'id':f'osm:{city}','path':str(path.relative_to(ROOT)),'sha256':digest(path),'normalized_path':f'data/geo/{city}.json','normalized_sha256':digest(DATA/f'{city}.json'),'source_url':url,'license':'ODbL 1.0','terms_url':'https://www.openstreetmap.org/copyright','attribution':'© OpenStreetMap contributors','retrieved_utc':response_time(city),'retrieval_time_precision':'HTTP response Date; preserved raw/*.headers','release':'OSM API 0.6 live snapshot; per-object versions/timestamps preserved','bbox':bbox,'node_count':len(nodes),'highway_ways':len(ways),'building_footprints':len(buildings),'water_geometries':len(water)})
 for name,url,license,terms,release in [
 ('airports.geojson','https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_airports.geojson','public domain','https://www.naturalearthdata.com/about/terms-of-use/','Natural Earth 10m; imported release unknown'),
 ('ports.geojson','https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_ports.geojson','public domain','https://www.naturalearthdata.com/about/terms-of-use/','Natural Earth 10m; imported release unknown'),
 ('places.geojson','https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_populated_places_simple.geojson','public domain','https://www.naturalearthdata.com/about/terms-of-use/','Natural Earth 10m; imported release unknown'),
 ('wb_population.csv','https://raw.githubusercontent.com/datasets/population/master/data/population.csv','CC BY 4.0 (World Bank data)','https://data.worldbank.org/summary-terms-of-use','World Bank SP.POP.TOTL; years in rows; imported snapshot'),
 ]:
  path=DATA/'raw'/name
  shutil.copyfile(ROOT/'upstream/homeless-realms-0.1/data/raw'/name,path)
  sources.append({'id':name.split('.')[0],'path':str(path.relative_to(ROOT)),'sha256':digest(path),'source_url':url,'license':license,'terms_url':terms,'release':release,'acquisition':'unaltered masterpack input; remote revision not verified','retrieved_utc':None})
 weather=DATA/'raw/weather_tampa.json'
 sources.append({'id':'weather:tampa','path':str(weather.relative_to(ROOT)),'sha256':digest(weather),'source_url':'https://api.open-meteo.com/v1/forecast?latitude=27.9586&longitude=-82.505&current=temperature_2m,relative_humidity_2m,precipitation,cloud_cover,wind_speed_10m,weather_code&timezone=UTC','license':'CC BY 4.0','terms_url':'https://open-meteo.com/en/terms','attribution':'Weather data by Open-Meteo.com','release':'model estimate 2026-10-20T19:15 UTC; 900s interval','retrieved_utc':response_time('weather_tampa')})
 write(DATA/'sources.json',{'version':1,'sources':sources,'gaps':['No Overture adapter/download yet','No global route coverage beyond the three acquired OSM windows','No surveyed lane or sidewalk widths; mapped tags and centerlines only','No FAA airways, flight traces, navigable maritime/AIS lanes','No WorldPop/GHSL population grid','No weather outside pinned Tampa model snapshot','No terrain, photogrammetry or building interiors']})
 if __name__=='__main__': print(json.dumps({'sources':len(sources),'graphs':[{k:d[k] for k in ['id','node_count','highway_ways','building_footprints']} for d in sources if d['id'].startswith('osm:')]},indent=2))

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');args=p.parse_args();build(args.refresh)
