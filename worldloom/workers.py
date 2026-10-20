"""Real isolated BusyBox shell, bounded QuickJS and fuel-limited Wasmtime."""
from __future__ import annotations
import hashlib,json,os,selectors,signal,socket,struct,subprocess,sys,tempfile,threading,time
from pathlib import Path
from .protocol import canonical,digest,clock
ROOT=Path(__file__).resolve().parents[1]

def _bounded(cmd,*,input_text=None,timeout=1,limit=65536,env=None):
 start=time.monotonic();p=subprocess.Popen(cmd,stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,env=env)
 if input_text is not None:p.stdin.write(input_text.encode());p.stdin.close()
 sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ,'stdout');sel.register(p.stderr,selectors.EVENT_READ,'stderr');out={'stdout':bytearray(),'stderr':bytearray()};timed=False;limited=False
 while sel.get_map():
  if time.monotonic()-start>timeout:
   timed=True
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
  for key,_ in sel.select(.02):
   b=os.read(key.fileobj.fileno(),4096)
   if not b:sel.unregister(key.fileobj);continue
   remaining=limit-len(out[key.data]);out[key.data].extend(b[:max(0,remaining)])
   if len(b)>remaining:
    limited=True
    try:os.killpg(p.pid,signal.SIGKILL)
    except ProcessLookupError:pass
 p.wait();sel.close();p.stdout.close();p.stderr.close()
 return {'exit_code':p.returncode,**{k:bytes(v).decode('utf8','replace') for k,v in out.items()},'timed_out':timed,'output_limited':limited,'elapsed_ms':round((time.monotonic()-start)*1000,3)}

def shell(script,wall_time_ms=1000,max_output_bytes=65536,engine=None):
 if not isinstance(script,str) or len(script.encode())>65536:raise ValueError('script budget')
 if not 10<=wall_time_ms<=5000 or not 128<=max_output_bytes<=65536:raise ValueError('execution budget')
 busybox=ROOT/'.cache/sysroot/usr/bin/busybox';client=ROOT/'artifacts/runtime/darkctl'
 if not busybox.exists() or not client.exists():return {'status':'blocked','blocker':'run scripts/provision.sh and scripts/build_runtime.sh'}
 proposed=[];ticks=[0];stop=threading.Event()
 with tempfile.TemporaryDirectory(prefix='worldloom-') as tmp:
  tmp=Path(tmp);work=tmp/'work';work.mkdir();bus=tmp/'bus';bus.mkdir();(work/'job.sh').write_text(script)
  from .protocol import Engine,Store
  localstore=None
  if engine is None:localstore=Store(tmp/'world.db');engine=Engine(localstore)
  broker=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);broker.bind(str(bus/'control.sock'));broker.listen(4);broker.settimeout(.1)
  def handle():
   while not stop.is_set():
    try:c,_=broker.accept()
    except socket.timeout:continue
    except OSError:break
    with c:
     c.settimeout(.5)
     try:
      h=c.recv(4,socket.MSG_WAITALL);n=struct.unpack('!I',h)[0]
      if n>65536:continue
      q=json.loads(c.recv(n,socket.MSG_WAITALL));cmd=q['command'];args=q['args'];data=None;code=0
      if cmd=='time':data=clock(ticks[0])
      elif cmd=='sleep' and len(args)==2 and args[0]=='--ticks':
       v=int(args[1])
       if not 0<=v<=36000:raise ValueError('tick budget')
       ticks[0]+=v;data=clock(ticks[0])
      elif cmd in ['query','inspect']:data=engine.invoke({'operation':'query','program':args[0] if args else 'purl://dark/world/state'})
      elif cmd=='curl' and len(args)==1:
       from urllib.parse import urlsplit
       u=urlsplit(args[0])
       if u.scheme!='https' or u.username or u.password or u.hostname not in ['api.github.com','api.open-meteo.com']:raise ValueError('fetch destination not allowed')
       fetched=_bounded(['/usr/bin/curl','--fail','--silent','--show-error','--proto','=https','--max-time','2',args[0]],timeout=2.5,limit=16384)
       data={'transport':'stock curl HTTPS via broker','result':fetched['stdout'],'exit':fetched['exit_code']};code=0 if fetched['exit_code']==0 else 2
      elif cmd=='propose' and len(args)==3 and args[0]=='sign.rename' and 0<len(args[2])<=160:
       data={'kind':'sign.rename','object':args[1],'text':args[2]};proposed.append(data)
      else:code=2;data={'reason':'unsupported command or typed arguments'}
      r={'request_id':digest(q),'command':cmd,'exit':code,'data':data,'output_digest':digest(data),'elapsed_tick':ticks[0],'effects_proposed':proposed,'effects_committed':[]}
     except Exception as e:r={'exit':2,'reason':str(e)}
     b=canonical(r).encode();c.sendall(struct.pack('!I',len(b))+b)
  thread=threading.Thread(target=handle,daemon=True);thread.start()
  cmd=['bwrap','--die-with-parent','--unshare-all','--new-session','--clearenv','--setenv','PATH','/bin','--dir','/bin','--ro-bind',str(busybox),'/bin/busybox','--ro-bind',str(client),'/bin/darkctl','--symlink','darkctl','/bin/curl','--bind',str(work),'/work','--ro-bind',str(bus),'/bus','--tmpfs','/tmp','--dev','/dev','--chdir','/work']
  for a in ['ash','sh','cat','printf','echo','tr','wc','sort','head','tail','sed','cut','true','false','test','pwd','ls','mkdir','date','kill']:
   cmd+=['--symlink','busybox','/bin/'+a]
  cmd+=['--','/bin/ash','/work/job.sh']
  try:r=_bounded(cmd,timeout=wall_time_ms/1000,limit=max_output_bytes,env={'PATH':os.environ.get('PATH','/usr/bin:/bin')})
  finally:
   stop.set();broker.close();thread.join(timeout=3)
   if localstore:localstore.close()
  return {**r,'status':'timeout' if r['timed_out'] else 'ok' if r['exit_code']==0 else 'error','typed_effects_proposed':proposed,'effects_committed':[],'trace_digest':digest({'script':script,'proposals':proposed}),'script_hash':hashlib.sha256(script.encode()).hexdigest(),'isolation':'bubblewrap unshare-all, minimal root, private /work, no inherited secrets or host network','clock_snapshot':clock(ticks[0])}

