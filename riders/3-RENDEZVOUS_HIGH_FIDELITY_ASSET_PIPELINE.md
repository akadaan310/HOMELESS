# HOMELESS — Rendezvous High-Fidelity Asset Ingestion Rider V2

**Directive type:** additive rendering/art pipeline contract; **does not modify** the immutable Unreal masterpack or Rendezvous V1 rider.

**Owner and founding player:** Dark / Abed Kadaan. **Target:** cinematic, photorealistic, interactive, stable browser and Android APK access. **Presentation layer:** PlayCanvas/WebGL2 baseline; opt-in WebGPU. **Permanent Unreal lane:** UE 5.8 assets and rendering ambitions unchanged. **Scope:** no invented visual substitutes when existing quality artwork is available.

## Absolute design decisions

1. **Assets first, procedural substitution never by convenience.** Find and obtain high-resolution professional 3D objects, 3D scenes, rigged/animated characters, architecture, vehicles, vegetation, street furniture, interior props, roads and materials. Catalog acquisition state as `candidate`, `retrieved`, `converted`, `verified`, `scene-integrated`. `candidate` alone does not count as a finished scene.
2. Maintain a **source-quality master asset** plus independently generated **Unreal-native** and **Rendezvous-runtime** derivatives. Processing, mesh reduction, LODs, atlas baking, texture packing and collision proxy generation are technical packaging operations, not art-content replacement.
3. Assets are **visually equivalent in authored design and identity across renderers**, not guaranteed pixel-identical: Nanite/Lumen/render-specific material graphs cannot simply be shipped through glTF. Preserve the source silhouette, proper scale, silhouette-defining components, texture detail and believable material response.
4. **No low-poly / graybox visible in investor release.** Physics collision proxies and fallback volumes may be invisible. If a required scenic category is unfilled, treat it as a visual-content acceptance failure; do not quietly replace a gorgeous street with procedural cubes.
5. Phones receive geometries appropriate to measured GPU budgets; their source fidelity remains archived. Stream from servers/CDN by position, velocity, view frustum, occlusion, and next probable street path. No requirement to bundle all large art in the APK.
6. Opening scene: North Dale Mabry Highway / West Spruce Street, Tampa; fictional store identities over geographic context. First impression includes authored human faces, vehicle silhouettes, rich signage, natural movement, reflections, vegetation, aircraft, spatial audio and the collective recognition moment.

## Evidence-backed source candidates and immediate acquisition order

### Priority A: import-ready, art-quality assets

- **Poly Haven Models:** https://polyhaven.com/models — photogrammetric and authored high-res objects in glTF/FBX and other interchange formats. First certified technical fixtures: https://polyhaven.com/a/covered_car (detailed 8K covered car); https://polyhaven.com/a/street_lamp_01 (8K ornate street lamp). These are *examples*; a covered car does not replace moving vehicles, nor a decorative lamp replace an entire street.
- **Poly Haven Materials:** https://polyhaven.com/textures ; specifically https://polyhaven.com/textures/asphalt-bitumen/roads and https://polyhaven.com/textures — physically based surface maps, brick, worn concrete, painted metal, glass, paving, vegetation. Find matching coherent material families rather than combining random uncalibrated swatches.
- **Poly Haven HDRIs:** https://polyhaven.com/hdris — real-environment lighting capture, image-based lighting reference and reflection calibration.
- **ambientCG:** https://ambientcg.com/ — additional detailed PBR scans/materials and environments.
- **Portable third-party art search:** inspect high-quality FBX/GLB/USD exports from multi-engine asset publishers in Fab and Sketchfab or other catalogues. Verify exact downloadable source formats and actual visual quality. Do not confuse marketing screenshots with successful in-engine renders.

### Priority B: maintain the Unreal art lane in parallel

- **Unreal City Sample, City Sample Buildings, Vehicles, Crowds, Megascans, Electric Dreams and other nominated reference packs:** retain the original UE collection/asset registry **as-is** for future Unreal rendering. Do not assume `.uasset` bundles are portable directly into browsers.
- **Unreal 5.8 GLTFExporter** supports export of many static/skeletal meshes, materials, animations and supported level content to glTF/GLB: https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/Miscellaneous/ExporttoGLTF?lang=en-US
- Export each *actually exportable* source only through available toolchains; document material baking, UV precision, animation limitations, missing collision and one-LOD-per-export behavior: https://dev.epicgames.com/documentation/en-us/unreal-engine/how-the-gltf-exporter-handles-unreal-engine-content . Source-file existence and successful cross-runtime visual result are separate gates.
- Exporting data from Unreal is not the same as exporting its Nanite scene graph, global illumination, weather behavior, or Chaos physics. Reimplement the renderer-specific *presentation and behavior adapters*, not the asset's artistic identity.

