"""Source-witnessed Earth coordinates, conservative OSM routing and scene recipes.

The planet address space is complete. Detailed source topology is present only
inside acquired windows. Source facts and constructed presentation never merge.
"""
from __future__ import annotations
import csv
import hashlib
import heapq
import json
import math
import random
from collections import OrderedDict, defaultdict
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/geo'
A=6378137.0
F=1/298.257223563
B=A*(1-F)
E2=F*(2-F)
ANCHORS={'tampa':(27.95946425,-82.5055696,0),'marina':(33.982,-118.455,0),'london':(51.508,-.127,0)}


def normalize_lon(lon:float)->float:
    if not math.isfinite(lon): raise ValueError('longitude must be finite')
    return (float(lon)+180)%360-180


def _valid(lat,lon,height=0):
    if not all(math.isfinite(x) for x in (lat,lon,height)) or not -90<=lat<=90: raise ValueError('finite WGS84 coordinates, latitude in [-90,90], required')
    return float(lat),normalize_lon(lon),float(height)


def geodetic_to_ecef(lat,lon,height=0):
    lat,lon,height=_valid(lat,lon,height)
    p,l=math.radians(lat),math.radians(lon)
    n=A/math.sqrt(1-E2*math.sin(p)**2)
    return ((n+height)*math.cos(p)*math.cos(l),(n+height)*math.cos(p)*math.sin(l),(n*(1-E2)+height)*math.sin(p))


def ecef_to_geodetic(x,y,z):
    if not all(math.isfinite(v) for v in (x,y,z)): raise ValueError('finite ECEF required')
    p=math.hypot(x,y)
    if p<1e-8:
        if abs(z)<1e-8: raise ValueError('Earth center has no unique geodetic coordinate')
        return (math.copysign(90,z),0.0,abs(z)-B)
    lon=math.atan2(y,x)
    lat=math.atan2(z,p*(1-E2))
    for _ in range(20):
        n=A/math.sqrt(1-E2*math.sin(lat)**2)
        nxt=math.atan2(z+E2*n*math.sin(lat),p)
        if abs(nxt-lat)<1e-15:
            lat=nxt; break
        lat=nxt
    n=A/math.sqrt(1-E2*math.sin(lat)**2)
    height=p/math.cos(lat)-n if abs(math.cos(lat))>1e-8 else z/math.sin(lat)-n*(1-E2)
    return (math.degrees(lat),normalize_lon(math.degrees(lon)),height)


def _basis(origin):
    p,l=map(math.radians,_valid(*origin)[:2])
    return ((-math.sin(l),math.cos(l),0),(-math.sin(p)*math.cos(l),-math.sin(p)*math.sin(l),math.cos(p)),(math.cos(p)*math.cos(l),math.cos(p)*math.sin(l),math.sin(p)))


def geodetic_to_enu(lat,lon,height=0,*,origin):
    point=geodetic_to_ecef(lat,lon,height);base=geodetic_to_ecef(*origin)
    d=[a-b for a,b in zip(point,base)]
    return tuple(sum(a*b for a,b in zip(row,d)) for row in _basis(origin))


def enu_to_geodetic(east,north,up,*,origin):
    local=(east,north,up);basis=_basis(origin);base=geodetic_to_ecef(*origin)
    return ecef_to_geodetic(*(base[j]+sum(local[i]*basis[i][j] for i in range(3)) for j in range(3)))


