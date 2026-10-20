# HOMELESS Rendezvous delivery

This is a PlayCanvas 2.23.3 / Rapier 0.19.3 WASM client and a Capacitor 7.4.3 Android application. It is separate from the Unreal 5.8 render lane. The browser and APK share the same application and bundled origin assets; no video or screenshot substitutes for local gameplay.

## Run and build

Use Node 22+, Python 3.11+, JDK 21, Android SDK 35. Dependencies are pinned by `web/package-lock.json`.

```sh
npm ci --prefix web
node tools/web_build.mjs
./scripts/serve_web.sh
```

Open `http://127.0.0.1:8080`. This runs the persistent world API and serves `web/dist`. `STATIC_ONLY=1 ./scripts/serve_web.sh` serves the offline static build. `artifacts/web` is the production copy. Serve it over HTTPS for installable PWA and microphone capabilities, or use loopback during development.

```sh
python tools/provision_android.py
./scripts/build_android.sh > evidence/android_build.log 2>&1
./scripts/test_android.sh
```

`JAVA_HOME`, `ANDROID_HOME`, and `GRADLE` can select existing installations. This workspace has its full JDK at `.cache/sysroot/usr/lib/jvm/java-21-openjdk-amd64`; downloaded SDK/Gradle stay under `.cache/android-tools`. Download hashes are recorded in `evidence/android_toolchain_downloads.json`. Gradle honors the inherited HTTP proxy through the build script, without storing credentials in the project. Native wrapper regeneration from the web project must retain `android/capacitor.settings.gradle`'s `../web/node_modules` path.

APK: `artifacts/android/HOMELESS-Rendezvous-debug.apk`. Package `world.homeless.rendezvous`, minSDK 23, target/compileSDK 35. It uses an Android debug certificate for development. APK byte count/hash are in `artifacts/android/build-manifest.json` and `SHA256SUMS`; package and certificate inspection are in `evidence/android_aapt.txt` / `android_signature.txt`.

Transfer the APK to Android and open it, allowing installation from the chosen source when Android asks. No app store publication is performed. For an attached authorized device, `scripts/test_android.sh` installs, launches, collects logcat and a screenshot. A missing device produces an explicit blocked result, never a fabricated installation pass.

## Play

Enter with sound enabled by the actual gesture. WASD/arrows move, drag or a gamepad right stick orbits the camera, and the left stick moves. Touch devices show a movement joystick and interaction control. Walk, relaxed local stroll and stationary witness are selectable. The arrival is skippable/replayable; reduced motion and captions are in settings. The journal shows local arrival/walk/interaction records. The fictional storefront accepts governance proposals through the world service; offline proposals remain drafts.

The opening coordinate comes from the acquired OpenStreetMap Tampa graph: latitude 27.95946425, longitude −82.5055696. ENU maps to PlayCanvas `[east, up, -north]`. Road widths, terrain and untagged building heights carry explicit estimation flags. Storefront assembly, narrative signs, characters and effects are fictional presentation. Imported source art includes Poly Haven frontage components, asphalt, street furniture and HDR lighting reference (CC0), Microsoft Rocketbox civilian humans (MIT), and Car Concept by Eric Chadwick / Darmstadt Graphics Group through Khronos (CC BY 4.0). Full attribution and content hashes remain in `assets/runtime/manifest.json` and source catalogs.

## Connected and offline behavior

The status chip distinguishes a reachable authoritative world service, a cached authoritative replay, and a standalone local origin. Cached episodes come from `tools/export_origin.py`'s actual witnessed world snapshots. A cached dialogue preview is labelled and cannot activate a world event. Local position/journal survives reload and Android suspension; the latest 500 events/pending records and 1,000 heard IDs are bounded. Overflow is counted and shown. If browser storage is unavailable, the session reports memory-only persistence.

