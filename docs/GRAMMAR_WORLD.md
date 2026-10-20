# Grammar, society and predictive media

`worldloom/grammar.py` generates four executable symbolic grammar candidates: connected walk paths, bounded audio gestures, fictional shop signs, and `RENDEZVOUS_HAVEN` evidence reports. `GrammarFactory.build()` instantiates a typed subject schema, selects a bounded grammar form, binds its interpreter, and runs positive, negative and separate held-out fixtures. Its certificate records the result and fixture digest. This is template-based grammar synthesis, not general induction of arbitrary languages or a proved new mathematical result.

```python
from worldloom.grammar import GrammarFactory, compile_program, Grammatical

grammar = GrammarFactory().build('walk')
compiled = compile_program('walk', 'walk a b c',
                           {'graph': {'a': ['b'], 'b': ['c']}})
assert compiled['valid']
assert Grammatical(compiled).expand() == compiled['program']
trace = Grammatical(compiled).run()
assert trace['effect_policy'] == 'propose-only'
```

Programs pin their grammar revision and context hash. The evaluator rechecks the parse, effect declarations, address, fold and witness before running. It produces actual typed movement steps, audio cue parameters, sign proposals or meeting-report proposals. It does not commit authoritative world effects. Ingram's original `KN3.fit/logprob` ranks usage independently from validity. Its original `Tower.fit/implicate/explicate/address/unaddress/from_json` supplies tested invertible folds, including Unicode. The original modules are imported by file under isolated names; historical files are unchanged. The rare balloon gesture is valid only when the declared event and geometry permit it. Invalid syntax, wrong types, missing information, semantic impossibility, budget failure and refusal have separate diagnostic codes.

`registry()` declares all 21 required model families and their alphabets, grammars, usage priors, contexts, transitions, observers, verifiers, budgets and capability interfaces. Each entry describes its implemented reference adapter or explicitly identifies an external adapter requirement. A registry entry alone is not a claim of cinematic rendering, production astrophysical accuracy or measured physical outcomes.

`worldloom/society.py` exports `World(seed=7)`, `tick(dt)`, `snapshot()`, `World.from_snapshot(snapshot)` and `dispatch(operation, payload, actor, capabilities=())`. Snapshots contain clocks, stateless keyed RNG identity, active actor records, schedules, typed memory, decisions, independent conversation, event chains, coauthor proposals, delegated membership, journeys and organic mission opportunities. JSON save/restore reproduces subsequent snapshots. IDs span `[0, 8190000000)` lazily; this is a synthetic identifier capacity, not a census or eight billion ticking minds. Twenty-four active NPCs tick; the remainder are declared aggregate background cohorts.

The source-confirmed Tampa origin is the midpoint of OSM junction nodes `2057042478` and `1603574189`, at `27.95946425, -82.5055696`. Active walkers interpolate a sourced pedestrian route from `worldloom.geo.route`. A hash-pinned compiled route in `evidence/grammar_world_navigation.json` avoids solving the route at daemon startup. Locomotion is synthetic and lacks a dynamic crowd collision solver. Geographic geometry, flat artistic terrain and fictional storefront names retain separate evidence labels. Marina del Rey is founder biography metadata, independent of the Tampa arrival. The founder's direct self-identification, `Abed Kadan`, is canonical; `Abed Kadaan` also appears in supplied riders and is retained as source-spelling metadata. A name field does not establish authentication.

The original REALMS `ActivityModel.schedule/check` executes through an optional adapter; a declared standard-library schedule remains available when numpy is absent. The adapter also executes `EventModel`, `society.impact` and exact `society.shapley` on small bounded fixtures. Those are modeled counterfactual witnesses on a declared synthetic graph, not measurements of real social causation. Every routine decision enumerates feasible actions and utilities, names its solver and seed, records constraints and a lexicographic tie-break, and hashes its witness. Ride negotiation can decline for time, compatibility, trust or seats; a separate enumerated coordination fixture has two pure Nash equilibria with explicit selection rules.

