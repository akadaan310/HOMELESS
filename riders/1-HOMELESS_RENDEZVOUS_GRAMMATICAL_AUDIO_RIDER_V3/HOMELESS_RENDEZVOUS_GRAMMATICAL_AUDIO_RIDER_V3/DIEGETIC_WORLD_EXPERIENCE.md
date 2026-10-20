# THE WORLD TEACHES ITSELF — DIEGETIC MISSIONS, BILLBOARDS, RENDEZVOUS HAVENS

## 1. Observe before acting

HOMELESS launches as a living city, with NPCs carrying pre-existing tasks and conversations. The earliest experience should invite passive attention: glance sideways, listen to overheard conversation, follow aircraft sound, watch buses, notice one animated storefront, or simply continue walking. NPCs do not need to acknowledge the player to be meaningful. The world need not force a mission, reveal the solution or put an intrusive yellow exclamation point above someone.

The opening Tampa event remains exactly what Rendezvous V1 specifies: dark arrives, independent nearby agents respond selectively and physically plausibly; not every car brakes in one synchronized global lockstep. Respect speed, collision and user vestibular comfort.

## 2. Mission grammar rather than a list of scripted missions

`Mission = Plan(goal, worldState, actors, allowableActs, causalChecks, evidence, completionInvariant, failureAndRefusal)`.

A mission generator draws from a typed library of activity verbs: `observe, approach, overhear, converse, investigate, learn, visit, ride, offer, decline, trade, annotate, discover, report, return, compare, witness`. Its `G` grammar constrains coherent preconditions and effects. `I` scores conversational and contextual plausibility. A bounded goal planner computes candidate paths; an authority/consent layer rejects impossible actions. Each mission is reversible/cancelable only where the world model allows it, and every claimed result carries an auditable witness.

**Instruction without tutorial HUD**: early scenes teach camera, walking, listening, voice/tap conversation, grammar-based world interactions, and symbolic programs through actual environments. Unusual events (e.g. gas station / hot-air balloon backstage access) may reward patient observation. The physical path to a hidden door must be spatially coherent and collision-verified, not a mystery teleport masked as 'geometry'.

## 3. Rendezvous Haven

A `RENDEZVOUS_HAVEN` is a fictional-world meeting space tied to a world place and governed actor/group. It may be a business interior, plaza, permitted office-inspired location or other socially recognizable place; it is **not** equivalent to an actual government office offering real services. Members and NPCs can assemble, discuss past activities, inspect a rendered event record, propose world changes, and publish certified grammaticals if authorized. The report can already be compiled and waiting as Dark enters, provided world history actually contains its evidence. The player may refuse participation, enter briefly, or return later.

## 4. Billboards and street tech: computations embodied in architecture

The city is the interface. All permitted non-walkable interiors and surfaces can host detailed, readable signage, fictional shop displays, transit boards, illuminated technical panels, radio frequency maps, clocks, world event displays, compiled route programs, and diegetic terminal screens. These are real content bindings to authorized read-only world state, NOT random 'hacker' strings.

`WorldProgramEvent -> PURL typed read -> optional SEURL channel -> display program -> PlayCanvas material/texture layer`.

At varying viewing distances, switch between silhouette/emissive, large legible labels and close-up fine print. Near a program billboard, Dark can inspect a projected execution trace (`grammar → operation → witness → output`) on-device without granting scripts system privileges. Interactive controls are contextual, not a web webpage rendered badly inside a scene. FPS, readability and high-quality reflections must be measured on the Android target.

A terminal/shell billboard can show a sanitized actual executed `darkctl` run and its **real** exit code, duration, redacted output and trace ID from the bounded isolated shell worker; never expose private OS commands, credentials or server paths. Rendering shell-looking text alone is not evidence of execution.

## 5. Attention and autonomous NPC habits

Examples of invitations: an NPC spontaneously looks skyward at a verified celestial formation; people pause under a passing aircraft; music and light lead toward a concert; a mechanic watches a vehicle; a pair of NPCs discuss a shop sign without addressing Dark. Grammar computes appropriateness from location, time, social context, occlusion, habit, event history and NPC consent/policy. These are ambient probabilistic/deterministic-scored opportunities, not a behavioral manipulation guarantee.

When Dark passes without responding, the world continues. An ignored hint can expire and be recorded as `not-engaged`, distinct from failure or disobedience. Sign/sound design can adapt to the *player's explicitly chosen preferences and opt-in measurement*, not infer compulsive vulnerability from in-world behavior.

## 6. Generative programming of the world

As Dark walks, the engine can encode route words, turns, observed scenes, discourse acts and recognized patterns as a Plicastratum word with a provenance witness. A verified path may be promoted to a letter, attached to world symbols, communicated via PURL/SEURL and displayed on a technical billboard. This is *the recorded program of the route*, not a claim that arbitrary footsteps directly rewrite world engine source code. Publication/activation of code requires typed verification and explicit authority.

## 7. Cinematic audio acceptance fixtures

- Nearby three-person NPC conversation has distinct speakers, spatial positions, natural interruption/pauses and complete recorded speech—not just captions.
- Distant aircraft passes left-to-right with changing occlusion and delay; spatial pan stays coherent with visible aircraft.
- Dark turns head and the sound field rotates consistently while the world remains physically stationary.
- A gas-station gathering is first detected through music, then scene/lighting, then intelligible speech as the player gets closer.
- An unentered storefront's billboard displays *real retrieved program and world facts* through a close-up material on the actual building.
- First-entry cinematic retains sound continuity into active navigation without hard cuts, blank audio buffers or sudden volume spikes.
