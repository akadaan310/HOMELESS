#!/usr/bin/env python3
"""Package the already-built static client; read short-lived credential via stdin.

The installed cloud skill's source helper is not present in this executor.
This fallback preserves its invariants: exact pushed source, matching immutable
archive, credentials only in stdin/process memory, and native Sites publication.
"""
import argparse,base64,hashlib,json,os,pathlib,shutil,subprocess,sys,tarfile,termios

def main():
 p=argparse.ArgumentParser();p.add_argument('--checkout',required=True);p.add_argument('--build',required=True);p.add_argument('--root-commit',required=True);p.add_argument('--archive',required=True);a=p.parse_args()
 if sys.stdin.isatty():
  attributes=termios.tcgetattr(sys.stdin.fileno());attributes[3]&=~termios.ECHO;termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,attributes)
 print('Ready for Site credential JSON on stdin (input is hidden).',flush=True)
 credential=json.loads(sys.stdin.readline());checkout=pathlib.Path(a.checkout);build=pathlib.Path(a.build)
 manifest=json.loads((checkout/'.openai/hosting.json').read_text());assert (build/'index.html').is_file()
 for f in build.rglob('*'):
  if f.is_file() and f.stat().st_size>25*1024*1024:raise ValueError('static file exceeds25MiB: '+str(f.relative_to(build)))
 shutil.rmtree(checkout/'dist',ignore_errors=True);shutil.copytree(build,checkout/'dist')
 (checkout/'SOURCE.json').write_text(json.dumps({'repository':'https://github.com/akadaan310/HOMELESS','commit':a.root_commit,'web_build':json.loads((build/'build-manifest.json').read_text())['revision'],'mode':'static cached replay; configure an actual HTTPS world gateway for live authority'},indent=2))
 env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0'
 if credential.get('token'):
  env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.extraHeader',GIT_CONFIG_VALUE_0='Authorization: Bearer '+credential['token'])
 def run(args):
  r=subprocess.run(args,cwd=checkout,env=env,capture_output=True,text=True)
  if r.returncode:raise RuntimeError(r.stderr[-3000:])
  return r.stdout.strip()
 if not (checkout/'.git').exists():
  run(['git','init','-b',credential.get('branch','main')]);run(['git','remote','add','origin',credential['remote_url']]);run(['git','config','user.name','Codex']);run(['git','config','user.email','codex@openai.com'])
 run(['git','add','.']);diff=run(['git','status','--porcelain'])
 if diff:run(['git','commit','-m','Publish verified HOMELESS Rendezvous browser build'])
 commit=run(['git','rev-parse','HEAD']);run(['git','push','-u','origin',credential.get('branch','main')])
 archive=pathlib.Path(a.archive);archive.parent.mkdir(parents=True,exist_ok=True)
 with tarfile.open(archive,'w:gz') as tar:
  tar.add(checkout/'.openai/hosting.json',arcname='.openai/hosting.json');tar.add(checkout/'dist',arcname='dist')
 print(json.dumps({'project_id':manifest['project_id'],'commit_sha':commit,'archive':str(archive),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}),flush=True)
if __name__=='__main__':main()
