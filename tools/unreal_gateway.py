#!/usr/bin/env python3
"""Linux presentation gateway: length-framed JSON <-> authoritative CBOR IPC.

This is not a Pixel Streaming server. It never creates grants or commits effects
on behalf of a presentation client; an invoke passes its original envelope.
"""
from __future__ import annotations
import argparse,json,os,pathlib,socket,socketserver,struct,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from worldloom.protocol import MAX_MESSAGE,request,canonical

def receive(sock,n):
    out=bytearray()
    while len(out)<n:
        block=sock.recv(n-len(out))
        if not block:raise ValueError('truncated JSON frame')
        out.extend(block)
    return bytes(out)

def dispatch(q,engine_socket):
    if not isinstance(q,dict) or q.get('protocol')!='worldloom.unreal.v1':raise ValueError('worldloom.unreal.v1 required')
    op=q.get('operation')
    if op=='projection':
        result=request(engine_socket,{'request_id':q.get('request_id'),'protocol':'seurl.world.v1','actor':'unreal-renderer','operation':'query','program':'purl://dark/world/state','payload':{}})
        if result.get('status')=='ok':
            data=result.get('data',{});world=data.get('world') or {}
            # Keep complete source projection in data; do not manufacture world
            # simulation ticks, weather measurements, or player coordinates.
            origin=world.get('origin',{})
            projection={'session_id':q.get('session_id',''),'source_quality':origin.get('source_kind','unknown')}
            if 'tick' in world:projection['tick']=world['tick']
            if 'lat' in origin:projection['latitude']=origin['lat']
            if 'lon' in origin:projection['longitude']=origin['lon']
            # Do not mutate the witnessed daemon data after its trace digest.
            result['presentation']=projection
        return result
    if op=='invoke':
        envelope=q.get('payload')
        if not isinstance(envelope,dict):raise ValueError('invoke payload must be a complete typed envelope')
        # The daemon remains the only authority for actor/capability validation.
        result=request(engine_socket,envelope)
        return result
    if op=='describe':return {'request_id':q.get('request_id'),'status':'ok','data':{'protocol':'worldloom.unreal.v1','wire':'4-byte big-endian JSON; max1MiB','authority':'ACSP CBOR daemon','operations':['projection','invoke','describe'],'engine_socket':str(engine_socket)}}
    return {'request_id':q.get('request_id'),'status':'unsupported','warnings':['unknown renderer operation']}

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(3)
        try:
            size=struct.unpack('!I',receive(self.request,4))[0]
            if not 0<size<=MAX_MESSAGE:raise ValueError('frame byte budget exceeded')
            q=json.loads(receive(self.request,size));canonical(q)
            result=dispatch(q,self.server.engine_socket)
        except Exception as exc:result={'status':'error','warnings':[str(exc)[:300]]}
        payload=canonical(result).encode()
        if len(payload)>MAX_MESSAGE:payload=canonical({'status':'error','warnings':['response budget exceeded']}).encode()
        try:self.request.sendall(struct.pack('!I',len(payload))+payload)
        except OSError:pass

class Server(socketserver.ThreadingUnixStreamServer):
    daemon_threads=True
    def __init__(self,path,engine_socket):
        self.engine_socket=engine_socket
        super().__init__(str(path),Handler);os.chmod(path,0o600)

def main():
    p=argparse.ArgumentParser();p.add_argument('--socket',default='/tmp/worldloom-unreal.sock');p.add_argument('--engine-socket',default=str(ROOT/'.runtime/worldloom.sock'));a=p.parse_args()
    path=pathlib.Path(a.socket);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise SystemExit('Socket already exists; stop the prior gateway before restarting: '+str(path))
    try:
        with Server(path,a.engine_socket) as server:
            print('Unreal JSON adapter ready: '+str(path),flush=True);server.serve_forever(poll_interval=.2)
    except KeyboardInterrupt:pass
    finally:path.unlink(missing_ok=True)
if __name__=='__main__':main()
