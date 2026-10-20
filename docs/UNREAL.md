HOMELESS has a real Unreal 5.8 source project at `unreal/Homeless/Homeless.uproject`. Its engine SDK, map import, C++ module build, cook, GPU rendering, Pixel Streaming video and actual device performance remain unverified. `tools/unreal_preflight.py` reports distinct machine-readable blockers and exits2 while blocked; it never substitutes a different engine.

The source includes a game/editor target, `Homeless` module, a game-instance adapter with typed projections and asynchronous host-local IPC, eleven camera profiles with swept collision recovery and a skippable arrival transition, bounded wetness/weather and Niagara parameter controllers, MetaSound parameter binding, Lumen/Nanite/TSR/VSM configuration, a sourced-asphalt wet material editor graph and an HLSL wet-surface function. Source assets are imported by editor Python. Material buffer response, occlusion, animation contact and cinematic quality still require the real editor/GPU test. The generated map is an **incomplete source-art QA fixture**, not a finished Tampa replica or production hero scene. Missing art remains a visual-content failure.

Build and launch on a licensed Linux GPU host:

```sh
export UE_ROOT=/path/to/UnrealEngine-5.8
python tools/unreal_preflight.py
scripts/build_unreal.sh
python -m worldloom.cli daemon --socket .runtime/worldloom.sock
python tools/unreal_gateway.py --engine-socket "$PWD/.runtime/worldloom.sock"
tools/unreal_pixelstreaming.sh provision
tools/unreal_pixelstreaming.sh start
PIXEL_STREAMING_URL=ws://127.0.0.1:8888 scripts/launch_unreal.sh
```

`build_unreal.sh` checks the exact5.8 major/minor, builds the editor module, executes actual import, converts the fixture with `WorldPartitionConvertCommandlet`, then invokes `BuildCookRun`. It stops on missing SDK or failed import. No fake `.umap` or `.uasset` files are supplied. City Sample, its traffic/crowds, MetaHuman and other Fab-entitled native packs remain acquisition work; identified listing URLs are never treated as downloaded content.

The Pixel Streaming lane uses **Epic's actual UE5.8 infrastructure**, pinned to commit `4c1fd4830cde8c6dd441b9c72ec8864b2f7f29bd` in `unreal/pixelstreaming/infrastructure.lock.json`. Its official signalling server and official TypeScript player were built and HTTP-served in this environment. `evidence/unreal_pixelstreaming.json` separates that successful infrastructure check from missing streamer/video/GPU/TURN/public-host gates. The provisioning script clones the pinned branch, installs locked npm dependencies and builds official packages; it does not implement a substitute signalling protocol. The official player is copied to `artifacts/assets/pixel-streaming-www` after build. Launch flags match the tested UE5.8 server. Public service requires a reachable GPU renderer, TLS/reverse proxy and TURN as needed by the target network.

Local adapter contract:

- Unix socket `/tmp/worldloom-unreal.sock`, mode0600.
- Four-byte big-endian frame length followed by UTF-8 JSON, maximum1MiB. One request/response per connection, timeout2s for the shared C++ client.
- `{"protocol":"worldloom.unreal.v1","operation":"projection","request_id":"...","session_id":"..."}` resolves `purl://dark/world/state` through the real canonical-CBOR daemon. Complete authoritative data and original trace digest remain unchanged; presentation metadata occupies a separate field.
- `operation:"invoke"` carries a complete typed daemon envelope in `payload`. The gateway creates no capabilities or founder authority; authorization occurs in WorldSession. Unknown operations are refused or unsupported.
- Transport runs on an Unreal worker thread, then dispatches results to the game thread. An in-flight request is bounded and shutdown uses weak object references.

`WorldLoomFrameClient.h` is shared by the Unreal module and a standalone native C++20 probe. `python tools/unreal_interop_test.py` compiles the actual shared header and proves native JSON→gateway→canonical-CBOR WorldSession query, trace witness, unauthorized-write refusal and malformed-protocol refusal. This is an interoperability test, **not an Unreal module build**. Evidence is in `evidence/unreal_native_interop.json`.

The shared art registry is `assets/catalog.json`, with runtime variants in `assets/runtime/manifest.json`, actual surface/HDR maps in `assets/runtime/surfaces.json`, immutable source byte references in `assets/originals/sha256`, and machine-readable QA under `evidence/assets_*`. Rebuild acquisition with `python tools/assets.py acquire`; selected Rocketbox civilians use `tools/assets_rocketbox_fetch.py`, Blender `tools/assets_rocketbox_convert.py`, and `tools/assets_register_rocketbox.py`. Original source bytes remain intact. The assembled Tampa frontage arranges actual CC0 architecture modules and is explicitly fictional. Sponza is a separately labelled, local architecture/material lookdev reference with a regional-style mismatch. Its actual source license is the Cryengine limited agreement, so its derivative is withheld in assets/quarantine rather than shipped in the public runtime; it is never evidence of Tampa authenticity. Native UE assets and portable glTF derivatives share canonical world asset IDs, never renderer-specific universal identities.

Shipped runtime derivatives can run without archival masters. `python tools/assets_restore.py` restores exact source bytes from tracked URLs and SHA256 records; changed publisher bytes are refused. `scripts/provision_assets.sh` reproduces acquisition/conversion/portable tiers when Blender, npm and the documented Python dependencies are installed. Source-only tests explicitly skip if masters are absent, while delivered runtime fingerprints and per-file25MiB ceilings are always checked. This environment actually ran source-hash checks with masters present. `evidence/assets_coverage.json` records each missing category and visual-content FAIL separately from hardware blockers.
