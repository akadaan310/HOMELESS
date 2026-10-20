#!/usr/bin/env python3
"""Auditable source acquisition and renderer-independent GLB derivatives.

No runtime-visible or Unreal-imported state is inferred from a successful download.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, io, json, math, os, pathlib, shutil, struct, subprocess, sys, time
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
USER_AGENT = 'HOMELESS-Asset-Ingest/1.0 (+source-fidelity-audit)'
SOURCES = [
    {'id':'street_lamp_01','kind':'polyhaven','category':'street-furniture','url':'https://polyhaven.com/a/street_lamp_01','license':'CC0-1.0'},
    {'id':'covered_car','kind':'polyhaven','category':'covered-static-vehicle','url':'https://polyhaven.com/a/covered_car','license':'CC0-1.0'},
    {'id':'fire_hydrant','kind':'polyhaven','category':'street-furniture','url':'https://polyhaven.com/a/fire_hydrant','license':'CC0-1.0'},
    {'id':'npc_hv_girl','kind':'glb','category':'rigged-human','url':'https://github.com/BabylonJS/Assets/blob/master/meshes/HVGirl.glb','download':'https://raw.githubusercontent.com/BabylonJS/Assets/master/meshes/HVGirl.glb','license':'CC-BY-4.0','attribution':'Babylon.js Assets contributors; HVGirl sample; repository license https://github.com/BabylonJS/Assets/blob/master/README.md'},
    {'id':'car_concept','kind':'glb','category':'passenger-vehicle','url':'https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/CarConcept','download':'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CarConcept/glTF-Binary/CarConcept.glb','license':'CC-BY-4.0','license_url':'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CarConcept/LICENSE.md','attribution':'Eric Chadwick / Darmstadt Graphics Group GmbH, 2024; Car Concept via Khronos glTF Sample Assets. Logos excluded from copyright license.'},
    {'id':'sponza','kind':'gltf','category':'architecture-environment-lookdev','url':'https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/Sponza','download':'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Sponza/glTF/Sponza.gltf','license':'LicenseRef-CRYENGINE-Agreement','license_url':'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Sponza/LICENSE.md','distribution_approved':False,'attribution':'Sponza by Frank Meinl / Crytek; model under Cryengine limited agreement, not CC-BY. Separate local lookdev only; omitted from public runtime pending distribution review.'},
    {'id':'aerobatic_plane','kind':'glb','category':'light-aircraft','url':'https://github.com/BabylonJS/Assets/blob/master/meshes/aerobatic_plane.glb','download':'https://raw.githubusercontent.com/BabylonJS/Assets/master/meshes/aerobatic_plane.glb','license':'CC-BY-4.0','attribution':'Babylon.js Assets contributors, aerobatic_plane model; repository CC-BY4.0 unless otherwise specified.'},
]
SOURCES += [
    {'id':name,'kind':'polyhaven','category':category,'url':'https://polyhaven.com/a/'+name,'license':'CC0-1.0'}
    for name,category in [
        ('modular_factory_facade','modular-commercial-architecture'),
        ('modular_urban_apartments_facade','modular-urban-architecture'),
        ('CoffeeCart_01','cafe-fixture'),
        ('jacaranda_tree','regional-compatible-vegetation'),
        ('modular_street_seating','street-seating'),
        ('concrete_road_barrier','roadside-barrier'),
        ('metal_trash_can','street-refuse-container'),
        ('modular_chainlink_fence','street-fencing'),
        ('modular_electricity_poles','street-utility-poles'),
        ('utility_box_01','street-utility-cabinet'),
        ('water_manhole_cover','street-manhole'),
    ]
]

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def curl(url, path, expected_md5=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and (expected_md5 is None or hashlib.md5(path.read_bytes()).hexdigest()==expected_md5): return
    tmp=path.with_suffix(path.suffix+'.part')
    subprocess.run(['curl','--fail','--location','--retry','2','--max-time','180','--silent','--show-error','--user-agent',USER_AGENT,url,'--output',str(tmp)],check=True)
    if expected_md5 and hashlib.md5(tmp.read_bytes()).hexdigest()!=expected_md5:
        tmp.unlink(); raise ValueError('Publisher MD5 mismatch: '+url)
    tmp.replace(path)

def archive(path):
    digest=sha(path); blob=ASSETS/'originals'/'sha256'/digest[:2]/digest
    blob.parent.mkdir(parents=True,exist_ok=True)
    if not blob.exists(): os.link(path,blob)
    blob.chmod(0o444)
    return {'path':str(path.relative_to(ROOT)),'sha256':digest,'bytes':path.stat().st_size,'master_ref':str(blob.relative_to(ROOT))}

def fetch(source, resolution):
    out=ASSETS/'originals'/source['id'];out.mkdir(parents=True,exist_ok=True)
    entry={**source,'canonical_id':'world://asset/'+source['id'],'status':'candidate','import_status':'not-imported','cook_status':'not-cooked','scene_test':'not-rendered','source_claim':'sourced-artwork','source_revision':'publisher-api-at-acquisition'}
    if source['kind']=='polyhaven':
        api=out/'publisher-files.json';curl('https://api.polyhaven.com/files/'+source['id'],api)
        info=out/'publisher-info.json';curl('https://api.polyhaven.com/info/'+source['id'],info)
        choices=json.loads(api.read_text())['gltf']
        if resolution not in choices:
            resolution=max(choices,key=lambda key:int(key.rstrip('k')))
        payload=choices[resolution]['gltf']
        files=[(source['id']+'_'+resolution+'.gltf',payload),*payload.get('include',{}).items()]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda x:curl(x[1]['url'],out/x[0],x[1].get('md5')),files))
        entry['source_file']=str((out/files[0][0]).relative_to(ROOT));entry['source_texture_variant']=resolution
        entry['files']=[{**archive(out/name),'publisher_md5':spec.get('md5'),'url':spec['url']} for name,spec in files]
        entry['publisher_author']=json.loads(info.read_text()).get('authors',{})
    elif source['kind']=='gltf':
        import urllib.parse
        file=out/(source['id']+'.gltf');curl(source['download'],file)
        doc=json.loads(file.read_text());base=source['download'].rsplit('/',1)[0]+'/'
        paths=[b['uri'] for b in doc.get('buffers',[])]+[i['uri'] for i in doc.get('images',[]) if 'uri' in i]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda p:curl(urllib.parse.urljoin(base,p),out/p),paths))
        if source.get('license_url'):curl(source['license_url'],out/'LICENSE.md')
        entry['source_file']=str(file.relative_to(ROOT));entry['files']=[{**archive(out/p),'url':source['download'] if p==file.name else urllib.parse.urljoin(base,p)} for p in [file.name,*paths]]
    else:
        file=out/(source['id']+'.glb');curl(source['download'],file)
        if source.get('license_url'): curl(source['license_url'],out/'LICENSE.md')
        entry['source_file']=str(file.relative_to(ROOT));entry['files']=[{**archive(file),'url':source['download']}]
    entry['status']='retrieved';write_json(out/'source-manifest.json',entry)
    return entry

def load_gltf(path):
    raw=path.read_bytes()
    if raw[:4]==b'glTF':
        magic,version,length=struct.unpack_from('<4sII',raw)
        if version!=2 or length!=len(raw):raise ValueError('invalid GLB header/length')
        cursor=12;doc=None;blob=b''
        while cursor<len(raw):
            size,kind=struct.unpack_from('<II',raw,cursor);cursor+=8
            chunk=raw[cursor:cursor+size];cursor+=size
            if len(chunk)!=size: raise ValueError('truncated GLB chunk')
            if kind==0x4e4f534a:doc=json.loads(chunk)
            elif kind==0x004e4942:blob=chunk
        if doc is None:raise ValueError('GLB lacks JSON')
        return doc,[blob]
    doc=json.loads(raw)
    return doc,[(path.parent/b['uri']).read_bytes() for b in doc.get('buffers',[])]

def accessor(doc,buffers,index):
    a=doc['accessors'][index]
    if 'sparse' in a:raise ValueError('sparse accessor not supported by geometry QA')
    view=doc['bufferViews'][a['bufferView']]
    fmt={5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']]
    n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16,'MAT3':9,'MAT2':4}[a['type']]
    size=struct.calcsize('<'+fmt*n);stride=view.get('byteStride',size)
    offset=view.get('byteOffset',0)+a.get('byteOffset',0);data=buffers[view['buffer']]
    if a['count'] and offset+(a['count']-1)*stride+size>len(data): raise ValueError('accessor beyond buffer')
    return [struct.unpack_from('<'+fmt*n,data,offset+i*stride) for i in range(a['count'])]

def metrics(path):
    import numpy as np
    from PIL import Image
    doc,buffers=load_gltf(path)
    issues=[];triangles=vertices=degenerate=nonfinite=0;bounds=[];normal_errors=[];edges=Counter();missing_normals=missing_uvs=0;normal_winding=[]
    for mi,m in enumerate(doc.get('meshes',[])):
        for pi,p in enumerate(m['primitives']):
            if p.get('mode',4)!=4: issues.append('non-triangle primitive');continue
            if 'POSITION' not in p['attributes']:issues.append('missing POSITION');continue
            v=np.asarray(accessor(doc,buffers,p['attributes']['POSITION']),dtype=float)
            vertices+=len(v);nonfinite+=int((~np.isfinite(v)).sum());bounds.extend([v.min(axis=0).tolist(),v.max(axis=0).tolist()])
            indices=np.asarray(accessor(doc,buffers,p['indices']),dtype=np.int64).reshape(-1) if 'indices' in p else np.arange(len(v))
            if len(indices)%3 or indices.max(initial=-1)>=len(v):raise ValueError('invalid triangle indices')
            faces=indices.reshape(-1,3);triangles+=len(faces)
            cross=np.cross(v[faces[:,1]]-v[faces[:,0]],v[faces[:,2]]-v[faces[:,0]])
            areas=np.linalg.norm(cross,axis=1);degenerate+=int((areas<1e-12).sum())
            for face in faces:
                for x,y in ((face[0],face[1]),(face[1],face[2]),(face[2],face[0])):edges[(mi,pi,min(int(x),int(y)),max(int(x),int(y)))]+=1
            if 'NORMAL' in p['attributes']:
                n=np.asarray(accessor(doc,buffers,p['attributes']['NORMAL']),dtype=float)
                normal_errors.extend(abs(np.linalg.norm(n,axis=1)-1).tolist())
                avg=n[faces].mean(axis=1);valid=areas>1e-12
                normal_winding.extend((np.einsum('ij,ij->i',cross[valid],avg[valid])<0).tolist())
            else:missing_normals+=1
            if 'TEXCOORD_0' not in p['attributes']:missing_uvs+=1
    image_metrics=[]
    for image in doc.get('images',[]):
        if 'uri' in image: data=(path.parent/image['uri']).read_bytes()
        else:
            view=doc['bufferViews'][image['bufferView']];off=view.get('byteOffset',0);data=buffers[view['buffer']][off:off+view['byteLength']]
        try:
            with Image.open(io.BytesIO(data)) as im:
                image_metrics.append({'name':image.get('name',image.get('uri','embedded')),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode})
                im.verify()
        except Exception as e:issues.append('image decode: '+str(e))
    if nonfinite:issues.append('nonfinite positions')
    if missing_normals:issues.append('missing normals')
    # Open edges and UV splits are common in scanned/hard-surface display meshes;
    # recorded diagnostics, never misrepresented as a watertight collision mesh.
    if triangles==0:issues.append('no triangles')
    transforms=[n.get('scale',[1,1,1]) for n in doc.get('nodes',[]) if 'mesh' in n]
    bb=np.asarray(bounds) if bounds else np.zeros((1,3))
    return {'format':'glTF-2.0','vertices':vertices,'triangles':triangles,'mesh_count':len(doc.get('meshes',[])),'materials':len(doc.get('materials',[])),'skins':len(doc.get('skins',[])),'bones':[len(s.get('joints',[])) for s in doc.get('skins',[])],'animations':[{'name':a.get('name','unnamed'),'channels':len(a.get('channels',[]))} for a in doc.get('animations',[])],'mesh_space_bounds':{'min':bb.min(axis=0).tolist(),'max':bb.max(axis=0).tolist()},'mesh_node_scales':transforms,'units':'glTF meters; authored node transforms preserved','triangles_degenerate':degenerate,'open_index_edges':sum(v==1 for v in edges.values()),'nonmanifold_index_edges':sum(v>2 for v in edges.values()),'normals_max_unit_error':max(normal_errors,default=None),'normal_winding_disagreement_fraction':sum(normal_winding)/max(1,len(normal_winding)),'missing_uv_primitives':missing_uvs,'images':image_metrics,'normal_map_convention':'glTF/OpenGL (+Y); Unreal import must convert','rig_contact_test':'not-run','mikk_tspace':'tangents preserved if present; UE recomputation pending','collision_test':'pending separate proxy/navmesh verification','issues':issues,'passed':not issues}

def pack_glb(source, dest, max_texture):
    from PIL import Image
    doc,buffers=load_gltf(source);blob=bytearray()
    def append(data):
        blob.extend(b'\0'*((-len(blob))%4));offset=len(blob);blob.extend(data);return offset
    original_views=[dict(v) for v in doc.get('bufferViews',[])]
    image_views={i['bufferView'] for i in doc.get('images',[]) if 'bufferView' in i}
    # Copy live geometry/accessor views, not an entire GLB BIN chunk containing
    # obsolete high-resolution images. Preserve indices so extension references
    # remain valid. Unreferenced former image views become tiny valid views.
    for index,view in enumerate(doc.get('bufferViews',[])):
        old=original_views[index]
        if index in image_views:
            view.clear();view.update({'buffer':0,'byteOffset':0,'byteLength':4})
        else:
            off=old.get('byteOffset',0)
            data=buffers[old['buffer']][off:off+old['byteLength']]
            view['byteOffset']=append(data);view['buffer']=0
    for image in doc.get('images',[]):
        if 'uri' in image:data=(source.parent/image.pop('uri')).read_bytes()
        else:
            view=original_views[image['bufferView']];off=view.get('byteOffset',0);data=buffers[view['buffer']][off:off+view['byteLength']]
        with Image.open(io.BytesIO(data)) as im:
            resized=max(im.size)>max_texture
            if resized:
                im.thumbnail((max_texture,max_texture),Image.Resampling.LANCZOS)
            # Explicit JPEG for opaque maps, PNG for maps carrying alpha. This
            # is a transport derivative; original art is retained unchanged.
            if im.mode not in ('RGBA','LA') or resized:
                out=io.BytesIO()
                if im.mode in ('RGBA','LA'): im.save(out,format='PNG');mime='image/png'
                else: im.convert('RGB').save(out,format='JPEG',quality=94,subsampling=0);mime='image/jpeg'
                data=out.getvalue()
            else:mime=Image.MIME.get(im.format,'image/png')
        off=append(data);image['bufferView']=len(doc.setdefault('bufferViews',[]));image['mimeType']=mime;doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data)})
    doc['buffers']=[{'byteLength':len(blob)}]
    doc.setdefault('asset',{})['generator']='HOMELESS source-preserving packer v1; topology/rig/animations unchanged'
    encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);blob.extend(b'\0'*((-len(blob))%4))
    total=12+8+len(encoded)+8+len(blob)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(struct.pack('<4sII',b'glTF',2,total)+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(blob),0x004e4942)+blob)

def build(entry,max_texture=2048):
    source=ROOT/entry['source_file'];before=metrics(source)
    if not before['passed']:raise ValueError(str(before['issues']))
    approved=entry.get('distribution_approved',True)
    runtime=ASSETS/('runtime' if approved else 'quarantine')/(entry['id']+'.glb');pack_glb(source,runtime,max_texture);after=metrics(runtime)
    if not after['passed'] or before['triangles']!=after['triangles'] or before['bones']!=after['bones'] or before['animations']!=after['animations']:raise ValueError('derivative identity/rig/topology validation failed')
    entry['status']='verified';entry['source_metrics']=before
    entry['variants']={'unreal-source':{'path':entry['source_file'],'status':'source-ready; import pending'},'rendezvous-medium':{'path':str(runtime.relative_to(ROOT)),'url':'/assets/runtime/'+runtime.name,'sha256':sha(runtime),'bytes':runtime.stat().st_size,'metrics':after,'texture_limit':max_texture,'compression':'embedded JPEG/PNG; mesh compression none','topology_deviation':0,'silhouette_deviation':0,'animation_channel_deviation':0,'render_status':'not-rendered'}}
    if not approved:
        entry['variants']['local-research-only']=entry['variants'].pop('rendezvous-medium')
        entry['variants']['local-research-only'].pop('url',None)
        entry['distribution_gate']='HOLD: source license requires distribution review; no public runtime variant'
    entry['compression_gates']={'KTX2':'pending encoder and exact importer round-trip','Draco':'uncompressed baseline chosen; optional decoder verification pending','LOD':'source topology retained; simplification not claimed'}
    write_json(ASSETS/'originals'/entry['id']/'source-manifest.json',entry)
    return entry

def catalog(entries):
    known={e['id'] for e in entries}
    for extra in (ASSETS/'extras').glob('*.json'):
        entry=json.loads(extra.read_text())
        if entry['id'] not in known:entries.append(entry);known.add(entry['id'])
    original=ROOT/'masterpack/DARK_HOMELESS_CODEX_MASTERPACK_2026_10_20/config/asset_candidates.json'
    old=json.loads(original.read_text())
    queries=[]
    for name in old['unfilled_families']+['commercial-storefronts','regional-vegetation','full-body-human-animation','vehicle-interiors','rain-weather']:
        queries.append({'category':name,'priority':'P0' if name in ('regional-architecture','animations','ambient-city-sounds') else 'P1','source_query':'https://www.fab.com/search?q='+name.replace('-','%20'),'state':'candidate','unavailable_reason':'Not yet acquired/entitlement and portable format unverified'})
    payload={'schema':'worldloom.asset-catalog.v1','assets':entries,'upstream_candidates':old['assets'],'unfilled_families':queries,'quality_acceptance':{'hero_scene':'FAIL: full commercial/storefront/crowd/traffic collection and final rendered visual fixture incomplete','unreal':'BLOCKED: UE5.8 SDK and GPU not present','phone':'BLOCKED: real device profiling not performed'},'source_state_semantics':['candidate','retrieved','converted','verified','scene-integrated'],'updated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    write_json(ASSETS/'catalog.json',payload)
    runtime={'schema':'worldloom.runtime-assets.v1','assets':[{'id':e['id'],'canonical_id':e['canonical_id'],'category':e['category'],'source_url':e['url'],'license':e['license'],'attribution':e.get('attribution',e.get('publisher_author')),'variants':e.get('variants',{}),'state':e['status']} for e in entries],'default_variant':'rendezvous-medium','world_authority':'worldloom; renderer-independent canonical IDs','fixture_category_gaps':['20+ Tampa commercial storefront modules','moving conventional passenger vehicles/interiors','three art-directed human characters','regional palm/vegetation set','cross-renderer material and rendered motion acceptance']}
    write_json(ASSETS/'runtime'/'manifest.json',runtime)
    write_json(ROOT/'data/assets/registry.json',payload)
    write_json(ROOT/'evidence/assets_acquisition.json',{'assets':[{'id':e['id'],'state':e['status'],'files':e.get('files',[]),'metrics':e.get('source_metrics'),'variants':e.get('variants')} for e in entries],'unreal_imported':False,'unreal_cooked':False,'render_acceptance_passed':False})

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['acquire','build','verify']);p.add_argument('--ids',nargs='*');p.add_argument('--resolution',default='8k');p.add_argument('--max-texture',type=int,default=2048);a=p.parse_args()
    entries=[];errors=[]
    for src in SOURCES:
        file=ASSETS/'originals'/src['id']/'source-manifest.json'
        if a.ids and src['id'] not in a.ids:
            if file.exists():entries.append(json.loads(file.read_text()))
            continue
        try:
            if a.command=='acquire': e=fetch(src,a.resolution);e=build(e,a.max_texture)
            elif a.command=='build': e=build(json.loads(file.read_text()),a.max_texture)
            else:
                e=json.loads(file.read_text())
                for f in e['files']:
                    if sha(ROOT/f['path'])!=f['sha256']:raise ValueError('source SHA256 mismatch')
                for v in e.get('variants',{}).values():
                    if 'sha256' in v and sha(ROOT/v['path'])!=v['sha256']:raise ValueError('variant SHA256 mismatch')
                if e.get('kind') in ('polyhaven','glb','gltf') and not metrics(ROOT/e['source_file'])['passed']:raise ValueError('geometry validation failed')
            entries.append(e);print(json.dumps({'id':src['id'],'state':e['status'],'triangles':e.get('source_metrics',{}).get('triangles')}),flush=True)
        except Exception as exc: errors.append({'id':src['id'],'error':str(exc)}); print(json.dumps(errors[-1]),file=sys.stderr,flush=True)
    catalog(entries)
    if errors:write_json(ROOT/'evidence/assets_failures.json',errors)
    return bool(errors)
if __name__=='__main__':raise SystemExit(main())
