# HIGH-FIDELITY UNREAL ACQUISITION → COOK → STREAM PIPELINE

**Hard choice:** Unreal Engine 5.8 or compatible patch, PC/cloud-GPU 3D primary; Pixel Streaming 2 to Android/web; native Android renderer only separately budgeted. The intent is premium City Sample / Matrix Awakens-grade visuals, not teaching assets or generated gray boxes marketed as photorealism.

## Acquisition philosophy

Find available production-quality 3D models, animations, materials, audio and scene configurations *before* authoring synthetic substitutes. Reuse existing high-quality meshes/scans wherever possible, with procedural systems arranging them to map footprints, traffic graphs, climate, time and story. Keep the resulting server library separate from the Android APK: user gets streamed frames/audio plus compressed local UI/model metadata. Cache only a walkable and visible cone plus motion-predictive surroundings. An item catalog is **not** an item downloaded, imported, quality checked or rendered; each state is tracked distinctly.

## Priority asset collection sources — verified leads

| Priority | Source | Use | Ingestion strategy |
|---|---|---|---|
| P0 | https://www.fab.com/listings/4898e707-7855-404b-af0e-a505ee690e68 | City Sample 5.8 complete urban seed, road/building PCG, traffic, crowd, audio | Ingest native UE project; isolate reusable content and example PCG graphs; map metadata; benchmark |
| P0 | https://www.fab.com/listings/008fe959-5511-428e-93bd-f99b1179f6d5 | City Sample buildings, 2,000+ modules | Catalog HISM/Nanite-compatible facades, corners, floors, doors, roof assemblies |
| P0 | https://www.fab.com/listings/2909157b-ddfa-4cef-a925-69dc2467021f | City Sample vehicles | Vehicle taxonomy, rigs, suspensions, material and LOD validation |
| P0 | https://www.fab.com/listings/903037e9-e1ac-4f41-96e8-1683c6fa7ad4 | City Sample crowds | Crowd variants, animation LOD, MassEntity, close range MetaHuman handoff |
| P0 | https://dev.epicgames.com/documentation/metahuman/metahuman-creator-in-unreal-engine | Hero NPC and avatar faces, rigged humans | Shared animation abstractions, clothing and hair LOD |
| P0 | https://www.fab.com/listings/d79688f5-29be-4fb2-a650-2d4a813f5306 | Electric Dreams flora / realistic landscape reference | Import compatible landscapes and vegetation for biomes |
| P0 | https://polyhaven.com/models ; https://polyhaven.com/hdris | Photogrammetric props/real HDRI | Download selected high-resolution source, metadata and preview variants |
| P0 | https://ambientcg.com/ | High-quality PBR surface library | Material normalization, packed maps, wetness layers |
| P0 | https://www.fab.com/listings/673d4ee4-db90-47a6-8520-38bcb8a43b24 | Surface detail for asphalt | High-res normal/roughness verification |
| P0 | https://cesium.com/learn/cesium-unreal/ref-doc/ | WGS84 georeference and 3D Tiles streaming | Match UE version; connect data source and geospatial metadata |
| P0 | https://www.ogc.org/standards/3dtiles/ | Hierarchical world 3D streaming | Vendor-neutral tile server cache, georeference/LOD specification |
| P1 | https://www.fab.com/listings/5dd132fe-ee32-4e8c-9cd3-7496547dfb29 | Automotive PBR surfaces | Normalize UE materials and instancing |
| P1 | https://www.fab.com/listings/0c19880e-21bd-42ba-8287-1caccc3951b1 | Valley of the Ancient environmental quality reference | Separate high-quality biome reference |
| P1 | https://www.fab.com/listings/e714ec2e-e31a-4390-a666-abee93c8d579 | Regional photogrammetric urban pack candidate | Acquire only if accessible and selected |

**Unfilled categories are acquisition work items, never fictional claims of existing inventory:** Cessna/general aviation, commercial airliners, airports/hangars, yachts/ferries/cruise/cargo craft, hot air balloons, scooters/bikes/motorcycles, global regional street families, shops/gas stations/food carts, cafes and interiors, skyscraper signage, palms and coastal plants, rain/snow volume assets, unique clothing crowds, detailed motion capture, people across ages, radio/festival/traffic/water audio. Build asset-discovery queries and a batch candidate index for all classes; download/install in the available environment in quality-ranked batches, not indiscriminately. Prefer curated premium-quality sources over large low-quality bulk sets. No Blender modeling prerequisite.

## Asset registry and ingestion graph

Candidate `→` obtained `→` verified-by-hash `→` geometry/texture/rig validated `→` compatible UE import `→` cooked `→` registered/LOD-tagged `→` placed `→` scene-tested `→` published-to-private-streaming-server.

