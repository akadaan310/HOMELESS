# Rendezvous render/asset/physics decision record

## Runtime selection

**Default production candidate: PlayCanvas Engine 2.23.x (current October 2026 family)**, WebGL2 baseline; WebGPU selectively feature-gated. Benchmark Babylon.js and Three.js in isolation against *the same* scene fixture if this candidate cannot meet the acceptance matrix; no unmeasured rewrite.

Why: browser-focused complete engine loop, WebGPU/WebGL2, glTF, PBR, first-class Gaussian splats, browser/mobile-friendly streamed LOD, XR options. Official starting points:
- https://playcanvas.com/products/engine
- https://developer.playcanvas.com/
- https://developer.playcanvas.com/user-manual/supersplat/streaming/
- https://threejs.org/manual/pages/webgpurenderer
- https://www.babylonjs.com/specifications/

**Geometry and materials**: GLB/glTF 2.0; KTX2 Basis Universal; glTF extension compatibility checked with the exact chosen importer; Draco vs meshopt compression handled based on loader support; machine-readable LOD policy; atmospheric cubemaps/HDRI; material parity reports. Editor-only Unreal `.uasset` content remains on Unreal's lane unless original mesh/texture interchange data can be exported into a common format.

**Gaussian splats** are visual only unless separately collidable. Collision, ray queries and movement use indexed low-complexity physics proxies and an independently validated world mesh. Do not simulate player contacts against millions of Gaussian primitives. Label volumetric display data vs geometric collision authority.

**Physics**: Rapier JS/WASM recommended for authoritative replay and character/vehicle physics where feature-fit is measured. When using PlayCanvas's Ammo.js system, wrap it behind a consistent `PhysicsPort` and document determinism scope. Rapier deterministic replication requires same initialization, insertion order and step inputs; nondeterministic JavaScript math at initialization can break equivalence. Use fixed-time simulation (`1/60` sec for high tier; budgeted server/cohort ticks separately), `interpolate(renderTime)`, clamp giant elapsed time after backgrounding, and preserve world state snapshot after app suspension.

**Camera**: cinematic damped third-person, dynamic occlusion recovery, horizon control, angular jerk constraints, near-clip and full-screen render resolution tests. Avoid using browser scroll or DOM animation as player-camera movement.

**Audio**: Web Audio worklets for dynamically mixed spatial ambience + streamed or cached high-quality stems; interpolated listener orientation from camera, environmental sends and occlusion. Touch unlock and interruption recovery tested.

**Engine separation**: game core owns truth, scenes consume typed projections. No cross-renderer dependence on a PlayCanvas asset ID or UE path as universal identity: use `world://` canonical entity/asset IDs and adapter-specific realization maps.

## Measured alternatives

- **Babylon.js**: strong node/frame graph control, WebGPU/WebGL, physical materials, built-in physics integrations, large-world / 3D Tiles facilities. If the reference PlayCanvas scene fails numerical frame-budget or missing required rendering effect, benchmark Babylon with same assets on same devices.
- **Three.js**: excellent low-level renderer and TSL/WebGPU render pipeline, WebGL2 fallback. Viable if manual game-engine subsystems are necessary and benchmark shows advantage; higher orchestration burden for a world game.
- **Unreal 5.8**: retained high-end primary renderer for GPU-host/Pixel Streaming and native builds, not demanded as a tool that must run inside ARM64 Oracle just to ship the Rendezvous presentation.

Do not combine physics islands or camera loops from competing rendering engines into one authoritative scene without explicit adapters and tests.