Observation requires local voice reach and an explicit unobstructed channel. Direct observations have typed scope, confidence and seven-day retention; actor memory keeps the latest 64 observations. Events outside reach remain unknown. NPC teaching, refusal, non-notice and sky-cue response are distinct tested outcomes. The finite English/Arabic intent grammar returns an in-world clarification for uncertain or unsupported text. A transcript cannot invoke a host command. The recognizer is not an ASR engine; microphone capture and actual transcription are separate voice-layer capabilities.

Founder names do not grant authority. `cohort.invite/delegate/revoke` require a verified `founder` capability supplied by WorldSession. Joining requires the invited actor's own acceptance; roles have expiry and cannot contain founder or shell powers. Shop-sign coauthor proposals preserve source grammar, author, consenting collaborators, endorsements, declines, prior revision, adoption event and unfold witness. Founder adoption is explicit and reversible. Mission opportunities derive from world evidence and use finite per-query plan budgets without a fixed lifetime mission-count ceiling.

`worldloom/bootstrap.py` provides the general-purpose `BootstrapScheduler`:

```python
scheduler.plan(snapshot, candidates, resources, now=world_time)
scheduler.prepare(resource_id, actual_bytes)
scheduler.activate(gate_id, snapshot, actual_distance_m=2,
                   authority=['scene.activate'], consent=True, now=world_time)
scheduler.cancel(gate_id)
scheduler.status()
scheduler.evict(target_bytes)
```

Candidate gates declare a kind, source actor, pinned world revision, geometry/ETA, horizon, authority, resource manifest, expiry and effect. All 14 V3 gate kinds share the same scheduler. Stationary distant actors do not predict movement unless explicit scheduled anticipation exists. Stale, unreachable, private, expired and low-priority low-battery candidates are rejected. A deterministic greedy baseline selects deduplicated resources under independent bandwidth, decode and resident-memory budgets; it does not claim a global knapsack optimum. Planning is bounded to 256 candidates and 1024 resource declarations per invocation.

Preparation verifies real byte length and SHA-256, then atomically reserves a gate only after its entire manifest is available. Changed checksums invalidate reservations. Retreat cancels a prediction while retaining reusable cache bytes. Predicted, fetched, played, ignored and canceled facts are distinct cache telemetry. Planning/preparing never append a world event; activation returns a proposal requiring current revision, actual proximity, consent and typed authority. WorldSession performs the durable commit. GPU decoding/timing is not claimed deterministic. Cache bytes are disposable on process restart; committed world memory survives through WorldSession.

`WorldSession._gate` uses this scheduler, the actual voice catalog and the actual source-asset registry. It matches speech by exact text or phrase ID and preserves embedded animation in its real GLB container. It prepares conversation, asset-cell, vehicle-entry, haven-report and billboard candidates using directional approach and current world state. The billboard and haven resources contain actual computed ledger/world records; the report lists each NPC's observed evidence. It returns immutable resource IDs, URLs, hashes and cost metadata to browser/Android clients; preparation validates trusted server catalog files. Oversized assets remain outside the declared phone budget. Texture/geometry memory and decode costs are estimates pending device measurements. Client decode and actual spatial playback still require renderer evidence. Three autonomous café speakers are present before player entry, and their spoken acts enter world history independently of player interaction.

The fresh targeted suite passes 32 tests (9 grammar, 13 society, 10 bootstrap). Unchanged historical suites pass 19 Ingram and 16 REALMS tests; the supplied rider reference kernel passes 17. `grammar_world_gate_integration.json` records actual speech/animated-GLB/report preparation, approach/retreat cancellation, local CPU/wall measurements and unchanged committed-event count. These are server-side cache measurements, not phone decoding or network-playback results. Root integration owns the definitive full-repository verification while other artifacts are changing.

Executed evidence resides in `evidence/grammar_world_*.log` and `evidence/grammar_world_report.json`. Historical REALMS and Ingram suites execute unchanged. The V3 reference prototype suite is evidence for the supplied kernel only. Unit tests establish typed behavior, replay and cache separation; they do not establish headphone quality, physical microphone operation, Oracle ARM performance, Samsung frame rate or Unreal rendering.
