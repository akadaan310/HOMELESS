# Independent final source review

Contract revision 1.1 / SHA-256 `e9327cbf55e496f3ad5029e409d6201f68d6095753a5ad95c58328cb6e8a4104`. Scope: HD-005.1,007,037–038,042,075,078–080,083,087,093–097. Reviewer owns delivery evidence only; application files reviewed read-only. This review does not certify C# compilation, Unity API compatibility, import, graphics or native gameplay.

`PYTHONPATH=portable python3 -m unittest discover -s portable/tests -v` independently passed six tests (coordinate axes/stratified round-trip, scoped Life replay/idempotency/policies, plate transport/refusal/inverse, population allocation/ranges/migration). Command output is `portable-independent.log`. Scope is synthetic bounded Python references. No globally sourced population, terrain coverage, collision-safe embodiment or authenticated founder role follows from these results.

`python3 -m unittest discover -s governance -p 'test_*.py' -v` independently passed five COP tests after the integrator corrected review findings; output is `cop-review.log`. The evaluator handles the documented bounded policy subset; it is not a complete prose constitutional compiler or production authorization service.

Read the Unity runtime source, Editor preparation/build method, assembly definitions, package manifest and Editor pin. No certain C# syntax error identified by inspection. Exact Unity 6000.0.62f1 / URP 17.0.4 APIs, serialized settings and package dependencies still require actual Editor import and compile. Current absence of Unity/JDK/Android SDK/device prevents execution; static inspection is NOT_RUN compile evidence.

Findings sent to the responsible integrator/visual worker:

- NativeBuild initially did not create `Assets/Scenes` and ignored `SaveScene` result. The integrator independently flagged this; require directory creation and a failure guard before claiming preparation.
- Fixture save initially loaded unbounded file bytes/history; require file/history limits and valid ordered event entries. Persistence still needs malformed-save, process-kill and backup restoration tests.
- File copying over the primary save is not an atomic commit and originally had no backup restore. No crash-safe persistence PASS is supported from source alone.
- Pause overlay initially left ride/sit buttons active, allowing mode and history changes while paused. Disable gameplay controls or guard their methods while paused.
- Diegetic projection initially announced a waiting car regardless of passenger/offer state. Derive the projection from the same current ride state as accessible controls.

Known scope limitations visible in code: primitive street/people/vehicle art, independent corridor walkers without production navigation or persistent identities, consented local passenger mode with witnessed relocation rather than animated boarding, no close-up imported animation/art, no globally navigable scene, no grounded spoken conversation, no production external AI/multiplayer authority. These are explicitly development fixtures and cannot pass §§88–94.

Required next verification remains clean supported Editor import, package lock generation, build log/exit/commit/hash, identified Android installation, 20-minute telemetry/thermal session and continuous native acceptance footage. All native gates remain BLOCKED/NOT_RUN until that evidence exists. Commissioner visual approval remains outstanding.

Follow-up source inspection confirms `Assets/Scenes` creation and a checked `SaveScene` result now exist. Restore now checks the 1 MiB file budget, 256 history entries, nonnull entries, increasing sequence and bounded kind/detail strings. These fixes address the specific static findings; they remain unexecuted in Unity. Backup recovery/atomic-save and pause/projection findings retain their stated status until separately verified.

Final follow-up: source now loads a Resources material template for shader retention, disables gameplay GUI while paused, derives ride projection text from passenger state, and uses File.Replace with backup (or initial File.Move). These address the reported source-level findings. Actual platform atomicity, backup restoration, built shader retention and native control/audio behavior remain unverified. Reran the six-test portable suite after these changes: PASS. No compiler or runtime result is implied. `reviewed-unity-hashes.json` pins the inspected C#/assembly/package/version bytes.
