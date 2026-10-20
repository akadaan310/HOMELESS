#!/usr/bin/env python3
"""Fetch pinned speech sources and verify hashes; models stay outside application startup."""
import argparse,hashlib,json,sys,tarfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--include-evaluation',action='store_true');args=parser.parse_args()
    manifest=json.loads((ROOT/'data/voice/sources.json').read_text())
    for source in manifest['sources']:
        if not source.get('required',False) and not args.include_evaluation:continue
        path=ROOT/source['path'];path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:
            temporary=path.with_name(path.name+'.download')
            urllib.request.urlretrieve(source['url'],temporary)
            if hashlib.sha256(temporary.read_bytes()).hexdigest()!=source['sha256']:
                temporary.unlink();raise ValueError('source hash changed: '+source['path'])
            temporary.replace(path)
        print(source['path'],path.stat().st_size,flush=True)
        if source.get('extract_to'):
            destination=(ROOT/source['extract_to']).resolve();destination.mkdir(parents=True,exist_ok=True)
            with tarfile.open(path) as tf:
                # Python tar data filter rejects path traversal, device and escaping links.
                tf.extractall(destination,filter='data')


if __name__=='__main__':main()
