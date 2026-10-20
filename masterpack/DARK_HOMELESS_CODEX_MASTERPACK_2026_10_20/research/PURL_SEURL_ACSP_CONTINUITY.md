# PURL + SEURL + SUBSTRATEIO + ACSP — COMPUTABLE LOCAL PROTOCOL SUBSTRATE

**Goal:** every meaningful game computation and discovery can be addressed, interpreted, certified, resumed and transferred without requiring an internet HTTP endpoint for operations staying on one computer. PURL means **Programmable URL**; its address may be both expression and reference. SEURL supplies typed protocol/verb interfaces; ACSP maintains continuity through explicitly stored handoffs. SubstrateIO is the observation-and-history dimension of transitions, not an ordinary input/output acronym. Do not rename PURL.

## A. Address grammar and semantics

`ProgramRef = (scheme, version, domain, grammar-id, operator-expression, operand-bindings, context-id, history-policy, effects, scope, digest)`.

Define resolution as `Resolve(u; E,H,D,A,R)` where `u` is address/program, `E` environment, `H` history and state, `D` versioned data, `A` authorization, `R` runtime. Same address can denote different outcomes when declared context differs; same address + same pinned context must replay identically within numerical policy. A bare cryptographic hash gives identity/integrity, not automatic inverse reconstruction; a self-describing program requires an explicit decodable opcode representation or an available content-addressed object.

### Example proposed PURLs (syntax to reconcile with actual repo)

- `purl://dark/earth/tiles/{quadkey}@data-rev` — address for geospatial cell and data source signatures.
- `purl://dark/actor/{uuid}/memory?depth=chain` — read authoritative consent-filtered memory.
- `purl://dark/scene/{scene-id}/resolve?epoch={time}` — resolve spatial design instructions.
- `purl://dark/journey/{journey-id}/program` — typed walk program with unfold/witness.
- `purl://dark/sky/discovery/{pattern-id}/proof` — geometric constellation-like discovery certificate.
- `purl://dark/audio/{event-id}/motif` — audio graph program and measured cues.
- `purl://dark/code/{object-id}/inspect` — read-only provenance and program grammar.

Propose side effects only via clearly separated verbs (e.g. `commit`, `adopt`, `invoke`) carrying a valid local capability and deterministic event ID. Never permit a read-only request to mutate the state. An operation compiled from a player's walk isn't directly a file-system command; it is a typed instruction graph lowered to permitted runtime abilities.

## B. SEURL typed local subsystem protocols

SEURL is a proposed typed programmable scheme family; inspect `akadaan310/seurl` for actual verb names/semantics before choosing wire syntax. Example **provisional**, not deployed endpoints:

- `seurl+audio://...` : sound graph, emit, spatialize, duck, mix, render.
- `seurl+animation://...` : actor gait, rig pose, anticipation, gesture.
- `seurl+physics://...` : simulate, integrate, query collision, constraint verdict.
- `seurl+world://...` : georeference, stream tile, route query, camera chart.
- `seurl+sky://...` : epoch positions, pattern discovery, render overlay.
- `seurl+weather://...` : field, turbulence, wetness, computed local perturbation.
- `seurl+model://...` : define grammar/model, compile, evaluate, verify.
- `seurl+math://...` : submit reference solve, fetch witness, run bounded native solution.
- `seurl+shell://...` : inspect script, run *approved* command, read structured stdout/stderr/exit.
- `seurl+continuity://...` : handoff, checkpoint, restore, compare committed histories.

Every protocol publishes a typed manifest: operation names, input/output schemas, resource budgets, effect types, permission scopes, clock domain, error codes, replay contract, conformance tests and event provenance. The actual wire transport is orthogonal to the scheme syntax; do not assume arbitrary custom URI schemes run through `curl` without a registered scheme adapter.

## C. ACSP continuity tunnels, zero mandatory HTTP dependence

**Local-first topology:** UE process ↔ local native engine daemon ↔ IPC bus ↔ sandboxed shell/JS/Wasm worker ↔ local append-only store. Choose platform-appropriate **Unix-domain sockets** on Linux/macOS/Android, **named pipes/AF_UNIX** on supported Windows, shared memory ring buffers for approved high-rate telemetry, and in-process channels where possible. Use Cap'n Proto, Protobuf or CBOR with versioned envelopes; select one coherent wire format and implement conformance tests. No web server, HTTP route or internet needed for host-local exchange.

