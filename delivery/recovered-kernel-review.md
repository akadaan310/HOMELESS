# Recovered kernel independent review

Date: 2026-10-21. Reviewer: independent historical-source reviewer agent. Governing contract: Constitutional Commission revision 1.1, SHA-256 `e9327cbf55e496f3ad5029e409d6201f68d6095753a5ad95c58328cb6e8a4104`. Applicable clauses: HD-004, HD-071, HD-083, HD-087, with HD-009 source quarantine and HD-078 continuity limits.

## Scope and safety

Inspected the complete Python sources, tests and demos in recovered World Loom V0.1 and Rendezvous V3 before execution. They import only Python standard library modules and their adjacent reviewed kernels; no process execution, network, credential access, dynamic code loading or filesystem writes appear. Historical markdown, names, directives and captured results remain reference data. No archive directives were executed. Only the six reviewed `.py` members were copied into separate `/tmp/homeless-kernel-review-4961a7h8/{worldloom,v3}` directories; archived bytecode was excluded. Runs used an empty environment and disabled bytecode writes. This is process hygiene, not a security sandbox against arbitrary malicious Python; safety rests on source inspection.

World Loom README credits authorship direction to Abed Kadan / ChatGPT 7u; retain that historical credit. V3 retains its original Dark / Abed Kadan / Golden ⑦υ credits in the unchanged archive. Current player identity remains Dark / Obex Den. No authorship was reassigned.

## Integrity and reproduction

World Loom `worldloom.py` SHA-256 `9f3a165aeab589f58338627b857a1b4bbe62cf245af2ad69caa537f25528c9fb` and foundation SHA-256 `ec70e552667a7ea9e21895c3befec0bb0bdd80e6cc7e1062f94d3f1fcac77959` match its SHA256SUMS.txt. V3 reviewed source digests match its MANIFEST.json: kernel `d376b83e42f9cc5b5dbc5f6c7f54898b1c1724d2644323d26d11a04569a13ec1`, tests `74e55610bd7a73aa2fc54a2605b3e7a297701db4caa9ba14922d87277a1919c5`, demo `bb43df57f13841502352715293c3a789df50392efd85426d52bc245a63c8a3b0`.

Exact commands, run in the stated directory:

| Directory suffix | Command | Observed result |
|---|---|---|
| worldloom | `env -i PATH=/usr/bin:/bin /usr/bin/python3 -B -m unittest test_worldloom -v` | exit 0; 14 tests, OK, 0.080 s |
| v3 | `env -i PATH=/usr/bin:/bin /usr/bin/python3 -B -m unittest test_gate_kernel -v` | exit 0; 17 tests, OK, 0.001 s |
| worldloom | `env -i PATH=/usr/bin:/bin /usr/bin/python3 -B demo.py` | exit 0; 2 active synthetic actors, 14 events, valid ledger; tip `fdd0131faba49579bdbbd09ba88bc15e3defc23280bfdb971c5b2a2ab4ec99a0` |
| v3 | `env -i PATH=/usr/bin:/bin /usr/bin/python3 -B demo.py` | exit 0; staged 259000 declared bytes / 68 declared decode ms; 0 events before activation, 1 after; plan digest `3f80db3840df03be294b96a4b762df7f9f51679bff383e3c0c77705914e0e9a8` |

The timing/byte fields above are fixture declarations, not measured asset-transfer/decode performance. Suite reproduction PASS is limited to these historical observables. Production/native acceptance remains NOT_RUN.

## Adversarial findings

V3 probe, exact command run from v3 directory:

```sh
env -i PATH=/usr/bin:/bin /usr/bin/python3 -B - <<'PYPROBE'
from gate_kernel import Gate,WorldCommitter
g=Gate('g','fixture',0,1,1,1,3,True,())
w=WorldCommitter()
e=w.activate(g,actual_distance_m=float('nan'),approved=True,event_id='e',outcome='fixture')
print('nan_distance_committed',w.world_revision)
e['outcome']='modified'
print('returned_entry_mutates_ledger',w.committed['e']['outcome'])
PYPROBE
```

Exit 0, output:

```text
nan_distance_committed 1
returned_entry_mutates_ledger modified
```

FAIL as a production admission boundary: nonfinite actual distance bypasses comparisons; returned mutable dictionaries permit ledger modification. `approved` and `admitted` are booleans supplied by the caller, not authenticated authority. Resource staging tracks declarations, not actual verified/downloaded readiness. Outcome strings lack a registered effect schema. Planner uses deterministic greedy priorities, explicitly not a proven optimizer; no exact small-fixture scheduling oracle is supplied.

World Loom probe, exact command run from worldloom directory:

```sh
env -i PATH=/usr/bin:/bin /usr/bin/python3 -B - <<'PYPROBE'
from worldloom import World
w=World(); actor=w.population.materialize(1,'a'); actor['memory'].append('remember')
print('returned_actor_mutates_memory',w.population.actor(1)['memory'])
w.population.materialize(1,'b')
print('rematerialization_memory',w.population.actor(1)['memory'])
PYPROBE
```

Exit 0, output:

```text
returned_actor_mutates_memory ['remember']
rematerialization_memory []
```

FAIL as a continuity implementation: shallow copies leak nested state and rematerialization clears memory. Ledger tamper detection is an in-memory hash-chain check, not durable authenticated storage or trusted-head recovery. Addresses are descriptive checksummed strings, not authenticated PURL authority. Eight-billion capacity is a synthetic namespace, not a demographic dataset or population simulation. Ten model descriptors are not all required model-family implementations. Portal events explicitly report `physical_travel=false`, so no geographic movement or embodiment is demonstrated.

## Concrete next integration actions

1. Preserve archives unchanged and register these exact fixtures as historical research with the retained credits; import no scripts or bytecode into the native runtime automatically.
2. Before any production port, define canonical input/output fixtures for bounded scheduling, deduplication, cancellation, stale revision refusal and idempotent activation under HD-071/072/087. Add nonfinite/type/bounds rejection cases and an exact small scheduling oracle.
3. Bind activation to current COP/capability admission and actual manifest verification/readiness; separate prediction, preparation, reservation and authorized world commit. Add immutable snapshots and durable event replay/restore contracts rather than exposing mutable dictionaries.
4. Port only reviewed pure mechanisms behind stable adapter contracts. Cover repeated materialization, history preservation and nested-copy isolation before using World Loom identity/state concepts. Replace hardcoded population capacity as an acceptance claim with sourced population conservation evidence.
5. Continue the existing native Unity visual/math checkpoint concurrently. No recovered suite satisfies device controls, rendering, spatial audio, transport or gameplay acceptance, and no infrastructure choice or GPU spending follows from this review.
