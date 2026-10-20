# GRAMMAR GENERATOR + ACTUAL EMBEDDED SHELL ENGINE

This is a critical requirement, not decorative ideation. An executable shell-like environment must be present in the game infrastructure and callable through typed local protocol, but arbitrary player/NPC speech must never become unrestricted host operating-system commands. The shell is a computational adapter; a rendered terminal display is merely an optional projection.

## 1. Theory of grammar: grammar-generating grammars (GGM)

Define a domain grammar as `G=(Σ,Sorts,Productions,Context,Semantics,Admissibility,Costs,Observable,Examples,Verifier)`. Define a **metagrammar** `M` that generates well-typed candidates `G_i` from a subject schema and examples, rather than merely generating text with a fixed grammar. This is the new **Grammar Generating Model (GGM)**, or *Grammatica Generatrix* as proposed Neo-Latin title.

Inputs: sample actions, domain constraints, types, conventions, corpus evidence, observed counterexamples, vocabulary and declared semantic operations. Outputs: versioned typed grammar, rejected counterexamples, executable parser/transducer, meaning-preservation checks, resource-bounded generation and a held-out validation report.

Formal shape:

`CandidateGrammars = M(subject, ontology, examples, constraints, anti_patterns)`
`Certify(G) = ParseRoundtrip ∧ TypeSafety ∧ AdmissibilityCoverage ∧ CounterexampleTests ∧ Budget ∧ Provenance`
`Promote(G) = if Certify(G) then AddVersionedAlphabet(G) else RecordFailure(G)`

**In-Grammar** is not the logical complement of grammar: usage-prior `I(word|context)` differs from the language complement `¬L(G)`. Keep distinct: (a) syntactically invalid, (b) semantically impossible, (c) unusual but legitimate, (d) probabilistically rare, (e) incompletely observed, (f) intentionally invented, (g) missing and (h) underdetermined. Need an explicit diagnosis code; human dialects and informal speech are not automatically invalid.

Model contracts extend `FOUNDATIONS.md` P1–P9: alphabets-of-alphabets, definitional graph, glossaries, grammar × usage, charted projections, discourse acts, history, addressable computation and arithmetic admissibility. CGT provides signature/semantics/cost; Plicastratum supplies fold/unfold, retial words and strata. A GGM's output itself becomes an operable typed alphabet.

Train optional *offline* corpus-authoring agents with Claude/Codex/ChatGPT to propose glossaries, ontologies and sentence pattern dictionaries; accepting into runtime requires held-out tests and authoring history. Actual in-game generation defaults to tiny symbolic, n-gram, finite state, weighted automata, graph rewriting and bounded probabilistic models. If a generator is too expensive, use cache/fallback without silently fabricating a new grammar.

## 2. Executable runtime split

**A. Native game API:** Unreal calls typed `WGM` operations; no process spawn on game thread.

