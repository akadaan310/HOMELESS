"""Hash reviewable source bytes; never represents a Git commit or native build."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=[]
for folder in ('Unity','portable','governance','delivery'):
    for p in sorted((root/folder).rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix in ('.pyc','.log') or 'evidence' in p.parts:continue
        files.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for name in ('README.md','.gitignore','AGENTS.md','HOMELESS_DARK_CONSTITUTIONAL_COMMISSION.md'):
    p=root/name;files.append({'path':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
payload=json.dumps(files,sort_keys=True,separators=(',',':')).encode()
value={'schema_version':1,'kind':'source_snapshot_not_native_build_or_commit','sha256':hashlib.sha256(payload).hexdigest(),'files':files}
(root/'evidence/source-snapshot.json').write_text(json.dumps(value,indent=2)+'\n')
print(value['sha256'])