**Schema**: `asset_id`, `source_url`, `origin_pack`, `version`, `category`, `geo_region_style`, `real_or_fictional`, `sha256`, `format`, `triangle_density`, `lods`, `skeletal_rig`, `animation_sets`, `collision_bounds`, `nanite_suitability`, `texture_size`, `normal_orientation`, `roughness_range`, `metalness_range`, `UV_conflicts`, `instancing`, `scale_m`, `material_instances`, `audio_occlusion`, `UE_plugin_dependencies`, `import_status`, `cook_status`, `runtime_tile`, `quality_metrics`, `visual_category_score`, `unavailable_reason`.

Automation must check mesh manifold/surface normals, transform, instancing viability, texture packed channels and MikkTSpace compatibility, animation contact, rig bone matching, material exposure and surface response, shader permutations, collisions and navmesh integration. Importers output deterministic manifests and machine-readable diagnostics. Preserve highest quality original assets in server store; cook device-specific derivatives rather than degrading original library.

## Scene realization, not whole-Earth memory

1. Geospatial index resolves requests in WGS84/ECEF and localized ENU coordinates; choose streaming LOD from screen-space error, distance, semantic importance, and predicted motion.
2. Layer `terrain + real road geometry + height/footprint evidence + building/style assets + traffic markings + curb/sidewalk geometry + façade/signage + props + vegetation + characters + FX + sound zones`.
3. Procedural placement uses sourced geometries where present. In uncertain areas build high-quality **fictional** coherent compositions, and attach precise source-quality metadata internally.
4. World Partition holds local detailed maps; OGC tiles manage global geospatial streamed scenery; HLOD and origin rebasing control memory/precision. Never require global actors to exist as UE Actors concurrently.
5. Streaming policy radius depends on camera FOV, avatar velocity, road traversal graph, likely turns, prior player habits and bandwidth. Track time-to-visible and tile eviction. Prefetch jet-flight/portal destinations during the portal choice/cinematic bridge.
6. Sound, weather, NPC schedules and sky use the same cell/time identities while remaining decoupled from render resolution.

## Physical fidelity gates

- Lumen and Nanite modes chosen by material/hardware; reflection response to street signs and emissive surfaces measured through environment maps and buffer probes. Rain creates wetness gradients and puddle microtopology rather than a uniform glossy material.
- Volumetric clouds, height fog, physically motivated sun/moon, cloud shadows, traffic lights, emissive billboards and coherent exposure; Virtual Shadow Maps and TSR where appropriate. Temporal shimmer/ghosting, texture streaming thrash, broken normals, shadow popping and animation foot slide are failing defects.
- Dense street ambience is real 3D and sound scene behavior—not 2D billboards hiding nonexistent pedestrians. Distant crowds use instanced high-quality LOD representation; near pedestrians become individual skeletal characters.
- Car interiors, headlamps, glazing, paint, wet tarmac, dynamic reflections, wheels and road contact. Record test vectors for physical and aesthetic metrics. Human art-direction final signoff is supplementary, never the only acceptance signal.

## Device strategy

**High-end PC / GPU server**: render premium UE, separate authoritative simulation, produce WebRTC AV using UE5.8 Pixel Streaming 2. Target 1080p60 in favorable network profiles; degrade bitrate/resolution before interactivity, preserve 30 fps minimum profile where possible. Instrument effective frame times, encoder time, capture-to-photon latency, packet loss, visual stability, audio sync.

**Android**: Kotlin native APK providing installable app, immersive full-screen stream viewer, input/touch/gyro control, secure session continuity, offline fallback mode, stable camera/input mapping, reconnect resume and optional gamepad. No claim the APK contains complete photorealistic UE PC assets. Browser uses the same stream frontend in responsive UI. For native UE Android build, create a downgraded profile and report independently.

**If no remote GPU host is available**: ship *actual APK containing a useful local offline interactive entry* and reproducible server deploy/launch scripts; do not call an unreachable streaming shell a complete playable AAA APK. Record the missing host and link success gates to an executable test.

## Performance and quality targets (initial acceptance targets, not achieved claims)

- 90th percentile visual streaming frame time ≤ 16.7ms on named GPU for chosen 60fps target; 99th percentile ≤ 33.3ms after warmup in canonical test area; alternate 30fps profile explicit.
- Model/material load spikes must not exceed 100 ms foreground stall at ordinary walking speed after prefetch; profile rather than presume.
- Occlusion/collision mesh consistency rate ≥ 99.5% across sampled sourced geometry; visible texture/material placeholder rate 0% in accepted hero scene.
- Asset catalog at least one verified installed item for each P0 core class with category-fidelity test before final scene quality declaration; all P1 gaps listed if not fulfilled.
- Coverage masks and truthful fallback labels for arbitrary worldwide coordinate probes. No fake success for absent globe resources.

**External primary docs**: https://dev.epicgames.com/documentation/unreal-engine/city-sample-project-unreal-engine-demonstration ; https://www.unrealengine.com/learning/city-sample-gets-a-major-update-with-pcg-and-unreal-mcp-workflows ; https://dev.epicgames.com/documentation/unreal-engine/pixel-streaming-2-overview-in-unreal-engine ; https://dev.epicgames.com/documentation/unreal-engine/metasounds-the-next-generation-sound-sources-in-unreal-engine
