"""Validate the derived requirement projection against the actual commission."""
import hashlib,json,re
from pathlib import Path

def validate(root):
    text=(root/'HOMELESS_DARK_CONSTITUTIONAL_COMMISSION.md').read_text()
    raw=(root/'HOMELESS_DARK_CONSTITUTIONAL_COMMISSION.md').read_bytes()
    ledger=json.loads((root/'governance/requirements.json').read_text())
    if ledger['constitution_sha256']!=hashlib.sha256(raw).hexdigest():
        raise ValueError('constitution digest drift')
    titles={f'HD-{int(i):03}':title for i,title in re.findall(r'^## (\d+)\. (.+)$',text,re.M)}
    rows=ledger['requirements']
    if len(rows)!=len(titles) or {r['id'] for r in rows}!=set(titles):
        raise ValueError('missing/duplicate/unknown clauses')
    for row in rows:
        if row['requirement']!=titles[row['id']]:raise ValueError('requirement title drift')
        if row['status'] not in {'PASS','FAIL','BLOCKED','NOT_RUN','NOT_APPLICABLE'}:raise ValueError('invalid status')
        if not row['owner'] or not row['verification']:raise ValueError('unowned/unverifiable requirement')
        if row['status']=='PASS' and (not row['evidence'] or not row['command']):raise ValueError('unsupported pass')
        for path in row['evidence']:
            if not (root/path).is_file():raise ValueError('missing evidence '+path)
    return {'status':'PASS','clauses':len(rows),'constitution_sha256':ledger['constitution_sha256'],'scope':'projection integrity only; not implementation acceptance'}
if __name__=='__main__':
    print(json.dumps(validate(Path(__file__).resolve().parents[1]),indent=2))
