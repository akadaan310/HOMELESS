#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INFRA_ROOT="${PIXEL_STREAMING_INFRA_ROOT:-$TASK_ROOT/.cache/pixel-streaming-ue5.8}"
COMMIT=4c1fd4830cde8c6dd441b9c72ec8864b2f7f29bd
COMMAND="${1:-provision}"
if [[ "$COMMAND" == provision ]]; then
  if [[ ! -d "$INFRA_ROOT/.git" ]]; then git clone --depth 1 --branch UE5.8 https://github.com/EpicGamesExt/PixelStreamingInfrastructure.git "$INFRA_ROOT"; fi
  if [[ "$(git -C "$INFRA_ROOT" rev-parse HEAD)" != "$COMMIT" ]]; then
    git -C "$INFRA_ROOT" fetch origin "$COMMIT" --depth 1
    git -C "$INFRA_ROOT" checkout --detach "$COMMIT"
  fi
  npm ci --prefix "$INFRA_ROOT" --ignore-scripts
  npm --prefix "$INFRA_ROOT" run build:all:cjs
  mkdir -p "$TASK_ROOT/artifacts/assets/pixel-streaming-www"
  cp -a "$INFRA_ROOT/SignallingWebServer/www/." "$TASK_ROOT/artifacts/assets/pixel-streaming-www/"
  echo "Genuine Epic UE5.8 Pixel Streaming infrastructure built at $INFRA_ROOT; no renderer attached yet."
elif [[ "$COMMAND" == start ]]; then
  [[ -f "$INFRA_ROOT/SignallingWebServer/dist/index.js" ]] || { echo 'BLOCKED PS_INFRA_NOT_BUILT: run tools/unreal_pixelstreaming.sh provision' >&2; exit 2; }
  cd "$INFRA_ROOT/SignallingWebServer"
  exec node dist/index.js --serve --player_port="${PIXEL_STREAMING_HTTP_PORT:-8081}" --streamer_port="${PIXEL_STREAMING_STREAMER_PORT:-8888}" --http_root="$TASK_ROOT/artifacts/assets/pixel-streaming-www" --log_folder="$TASK_ROOT/.runtime/pixel-streaming-logs" --homepage=player.html --log_config=false
else echo 'usage: tools/unreal_pixelstreaming.sh provision|start' >&2; exit 64; fi