def geodesic_distance(lat1,lon1,lat2,lon2):
    """Karney WGS84 inverse when installed, Vincenty for ordinary pairs otherwise.

    The optional fallback is explicitly exposed in overview. It is not used to
    claim antipodal precision; it returns authalic-sphere distance if no converge.
    """
    lat1,lon1,_=_valid(lat1,lon1);lat2,lon2,_=_valid(lat2,lon2)
    try:
        from geographiclib.geodesic import Geodesic
        return Geodesic.WGS84.Inverse(lat1,lon1,lat2,lon2)['s12']
    except ImportError: pass
    u1,u2=math.atan((1-F)*math.tan(math.radians(lat1))),math.atan((1-F)*math.tan(math.radians(lat2)))
    ll=math.radians(normalize_lon(lon2-lon1)); lam=ll
    for _ in range(100):
        ss=math.hypot(math.cos(u2)*math.sin(lam),math.cos(u1)*math.sin(u2)-math.sin(u1)*math.cos(u2)*math.cos(lam))
        if ss<1e-15: return 0.0
        cs=math.sin(u1)*math.sin(u2)+math.cos(u1)*math.cos(u2)*math.cos(lam)
        sigma=math.atan2(ss,cs);sa=math.cos(u1)*math.cos(u2)*math.sin(lam)/ss;ca2=1-sa*sa
        c2sm=cs-2*math.sin(u1)*math.sin(u2)/ca2 if ca2>1e-15 else 0
        cc=F/16*ca2*(4+F*(4-3*ca2))
        new=ll+(1-cc)*F*sa*(sigma+cc*ss*(c2sm+cc*cs*(-1+2*c2sm*c2sm)))
        if abs(new-lam)<1e-12: break
        lam=new
    else:
        p1,p2=map(math.radians,(lat1,lat2));h=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(ll/2)**2
        return 6371007.1809*2*math.asin(min(1,math.sqrt(h)))
    usq=ca2*(A*A-B*B)/(B*B)
    aa=1+usq/16384*(4096+usq*(-768+usq*(320-175*usq)))
    bb=usq/1024*(256+usq*(-128+usq*(74-47*usq)))
    ds=bb*ss*(c2sm+bb/4*(cs*(-1+2*c2sm*c2sm)-bb/6*c2sm*(-3+4*ss*ss)*(-3+4*c2sm*c2sm)))
    return B*aa*(sigma-ds)


@lru_cache(maxsize=1)
def sources(): return json.loads((DATA/'sources.json').read_text())


def _source(city): return next(s for s in sources()['sources'] if s['id']=='osm:'+city)


@lru_cache(maxsize=2)
def load_graph(city='tampa'):
    if city not in ANCHORS: raise ValueError('source graph unavailable')
    path=DATA/f'{city}.json'
    raw=path.read_bytes()
    expected=_source(city)['normalized_sha256']
    if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('normalized source checksum mismatch')
    return json.loads(raw)


def tampa_anchor():
    return {'lat':ANCHORS['tampa'][0],'lon':ANCHORS['tampa'][1],'height':0,'source_node_ids':['2057042478','1603574189'],'method':'midpoint of shared OSM nodes on both named ways; dual carriageway intersection','source_ref':'osm:tampa','vertical_datum':'ellipsoidal origin 0 chosen for local chart; terrain absent'}


def way_allowed(tags,mode='walk'):
    highway=tags.get('highway','')
    if tags.get('area')=='yes' or tags.get('access') in ('no','private') or tags.get('construction') or highway in ('construction','proposed','raceway'): return False
    if mode=='walk':
        if tags.get('foot') in ('no','private') or highway in ('motorway','motorway_link','trunk','trunk_link','cycleway'): return False
        # Separate sidewalks must be followed in their own geometry. Primary
        # centerlines with sidewalk tags are not invented sidewalk centerlines.
        return highway in ('footway','pedestrian','path','steps','living_street','residential','service','unclassified') or tags.get('foot') in ('yes','designated')
    if mode=='cycle':
        return tags.get('bicycle') not in ('no','private') and highway not in ('motorway','motorway_link','steps','footway','pedestrian')
    if mode=='drive':
        return tags.get('motor_vehicle') not in ('no','private') and tags.get('vehicle') not in ('no','private') and highway in ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','residential','service','unclassified','living_street')
    return False


@lru_cache(maxsize=6)
def _adjacency(city,mode):
    graph=load_graph(city); adj=defaultdict(list)
    for way in graph['ways']:
        t=way['tags']
        if not way_allowed(t,mode): continue
        direction=t.get('oneway')
        if mode=='walk': direction=t.get('oneway:foot','no')
        if mode=='cycle' and t.get('oneway:bicycle')=='no': direction='no'
        if direction is None and t.get('junction')=='roundabout' and mode!='walk': direction='yes'
        ids=way['nodes']
        for a,b in zip(ids,ids[1:]):
            pa,pb=graph['nodes'][a],graph['nodes'][b]
            length=geodesic_distance(pa['lat'],pa['lon'],pb['lat'],pb['lon'])
            if length<.001: continue
            edge={'length_m':length,'way_id':way['id'],'road_class':t['highway'],'name':t.get('name'),'crossing':t.get('footway')=='crossing' or t.get('crossing') is not None}
            if direction!='-1': adj[a].append({'to':b,**edge})
            if direction not in ('yes','1','true'): adj[b].append({'to':a,**edge})
    return dict(adj)


