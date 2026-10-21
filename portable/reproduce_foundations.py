"""Reproduce reviewed research suites without running archive install/directive scripts.

Requires an explicit --run-reviewed flag. Inspect the selected source/test files first.
Use --python /tmp/homeless-reference-venv/bin/python for NumPy/NLTK/SciPy/Shapely suites.
Original archives remain read-only; all extraction/cache writes occur in --work-dir.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parent
JOBS={
 'v3':('HOMELESS_AI_NATIVE_ENGINE_V3_BORNE.zip','HOMELESS_AI_NATIVE_ENGINE_V3/prototype',['node','--test','tests.mjs','plicate.test.mjs','borne.test.mjs']),
 'tashkil':('tashkil-kernel-v0.1.zip','tashkil',['node','--test','test/tashkil.test.mjs']),
 'ingram':('ingram-0.1.zip','ingram-0.1',['PYTHON','-m','unittest','discover','-s','tests','-v']),
 'realms':('homeless-realms-0.1.zip','homeless-realms-0.1',['PYTHON','-m','unittest','discover','-s','tests','-v'])}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-reviewed',action='store_true',required=True)
    parser.add_argument('--source-dir',type=Path,default=Path('/home/ubuntu/homeless/masterpack/extracted/DARK_HOMELESS_CODEX_MASTERPACK_2026_10_20/inputs'))
    parser.add_argument('--work-dir',type=Path,required=True)
    parser.add_argument('--python',default=sys.executable)
    parser.add_argument('--suite',choices=JOBS,required=True)
    args=parser.parse_args()
    if args.work_dir.exists(): parser.error('work directory must be new, preventing reuse of unreviewed caches')
    if not args.work_dir.resolve().is_relative_to(Path('/tmp')): parser.error('work directory must be in /tmp')
    archive,relative,command=JOBS[args.suite]
    expected={Path(x['path']).name:x['sha256'] for x in json.loads((ROOT/'evidence/source-inputs.json').read_text())}
    source=args.source_dir/archive
    if hashlib.sha256(source.read_bytes()).hexdigest()!=expected[archive]: parser.error('archive differs from reviewed hash')
    args.work_dir.mkdir(parents=True)
    with zipfile.ZipFile(source) as z:
        for item in z.infolist():
            target=args.work_dir/item.filename
            if not target.resolve().is_relative_to(args.work_dir.resolve()) or stat.S_ISLNK(item.external_attr>>16): parser.error('unsafe archive path')
            if item.is_dir(): target.mkdir(parents=True,exist_ok=True)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                # Pickles are executable: never deserialize archive-supplied caches.
                if not target.name.endswith('.pkl'): target.write_bytes(z.read(item))
    cwd=args.work_dir/relative
    command=[args.python if x=='PYTHON' else x for x in command]
    env={'PATH':os.environ['PATH'],'LANG':'C.UTF-8','PYTHONPATH':str(cwd)+':'+str(cwd/'ingram')}
    try:
        result=subprocess.run(command,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
        output,code=result.stdout,result.returncode
    except subprocess.TimeoutExpired as error: output,code=error.stdout or b'',124
    output+=b'\nEXIT_STATUS='+str(code).encode()+b'\n'
    (ROOT/'evidence'/(args.suite+'-reproduced.log')).write_bytes(output)
    sys.stdout.buffer.write(output)
    return code

if __name__=='__main__': raise SystemExit(main())
