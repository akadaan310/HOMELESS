#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$TASK_ROOT"
# Run only when rebuilding source art; shipped runtime bundles need no masters.
python3 tools/assets.py acquire --resolution 8k --max-texture 1024
python3 tools/assets_rocketbox_fetch.py
blender --background --python tools/assets_rocketbox_convert.py
python3 tools/assets_surfaces.py
python3 tools/assets_assemble_frontage.py
python3 tools/assets_register_rocketbox.py
python3 tools/assets_mobile.py
python3 tools/assets_low_geometry.py
python3 tools/assets_low_textures.py
python3 tools/assets_catalog.py
