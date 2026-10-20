#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="${HOMELESS_UNREAL_BINARY:-$TASK_ROOT/artifacts/unreal/Linux/Homeless/Binaries/Linux/Homeless}"
if [[ ! -x "$APP" ]]; then echo 'BLOCKED UE_COOK_MISSING: run scripts/build_unreal.sh with a licensed UE5.8 SDK and GPU host.' >&2; exit 2; fi
SIGNAL_URL="${PIXEL_STREAMING_URL:-ws://127.0.0.1:8888}"
if [[ ! "$SIGNAL_URL" =~ ^wss?:// ]]; then echo 'PIXEL_STREAMING_URL must use ws:// or wss://' >&2; exit 64; fi
exec "$APP" -RenderOffscreen -AudioMixer -Unattended -PixelStreamingURL="$SIGNAL_URL" -PixelStreamingEncoderCodec=H264 -ForceRes -ResX=1920 -ResY=1080 -Log "$@"