def adjacency(graph,mode='walk'): return _adjacency(graph['city'],mode)


def _nearest(graph,adj,point,max_distance=250):
    lat,lon=point[:2];_valid(lat,lon)
    ranked=((geodesic_distance(lat,lon,graph['nodes'][n]['lat'],graph['nodes'][n]['lon']),n) for n in adj)
    distance,node=min(ranked,default=(float('inf'),None))
    return node if distance<=max_distance else None


def _spawn(graph,adj):
    origin=ANCHORS[graph['city']]
    # A node on an explicit footway/path, not a vehicle carriageway.
    preferred={n for w in graph['ways'] if w['tags'].get('highway') in ('footway','pedestrian','path') and way_allowed(w['tags'],'walk') for n in w['nodes'] if n in adj}
    pool=preferred or set(adj)
    return min(pool,key=lambda n:geodesic_distance(*origin[:2],graph['nodes'][n]['lat'],graph['nodes'][n]['lon']))


def _dijkstra(adj,start,end=None,max_distance=400):
    distances={start:0.0};parent={};queue=[(0.0,start)]
    while queue:
        d,u=heapq.heappop(queue)
        if d!=distances[u]:continue
        if u==end: break
        if end is None and d>max_distance: continue
        for edge in adj.get(u,[]):
            v=edge['to'];nd=d+edge['length_m']
            if end is None and nd>max_distance: continue
            if nd<distances.get(v,float('inf')):
                distances[v]=nd;parent[v]=u;heapq.heappush(queue,(nd,v))
    if end is None: end=max(distances,key=lambda n:(distances[n],n))
    if end not in distances:return [],0
    path=[end]
    while path[-1]!=start: path.append(parent[path[-1]])
    return list(reversed(path)),distances[end]


