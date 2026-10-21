"""Run the supported local checks; native gates remain explicitly unrun."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
checks=[('cop', [sys.executable,'-m','unittest','discover','-s','governance','-p','test_*.py','-v']),('ledger',[sys.executable,'governance/validate_ledger.py']),('portable',[sys.executable,'-m','unittest','discover','-s','portable/tests','-p','test_*.py','-v'])]
checks.append(('unity_file_integrity',[sys.executable,'Unity/Tools/check_fixture.py']))
results=[]
for name,cmd in checks:
    env=dict(os.environ);env['PYTHONPATH']=str(root/'portable')
    result=subprocess.run(cmd,cwd=root,env=env,capture_output=True,text=True,timeout=120)
    log=root/'evidence'/('verify-'+name+'.log');log.write_text(result.stdout+result.stderr)
    results.append(dict(check=name,command=cmd,exit_code=result.returncode,evidence=str(log.relative_to(root)),sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
summary=dict(schema_version=1,scope='portable integration only',checks=results,native_status='BLOCKED',release_accepted=False)
(root/'evidence/verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
sys.exit(any(r['exit_code']!=0 for r in results))
