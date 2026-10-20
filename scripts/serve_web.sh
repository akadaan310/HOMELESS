#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${PORT:-8080}"
if [[ "${STATIC_ONLY:-0}" == 1 ]]; then
 exec python -m http.server "$PORT" --bind "${HOST:-127.0.0.1}" --directory web/dist
fi
exec python -m worldloom.server --host "${HOST:-127.0.0.1}" --port "$PORT"
