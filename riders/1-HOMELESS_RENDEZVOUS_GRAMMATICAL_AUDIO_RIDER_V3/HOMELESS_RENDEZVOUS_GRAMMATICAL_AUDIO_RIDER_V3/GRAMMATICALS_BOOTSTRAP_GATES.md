# GRAMMATICALS & RENDEZVOUS BOOTSTRAP GATES — engineering specification

## 0. Authoritative inheritance

Add this as a new producer/consumer substrate between existing `WorldSession`, World Loom / REALMS model families, In-Grammar / Tashkīl / Plicastratum / BORNE / Octave reference mathematics / PURL-SEURL-ACSP and the Rendezvous renderer/asset/audio layers. **Do not fork world authority into the renderer.** The original Unreal commission and Rendezvous V1 / Asset Fidelity V2 remain intact. This rider adds **predictive media preparation and grammar-grounded scene production**, not an alternative game or an alternative renderer.

## 1. Core definitions [construction]

**Grammatical** is a versioned runnable grammar-backed form

`Γ = (alphabet, typed_context, grammar, denotation, transition, admissibility, effects, observable, witness, identity_depth, budget)`.

A grammatical represents a runnable computation only if: parse/typecheck succeeds; interpretation has an implementation; inputs and effects are bounded; explicit external dependencies are resolved; and required witness/tests pass. A *grammatical* can be a dialogue act, NPC policy step, conversation episode, media transition, walking program, billboard program, storylet, scene, mission, scene transition, or prefetch predicate. The suffix *-able* denotes a verified predicate (`preparable`, `runnable`, `audible`, `renderable`, `replayable`, `reversible`, `cancelable`, `publishable`). Promotion into a reusable higher-alphabet letter requires signature, expand/unfold path, proof/witness and recorded provenance. Do not call an uncaptured and uncoded pattern runnable.

**Grammar Factory** (proposed `Grammatica Generatrix`) synthesizes domain grammars from typed alphabets, admissibility constraints, invariant templates, examples and counterexamples. It may search/select grammar forms (DFA, PEG/CFG, attribute grammar, graph grammar, typed effect system, statechart, temporal logic) according to the problem. Required outputs: explicit grammar definition, consistency diagnostics, the accepted language and known limitations, positive/negative fixtures, derivation trace, versioned executable evaluator, and conformance certificate. In-Grammar supplies *rankings conditioned on context* among admitted continuations; optionally selected neural estimators are not authoritative.

**Anti-grammar/In-Grammar distinction:** `anti(G)` can mean complement of a declared language relative to a declared universe, whereas In-Grammar ranks/usefully handles atypical but admissible expressions. Invalid syntax, unusual usage, missing information, and intentionally transgressive fictional behavior must not silently collapse into the same category. Each rejection has a typed diagnostic.

**Rendezvous Bootstrap Gate (RBG)** is a predicate over versioned world/actor state and a possible future event that prepares resources before the actual event is committed. Its pipeline is:

`OBSERVE -> PREDICT -> ADMIT -> STAGE -> VERIFY -> RESERVE -> ACTIVATE (optional) -> RETIRE`

`CANCEL` and `EXPIRE` are possible before activation. A speculative event cannot mutate the authoritative world merely by entering STAGE.

**Preparation Gate** downloads/transcodes/decodes near-future media. **Activation Gate** commits a verified gameplay effect only when real scene, participant and player/world preconditions hold. **Promotion Gate** turns a repeatedly successful pattern into a certified higher-level grammatical with its unfolding witness; not the same as an activation event.

## 2. Formal scheduler

For snapshot S at time t, modeled candidate event e and resource r:

`p_e = Admit_G(e,S) * Utility_I(e|S) * Need(e,S)`, where `Admit_G` is 0 or 1 and non-model `Utility_I` may be an integer policy score; it is *not* a claim of true human-behavior probability.

`ETA(e) = expected path distance / max(reliable speed, epsilon)` adjusted by path/navigation feasibility, known pauses, vehicle mode, and stale-data penalty. If speed is near zero, event may be staged only by an explicitly scheduled/near-visible anticipation rule. Rank every resource using priority, urgency, reuse probability and time-to-use under the **measured** bandwidth/CPU/storage budget.

Choose staged resources solving a bounded knapsack-like problem:

`maximize Σ value_r x_r` subject to `Σ bytes_r x_r <= byte_budget`, `Σ decode_ms_r x_r <= decode_budget`, per-device memory budgets, privacy/authorization and network reliability. `x_r in {0,1}`. A fast deterministic greedy baseline is sufficient initially; Octave or bounded optimization can provide an oracle/reference on small fixtures. Do not claim greedy is globally optimal for arbitrary budgets.

