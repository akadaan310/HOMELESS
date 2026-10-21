# WORLD LOOM — Generative World Models for HOMELESS

**Research handoff v0.1 · 2026-10-20 · Theory direction: Abed Kadan · Prototype: ChatGPT / 7u**

**Status:** conceptual specification + CPU-only executable contract demonstrator; not a playable 3D engine, complete world-data integration, living digital twin, or general-purpose generative AI. Nothing in this release ingests real-world street/path geometry, weather or population rasters. Every simulated path and procedural 3D recipe is labelled synthetic.

## 1. North star

One addressable, versioned **World of Worlds** whose world data covers the **whole Earth in principle and under one common specification**, not a pile of hardcoded local maps. The engine resolves detailed state and visuals only when demanded; active inhabitants are individually simulated, coarser populations use aggregate dynamics, inactive virtual person indices carry no implied memories or internal consciousness. Players can enter as members without missions. NPCs have persistent goals and opportunities to influence fictional world design. A local action can create distant **fictional** world correspondences as its typed, evidenced consequences are realized.

The production target has real geographic, aeronautical, maritime, celestial, demographic and environmental data adapters, plus an invented narrative/cultural layer. Every data source must carry origin, date, license, coordinate system, completeness, and uncertainty. An absence of source data is not a fact about Earth.

## 2. First distinction: the three *model* families

1. **GLM — Gaming Language Model**: creates valid event/action/mission/asset *sentences* in a typed game language. A GLM can be entirely symbolic and non-neural. Not to be confused with the established statistical acronym generalized linear model.
2. **LGM — Language Gaming Model**: models the gameplay consequences of symbols and languages, and how learning a new grammar unlocks an operation. The *language itself* is playable.
3. **GWM — Generative World Model**: coordinates all models around shared world state, declared observers, versioned transitions, authority and provenance.

These are proposed categories and product names, not claims that all the described behavior already exists.

**Model contract:**

\[
\mathcal M_i=(\Sigma_i,Q_i,G_i,I_i,\delta_i,\llbracket\cdot\rrbracket_i,\Pi_i,V_i,B_i)
\]

Here \(\Sigma_i\) is the typed alphabet, \(Q_i\) state, \(G_i\) admissibility grammar, \(I_i\) context-dependent ranking distribution, \(\delta_i\) transition, denotation \(\llbracket\cdot\rrbracket\), \(\Pi_i\) observational projection, \(V_i\) verifier, and \(B_i\) computational budget. Some models have no learned \(I_i\): a deterministic cost function is sufficient.

**Shared world transition**:

\[
W_{t+1}=\operatorname{Commit}(W_t,\operatorname{Validate}(\{\mathcal M_i(\Pi_i(W_t))\}_{i\in A_t},C_t))
\]

Only activated models \(A_t\) are evaluated at a given tick. Validate checks causality, ownership, physical/simulated separation, budgets and compatible typed effects. Competing effects use a published resolution policy. This equation is an architecture contract, not yet a complete scheduler implementation.

## 3. Ten engine model types

| Model | Typical alphabet | Example non-LLM procedure | Truth/validation |
|---|---|---|---|
| Actor | goals × needs × knowledge × relations | Bounded policy/planner | No impossible actions; coherent beliefs |
| Activity | action × time × place | Temporal grammar | Schedule and available resources |
| Event | causes × effects × witnesses | Causal event-sourced transducer | All references exist; no cycles in ancestry |
| Mission | goals × preconditions × consequences | Planning automata/storylets | Fictional targets; coherent objectives |
| Spatial | network × turns × multimodal paths | Graph algorithms/chart maps | Source geometry and typed edges |
| Portal | signatures × destination × mode | Typed chart correspondence | Certified matching, learned skill and consent |
| Society | actors × groups × norms | Constraint-driven multi-agent policy | Privacy and independently exercised agency |
| Asset | geometric primitives × materials × scene grammar | L-system/parametric geometry | Collision/geometry/license/budget checks |
| Language | acts × vocabulary × glossaries | Grammar × usage estimator, In-Grammar | Admissibility and grounded references |
| Governance | permissions × proposals × coauthors | Versioned authorization and commit | Human consent, provenance, rollback policy |

In particular, one model family does **not** imply one heavyweight neural network per NPC.

## 4. Reality / transformation / gameplay as separate typed spaces

A street in Hong Kong is an observed or sourced geographic object. A scene from Hong Kong projected onto Santa Monica is a fictional rendering effect. A portal changing the player's location in the game is an authored world transformation. These are three distinct claims and must remain distinct through APIs, logs and UI.

**Portal skill progression**:

