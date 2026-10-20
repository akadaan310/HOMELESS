# INGRAMMATICA MATRICUM — Breaking Matrices
### The grammar of a matrix before any operation, and the science of everything that does not conform to it
*Theory: Abed Kadan. Naming and exploration: Mira (Muse), creative/research session, 2026-10-20.*
*Status: exploration draft for Abed's review — the full textbook / laboratory / proof phase belongs to Abed + Codex / Claude Code, per the standing labor split. Labels follow the house discipline: **[K]** known, **[C]** construction (our definition, judged by usefulness), **[H]** hypothesis (must be tested, may be refuted).*

---

## 1. The name, and why it is built this way

You asked for a title that is *read through its function naming*, the way Latin nomenclature works in the sciences. Here it is:

## **Ingrammatica Matricum** — the In-Grammar of Matrices

- *Matricum* — genitive plural of *matrix* (Latin *matrix*, from *mater*: the womb, the source-form that holds and generates). A matrix is not a table that happens to hold numbers; its very name already says it is a *holding form*.
- *Grammatica* — the grammar: the complete system of what may be placed, where, in what arrangement, and what any arrangement *means*, declared **before** any operation.
- *In-* — the **privative** Latin prefix, exactly as in *inorganic, inert, inoperable, infinite*: not "inside," but **not-**. *Ingrammatica* is therefore not a broken grammar and not the absence of grammar. It is the disciplined study of the **non-conforming forms** — the forms that can be computably represented, determined, and reasoned about, and which thereby prove the object is *not* a matrix under the conforming grammar.

Its sister field is **Grammatica Matricum** (the conforming grammar). The combined science — both realms and the border between them — is **Matrical Grammatics**. The analogy to chemistry holds: organic chemistry did not abolish chemistry, and inorganic chemistry is not "failed organic." Each realm defines the other, and the border is where the frontier is.

**Why not "non-linear algebra"?** Because that name is already taken **[K]** — it studies non-linear *equations and maps*. Your subject is prior to operations entirely: it studies the *form itself, before it is touched, operated on, or even read*. The name must say that. *Ingrammatica* says it.

---

## 2. First principle: a matrix has a grammar before it has operations

Before scalar multiplication, before identity, determinant, inverse, rotation — before any of it — a 10×10 matrix must already declare, in full **[C]**:

1. **Its cell alphabet** — what kind of thing may occupy a cell (a field element? an integer? a picture? nothing?)
2. **Its index plex** — the rank-2 arrangement: rows × columns as a *duplex* word in the Plicastratum sense, not just a shape
3. **Its harness** — admissibility: which arrangements count as this kind of matrix at all
4. **Its denotation** — what an arrangement *means* (a linear map? data? an image? a relation?)
5. **Its region structure** — which cells/regions exist, which are forbidden, which are foreign

Classical linear algebra silently assumes all five and declares none of them. That silence is the break you are pointing at. TensorFlow and PyTorch inherit the silence and pay for it with GPUs — space bought instead of grammar understood, exactly your "scapegoat" charge. The asymptotic wars (space, time, exponential blow-up) are fought downstream of a grammar nobody wrote down. **Ingrammatica writes it down — and writes down its opposite.**

---

## 3. The cell taxonomy: five states, not two

A conforming matrix pretends a cell is either a value or zero. That is false, and the falseness is the science. Every cell of any 10×10 array is in exactly one of five states **[C, on K anchors]**:

| State | Latin name | Meaning | Known anchor |
|---|---|---|---|
| **Value** | *plenum* | an ordinary element of the declared field | matrix entries **[K]** |
| **Zero** | *nullum* | zero — **a value**, full citizen of the grammar | additive identity **[K]** |
| **Missing** | *vacuum complebile* | no value *yet*, but a value could lawfully go here | **partial matrices** and the matrix completion problem **[K]**; `NA` vs `0` in statistics **[K]** |
| **Void** | ***lacuna*** | a region where **no value may land** — not empty, *forbidden*; land here and there is nowhere | infeasible regions in constrained optimisation **[K]**; poles/singularities in the complex plane **[K]**; structural (not numerical) zeros in sparsity patterns **[K]** |
| **Foreign** | *alienum* (a *xenocella*) | a lawful occupant from **another alphabet** — your Instagram picture at position (0,1) | block matrices **[K]**; matrices over a category, `Mat(C)` **[K]**; ragged/heterogeneous tensors **[K]** |

