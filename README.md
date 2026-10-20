# HOMELESS / Dark — World of Worlds

Founder and founding player: **Abed Kadan (Dark)**. Marina del Rey is his origin; the first world entry is the sourced North Dale Mabry × West Spruce intersection in Tampa.

This is a runnable engineering build of the independent **World Loom** engine, the **Rendezvous PlayCanvas** browser/Android adapter, and an Unreal 5.8 integration project. **Full Unreal rendering and final cinematic/device acceptance are not complete.** The exact results and remaining failures are recorded in [the acceptance report](evidence/acceptance.md).

Owner-private browser preview: **https://homeless-rendezvous-dark.daintyaspen11.chatgpt.site**. This is cached origin play; a separately configured HTTPS world service is required for new authoritative events and microphone transcription. Local connected play is described below. The [draft integration PR](https://github.com/akadaan310/HOMELESS/pull/1) retains the full implementation and evidence.

## Run the connected world locally

On Debian 13 / Linux with Python 3.11+, Node 22+, g++ and bubblewrap:

```sh
git clone -b codex/one-shot-implementation https://github.com/akadaan310/HOMELESS.git
cd HOMELESS
sh scripts/provision.sh
npm --prefix web ci
python3 tools/export_origin.py
npm --prefix web run build
sh scripts/run.sh
```

Open **http://127.0.0.1:8080**. Enter, walk with WASD/arrows or touch, listen to nearby independent conversations, inspect the world-record billboard, and speak/type a bounded request to an NPC. Try `hello`, `teach me`, `show the report`, or `no thanks`. Missions are optional. The local service commits accepted events and restores them after restart; the browser retains its authenticated player session. Offline replay is labelled and cannot overwrite newer server history.

The shipped speech clips work without installing speech models. Optional microphone transcription and voice regeneration use [requirements-voice.txt](requirements-voice.txt), [the voice build tools](docs/VOICE.md), and pinned model downloads; baseline language generation remains symbolic. Mic capture is push-to-talk and transcripts require review before sending.

A local founder/operator capability is created at `.runtime/worldloom.operator-token` for explicit authenticated operator requests through the engine API. It is not included in any build or repository. The browser creates a guest player account; founder account federation remains a deployment requirement. This is local operator authentication, not independent real-world identity verification. For an HTTPS gateway intentionally used by the APK, explicitly configure `--allowed-origin https://localhost`; default writes allow only the same origin.

## Artifacts and checks

Downloads: [Rendezvous engineering prerelease](https://github.com/akadaan310/HOMELESS/releases/tag/rendezvous-engineering-2026-10-20). Its links point to the committed build files; GitHub release attachments are unavailable under this session's upload credentials.

- Android development package: [HOMELESS-Rendezvous-debug.apk](artifacts/android/HOMELESS-Rendezvous-debug.apk), with [checksums](artifacts/android/SHA256SUMS), package metadata, signature verification and device-test status in `evidence/android_*`.
- Browser build: generated in `web/dist/` and `artifacts/web/`; `npm --prefix web run build` reproduces it. Cached origin projections are separate from the connected authoritative world.
- Downloadable browser/native archives and their checksums: [artifacts/releases](artifacts/releases). GitHub's separate release-upload endpoint returned HTTP401; these build bytes are committed in the repository.
- Native executable/library: `artifacts/native/`; actual isolated shell client, JavaScript and Wasm fixtures: `artifacts/runtime/`.
- Synthesized speech and seven sound classes: `artifacts/voice/` and `artifacts/audio/`, with source/model hashes and measured timing.
- Unreal project: [Homeless.uproject](unreal/Homeless/Homeless.uproject), build/import/preflight scripts, source art registry, native IPC adapter and official UE5.8 Pixel Streaming infrastructure integration. See [Unreal status](docs/UNREAL.md).

```sh
python3 -m pip install -r requirements-dev.txt
sh scripts/test.sh
python3 tools/integration_smoke.py
python3 tools/build_acceptance.py
```

The real daemon smoke test exercises CBOR/Unix IPC, typed channels, media preparation without activation, a spoken event, forced restart, identical replay, and duplicate retry. Numerical witnesses compare native C++ with actual Octave. Browser telemetry is a software-renderer measurement, not a Samsung or GPU-host result. See [grammar/world](docs/GRAMMAR_WORLD.md), [geography/sky](docs/GEO_SKY.md), [numerics](docs/NUMERICAL_RESEARCH.md), [speech](docs/VOICE.md), and [protocols](docs/PROTOCOL.md).

Final checks: **98 Python tests and 12 Node tests passed**. Actual Chromium walking/reload/account/audio checks passed, with the final minor input/telemetry delta recorded in `evidence/web_checks.json`. All 90 APK web files match the final browser build byte for byte. Full commission acceptance is **FAIL**, with 19 failed and 80 blocked checks. The latest software-renderer p95 was 8,242.7 ms under concurrent cloud workload. Targets for 30 FPS on named devices, full visual coverage, Arabic ASR, actual Unreal rendering and Oracle execution remain unmet or unverified.

## Preserved commission and source art

Original release: [masterpack-v1](https://github.com/akadaan310/HOMELESS/releases/tag/masterpack-v1).

`DARK_HOMELESS_CODEX_ONE_SHOT_MASTERPACK_2026_10_20.zip` is **95,551,079 bytes**, SHA-256 **263e7c172e2a9ec9fabb6e916dd6fef03226fa3e21cb78c59c2fe42a0b98db95**. The release is unchanged. Its original text documents and all Rendezvous rider archives/documents are retained unchanged here; `scripts/fetch_sources.py` verifies and restores the original ZIP and historical source archives. Nothing in an older source overrides the newer commission.

`assets/catalog.json` tracks individual source files, hashes, licenses, conversion metrics, separate runtime derivatives and honest acquisition states. Large original art and neural weights are reproducibly retrieved by the recorded tools; local immutable masters remain in `assets/originals/` and are excluded from ordinary Git to avoid multi-gigabyte duplication. Source factual geometry, authored fictional façades/names, approximation masks and generated effects remain distinct. An acquired or converted asset is not called scene-integrated before an actual render test.
