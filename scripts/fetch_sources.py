#!/usr/bin/env python3
"""Retrieve immutable commission and historical sources; never overwrite differing files."""
import hashlib,pathlib,urllib.request,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
NAME='DARK_HOMELESS_CODEX_ONE_SHOT_MASTERPACK_2026_10_20.zip'
HASH='263e7c172e2a9ec9fabb6e916dd6fef03226fa3e21cb78c59c2fe42a0b98db95'
URL='https://github.com/akadaan310/HOMELESS/releases/download/masterpack-v1/'+NAME

def extract(z,dest):
 with zipfile.ZipFile(z) as archive:
  for f in archive.infolist():
   p=pathlib.PurePosixPath(f.filename)
   if p.is_absolute() or '..' in p.parts or (f.external_attr>>16)&0o170000==0o120000:raise ValueError('unsafe archive member')
   if f.is_dir():continue
   target=dest/pathlib.Path(*p.parts);data=archive.read(f)
   if target.exists() and target.read_bytes()!=data:raise ValueError('refusing to overwrite changed source '+str(target))
   target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)

def main():
 p=ROOT/'.cache'/NAME;p.parent.mkdir(exist_ok=True)
 if not p.exists():
  with urllib.request.urlopen(URL,timeout=120) as r,p.open('wb') as out:
   while b:=r.read(1024*1024):out.write(b)
 if p.stat().st_size!=95551079 or hashlib.sha256(p.read_bytes()).hexdigest()!=HASH:raise ValueError('masterpack checksum mismatch')
 extract(p,ROOT/'masterpack')
 for z in (ROOT/'masterpack/DARK_HOMELESS_CODEX_MASTERPACK_2026_10_20/inputs').glob('*.zip'):extract(z,ROOT/'upstream')
 print('Verified original archive and extracted historical source snapshots.')
if __name__=='__main__':main()
