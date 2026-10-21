# Dark portable references

Commission revision 1.1; SHA256 `e9327cbf55e496f3ad5029e409d6201f68d6095753a5ad95c58328cb6e8a4104`.

From repository root:

```sh
PYTHONPATH=portable python3 -m unittest discover -s portable/tests -v
PYTHONPATH=portable python3 portable/verify_numerics.py
```

The first command needs Python 3.10+ standard library. Numeric comparison also needs GNU Octave (measured with 6.4.0). These packages are **pure bounded reference fixtures**, not authoritative production services or Unity substitutes.

- `dark.population`: exact rational Hamilton/largest-remainder allocation; ties by sorted shard key, contiguous stable ranges, lazy individual realization, separate resident/present counts and migrations. Empty/all-zero weights refuse. Realizing a range member is not simulating a person. No selected global demographic epoch/data has been ingested.
- `dark.geo`: WGS84 geodetic degrees + ellipsoid height meters to binary64 ECEF; orthonormal ENU transform and its inverse. ±180° longitude is accepted; no longitude wrap silently changes invalid input. Poles have longitude-defined east convention. No geoid, terrain, source street geometry or global tiles.
- `dark.life`: seven test entity kinds, compact policy/continuity records, scoped observation memory and deterministic ordered hash chain. Curious/reserved policies are simple authored state machines. Snapshot replay checks a supplied head and final observable state. It is tamper evidence relative to a trusted external head, not an operator-proof database or authentication. Snapshot files must be trusted/validated at a production boundary.
- `dark.plates`: transactional bounded undirected edge replacement, stale-version refusal, explicit per-occupant policies and reachability witness. Carriage is a **discrete reference transform**, not native continuous collision validation. Relocation stores declared fixture authority/time but does not authenticate it. Boundary straddlers refuse. Inverse restores geometry/connectivity only while the resulting state matches its witness, and advances revision; it does not rewind authority time. Native physics, actual two inhabited plates, vehicle/attachment propagation, crash persistence and authorized operator checks remain required.

These mathematical fixtures are labelled synthetic. The graph has no verified Tampa coordinates/connectivity. The `Population(17, ...)` test has 17 synthetic estimates, one persisted identity/history and zero active/visible/voiced actors; it is not a world population result. The source archives stay outside the repository; historical research suites run only after source inspection in `/tmp`.

Reviewed foundation suites are reproducible without executing archive installer scripts:

```sh
python3 portable/reproduce_foundations.py --run-reviewed --suite v3 --work-dir /tmp/dark-v3-repro
python3 portable/reproduce_foundations.py --run-reviewed --suite tashkil --work-dir /tmp/dark-tashkil-repro
# In an isolated environment with numpy, scipy, nltk and shapely installed:
python3 portable/reproduce_foundations.py --run-reviewed --suite ingram --python /tmp/homeless-reference-venv/bin/python --work-dir /tmp/dark-ingram-repro
python3 portable/reproduce_foundations.py --run-reviewed --suite realms --python /tmp/homeless-reference-venv/bin/python --work-dir /tmp/dark-realms-repro
```

Use new `/tmp` directories. The runner verifies pinned original archive hashes, rejects path traversal/symlinks, excludes executable pickle caches, uses an explicit reviewed test allowlist and 60-second caps, and preserves exit logs. It never follows archive agent instructions. Installing dependencies is separate; captured versions are in `evidence/reference-dependencies.log` and `reference-shapely-dependency.log`.
