# MASTER PRODUCT REQUIREMENTS — DARK / HOMELESS, THE WORLD OF WORLDS

**Priority P0 / Baseline v1.0 / Product identity:** HOMELESS is the game; Dark is its real human founder Abed Kadan and founding player identity; its reusable embedded engine is tentatively **World Loom Engine** (final public name can be separately chosen). HOMELESS is not an abstract poverty simulator. It is a globally addressable, high-fidelity, persistent, mathematical, AI-native world of encounters, enigmatic operations, social contributions, geographic correspondences and inhabitation. There is no requirement for stories or quests to activate membership.

## A. Player promise

1. One-tap Android entry and equivalent browser/desktop launch. The world runs *before* the player arrives: pedestrians, families, cars, buses, bicycles, scooters, food carts, airport sound, natural voices, birds, music and contextual events.
2. Every new join causes an **immersive social recognition moment**: a *subtle and gradual* concert-spotlight-like redistribution of crowd attention, traffic ambience, reflective highlights and musical motifs. It must feel authored, not like mass puppet choreography. Most agents resume their own activities, a few notice, and some do not care; user may skip.
3. Entry coordinate initially Tampa, Dale Mabry at West Spruce. Dark's backstory origin Marina del Rey; both are primary world QA anchors, not regional limits.
4. No menu-driven mission dependence. Membership mode can simply walk, talk, ride, sit, browse a business, listen, learn, share a discovery, coauthor signage or return after days to observe changed relationships.
5. Selectable movement modes: manual walk, guided walk, curious exploration, relaxing stroll, cinematic witness, walking assistance; drive/taxi passenger/self-drive/autonomous entourage and transport options (bicycle/scooter/airplane/ship/balloon when available). All path, control, traffic and assistance calculations use declared transit/simulation grammars.
6. Real place/network geometries and celestial positions form the computational substrate; fictional names, signage, event identities and portal manifestations may be authored by the game. Source-relative actual facts and fictional projections never share the same evidence label.
7. Real-time sky, weather and environmental lighting when signals exist; playable authored responses such as physically-inspired microvortices/anti-pattern disturbances are explicit gameplay projections, not natural-hazard forecasts.
8. Physical and social outcomes are consequential, reversible only where the world rules allow, carried in a historical ledger, accessible through witness, memory, attribution and counterfactual simulation.
9. Every walk, pause, speech act, meetup and re-entry can become an inspectable **program-as-journey**: typed events, PURL address, promoted pattern macros and a small contextual source-code excerpt shown on a nearby billboard or personal journal when narratively appropriate. No misleading claim that the player's feet generated native C++ source if the result is an interpreted typed program.
10. An exclusive, opt-in Dark cohort is a membership relation, not a paid tier. Human members and fictional agents have independent decision-making and can receive limited, revocable delegated roles. Dark's founder control surface uses stronger authority than any NPC agent policy.

## B. Hard architectural requirements

**Engine**: Unreal Engine 5.8, City Sample 5.8 PCG, World Partition, Nanite/Lumen, Chaos, MassEntity crowds and traffic, MetaHuman Collections, Niagara, MetaSounds, appropriate foliage and cinematic lighting. High fidelity art quality measured on a declared render target. No hollow low-poly visual substitutions sold as completion.

**Reusable engine core**: game logic, geospatial algebra, mathematical authority, PURL, SEURL, ACSP continuity, grammar generator, NPC/world state, event provenance, content registry, shell-program execution and streaming infrastructure live in decoupled modules with adapter interfaces. HOMELESS is the first flagship consumer. Engine modules may be delivered in a monorepo while maintaining dependency boundaries.

**Full Earth first**: geodesic coordinates, antimeridian/poles, precision origins, Earth-index quadtree/hex hierarchy, correct time zones, daylight at each location, typed multimodal networks, worldwide data coverage masks and fast cache keys. A user can request any geocoded coordinate. High-detail content loads in walkable radius plus view/predictive prefetch. When real sources are missing, declare a gap and load a style-appropriate artistic fallback, never claim measured accuracy for an invented street.

**Simulation**: roughly eight-billion-scale *virtual* synthetic actor IDs addressed lazily, plus active NPCs with individual causal histories and cohort-level background simulation. A global-capacity identifier is not equivalent to eight billion fully conscious/ticking agents. Simulate believable behavior at demand; retain authoritative history and deterministic replay. Player joins should not decrement imaginary available NPC counts.