**B. Small script evaluation:** **QuickJS** (https://bellard.org/quickjs/) for deterministic JavaScript scripts with host callback bindings; runtime memory/time/op budget, no arbitrary native system bindings. Scripts can compose score, geometry, signage, camera and sound programs.

**C. Embedded cross-language components:** **WAMR** (https://github.com/wasm-micro-runtime/wasm-micro-runtime) for compact Wasm/WASI-style modules where Android portability matters; **Wasmtime** (https://docs.wasmtime.dev/) for server worker implementation, with the Component Model and explicit capabilities. Support Python-like scripts via a compatible module or worker where useful, not by dragging a full desktop Python distribution into every APK.

**D. Real shell execution on isolated host worker:** **BusyBox ash** or similar free-standing POSIX shell, running as a separate bounded local process/container with explicitly provisioned `darkctl` and a curated command set. It supports proper pipes, quoting, redirections to a private workdir, process exit codes, virtual clocks and tool invocation. Do not accidentally expose arbitrary host environment, inherited environment secrets or unrestricted destructive commands. The shell worker can emit structured results back into ACSP and `seurl+shell`.

**E. Curl-style operations:** `curl` is a CLI implementation of particular transport protocols; embed **libcurl** on the isolated service for supported conventional requests and a *custom local URI dispatcher* for `purl://` and `seurl+*://`. A line such as `darkctl purl inspect ... | jq ...` works locally without HTTP; actual `curl` against a conventional URL uses its supported protocol. Do not pretend that implementing a URL grammar automatically registers a new libcurl protocol. All remote fetches pass allowlisted endpoint categories, resource limits and structured error handling.

**F. Storage:** local SQLite event store, content-addressed objects and named actor repositories. Shell scripts can propose typed state mutations; the simulator commits only after schema validation, event preconditions and authority checks. Neither stdout nor generated strings constitute a valid game state update.

## 3. Clock and timer architecture

Four clocks: `monotonic_engine_tick`, `real_UTC`, `world_epoch` (may simulate historical/future time), `presentation_clock` (interpolated camera/audio). Distinguish `dt` in render, audio buffer, physics substep, NPC schedule and network packet. Local shell command `darkctl time` returns a structured cross-clock snapshot, and `darkctl sleep --ticks N` is virtual scheduling, not an OS sleep that blocks gameplay.

Use deterministic fixed physics timestep (e.g. 60Hz with bounded accumulation), saved RNG stream positions, monotonic logical event numbers, type-tagged date representations and clock-skew telemetry; restore/replay must state which clock and epoch is driving astronomy and weather.

## 4. Example shell-to-game operation

```
# Worker shell, not an Android-user terminal
$ darkctl world query --cell=<id> --mode=read > /work/cell.json
$ darkctl gram compile --subject=walk --in=/work/walk.json --out=/work/walk.program
$ darkctl gram check --program=/work/walk.program
$ darkctl session checkpoint --actor=<authorized-actor>
```

`darkctl` is an engine adapter CLI the agent must implement. Every command emits machine-readable JSON with `request_id`, `command`, `exit`, `output_digest`, `elapsed_tick`, `effects_proposed`, `effects_committed`. Unsupported flags return nonzero status with reason. Install actual sample shell scripts and integration tests, not only an ASCII diagram.

## 5. Capability and execution separation

Actors may produce programs in a constrained language (walk grammar, audio grammar, asset arrangement); only verified compilers turn those into the small set of permitted world effects. Distinct privilege tiers: game simulation agent, NPC, player creative-script object, founder/operator, offline build agent. Public creative scripts cannot spawn privileged host commands or allocate unlimited CPU. Use Wasm fuel/time/memory budget, worker restart, bounded stdout/stderr, parse limits, append-only provenance and deterministic replay snapshots.

For user-facing billboard terminal: choose recorded allowed commands, reveal actual path signatures, event ID and compile steps. When the player walks away, only the screen stream disappears; the computational event remains anchored in history.

## 6. Concrete acceptance

- Launch and run BusyBox-style shell worker; verify pipe, file sandbox redirection, exit status and timeout behavior.
- Run a QuickJS world program and a WAMR/Wasmtime component with typed inputs; reject unauthorized host imports; enforce resource budgets.
- Execute `darkctl` in a shell with typed PURL/SEURL; check that output creates an audit event but does not commit state until admitted.
- Kill/restart workers in the middle of a job and confirm idempotent ACSP replay and durable commit state.
- GGM constructs **three distinct runnable grammars**: walk, audio gesture and shop-sign naming, each with parser, positive and negative fixtures, held-out validation and composable program addresses.
- Test a *rare but legitimate* anti-pattern (balloon audience) passes when event/geometry permit it; reject logically invalid spatial arrangements with diagnostics.

Source refs: https://docs.wasmtime.dev/introduction.html ; https://github.com/wasm-micro-runtime/wasm-micro-runtime ; https://bellard.org/quickjs/ ; https://curl.se/libcurl/ ; historical `FOUNDATIONS.md` P4/P8 and Plicastratum `-able` tests.