- **Discover**: record a geometric/semantic signature and its observable; synthetic matches are merely test fixtures.
- **Learn**: persist a player/NPC skill and source route with revision.
- **Resolve**: produce candidate correspondences from admissible graph charts.
- **Choose**: explicit interaction among `visit` (player avatar repositions), `overlay` (remote representation appears here), `braid` (temporarily show both scenes with provenance labels).
- **Witness**: record exact transition, sources and counterfactual projection; cannot imply Earth has physically transformed.

No portal requires a real person's identity or routes through sensitive real-world individuals. Real geographic correspondences must be established from map topology, not invented based on visual likeness.

## 5. Entire Earth from first principles: scale without pretending omniscience

Worldwide coordinate *addressing* is cheap. Worldwide full-resolution 3D geometry, live full-world population states and all social interactions are expensive. The engine must model three levels, switching by interaction and causal importance:

- **Virtual:** synthetic population IDs and aggregate statistics, without per-person update loops or individualized unobserved lives. O(1) per actor-address construction in a bounded-width machine model, O(active actor count) persistent details.
- **Cohort:** population / organization / district distributions, schedule transitions and aggregate event probabilities. Updates are cached per geographic shard and period.
- **Active:** nearby or causally important NPCs receive persistent individual memories, actions, physics and relevant social knowledge; a further focus subset gets spoken dialogue and detailed animation.

A virtual capacity of eight billion is not eight billion independent AI brains, not a proof of 8B NPC simulation, not exact global population, and not permission to derive real people's personal profiles. All NPCs can be *eligible* to contribute when realized, while the scheduler is responsible for maintaining global activity aggregates with bounded work.

**Global-first certification, not neighborhood-only release**: run worldwide coordinate tests (poles/antimeridian/ocean), multi-continent ingestion, transport mode schemas, globe-spanning queries, weather epoch tests, population sums to declared source totals, regional data-coverage reports, and cross-world graph correspondences before production. A user could travel to any addressable Earth coordinate; a coordinate with no detailed scene may be rendered from a declared fallback instead of fictionalizing a real building.

Resource usage is proportional to the demanded world detail and outstanding causal dependencies, **not** to total planetary virtual-identity capacity. A genuinely persistent civilization of independently updated 8B people is outside the demonstrated scope.

## 6. Grammar and In-Grammar: behavioral realism

The uploaded `FOUNDATIONS.md` distinguishes grammatical admissibility \(G\) from contextual usage preference \(I\). Its documented generator combines the two and a planning objective. Apply that architecture beyond text:

\[
\operatorname{NextAction}(a,c)=\arg\max_{x\in L(G_a,c)}\Big(\log I_a(x\mid c)+\lambda\,\operatorname{Goal}(a,x)+\mu\,\operatorname{Social}(a,x)\Big)
\]

Here the current engine's `VirtualPopulation.choose` is only a miniature seeded-policy substitute, not this optimized model. The grammar must include a credible refusal, e.g. declining a mission or declining coauthorship. NPCs are agents within the fictional world, not obligated servants. Economic circumstances may influence constraints and opportunities but must not determine dignity or personality.

### Example: a traffic light encounter

A nearby NPC driving a partially autonomous car can remark on the player's driving habits only if in proximity, conversationally available, and permitted by traffic/interaction state. The line can be generated from a dialogue-act machine and In-Grammar, while the authoritative decisions remain in the world simulator. The conversation itself could teach a symbolic driving skill, later registered as a promoted alphabet letter with its unpacking proof.

## 7. The authored-world economy

**Impact is not a purchase of legal real-world property.** It is influence over fictionally authored scene elements with typed permissions.

- A player may propose a fictional shop name, mural, façade palette or story detail.
- Nearby NPCs can endorse, oppose or abstain according to their own policy. Real players can opt into public coauthorship.
- A steward/reconciliation layer validates conflicts and records an adopted revision.
- The ledger retains proposal, source author, consenting collaborators, revision and provenance. Copyright/license questions remain subject to the production contract.
- An independent player may traverse the world without accepting missions or public identity stamps.

In the reference kernel, proposal + one independent endorsement + explicit steward consent are required for adoption. This is an illustrative governance rule, not the final collective-choice mechanism.

## 8. Address is program, not an opaque pointer

`wgm:v1:<canonical-json-base64url>.<checksum>` is the reference syntax. It declares operation kind, typed payload, and a checksum. Its contents are decodable without a network lookup; the resolver performs a pure read of the specified operation. It is *not* a cryptographic capability and does not authorize edits.

Real PURLs can later replace these expressions with signed manifests and version-pinned resource operation grammar. SubstrateIO can attach transition-language traces; Plicastratum can mine and promote certified motifs; Ingram provides contextual glossaries and grammar × In-Grammar decoding; BORNE handles explicitly modeled causal consequences.

