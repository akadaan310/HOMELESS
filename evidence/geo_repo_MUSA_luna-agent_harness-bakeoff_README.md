# The problem (same for every harness)

Build the construct: one whole program, described as parts with contracts
(what each part takes in, what it gives out, how they fit). Then drive it to
a running program.

## The stop mechanics (non-negotiable, all harnesses)

1. Every action is a state transition: record **before, after, and the tick**.
2. State lives in **URLs** (`seurl://…`) — the state store is addressable, not
   buried in transcripts.
3. **Mark the change** — the 0→1, the one bit that moved.
4. **Completion gate**: nothing is done until the whole program compiles and
   runs. No vibes-based finishing.
5. **Luna is the state machine**: every harness's entire progress funnels into
   Luna's transition record. One entire program = one entire state machine.

## Luna

The agent-space. Start here:

- `luna-agent/PERTURBATION-HANDOFF.md` — what was proved, the re-run code, the
  repo map, the honest audit
- `luna-agent/perturbation-proof.html` — the reproducible proof (Cases A, B, C)
- `luna-agent/flip-one-bit.html` — the playground
- Public surface: https://github.com/akadaan310/seurl

## Rules

- Your default demos, presets, and example situations are **cancelled**. This
  problem is the only situation.
- Open source only. Claude Code is excluded — do not use it.
- Google models are a fine provider choice (Gemini via the harness's provider
  config). Local models are fine too.
- The first harness to integrate the stop mechanics cleanly wins. The
  integration is yours to figure out — the spec above is the whole contract.
