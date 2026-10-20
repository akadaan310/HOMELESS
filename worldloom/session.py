"""Single authority for browser, Android and local renderer operations."""
from __future__ import annotations
import importlib,json,math,secrets,threading,uuid,time
from pathlib import Path
from .protocol import Store,Engine,canonical,digest,clock,public_projection,ProtocolError,MAX_MESSAGE
ROOT=Path(__file__).resolve().parents[1]

class WorldSession(Engine):
 def __init__(self,path):
  super().__init__(Store(path));self.lock=threading.RLock();self.world=None;self.plans={};self._init_world()
 def _init_world(self):
  try:
   from .society import World
   saved=self.store.state()['world'];self.world=World.from_snapshot(saved) if saved else World(seed=7)
  except ImportError:pass
 def close(self):self.store.close()
 def open_player(self):
  session=uuid.uuid4().hex;actor='player:'+session
  token=self.store.grant(actor,['journey.append','world.play','speech.act','governance.propose'],ttl=30*86400)
  return {'session':session,'actor':actor,'token':token,'founder':False}
 def snapshot(self):
  with self.lock:
   if self.world is None:self._init_world()
   world=self.world.snapshot() if self.world else {'status':'unavailable','reason':'society module not installed'}
   return {'version':1,'world':public_projection(world),'continuity':self.store.checkpoint(),'objects':self.store.state()['objects'],'mode':'local-authoritative','clock':clock(getattr(self.world,'world_tick',0)),'source_quality':{'geography':'see /api/scene for source witnesses','aesthetic':'authored projection'}}
 def invoke(self,q):
  with self.lock:
   if not isinstance(q,dict):return {'status':'error','warnings':['map required']}
   op=q.get('operation','query');payload=q.get('payload',{})
   if not isinstance(op,str):return {'status':'error','warnings':['operation must be a string']}
   op={'model.compile':'grammar.compile','model.validate':'grammar.validate','model.expand':'grammar.expand','model.run':'grammatical.run'}.get(op,op)
   try:
    if len(canonical(q).encode())>MAX_MESSAGE:raise ValueError('message budget exceeded')
    if not isinstance(payload,dict):raise ValueError('payload must be a map')
    if op in ['query','resolve','inspect'] and str(q.get('program','')).startswith('purl://dark/journey/'):
     from urllib.parse import urlsplit
     path=urlsplit(q['program']).path;parts=path.strip('/').split('/')
     if len(parts)!=3 or parts[0]!='journey' or parts[2]!='program':raise ValueError('invalid journey program address')
     session_id=parts[1];actor=q.get('actor','guest');token=q.get('capability','')
     owner=actor=='player:'+session_id and self.store.authorized(token,actor,'world.play')
     if not owner and not self.store.authorized(token,actor,'*'):return {'status':'refused','warnings':['journey owner capability required']}
     context=q.get('context_hash');context=context.removeprefix('sha256:') if isinstance(context,str) else context
     events=self.store.state(context)['sessions'].get(session_id,[])
     steps=[{'kind':e.get('journey_kind','walk'),'position':e['position']} for e in events]
     return self._ok({'grammar':'journey.observation.v1','program':{'sort':'JourneyObservation','steps':steps},'address':q['program'],
      'witness':{'request_hashes':[e.get('request_hash') for e in events],'trace_digest':digest(steps)},
      'provenance':'authenticated client observations; physical motion and route admissibility are not independently proven'})
    if op in ['world.query','state']:return self._ok(self.snapshot())
    if op=='mission.opportunity':
     if self.world is None:raise ValueError('world module unavailable')
     return self.world.dispatch(op,payload,actor=q.get('actor','guest'))
    if op=='billboard.inspect':
     check=self.store.checkpoint();return self._ok({'program':'purl://dark/continuity/checkpoint','grammar':'typed read -> checkpoint -> verify','witness':check,'output':{'committed_events':check['count'],'state_hash':check['state_hash']},'exit_code':0,'source':'actual durable ledger; no host paths or credentials'})
    if op in ['grammar.compile','grammar.validate','grammar.expand','grammatical.run','model.describe']:
     from .grammar import compile_program,validate_program,Grammatical,registry
     if op=='model.describe':return self._ok(registry())
     if op=='grammar.compile':return self._ok(compile_program(payload['subject'],payload['source'],payload.get('context')))
     program=payload['program']
     if op=='grammar.validate':return self._ok(validate_program(program))
     return self._ok(Grammatical(program).expand() if op=='grammar.expand' else Grammatical(program).run())
    if op.startswith('gate.'):
     # The same pure resource planner serves all clients. No durable write here.
     from .bootstrap import BootstrapScheduler
     if not hasattr(self,'scheduler'):self.scheduler=BootstrapScheduler()
     return self._gate(op,payload)
    if op in ['geo.scene','geo.route','geo.overview']:
     from . import geo
     return self._ok(getattr(geo,op.split('.')[1])(**payload))
    if op in ['sky.observer','sky.discover','sky.overview']:
     from . import sky
     return self._ok(getattr(sky,op.split('.')[1])(**payload))
    if op.startswith('math.'):
     from . import numerics
     f={'math.solve':'solve_box_qp','math.camera':'camera_trace','math.weather':'weather_field'}.get(op)
     return self._ok(getattr(numerics,f)(payload)) if f else self._ok(numerics.overview())
    if op in ['sound.describe','audio.resolve','voice.catalog']:
     p=ROOT/'artifacts/voice/catalog.json'
     return self._ok(json.loads(p.read_text()) if p.exists() else {'status':'unavailable','speech_artifacts':[]})
    if op=='physics.integrate':
     dt=float(payload.get('dt',1/60));x=float(payload.get('position',0));v=float(payload.get('velocity',0))
     if not all(math.isfinite(i) for i in [dt,x,v]) or not 0<dt<=.1:raise ValueError('physics bounds')
     return self._ok({'position':x+v*dt,'dt':dt,'method':'bounded constant velocity fixture','projection_only':True})
    if op in ['shell.run','script.js','script.wasm']:
     if not self.store.authorized(q.get('capability',''),q.get('actor',''),'worker.run'):return {'status':'refused','warnings':['worker.run capability required']}
     from .workers import shell,javascript,wasm
     frozen=self.snapshot()
     class ReadProjection:
      def invoke(_,query):
       program=query.get('program','purl://dark/world/state')
       if program=='purl://dark/world/state':return {'status':'ok','data':frozen,'trace_digest':digest(frozen),'effects':[]}
       if program=='purl://dark/continuity/checkpoint':return {'status':'ok','data':frozen['continuity'],'effects':[]}
       return {'status':'unsupported','effects':[]}
     return self._ok(shell(payload['source'],engine=ReadProjection()) if op=='shell.run' else javascript(payload['source']) if op=='script.js' else wasm(payload['source']))
    if op in ['journey.append','npc.interact','speech.act','governance.propose','haven.enter','mission.accept','event.activate','world.tick'] or op.startswith(('cohort.','authorship.')):
     return self._player_operation(q)
    return super().invoke(q)
   except (ValueError,TypeError,KeyError,AttributeError,ImportError) as e:return {'status':'error','warnings':[str(e)]}
 def resolve(self,url,context=None):
  if context is None and url in ['purl://dark/world/state','purl://dark/world/state@v1']:return {**self.snapshot(),'context_hash':context}
  return super().resolve(url,context)
 def _ok(self,data):return {'status':'ok','data':data,'commit_id':None,'effects':[],'trace_digest':digest(data)}
 def _gate(self,op,payload):
  from .bootstrap import BootstrapScheduler
  if not hasattr(self,'scheduler'):self.scheduler=BootstrapScheduler()
  if op=='gate.status':return self._ok({**self.scheduler.status(),'committed_events':self.store.verify()['count']})
  if op=='gate.cancel':
   plan=self.plans.get(payload.get('plan_id'),{})
   keys=[payload['gate_id']] if payload.get('gate_id') else plan.get('eligible_gates',[])
   return self._ok({'canceled':[self.scheduler.cancel(k,payload.get('reason','ignored')) for k in keys]})
  if op=='gate.prepare':
   plan=self.plans.get(payload.get('plan_id'))
   if plan is None:raise ValueError('unknown plan')
   ready=[]
   for r in plan['resources']:
    # Only server-registered catalog paths may provide bytes. A client cannot
    # choose arbitrary local paths, and server paths never appear in response.
    inline=getattr(self,'_gate_inline',{}).get(r['id']);path=getattr(self,'_gate_files',{}).get(r['id'])
    if inline is not None:ready.append(self.scheduler.prepare(r['id'],inline))
    elif path is not None and path.is_file():ready.append(self.scheduler.prepare(r['id'],path.read_bytes()))
   return self._ok({**plan,'state':'prepared' if len(ready)==len(plan['resources']) else 'manifest-ready',
                    'prepared':ready,'activation':False,'client_decode_required':True,'effects_committed':[]})
  if op!='gate.plan':raise ValueError('unsupported gate operation')
  position=payload.get('position',[0,0,0]);velocity=payload.get('velocity',[0,0,0])
  if len(position)!=3 or len(velocity)!=3 or not all(math.isfinite(float(x)) for x in position+velocity):raise ValueError('position/velocity')
  world=self.world.snapshot();now=world.get('world_time',0);resources=[];self._gate_files={};self._gate_inline={}
  catalog_path=ROOT/'artifacts/voice/catalog.json'
  if catalog_path.exists():
   catalog=json.loads(catalog_path.read_text());clips=catalog if isinstance(catalog,list) else catalog.get('assets',catalog.get('clips',catalog.get('utterances',[])))
   for clip in clips:
    if not isinstance(clip,dict):continue
    rid=clip.get('id',clip.get('cacheKey'));checksum=clip.get('audioHash',clip.get('audio_hash',clip.get('sha256',clip.get('hash'))))
    path=None
    for key in ('path','file','audio_path','output_path'):
     if clip.get(key):
      raw=Path(clip[key]);candidate=(ROOT/str(raw).lstrip('/')).resolve() if str(raw).startswith('/artifacts/') else (ROOT/raw).resolve() if not raw.is_absolute() else raw.resolve()
      if candidate.is_relative_to((ROOT/'artifacts/voice').resolve()) and candidate.is_file():path=candidate;break
    if path is None and clip.get('url'):
     url=clip['url'].split('?',1)[0]
     for candidate in [ROOT/url.lstrip('/'),ROOT/'artifacts/voice'/Path(url).name,ROOT/'artifacts/voice/audio'/Path(url).name]:
      candidate=candidate.resolve()
      if candidate.is_relative_to((ROOT/'artifacts/voice').resolve()) and candidate.is_file():path=candidate;break
    if path is not None:
     import hashlib
     actual=hashlib.sha256(path.read_bytes()).hexdigest()
     if checksum and checksum!=actual:continue
     checksum=actual;self._gate_files[rid]=path
    size=path.stat().st_size if path else clip.get('bytes',clip.get('size_bytes'))
    if not rid or not checksum or size is None:continue
    resources.append({'id':rid,'kind':'npc_speech','bytes':size,'memory_bytes':int(clip.get('durationMs',clip.get('duration_ms',2000))*96),
                      'decode_ms':float(clip.get('decode_ms',4)),'hash':checksum,'url':clip.get('url',clip.get('audio_url',clip.get('path',''))),
                      'phrase_id':clip.get('phrase_id',clip.get('utterance_variant_id')),'text':clip.get('text',clip.get('subtitle','')),
                      'speaker_actor':clip.get('speaker_actor'),'semantic_act':clip.get('semantic_act',clip.get('semanticAct'))})
  candidates=[];speed=math.sqrt(sum(float(x)**2 for x in velocity))
  def gate(identifier,kind,pos,resource_ids,radius=20,priority='B',source='world'):
   distance=math.dist(position,pos)
   closing=max(0,sum((float(b)-float(a))*float(v) for a,b,v in zip(position,pos,velocity))/max(distance,.0001))
   return {'id':identifier,'kind':kind,'candidateStateRevision':world['revision'],'distance_m':distance,
    'speed_mps':closing,'horizonSeconds':20,'activation_radius_m':radius,'admitted':True,
    'resourceSet':resource_ids,'priority':'A' if distance<=radius else priority,'expiry':now+30,'sourceActor':source,
    'authority':'scene.activate','effect':{'kind':kind.lower()+'.propose'},'public_information':True,
    'worldCell':world.get('cell'),'target_position':pos,'resource_policy':'preparation-only'}
  for conversation in world.get('conversations',[]):
   pos=conversation.get('position',[0,0,0]);distance=math.dist(position,pos)
   matching=[r['id'] for r in resources if r['phrase_id']==conversation.get('phrase_id') or r['text']==conversation.get('exact_text')]
   candidate=gate(conversation['episode_id'],'CONVERSATION_EPISODE',pos,matching,conversation.get('audibility_range',22),source=conversation['speaker_actor'])
   candidate['effect']={'kind':'conversation.overhear','act_id':conversation['act_id']};candidates.append(candidate)
  # Source registry variants are actual, independently cacheable GLB containers.
  # Embedded animation is retained as part of its real container, not invented
  # as a separate downloadable clip. Decode costs are conservative estimates.
  manifest_path=ROOT/'assets/runtime/manifest.json';animated=[];vehicle=[];asset_status=[]
  if manifest_path.is_file():
   import hashlib
   for asset in json.loads(manifest_path.read_text()).get('assets',[]):
    variant=asset.get('variants',{}).get('rendezvous-medium',{})
    if not variant.get('path'):continue
    path=(ROOT/variant['path'].lstrip('/')).resolve()
    if not path.is_relative_to((ROOT/'assets/runtime').resolve()) or not path.is_file():continue
    checksum=hashlib.sha256(path.read_bytes()).hexdigest()
    if checksum!=variant.get('sha256'):
     asset_status.append({'id':asset['id'],'status':'checksum-refused'});continue
    metrics=variant.get('metrics',{});animations=metrics.get('animations',[]);rid='asset:'+asset['id']+'@'+checksum
    texture_bytes=sum(int(i.get('width',0))*int(i.get('height',0))*4 for i in metrics.get('images',[]))
    geometry_bytes=int(metrics.get('vertices',0))*32+int(metrics.get('triangles',0))*12
    memory=max(path.stat().st_size,texture_bytes+geometry_bytes)
    resources.append({'id':rid,'kind':'animated_glb' if animations else 'glb','bytes':path.stat().st_size,
     'memory_bytes':memory,'decode_ms':8 if animations else 12,'hash':checksum,'url':variant.get('url','/'+variant['path']),
     'canonical_asset_id':asset.get('canonical_id'),'category':asset.get('category'),'animations':animations,
     'contains':['geometry','materials']+(['animation'] if animations else []),'memory_cost_kind':'conservative decoded-image/geometry estimate; client measurement required'})
    self._gate_files[rid]=path
    category=asset.get('category','')
    pos=[10,0,8] if animations else [4,0,-34] if category=='passenger-vehicle' else [-12,0,-8]
    candidates.append(gate('asset-cell:'+asset['id'],'ASSET_CELL',pos,[rid],25))
    asset_status.append({'id':asset['id'],'status':'hash-verified','memory_bytes_estimate':memory})
    if animations:animated.append(rid)
    if category=='passenger-vehicle':vehicle.append(rid)
  # Real read-only output can be pre-rendered as an inline verified resource.
  # Its identity derives from content, not who is expected to view the panel.
  def inline_resource(kind,body):
   import base64,hashlib
   encoded=canonical(body).encode();checksum=hashlib.sha256(encoded).hexdigest();rid=kind+':'+checksum
   resources.append({'id':rid,'kind':kind,'bytes':len(encoded),'memory_bytes':len(encoded),'decode_ms':1,
    'hash':checksum,'url':'data:application/json;base64,'+base64.b64encode(encoded).decode(),
    'source_kind':'computed-from-authoritative-read','inline':body})
   self._gate_inline[rid]=encoded
   return rid
  checkpoint=self.store.checkpoint()
  billboard=inline_resource('billboard_program',{'program':'purl://dark/continuity/checkpoint','grammar':'typed read -> verify -> display',
   'witness':checkpoint,'world_revision':world['revision'],'event_trace':[{'id':e['id'],'kind':e['kind'],'hash':e['hash']} for e in world.get('events',[])[-3:]],
   'decision_trace':world.get('decisions',[])[:1],'source':'actual current world records; no host paths or credentials'})
  candidates.append(gate('billboard:world-record','BILLBOARD_PROGRAM',[15,0,3],[billboard],20))
  evidence=[e['id'] for e in world.get('events',[])[-4:]]
  report=inline_resource('haven_report',{'grammar':'RENDEZVOUS_HAVEN.v1','evidence':evidence,'world_revision':world['revision'],
   'speakers':{a['actor_id']:[m['event_id'] for m in a['memory'] if m['event_id'] in evidence] for a in world.get('actors',[]) if any(m['event_id'] in evidence for m in a['memory'])},
   'participation':'optional; no attendance committed','report_hash':digest(evidence)})
  candidates.append(gate('haven:tampa','RENDEZVOUS_HAVEN',[13,0,-32],[report]+animated[:1],15))
  if vehicle:candidates.append(gate('vehicle:passenger-entry','VEHICLE_ENTRY',[4,0,-34],vehicle[:1],5))
  plan=self.scheduler.plan({**world,'battery':payload.get('battery',1),'network_available':payload.get('network_available',True)},candidates,resources,now=now)
  plan.update({'state':'predicted','activation':False,'expires_seconds':30,'gates':candidates,'asset_verification':asset_status})
  self.plans[plan['plan_id']]=plan
  if len(self.plans)>32:self.plans.pop(next(iter(self.plans)))
  return self._ok(plan)
 def _player_operation(self,q):
  op=q['operation'];actor=q.get('actor','guest');token=q.get('capability','');session=q.get('session','');p=q['payload']
  scope='journey.append' if op=='journey.append' else 'world.play'
  if op=='world.tick':scope='world.simulate'
  if not self.store.authorized(token,actor,scope):return {'status':'refused','warnings':['authenticated scoped session required']}
  if actor.startswith('player:') and session!=actor[7:]:return {'status':'refused','warnings':['session mismatch']}
  eid=q.get('event_id')
  if not isinstance(eid,str) or not 1<=len(eid)<=128:raise ValueError('event_id required')
  fingerprint=digest({'actor':actor,'session':session,'operation':op,'payload':p})
  prior=self.store.db.execute('SELECT body,hash FROM events WHERE event_id=?',(eid,)).fetchone()
  if prior:
   event=json.loads(prior[0])
   if event['payload'].get('request_hash')!=fingerprint:return {'status':'conflict','warnings':['event_id reused with different input']}
   return {'status':'ok','data':event['payload'].get('result',{}),'commit_id':prior[1],'effects':[op],'trace_digest':digest(event)}
  if op=='journey.append':
   position=p.get('position',[0,0,0])
   if not isinstance(position,list) or len(position)!=3 or not all(isinstance(x,(int,float)) and math.isfinite(x) and abs(x)<1e8 for x in position):raise ValueError('bounded position required')
   result={'accepted':True,'position':position,'program':{'grammar':'walk.observation.v1','source':'player-observed offline/online walk','steps':[{'kind':p.get('kind','walk'),'position':position}]}}
   payload={**p,'kind':'journey.append','journey_kind':p.get('kind','walk'),'request_hash':fingerprint,'result':result}
  else:
   if self.world is None:self._init_world()
   if self.world is None:raise ValueError('world module unavailable')
   before=self.world.snapshot()
   if op=='world.tick':result=self.world.tick(float(p.get('dt',.1)))
   else:result=self.world.dispatch(op,p,actor=actor,capabilities=('founder',) if self.store.authorized(token,actor,'*') else ())
   if isinstance(result,dict) and result.get('status') in ['refused','error','unsupported','infeasible']:
    self.world=type(self.world).from_snapshot(before);return result
   result=result.get('data',result) if isinstance(result,dict) else result
   payload={'kind':'world.snapshot','snapshot':self.world.snapshot(),'operation':op,'request_hash':fingerprint,'result':result}
  event={'version':1,'event_id':eid,'session':session,'actor':actor,'payload':payload,'source_revision':'worldloom-v1','parents':[],'world_tick':getattr(self.world,'world_tick',0)}
  try:h=self.store.append(event,q.get('expected_head'))
  except ProtocolError as e:
   if op!='journey.append':self.world=type(self.world).from_snapshot(before)
   return {'status':'conflict','warnings':[str(e)]}
  except Exception:
   if op!='journey.append':self.world=type(self.world).from_snapshot(before)
   raise
  return {'status':'ok','data':result,'commit_id':h,'effects':[op],'trace_digest':digest(event)}
