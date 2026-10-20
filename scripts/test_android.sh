#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export ANDROID_HOME="${ANDROID_HOME:-$PWD/.cache/android-tools/sdk}"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
mkdir -p evidence
adb devices -l | tee evidence/android_devices.txt
if ! adb devices | awk 'NR>1&&$2=="device"{found=1}END{exit !found}'; then
 printf '{"status":"BLOCKED","reason":"No connected authorized Android device or emulator; APK install/startup/WebView/physical microphone/Samsung A60 and A16 measurements not executed."}\n' > evidence/android_device_test.json
 exit 0
fi
adb install -r artifacts/android/HOMELESS-Rendezvous-debug.apk | tee evidence/android_install.txt
adb logcat -c
adb shell am force-stop world.homeless.rendezvous
adb shell am start -W -n world.homeless.rendezvous/.MainActivity | tee evidence/android_launch.txt
adb logcat -d -t 1000 > evidence/android_logcat.txt
if rg -q 'FATAL EXCEPTION|Fatal signal' evidence/android_logcat.txt; then exit 1; fi
adb exec-out screencap -p > evidence/android_launch.png
printf '{"status":"startup-smoke-passed","scope":"Install, launch, fatal-log scan. Interactive GPU/audio/device performance still requires on-device testing."}\n' > evidence/android_device_test.json