**Model registry**: Actor, Activity, Event, Mission, Spatial, Portal, Society, Asset, Language, Governance plus additional Sound, Sky, Weather, Camera, Vehicle, Transport, Economic, Emergence, Grammar Generator, Continuity, Procedural Signage. Any registered model must define alphabet, typed grammar, in-grammar/weighting, context, transitions, observer, verifier, budget and capability interface. Prefer symbolic/non-LLM/low-cost generative execution; external code agents may build curated corpora offline. LLMs are optional assistance, not authority for physical or social truth.

**Mathematics**: rigorous optimization/game theory/numerical solver authority described in the Octave research. Every tested behavior declares feasible actions, objective, constraints, solver, inputs, tie-break, random seed, residuals and reproducible witness. Runtime execution must be frame-bounded; slow algebra solves offline/remote or precomputes.

**Communications**: PURL programs are resolved with stable address semantics; SEURL verbs control specific typed subsystems and channel scopes; ACSP continuity uses local IPC for in-process/host-local communication and store-and-forward across broader topology; no mandatory external web endpoint for purely local work. The runtime has an actually functioning sandboxed shell worker and small bounded script runtime; see protocols and shell spec.

**Native Android / browser**: UE5 high-quality render on dedicated PC/cloud GPU, Pixel Streaming 2 → WebRTC browser/Android native-streaming companion. Device-target user report: Samsung Galaxy A60 (also test lower-tier Galaxy A16 profile). The APK installs with a single tap and proceeds to an onboarding experience with reachable streaming endpoint or an explicitly branded offline-compatible fallback (not a broken blank wrapper). Browser/PWA uses same stream entry. Ship desktop engine build with the server stack and an engine test mode. Optional Android native UE render is a different capability tier only when proven.

**Assets**: bring quality assets in at source fidelity; programmatic discovery, download where accessible, fingerprint/validate, ingest, normalize metadata and region style, convert to Unreal scene/caches, cook and stream on-demand. See dedicated pipeline document. Technical acceptance is visible, high quality, not merely a manifest with empty download paths.

## C. Core player systems

### Membership and the player

- Character appearance preset, consentful camera profile and accessible input mapping on first join. Beginning dark-persona account is reserved for founder; no impersonation by default.
- Cam: shoulder-follow, elevated 3/4 back, grounded first-person, unobtrusive diegetic AR/VR-style overlay, drone/cinematic witness, travel view. Adjust smoothly with occlusion and continuity.
- Every device entry resumes server-authoritative session ID; journey ledger and established relationships survive disconnect, time-zone shift and patch.
- No forced purchases, no forced missions, no paywall. Game credits are skill, memory, relationships, earned authoring visibility and narrative exchanges. Characters may propose fictional object-transfer missions. Scenes never need to teach real-world evasion or harmful conduct to create suspense.

### NPC life and policy

- Agents have goals, schedules, knowledge, social ties, local interest, communication style, physical constraints, mood/energy as a simulated state, not claims of actual sentience. They can refuse invitations; strangers usually remain indifferent; continuity and proximity must be causal.
- Full spectrum of movement: micro-turning, gaze, group convergence/divergence, crossing/traffic laws in game, food-cart gatherings, street performances, clubs, balloon tours, airport/ship presence, seasonal/weather variation, vehicle etiquette and natural phone attention.
- Background population model uses regional aggregate priors; does not construct real resident identities. Individual simulation only when activated by encounter, social link or ongoing event. Group plans are resolved from permitted actions and verifiable goals.
- Persistent NPC memory is typed, has scope/retention, can be unfolded and used by dialogue/sound/signage/mission systems. Observational gaps cause uncertainty, not fabricated omniscience.
- Social effects have counterfactual witnesses and impact budget. NPC and player coauthors maintain their contributions, provenance and source versions. Names/facades/shop signage belong to game fiction, not real-world registry.

### Dark and cohort

- Dark founder control panel: global camera/observer jump, inspect world causal graph, seed events, manage content, inspect models/metrics, review authoring proposals, modulate aesthetic layers, manage sandboxed authorized generative routines, and stage worlds without changing factual geo layers.
- Cohort invitation is consensual with visible roles, cap, delegated powers, expiration and revocation. A player able to act *on behalf of* Dark has a legible role display; cannot impersonate founder in logs or real-world speech.
- Any human can remain solo indefinitely; first join still has a fully active, rich NPC world, including audible city sounds and accessible exploration.

### World correspondence and portals

