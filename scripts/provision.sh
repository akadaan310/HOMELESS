#!/bin/sh
# Isolated Debian toolchain; no root and no changes to existing services.
set -eu
cd "$(dirname "$0")/.."
python3 -m pip install -r requirements.txt
python3 scripts/fetch_sources.py
mkdir -p .cache/apt/lists/partial .cache/apt/archives/partial .cache/sysroot .cache/bin
root=$(pwd)
apt-get -o Dir::Etc::parts=- -o "Dir::State::lists=$root/.cache/apt/lists" -o "Dir::Cache::archives=$root/.cache/apt/archives" update
apt-get -o Dir::Etc::parts=- -o "Dir::State::lists=$root/.cache/apt/lists" -o "Dir::Cache::archives=$root/.cache/apt/archives" --download-only -o Debug::NoLocking=1 -y --no-install-recommends install busybox-static octave espeak-ng openjdk-21-jdk-headless
for p in .cache/apt/archives/*.deb; do dpkg-deb -x "$p" .cache/sysroot; done
if [ -d /usr/lib/jvm/java-21-openjdk-amd64 ]; then cp -an /usr/lib/jvm/java-21-openjdk-amd64/. .cache/sysroot/usr/lib/jvm/java-21-openjdk-amd64/; fi
cat > .cache/bin/octave <<EOF
#!/bin/sh
export LD_LIBRARY_PATH="$root/.cache/sysroot/usr/lib:$root/.cache/sysroot/usr/lib/x86_64-linux-gnu:$root/.cache/sysroot/usr/lib/x86_64-linux-gnu/octave/9.4.0"
export OCTAVE_HOME="$root/.cache/sysroot/usr"
exec "$root/.cache/sysroot/usr/bin/octave-cli" "\$@"
EOF
chmod +x .cache/bin/octave
sh scripts/build_runtime.sh