def _script(kind,source,wall_time_ms,**kwargs):
 if not isinstance(source,str) or len(source.encode())>65536:raise ValueError('program budget')
 q={'kind':kind,'source':source,'wall_time_ms':wall_time_ms,**kwargs}
 r=_bounded([sys.executable,'-m','worldloom.workers','--child'],input_text=canonical(q),timeout=wall_time_ms/1000+2,limit=65536,env={'PATH':os.environ.get('PATH',''),'PYTHONPATH':str(ROOT),'PYTHONUSERBASE':os.environ.get('PYTHONUSERBASE',str(Path.home()/'.local'))})
 if r['timed_out']:return {**r,'status':'timeout'}
 try:return {**json.loads(r['stdout']),'elapsed_ms':r['elapsed_ms']}
 except (json.JSONDecodeError,TypeError):return {**r,'status':'error'}

def javascript(source,wall_time_ms=100):return _script('js',source,wall_time_ms)
def wasm(source,wall_time_ms=500,fuel=100000):return _script('wasm',source,wall_time_ms,fuel=fuel)

def _child(q):
 try:
  if q['kind']=='js':
   import quickjs
   ctx=quickjs.Context();ctx.set_memory_limit(32*1024*1024);ctx.set_max_stack_size(256*1024);ctx.set_time_limit(q['wall_time_ms']/1000)
   result=ctx.eval(q['source'])
   if not isinstance(result,str):raise ValueError('script must return JSON string')
   event=json.loads(result)
   if not isinstance(event,dict) or event.get('kind') not in ['sky.overlay','sound.cue','sign.proposal']:raise ValueError('unadmitted event kind')
  else:
   import wasmtime
   config=wasmtime.Config();config.consume_fuel=True;engine=wasmtime.Engine(config);module=wasmtime.Module(engine,q['source'])
   if list(module.imports):raise ValueError('host imports forbidden')
   store=wasmtime.Store(engine);store.set_fuel(q['fuel']);store.set_limits(memory_size=32*1024*1024,instances=1,memories=1,tables=1)
   instance=wasmtime.Instance(store,module,[]);value=instance.exports(store)['event'](store);event={'kind':'wasm.event','value':value}
  canonical(event);return {'status':'ok','event':event,'effects_committed':[],'trace_digest':digest({'source':q['source'],'event':event})}
 except Exception as e:
  s=str(e);return {'status':'timeout' if 'interrupted' in s or 'fuel' in s else 'error','reason':s[:1000],'effects_committed':[]}

if __name__=='__main__':print(canonical(_child(json.loads(sys.stdin.read(100000)))))
