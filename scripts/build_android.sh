#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
export JAVA_HOME="${JAVA_HOME:-$ROOT/.cache/sysroot/usr/lib/jvm/java-21-openjdk-amd64}"
export ANDROID_HOME="${ANDROID_HOME:-$ROOT/.cache/android-tools/sdk}"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"
GRADLE="${GRADLE:-$ROOT/.cache/android-tools/gradle-8.10.2/bin/gradle}"
node tools/web_build.mjs
python - <<'PY'
import shutil
from pathlib import Path
p=Path('android/app/src/main/assets/public')
if p.exists():shutil.rmtree(p)
shutil.copytree('web/dist',p)
PY
printf 'sdk.dir=%s\n' "$ANDROID_HOME" > android/local.properties
mkdir -p artifacts/android evidence
readarray -t GRADLE_PROXY_ARGS < <(python - <<'PYPROXY'
import os,urllib.parse
p=urllib.parse.urlparse(os.environ.get('HTTPS_PROXY',''))
if p.hostname:
 for scheme in ['http','https']:
  print(f'-D{scheme}.proxyHost={p.hostname}')
  print(f'-D{scheme}.proxyPort={p.port or 80}')
PYPROXY
)
"$GRADLE" "${GRADLE_PROXY_ARGS[@]}" -p android --no-daemon --console=plain assembleDebug
cp android/app/build/outputs/apk/debug/app-debug.apk artifacts/android/HOMELESS-Rendezvous-debug.apk
sha256sum artifacts/android/HOMELESS-Rendezvous-debug.apk > artifacts/android/SHA256SUMS
"$ANDROID_HOME/build-tools/35.0.0/aapt" dump badging artifacts/android/HOMELESS-Rendezvous-debug.apk > evidence/android_aapt.txt
"$ANDROID_HOME/build-tools/35.0.0/apksigner" verify --verbose --print-certs artifacts/android/HOMELESS-Rendezvous-debug.apk > evidence/android_signature.txt
python - <<'PY'
import hashlib,json,os
from pathlib import Path
p=Path('artifacts/android/HOMELESS-Rendezvous-debug.apk')
Path('artifacts/android/build-manifest.json').write_text(json.dumps({'package':'world.homeless.rendezvous','version':'1.0','minSDK':23,'targetSDK':35,'compileSDK':35,'signing':'Android debug certificate; development build','bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'renderer':'PlayCanvas 2.23.3 / WebGL2','physics':'Rapier WASM 0.19.3','wrapper':'Capacitor 7.4.3 / Kotlin native lifecycle','device_verification':'BLOCKED: no attached Android device'},indent=2))
PY
