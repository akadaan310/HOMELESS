#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$TASK_ROOT/tools/unreal_preflight.py" --allow-blocked >/dev/null
if [[ -z "${UE_ROOT:-}" || ! -f "$UE_ROOT/Engine/Build/Build.version" ]]; then
  echo 'BLOCKED UE_SDK_MISSING: set UE_ROOT to a licensed Unreal Engine 5.8 installation. See evidence/unreal_preflight.json.' >&2
  exit 2
fi
python3 - "$UE_ROOT" <<'PY'
import json,pathlib,sys
v=json.load(open(pathlib.Path(sys.argv[1])/'Engine/Build/Build.version'))
if (v['MajorVersion'],v['MinorVersion'])!=(5,8):raise SystemExit('BLOCKED UE_VERSION_MISMATCH: UE5.8 required')
PY
PROJECT="$TASK_ROOT/unreal/Homeless/Homeless.uproject"
"$UE_ROOT/Engine/Build/BatchFiles/Linux/Build.sh" HomelessEditor Linux Development "$PROJECT" -WaitMutex
"$UE_ROOT/Engine/Binaries/Linux/UnrealEditor-Cmd" "$PROJECT" -unattended -nosplash -ExecutePythonScript="$TASK_ROOT/tools/unreal_import.py" -stdout -FullStdOutLogOutput
[[ -f "$TASK_ROOT/unreal/Homeless/Content/WorldLoom/Maps/TampaEntry.umap" ]] || { echo 'BLOCKED UE_SCENE_NOT_IMPORTED: import did not produce map' >&2; exit 3; }
"$UE_ROOT/Engine/Binaries/Linux/UnrealEditor-Cmd" "$PROJECT" -run=WorldPartitionConvertCommandlet /Game/WorldLoom/Maps/TampaEntry -AllowCommandletRendering -SCCProvider=None -unattended -stdout
"$UE_ROOT/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun -project="$PROJECT" -noP4 -platform=Linux -clientconfig=Development -build -cook -stage -pak -iostore -archive -archivedirectory="$TASK_ROOT/artifacts/unreal"
