# Release acceptance / measurable engineering gates

All objectives require a **measured test result**, hardware/browser/version, date, trace or build artifact, exact pass/fail. Reference targets are budgets to verify, not claimed achievements. A criterion may be blocked; never mark blocked as passed.

## 1. Actual delivered artifacts

| Deliverable | Evidence / acceptance |
|---|---|
| Web build | Production assets load over HTTPS, controls respond, after intro there is actual free 3D movement, audio, NPCs and persistent world state |
| Android | `.apk` built through Gradle/Capacitor with real bytes; app package inspection, checksum, install/run log on a supported device/emulator |
| Fullscreen | Web first-entry gesture requests fullscreen; no scrollbars or page overscroll; Android immersive mode with recoverable system bars |
| Shared state | Given same player/session, browser and APK load the same authenticated world state and see same committed events |
| Real physics | Character stops at collisions; moving objects have impulses and fixed timestep; replay divergence measured with state checksums |
| NPCs | At least one non-player character has independent routine, decision trace, contextual interaction and restart persistence; population-scale virtualization test |
| Onboarding | World active before entry, camera smoothly joins Dark, nearby vehicles/pedestrians/audio respond gracefully, user can skip/re-enter |
| Geometry | Tampa entrance is geospatially anchored; nearby geometry/asset source transparently identified; real source tiles distinguished from adapted recipes |
| Audio | After gesture: stereo ambient, positional events, footsteps, NPC effects and traffic; no pop/glitch in streaming transitions |
| Continuity | PURL/SEURL/ACSP integration for a real gameplay event and local authorized runtime operation; reconnect/replay after killing app process |
| Unreal preserved | All original UE interfaces, configs and scope remain; Unreal rendering/cooking acceptance remains BLOCKED until actually run |

## 2. Baseline hardware profiles

- **Low**: Samsung Galaxy A16-equivalent Android WebView/Chrome, if physically accessible; evaluate the A60-class founder device separately. Low profile: adaptive **stable 30 FPS target**, p95 frame time ≤ 40 ms in steady-state walk, no unbounded multi-second freezes after load, CPU/GPU memory resident assets bounded by telemetry. No invented promise of 60fps at maximum quality on low-end hardware.
- **Mid**: 30 FPS or higher with sharper materials, denser animated NPC crowds, reflection effects.
- **High / cloud**: high-fidelity desktop/browser WebGPU or Unreal Pixel Streaming; target 60 FPS where tests support it.
- Record cold start / first interactive frame / near-cell transition time, 1% low FPS, p50/p95 frame, GPU/CPU memory if available, draw calls, triangles, streamed bytes/minute, number of visibly animated NPCs, simulation steps and audio glitches. Target cold start ≤ 15s on stable connection where measured, else report. Under low power/device background/reconnect conditions measure explicitly.

## 3. Quality instrumentation

`requestAnimationFrame` latency tracing, GPU timestamp timers where available, rendering pipeline stats, physics-step histograms, origin-world frame-to-viewport time, dropped scene frames, game-controller response. No screenshot-only quality claims; use objective metrics AND rendered image inspection where hardware allows (both matter).

Physics conformance: zero collision tunneling for agreed speed/shape fixture; max allowed contact penetration; variance under repeated initial-state seeds; conservation/damping within declared integrator tolerance; avoidance of incoherent street vehicle movement; interpolation and teleport camera continuity. Camera mean jerk and p95 angular delta must be recorded.

Asset QA: scene smoke load, GLB inspect, texture correctness, LOD swaps without identity loss, visible crossfade/popping score measured by projection difference, no missing materials/magenta textures, no runtime shader errors. Enforce configurable memory residency ceilings instead of fixed untested budget constants.

Web input: Enter action initiates fullscreen when supported; browser denied fullscreen gracefully retains playable 100dvh canvas. Browser audio resumes after focus; status/navigation bars accessible via OS gesture in APK. Touch joystick sensitivity and camera limits verified in portrait/landscape supported orientation.

## 4. One-run human acceptance story

- User taps APK or visits URL.
- World's preexisting audiovisual scene appears.
- One clear Enter action leads into full-screen play; no browser page scrolling or blank WebView.
- Camera reveals Dark's arrival at Tampa (Dale Mabry / West Spruce).
- NPCs already moving, vehicular flow, ambient airport sound and dynamic lighting; reactions natural and selective.
- Player freely walks, investigates a fictional storefront, speaks to one NPC, sees an independently generated response and causal event, changes one approved world detail or discovers a route pattern.
- Exits then rejoins; same world memory and saved event are there.
- Low-performance renderer automatically reduces costly effects without degrading to raw test geometry or dead-static screenshots.

## 5. Verification workflow in Codex

Automated CI stages: package installation → unit/property/math contracts → world server start → web build → browser headless GPU check when possible → Android Gradle build → APK inspect → instrumented device/emulator run when accessible → session cross-client/reconnect → publish artifacts and reports. Preserve the masterpack and existing UE tests in the verification matrix as separate lanes; do not claim engine rendering was tested by the web lane.

Final report must include live URL if actually deployed; installable APK link if actually built; commit SHA; hash; hardware/software baseline; real integration test trace; remaining blocked requirements. **No false pass for 'fully playable' if all that exists is an intro animation.**