### Priority C: landscape/architecture scans

- **PlayCanvas SuperSplat / Streamed SOG:** https://developer.playcanvas.com/user-manual/gaussian-splatting/formats/streamed-sog/ and https://developer.playcanvas.com/user-manual/gaussian-splatting/building/unified-rendering/lod-streaming/ . Ingest existing high-resolution real-world scans where source content exists; convert to streaming LOD, partitioned by area and camera relevance.
- Represent photoreal scene background with splats when useful. Render interactive cars, doors, characters, collision geometry and animated NPCs primarily as rigged polygon meshes unless explicitly verified for another pipeline.
- **Worldwide spatial indexes:** existing HOMELESS atlas adapter, Overture/OSM road/building geometry and scanned architecture. Map shape/data are used for placement and provenance, not to justify fake photo-real objects. Source priority: verified acquired model > real geometry + premium modular authored components > explicitly labeled incomplete sector.

### Priority D: unmet categories (must actively search, obtain, import, and report)

1. Streets/architecture: 20+ visibly distinct modern commercial storefront modules, 10+ roadside asset classes, parking/sidewalk/curb/road-sign/signal sets; real regional style selection.
2. Vehicles: high-fidelity passenger cars, buses, bikes, scooters, motorcycles, vans, emergency-style snack-break vehicles, drivable interiors, accurate tires/glass/paint; car rigs and wheel pivot validation.
3. NPCs: real human facial quality, age/wardrobe variety, skeletons, hands, gait and facial animation, crowd LOD families, independent behavior linked to authoritative world-model agents.
4. Water/air: aircraft, balloons, ground service vehicles, boats, reflective water surfaces and engine/rotor/traffic audio.
5. Retail/urban culture: cafes, interior fixtures, food carts, furniture, illuminated shop signs, billboards, realistic food/drink props; false/fictional storefront names applied as texture/signage variants over sourced meshes.
6. Natural/weather: regional vegetation, sky/HDRI reference, detailed wet road, puddle decals, reflection probes, rain particle/mesh/audio assets, believable nighttime lighting.
7. Animation/audio: footfall/idle/turn/gesture/wave/interact cycles, crowd choreography, vehicle cabin sounds and ambiences.

## Acquisition/build pipeline (exact order, with independent checks)

`DISCOVER → PREVIEW → FETCH → INVENTORY/HASH → NORMALIZE → MATERIAL-CONVERT → RETOPO/LOD/ATLAS → COMPRESS → PHYSICS PROXY → INTEGRATE → INSTRUMENT → PUBLISH TO STREAMING CATALOG`

- Discovery: build a **category/priority/source/format/quality** catalog of individual concrete asset IDs and collections; actively retrieve the best available candidates. Do not stop at writing this list. Use downloadable public source formats and access the official publisher's archive.
- Source master: keep highest-quality mesh and texture files in immutable content-addressed storage with SHA-256 and original source name. Record `width`, `height`, units, vertex/triangle count, skeleton, animations, shader inputs, physically measured bounds, scene scale, texel density and image-space lookdev references.
- Normalization: enforce meters and coordinate handedness/forward/up orientation with per-family adapters; bake transformations; verify normals/tangents/UVs/material packing; maintain PBR metallic-roughness with accurate normal-map handedness and roughness. Check glass, emissive, decals, foliage opacity and double-sided materials separately.
- Output: baseline **GLB/glTF 2.0**, KTX2/BasisU compressed textures (supported transcode targets), runtime-verified Draco mesh compression where advantageous, and explicit LOD files. Source remains uncompressed/unreduced. Test asset re-import into the selected PlayCanvas version. Use `gltf-transform inspect`, `gltf-transform optimize` with deliberate compression selection; do not treat defaults as universal.
- GPU variants: one common canon asset ID with `rendezvous-low`, `rendezvous-medium`, `rendezvous-high`, `unreal-source`. Versions, asset art provenance, checksum and geometry/texture deviation stats recorded for each; never bind world identity to a renderer-specific filename.
- Physics: retain separate lower-poly triangle collision geometry / convex or primitive colliders where they provide adequate collision behavior; render visually rich sourced mesh independent of physics proxy. Gaussian splats alone are not authoritative collision meshes.
- Streaming: cache neighboring cells, apply predictive preload using speed and path direction, shed unseen far LOD levels first, reuse material textures, and evict old cells under measured memory pressure. CDN or object storage asset bundles may be arbitrarily large collectively. **Initial download to playable frame remains bounded and measured.**
- QA: byte/format validation, mesh bounds, naming convention, missing material flags, skeletal rig round-trip, camera-visible alpha and blend passes, directional lighting comparisons, signed/unsigned coordinate assumptions and real device GPU measurement. Stop on unreadable/improper assets; avoid invisible replacement assets that only satisfy code-path tests.