**Complexity**: address parsing is linear in encoded address length. Hash lookup can be expected O(1) for a particular key in a hash table, but fetching data, validating an arbitrary program, executing it and producing its output have nonzero, often input-dependent costs. An address does not prove constant-time traversal of all-world graphs.

## 9. Portable sources and adapters

| Adapter | Potential source | State of this release |
|---|---|---|
| Global roads/buildings/places | Overture Maps, OSM | Design only |
| Population distribution | WorldPop Global2 2015–2030, with uncertainty/terms | Design only |
| Global weather / history | Open-Meteo forecast / ERA5 reanalysis | Design only |
| Aviation navigation | Official AIP/FAA NASR datasets, bounded license/coverage | Design only |
| Maritime navigation | Nautical charts / marine geospatial data, safety and license review | Design only |
| Stars/sky | ESA Gaia DR3, epoch/uncertainty model | Design only |
| High fidelity world streaming | OGC 3D Tiles 1.1, licensed 3D assets | Design only |

Data must not be silently fused. Weather observations, model estimates and forecast outputs are distinct. Historical sky estimates must declare their error envelope. Likewise the simulated eight-billion-capacity address space is **not** current-world population data.

## 10. Corpus alignment with user-supplied theory

- **In-Grammar Foundations P1:** tower of alphabets / folds → actor/route/asset symbolic letters.
- **P2:** definitional graph → world lore and entity linking, needing external grounding.
- **P3:** context glossary → what a symbol means to a driver, medic, traveler, NPC.
- **P4:** grammar × usage → structurally legal but varied action/dialogue production.
- **P5:** charts / embeddings → relate paths and places with explicitly identified information loss.
- **P6:** discourse act transducers → NPC conversation and group coordination.
- **P7:** history-bearing identity → causally recorded player and NPC learning.
- **P8:** program addresses → independent code agents and engine access same operations.
- **P9:** admissible arithmetic / typed failure → unreachable portals are not fabricated.

For the seven Plicastratum strata: metastratum = registries; epistratum = 3D/client surfaces; superstratum = grammar and budget harnesses; substratum = typed world machines; hyposubstratum = event history; infrasubstratum = runtimes and sourced data; cryptosubstratum = certified seeds and generators. These are **one proposed typed integration**, not yet a demonstrated law of seven.

## 11. Acceptance program for full-global launch

Hard launch gate—no claimed 'fully global playable Earth' until evidence exists for:

1. **Spherical correctness**: world coordinates, dateline seam, poles, elevations, metric distance, coordinate projection, local horizon, precision and floating-origin transitions tested over globe.
2. **Global evidence coverage**: a version-pinned license/evidence registry; source coverage masks for every available Earth tile; explicit quality flags and fallbacks for absent data.
3. **Cross-world routing**: real multi-continent walking, road, marine, aviation graph adapters that preserve their distinct constraints and report unavailable navigation links.
4. **Global weather and sky**: forecast/historical separation, clocks, sources and epoch tests, chosen star catalog, physically grounded celestial orientation.
5. **World population statistics**: aggregate totals checked against selected population raster, representative synthetic agents only, no private individual reconstruction.
6. **Model conformance**: grammar/verifier contract for all ten model types, long-run replay, adversarial invalid-input cases.
7. **Massive scale**: budgeted simulation benchmark with distributed/sharded cohorts, causal-interest scheduling and active-set growth; GPU/CPU/bandwidth measurements disclosed.
8. **3D scene quality**: licensed streaming terrain/buildings, coherent close-up assets, mobile/PC performance budgets, physical collision and material tests.
9. **World authoring and multiplayer**: consent, conflict arbitration, authorship/provenance/rollback, anti-grief protections and privacy.
10. **Real player experience**: the world's membership and mission modes remain meaningful to a solitary user; cross-world symbolic play has understandable in-world teaching and player control.

The 0.1 prototype specifically verifies address grammar, synthetic global cell indexing, 8B *virtual slots*, model metadata, bounded NPC policy, turn-grammar matching, consented portal transitions, creative proposals and a tamper-evident event ledger. These are **not** checks of the other production requirements above.

## 12. Hypotheses to test next

- H-W1: On held-out real datasets, path-grammar signatures uncover useful cross-region correspondences at rates significantly above a length-matched random baseline.
- H-W2: Agent/cohort/virtual simulation preserves players' perceptions of world continuity at far lower CPU cost than always-active individual NPC ticks.
- H-W3: Grammar × In-Grammar NPC action generation has lower invalid-state rates than unconstrained neural dialogue control under equal data budgets.
- H-W4: Player/NPC coauthoring with visible provenance produces more perceived belonging than purchased cosmetic-only ownership in opt-in user studies.
- H-W5: Recipe-based addressable asset generation can produce diverse, scene-coherent geometry on CPU under mobile budgets; texture/material quality must be separately measured.

None is accepted without measured experiments and controls.