Local records are sent only through the journal's explicit review-and-send action. Their original IDs provide idempotent retries. They are submitted separately and do not overwrite newer server state. The world account's bearer/session is stored only in runtime local storage, scoped to the configured service base. Changing endpoints does not forward the previous host's credential. The default account is a guest player and does not impersonate Dark / Abed Kadan.

In settings, set an HTTPS world-service URL. Server operators must explicitly allow the client origin, for example `python -m worldloom.server --allowed-origin https://localhost` for the bundled Capacitor origin. Public sites require their exact HTTPS origin in this allowlist. The server remains a separate process; the APK does not embed the Python daemon. Use an HTTPS reverse proxy for a remote phone connection. Cleartext networking is disabled in the Android app.

The optional Pixel Streaming setting uses Epic's real UE 5.8 frontend package `@epicgames-ps/lib-pixelstreamingfrontend-ue5.8` 0.1.3. It negotiates signaling/WebRTC with a supplied WS(S) endpoint, retaining the local renderer during connection attempts and restoring it on disconnection. A live-video label appears only upon the stream playback event. No GPU-host success, codec/bitrate, stream latency or multi-user capacity is claimed without an actual host test.

## Speech, gates and billboards

Browser microphone acquisition is explicit push-to-talk. Capture stops on release, cancellation, native pause and panel close; a release during the permission prompt cannot start a later hidden recording. The configured service receives bounded MediaRecorder bytes and proposes a transcript; the player reviews it before sending a grammatical intent. Typed input remains available. Saving player dialogue transcripts in the local journal is opt-in and off by default. NPC speech uses actual cached Piper audio, exact authorized text matching, HRTF panners, a camera-oriented listener and collision-ray-dependent low-pass/gain occlusion. Missing audio falls back to captions.

Independent NPC conversation records come from the server snapshot, or the separately labelled cached timeline offline. Source audio fetch/decode/play, played act IDs and occlusion changes are instrumented. Heard IDs commit only after playback starts. Prediction sends typed `gate.plan` / `gate.prepare`, fetches selected resource URLs, measures bytes/time, and aborts obsolete requests. Preparation does not itself activate a world event. A connected billboard retrieves the real `billboard.inspect` computation trace and updates the emissive in-scene texture.

## Verification and limits

Run `npm test --prefix web` for bounded persistence, endpoint validation, authenticated resume/idempotency/refusal, fixed-clock bounds an actual Rapier WASM collision fixture, and real PlayCanvas animation-component transitions using source track names. The stress fixture declares an 8 cm maximum contact-penetration tolerance at a 6 m/s attempted speed; it is not a universal physics guarantee.

`python tools/web_smoke.py` runs actual Chromium with software WebGL2 against port 8086. It exercises source-model loading, walking, AudioContext decode/spatial graph, screenshot capture, reload persistence and account continuity; output is `evidence/web_browser.json`. Its software renderer and concurrent cloud CPU load cannot establish Samsung performance. Frame times use independent performance.now() wall intervals; the engine-supplied delta is itself clamped; simulation separately clamps background catch-up. Triangle telemetry is the loaded-mesh inventory, not a hardware post-cull counter. GPU bytes are engine allocation counters, not physical device VRAM telemetry.

No Samsung Galaxy A60/A16, authorized emulator, physical microphone, GPU Unreal host, Oracle ARM node or human headphone/art review is present in this workspace. Android installation/lifecycle/GPU/audio/input/thermal/power measurements, target-device 30 FPS acceptance, photoreal scene completeness, all premium asset categories, Unreal cooking/render parity and Pixel Streaming latency remain independent verification gaps. Source-art and animation smoke evidence does not certify cinematic quality or artist approval.

Near the haven, interaction offers an explicit witnessed-report request; proximity only stages a local notice. A learned mission opportunity can be considered and accepted through the authoritative service, with consent. Neither walking past the haven nor media preparation commits attendance or a mission. Recognition results carry dialog/recording/input versions: canceling, closing the panel, starting a new recording, or typing newer text discards stale results and aborts the outstanding request.
