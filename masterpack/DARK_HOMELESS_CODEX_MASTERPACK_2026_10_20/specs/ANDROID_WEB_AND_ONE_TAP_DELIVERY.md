# ONE-TAP MOBILE / BROWSER / PC DELIVERY

## Experience mandate

User has a Samsung Galaxy A60 as the stated receiving Android device; test an additional resource-constrained Galaxy A16-equivalent profile. Deliver an installable `.apk` when Android signing/build tools exist. The first tap opens a branded, high-quality HOMELESS entry and an interactive join flow; never show a blank WebView, source build instructions, a default 'hello world' project or an unresolved IP placeholder.

**Full-fidelity architecture:** Unreal Engine 5.8 game/render host with Pixel Streaming 2/WebRTC; Kotlin Android companion uses full-screen immersive media player (WebView with WebRTC capable frontend or a native WebRTC track client) and touch/gyro/gamepad controls, polished startup transitions and ACSP restore. Browser HTML/JS frontend uses the same streaming session and accessible controls. Desktop UE build can render natively from the same server world state.

**Preflight logic:** on Android app startup detect connectivity, validate configured world endpoint, negotiate stream and capabilities, show immediate local lightweight animated scene/status if stream takes time, provide rejoin/retry; no fake claim gameplay happened before connection. **When no GPU host is reachable, ship an offline playable fallback**: high-quality locally bundled cinematic 2.5D/limited 3D origin entry with walk/look, authored sound and state, explicitly labelled offline mode; do not force an empty blank screen. Save offline local journey and reconcile when actual world connection appears.

**World server:** UE5 Pixel Streaming 2 host, matching UE branch of `PixelStreamingInfrastructure`; signaling, SFU when several spectators/members join, session allocator, content cache/CDN as needed, authoritative world daemon, local ACSP socket IPC, telemetry and resume service. WebRTC carries encoded audio/video and interactions; SEURL/PURL semantics remain in their own typed bus. Multi-user permissions and scalable session allocation must be tested; no assumption one server GPU runs thousands of independent full-AAA camera views.

**Android deliverables:** `app-release-or-debug.apk` with actual bytes and SHA256; Gradle/Kotlin project, package/application ID, build manifest, minSDK/targetSDK, valid startup icon/splash/assets, device orientation/input profiles, audios focus and reconnect, install steps and `adb install` smoke-test script; if no connected device, report emulator/device-verification gap. Avoid unrequested app-store publishing.

**Web deliverables:** deployment-ready static frontend, configurable world-service endpoints, accessible touch/keyboard/gamepad, mobile layout, first-run cutscene, sound unlock behavior after gesture in browsers, captions, reduced motion option, reconnect/replay. Provide dev server and production build output.

**Unreal deliverables:** `.uproject`, cookable/cooked Windows/Linux targets as supported, Pixel Streaming 2 config, packaged server executable where environment allows, launch service compose files/config, assets database, benchmark scene, world-origin camera tracking, audio stream and input handler.

## Streaming acceptance profiles (initial hypothesis targets)

- Network normal: 1080p60 intended GPU host render where achieved; fallback 720p30 when device/network performance dictates. Report actual resolution, FPS, late frames, codec, bitrate, render/capture/encode latency, WebRTC RTT/packet loss, input-to-present p50/p95, audio-video skew and reconnect p95.
- Android touch response: well-calibrated camera yaw/pitch, on-screen analog movement, basic gestures and optional gyro; vehicle input separately tuned. No unstabilized camera motion or packet-jitter camera jerks.
- Resume: kill app during stroll, restart and return to latest durable state and same player account. Offline mode cannot silently overwrite newer server events; explicit conflict resolution.
- Sound: real synchronized spatial world audio through stream, headphone profile and phone speaker profile; mute/accessibility and autoplay restrictions handled gracefully.
- World coverage: remote teleport between Tampa and Marina del Rey, plus at least one other continent when real data adapter available; show fallback quality flags; no client-side global 3D preload.
- First join: opening recognition effect must play *in the actual running game*, not a fixed video in a wrapper (offline mode may use pre-captured scene with distinct presentation).

## Proof of deliverable

Required machine results: APK file hash and `aapt` package metadata, successful `adb install` or honest absence of connected device, Android log no crash on first launch, screen lifecycle and WebRTC connection diagnostics; accessible web URL if actually deployed, else build path, local run script and confirmed endpoint tests. PRD accepts no fabricated public URL.
