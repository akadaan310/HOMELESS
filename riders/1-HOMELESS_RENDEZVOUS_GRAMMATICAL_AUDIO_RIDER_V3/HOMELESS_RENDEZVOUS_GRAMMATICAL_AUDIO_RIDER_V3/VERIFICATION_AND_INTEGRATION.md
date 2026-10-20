# CODEX VERIFICATION MATRIX — GRAMMATICALS / VOICES / BOOTSTRAP GATES

## 0. Execution rule

The goal is an integrated playable Android APK + browser, not a paper or an isolated audio service. This rider augments the earlier release gates. **Do not conclude based on mocked or unplayed audio.** Implement, build, link and run the features. Continue on the existing development branch rather than restart.

## 1. Workstream and authority interfaces

| Layer | Authority | Required interface |
|---|---|---|
| World/actors | existing backend and versioned ledgers | `WorldSession` actor/context/event APIs |
| Grammar factory | G + In-Grammar/plicastratum | `grammar.compile`, `grammar.validate`, `grammar.expand`, `grammatical.run` |
| Gate scheduler | pure prediction from world snapshot | `gate.plan`, `gate.prepare`, `gate.cancel`, `gate.status` |
| Asset and media | source art V2 / voice catalog | `asset.resolve`, `audio.resolve`, `voice.prepare`, `cache.evict` |
| Small utterance helper | optional Ollama worker | `utterance.propose`, `utterance.validate`, `utterance.reject` |
| Player mic/ASR | chosen runtime (on-device or bounded service) | `speech.capture`, `speech.transcribe`, `speech.act` |
| Renderer/mixer | PlayCanvas/web + Capacitor Android | `SceneBridge`, `AudioBridge`, billboards, spatial sound |
| Protocol continuity | PURL, SEURL, ACSP | signed/authorized typed operation and replay references |
| Unreal lane | master Godpack unchanged | same scene/media/world protocols when built on compatible machine |

## 2. Real integrated acceptance tasks

1. **TTS acquisition, verified:** retrieve and load at least one actual voice, synthesize/encode 10 distinct utterances, save bytes+hash+timing; for at least two distinct voices provide measured samples. Include Arabic-Jordanian candidate test or report its actual failure.
2. **Oracle workload:** on actual reported 2-vCPU ARM64 node benchmark pre-generation queue 1 vs 2, RAM/disk/latency, unaffected PURL/Ollama/PostgreSQL service health; if not connected, report BLOCKED not passed.
3. **Tiny-LM experiment:** optional 135M and 360M grammar-grounded paraphrasing on 30 held-out lines. Compare grammar/refusal/canonical fact preservation and warm latency to deterministic template. Never require the LLM for playable speech.
4. **Player voice:** explicit permission, mic-on button, push-to-talk; real ASR to deterministic intent + graceful unknown/ambiguous; test English and Arabic. Physical microphone unavailable → unit pass + hardware BLOCKED.
5. **Aural city:** at least 3 real positional speaking NPCs and naturally overheard dialogue, three-dimensional attenuation/occlusion and lip/gesture synchronization where models support it.
6. **Predictive gate:** player approaches/retreats/changes routes: selected resource predictions prefetch, far assets canceled, no fabricated world events and no premature NPC engagement. Trace actual network requests and cache bytes.
7. **Billboard:** true nontrivial computation trace from authorized world event, correctly rendered as emissive close-range readable material, not placeholder text.
8. **Rendezvous haven:** precomputed report is read by NPCs who actually have relevant event knowledge, entered via world walk, and persists across rejoin.
9. **Mission first 15 minutes:** world playable without player obligation, organically discoverable hints, optional voice/tap interaction, one real generated mission opportunity without arbitrary mission-count ceiling.
10. **Android/web cross-session:** verify cached clip reuse, process kill/resume, no audio loops, same authoritative world record, background audio focus and device power stress.
11. **Visuals unchanged:** high fidelity source-art pipeline V2 still has its independent visual gates; this new rider cannot substitute TTS/billboards for actual 3D quality.
12. **Unreal unchanged:** status explicitly separate from Rendezvous browser/APK; never say Unreal cook/render passed when unavailable.

## 3. Quantitative quality targets, not preexisting results

- Cached speech onset target **p95 < 250 ms** after authorized sound activation *where bytes decoded and ready locally*; uncached network audio measured separately with no hard invented speed claim.
- Render/audio fixed-step drift, camera audio-listener orientation, p95 audio queue underruns and sound pops; report quantitative event trace and human headphone listening results.
- Sound masking: NPC side conversation intelligible at natural distances and drops with occlusion; no hard clipping or continuous gratuitous loudness escalation.
- Prefetch: measured true-positive/false-positive, bytes of wasted downloads, p50/p95 time-to-ready, cache hit %, event-activation correctness and memory ceiling on Samsung-class tier.
- Grammar: valid branches 100% pass declared predicates in fixtures; invalid branches rejected with typed diagnostics; property/fuzz tests with reproducible seeds; `prepare` never changes committed world event count.
- Report held-out evidence: not just deterministic toy fixtures, but in real rendered scene with mixed voices, variable walks, weather, misspoken requests, ASR errors and unpredictable NPC movements.
- First actual launch: website/Android opens, controls move, ambience already audible after entry gesture, nearby NPCs converse, footsteps/speech pan in 3D, one event leads to new voice pack, billboard shows a real program, user exits/returns without duplication.

## 4. Build evidence and report

Include version/commit, CPU/GPU/device, installed model IDs and hashes, speech codec and phoneme inputs, audio artifact hashes, prompt/utterance comparisons, throughput/p95 latency, memory/energy/bandwidth cost, logs for cache gates and failed branches, source and produced APK/web build artifact checksums. Measure through actual `AudioContext`, decoded audio assets, and Android/WebView supported runtime. Mark every not-executed test BLOCKED. Keep visual/mathematical measurement programs separate from per-frame serving workloads.

The accompanying `prototype/` tests only the pure planning and commit distinction, **not this integrated acceptance matrix**.