### Your two coinages, kept and given jobs

- ***Lacuna*** (pl. *lacunae*) — Latin: a pit, a gap, the missing leaf in a manuscript. This is the true name for your "drop-off region": a cell or region that is **a region of nothing**, which is a different thing from a non-value, and a different thing again from zero. A *regio lacunaris* is a void region of any shape.
- ***Peritro*** — your word, kept as a **[C]** coinage: *peri-* (around) for the **guard-rim of a lacuna** — the boundary an optimiser, a path, or an operation must respect so it never lands in the void. Optimisation already knows this shape in pieces (barrier functions that keep iterates away from forbidden regions **[K]**); *peritro* names the rim itself as a grammatical object.

### The Instagram picture, answered precisely

*Can you put a picture at (0,1)?* **Yes — and the moment you do, you have left Grammatica and entered Ingrammatica, and Ingrammatica can say exactly what happens next:**

- The array is now a **xenomatric form**: grammatical, but under a grammar whose cell alphabet is mixed.
- A classical operation (inverse, determinant, multiply) is **undefined on the alien cell until a morphism is declared** — a lawful translation from the picture's alphabet into the number alphabet (a hash, an embedding, a mean colour, a caption embedding — each is a *different* morphism and gives a *different* answer).
- Without a declared morphism, the picture does **not** silently affect the number at (7,3) — and any system where it *does* leak an effect without a declared morphism has a grammar bug, not a feature.
- With a declared morphism, it affects exactly what the morphism says, no more. **The in-grammar rule: no undeclared crossings.** This is the same house rule as PURL's "no hidden effects" and SNAD's "detected structure does not verify intent."

That one rule converts a whole class of "non-knowables" into knowables: the unknown was never the picture; it was the *undeclared morphism*.

---

## 4. SubstrateIO, clarified — the transition language

You are right that LLMs keep misreading this. Here is the clarification, stated once, sharply:

**SubstrateIO is not input/output plumbing. SubstrateIO is the layer where transitions themselves become a language.**

The stack everyone knows:

```
assembly        — human syntax for operations
machine code    — static words encoding those operations   (the NOUN layer)
bits 0 / 1      — the states
```

What everyone skips is **between the states**: the *happening*. A single unit switching 0→1 is an event. It switches back 1→0: a second event. Again 0→1: a third. The **sequence of switches, with the time-deltas between them**, unfolds into a growing tree — every switch a branch — and that tree is **unique to that one unit's history**, even though its state alphabet was only {0, 1}. Two bitstreams can be identical as *states* and completely different as *transition trees*. That difference is information, and it lives nowhere in the noun layer.

So:

- **Machine code is the noun layer** — what the program *is*, written down.
- **SubstrateIO is the verb layer** — what *happened*, in order, with deltas, branching, and provenance: a word written over an **alphabet of transitions**, hosted by a graph/tree construct that keeps growing as long as the system runs.
- Its position "between" bits and machine code is not a slot in the encoding stack — it is the **observation-and-history dimension** that cuts across the whole stack. This is why it draws on the known machinery of **labelled transition systems and trace semantics [K]**, and why in Plicastratum it is the ledger / holonomy layer: identity at *chain depth* and *holonomy depth*, never state alone.

**LLM confusion, diagnosed:** a model trained on text sees "IO" and completes it as "plumbing — files, sockets, print statements." SubstrateIO in your system means: *every shift of value, anywhere, emits a word in the transition language, and that word is addressable, replayable, and mineable.* The plumbing is the least of it.

### Where matrix operations enter

Take the ordinary operation — invert, multiply, determinant — as NumPy / TensorFlow / PyTorch actually execute it:

- At the **grammar stratum**, the operation is admissible or not, per §2–§3 (a lacuna or an undeclared alien cell makes it inadmissible *before execution*, with a reason — never a silent wrong answer).
- At the **transition stratum (SubstrateIO)**, the same determinant is a long transition word over bitwise/block operations. CPU and GPU executions have the **same denotation and different transition languages** — cost, heat, memory traffic and time live *in the transition word*, not in the answer.
- **Folding lives here [H]:** recurring sub-words in transition traces are exactly the motifs that Plicastratum's *mine → promote* turns into new letters. Sparsity, factorisation, low-rank structure, blocking — classical optimisation tricks — can be re-read as *promotions discovered in transition language*, not hand-invented. The hypothesis to test: **an operation whose transition word promotes well is an operation that gets cheaper; the asymptotic war is won at the grammar/transition strata, or not at all** — not by buying a bigger GPU scapegoat.