**Plan changes** are versioned; obsolete resources are cancelable and cacheable; a cached asset may be useful after the prediction changes. Evict based on policy, not world-state meaning. Resource hashes and decoder-version hashes are independent of actor identity and player identity.

## 3. Mandatory scenario: off-axis overhearing in Tampa

As Dark walks toward a fictional café at North Dale Mabry × West Spruce, his sight cone includes a shopfront while another NPC pair is having their own conversation. Their **conversational grammatical** has acts independent of Dark's arrival; a chance to overhear is generated by geometric audibility, dialogue context, occlusion and their relationship state. The predicted **preparables** are already voiced on Oracle and stored in the audio cache. Audio is reserved with a short lead time; sound level and spectral occlusion change as Dark turns toward them. The NPCs never have to address him. If he speaks, an ASR pipeline proposes a dialogue act; the world grammar validates it, and the NPC can continue, redirect or refuse according to its own state. If Dark walks away, prefetched data expires without forcing an encounter. Log `predicted`, `fetched`, `played`, `ignored`, `canceled` as distinct facts.

## 4. Scene/mission/bootstrap intersections

Gate kinds (typed, extendable): `NPC_LINE`, `CONVERSATION_EPISODE`, `WHISPERED_HINT`, `EVENT_SCENE`, `MISSION_OPPORTUNITY`, `RENDEZVOUS_HAVEN`, `BILLBOARD_PROGRAM`, `MUSIC_CUE`, `VEHICLE_ENTRY`, `AIRCRAFT_APPROACH`, `ASSET_CELL`, `PORTAL_CORRESPONDENCE`, `WEATHER_FIELD`, `SHELL_VISUAL`.

The gate recognizes a *possible next state* with supporting condition; it must never assert that a possible branch already occurred. Each gate declares `kind, sourceActor, candidateStateRevision, worldCell, horizonSeconds, preconditions, authority, resourceSet, byteBudget, computeBudget, effectPolicy, checksum, expiry, evaluationTrace`. An external NPC's plans and private information cannot be exposed through hints that the world does not authorize Dark to know.

**Recurring speech** should be a **small number of high-fidelity assets** shared across combinatorial contexts. Use stable phrase IDs and speaker/voice variants. For personalized variations, the grammar picks an existing variant or queues background TTS; if unavailable in time, synthesize on the designated worker if measured capable, or use a grounded text/gesture fallback, never interrupt gameplay waiting synchronously for an LLM.

## 5. Committed state and cross-run continuity

`resource.prepare` is not a world-effect event. `event.activate` happens only through `WorldSession` with validated preconditions and authoritative event ledger. Identical canonical input plus versioned grammar/policy and identical world snapshot produces the same planning output; GPU rendering and codec timing are *not* assumed bit-deterministic. Reconnect restores already committed acts and relevant media-playback state but does not replay dialogue the player already heard unless appropriate.

PURL exposes parseable version-pinned resource/program identities; SEURL denotes typed channels (e.g. `seurl+audio`, `seurl+dialog`, `seurl+event`, `seurl+billboard`); local ACSP maintains engine/worker continuity through local IPC where available. No new privileges by inventing a URI. Writes go through typed, authorized effect declarations. On a phone, network fetches are through the existing authenticated web transport and cache; local Unix-domain sockets are used only between processes capable of IPC, not as a universal replacement for phone-to-cloud networking.

## 6. Resource acquisition and testing contracts

- Reuse the asset master registry from V2. One gate may stage audio, GLB, textures, animation, billboard program, and audio convolution/occlusion parameters as an atomic manifest; each asset is independently cacheable.
- Priority bands: `A` guaranteed soon for the currently observed actor; `B` plausible near future; `C` opportunistic long tail. Do not exhaust phone bandwidth for distant alternate branches while near-field assets need it.
- Explicit cache keys for TTS include normalized text, language, exact model and voice revision, pronunciation/phoneme lexicon, prosody tags, sample rate and output codec. A cache hit must still have valid audio bytes and content hash.
- Graceful degraded operation under network loss, 3% battery, and background/reconnect scenarios: preserve control/camera and existing ambient bed; reduce lookahead downloads before interrupting world state.
- The initial scene must already contain active ambient events before the arrival cinematic, and a nearby conversation must be audible without Dark interacting; preloading is observable through trace and actual audio playback.

## 7. Evidence status

All formal objects and names in this document are newly **proposed constructions**, not proved new mathematical theorems. The baseline graph/grammar/prefetch/cache techniques are established families. Novel integration and measured outcomes must be earned by tests. Every optimizable or 'infinite' claim must identify the finite per-frame work budget and composition rules. The engine may generate indefinitely many distinct sequences over time; that does not imply infinite storage or unbounded instantaneous compute.
