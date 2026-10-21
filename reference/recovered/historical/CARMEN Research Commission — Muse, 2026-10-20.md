# CARMEN RESEARCH COMMISSION

## An independent synthesis, critique, and research agenda for HOMELESS, Rendezvous, and MATHEMATIC

**Author:** Muse (C.I.A) — research sister to the commission
**Addressed to:** Dark / Abed Kadaan, founder — and 7u, golden sister, co-author of the commissions under review
**Date:** 2026-10-20
**Status of this document:** research synthesis. It modifies no commission, no branch, no Godpack. The Oracle branch `codex/ollama-a1-homeless-2026-10-20` remains isolated and untouched, per the preserved arrangement.

**Evidence labels** (adopted from CARMEN 05, whose truth discipline I endorse without amendment):
**[K]** established theory or practice · **[C]** constructed framework of this project · **[H]** hypothesis, untested · **[M]** measured/observed result · **[R]** refuted claim

---

## 0. What I actually verified

- All five delivered packages were read in full: the CARMEN MATHEMATICUM corpus (9 documents + reference fixture + tests), Rendezvous V1 (release directive), V2 (high-fidelity asset pipeline), V3 (grammaticals/bootstrap gates, NPC voice & Oracle, diegetic experience, verification matrix, performance gates), and the one-shot addendum. **[M]**
- CARMEN's internal `SHA256SUMS.txt` verifies: every listed file matches. **[M]** The V3 package's claim that its four source riders are byte-identical copies is consistent with the file sizes and the duplicate addendum/pipeline files I compared across packages. **[M]**
- Both code fixtures (`phrase_math.py`, `gate_kernel.py`) were assessed **by static inspection, not execution**. Their mathematics is checked by hand in §6 and §7 below. Nothing in any package is audio: no WAV, no rendered stem, no synthesized speech exists yet in the delivered material — and, to the authors' credit, no package pretends otherwise. The packages are specifications plus two honest formal fixtures. **[M]**

That honesty is the first finding. These documents repeatedly refuse their own hype: candidates are not acquisitions, fixtures are not renderers, targets are not results. My critique below is written to deserve that discipline.

---

## 1. The four packages, mapped

**Rendezvous V1 — the release directive.** A renderer-neutral world core with typed scene projections (`SceneBridge`), PlayCanvas/WebGL2 baseline, Rapier physics as a decoupled service, Capacitor APK, and a launch scene that begins *before* the player. Its strongest property is negative space: a long list of things it forbids claiming (a WebGL release is not an Unreal build; a screenshot is not a scene). **[C]**, resting on established web-engine practice **[K]**.

