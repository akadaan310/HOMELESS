#!/usr/bin/env python3
"""Download Android command line tools + pinned Gradle locally, preserving proxy/TLS trust."""
import hashlib,json,os,shutil,subprocess,urllib.request,urllib.parse,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'.cache/android-tools'
URLS={'cmdline.zip':'https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip','gradle.zip':'https://services.gradle.org/distributions/gradle-8.10.2-bin.zip'}
def main():
 CACHE.mkdir(parents=True,exist_ok=True);manifest=[]
 for name,url in URLS.items():
  dest=CACHE/name
  if not dest.exists():
   with urllib.request.urlopen(url,timeout=90) as r,dest.open('wb') as f:shutil.copyfileobj(r,f)
  manifest.append({'name':name,'source':url,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 if not (CACHE/'sdk/cmdline-tools/latest/bin/sdkmanager').exists():
  with zipfile.ZipFile(CACHE/'cmdline.zip') as z:z.extractall(CACHE/'sdk-unpack')
  (CACHE/'sdk/cmdline-tools').mkdir(parents=True,exist_ok=True);shutil.move(CACHE/'sdk-unpack/cmdline-tools',CACHE/'sdk/cmdline-tools/latest')
  for p in (CACHE/'sdk/cmdline-tools/latest/bin').iterdir():p.chmod(0o755)
 if not (CACHE/'gradle-8.10.2/bin/gradle').exists():
  with zipfile.ZipFile(CACHE/'gradle.zip') as z:z.extractall(CACHE)
  (CACHE/'gradle-8.10.2/bin/gradle').chmod(0o755)
 env=os.environ.copy();fallback=ROOT/'.cache/sysroot/usr/lib/jvm/java-21-openjdk-amd64'
 if 'JAVA_HOME' not in env and fallback.exists():env['JAVA_HOME']=str(fallback)
 if not env.get('JAVA_HOME') and not shutil.which('javac'):raise SystemExit('Install JDK21 or set JAVA_HOME to a full JDK before provisioning.')
 proxy=urllib.parse.urlparse(env.get('HTTPS_PROXY',''));opts=[]
 if proxy.hostname:
  for scheme in ['http','https']:opts += [f'-D{scheme}.proxyHost={proxy.hostname}',f'-D{scheme}.proxyPort={proxy.port or 80}']
 env['JAVA_OPTS']=' '.join(opts)
 sdk=str(CACHE/'sdk/cmdline-tools/latest/bin/sdkmanager');args=[sdk,'--sdk_root='+str(CACHE/'sdk')]
 (ROOT/'evidence').mkdir(exist_ok=True)
 with (ROOT/'evidence/android_provision.log').open('w') as log:
  subprocess.run(args+['--licenses'],input='y\n'*200,env=env,stdout=log,stderr=log,text=True,check=True)
  subprocess.run(args+['platform-tools','platforms;android-35','build-tools;35.0.0'],env=env,stdout=log,stderr=log,check=True)
 (ROOT/'evidence/android_toolchain_downloads.json').write_text(json.dumps(manifest,indent=2));print('Android SDK35 and Gradle8.10.2 are installed in .cache/android-tools.')
if __name__=='__main__':main()
