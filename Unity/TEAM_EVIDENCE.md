# Visual world / art and Sound team checkpoint

Commission revision **1.1**, SHA-256 **e9327cbf55e496f3ad5029e409d6201f68d6095753a5ad95c58328cb6e8a4104**. Owner: visual team; integrator owns git. Work started concurrently with portable mathematics/systems (§86.1). Changes restricted to `Unity/`; no index/commit/push operations performed.

Source reconciliation precedes implementation: common `governance/SOURCE_RECONCILIATION.md`, plus `IMPLEMENTATION_PLAN.md` identifies exact inherited sources, renderer/name conflicts and applicable clauses. No archive directives or scripts executed. No inherited art, voices, code or prior-attempt branch copied.

| Evidence | Verdict | Exact scope / limitation |
|---|---|---|
| `python3 Unity/Tools/generate_audio.py` | PASS | Three original deterministic PCM signals, hashes/peak/RMS in audio-manifest. Not a recorded sound library or speech. |
| `python3 Unity/Tools/check_fixture.py` | PASS | JSON/scene/meta GUID integrity and WAV bytes, frame counts, no integer clipping. `Evidence/portable-integrity.json`. |
| Tree-sitter C# grammar over eight sources | PASS | Syntax only in `Evidence/csharp-syntax.json`. No C# compiler or Unity API/type check available. |
| Pinned Editor release and URP/API source inspection | PASS | Official links in README. URP17.0.4 seen with same 6000.0 line; exact fixture package resolution unrun. Direct registry tar returned 404; no invented lock. |
| Native Editor import / shader compilation | BLOCKED | Host `aarch64`; no Unity Editor/UnityHub/license or supported worker access verified. |
| Android APK/AAB / install / native playback | BLOCKED | No build worker, Android toolchain/device or signing route verified. No APK produced. |
| §§35–45,49–54,75,78,90,92–94 native behavior/review | NOT_RUN | Source paths and scenario checklist provided; no rendered imagery, gameplay capture, speech, audition or native performance claim. |

Native source is an offline synthetic development fixture (§11), explicitly separate from production engine authority. Contains procedural street geometry/colliders, local controls, follow camera/occlusion query, independent authored walker schedules, passenger fixture, pause/settings/projections, bounded snapshots and spatial audio. Ordinary member only; no fabricated founder credentials (§2). Placeholder art, capsule actors, no human rigs, no proper seat animation, no authored conversation, no sourced Tampa topology, no production traffic/routing, no worldwide terrain/transport. It cannot pass close-up/native experience acceptance.

Fixes during review: created shader-retaining Resources material in Prepare; checked generated scene save result; guarded new-project settings array; bounded snapshot to 1MiB/256 events with monotonic sequences and bounded fields; replaced copy-over-save with File.Replace/initial File.Move; prevented paused UI actions; derive projection caption from ride state; cached three audio clips and reused player AudioSource. Snapshot backup exists, but restoration from it is not yet implemented. Atomic operation and all Unity APIs remain untested on Android.

Next: resolve exact pinned project on supported licensed Editor; capture compile/import failures and fix; create actual build/lock/hash; verify native checklist; acquire source-quality licensed region-specific art, rigs, motion and speech; connect verified Dark contracts through conformance fixtures; complete global data and every mandatory acceptance gate. Native blockers do not authorize a web substitute.
