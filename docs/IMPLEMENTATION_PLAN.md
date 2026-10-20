# HOMELESS commission implementation plan

Goal: deliver all executable modules this machine supports, preserving the release specification.
Spec: masterpack-v1, SHA256 263e7c172e2a9ec9fabb6e916dd6fef03226fa3e21cb78c59c2fe42a0b98db95.

The user explicitly selects autonomous one-shot execution; the written commission supersedes interactive design/plan approval gates. The fresh clone and dedicated codex/one-shot-implementation branch isolate this work.

Architecture: independent Python World Loom SDK with native bounded numerical kernels; CBOR Unix IPC; durable SQLite ACSP journal; restricted process workers; Unreal C++ adapter; static browser and Android companion. Sources and effect projections retain distinct provenance.

1. Preserve and hash all inputs; safely extract historical archives, run their tests, record reconciliation.
2. Implement SQLite hash-chain continuity, scoped authentication, pure PURL reads, typed SEURL dispatcher and framed CBOR IPC. Test duplicates, conflicts, restarts, malformed input and unauthorized writes before code.
3. Implement real BusyBox/bubblewrap shell, QuickJS and Wasmtime workers with bounded resources; test pipes, proposals, isolation, timeout, imports and replay.
4. In parallel build generated typed grammars/NPCs, grounded global geo/sky, native mathematical/audio/weather systems, Unreal adapter/assets, and web/Android delivery. Each lane owns separate files, tests, and evidence.
5. Integrate through JSON-serializable APIs. Persistent effects use typed authority checks and causal history. Web default binds loopback and has no implicit founder privilege.
6. Build native binaries, WAV assets, static web output, actual APK if downloadable toolchain runs. Cook Unreal only with actual engine and assets.
7. Run all tests plus real daemon kill/restart, browser flow, numerical oracle and artifact hash checks; acceptance has pass/fail/blocked for every ID.
8. Independent review, fix demonstrated defects, rerun affected checks, commit and push branch with artifact outputs.

Review focus: forged founder identity, duplicate IDs with different payload, hash-chain corruption, cross-session reads, worker host escape, nonfinite/oversized inputs, offline/server conflicts, source facts confused with authored effects.
