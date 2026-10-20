"""Versioned semantic dispatcher, durable ACSP journal and host-local CBOR transport.

PURL/SEURL syntax here is the v1 adapter defined by the commission, not a claim
of compatibility with every historical research repository.
"""
from __future__ import annotations
import hashlib, io, json, math, os, secrets, socket, sqlite3, struct, time, uuid
from pathlib import Path
from urllib.parse import urlsplit, unquote
import cbor2

MAX_MESSAGE=1024*1024
class ProtocolError(ValueError): pass

def canonical(value):
 try:return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
 except (ValueError,TypeError) as e:raise ProtocolError('invalid/nonfinite JSON value') from e

def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()

def public_projection(value):
 if isinstance(value,list):return [public_projection(x) for x in value]
 if isinstance(value,dict):return {k:public_projection(v) for k,v in value.items() if not any(word in k.lower() for word in ['memory','memories','knowledge','belief','capabilit','token','private']) and k not in ['schedule','preferences','goals','relations']}
 return value

def clock(tick=0):return {'monotonic_engine_tick':tick,'real_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'world_epoch':'2026-10-20T19:00:00Z','presentation_clock':tick/60}

class Store:
 def __init__(self,path):
  self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
  self.db=sqlite3.connect(str(self.path),timeout=10,check_same_thread=False)
  os.chmod(self.path,0o600)
  self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
  self.db.executescript('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE,body TEXT,predecessor TEXT,hash TEXT); CREATE TABLE IF NOT EXISTS grants(token_hash TEXT PRIMARY KEY,actor TEXT,scopes TEXT,expires REAL,revoked INTEGER); CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT);')
  self.db.commit(); tokenpath=self.path.with_suffix('.operator-token')
  if not tokenpath.exists():
   fd=os.open(tokenpath,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
   with os.fdopen(fd,'w') as f:f.write(secrets.token_urlsafe(32))
  self.operator_token=tokenpath.read_text().strip()
  if not self.db.execute('SELECT 1 FROM grants WHERE token_hash=?',(hashlib.sha256(self.operator_token.encode()).hexdigest(),)).fetchone():self._grant(self.operator_token,'dark',['*'],time.time()+365*86400)
 def close(self):self.db.close()
 def _grant(self,token,actor,scopes,expires):
  self.db.execute('INSERT OR REPLACE INTO grants VALUES(?,?,?,?,0)',(hashlib.sha256(token.encode()).hexdigest(),actor,canonical(scopes),expires));self.db.commit();return token
 def grant(self,actor,scopes,ttl=3600):return self._grant(secrets.token_urlsafe(32),actor,scopes,time.time()+ttl)
 def revoke(self,token):self.db.execute('UPDATE grants SET revoked=1 WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),));self.db.commit()
 def authorized(self,token,actor,scope):
  if not isinstance(token,str) or not isinstance(actor,str):return False
  row=self.db.execute('SELECT actor,scopes,expires,revoked FROM grants WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
  return bool(row and row[0]==actor and not row[3] and row[2]>time.time() and ('*' in json.loads(row[1]) or scope in json.loads(row[1])))
 def verify(self):
  head='0'*64;count=0
  for seq,eid,body,parent,h in self.db.execute('SELECT * FROM events ORDER BY seq'):
   if parent!=head or hashlib.sha256((head+body).encode()).hexdigest()!=h:return {'valid':False,'count':count,'head':head,'bad_seq':seq}
   head=h;count+=1
  return {'valid':True,'count':count,'head':head}
 def checkpoint(self):
  check=self.verify()
  if not check['valid']:raise ProtocolError('journal corruption')
  return {**check,'state_hash':digest(self.state())}
 def replay(self,until_hash=None):
  if not self.verify()['valid']:raise ProtocolError('journal corruption')
  if until_hash=='0'*64:return []
  rows=[]
  for body,h in self.db.execute('SELECT body,hash FROM events ORDER BY seq'):
   rows.append(json.loads(body))
   if h==until_hash:return rows
  if until_hash is not None:raise ProtocolError('unknown pinned context')
  return rows
 def state(self,until_hash=None):
  state={'objects':{},'sessions':{},'world':None}
  for e in self.replay(until_hash):
   p=e['payload'];kind=p['kind']
   if kind=='sign.rename':state['objects'][p['object']]={'text':p['text'],'author':e['actor'],'event_id':e['event_id']}
   elif kind=='journey.append':state['sessions'].setdefault(e['session'],[]).append(p)
   elif kind=='world.snapshot':state['world']=p['snapshot']
   elif kind=='event.activate':state['objects'][p['object']]=p
  return state
 def append(self,event,expected_head=None):
  body=canonical(event)
  try:
   self.db.execute('BEGIN IMMEDIATE')
   prior=self.db.execute('SELECT body,hash FROM events WHERE event_id=?',(event['event_id'],)).fetchone()
   if prior:
    self.db.rollback()
    if prior[0]!=body:raise ProtocolError('duplicate event_id has different content')
    return prior[1]
   check=self.verify()
   if not check['valid']:raise ProtocolError('journal corruption')
   if expected_head is not None and expected_head!=check['head']:raise ProtocolError('predecessor conflict')
   h=hashlib.sha256((check['head']+body).encode()).hexdigest()
   self.db.execute('INSERT INTO events(event_id,body,predecessor,hash) VALUES(?,?,?,?)',(event['event_id'],body,check['head'],h));self.db.commit();return h
  except Exception:
   self.db.rollback();raise

CHANNELS={
 'world':['query','simulate','propose','commit'], 'sound':['describe','render','mix'],
 'sky':['describe','observer','discover'], 'physics':['describe','integrate'],
 'math':['describe','solve','camera','weather'], 'shell':['describe','run'],
 'continuity':['HELLO','DISCOVER','OPEN','SNAPSHOT','APPEND','RESUME','ACK','REPLAY','VERIFY','CLOSE','CONFLICT'],
 'model':['describe','compile','validate','expand','run'],'dialog':['describe','act'],
 'gate':['plan','prepare','cancel','status'],'audio':['describe','resolve'],'billboard':['inspect']}

def describe():return {'version':1,'wire':'4-byte big-endian length + canonical CBOR','transport':'AF_UNIX','channels':{k:{'operations':v,'budget':{'bytes':MAX_MESSAGE,'ms':1000},'write_scope':'explicit capability per effect','clock':'fixed60+UTC','replay':'versioned source and canonical input; media timing nondeterministic'} for k,v in CHANNELS.items()}}

class Engine:
 def __init__(self,store):self.store=store
 def invoke(self,q):
  req=q.get('request_id') if isinstance(q,dict) else None
  base={'request_id':req,'status':'ok','data':{},'commit_id':None,'effects':[],'source_versions':['worldloom-v1'],'warnings':[]}
  try:
   canonical(q)
   if not isinstance(q,dict):raise ProtocolError('request must be a map')
   op=q.get('operation','query');payload=q.get('payload',{});actor=q.get('actor','guest')
   if not isinstance(payload,dict):raise ProtocolError('payload must be a map')
   if op in ['describe','DISCOVER','HELLO']:data=describe()
   elif op in ['query','resolve','inspect']:data=self.resolve(q.get('program','purl://dark/world/state'),q.get('context_hash'))
   elif op in ['SNAPSHOT','RESUME','VERIFY','checkpoint']:data=self.store.checkpoint()
   elif op=='REPLAY':
    if not self.store.authorized(q.get('capability',''),actor,'continuity.read'):return {**base,'status':'refused'}
    data=self.store.replay()
   elif op=='propose':data={'proposal':payload,'admitted':False,'reason':'proposals require explicit commit authority'}
   elif op in ['commit','APPEND']:
    kind=payload.get('kind');allowed={'sign.rename','journey.append','world.snapshot','event.activate'}
    if kind not in allowed:raise ProtocolError('unknown typed effect')
    if not self.store.authorized(q.get('capability',''),actor,kind):return {**base,'status':'refused','warnings':['missing, expired, or wrong actor capability']}
    for k in ['event_id','session']:
     if not isinstance(q.get(k),str) or not 1<=len(q[k])<=128:raise ProtocolError('missing/bounded '+k)
    if kind=='sign.rename':
     if not isinstance(payload.get('text'),str) or not 1<=len(payload['text'])<=160:raise ProtocolError('sign text length')
     if not isinstance(payload.get('object'),str) or not payload['object']:raise ProtocolError('object required')
    elif kind=='world.snapshot':
     if not isinstance(payload.get('snapshot'),dict):raise ProtocolError('world snapshot required')
     try:
      from .society import World
      World.from_snapshot(payload['snapshot'])
     except (ImportError,ValueError,KeyError,TypeError,AttributeError) as e:raise ProtocolError('invalid versioned world snapshot') from e
    elif kind=='event.activate':
     if not isinstance(payload.get('object'),str) or not payload['object']:raise ProtocolError('event object required')
    elif kind=='journey.append':
     position=payload.get('position')
     if not isinstance(position,list) or len(position)!=3 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in position):raise ProtocolError('journey position required')
    if len(canonical(payload))>512*1024:raise ProtocolError('effect too large')
    event={'version':1,'event_id':q['event_id'],'session':q['session'],'actor':actor,'payload':payload,'source_revision':q.get('source_revision','worldloom-v1'),'parents':q.get('parents',[]),'world_tick':q.get('world_tick',0)}
    try:h=self.store.append(event,q.get('expected_head'))
    except ProtocolError as e:return {**base,'status':'conflict','warnings':[str(e)]}
    return {**base,'data':{'event_id':q['event_id']},'commit_id':h,'effects':[kind],'trace_digest':digest(event)}
   elif op=='time':data=clock(self.store.verify()['count'])
   else:return {**base,'status':'unsupported','warnings':['unknown operation '+str(op)]}
   return {**base,'data':data,'trace_digest':digest(data)}
  except (ProtocolError,ValueError,TypeError,KeyError) as e:return {**base,'status':'error','warnings':[str(e)]}
 def resolve(self,url,context=None):
  u=urlsplit(url)
  if u.scheme!='purl' or u.netloc!='dark' or u.fragment:raise ProtocolError('invalid PURL scheme/authority/fragment')
  path=unquote(u.path)
  if '..' in path.split('/'):raise ProtocolError('invalid path')
  if path.startswith('/world/state@') and path!='/world/state@v1':context=path.split('@',1)[1];path='/world/state'
  if path in ['/world/state','/world/state@v1']:
   pinned=context.removeprefix('sha256:') if isinstance(context,str) else context
   s=self.store.state(pinned);return {'objects':s['objects'],'world':public_projection(s['world']),'context_hash':context,'revision':pinned if pinned is not None else self.store.verify()['head']}
  if path=='/continuity/checkpoint':return self.store.checkpoint()
  if path.startswith('/journey/') and path.endswith('/program'):
   session=path.split('/')[2]
   # Only public journey parse is available here; private session ledger is not exposed.
   return {'program':[],'session':session,'quality':'requires authorized session adapter','context_hash':context}
  raise ProtocolError('unresolved PURL')

def _receive(sock,n):
 data=b''
 while len(data)<n:
  part=sock.recv(n-len(data))
  if not part:raise ProtocolError('truncated frame')
  data+=part
 return data

def receive(sock):
 n=struct.unpack('!I',_receive(sock,4))[0]
 if n>MAX_MESSAGE or n==0:raise ProtocolError('message budget exceeded')
 stream=io.BytesIO(_receive(sock,n))
 try:
  value=cbor2.CBORDecoder(stream).decode()
  if stream.tell()!=n:raise ProtocolError('trailing CBOR data')
  return value
 except (cbor2.CBORDecodeError,RecursionError,OverflowError) as e:raise ProtocolError('invalid CBOR frame') from e

def send(sock,obj):
 b=cbor2.dumps(obj,canonical=True)
 if len(b)>MAX_MESSAGE:raise ProtocolError('response exceeds budget')
 sock.sendall(struct.pack('!I',len(b))+b)

def request(socket_path,envelope):
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
  s.settimeout(5);s.connect(str(socket_path));send(s,envelope);return receive(s)

def serve(socket_path,engine):
 p=Path(socket_path);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():p.unlink()
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
  s.bind(str(p));os.chmod(p,0o600);s.listen(16);s.settimeout(.5)
  try:
   while True:
    try:c,_=s.accept()
    except socket.timeout:continue
    with c:
     c.settimeout(2)
     try:send(c,engine.invoke(receive(c)))
     except (ProtocolError,ValueError,OSError,RecursionError) as e:
      try:send(c,{'status':'error','warnings':[str(e)]})
      except OSError:pass
  finally:p.unlink(missing_ok=True)