**Across devices:** an authorized tunnel/gateway can forward *the same typed envelopes* over an authenticated encrypted connection (e.g. QUIC or a WebRTC data channel), but that transport is separate from the semantic protocol. This is particularly important for the Android streaming companion communicating with remote world runtime. The *local* tunnel is intentionally not HTTPS-based; remote user authentication/session integrity must still be proven and monitored. Transport and encryption details are engineering choices, not program semantics.

**ACSP envelope:** `{protocol:'acsp', version, session, actor, event_id, clock:{wall_utc,monotonic,world_tick,sky_epoch}, source_revision, predecessor_hash, payload_kind, payload, capability_ref, signature?}`. Envelopes support `HELLO`, `DISCOVER`, `OPEN`, `SNAPSHOT`, `APPEND`, `RESUME`, `ACK`, `REPLAY`, `VERIFY`, `CLOSE`, `CONFLICT`. `ACK` only after durable append, retries idempotent by event ID. Clock skew and causality are different: monotonic tick for local order, UTC/TAI-like epoch for historical sky, lamport/vector/hybrid-logical clocks for distributed events as warranted; define chosen rules explicitly.

**Continuity correctness:** restart the shell worker, daemon, renderer, player app and entire device individually. For each restart, authoritative world state and journal resume from last durable accepted event; duplicate events deduplicate; dropped messages retransmit; divergent branches reconcile via explicit conflict policy rather than overwriting. Validate checksum, state hash, actor authorization and historical depth.

## D. SubstrateIO observables and promoted operations

Keep log at defined levels `semantic-operation`, `IR-compile`, `runtime-step`, `simulation-tick`, `source-revision`, `visual/audio-projection`, not at an imaginary omniscient bit-level trace. Each observer declares sampling and what information was lost. State-identity, holonomy identity and full-chain identity may differ. A repeating path only becomes a promoted capability when reproducibly *unfoldable*, typed, useful and admitted under its declared grammar. The engine's runtime capabilities are versioned independently from NPC cosmetic authored content.

### Billboard shell projection example

A player's plaza route becomes a typed `walk{turn,L,R,edgeClass}` record. The capability engine recognizes a graph signature and logs a `constellatable` candidate. In the scene, a billboard may show a real serialized representation:

```
$ darkctl journey inspect purl://dark/journey/j-204/program
signature: L4.S3.R4
match: cand-221 [two observed source charts]
$ darkctl sky validate cand-221
status: pattern-certified / context: sky-epoch-...
$ darkctl journal checkpoint
commit: sha256:...
```

This should be produced from actual engine results, with actual IDs/certificates, not randomized terminal gibberish. Billboard presentation does not grant a player a full interactive system shell.

## E. Deterministic data and runtime registers

Store program ASTs, fold/unfold definitions, content digests, data revisions, compiler versions, numeric policies and related sources. A local repository (SQLite, RocksDB or durable event store) supports snapshot, Merkle history, deduplicated program blobs, journal replay and capability grants. Long-running distributed state may need a shared backend; local continuity requires no central cloud dependence.

## F. Acceptance tests

1. Read-only resolve has no side effects; malformed scheme/grammar yields typed error.
2. Local ACSP IPC roundtrip works **without any HTTP service running**.
3. Streamed remote gateway can be disconnected without corrupting source ledger.
4. Stop/start game and renderer, resume last committed state and player journey.
5. Same source address with different pinned contexts yields different *declared* results; identical pinned context replays.
6. Unknown capability rejects effect; no arbitrary host file/write/network calls from billboard or NPC event scripts.
7. Promoted walking/sound macro unfolds to original accepted typed trace.
8. Local command execution demonstrates `curl`-style use through approved client transport and a separate protocol dispatcher; no false claim that stock `curl` speaks arbitrary `purl://` schemes.

**Historical sources to inspect:** https://github.com/akadaan310/purl ; https://github.com/akadaan310/seurl ; https://github.com/akadaan310/substrateIO ; https://github.com/akadaan310/snad ; `inputs/` legacy research assets.
