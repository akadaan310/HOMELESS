"""Loopback client gateway and static release host; local engine uses separate IPC."""
from __future__ import annotations
import argparse,base64,hashlib,json,mimetypes,os,secrets,threading,time,uuid
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit,unquote
from .protocol import canonical
from .session import WorldSession,ROOT

class Handler(BaseHTTPRequestHandler):
 server_version='WorldLoom/0.1'
 def log_message(self,format,*args):pass
 def _json(self,obj,status=200):
  data=canonical(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
 def do_GET(self):
  path=urlsplit(self.path).path
  try:
   if path=='/api/health':return self._json({'status':'ok','engine':'WorldLoom','version':1,'render_host':'Unreal unavailable; Rendezvous client'})
   if path=='/api/state':return self._json(self.server.session.snapshot())
   if path=='/api/scene':
    from .geo import scene
    return self._json(scene('tampa'))
   if path=='/api/voice':return self._json(self.server.session.invoke({'operation':'voice.catalog'}))
   if path.startswith('/api/'):return self._json({'status':'unsupported'},404)
   decoded=unquote(path)
   if '\\' in decoded or '..' in decoded.split('/'):return self._json({'status':'refused'},403)
   if decoded.startswith(('/artifacts/voice/','/artifacts/audio/','/assets/','/data/geo/')):
    target=(ROOT/decoded.lstrip('/')).resolve()
    if ROOT not in target.parents:return self._json({'status':'refused'},403)
   else:
    target=(self.server.webroot/decoded.lstrip('/')).resolve()
    if self.server.webroot not in target.parents and target!=self.server.webroot:return self._json({'status':'refused'},403)
    if target.is_dir():target=target/'index.html'
   if not target.is_file():return self._json({'status':'missing','path':path},404)
   content=target.read_bytes();self.send_response(200);mime=mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
   if target.suffix=='.wasm':mime='application/wasm'
   self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(content)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-cache');self.end_headers();self.wfile.write(content)
  except Exception as e:self._json({'status':'error','warnings':[str(e)[:300]]},500)
 def do_POST(self):
  try:
   origin=self.headers.get('Origin')
   if origin and urlsplit(origin).netloc!=self.headers.get('Host'):
    return self._json({'status':'refused','reason':'cross-origin write'},403)
   length=int(self.headers.get('Content-Length','0'))
   if not 0<=length<=6*1024*1024:return self._json({'status':'error','reason':'payload budget'},413)
   data=json.loads(self.rfile.read(length) or b'{}');path=urlsplit(self.path).path
   if not isinstance(data,dict):raise ValueError('request must be object')
   if path=='/api/session':return self._json(self.server.session.open_player())
   token=self.headers.get('Authorization','').removeprefix('Bearer ')
   with self.server.session.lock:
    row=self.server.session.store.db.execute('SELECT actor FROM grants WHERE token_hash=? AND revoked=0 AND expires>?',(hashlib.sha256(token.encode()).hexdigest(),time.time())).fetchone()
   actor=row[0] if row else 'guest';session=actor[7:] if actor.startswith('player:') else data.get('session','')
   if path=='/api/transcribe':
    if not row:return self._json({'status':'refused'},403)
    from .voice import transcribe_audio
    b=base64.b64decode(data['audio_base64'],validate=True)
    if len(b)>4*1024*1024:raise ValueError('audio budget exceeded')
    return self._json({'status':'ok','data':transcribe_audio(b,mime_type=data.get('mime_type','audio/webm'),locale=data.get('locale','en-US'))})
   if path!='/api/operation':return self._json({'status':'unsupported'},404)
   q={'operation':data.get('operation'),'payload':data.get('payload',{}),'event_id':data.get('event_id',uuid.uuid4().hex),'session':session,'actor':actor,'capability':token}
   response=self.server.session.invoke(q);return self._json(response,403 if response.get('status')=='refused' else 200)
  except (ValueError,TypeError,KeyError) as e:return self._json({'status':'error','warnings':[str(e)[:300]]},400)
  except ImportError:return self._json({'status':'blocked','warnings':['ASR worker not provisioned; text and tap remain available']},503)
  except Exception as e:return self._json({'status':'error','warnings':[str(e)[:300]]},500)

def make_server(host='127.0.0.1',port=8080,db='.runtime/worldloom.db',webroot=None):
 server=ThreadingHTTPServer((host,port),Handler);server.session=WorldSession(db)
 if webroot is None:
  webroot=ROOT/'web/dist' if (ROOT/'web/dist/index.html').exists() else ROOT/'artifacts/web' if (ROOT/'artifacts/web/index.html').exists() else ROOT/'web'
 server.webroot=Path(webroot).resolve();return server

def main():
 p=argparse.ArgumentParser();p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8080);p.add_argument('--db',default='.runtime/worldloom.db');p.add_argument('--webroot');a=p.parse_args();s=make_server(a.host,a.port,a.db,a.webroot)
 stop=threading.Event()
 def ambient():
  last=time.monotonic();lastsave=last
  while not stop.wait(.5):
   try:
    now=time.monotonic()
    with s.session.lock:
     w=s.session.world
     if w:
      w.tick(min(now-last,1));last=now
      if now-lastsave>=10:
       payload={'kind':'world.snapshot','snapshot':w.snapshot(),'operation':'ambient.tick'}
       event={'version':1,'event_id':uuid.uuid4().hex,'session':'ambient','actor':'simulation','payload':payload,'source_revision':'worldloom-v1','parents':[],'world_tick':getattr(w,'world_tick',0)}
       s.session.store.append(event);lastsave=now
   except Exception as e:print('ambient worker:',str(e)[:200],flush=True)
 t=threading.Thread(target=ambient,daemon=True);t.start();print(f'HOMELESS local gateway: http://{a.host}:{s.server_port}',flush=True)
 try:s.serve_forever()
 except KeyboardInterrupt:pass
 finally:stop.set();t.join(timeout=2);s.server_close();s.session.close()
if __name__=='__main__':main()
