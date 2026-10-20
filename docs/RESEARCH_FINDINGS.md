# Measured research findings

The aggregate [findings.jsonl](../findings.jsonl) preserves the individual math/voice findings and adds source-backed geographic and sky negative results. Each record contains a reproducible fixture, observed evidence, scientific decision, next experiment and current source/build hash. Accepted results apply to the declared fixture. They do not establish human perception, scene fidelity, device performance or a new theorem.

| Experiment | Observed result | Decision and limit |
|---|---|---|
| Native diagonal convex QP versus actual GNU Octave 9.4.0 `qp` | Maximum primal difference 0; tolerance 1e−8 | Accepted for bounded separable convex quadratics. Negative curvature, inconsistent bounds and unbounded linear directions have explicit statuses. |
| Native RK4 decay versus Octave `ode45` | Final difference 9.6085e−12; tolerance 1e−8 | Accepted for the declared scalar decay fixture; not a general differential-equation guarantee. |
| Universal pure equilibrium | Matching pennies returns no pure equilibrium | Rejected. Mixed equilibria require a separate verified solver. |
| Fixed-lattice camera versus direct follow | Jerk about 25 versus 266.58 m/s³ at 24/30/60/90fps; tracking proxy error about 0.333 | Lower synthetic jerk accepted. Scene occlusion, image horizon, collisions and perceived cinematography remain unmeasured. |
| Authored compact-support weather field | Finite-difference divergence 5.3198e−14 s−1 versus 0.002 threshold | Accepted numerical fixture. Not measured atmospheric/weather fidelity or a full Navier–Stokes solution. |
| Neural phrase preparation/cache | 23 real clips; four voice identities; 41.047s in 251,549 Opus bytes; repeat cache hit 100% | Accepted local preparation measurement. Device onset and actual Oracle ARM throughput remain unmeasured. |
| Clean English ASR | Normalized WER 0 on two tiny clean fixtures with Moonshine and Whisper | Accepted for those samples only. No population accuracy estimate. |
| English ASR at synthetic 10dB white noise | WER 0.125 | Rejects generalizing clean exact recognition to noise. Real city noise remains untested. |
| Jordanian Arabic candidate through multilingual ASR | WER 0.333 on three normalized synthesized words | Current Arabic interaction fixture fails. Native, colloquial and spontaneous Jordanian speech need independent evaluation. |
| Kokoro int8 on local CPU | Two synthesis RTFs 6.86 and 3.77; about 344MiB peak process RSS | Rejects real-time synthesis for this local fixture. Human preference is unresolved. |
| Offline positioned sound mix | Seven source classes; zero adjacent-sample jumps above 0.15 | Accepted offline DSP fixture. Device buffering, masking, HRTF and human listening remain unverified. |
| Tampa–London route winner | Score 0.7100594; held-out p=0.39535 | Negative at α=0.05. A valid tested negative satisfies original G05; no rare resemblance is certified. |
| Tampa–Marina route winner | Score 0.6312459; held-out p=0.76744 | Negative at α=0.05. No causal or physical cross-city connection follows. |
| Blind four-star sky motif | Held-out p=0.17; Southern Cross template overlap 3/4 vertices and 1/2 edges | Negative/inconclusive rarity and partial vertex agreement. Traditional line geometry was not recovered. |

Route calibration uses seed31, 128 held-out null samples, and the same 16-candidate maximum search in each replicate. It omits lanes, plazas, building and POI features. Sky calibration uses 99 training and 99 held-out maximum searches; RA is randomized while observed declination and magnitude remain fixed. The sky source-ID/algorithm hash is frozen before the pinned Stellarium template is loaded. This controls the declared search, not all Milky Way structure.

Reproduce math with `python -m worldloom.numerics`, voice with `python tools/voice_benchmark.py`, geographic comparisons with `worldloom.geo.match_routes('tampa', 'london', seed=31, samples=128)` and sky with `worldloom.sky.discover(seed=42, null_trials=99)`. These commands can be expensive and intentionally remain outside normal game startup. Exact source revisions and witnesses are in [math_benchmarks.json](../evidence/math_benchmarks.json), [voice_benchmarks.json](../evidence/voice_benchmarks.json), [geo_match_tampa_london.json](../evidence/geo_match_tampa_london.json), [geo_match_tampa_marina.json](../evidence/geo_match_tampa_marina.json) and [sky_discovery.json](../evidence/sky_discovery.json).

Remaining measurable work: larger independent English/Arabic corpora; native-speaker Jordanian recordings and real traffic noise; blinded headphone listening; physical microphone and Samsung onset/dropout/power tests; actual Oracle ARM64 queue1-versus2 with PURL/Ollama/PostgreSQL health; richer geographic hold-outs/null controls; Gaia real-source ingest; controlled rendered camera/weather/audio/material fixtures. [acceptance.json](../evidence/acceptance.json) records the current full commissioning gaps independently of these research decisions.
