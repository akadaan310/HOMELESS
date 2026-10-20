#!/usr/bin/env python3
"""Compile shared native IPC client and exercise actual JSON -> CBOR authority."""
import hashlib,json,pathlib,subprocess,sys,tempfile,time,uuid
ROOT=pathlib.Path(__file__).resolve().parents[1]
def ready(path,process):
    for _ in range(200):
        if path.exists():return
        if process.poll() is not None:raise RuntimeError('service terminated')
        time.sleep(.02)
    raise RuntimeError('socket startup timeout')
def main():
    binary=ROOT/'artifacts/assets/unreal_native_probe';binary.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['g++','-std=c++20','-Wall','-Wextra','-Werror','-I',str(ROOT/'unreal/Homeless/Source/Homeless/Public'),str(ROOT/'tools/unreal_native_probe.cpp'),'-o',str(binary)],check=True)
    with tempfile.TemporaryDirectory(prefix='homeless-ue-') as d:
        base=pathlib.Path(d);engine=base/'engine.sock';gateway=base/'ue.sock'
        daemon=subprocess.Popen([sys.executable,'-m','worldloom.cli','daemon','--socket',str(engine),'--db',str(base/'world.db')],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        adapter=None
        try:
            ready(engine,daemon)
            adapter=subprocess.Popen([sys.executable,str(ROOT/'tools/unreal_gateway.py'),'--socket',str(gateway),'--engine-socket',str(engine)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            ready(gateway,adapter)
            results=[]
            for query in [
                {'protocol':'worldloom.unreal.v1','request_id':'native-projection','operation':'projection','session_id':'interop'},
                {'protocol':'worldloom.unreal.v1','request_id':'native-denied','operation':'invoke','payload':{'operation':'commit','actor':'unreal-renderer','session':'interop','event_id':uuid.uuid4().hex,'payload':{'kind':'sign.rename','object':'fixture','text':'Not authorized'}}},
                {'protocol':'wrong','operation':'projection'},
            ]:
                completed=subprocess.run([str(binary),str(gateway),json.dumps(query)],capture_output=True,text=True,check=True)
                results.append(json.loads(completed.stdout))
            assert results[0]['status']=='ok' and len(results[0]['trace_digest'])==64
            canonical=json.dumps(results[0]['data'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
            assert hashlib.sha256(canonical.encode()).hexdigest()==results[0]['trace_digest'],'gateway mutated witnessed authority data'
            assert results[1]['status']=='refused'
            assert results[2]['status']=='error'
            report={'status':'passed','compiler':'g++ -std=c++20 -Wall -Wextra -Werror','shared_header':'unreal/Homeless/Source/Homeless/Public/WorldLoomFrameClient.h','native_client':'artifacts/assets/unreal_native_probe','transport':'native AF_UNIX framed JSON -> Python gateway -> AF_UNIX canonical CBOR WorldSession daemon','checks':['actual source-world projection returned','native round-trip trace digest','unauthorized effect refused by daemon','wrong protocol refused'],'results':results,'unreal_module_compiled':False,'unreal_sdk_blocker':'SDK absent; this verifies shared native transport independently'}
            (ROOT/'evidence/unreal_native_interop.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
        finally:
            if adapter:adapter.terminate();adapter.wait(timeout=5)
            daemon.terminate();daemon.wait(timeout=5)
if __name__=='__main__':main()