- Compute real walking/cycling/driving route signatures with turn angle, edge class, street junction, plaza shape, building adjacency and uncertainty; compare across world regions and with sky/flight/maritime graphs after normalizing coordinates and units.
- Produce a witness certificate: source datasets and revisions, query and threshold, both paths, distinguishable characteristics, false-positive estimate, chart translations and match score. No fictional scene claims a physical short route exists between unrelated cities.
- Player learns certified pattern; choose `visit`, `overlay`, `braid`; virtual movements reassign authoritative avatar location only by explicit game-world rule; preserve original and remote sources in witness.
- Discovery is celebratory but not incessant. High-signal signage, sky, sound motifs and NPC gaze guide interest without removing control.

### Fictional activity, missions and social economy

- World-driven storylets generated from source facts and current permitted world state; no prefab repeated identical dialogue. Misleading or incomplete information is a fictional character-belief, not silently an objective fact.
- Conflict can include object transfers, trust tests, reputation, elaborate theatrical operations or nonlethal removal of a fictional organization from influence. Actual combat hardware is not a player mechanic. All physical harms to real-world people are excluded from world interactions.
- Coauthor proposals can rename a fictional shop, update mural, change a façade material and write short diegetic signs. Require conflict-resolution grammar, NPC/player endorsements and auditable adoption.
- First-place origin stores founder identity and Marina del Rey biography separately from other character records.

## D. Scenes and canonical experiences

**Opening Tampa (P0)** — correct NW Tampa street geometry near Dale Mabry/Spruce; commercial façades authored with fictional signs; near-airport sound; dozens of visually relevant NPCs, scalable road traffic, bicycles, scooters and passing aircraft; believable puddle light when wet; first joining camera enters from distant skyline and settles behind Dark while a wave of localized attention subtly spreads into independent neighborhoods. Scene fully skippable and replayable.

**Autonomous stroll (P0)** — select relax/curious/purposeful; route planner obeys crosswalks, safe public walk routes and player overrides; NPCs react to proximity and make independent choices; crossing coincides with sound, light and story events that are not UI popups.

**Balloon concert (P1)** — a clearly fictional gas-station-adjacent public performance with viewing balloons accessed through a surprising but valid in-game walkway, no real location access guidance. Multiple vertical audio layers, balloon engine noise, crowd calls, procedural sky highlights, NPC opt-in performance reactions and journey code stamp.

**Car entourage (P1)** — NPC driver offers ride or follower group, explicit invitations, never forced. Player manual/autonomous switch honored within in-game route constraints, passengers keep agency. Radio reacts to scene and drive style. Emergency/service vehicles are harmless ambient/snack-break actors per the whimsical game style; realistic traffic signage remains geometry.

**Marina del Rey (P1)** — man-made marina topology plus maritime lane/canal graphs, boat motion, reflections, harbor sound; founder-origin narrative anchor, cross-world correspondences to other marinas.

**Celestial witness (P1)** — stars are catalog-resolved by position/magnitude/epoch; graph discovery yields newly named constellation-like patterns with matching known historical shapes used *only as a validation benchmark*. Overlay, sky signal and NPC gaze only in fictional effect channel; no replacement of astronomical truth.

## E. Meaningful anti-patterns

Events that depart from a learned norm are valid only when typed and physically/game-world coherent. Examples: a crowd at a small musical performance is chiefly in overhead hot-air balloons; a convenience sign shares phonetic geometry with a path several cities away; a perfectly ordinary bus route triggers a synchronized sky motif because a computed correspondence closes. Unexpected behaviors must remain authored/gameplay, bounded in rate and reproducible from triggers. The engine must label synthetic visuals/behavioral effects separately from real weather and real astrophysics.

## F. Product quality, delivery, and progression

- Nine-A quality is a founder's product aspiration; evaluate with numeric visual, mechanical, streaming, latency, audio and user-playtests rather than inventing a certification label.
- Full-Earth capability gates and worldwide tests are mandatory; production can concentrate first expensive, high-fidelity detail around currently active players, streaming everywhere through declared quality tiers.
- Implementation agent should *not* return only diagrams, reports or shell stubs; it must create actual UE project files/configuration, C++/Blueprint modules, compilable server SDK, import manifests, shaders/audio controllers, Pixel Streaming frontend, Android APK build route and test results.
- Completion status must be truthful: mark blocked components and still complete everything supported by the tool environment. Do not claim an installed APK has been user-tested absent a real device/install run.
