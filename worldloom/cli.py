"""Local engine operator CLI. No HTTP is needed for daemon/inspect/propose."""
import argparse,json,sys
from pathlib import Path
from .protocol import Store,Engine,request,serve,canonical

def main():
 p=argparse.ArgumentParser(prog='darkctl');p.add_argument('command',choices=['daemon','time','query','inspect','propose','invoke','checkpoint','verify']);p.add_argument('args',nargs='*');p.add_argument('--socket',default='.runtime/worldloom.sock');p.add_argument('--db',default='.runtime/worldloom.db');p.add_argument('--json');a=p.parse_args()
 if a.command=='daemon':
  store=Store(a.db)
  try:serve(a.socket,Engine(store))
  except KeyboardInterrupt:pass
  finally:store.close()
  return 0
 if a.command=='invoke':q=json.loads(a.json or sys.stdin.read())
 elif a.command in ['checkpoint','verify']:q={'operation':'SNAPSHOT' if a.command=='checkpoint' else 'VERIFY'}
 elif a.command in ['query','inspect']:q={'operation':'query','program':a.args[0] if a.args else 'purl://dark/world/state'}
 elif a.command=='propose':
  if len(a.args)!=3:p.error('propose requires kind object text')
  q={'operation':'propose','payload':dict(zip(['kind','object','text'],a.args))}
 else:q={'operation':'time'}
 r=request(a.socket,q);print(canonical(r));return 0 if r['status']=='ok' else 1
if __name__=='__main__':raise SystemExit(main())