## Fidelity tier ladder (per scene, not a cosmetic label)

| Tier | Rendering | Target implementation / evidence |
|---|---|---|
| **R0 archival source** | Master 8K/16K scans, photogrammetry, PBR and animation, original formats | lossless source, preview, dimensions, hashes; not a game target |
| **R1 Unreal cinematic** | UE native highest-end assets; Nanite/Lumen and high-end render features | original Godpack's UE render gates; compiled/cooked only when Unreal host exists |
| **R2 Rendezvous cinematic desktop/cloud web** | PlayCanvas WebGPU where supported, best authored mesh LOD, detailed material/light/shadow/reflection and streamed splats | measured 60 FPS target on declared workstation, parity fixtures and material tests |
| **R3 Rendezvous premium midrange mobile** | portable GLB medium/high LOD, GPU-compressed maps, targeted environment/reflections, dense but bounded NPC population | stable measured 30–60 FPS target as feasible with visible quality checks |
| **R4 Rendezvous founder low-tier phone** | authored original shapes preserved via appropriate LOD, KTX2, adaptive render scale, intelligent cell streaming, selective expensive post effects | stable 30 FPS target; p95 frame budget and input latency recorded on actual device; no long frame stalls or placeholder appearance |

Tier downgrade changes *rendering cost*, not identity, art direction, discovered world location, NPC agency, PURL state or user ownership. The app automatically chooses a tier by observed load, dynamic resolution and screen-space error; low-power mode must preserve stable controls and audio. Features too expensive for the device should be carefully minimized or moved to streamed/cloud rendering where available.

## Photoreal quality numeric/visual acceptance gates

- **Material fixture**: calibrated wet/dry asphalt alongside gold/painted signage, headlight response, glossy automobile paint, skin scattering approximation, glass, matte clothing, foliage; validate BRDF inputs, tonemapping/exposure and high-contrast legibility. Reflection of a yellow fictional convenience-store sign should respond to wetness, time and view angle, not be painted permanently into a fake normal map.
- **Motion fixture**: three full-body rigged NPCs with animated footsteps, turn/gesture/idle, collision and correct feet on pavement; one detailed vehicle drives past with tire rotation, suspension proxy, headlights, wheel material and contextual audio.
- **Scene fixture**: investor-grade Tampa entrance with near-camera street lamp/car, detailed storefronts, small active crowd, believable exposure; real source assets in `asset-manifest.json`, not substitute cubes.
- **Streaming fixture**: walk/drive several consecutive cells and return; report bytes loaded, CPU/GPU memory, draw calls, 1% low FPS, p95 frametime, render resolution, decoded textures, LOD swaps, shader compilation spikes and asset cache hit rates.
- **Visual validation**: programmable side-by-side art references plus controlled rendered viewpoint captures and numeric similarity/edges/material checks. Include *human art review* when available; metrics alone cannot determine visual taste. Never claim cinematic parity merely because tests passed or a marketing picture was retrieved.
- **Real Android browser/WebView**: verify actual 3D material shaders, HDRI fallbacks and image decoding in the APK and the real phone. WebGPU is enhancement only; WebGL2 must actually work where chosen. Fullscreen, orientation/audio-unlock, page scroll prevention and process suspend/rejoin remain under Rendezvous V1 gates.

## Codex acceptance for this rider

- Produce `assets/catalog.json`, `assets/originals/` or versioned server-side asset bucket, `assets/runtime/` manifest, converters/config/QA scripts, at least one real sourced environment and imported 3D NPC/vehicle model, and downloadable + device-testable scene.
- Include a source-asset `SHA256`, content-addressed master source reference, per-tier delivered GLB/texture/splat paths, mesh/material metrics, final runtime material screenshot or capture, and FPS/thermal/VRAM report. `candidate` is not `acquired`; `optimized` is not `rendered`.
- Full object coverage is a catalog-and-acquisition task even where the first render can only load nearby content. Missing collections should be reported exactly, not fabricated as finished.
- Reuse PURL/SEURL/ACSP and world state through existing interfaces, not replace these contracts with a renderer-local data model.
- Do not rewrite existing Unreal or Rendezvous Godpack documents. Implement the new fidelity pipeline as an additive, auditable commissioning requirement.
