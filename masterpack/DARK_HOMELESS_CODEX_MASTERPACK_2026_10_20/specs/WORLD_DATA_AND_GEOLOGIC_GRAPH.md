# WORLD DATA — PLANETARY MULTIGRAPH, SOURCING AND WALKABLE STREAMING

**Scope:** Earth from day one at the *address and protocol* level, detailed at places actively requested by members. Global coverage is a data and computation responsibility, not a request to render eight billion NPCs at once. Initial live/QA anchors: Tampa N Dale Mabry + W Spruce, Marina del Rey and cross-continent candidates (Los Angeles/Hong Kong/Dubai). A fictional projection must never be reported as an observed geographic fact.

## World schema

`WorldEntity=(typed-id, geo/WGS84, local-ENU/transform, temporal-validity, layer, attributes, evidence-ref, confidence, history-ref, presentation)`.

`WorldGraph=(V,typedEdges,charts,admissibleTransitions,renderAnchors,dataRevisions,projections)` with layers:

- terrestrial road, path, sidewalk, crosswalk, cycle and rail networks;
- buildings, lot footprint, storefront, interiors when sourced, elevations, vegetation/water/terrain;
- aeronautical airport, navigation fix, route segments and live or historic aircraft traces where sources exist;
- maritime waterways, ports, lanes and historical vessel routes;
- astronomy: spherical graph of star neighbor relationships with epoch-aware positions;
- population density, synthesized actor neighborhoods and daily life cohorts;
- surface weather/lighting/time, fictional event and social causality.

A relation can cross layers only with a typed chart or function. Example `ground.walk.signature` vs `sky.graph.signature` may be compared with an explicit transform and normalized geometry, but they are not physically connected paths. The same coordinates may identify multiple entities across layers without being identical resources.

## Source acquisition priorities

1. Overture Maps: global transportation segments/connectors and buildings; explicit real street routing where coverage exists. https://docs.overturemaps.org/guides/transportation/
2. OpenStreetMap: planet extract, routable street topology and place tags; maintain its geometric provenance, but default *rendered shop names* are newly invented in-game aliases. https://planet.openstreetmap.org/
3. OGC 3D Tiles + Cesium for Unreal: global terrain and photogrammetry geometry streaming in native UE georeference. https://www.ogc.org/standards/3dtiles/ ; https://cesium.com/learn/cesium-unreal/ref-doc/
4. WorldPop/GHSL demographic estimates: grid-level population signals and cohort assignment, never identity-level copies of actual humans. https://www.worldpop.org/datacatalog/
5. FAA/NASR + OurAirports for aviation reference points, airports/airways when included; formal restrictions for traversable game links. https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/
6. Marine Cadastre AIS historical US vessel traces, coastline/ports and public waterways; route gaps flagged. https://marinecadastre.gov/ais/
7. ESA Gaia/JPL Horizons astrometry: sky source and epoch; see astral spec.
8. Open-Meteo/ERA5: source-declared current/historic data and atmospheric uncertainty. https://open-meteo.com/

## Worldwide ingest and query

- Ingest one *geographical source tile* at a time, normalize CRS/time/units, store geometries as spatial indexes (R-tree, S2, H3 or selected scheme with measured costs), record source hash, data confidence and update epoch.
- Queries include `ResolveCell(lat,lon,epoch)`, `NearbyActor(context,radius,time)`, `TileVisualRecipe(camera_pose, budget)`, `Route(mode,start,end,constraints)`, `PatternCompare(typed_path, atlas, score)`, `CrossDomainObserve(chart-a,chart-b, transform)`, `WeatherField(cell,time)`, `VisibleStars(observer,time)`, `StoryEvents(context)`.
- **Source quality mask** accompanies each query response: confirmed factual, approximate inference, incomplete, fictional synthetic fallback, time-unknown or unresolvable. Renderer can choose high-fidelity fictional composition while gameplay fact layers remain honest.
- Earth globe tests: poles, anti-meridian, altitude below sea level, continuous floating origin, horizon/LOS and geodesic path distance. No snapping with visible jitter while walking or zooming.
- Simulated local actor counts weighted by selected population grid; eight-billion-scale random address space is a capacity target, not a source-measured constant. NPC realization consumes memory only for demand-selected actors/cohorts; source-date specific populations remain separate from generated world state.

## Cross-world geometric matching

Use layered feature signatures e.g. `turn-sequence × junction-degree × functional-road-class × length-ratios × plaza-topology × building-height-histogram × POI-class-shapes`. Evaluate graph edit distance/approximate search with temporal and geographic normalization. Calculate null distribution from location-matched random samples; only surface rare meaningful matches to players. False positives are recorded and future thresholds recalibrated.

A player's journey is a typed path word whose **source geometric witness** is reproducible; charts for walking, bicycling, driving, flying and shipping have different degrees of freedom and constraints. A portal `visit/overlay/braid` is always fictional movement or representation, not a factual road/flight connection.

## Specific Tampa scene fixture

Geocode and verify North Dale Mabry / West Spruce intersection. Create real roadway lane/crosswalk/sidewalk geometry from accessible sources, preserve directional topology and traffic signal grammar; use known nearest-airport context (Tampa Intl) but do not hardcode an unverified aircraft route overhead. Determine camera origin and first character spawn in a pedestrian-permitted point from graph search. Load locally visible streets, storefront forms and mature texture/material library. Replace store names with fictional names derived from deterministic symbolic grammar. Nearby services and signs use event-driven names/narrative claims only; player and NPC proposals update *fictional* material instances, not source street graph.

## Global acceptance

- At least one successful machine-verifiable query in each broad world region and the poles/dateline/ocean edge cases; missing-detail response is correct and does not crash.
- Real Tampa road topology and factual source revision are logged and compared to actual adapter results; no fake match claim.
- End-to-end Overture/OSM ingest yields a sampled real-route matcher across at least two continents; report match rarity and projection loss.
- 3D streaming has bounded RAM/VRAM and grade transitions at walking, driving, portal and flight pace; block current texture/mesh quality must meet high fidelity rubric.
- Player approaching any target area gets sourced facts where known and explicitly fictional but visually refined fill where unknown; absent source data cannot be inferred as a specific real building.
