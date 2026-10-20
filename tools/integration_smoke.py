#!/usr/bin/env python3
"""Actual daemon, typed channels, speech event and kill/restart verification."""
import hashlib,json,pathlib,subprocess,sys,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from worldloom.protocol import request,digest

def main():
 rows=[]
 with tempfile.TemporaryDirectory(prefix='worldloom-smoke-') as tmp:
  tmp=pathlib.Path(tmp);sock=tmp/'bus.sock';db=tmp/'world.db'
  def launch():
   p=subprocess.Popen([sys.executable,'-m','worldloom.cli','daemon','--socket',str(sock),'--db',str(db)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   deadline=time.monotonic()+15
   while time.monotonic()<deadline:
    if p.poll() is not None:raise RuntimeError(p.stderr.read().decode())
    try:request(sock,{'operation':'HELLO'});return p
    except (OSError,ValueError):time.sleep(.02)
   p.kill();p.wait();raise TimeoutError('daemon readiness')
  p=launch();token=db.with_suffix('.operator-token').read_text().strip()
  def call(channel,op,payload=None,**extra):
   q={'protocol':'seurl.world.v1','request_id':channel+'-fixture','operation':op,'payload':payload or {},**extra};start=time.perf_counter();r=request(sock,q)
   assert r['status']=='ok',(channel,r)
   rows.append({'channel':channel,'operation':op,'status':r['status'],'elapsed_ms':(time.perf_counter()-start)*1000,'result_hash':digest(r),'trace_digest':r.get('trace_digest'),'commit_id':r.get('commit_id')});return r
  try:
   call('continuity','HELLO');call('sound','audio.resolve');call('sky','sky.observer',{'limit':5});call('physics','physics.integrate',{'position':1,'velocity':2,'dt':1/60});call('math','math.solve',{})
   call('grammar','grammar.compile',{'subject':'audio','source':'emit bell 0.4 250'})
   for op,source in [('script.js',"JSON.stringify({kind:'sky.overlay',intensity:0.2})"),('script.wasm','(module (func (export "event") (result i32) i32.const 7))'),('shell.run',"printf 'Golden\\n' | tr a-z A-Z; darkctl time; darkctl propose sign.rename cafe 'Golden Haven'")]:
    r=call(op,op,{'source':source},actor='dark',capability=token)
    assert r['data'].get('status')=='ok',(op,r)
   before=request(sock,{'operation':'SNAPSHOT'})['data']
   gate=call('gate','gate.plan',{'position':[10,0,-4],'velocity':[1,0,0]})
   call('gate','gate.prepare',{'plan_id':gate['data']['plan_id']})
   assert request(sock,{'operation':'SNAPSHOT'})['data']==before
   q={'operation':'speech.act','payload':{'text':'hello','npc_id':'npc:0','position':[10,0,-4]},'event_id':'spoken-persistent-event','actor':'dark','session':'founder','capability':token}
   spoken=request(sock,q);assert spoken['status']=='ok' and spoken['commit_id'],spoken
   checkpoint=request(sock,{'operation':'SNAPSHOT'})['data']
   p.kill();p.wait();p.stderr.close();sock.unlink(missing_ok=True);p=launch()
   assert request(sock,{'operation':'SNAPSHOT'})['data']==checkpoint
   assert request(sock,q)['commit_id']==spoken['commit_id']
   result={'status':'pass','transport':'AF_UNIX + framed canonical CBOR','http_required':False,'channels':rows,'media_prepare_committed_events':0,'speech_reply':spoken['data'].get('response_text'),'speech_commit':spoken['commit_id'],'checkpoint':checkpoint,'restart_replay_identical':True,'duplicate_retry_exactly_once':True,'authority':'local operator fixture; token excluded','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
  finally:p.terminate();p.wait(timeout=5);p.stderr.close()
 out=ROOT/'evidence/service-integration.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'channels':len(rows),'checkpoint':checkpoint,'restart':True},indent=2))
if __name__=='__main__':main()
