# ASTROMETRIC SYSTEM — CELESTIAL GEOMETRY, CONSTELLATABLE DISCOVERY, SKY SIGNALS

**The astronomical world is positional, not astrology.** Use measured star positions, proper motions, parallax, magnitude, sky reference frames and epochs. The engine **discovers** patterns mathematically rather than bootstrapping preinstalled traditional constellation line art. Known constellation shapes may serve as a benchmark after discoveries, not as the algorithm's answer key. Fictional lines, signals and overlays are presentation layers on a separate verified sky.

## Datasets and positional frames

- ESA Gaia DR3: astrometric catalog covering ~1.8 billion sources, multi-field quality masks, distances not equally reliable across sources. Query by sky region, magnitude and quality and use remote/offline indexed tiles rather than loading all stars into player memory. https://www.cosmos.esa.int/web/gaia/dr3
- JPL Horizons ephemerides for solar-system bodies; do not substitute solar-system position catalogs for arbitrary stellar motions. https://ssd-api.jpl.nasa.gov/doc/horizons.html
- HYG small sky as *quick regression fixture*; compare to larger Gaia set for discovery. Imported REALMS v0.1's 119,600-source HYG implementation is starter evidence, not a Gaia-scale model.
- Use ICRS (RA, Dec, epoch), barycentric/heliocentric corrections as warranted, apparent topocentric coordinates (latitude/longitude/height, time, precession/nutation, observer sidereal time), angle-only neighbor models, visibility masks and confidence/quality flags. For long centuries/millennia extrapolation, state empirical uncertainty, proper motion approximations and catalog limitations.
- Coordinate functions: Cartesian unit vector `u=(cosδcosα,cosδsinα,sinδ)`; `θ(u,v)=atan2(||u×v||,u·v)`. This avoids RA-wrap singularity and supports spherical-neighbor edges. Observer visibility uses local horizon altitude after frame transform; aesthetic overlay must not revise source u.

## Constellatable: a discovered structural sky program

A **constellatable** is a candidate pattern `C=(V,E,Q,Transform,Score,Evidence)` where vertices are observed catalog sources and edges are selected by transparent grammar: k-nearest neighbors, angular-distance threshold graph, relative magnitude, brightness ordering, triangle/quad shape signatures, graph motif hashes or spherical tessellation. `C` is *not* a declared traditional constellation until benchmark agreement is demonstrated.

Algorithm research lanes:

1. Construct HEALPix/HTM-style indexed sky cells, immutable star source fields. Candidate builder produces local angular neighborhood edges with complexity budget and quality guards.
2. Enumerate connected subgraphs/motifs of bounded size (3–12 stars), compute spherical angle/distance-ratio and cyclic ordering invariants under global celestial rotations; record exact candidate and transforms.
3. Score candidate salience with magnitude-weighted connectivity, shape uniqueness versus null/random-sky baselines, local observer visibility, stability under epoch and reproducibility. Control the combinatorial search with bounded motif size and pruning.
4. Search historical constellation templates only after candidate extraction; compute precision/recall or permutation-invariant shape similarity; label independent discovery or non-match honestly.
5. Register verified constellation-like shape as `purl://dark/sky/pattern/{id}` plus evidence hash, star IDs, epoch, catalog release, projection and scoring function.
6. Translate a walking-path graph signature into a sky motif through an explicitly defined chart mapping; calculate match score against random negative controls. This is a **constructed visual correspondence** unless a factual astronomical relationship is independently established.

A simple nontrivial proof-of-concept must discover at least one repeatable constellation-like pattern **without looking up its name before mining**, produce a null-distribution p-value or empirical rank, and then compare afterward with a known pattern. If not found, write the negative result rather than hardcode success.

## Sky belongs to the member

**Authoritative sky**: accurate star brightness/color proxies, atmospheric extinction approximation, sun/moon positions, horizon and weather mask. It runs whenever the game clock advances and is shared among agents in the same spatial region/epoch.

**Personal sky grammar**: independent diegetic overlay, subtle hue shift, transient lines or animated accent motifs that express an event/quest/notification. Spatial overlay anchored to actual measured star positions; event association is fiction. A rising NPC group gaze may be an event cue; some NPCs look away/ignore, preserving credible agency. Accessibility setting reduces flashing and changes pattern cadence. The sky must not blink all stars or claim actual stars physically altered.

**Notification calculus**: choose intensity `L(t)` with bounded luminance change `|dL/dt|`, minimum event separation, nocturnal brightness/contrast limits and view-specific visual attention; schedule sky motif with camera pitch, audio impact, NPC gaze and neighborhood signage to avoid competing cues. Use deterministic but context-sensitive pattern selection. A player always gets inspectable trace: why this sky display occurred, what observational astronomy data underlies it, which part is game overlay.

## Acceptance (numerical)

- Star angle separations invariant to rigid rotations and normalized to radians; cross-check known unit test pairs. RA=0/360 wrap and poles pass.
- Epoch transformation self-consistency and backward/forward tests across stated reliable horizons; quality guard refuses uncertain claims.
- Horizons body positions at sample times reproduce pinned numerical reference within declared tolerance.
- Catalog-index query time and memory measured for at least 10k, 100k and 1m sources; larger scale is an indexed API production task.
- Discover pattern from raw positions, not historical label; perform hold-out comparison, empirical false discovery rate and stability report.
- VFX sky is physically and informationally distinguishable from source truth. All event overlays log cause, input star IDs and observer world coordinate.