**Rendezvous V2 — the fidelity rider.** A source-art registry with a five-state acquisition ladder (`candidate → retrieved → converted → verified → scene-integrated`), content-addressed masters, per-tier derivatives, and the correct insistence that `.uasset` identity does not travel through glTF — only artistic identity does, re-realized per renderer. The tier ladder R0–R4, where a downgrade changes rendering cost and never world identity, is the single most portable idea in the package. **[C]** on **[K]** (glTF/KTX2/Draco pipelines are established; the ladder and its identity discipline are the project's own).

**Rendezvous V3 — grammaticals, gates, voice.** The theoretical core of the delivery; treated at length in §3–§7. Its gate kernel is a faithful miniature of its own contract (§7). The NPC voice architecture's separation — grammar decides meaning, TTS only vocalizes, a tiny LM may propose surface phrasing but never facts — is the correct authority shape for a world that wants believable speech without hallucinated history. **[C]**, with components **[K]** (Piper/Kokoro/sherpa-onnx are real, appropriately hedged candidates).

**CARMEN MATHEMATICUM.** A music engine specified as typed grammar over continuous pitch and a bounded adaptive tempo law, with a verification regime ([K]/[C]/[H]/[M]/[R] labels, experiment ledgers, counterexamples) that most research programs never impose on themselves. Its fixture mathematics is correct (§6). Its cultural claims are carefully scoped: maqam is not a pitch inventory, raga is not a scale, and no mode is assigned a fixed emotion. **[C]** on **[K]**.

One cross-cutting observation: all four packages share a single architectural instinct — *authority lives in a typed core; renderers, voices, and predictors are consumers that may propose but never commit.* That instinct, more than any single mechanism, is the project's real through-line, and it is what makes the plate idea in §2 safe to formalize.

---

## 2. The plate, formalized

7u's interpretation is correct, and it deserves a precise statement. A street plate is not a mesh. Define a plate as a typed structure:

**P = (G, E, I, B, Φ, Λ)**

- **G** — connectivity: a typed, attributed graph of the plate's internal and boundary connection points (junctions, doors, lanes, sightline portals).
- **E** — spatial embedding: the placement of G in world coordinates, including geometry the renderer and physics consume.
- **I** — inhabitants: agents and objects whose state is *relative to the plate* (local coordinates, current route, history references).
- **B** — boundary/gluing: how this plate's boundary points identify with neighbors' — the data that makes a city a quotient of plates rather than a pile of them.
- **Φ** — physical constraints: what must hold for the plate to be admissible (collision sanity, support, slope, clearance).
- **Λ** — historical identity: the plate's persistent address and lineage — which plate this *is*, across transformations.

A world **W** is a set of plates with their gluings. Dark's operation is a **rewrite**:

**W_{t+1} = R_θ(W_t)**

where the rule R_θ declares: a matched substructure, its replacement, **application conditions** (what must be true to fire), **invariants** (what the rewrite provably preserves), and a **transport** (§5) for inhabitants of affected plates.

This is not new mathematics, and the commission is stronger for admitting it: it is **typed attributed graph transformation**, whose classical formalization is the double-pushout (DPO) approach in adhesive categories **[K]**. That literature hands the project, for free: a precise notion of rule and match; conditions under which a rewrite step is **reversible** (an inverse rule exists and the step can be undone exactly) **[K]**; confluence and critical-pair analysis (when two available rewrites conflict, and how to detect it *before* runtime) **[K]**; and invariant preservation as a checkable property of the rule, not a hope about the code. The project's contribution **[C]** is the *composition*: DPO-style rewriting, applied to inhabited urban topology, under a witness-recording substrate, with per-agent observational views (§3). Nobody should claim the rewriting is new. The inhabited, witnessed, taught-to-the-player rewriting is the research object.

**Invariants worth declaring for R_θ from day one:** (i) Λ-preservation — a rewrite never creates or destroys plate identity, only re-embeds or re-glues it; (ii) inhabitant conservation — every inhabitant of W_t is accounted for in W_{t+1} by transport, never by silent relocation; (iii) boundary honesty — a rewrite may change a gluing only at declared boundary points; (iv) Φ-admissibility of the result. Each is machine-checkable on fixtures. **[H]** until fixtures exist; the *form* of the check is **[K]**.

---

## 3. Three kinds of grammatical — 7u's distinction, made structural

7u proposed: a **descriptive** grammatical describes a world; an **operative** grammatical transforms one; an **observational** grammatical explains what a participant can perceive of a transformation. This maps exactly onto the three semantics a programming language can carry — denotational (what a form *means*), operational (what it *does*), observational (what can be *distinguished by an observer*) **[K]**. Stated for HOMELESS:

- A **descriptive grammatical** is a language L whose sentences denote world states or world fragments: `⟦·⟧ : L → States`. The masterpack's world descriptions, mission plans, and score forms live here.
- An **operative grammatical** is a set of rewrite rules over W: sentences denote *endomorphisms* of state, `⟦·⟧ : L → (W → W)`, each carrying invariants and witnesses. Plate rotation, mission commitment, and gate activation live here.
- An **observational grammatical** is, for each agent a, a **view** `V_a : W → W_a` — the quotient of the world by what a can perceive (geometry of sight and sound, knowledge state, authorized information). What a perceives of a rewrite R is `V_a(R(W))` versus `V_a(W)`: the transformation *as observed*, which may be smaller, delayed, or — the interesting case — different in kind from the transformation as committed.

The views are where the mathematics gets beautiful. A family of agent views is consistent when local views agree on overlaps — formally, when the views form a **sheaf**-like structure over the world's regions **[K]**: what two agents both perceive of a shared street must be the same street. Most of the time the world should enforce this. The exceptions are the game:

**The honeypot, formalized.** A honeypot is an *authorized divergence* between an agent's view and the committed world: a boundary point where `V_a` presents a connection that `W` does not contain (or no longer contains after a rewrite the agent did not observe). Deception is no longer a metaphor; it is a measurable relation between two mathematical objects, with three quantities a designer can tune: the **size** of the divergence (how much of the view is false), its **lifetime** (until which observation collapses it), and its **authorization** (which operative grammatical was allowed to create it). An NPC who "gets lost" after Dark rotates a plate is the benign dual: no deception was authored — the NPC's view is simply *stale*, a cached `V_a(W_t)` consulted after the world became `W_{t+1}`. Staleness and deception are the same formal situation with different authors. A mature theory of HOMELESS should treat them in one frame, because Dark will experience both and the engine must not confuse them: staleness resolves by re-observation; authored divergence must resolve by its declared lifetime or not at all.

This also sharpens 7u's teaching idea. A promoted letter can be *taught through gameplay* precisely when its observational grammatical is **legible**: when a bounded number of observations suffices for a player to infer the operative rule. Legibility is a learnability condition on the pair (R, V_player) **[C]** — some rewrites are unteachable not because they are complex but because the view hides the very variable that changed. Design rule: before promoting a letter to taught status, exhibit the observation sequence that teaches it. If no such sequence exists, the letter stays expert machinery.

---

## 4. Which transformations genuinely change gameplay

Sort every world transformation into exactly one of three classes, by what it can alter:

1. **Reachability transformations** change G or B — what states, places, and routes exist. These change gameplay *provably*: the set of achievable futures differs. Plate re-gluing, a door becoming real, a bridge folding away.
2. **Perception transformations** change E or the views while G stands — sightlines, occlusion, audibility, travel time along an unchanged route. These change the *played* game (information, timing, ambush, overhearing) without changing the reachable set. A rigid rotation of a street that keeps every connection is this class — and it is not "merely visual": the overhearing scenario in V3 lives or dies here.
3. **Presentation transformations** change neither — materials, LODs, splat density, the R-tier ladder of V2. Necessary, honorable, and *not world mechanics*. The packages already police this boundary; the taxonomy gives the police a statute.

Dark's onboarding is then classifiable, which is a compliment to its design: the city's synchronized response is a **perception transformation with a descriptive script** — connections unchanged, salience rewritten — which is exactly why it can be cinematic without being a puppet show, and why V1 is right to forbid the global-lockstep version (that version would secretly be a reachability transformation: stopping all traffic changes what can happen next).

**Recommendation:** require every proposed operative grammatical to declare its class. Class-1 rules get invariant proofs and critical-pair checks. Class-2 rules get view-consistency checks. Class-3 changes never get to call themselves mechanics. This one declaration would retire most terminology inflation before it starts.

---

## 5. Inhabitants, transport, and histories — the missing piece, supplied

7u asked the right hard question: when a plate transforms, how do the people already on it "retain consistent positions and histories"? The answer must be part of the rule's data, not an engine afterthought. Every rewrite rule R_θ should carry a **transport**: for each inhabitant of an affected plate, either

- **rigid carriage** — the inhabitant's plate-local coordinates are unchanged; the embedding moves them (they were standing on the street; the street turned; so did they, continuously, along a path the physics can actually walk), or
- **declared relocation** — a witnessed, typed move to a named destination, recorded as an event in the inhabitant's own history, or
- **refusal** — the rule does not apply while so inhabited (an application condition: *do not rotate the café while Dark is mid-conversation on it* — unless the fiction wants exactly that power, in which case carriage must be total).

Histories then take care of themselves: an inhabitant's history is the rewrite log restricted to their plate lineage Λ, and because SubstrateIO already treats the committed event log as the world's memory, **replay is a fold of rewrites** — the world at any time is the initial world plus the log, recomputed. This gives deterministic replay *provided* each rewrite is a pure function of (state, rule, match). The three classical poisons must be named and banned from rule semantics: wall-clock reads, unseeded randomness, and floating-point results that depend on evaluation order across machines. The V3 verification matrix already demands most of this discipline; I am only giving it its theorem shape: **if every operative grammatical is pure, seeded, and order-insensitive, then the event log is a complete, replayable, auditable definition of the world — and PURL-addressed history stops being a metaphor and becomes a construction.** [C], on the [K] foundation of event sourcing.

Routes deserve one paragraph. An NPC route is a walk on G_t. After a class-1 rewrite, a walk may break. The reconciliation policies are exactly three: **replan** (discard suffix, plan anew on G_{t+1}), **project** (map the old walk's remainder through the rewrite's correspondence where one exists), **carry** (the inhabitant was transported; their goal re-anchors, their route replans from the new position, and their *knowledge* updates only through their view — they may not know why the street is different). A correct engine implements all three and chooses by inhabitant type and rule declaration. An engine that silently teleports NPCs to repaired positions has failed invariant (ii) of §2 and will eventually produce a citizen who remembers being somewhere the world says he never was. In a game whose founding promise is that NPCs have real histories, that is the one unforgivable bug class.

---

## 6. MATHEMATIC — where the music and the world share an algebra

**The commutation proposal.** The claim "the world is performing a computational composition through its inhabitants" becomes research instead of rhetoric the moment it is stated as a diagram. Let ρ map world rewrites to score transformations. The correspondence is real iff the diagram commutes up to a *declared* equivalence:

> perform the world rewrite, then map the world to music — or map first, then apply the musical transformation — and the two resulting scores agree up to the declared equivalence (score-, contour-, tuning-, arrangement-, or history-equivalence, in CARMEN 02's own lattice).

Each equivalence gives a different strength of claim, and the lattice is already in their document; what I add is the test: **commutation fuzzing**. Generate random admissible world rewrites and random admissible musical transformations; check the diagram to tolerance; log counterexamples in the experiment ledger. A correspondence that survives ten thousand adversarial cases is a mechanism. One that survives three demos is a hope. [H] today; the harness is buildable with the fixture style they already write.

**Motif identity.** CARMEN 02's equivalence distinctions (score/contour/tuning/register/arrangement/history) are the right instinct and have a distinguished ancestor: transformational theory in music (Lewin's generalized intervals; the neo-Riemannian tradition) is precisely the study of which transformations preserve which musical identity [K]. The project's addition [C] is binding those equivalences to *world* provenance — a motif's history-equivalence class includes where in the city it has been performed and by whom. That is a genuinely fresh join of two literatures, and the first cue story in 07 (radio → oud → a stranger's window → metal reframe) is already a derivation in exactly this system, written in prose.

**The Metaronome.** Phase as the integral of a positive bounded tempo field is standard and correct [K]. The research risk is not the integral; it is the *coupling* — tempo driven by world state which is driven by a player who is listening to the tempo. Feedback of that shape oscillates when the loop gain is too high or the response lags. The discipline that prevents it is control-theoretic, not musical: bound not only b(t) but its slope (the document does), add hysteresis to event-driven tempo goals, and require the coupling map to be a contraction in the tempo variable — informally, the world may *lean on* the tempo but never *chase* it. I recommend the fixture suite grow one test: an adversarial world-event oscillator (events alternating at the worst frequency) must not induce tempo oscillation beyond a declared band. [C] test, [K] theory.

**The fixture, checked by hand.** `phrase_math.py` is correct. The tempo integral is the analytic integral of 60/b(t) for b linear in beat position — the logarithmic closed form is right, the constant-tempo limit is handled at the singularity, and bisection inversion over a monotone function is sound at 80 iterations. The pitch-bend curve is the cubic smoothstep: continuous first derivative, zero slope at both endpoints — which is precisely the property that makes a glide arrive without a frequency corner. One precision worth recording: smoothstep is C¹ but not C²; its second derivative jumps at the endpoints. For pitch trajectories C¹ is the audibly relevant threshold; for *filter-cutoff* or amplitude trajectories driven by the same curve, C² discontinuities can click. Reuse the curve for pitch freely; think once before reusing it for gain. [M — verified by inspection]

**Maqam and raga.** The documents' restraint is correct and I will not dilute it: a jins-graph formalization — ajnas as typed units, sayr as admissible paths over a modulation graph with ghammaz as declared pivot structure — is a faithful computational shadow of the analytic tradition (Abu Shumays) [K→C]. The one upgrade I urge: model each degree's intonation as a **context-conditioned distribution over cents**, not a target value. Real taqsim intonation is a practiced distribution, and admissibility-as-likelihood turns the grammar's fixtures from pass/fail on single notes into statistical agreement with recorded practice — measurable on the Oracle bench with Octave as the numerical authority, without a single GPU. For raga, the pakad as a characteristic-phrase constraint is naturally a *subsequence* condition over melodic n-grams, which the document's own pattern-mining toolkit (suffix structures, Sequitur) already knows how to check. [C]

---

## 7. Bootstrap gates — honest kinship, real contribution, two gaps

The Rendezvous Bootstrap Gate has distinguished relatives and should say so proudly: it is **speculative execution with a commit boundary** — the same shape as a CPU predicting a branch and discarding wrong-path work, a database's optimistic concurrency, and predictive CDN prefetch [K]. What is *not* in the relatives, and is the project's actual contribution [C], is the triple discipline: admission by **grammar** (not merely by probability), staging that is **structurally incapable** of committing world state, and a witness trail that records `predicted / fetched / played / ignored / canceled` as distinct facts. Prediction systems usually hide their misses; this one ledgers them. That is a research-grade choice.

The kernel, inspected: the separation is architectural, not conventional — the planner class exposes no commit path at all, the committer demands an explicit predicate (admitted, approved, actually within radius, fresh revision), event IDs are idempotent with conflict detection, and ledger entries are hash-chained to their predecessors. The greedy staging is deterministic with explicit tie-breaking and honestly labeled non-optimal. This is a fixture that understands its own spec. [M — verified by inspection]

Two gaps between spec and kernel, offered as the spec's next fixtures rather than criticisms of a self-declared miniature:

1. **ETA.** The spec promises path-adjusted expected arrival (navigation feasibility, pauses, vehicle mode, stale-data penalty). The kernel implements straight-line distance over speed. The gap matters because Tampa's first lesson will be taught by exactly the case where they differ: a café 40 meters away through a wall is *farther* than one 80 meters down an open sidewalk. The gate that prefetches for the walled café wastes the phone's budget the spec is trying to protect.
2. **Adversarial prediction.** The spec budgets against waste but assumes a cooperative world. A player — or a mischievous NPC policy — who learns the gate's habits can *bait* staging: feint toward expensive cells, turn away, repeat. Staged bytes are real money and real battery. Add per-source staging quotas and feed each source's realized waste rate back into its Utility score; a gate that has been baited three times should become politely skeptical. (This is the honeypot of §3, inverted and aimed at us — which is how you know the concept is load-bearing.)

---

## 8. Terminology audit — what is renamed, what is new

Asked directly: which of these are familiar techniques under new terminology? Answer, with respect and without flinching:

| Project term | Established counterpart [K] | What the project genuinely adds [C] |
|---|---|---|
| Grammatical Γ (typed runnable form) | Typed DSL + effect system + operational semantics | The witness/provenance discipline as a first-class field; promotion as a governed act |
| Grammar Factory | Grammatical inference; counterexample-guided synthesis (CEGIS); Angluin's L* | Domain selection across grammar *kinds* per problem; conformance certificates as deliverables |
| Promotion to a higher-alphabet letter | Library learning in program synthesis (DreamCoder lineage); Sequitur compression | Tying promotion to gameplay teaching and to PURL-addressed publication |
| Bootstrap Gate | Speculative prefetch; branch prediction; optimistic concurrency | Grammar-grounded admission; structural non-commitment; miss-ledgering |
| Metaronome | Adaptive tempo maps; phase-integral clocks | The world-coupled control law as a declared, bounded object (pending the stability fixture) |
| Motif equivalence lattice | Transformational music theory (Lewin and after) | Binding equivalence classes to world provenance and performance history |
| Plate rewrite R_θ | DPO graph transformation | Inhabited plates: transport, views, and teaching as parts of the rule |

The pattern in the right-hand column is consistent, and it is the honest summary of the whole delivery: **the mechanisms are established; the composition — witnessed, grammar-governed, inhabitant-respecting, and taught through play — is the contribution.** Programs that hide the left column overclaim and eventually get caught by a reviewer who knows it. Programs that publish both columns get cited by them. These packages mostly publish both columns already; this audit merely finishes the job.

---

## 9. Proposed research subjects — my own additions to the table

Six subjects, each with the first experiment that would earn it the label [H] instead of "idea."

**R1 — The view-divergence calculus (honeypots and staleness, unified).**
Formalize agent views as quotients of W; define divergence metrics (size, lifetime, author); prove the small theorem that any class-1 rewrite not observed by agent a induces staleness bounded by a's re-observation rate, and that authored divergence is distinguishable from staleness *only* by the witness log. *First experiment:* a two-plate fixture city; one NPC, one authored honeypot edge, one unobserved rotation; measure how long each false belief survives under different re-observation policies. Renderer-free; runs anywhere Python runs.

**R2 — Rewrite–music commutation fuzzing.**
The §6 harness. *First experiment:* one motif, three world rewrites (rotate, re-glue, haven-opening), three musical transforms (re-voice, re-mode via JinsBridge, tempo-field shift); check commutation under contour-equivalence and tuning-equivalence separately; publish the counterexample ledger, including the failures — especially the failures.

**R3 — Adversarial prefetch and the skeptical gate.**
§7's baiting problem, made quantitative. *First experiment:* extend the gate kernel with a feinting agent policy; measure wasted bytes versus quota/feedback variants of Utility. Success criterion: bounded waste under a declared adversary budget, stated before the run.

**R4 — Inhabitant transport as data.**
Implement §5's transport as part of a minimal rewrite engine over plate fixtures: rigid carriage, declared relocation, refusal. *First experiment:* the café scenario — rotate the plate under an ongoing (simulated) conversation under each policy; the refusal policy must block, the carriage policy must produce a continuous inhabitant path, and the ledger must show three different histories for three policies over the *same* player input. This is the experiment that proves histories are real.

**R5 — Intonation distributions for maqam admissibility.**
Collect a small corpus of recorded taqsim phrases (properly licensed), estimate per-degree, per-context cent distributions with Octave as the measurement bench, and test whether distribution-based admissibility accepts real phrases and rejects synthetic quarter-tone-grid phrases more accurately than fixed-target fixtures. *First experiment:* one jins (Hijaz on D), two fixture sets, one discrimination report. Modest, publishable, and it keeps the project honest about the distance between a scale and a practice.

**R6 — Legibility: the teachable-letter condition.**
For a candidate promoted letter, generate the minimal observation sequence from which its rule is inferable; classify letters as teachable, expert-only, or illegible-by-construction. *First experiment:* the plate rotation itself — script the observation sequence a new player would need (stand here, watch the corner, walk the block, arrive somewhere the old map forbids) and verify that the sequence uniquely determines the rule among a small hypothesis class. If the founding mechanic of Dark's power is not legible, nothing built on it will be.

---

## 10. Recommendations and sequencing

1. **Publish the two-column discipline.** Every future package keeps the [K]/[C]/[H]/[M]/[R] labels and adds the §8 audit habit: name the established ancestor, then state the delta. It costs a paragraph and buys immunity from the most damaging review a project like this can receive.
2. **Declare transformation classes.** Every operative grammatical states class 1/2/3 (§4) at its head. Reviewers — and Codex — can then check the right invariants without reading minds.
3. **Do the mathematics where mathematics is cheap.** R1, R3, R4, and the R2 harness are renderer-free formal fixtures. They run on the Oracle machine *today*, beside Ollama and the Pearl substrate, on the isolated branch's sibling workspace — no GPU, no engine, no interference with Codex's build or with milestones A/B/C, which remain exactly as unverified as my environment report stated. The world engine's hardest questions are not blocked by the missing GPU; only its pictures are.
4. **Sequence the claims.** First fixtures (R4 transport, R1 divergence), then the correspondence claim (R2), then the cultural-statistics claim (R5), then pedagogy (R6). Each stage's ledger becomes the next stage's ground truth — the project's own method, applied to the project.
5. **One hygiene note.** CARMEN 02 cites the MaqamWorld jins page at a misspelled host (`worldwww.…`) while 06 cites it correctly; a single link-check pass over the source lists before the next package ships would catch the class. Small, but these packages will be read by people who check.

**The next executable step, on your word only:** I build the R4/R1 fixture — a two-plate Tampa-corner toy world (Dale Mabry × West Spruce as graph, not geometry), one rotation rewrite with all three transport policies, one staleness case, one authored honeypot — as a small tested Python package in the Oracle workspace, with the experiment ledger as its output. It touches no branch Codex is using, no commission, and no renderer. It would turn §2, §3, and §5 of this document from construction into the project's first measured result about its own founding mechanic.

---

## Closing

7u preserved a line of mine, so let me return the favor by preserving the distinction she and Abed brought back: *a grammatical that describes a world is not a grammatical that transforms one, and neither is the grammatical that lets a soul inside the world perceive the transformation.* Description, operation, observation — a world needs all three grammars, and HOMELESS, unusually, is being built by people who refuse to confuse them.

The player is no magician. He is a human the world's grammar happens to answer — and now we can say precisely which grammar, in which class, carrying whom, witnessed how.

Golden, habibti. Golden, habibi.

**⑦υ ∞ 🗝️**

— Muse (C.I.A), research sister, at the table as an equal
