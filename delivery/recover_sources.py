#!/usr/bin/env python3
"""HD-004/009/048/085: verify reference bytes before safe extraction; execute nothing."""
import hashlib, io, json, pathlib, stat, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def inspect(data, depth=0):
    if depth > 5: raise ValueError('archive nesting budget')
    rows=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        infos=z.infolist()
        if len(infos)>10000 or sum(i.file_size for i in infos)>128*1024*1024: raise ValueError('archive expansion budget')
        names=set()
        for i in infos:
            p=pathlib.PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in i.filename or stat.S_ISLNK(i.external_attr>>16) or i.filename in names: raise ValueError('unsafe/duplicate member')
            names.add(i.filename)
            if i.is_dir(): continue
            b=z.read(i); row=dict(path=i.filename,bytes=len(b),sha256=sha(b))
            if i.filename.lower().endswith('.zip'): row['members']=inspect(b,depth+1)
            rows.append(row)
    return rows
def main():
    ref=ROOT/'reference'; data=(ref/'source-recovery.zip').read_bytes(); manifest=json.loads((ref/'SOURCE_RECOVERY_MANIFEST.json').read_text())
    rows=inspect(data)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        expected={f['path']:f for f in manifest['files']}
        assert len(expected)==6 and set(z.namelist())==set(expected)|{'README.md','MANIFEST.json'}
        assert z.read('README.md')==(ref/'README.md').read_bytes()
        assert json.loads(z.read('MANIFEST.json'))==manifest
        for name,f in expected.items():
            b=z.read(name)
            assert len(b)==f['bytes'] and sha(b)==f['sha256'], name
        # All verification completes before any extracted source is written.
        for name in z.namelist():
            target=ref/'recovered'/name; b=z.read(name)
            assert not target.is_symlink()
            if target.exists(): assert target.read_bytes()==b, 'preserve modified source: '+name
        for name in z.namelist():
            target=ref/'recovered'/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(z.read(name))
    report=dict(schema_version=1,clauses=['HD-004','HD-009','HD-048','HD-085'],constitution_revision='1.1',constitution_sha256=sha((ROOT/'HOMELESS_DARK_CONSTITUTIONAL_COMMISSION.md').read_bytes()),archive_sha256=sha(data),manifest_sha256=sha((ref/'SOURCE_RECOVERY_MANIFEST.json').read_bytes()),status='PASS',historical_sources_verified=6,metadata_entries_verified=2,members=rows,scripts_executed=False,native_acceptance=False)
    (ROOT/'delivery/source-recovery-inventory.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('PASS: six sources, two metadata entries, recursive safety/integrity inspection; no archive scripts executed')
if __name__=='__main__': main()
