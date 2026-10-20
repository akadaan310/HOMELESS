#!/usr/bin/env python3
"""Restore exact archival masters from tracked source URLs and SHA256 witnesses.

Shipped runtime GLBs do not require multi-GB masters. This command does not accept
changed bytes at a publisher URL as an equivalent version.
"""
import argparse,json,pathlib,sys,urllib.parse
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from assets import ROOT,ASSETS,curl,sha,archive,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument('--ids',nargs='*');a=p.parse_args();catalog=json.load(open(ASSETS/'catalog.json'));files={};selected=[]
 for e in catalog['assets']:
  if a.ids and e['id'] not in a.ids:continue
  selected.append(e)
  for f in e.get('files',[]):files[f['path']]=f
 failures=[];restored=0
 for name,f in files.items():
  dest=(ROOT/name).resolve()
  if ASSETS.resolve() not in dest.parents:raise RuntimeError('Source destination outside asset store')
  if dest.exists() and sha(dest)==f['sha256']:continue
  if not f.get('url'):failures.append({'path':name,'error':'missing tracked download URL'});continue
  try:
   temporary=dest.with_name(dest.name+'.restore');temporary.unlink(missing_ok=True);curl(f['url'],temporary,f.get('publisher_md5'))
   if sha(temporary)!=f['sha256']:raise ValueError('Publisher bytes changed: exact SHA256 restore refused')
   temporary.replace(dest);archive(dest);restored+=1
  except Exception as exc:failures.append({'path':name,'error':str(exc)})
 for e in selected:
  if e.get('kind') in ('polyhaven','glb','gltf'):write_json(ASSETS/'originals'/e['id']/'source-manifest.json',e)
 result={'restored':restored,'exact_source_files':len(files),'failures':failures};print(json.dumps(result,indent=2));return bool(failures)
if __name__=='__main__':raise SystemExit(main())
