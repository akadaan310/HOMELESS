# BUILD GRAPH / MODULE DEPENDENCIES

This file converts the long PRD into a dependency DAG for parallel coding agents. It is NOT an excuse to abandon the one-shot product delivery.

`SourcePacks → (Models, CGT, InGrammar, Plica, BORNE) → CoreIR → ProtocolBus → WorldService → UnrealAdapter → WebRTC/Android/Web`.

**Parallel work lanes:**

- `CoreIR`: grammar generator, AST, programs-as-walks, finite weighted transducers, fold/unfold, typed solver problem interfaces.
- `Continuity`: event store, ACSP local bus and renderer restarts; native shell `darkctl` worker, JS and Wasm and local CLI.
- `Geo`: Overture/OSM ingestion, ECEF/ENU world coordinates, source masks, route/spatial grammar and worldwide indexing.
- `Math`: Octave reference fixtures, runtime solver bridge, camera/controller optimization, causal/multi-agent games and statistical tests.
- `WorldModels`: active/cohort/virtual NPC simulation, fictional names, authorship, missions, grammar/ingrammar and policy selection.
- `AstralAudioWeather`: catalog sky solver, constellation pattern miner, numerical weather field and procedural MetaSounds integration.
- `UnrealVisual`: UE5.8 project/cook, City Sample assets, crowd/cars/terrain, light/weather/sky, cameras, first-run cinematic and scene QA.
- `Delivery`: stream host frontend, Android APK, browser, offline entry, world protocol bridge and soak tests.
- `Verification`: build environment manifest, schema conformance, CI, source metrics, frame/audio tests, APK installation, result pack/hashes.

**Stable contracts first** from `interfaces/PROTOCOL_CONTRACTS.md`; generated code/test suites share explicit type schemas. When a lane is blocked by missing hardware, other lanes proceed. Rejected schema changes require migration manifest. Do not allow independent agents to modify the same persistent store or world-authority table without integration tests.

**Executable gates:** `core-conformance`, `protocol-IPC`, `shell-worker`, `octave-reference`, `world-global-index`, `unreal-cook`, `scene-interactive`, `pixel-stream`, `apk-install`, `cross-platform-smoke`, `research-findings`.
