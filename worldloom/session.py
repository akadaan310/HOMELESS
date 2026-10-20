"""Single authority for browser, Android and local renderer operations."""
from __future__ import annotations
import importlib,json,math,secrets,threading,uuid,time
from pathlib import Path
from .protocol import Store,Engine,canonical,digest,clock
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
   return {'version':1,'world':world,'continuity':self.store.checkpoint(),'objects':self.store.state()['objects'],'mode':'local-authoritative','clock':clock(getattr(self.world,'world_tick',0)),'source_quality':{'geography':'see /api/scene for source witnesses','aesthetic':'authored projection'}}
 def invoke(self,q):
  with self.lock:
   if not isinstance(q,dict):return {'status':'error','warnings':['map required']}
   op=q.get('operation','query');payload=q.get('payload',{})
   try:
    canonical(q)
    if not isinstance(payload,dict):raise ValueError('payload must be a map')
    if op in ['world.query','state']:return self._ok(self.snapshot())
    if op=='billboard.inspect':
     check=self.store.checkpoint();return self._ok({'program':'purl://dark/continuity/checkpoint','grammar':'typed read -> checkpoint -> verify','witness':check,'output':{'committed_events':check['count'],'state_hash':check['state_hash']},'exit_code':0,'source':'actual durable ledger; no host paths or credentials'})
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
     return self._ok(shell(payload['source'],engine=self) if op=='shell.run' else javascript(payload['source']) if op=='script.js' else wasm(payload['source']))
    if op in ['journey.append','npc.interact','speech.act','governance.propose','haven.enter','mission.accept','event.activate','world.tick']:
     return self._player_operation(q)
    return super().invoke(q)
   except (ValueError,TypeError,KeyError,AttributeError,ImportError) as e:return {'status':'error','warnings':[str(e)]}
 def _ok(self,data):return {'status':'ok','data':data,'commit_id':None,'effects':[],'trace_digest':digest(data)}
 def _gate(self,op,payload):
  # Planner API integration is finalized against the grammar lane's concrete API.
  if op=='gate.status':return self._ok({'plans':self.plans,'committed_events':self.store.verify()['count']})
  if op=='gate.cancel':
   key=payload.get('plan_id');plan=self.plans.get(key)
   if plan:plan['state']='canceled'
   return self._ok({'plan_id':key,'state':'canceled'})
  if op=='gate.prepare':
   key=payload.get('plan_id');plan=self.plans.get(key)
   if plan is None:raise ValueError('unknown plan')
   return self._ok(plan)
  position=payload.get('position',[0,0,0]);velocity=payload.get('velocity',[0,0,0])
  if len(position)!=3 or len(velocity)!=3 or not all(math.isfinite(float(x)) for x in position+velocity):raise ValueError('position/velocity')
  # Candidate metadata is public. Actual resource fetch/decoding is client-side.
  resources=[]
  p=ROOT/'artifacts/voice/catalog.json'
  if p.exists():
   catalog=json.loads(p.read_text());clips=catalog if isinstance(catalog,list) else catalog.get('clips',catalog.get('utterances',catalog.get('assets',[])))
   for clip in clips[:8]:
    if isinstance(clip,dict):resources.append(clip)
  plan={'plan_id':digest({'snapshot':self.store.verify()['head'],'position':position,'velocity':velocity,'resources':resources}),'state':'predicted','world_revision':self.store.verify()['head'],'resources':resources,'effect_policy':'prepare-only','activation':False,'expires_seconds':30}
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
   if isinstance(result,dict) and result.get('status') in ['refused','error','unsupported']:
    self.world=type(self.world).from_snapshot(before);return result
   payload={'kind':'world.snapshot','snapshot':self.world.snapshot(),'operation':op,'request_hash':fingerprint,'result':result}
  event={'version':1,'event_id':eid,'session':session,'actor':actor,'payload':payload,'source_revision':'worldloom-v1','parents':[],'world_tick':getattr(self.world,'world_tick',0)}
  try:h=self.store.append(event,q.get('expected_head'))
  except Exception:
   if op!='journey.append':self.world=type(self.world).from_snapshot(before)
   raise
  return {'status':'ok','data':result,'commit_id':h,'effects':[op],'trace_digest':digest(event)}