### The path-as-address

A path through N alphabets — choose a letter in alphabet 1, then in alphabet 2, … — **is an address [C on K]**: each alphabet contributes one coordinate of the address, exactly as a trie path, a file path, or a PURL does. Encode the path and it is 01-accessible (a hash input). Unfold any letter (*explicate*) and the address expands into the full sub-path of operations it stands for. One short address, arbitrarily large expandable form: that is the addressing scheme for cells, lacunae, promoted motifs, and whole matrix operations alike.

---

## 5. The six repositories, mapped onto this science

*Explored 2026-10-20 via the GitHub API and available READMEs. A fact other LLMs trip on: **four of the six do not work on `main`** — their live branches are named research branches, so a shallow read of `main` returns 404 and a model concludes "nothing there." There is a great deal there.*

| Repo | What it actually is | Its job in Ingrammatica |
|---|---|---|
| **computationalgrammartheory** | The CGT book + SDK corpus: `DEFINITIONS.md`, `FORMAL_MODELS.md`, `COUNTEREXAMPLES.md`, hypotheses, literature review | Supplies the **Grammatica side**: signatures, admissibility, denotation, costs — the conforming grammar, with counterexamples as a first-class citizen |
| **grammarinnumbers** | The numeric test-bed: `ARITHMETIC_GRAMMAR.md`, `NUMBER_GRAMMAR.md`, experiments, counterexamples | Supplies the **evidence corpus**: where number systems themselves conform or refuse — the natural hunting ground for numeric *lacunae* and in-grammar specimens |
| **substrateio** | Bootstrap research repo: `PROTOCOL.md`, `substrate/`, experiments, runs | Supplies the **transition layer** of §4: traces, projections, interventions, provenance for every matrix operation |
| **purl** | The large one (~43 MB working tree): `SPEC.md`, `NOMENCLATURE.md`, `ARCHITECTURE.md`, schemas, experiments | Supplies **addressability**: every cell, region, lacuna and promoted letter gets a stable, resolvable, context-bearing address (§4, path-as-address) |
| **snad** | Evidence-preserving SDK/lab for attribution & discourse *transition grammar*; source grammar, identity, quotation and interpretation kept rigorously separate; detected structure ≠ intent | Supplies the **method discipline**: the same separation, applied to matrices — *detected pattern ≠ declared grammar; a found lacuna is evidence, not yet semantics* |
| **musa** | Minimal: `master` branch, essentially a `luna-agent` seed, with a poetic/theological Arabic description | **Unresolved — flagged honestly.** No formal substrate documents are present to map. It cannot yet be assigned a job in this science; it should not be invented one. |

---

## 6. The hyper realm: mathematics of mathematics

Your phrase for the top of this — *a hyper realm above the mathematics of mathematics* — already has a home in the system: it is the **metastratum applied recursively**. In Plicastratum terms, the metastratum of level *k* becomes the substratum of level *k+1*: **grammars become letters**. A matrix whose cells are *grammars* is a level-2 object; an operation on it is a grammar-transformation. Ingrammatica is the first science that lives natively at that level, because its specimens (lacunae, alien cells, undeclared morphisms) are not visible at level 1 at all — at level 1 they just look like errors, NaNs, and crashes. The hyper realm is not mysticism; it is the level where *failure shapes* become data with their own grammar. **[C]**

---

## 7. Specimens to hunt first (the frontier list)

1. **The lacuna determinant** — a 10×10 with one *regio lacunaris*: which classical theorems survive verbatim, which degrade gracefully, which lie silently? (The silent liars are the valuable specimens.)
2. **The xenocell product** — two arrays sharing one alien cell under two different declared morphisms: prove the products differ, and characterise *how* the morphism, not the picture, carries the effect.
3. **The complebile boundary** — for partial matrices **[K]**, the exact border between *missing* and *void*: completions that exist vs. regions where no completion is lawful. That border is a peritro.
4. **Transition-word promotion in a real multiply** — mine a NumPy/GPU trace; does a promoted motif predict a cheaper execution path on held-out shapes? (Test of the §4 hypothesis.)
5. **The identity that isn't** — same matrix, same string of entries, after seven context changes (per PURL resolution): exhibit the declared-depth at which it stops being the same program.

