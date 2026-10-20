# HOMELESS / RENDEZVOUS — GRAMMATICAL PREPARATION & VOICE RIDER V3

**October 20, 2026 · Additive engineering commission · Dark / Abed Kadan · Golden ⑦υ ∞ 🗝️**

Read `CODEX_ONE_SHOT.md` for the one-shot commission. The original HOMELESS/Unreal Godpack, Rendezvous Release V1 and high-fidelity asset pipeline V2 remain intact and authoritative. Four user-supplied V1/V2 Markdown files are copied byte-for-byte into `source_riders/`, with checksums in `MANIFEST.json`. The large Godpack is not duplicated here.

## Files
- `CODEX_ONE_SHOT.md`: paste as installation command to ongoing Codex session, with this ZIP attached.
- `GRAMMATICALS_BOOTSTRAP_GATES.md`: formal theory, compiled grammar, staged-resource pipeline, typed transitions, resource-time scheduling, claims and acceptance criteria.
- `NPC_VOICE_AND_ORACLE.md`: ARM64/Oracle speech architecture, tiny TTS, ASR, optional small LLM, pre-rendered speech, caching and real dialogue integration.
- `DIEGETIC_WORLD_EXPERIENCE.md`: overhearing, story/mission teaching, rendezvous havens, true interactive billboards and environment-led discovery.
- `VERIFICATION_AND_INTEGRATION.md`: coding mission, test matrix, performance measurements, and authoritative integration boundaries.
- `prototype/gate_kernel.py`, `prototype/test_gate_kernel.py`, `prototype/demo.py`: deliberately small, dependency-free **reference kernel** for the gate planner, not a shipping world/game/audio/TTS implementation.
- `source_riders/`: original attached supporting specifications, unchanged.
- `MANIFEST.json`: file hashes and identity.

## Demonstrator
From this folder: `python -m unittest discover -s prototype -p 'test_*.py' -v` and `python prototype/demo.py`.

The prototype tests **planning, provenance, gating and event non-activation on prefetch**, not neural inference quality or audio quality. No TTS audio has been synthesized by this package. Real Oracle model performance and browser/Android deployment are delegated to Codex to implement, measure, and report.