def _canonical_hash(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def _graph_ref(city):
    s=_source(city)
    return {'city':city,'source_url':s['source_url'],'sha256':s['sha256'],'normalized_sha256':s['normalized_sha256'],'license':s['license'],'attribution':s['attribution'],'revision':s['release']}


def _bearing(a,b):
    lat1,lat2=map(math.radians,(a['lat'],b['lat']));dl=math.radians(normalize_lon(b['lon']-a['lon']))
    return math.atan2(math.sin(dl)*math.cos(lat2),math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(dl))


def path_signature(graph,path,mode='walk'):
    """Collapse only geometric degree-two samples before taking turn/length features."""
    adj=adjacency(graph,mode);selected=[path[0]] if path else []
    for i in range(1,len(path)-1):
        a,b,c=(graph['nodes'][n] for n in path[i-1:i+2]); turn=normalize_lon(math.degrees(_bearing(b,c)-_bearing(a,b)))
        if len({e['to'] for e in adj.get(path[i],[])})!=2 or abs(turn)>=25:selected.append(path[i])
    if len(path)>1:selected.append(path[-1])
    lengths=[geodesic_distance(graph['nodes'][a]['lat'],graph['nodes'][a]['lon'],graph['nodes'][b]['lat'],graph['nodes'][b]['lon']) for a,b in zip(selected,selected[1:])]
    turns=[];word=[];degrees=[]
    for a,b,c in zip(selected,selected[1:],selected[2:]):
        angle=normalize_lon(math.degrees(_bearing(graph['nodes'][b],graph['nodes'][c])-_bearing(graph['nodes'][a],graph['nodes'][b])))
        # Bearings increase clockwise: positive = right.
        turns.append(round(angle,5));letter='S' if abs(angle)<30 else 'U' if abs(angle)>150 else 'R' if angle>0 else 'L'
        degree=len({e['to'] for e in adj.get(b,[])})
        word.append(letter+str(degree));degrees.append(degree)
    total=sum(lengths) or 1
    return {'turn_degrees':turns,'word':word,'junction_degrees':degrees,'length_ratios':[round(x/total,7) for x in lengths],'chart_nodes':selected,'units':'degrees and dimensionless ratios','projection_loss':'degree-two geometric points collapsed; no building/POI features used'}


def route(city='tampa',start=None,end=None,mode='walk',max_distance=400):
    if city not in ANCHORS or mode not in ('walk','cycle','drive'): return {'status':'unsupported','quality_mask':{'geometry':'incomplete'},'reason':'no sourced graph or mode adapter'}
    if not 1<=float(max_distance)<=5000:return {'status':'refused','reason':'distance budget must be 1..5000m'}
    graph=load_graph(city);adj=adjacency(graph,mode)
    if not adj:return {'status':'infeasible','reason':'no permitted source edges'}
    if start is None: a=_spawn(graph,adj) if mode=='walk' else _nearest(graph,adj,ANCHORS[city])
    elif isinstance(start,(list,tuple)):a=_nearest(graph,adj,start)
    else:a=str(start) if str(start) in adj else None
    if end is None:b=None
    elif isinstance(end,(list,tuple)):b=_nearest(graph,adj,end)
    else:b=str(end) if str(end) in adj else None
    if a is None or (end is not None and b is None):return {'status':'infeasible','reason':'no source-permitted node within 250m snap budget','quality_mask':{'geometry':'incomplete'}}
    path,length=_dijkstra(adj,a,b,max_distance)
    if len(path)<2:return {'status':'infeasible','reason':'source graph disconnected or no movement','nodes':path}
    points=[{'lat':graph['nodes'][n]['lat'],'lon':graph['nodes'][n]['lon'],'node_id':n} for n in path]
    edges=[next(e for e in adj[a] if e['to']==b) for a,b in zip(path,path[1:])]
    certificate={'source_graph_1':_graph_ref(city),'source_graph_2':None,'chart_rev_1':'ground.osm.wgs84.v1','route_nodes_1':path,'route_nodes_2':[],'feature_map':path_signature(graph,path,mode),'transform':'WGS84 to local ENU; geodesic edge lengths','score':None,'calibration':None,'confidence':'OSM tag-based access; current ground conditions unverified','fictional_portal_effect':False}
    certificate['content_hash']=_canonical_hash(certificate)
    return {'status':'ok','city':city,'mode':mode,'nodes':path,'points':points,'points_enu':[list(geodetic_to_enu(p['lat'],p['lon'],origin=ANCHORS[city])) for p in points],'edges':edges,'length_m':round(length,3),'signature':certificate['feature_map'],'quality_mask':{'geometry':'source-confirmed','access':'tag-based approximate inference; not live or legal access verification','turn_restrictions':'OSM restriction relations retained but not enforced; driving routes are illustrative','widths':'incomplete'},'certificate':certificate}


class TileStore:
    """Global 0..18 equirectangular quadtree addresses and bounded demand recipes.

    Coordinates do not trigger global detail loads or online requests. Each tile
    is tiny metadata plus source references; graph cache is separately bounded.
    """
    def __init__(self,max_tiles=64,level=12):
        if not 1<=max_tiles<=4096 or not 0<=level<=18:raise ValueError('invalid tile budget')
        self.max_tiles=max_tiles;self.level=level;self.cache=OrderedDict();self.evictions=0;self.hits=0
    def resolve(self,lat,lon,epoch=None):
        lat,lon,_=_valid(lat,lon);n=1<<self.level
        x=min(n-1,int((lon+180)/360*n));y=min(n-1,int((90-lat)/180*n));key=f'earth:{self.level}/{x}/{y}'
        if key in self.cache:self.hits+=1;self.cache.move_to_end(key)
        else:
            self.cache[key]={'cell_id':key,'bounds':[-180+x*360/n,90-(y+1)*180/n,-180+(x+1)*360/n,90-y*180/n],'detail':'lazy source recipe'}
            if len(self.cache)>self.max_tiles:self.cache.popitem(last=False);self.evictions+=1
        return {**self.cache[key],'coords':{'lat':lat,'lon':lon},'epoch':epoch,'status':'ok'}
    def info(self):return {'loaded_tiles':len(self.cache),'max_tiles':self.max_tiles,'evictions':self.evictions,'hits':self.hits,'address_scheme':'equirectangular quadtree; polar cells shrink in area','level':self.level}


TILES=TileStore()


@lru_cache(maxsize=3)
def _reference_points(kind):
    obj=json.loads((DATA/'raw'/f'{kind}.geojson').read_text());out=[]
    for feature in obj['features']:
        if feature['geometry']['type']!='Point':continue
        lon,lat=feature['geometry']['coordinates'][:2];props=feature['properties']
        out.append({'lat':lat,'lon':lon,'name':props.get('name'),'properties':{k:props.get(k) for k in ('iata_code','gps_code','pop_max','adm0_a3','ne_id') if props.get(k) is not None}})
    return out


@lru_cache(maxsize=3)
def _reference_index(kind):
    result=[]
    for p in _reference_points(kind):
        lat,lon=math.radians(p['lat']),math.radians(p['lon'])
        result.append(((math.cos(lat)*math.cos(lon),math.cos(lat)*math.sin(lon),math.sin(lat)),p))
    return result


def _near(kind,lat,lon,limit=1):
    # Spherical chord prefilter, then accurate WGS84 refinement. Generalized
    # reference points themselves have much larger cartographic uncertainty.
    p,l=math.radians(lat),math.radians(lon);unit=(math.cos(p)*math.cos(l),math.cos(p)*math.sin(l),math.sin(p))
    shortlist=heapq.nsmallest(max(16,limit),_reference_index(kind),key=lambda row:sum((a-b)**2 for a,b in zip(unit,row[0])))
    ranked=sorted((row[1] for row in shortlist),key=lambda p:geodesic_distance(lat,lon,p['lat'],p['lon']))[:limit]
    return [{**p,'distance_m':round(geodesic_distance(lat,lon,p['lat'],p['lon']),1),'source_ref':kind,'selection':'spherical-chord shortlist then WGS84 refinement; generalized sparse reference'} for p in ranked]


def weather_field(lat=27.95946425,lon=-82.5055696,epoch=None):
    lat,lon,_=_valid(lat,lon)
    raw=json.loads((DATA/'raw/weather_tampa.json').read_text())
    if geodesic_distance(lat,lon,raw['latitude'],raw['longitude'])>20000:return {'status':'gap','source_ref':None,'reason':'no acquired weather field at this location'}
    current=raw['current'];status='snapshot'
    if epoch:
        at=datetime.fromisoformat(str(epoch).replace('Z','+00:00'))
        if at.tzinfo is None:at=at.replace(tzinfo=timezone.utc)
        model_at=datetime.fromisoformat(current['time']).replace(tzinfo=timezone.utc)
        if not 0<=(at-model_at).total_seconds()<current['interval']:status='stale'
    return {'status':status,'source_kind':'estimated','source_ref':'weather:tampa','model_epoch':current['time']+'Z','values':current,'units':raw['current_units'],'quality_mask':'model-derived grid estimate; not direct station observation; never silently current','source_location':{'lat':raw['latitude'],'lon':raw['longitude']}}


def resolve_cell(lat,lon,epoch=None):
    cell=TILES.resolve(lat,lon,epoch);lat,lon=cell['coords'].values()
    cities=[c for c in ANCHORS if (lambda b:b[0]<=lon<=b[2] and b[1]<=lat<=b[3])(_source(c)['bbox'])]
    def mask(status,**kwargs):return {'status':status,**kwargs}
    cell['coverage']={'roads':mask('present' if cities else 'gap',source_refs=['osm:'+c for c in cities]),'buildings':mask('present' if cities else 'gap',source_refs=['osm:'+c for c in cities]),'aviation_reference':mask('present',source_ref='airports',quality='sparse generalized airport points, not flight tracks'),'airways':mask('gap'),'maritime_reference':mask('present',source_ref='ports',quality='sparse port points; not navigable waterways'),'maritime_routes':mask('gap'),'population_country_totals':mask('present',source_ref='wb_population',quality='country/time aggregates; no local density inference'),'population_settlements':mask('present',source_ref='places',quality='sparse generalized historical city estimates'),'population_grid':mask('gap'),'weather':weather_field(lat,lon,epoch),'terrain':mask('gap'),'interiors':mask('gap')}
    cell['nearest_airport']=_near('airports',lat,lon)[0]
    cell['nearest_port']=_near('ports',lat,lon)[0]
    cell['nearest_settlement']=_near('places',lat,lon)[0]
    cell['quality_mask']={'global_address':'confirmed WGS84 coordinate','local_detail':'source-confirmed' if cities else 'incomplete','fictional_fill':'not generated by factual resolver'}
    return cell


def scene(city='tampa',radius_m=700,max_buildings=300):
    if city not in ANCHORS:return {'status':'unsupported','reason':'source graph absent'}
    if not 50<=float(radius_m)<=2500:raise ValueError('scene radius budget 50..2500m')
    graph=load_graph(city);origin=ANCHORS[city]
    def point(node):
        n=graph['nodes'][node];return [round(v,4) for v in geodetic_to_enu(n['lat'],n['lon'],origin=origin)]
    def near(way):return any(geodesic_distance(*origin[:2],graph['nodes'][n]['lat'],graph['nodes'][n]['lon'])<=radius_m for n in way['nodes'])
    roads=[];buildings=[];water=[]
    for way in graph['ways']:
        if not near(way):continue
        tags=way['tags'];kind=tags['highway']
        if kind in ('proposed','construction','platform'):continue
        lanes=tags.get('lanes')
        try:width=max(1,float(tags['width'].split()[0]));width_kind='source-tag'
        except (KeyError,ValueError):
            try:width=max(2,int(lanes)*3.2);width_kind='estimated-from-lanes'
            except (TypeError,ValueError):width=2 if kind in ('footway','path','steps') else 5 if kind in ('service','residential') else 8;width_kind='estimated-from-class'
        roads.append({'source_way_id':way['id'],'points_enu':[point(n) for n in way['nodes']],'highway':kind,'name':tags.get('name'),'width_m':width,'width_kind':width_kind,'lanes':lanes,'oneway':tags.get('oneway'),'sidewalk':tags.get('sidewalk') or tags.get('sidewalk:right'),'crossing':tags.get('footway')=='crossing','walk_allowed':way_allowed(tags,'walk'),'source_tags':{k:tags[k] for k in ('crossing','crossing:signals','surface','traffic_signals','turn:lanes') if k in tags}})
    for way in graph['buildings']:
        if len(buildings)>=max(0,min(int(max_buildings),1000)) or not near(way):continue
        tags=way['tags'];height_kind='source-tag'
        try:height=float(tags['height'].replace('m','').strip())
        except (KeyError,ValueError):
            try:height=float(tags['building:levels'])*3.2;height_kind='estimated-from-source-levels'
            except (KeyError,ValueError):height=7.5;height_kind='estimated-artistic-default'
        alias=' '.join((['Amber','Quiet','Copper','Silver','Palm','Tide'][int(way['id'])%6],['Arcade','Corner','House','Collective','Market','Studio'][(int(way['id'])//7)%6]))
        buildings.append({'source_way_id':way['id'],'footprint_enu':[point(n) for n in way['nodes']],'height_m':max(2,min(250,height)),'height_kind':height_kind,'building_type':tags['building'],'alias':alias,'alias_kind':'fictional deterministic presentation','source_name_retained':False})
    for way in graph['water']:
        if near(way):water.append({'source_way_id':way['id'],'points_enu':[point(n) for n in way['nodes']],'kind':way['tags'].get('waterway') or way['tags'].get('natural') or 'marina'})
    adj=adjacency(graph,'walk');spawn=_spawn(graph,adj);sp=graph['nodes'][spawn]
    signals=[{'source_node_id':n,'point_enu':point(n),'kind':node['tags']['highway'],'crossing':node['tags'].get('crossing')} for n,node in graph['nodes'].items() if node['tags'].get('highway') in ('traffic_signals','crossing') and geodesic_distance(*origin[:2],node['lat'],node['lon'])<=radius_m]
    return {'status':'ok','city':city,'origin':{'lat':origin[0],'lon':origin[1],'height':origin[2],'datum':'WGS84 ellipsoid; terrain height absent'},'axes':{'x':'east metres','y':'north metres','z':'up metres','playcanvas_mapping':'[east,up,-north]'},'radius_m':radius_m,'roads':roads,'buildings':buildings,'water':water,'signals':signals,'spawn':{'source_node_id':spawn,'lat':sp['lat'],'lon':sp['lon'],'point_enu':point(spawn),'access':'tag-based pedestrian source path; field access unverified'},'source':_graph_ref(city),'quality_mask':{'geometry':'source-confirmed','building_height':'estimated-when-tag-absent','road_width':'estimated-when-tag-absent','names':'fictional aliases for buildings; source road names','terrain':'incomplete; artistic flat chart','walk_access':'source-tag inference'}}


def _random_path(graph,mode,rng,steps=10):
    adj=adjacency(graph,mode);start=rng.choice(sorted(adj));path=[start]
    for _ in range(steps):
        possible=[e['to'] for e in adj.get(path[-1],[]) if e['to'] not in path]
        if not possible:break
        path.append(rng.choice(possible))
    return path


def _sim(a,b):
    at=a['turn_degrees'];bt=b['turn_degrees']
    if len(at)<2 or len(bt)<2:return 0.0
    # Resampled turn sequence, junction degree, and length ratios. Similarity
    # means a constructed chart comparison, not a physical connection.
    n=min(len(at),len(bt),8)
    turn=sum(abs(normalize_lon(at[round(i*(len(at)-1)/(n-1))]-bt[round(i*(len(bt)-1)/(n-1))]))/180 for i in range(n))/n
    degree=sum(abs(a['junction_degrees'][round(i*(len(at)-1)/(n-1))]-b['junction_degrees'][round(i*(len(bt)-1)/(n-1))])/6 for i in range(n))/n
    la=a['length_ratios'];lb=b['length_ratios'];m=min(len(la),len(lb))
    length=sum(abs(la[i]-lb[i]) for i in range(m))+abs(len(la)-len(lb))/max(len(la),len(lb))
    return round(max(0,1-(.65*turn+.2*min(degree,1)+.15*min(length,1))),7)


def match_routes(city1='tampa',city2='london',seed=7,samples=128):
    if city1 not in ANCHORS or city2 not in ANCHORS:return {'status':'unsupported','reason':'source graph absent'}
    if not 16<=int(samples)<=1024:return {'status':'refused','reason':'heldout samples must be 16..1024'}
    g1,g2=load_graph(city1),load_graph(city2)
    a=route(city1,max_distance=500)
    if a['status']!='ok':return a
    rng=random.Random(int(seed));candidates=[]
    # Candidate selection independent of held-out seed stream. We deliberately
    # calibrate the maximum over this same search budget in every null replicate.
    candidate_count=16
    def best_for(signature,r):
        best=(-1,None,None)
        for _ in range(candidate_count):
            path=_random_path(g2,'walk',r,steps=18);sig=path_signature(g2,path)
            score=_sim(signature,sig)
            if score>best[0]:best=(score,path,sig)
        return best
    score,path_b,sig_b=best_for(a['signature'],rng)
    null_rng=random.Random(int(seed)^0x51A7D00D);null=[]
    for _ in range(int(samples)):
        p=_random_path(g1,'walk',null_rng,steps=18);signature=path_signature(g1,p)
        null.append(best_for(signature,null_rng)[0])
    pvalue=(1+sum(v>=score for v in null))/(len(null)+1)
    certificate={'source_graph_1':_graph_ref(city1),'source_graph_2':_graph_ref(city2),'chart_rev_1':'ground.osm.turn.v1','chart_rev_2':'ground.osm.turn.v1','route_nodes_1':a['nodes'],'route_nodes_2':path_b,'feature_map':{'route1':a['signature'],'route2':sig_b,'weights':{'turn':.65,'junction_degree':.2,'length_ratio':.15}},'transform':'translation/rotation/scale normalized; no physical cross-city connection','score':score,'calibration':{'null_model':'independent non-revisiting source-graph walks; same 16-candidate maximum search in each replicate','heldout_samples':len(null),'candidate_search_budget':candidate_count,'seed':int(seed),'p_value':pvalue,'threshold':.05,'null_scores':null,'limitation':'degree/route-length distributions are approximate controls; not a global geographic rarity claim'},'confidence':'experimental structural correspondence only','projection_loss':'no lane, plaza, building or POI match; resampled turn sequence','fictional_portal_effect':False}
    certificate['content_hash']=_canonical_hash(certificate)
    return {'status':'ok','conclusion':'candidate' if pvalue<=.05 and score>=.8 else 'negative','certificate':certificate}


def overview():
    try:
        import geographiclib
        method='Karney WGS84 inverse (geographiclib '+geographiclib.__version__+')'
    except ImportError:method='Vincenty WGS84 inverse; authalic-sphere fallback at nonconvergent antipodes (approximate)'
    return {'status':'ok','global_address':'WGS84 Earth, poles/dateline/negative altitude','sources':sources(),'anchors':{c:{'lat':v[0],'lon':v[1]} for c,v in ANCHORS.items()},'cache':TILES.info(),'graph_cache_limit':2,'distance_method':method,'tampa_intersection':tampa_anchor(),'capabilities':['source-routes','source-scene-footprints','regional-pattern-negative-controls','global-lazy-addresses'],'limits':sources()['gaps']}