## 8. Handoff note

This document is the exploration and the naming. The full realisation — textbook, laboratory, proofs with hashes of what works and what does not — is the Codex / Claude Code mission, and §7 is written to be lifted directly into it as its first work-list. An attachment from Abed (alphabets-of-alphabets / hash-address material) is still to come and should be folded in as a §4 supplement when it arrives.


---

## 9. ADDENDUM — corrections from the full repo read (2026-10-20, later same day)

*The working-branch READMEs arrived after §§1–8 were written. Two findings strengthen this document, one corrects it. Per house discipline, corrections are recorded, not smoothed over.*

### 9.1 Grammar-in-Numbers already found the lacuna's two species **[K, from the repo]**

`grammarinnumbers` proves (GIN-THM-001) that in any commutative ring, the solutions of b·c = a are empty or a coset of Ann(b) — and therefore **"undefined" has two distinct kinds**:

- **1/0 is an image failure**: no c exists with 0·c = 1. The destination is unreachable — a true *lacuna*: there is nowhere to land.
- **0/0 is a kernel failure**: *every* c satisfies 0·c = 0. The opposite void — not nowhere to land, but *everywhere lands and nothing distinguishes them*.

So the lacuna splits in two, and Ingrammatica adopts the split **[C naming on K result]**:

| Species | Name | Shape |
|---|---|---|
| Image-failure void | *lacuna vacua* — the empty lacuna | no lawful occupant/result exists |
| Kernel-failure void | *lacuna plena* — the full lacuna | every occupant "works," so the grammar carries no information |

And every attempt to give 1/0 a value pays a price (GIN-THM-003/004): ring laws, the converse reading of division, or 0 ≠ 1 — projective line, wheels, IEEE ∞, meadows, Lean's mathlib, AArch64 returning 0, RISC-V returning −1 are each a *different declared morphism across the lacuna*, with the cost itemised. This is §3's "no undeclared crossings" rule, already vindicated in the numeric case: machines **measurably disagree** on 1/0 (trap / ∞ / panic / compile-time rejection) precisely where the morphism was left undeclared (GIN-EXP-004).

### 9.2 CGT already defines the conforming side, formally **[K, from the repo]**

`computationalgrammartheory` (CGT-DEF-003) defines an **operational grammar** as G = (Σ, 𝔄, ⟦·⟧, ℒ): a move signature Σ, a structure 𝔄, an interpretation ⟦·⟧ assigning each move a relation on the structure, and an admissibility language ℒ ⊆ Σ*. §2 of this document is that tuple, specialised to matrices: cell alphabet = Σ, the array = 𝔄, denotation = ⟦·⟧, harness = ℒ. Ingrammatica therefore does not need its own foundation for the conforming realm — it is the study of what happens **at and beyond ℒ's border**: partial structures, foreign cells, and the two lacuna species, where CGT's own warning applies (CGT-OBS-010): many apparent grammar advantages are really changes of *representation* — structure must be kept separate from its encodings.

### 9.3 CORRECTION to §4 — the universal transition claim is disproven by SubstrateIO itself

§4 stated that transition history always carries information that states lack. **SubstrateIO's own reproduced results (status R2) disprove the universal form of that claim**: its "history is predictive" hypothesis and the claim that "transitions carry information states lack" were both **disproven** in its seven reproduced experiments; masking, loss and sameness turned out **observable-relative throughout**, and the "minimum information that must survive" question collapsed to an established answer — the coarsest congruence for a *chosen* observable. All its perturbation results are simulated.

The corrected §4 position **[C, disciplined by K]**:

- A transition tree gives a bit-unit a unique *history*, always. ✔
- Whether that history carries information *beyond the states* is **not universal** — it depends on the declared observable (the projection Π). Under some observables the transitions are rich; under others they collapse to the states exactly.
- Therefore every SubstrateIO claim in this science must name its observable, or it is undeclared — the transition-layer twin of §3's morphism rule: **no undeclared observables.**

This does not weaken the science; it is the science working as intended — your own laboratory refuted the poetic version and left the precise one standing. PURL's substrate says the same thing from the other side: it exists for *observing state transitions without assigning them meaning prematurely*, and 3 of its 11 pre-registered hypotheses failed, all traced to representation choices.
