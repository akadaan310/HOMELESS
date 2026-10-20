#!/usr/bin/env python3
"""Content hashes of actual deliverables and their accompanying source snapshot."""
import datetime,hashlib,json,pathlib,platform,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 suffixes={'.py','.mjs','.js','.cpp','.h','.hpp','.kt','.gradle','.xml','.toml','.m','.sh','.ush','.uproject','.cs','.css','.html','.json','.properties','.png','.svg','.webmanifest'}
 files=[]
 for name in ['worldloom','native','runtime','math','web/src','android/app/src/main/java','android/app/src/main/res','unreal/Homeless/Source','unreal/Homeless/Config','unreal/Homeless/Shaders','scripts','tools','data/geo','data/world','data/assets']:
  for p in (ROOT/name).rglob('*'):
   if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts:files.append(p)
 for name in ['web/index.html','web/style.css','web/icon.svg','web/manifest.webmanifest','web/package.json','web/package-lock.json','web/capacitor.config.json','android/app/src/main/AndroidManifest.xml','android/app/build.gradle','android/app/capacitor.build.gradle','android/build.gradle','android/variables.gradle','android/gradle.properties','android/settings.gradle','android/capacitor.settings.gradle','android/gradle/wrapper/gradle-wrapper.properties','unreal/Homeless/Homeless.uproject','assets/runtime/manifest.json','requirements.txt','requirements-dev.txt','requirements-voice.txt']:
  if (ROOT/name).is_file():files.append(ROOT/name)
 source=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(set(files))]
 tree_hash=hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest();artifacts=[]
 for name in ['artifacts/android','artifacts/native','artifacts/runtime','artifacts/audio','artifacts/voice','artifacts/web','artifacts/releases','assets/runtime']:
  for p in (ROOT/name).rglob('*'):
   if p.is_file():artifacts.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)})
 r={'schema':'homeless.deliverables.v1','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_tree_sha256':tree_hash,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'environment':platform.platform(),'source_files':source,'artifacts':artifacts,'unreal_cooked':False,'oracle_connected':False,'android_install_verified':False,'notes':['Git commit may precede final verification, packaging and report commits; the source tree hash pins the listed accompanying files.','Executable bytes, APK/web equality and human/device/render quality have separate checks.']}
 p=ROOT/'artifacts/BUILD_MANIFEST.json';p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'source_tree_sha256':tree_hash,'files':len(artifacts),'artifact_bytes':sum(x['bytes'] for x in artifacts)}))
if __name__=='__main__':main()
