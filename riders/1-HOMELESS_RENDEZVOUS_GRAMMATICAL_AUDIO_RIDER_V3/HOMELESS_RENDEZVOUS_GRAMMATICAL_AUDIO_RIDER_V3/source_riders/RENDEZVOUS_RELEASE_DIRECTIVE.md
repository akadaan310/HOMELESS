# MANDATORY RELEASE RIDER — HOMELESS: RENDEZVOUS

## 0. Invariant mission

**Commission identity:** Dark is Abed Kadaan (two consecutive a's in Kadaan). HOMELESS is the real-world-geography-inspired membership/game. Maintain the original unmodified 95,551,079-byte Godpack exactly. This directive **adds a release surface** and does not replace Unreal Engine 5.8, the Unreal acquisition/streaming pipeline, Pixel Streaming 2, source research, or any advanced backend/AI native subsystem.

**Rendezvous Release:** A fully playable, high-quality, immersive, responsive 3D browser build plus an installable Android APK, using the existing deterministic world core, source assets, real-world geodata where present, PURL/SEURL/ACSP, mathematically modeled NPC activity, provenance, continuity, scene/asset data, the Tampa spawn, and the founder onboarding. The underlying engine must be renderer-neutral. Unreal remains the primary AAA rendering destination and must be able to consume the common world state and assets later.

**Release semantics:** Do not call this an Unreal build. Do not create a fake video or UI shell that merely resembles gameplay. Both web and Android must launch an actual interactive, persistent world, with characters, cameras, vehicle activity, audio, and meaningful deterministic decisions. If high-end art or data isn't obtainable in current compute/storage constraints, deliver verified feasible tiers and report the blocked fidelity; never silently substitute grayboxes as final art. The release is not complete if the APK doesn't exist, if the browser only shows a scene screenshot, or if source subsystems aren't integrated.

## 1. Runtime platform decision

**Recommended baseline:** PlayCanvas Engine 2.x, WebGL2 compatibility path required; use WebGPU where feature detection says genuinely supported. Evaluate Babylon.js 8.x/current and Three.js WebGPURenderer as measured alternatives rather than combining three scene engines into one application. The highest-scoring actual implementation on target Android, not marketing screenshots, wins. Use PlayCanvas by default because it has built-in web-game scene/lifecycle machinery, physically based rendering, glTF and first-class Gaussian splatting, WebGPU, mobile-tuned content streaming.

**Physics:** Rapier JS/WASM as an independent gameplay physics service for deterministic authoritative rigid-body interactions; physics meshes are decoupled from visual/splat geometry. PlayCanvas's built-in Ammo.js/Bullet may be used for the native component system only if it is clearly adapter-isolated and does not create divergent authoritative world histories. Numerical/camera path reference authority stays available through GNU Octave + verified native solvers. Simulation fixed timestep, separate render interpolation.

**Android:** Capacitor wrapping the same compiled web renderer/client, with Kotlin native immersive-screen support through platform UI APIs, sound focus, haptics, gesture detection and reconnect. Produce **real** `.apk` bytes and signed/debug provenance (APK hash, build log), no placeholder. Offer a PWA for browser install independently. Device boot/cold entry, mobile graphics backend, touch and audio require actual tests.

**Cloud high-fidelity path:** When a real Unreal GPU host becomes available, rendezvous client can connect to Pixel Streaming 2. It must also run as a native locally rendered web scene when Pixel Streaming is unavailable. Do not stop web/APK execution simply because Unreal cannot be installed on Oracle ARM.

## 2. One world, multiple renderers

The following remain authoritative outside the front end: global coordinate/tiles/world graph; NPC actor/cohort/virtual policies; state grammar × in-grammar; causality/events; PURL/SEURL/ACSP; founder and cohort rights; authenticated self-describing operation addresses; asset provenance; named world transformations; real astronomical positions and fictional sky signals; spatial/weather/transport mathematical models; sound event semantics. One coherent `WorldSession` protocol handles actor identity, reference frame, timebase, entity snapshot, delta, activity, speech act, physics authoritative events, event log, ownership, computed decisions and reconnect. Schema version and compatibility tests required.

Rendering adapters consume only typed scene projections, not game rules. Define `SceneBridge` methods: `initialize`, `loadWorldCell`, `applySnapshot`, `applyDelta`, `attachActor`, `attachAudio`, `setWeather`, `setSky`, `setCameraGrammar`, `preloadNearField`, `unloadFarField`, `captureTelemetry`, `dispose`. Support `renderTarget: webgl2|webgpu|pixelstream` without changing world state identity. The UE adapter is an explicit future/parallel executable target; no false claim of parity before comparison tests.

## 3. Visible playable launch / Dark rendezvous

**World enters before player**: opening begins with an existing world simulation. Traffic streams continue, parked cars glow from nearby lighting, character groups converse, planes are audibly passing at varying distances, food-cart audio exists, an ambient song or street performer may be audible, billboard emissive materials react to light, and near-field crowds cross sidewalks. The player arrives at **North Dale Mabry Highway × West Spruce Street, Tampa**, with no real-person surveillance/reconstruction. Business names and public-facing labels are fictional and renamable under the game governance model. Dark's personal origin **Marina del Rey** is retained as historical character metadata and later world QA anchor.

**Opening cinematic**: transition from a moving street/sky glance into third-person hero framing of Dark. A few NPCs turn naturally, a distant group hesitates then resumes, nearby traffic gently modulates within lawful physics, music and spatial ambience swell with subtle motifs, signs and reflected light accentuate the arrival. The effect is **diegetic**, not a modal interface; users may skip or reduce motion. Never slam all cars to a stop or turn every agent into a synchronized puppet. Distinguish first-time arrival from rejoin. Changes to globally shared simulation must not punish nonjoining players; local perception layers can personalize the event.

**Player controls**: third-person walk, orbit camera, look, touch joystick, tap to interact, hands-free curious/relaxed walking where paths exist, pause/resume and safe exit, default camera keeps horizon stable without camera jitter and with obstruction smoothing. Fallback high-level vehicle passenger/entourage interaction only when implemented in real simulation; never animate non-interactive cars and claim drivable vehicles. City becomes the interface: believable billboards, signs, lamps, sound, NPC reactions and street performance rather than a floating HUD flood.

**Joining**: user enters a real 3D runtime full-window experience; web fullscreen request is triggered by a real `Enter HOMELESS` gesture where supported. Browsers sometimes refuse or exit fullscreen; then use the 100dvh viewport and minimal chrome-compatible fallback without scrollbars. Android launches in native immersive mode and lets the user reveal OS system navigation when required. No assumption browsers permit programmatic forced fullscreen without gesture.

**Founder controls**: Dark/Abed Kadaan can see developer/provenance overlays via authenticated internal tools; these must not become publicly reachable debug powers. Cohort membership and NPC friendships are opt-in and persistent; NPCs retain their own refusals and believable daily autonomy.

## 4. 3D fidelity and ingestion

Collect visually strong, **actually usable runtime-agnostic original models/textures** (GLB/glTF 2.0, FBX/OBJ source where convertible, KTX2/Basis textures, HDRIs, animations). Keep an organized source inventory for Unreal-native `.uasset` content separately; the web renderer cannot directly load arbitrary `.uasset` files, shaders, Nanite assets or UE-only blueprints. Where a selected production-grade asset has source interchange files, create a validated web variant. Otherwise acquire a comparable independent high-fidelity asset and retain the original Unreal acquisition lane.

Asset grades: visible close-up / interactive PBR meshes; mid-range instanced mesh LOD; far-range impostors or streamed splat/environment. Prioritize people/face+hair rigs, car interiors/exteriors, motorcycles, bikes, pedestrians, airplanes near Tampa airport, street pavement, urban façades, shopfronts, glass, puddles, signage, scooters, landscaping and atmospheric effects. Material specifications: physically based basecolor, metallic, roughness, normal, emissive, AO and correct color-space handling. Wet pavement and shop signage must produce physically plausible specular highlights/reflections *within available hardware capabilities*; no fake static painted puddles marketed as dynamic reflections.

Run explicit asset validation: model formats, triangle budgets per LOD, UV/normal/tangent correctness, bounds, transforms, skeleton mapping, animation clips, collision proxies, KTX2 texture dimensions/transcoding, load times, visual regression where GPU test runner is available. Encode glTF geometry for verified target loader: prefer Draco where supported, do not blindly ship unsupported meshopt glTF extensions to PlayCanvas. Separate format compression from actual runtime decoding tests. Implement offline bundle with compact origin subset + CDN/cache long-tail worlds, speculative loading along walking direction and user-teleport destinations.

WebGPU and WebGL2 should share visual semantic targets but not assume feature parity. Enable advanced effects (temporal anti-aliasing if supported, SSR-like reflection, SSAO, contact shadows, high-quality sky/volumetric approximation, bloom, tone mapping) only where stable. Lower render resolution and splat budgets before destroying the world-content quality. Reconcile interpolated motion to eliminate jitter from inconsistent simulation and render timestamps.

## 5. Audio and mathematically driven movement

Audio layers: binaural/stereo positional vehicles, distant planes, crowds, conversation, footstep surface changes, reflections/occlusion when computed, shops, ambient music, wind, and discrete celestial/symbolic effects. Browser audio unlock after the enter gesture; Android focus routing. Measured roundtrip from action to sound and no audible gaps when the world streams.

Navigation / camera grammar is a typed mathematical problem: collision-safe available paths, state-relative jerk/acceleration minimization, occlusion recovery, damped follow camera, angle and angular-velocity bounds, auditable decision constraints. Test control system stability under 15/30/60 FPS simulation render interpolation and reconnection. Physics and navigation require real interactive responses, not declarative animation only.

## 6. Non-LLM game intelligence / world contribution

Connect ALL model families to the world session, not separate tech demos: activity, social group, actor agency, dialogue act, grammar/in-grammar, soundscape, transport, environment, astronomy, mission/scene, asset, governance, portal. Heavy models may be synthesized into portable symbolic recipes and opened on demand, but event and outcome evaluation must remain in the trusted core. Every generated structure records grammar, generation seed, input context, verification and observable. Users and NPCs can contribute names, signs, routes, discovered patterns, public murals and code-as-journey fragments; records are versioned and reversible where permitted. Use free member mode without forcing quest activation.

The existing `World Loom`, `HOMELESS REALMS`, `Ingram`, `Tashkīl`, `PLICASTRATUM`, `BORNE`, `PURL/SEURL`, `ACSP`, and Octave-derived research artifacts are source inputs, not optional fluff. If an integration requires shims, make shims; don't replace the authority with mock JSON responses. Provide at least one inspectable actual actor decision, street event, and persisted world change visible after an app restart.

## 7. World scope and releases

**Planetary grammar from day one**, no Los Angeles-only or Tampa-only engine. Real location/provider adapters, global canonical coordinate charts and index correctness (antimeridian, poles, boundaries) must compile/test. Render one real client camera at a time and stream near-field spatial cells + relevant active/cohort NPCs; virtual worldwide people should not incur per-frame simulation ticks. If a region has incomplete sourced assets, use an explicitly identified high-quality adaptive environment recipe for that region rather than lie about actual buildings. Globally addressable is not identical to globally photogrammetric.

Launch profile: first interactive world coordinate Tampa, but global indexing/traversal remains functional. The shipped Rendezvous web+APK is a **fully playable integrated release** that can expand geographically, not a six-block graybox called done. Preserve the original Unreal asset/render pipeline as an independent continuing requirement.

## 8. Delivery

Implementation outputs: source tree and repeatable dependencies; web production build; deployed web URL when suitable deployment access exists; PWA manifest/service worker; Capacitor Android project; `.apk` file with checksum; demo journey trace (Tampa arrival → walk → talk → world change → exit → reenter); benchmark logs and dimensioned performance results; state/server services; story event log; asset hashes, residency controls and tests. Capture release manifest hashes and origin source commit. If external accounts or physical device access are missing, build everything possible and report exact missing item honestly. Do not state APK installed on Samsung without an actual install/run test.

**Masterpack priority:** Source Godpack is immutable. This rider applies to the delivery surface. It does not remove or rewrite any source scope; a WebGL release is not falsely reported as passing Unreal-only cook/render gates.
