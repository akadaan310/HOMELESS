# In-Grammar: Foundations of a Generative System Without a Language Model
### Nine subject-agnostic pillars for alphabets of alphabets, contextual meaning, harnessed generation and history-bearing computation
*Theory and direction: Abed Kadaan. Formalisation, experiments and reference implementation (`ingram/`): this document.*
*Research specification v0.1, 2026-10-20. It continues `RELATIONAL_GENERATIVITY_FOUNDATION_V0_1.md` and `PLICASTRATUM.md`.*

---

## 0. Reading discipline

Every claim carries one label, as in Plicastratum:

| Label | Meaning |
|---|---|
| **[K] Known** | Established mathematics, linguistics or computer science. Cited. Reproduced in code where possible. |
| **[C] Construction** | A definition we choose. It is useful or not; it is never true or false. It is judged by what it lets us build and test. |
| **[H] Hypothesis** | A claim about what will happen. It must be tested and may be refuted. Refutations go in §12. |
| **[M] Measured** | A number produced by a script in `experiments/`, reproducible from the open data in `data/`. |

The conformance suite (`tests/test_ingram.py`, 19 tests) encodes each pillar's acceptance criteria. Nothing below is called a new theorem. What is new is the *assembly*: one kernel, nine pillars, and the measurements on real data.

---

## 1. The idea, and the name

Natural text is produced by two different kinds of structure at once.

1. **Grammar (G).** The rules that can be *written down*: which arrangements are admissible. They are computable and checkable, and they yield a verdict with a reason (CGT-DEF-003). Grammar is generatively determinable. Given G, the admissible language L(G) is fixed.
2. **In-grammar (I).** The structure that lives *inside* usage and is never written as a rule. It covers which admissible word follows which, in whose company, and how often, so that "the apple fell from the tree" is natural and "the apple fell from the theorem" is admissible but strange. Formally I is a **conditional measure on the admissible language**, I(w | history, context).

**The chemistry analogy, made exact [K].** "Organic" chemistry was named for compounds thought to need a *vital force*. Wöhler synthesised urea from inorganic salts in 1828, and organic chemistry became ordinary chemistry: the chemistry of carbon compounds. The in-grammar holds the same position. It feels "alive", like usage, tone and naturalness, but it is a measure, and measures can be estimated, factored, constrained and computed. An n-gram table, a recurrent network and a transformer are three estimators of the *same object* I. **An LLM is a very large estimator of the in-grammar with no explicit grammar.** That is the precise sense of the user's term *in-LLM*: generation assembled **inside** explicit structures, with I as one component among several rather than the whole system.

**Natural form [C].** For a context c and a plan p (what must be said),

$$
\mathrm{nf}(c,p) \;=\; \arg\max_{w\,\in\,L(G)}\; \log I(w\mid c) \;+\; \beta\,\mathrm{anchor}(w,p) \;+\; \gamma\,\mathrm{field}_c(w)
$$

Grammar alone gives admissible nonsense ("colorless green ideas sleep furiously", Chomsky 1957). In-grammar alone gives fluent drift with no guarantees. The **product** is the object of study, and it is computable whenever G is finite-state and I is finite-order: generation is a search over the product automaton (Barrett, Jacob & Marathe 2000; CGT-THM-001). Inadmissible continuations are pruned *before* scoring (mechanism M-PRUNE).

**Theory of forms, computable [K → C].** If forms exist, they need predicates, and the predicates need to be computable. One reading of Plato's question has a precise answer. Fix an observable: what a listener, a grammar or a test can distinguish. Two expressions have **the same form** iff no context distinguishes them under that observable. That relation is the **syntactic congruence**. Its classes are the forms.
- **Myhill–Nerode [K]:** a language has finitely many forms (right-congruence classes) iff it is regular. The forms *are* the states of its minimal automaton.
- **Harris's distributional hypothesis (1954) [K]:** words with the same contexts are the same form. Embeddings are approximate, metric versions of this congruence (§P5).
- **SubstrateIO H-006 [K]:** the minimum information that must survive is the coarsest congruence for a chosen observable.

So **a form is a quotient class, and a predicate on forms is any invariant of the quotient.** "Forms and anti-forms": the complement language has the same congruence, so the forms of L and of its anti-form ¬L coincide. That is a small, true, checkable statement. *Forms discovered vs invented* also gets a precise reading: the quotient is **determined** (discovered) once the observable is **chosen** (invented). The choice is the act of invention, and everything after it is computation.

---

## 2. The kernel every pillar instantiates

From the Relational Generativity foundation [C]:

$$
\mathcal K=(A,\;Q,\;\mathcal O,\;\delta,\;[\![\cdot]\!],\;\Pi,\;I,\;V)
$$

That is: alphabet, states, operators, transitions, denotation, projections (with declared loss), invariants, and verification interface. A **pillar** is a subject-agnostic choice of these eight fields together with its acceptance tests. A **domain** (language, music, a city, a game world, code) *applies* a pillar through an adapter (Plicastratum §7). The nine pillars below were found by building one demanding application, natural conversation. None of them mentions conversation in its definition.

The seven Plicastratum strata are kept as a checklist. For each pillar we say what fills the meta-, epi-, super-, sub-, hypo-, infra- and crypto- slots (§11).

---

## 3. Pillar P1: Plex and Tower (alphabets of alphabets) — `ingram/tower.py`

**Objects.**
- **Level 0** is the Unicode code space U = {0,…,0x10FFFF}. It is already a *product alphabet* [K]: every code point has coordinates (plane, row, cell, general category, bidi class, combining class, decomposition, 21-bit pattern) from the Unicode Character Database. `codepoint_coordinates('ب')` returns plane 0, row 6, cell 40, category Lo, bidi AL, name ARABIC LETTER BEH. These coordinates are the *n dimensions* of a character. They are facts, not metaphors.
- **Level k+1.** A new letter is a *certified recurring pair* of letters of level ≤ k, kept with its unfold rule. This is byte-pair folding [K] (Gage 1994; Sennrich, Haddow & Birch 2016), the move Sequitur makes (Nevill-Manning & Witten 1997). It is also exactly how LLM tokenisers build their vocabularies: **every modern LLM already runs on an alphabet of alphabets**, but discards the tower after training.

**Address [C on K].** A unit's address is its *derivation*, not an opaque hash:

```
addr(x) = tag ":" base32( ν(letters(x)) ) "." check(x)
ν(a₁…aₘ) = Σ (aᵢ+1)·N^(m−i)        (bijective base-N numeral, N = tower size)
```

- Bijective base-N numeration is a bijection Σ* ↔ ℕ [K]. So the address is **injective and decodable**. It looks like a hash, but it is a program that rebuilds its text (GIN: numerals are programs; GIN-PROP-006).
- The 20-bit check digest detects corruption without being needed for decoding.

**Laws (tests P1.\*).**
1. `explicate ∘ implicate = id` on all text.
2. `unaddr ∘ addr = id`.
3. A corrupted address is refused.
4. Every letter unfolds to level 0 in finitely many steps, so no capability is opaque.

**Measured [M] (EXP-06, 3,000 merges learned from Brown + SNAD docs + seed strings):**
- *apple* → 2 letters (`ap|ple`), address `ig:12FR8.4KGD`.
- *الباب* → **one level-4 letter**, address `ig:33H.0QRE`.
- *def f(x): return x + 1* → 15 letters, with `def` and `return` folded as letters.
- *PING* stays at level 0 (4 letters). That is the punctum: a letter whose meaning lives entirely in its channels (Plicastratum D3).
- Random multi-script strings round-trip **3,000/3,000**, and corruption is detected.

**n-dimensional projection [C].** A tower letter has three kinds of coordinate: tower coordinates (level, unfold tree), code-point coordinates (the UCD vector) and chart coordinates (P5 embeddings). A *projection* Π maps it to any subset and **declares what is lost**. For example, projecting *الباب* to "major category" keeps only L,L,L,L,L.

**Next.** Fold at the code-point level (base alphabet = code points seen, not bytes), so partial UTF-8 letters disappear. Then promote multi-letter morphemes certified by the dictionary (P2), not only by frequency.

---

## 4. Pillar P2: Lexical Self-System — `ingram/lexicon.py`

**Objects [C on K].** A dictionary D = (W, def), where def : W → W*. Reading every token of def(w) as the **address** of a headword gives the definitional graph G_D = (W, E), with u → v iff v occurs in def(u). The value of *apple* is not its meaning. It is **a word of addresses** (*fleshy, pome, fruit, rosaceous, tree, …*). Each of those is in turn a word of addresses searchable only inside the same dictionary. This is the user's "structure of structures of structures", and it has standard names:
- The **definitional closure** (BFS layers of G_D).
- The **Kernel** (repeatedly delete words that no remaining word uses).
- The **Core** (largest strongly connected component).
- A **grounding set** (a feedback vertex set: words that must be known from outside before all others become learnable from definitions). See Vincent-Lamarre, Massé, Lopes, Lord, Marcotte & Harnad, *Topics in Cognitive Science* 8(3), 2016 [K]; Harnad's symbol-grounding problem, 1990 [K].

**Proposition P2.1 (closed dictionaries mean only up to automorphism) [K, elementary].** Let φ be any automorphism of the labelled graph G_D. Every fact statable *inside* D (who defines whom, path lengths, closures, cores) is invariant under renaming each w by φ(w). Hence D alone cannot distinguish w from φ(w). When G_D has non-trivial automorphisms, meaning is underdetermined until something outside D breaks the symmetry. *This is the user's "self-system that has no meaning until you gloss outside its ary", stated as a theorem about graphs.* The outside can be a glossary, a perception, a demonstration or a second dictionary.

**Measured [M] (EXP-01, Webster's Unabridged 1913, Project Gutenberg #29765, public domain):**

| Quantity | Value |
|---|---|
| headwords (single-token) | 95,885 |
| definition tokens / resolved to a headword address | 3,314,896 / **94.3 %** |
| distinct address edges | 2,020,967 |
| closure of *apple* by layer | 1 → 182 → 6,773 → 24,201 → 31,325 → 32,992 → … → **33,527** |
| closures of *seed, tree, grow, fruit, the* | all terminate at the **same 33,527** |
| Kernel | 36,912 |
| strongly connected components in Kernel / Core | 1,800 / **33,519** |
| grounding set (greedy FVS on Core, self-reference ignored) | **≤ 11,360** (upper bound; minimum FVS is NP-hard, Karp 1972) |

*Reading.* Every word dissolves into one self-defining core within about 5–10 address steps. The core cannot be bootstrapped from inside. About 12% of headwords (an upper bound) must come from outside. Webster's illustrative quotations (Shak., Milton, Dryden) inflate the edges, so a quotation-stripped graph should give a smaller grounding set. **[H]** it will be ≤ 5%. Vincent-Lamarre et al. report about 1% for smaller learner dictionaries.

**Converse lookups [C, GIN-THM-001 transferred].** "Which word means X?" is the *converse* of def. It fails in the same two ways as division:
- **Image failure:** nothing is defined by X.
- **Kernel failure:** many words are; the converse is not single-valued (synonymy).

A reverse dictionary is therefore an admissibility problem, not a search problem. This pillar transfers to any address system (DNS, PURL, file paths) unchanged.

---

## 5. Pillar P3: Glossary Field (al-muṣṭalaḥ) — `ingram/gloss.py`

**Objects [C].** A **glossary** for subject c is a measure μ_c on W. It lives *outside* G_D: the dictionary supplies the relations, the glossary supplies where attention enters. **We do not invent the outside.** Webster labels its own senses with subjects, (Bot.), (Med.), (Law), (Naut.) and so on. Collecting them gives **250 subject glossaries with ≥ 30 terms each** [M]. The largest are Zoöl. 7,138, Bot. 5,166, Law 4,287, Naut. 3,865 and Med. 3,275.

**Contextual meaning [C on K].** The meaning of an utterance q in context c is the stationary distribution of a reader who follows definition addresses and, on stopping, returns either to the words heard or to the subject they stand in:

$$
[\![q]\!]_c=\mathrm{PPR}_\alpha\big(\lambda\,u_q+(1-\lambda)\,\mu_c\big),\qquad
\mathrm{lift}_c(v)=\frac{[\![q]\!]_c(v)}{[\![\cdot]\!]_\varnothing(v)}
$$

This is personalised PageRank (Brin & Page 1998; Haveliwala 2002) [K], spreading activation (Collins & Loftus 1975) [K] and the grammar-constrained surfer (CGT-PROP-010). Sense selection is PPR-weighted Lesk (Lesk 1986) [K], with a declared prior for Webster's sense order and an admissibility rule for compound sub-entries ("Apple of the eye" is admissible only if the context supplies *eye*).

**The ER scene, computed [M] (EXP-02).** Query {throat, swelling, apple, seed, shellfish}; values are log-lift:

| concept | patient: dictionary only | doctor: Med. glossary | botanist: Bot. glossary |
|---|---|---|---|
| irritation | −2.17 | **+3.49** | +0.16 |
| inflammation | −3.22 | **+1.34** | −2.02 |
| fever | −1.18 | **+2.52** | −0.30 |
| tumor | +0.46 | **+2.35** | +0.01 |
| tree | **+1.43** | +0.95 | +1.46 |
| sprout | −1.76 | −0.12 | **+2.20** |

The patient's strongest pull is *tree*: he is stuck in the dictionary chart. The doctor's glossary moves the mass to irritation, fever and inflammation. **Finding:** *allergy* (coined 1906) **is not in Webster 1913.** The dictionary chart cannot contain the doctor's answer. The fix is structural, not a better weight: an **atlas** of dictionaries.

**Atlas [K structure, C use].** Each dictionary is a chart. Overlaps are shared headwords, and the transition map identifies them. The engine carries Webster 1913 and WordNet 3.0 as two charts. *Your research corpus is a third chart* with the highest priority for its own terms. "What is a PURL?" returns your protocol from `purl/NOMENCLATURE.md` *and* Webster's *purl* (an embroidered border, or spiced ale), each labelled by chart. Sheaf vocabulary is reserved until gluing axioms are tested (Relational Generativity §2).

**Glossary of glossaries [C].** The labels {bot, med, law, …} form a level-2 alphabet. A measure on labels is a glossary of glossaries. Mapping an unseen context phrase ("in a hospital", "at the store") to a label is itself computed: which subject glossary carries most of the phrase's own definitional mass. The system **refuses to pretend** when no subject dominates (ratio < 1.5). Example: "seed in the family" gives *no subject dominates (engin 0.43 vs 0.35)*.

**Sense results [M]:**
- correct: *apple + {eye, pupil}* → "the pupil"
- correct: *apple + {tree, orchard, graft}* → fruit-tree sense
- correct: *seed + {plant, sow}* → Bot. sense
- correct: *seed + {father, descendant, offspring}* → "progeny; offspring"
- **failure:** *seed + "in the family"* (free phrase, no lexical overlap) → Bot. sense

**Failure recorded and fixed:** before the compound rule and the sense-order prior were added, apple + {market, pound, buy} chose a compound sub-entry ("Apple midge"); it now returns the fruit sense. Webster 1913 still has no *retail* sense, which is again an atlas problem.

- correct (after fix): *apple + {market, pound, buy, red, green}* → fruit sense

---

## 6. Pillar P4: Duality of Grammar and In-Grammar — `ingram/ingrammar.py`

**Grammar G [C on K].** A finite automaton over the 12 universal POS tags (Petrov, Das & McDonald 2012), learned from the tagged Brown corpus. A transition is admissible iff it occurs at least 25 times. Sentence rules: a verb is required, terminal punctuation is required, and stutter is forbidden. `check()` returns *(verdict, diagnostics)*, and an inadmissible output is **refused, never narrated** (STORY_GRAMMAR rule).

**In-grammar I [K].** Interpolated Kneser–Ney trigrams (Kneser & Ney 1995; Chen & Goodman 1998), trained on 1.69 M tokens: Brown, eight Gutenberg books, NPS Chat and 8,547 sentences of your research documents.

**Product decoding [K].** Grid beam search (Hokamp & Liu 2017). Beams are bucketed by how many anchors they have realised, so content constraints cannot be starved by fluency. Each step is pruned by G before it is scored by I. Prior art includes grammar-constrained decoding for LLMs (GBNF, Outlines, Willard & Louf 2023): we apply the same product to a small, inspectable I.

**Measured [M] (EXP-03):**

| | real sentences | same words shuffled |
|---|---|---|
| grammar G accepts | **61.8 %** | 4.4 % |
| in-grammar I, mean log-prob per token | **−5.50** | −7.91 |
| I perplexity on held-out Brown | 308 | — |

Generated natural forms (anchors → output, all G-admissible):
- {seed, grow} → *"I am sure she will grow larger than the seed."*
- {apple, tree} → *"The apple tree, and I am sure I should like to know what to do with it."*
- {city, walk, night} → *"…the little city mouse took a walk in the night before."*

**Observed limit.** I has a 2-word memory, so mode phrases ("I am sure") recur. That is the cost of a small I, and the reason §13 matters.

**Estimators of I (EXP-05) [M].** On the same Brown text, held-out bits per character: Witten–Bell n-gram order 2: 2.91; **order 4: 2.27**; order 6: 2.40 (sparsity). A numpy GRU (Cho et al. 2014; H = 192), trained for 25 CPU-minutes (9,247 steps, about 19 M characters seen): **2.25 bpc**, slightly better than the best count model. **Reading:** at about 7 CPU-minutes the GRU was still worse (3.32 bpc); at 25 minutes it crossed the n-gram. Both are estimators of the same I, and the harness does not care which one is plugged in. This matches the known regime: Mikolov et al. 2010 and later work show RNN LMs overtaking n-grams once adequately trained.

---

## 7. Pillar P5: Grammar of Embedding — `ingram/embed.py`

**The shift, precisely [K].** In an AI system, text becomes numbers twice:
1. **Encoding / addressing:** text → token ids. This is discrete, exact and invertible (P1).
2. **Embedding:** ids → vectors in ℝᵈ. This is a *projection* chosen so that inner products approximate an association measure.

Levy & Goldberg (NIPS 2014) proved that skip-gram with negative sampling (word2vec) implicitly factorises the **shifted PMI matrix**, M[w,c] = PMI(w,c) − log k. So an embedding is a low-rank **chart of a relational field**, and the "shift" is literally a shift: by log k. Transformer input embeddings are learned end to end, but they are still a map from the address alphabet to ℝᵈ, and their geometry is studied with the same tools.

**Two charts, no neural network [C on K].** Both use PPMI followed by truncated SVD (d = 100), on the same 15,000 words:
- **Distributional chart:** co-occurrence in running text (window 4, harmonic weights).
- **Definitional chart:** the dictionary address graph G_D, made symmetric (defines and used-in). *This is the user's Webster idea turned into a vector space*: a word is placed by the addresses in its definition, not by its neighbours in prose.

Projection loss is declared: rank 100 keeps 14.1% (distributional) and 16.3% (definitional) of the PPMI energy.

**Measured [M] (EXP-04).** Spearman ρ against WordNet Wu–Palmer similarity, an independent hand-built chart, on 7,761 noun pairs:

| chart | ρ |
|---|---|
| distributional (2.3 M tokens of text) | 0.351 |
| **definitional (Webster address graph)** | **0.483** |
| sum of both | 0.431 |

Nearest neighbours:
- *doctor*. Distributional: mary, carriage, sam, waiter. Definitional: **medicine, student, physician, expert**.
- *grammar*. Distributional: copenhagen, annals. Definitional: **literature, academy, science**.

*Caveats.* WordNet is itself definitional and taxonomic, which biases the comparison toward the dictionary chart. Distributional charts are known to improve greatly with 10³–10⁶ times more text. **[H]:** at equal text volume the definitional chart is the more data-efficient prior, so a fused chart should beat both once the distributional side is scaled. The naive sum here does not.

---

## 8. Pillar P6: Discourse Transition Grammar — `ingram/acts.py`, `converse.py`

**Objects [K + C].** A conversation is a word over an alphabet of acts: Greet, Bye, whQuestion, ynQuestion, Statement, Emotion, Accept, Reject, Clarify, Continuer, and so on (NPS Chat; Forsyth & Martell 2007). The act estimator is multinomial naive Bayes. The **dialogue policy** is a *transducer* from (user act, request production) to (response act, route). It is the conversational harness: an ordered request grammar whose productions are *help, why, trace, context, name, arithmetic, fetch, address, unfold, path, meaning, generate, similarity, greet, bye, thanks, affection, identity, question, reflect*. SNAD's separation holds: grammatical person is not attributed identity, and detection is not intent.

**Invariants (tested):**
- Every turn produces a record {text, route, act, evidence[], hash}.
- `/why` renders the evidence: a source path and section, a computation trace, an admissibility failure or a beam diagnostic.
- When retrieval has no passage above threshold, the reply says *"I don't have a sourced answer"* and labels anything composed as composed.
- Template variants are chosen by the in-grammar (log-prob per token minus a repetition penalty). The *wording* is I's choice; the *act* is G's.

---

## 9. Pillar P7: History-Bearing Identity — `ingram/ledger.py`

From Plicastratum D5–D7 and PURL's event log [C on K]:
- Each turn is an event in a **hash-chained ledger** (a Merkle chain, as in git).
- The memory group is ℤ^|acts|, and holonomy is the running sum.
- **Identity is declared at a depth:** `state`, `holonomy` or `chain`.

**Proposition P7.1 [K, elementary; test `test_identity_depths`].** With an *abelian* memory group, holonomy forgets order. The sessions (Greet, Statement) and (Statement, Greet) with the same last utterance are the same program at depth `holonomy` but different at depth `chain`. *Consequence for design:* to make "the same string, seven changes later, a different program", the memory group must be **non-abelian**, or the identity depth must be `chain`. Choosing G is choosing what the system can remember. Free groups, permutation groups and matrix groups such as SL(2,ℤ) all remember order.

**Promotion.** `mine()` finds recurring act motifs and promotes them to level-1 letters with their unfold rule. Every promoted letter stays a hypothesis until it recurs in held-out sessions.

---

## 10. Pillars P8 and P9: Addressable Computation and Admissible Arithmetic

**P8 — PURL semantics (`server.py`, `tools.py`) [C on PURL SPEC].**
- Every chart has an address: `/lex/apple`, `/gloss/med/apple`, `/field?q=…&domain=…`, `/path/ketchup/pyramid`, `/addr/…`, `/unaddr/…`, `/gen?anchors=…`, `/check?s=…`, `/trace/<session>`.
- **GET never mutates. POST /chat is the only effectful operation**, and it appends to the ledger.
- Resolution follows Resolve(u; E, H, D, A, R) from Relational Generativity §3.
- The engine can **fetch** `purl://` and `https://` addresses: GET only, with `Accept: application/purl+json`, and failures reported. In this sandbox GitHub resolves and the Railway PURL host is blocked by the network allowlist. That was reported, not hidden.

**P9 — Admissible arithmetic (`arith.py`) [K: GIN-THM-001].**
- Exact rationals throughout.
- 1/0 → **image failure**; 0/0 → **kernel failure**; 0/1 → 0.
- √−1 in ℝ → image failure.
- Exponent beyond budget → **budget** refusal (cost is part of admissibility, CGT-DEF-005).

The same two failure kinds apply to every *converse* operation in every pillar (reverse dictionary P2, unfold P1, sense lookup P3). That makes them the system's general vocabulary for "cannot".

---

## 11. The seven strata, filled for this system

| Stratum | In this system |
|---|---|
| 1 Metastratum (registry) | `/.well-known/ingram` manifest; this document; the test suite |
| 2 Epistratum (surface) | CLI and HTTP; templates; natural forms |
| 3 Superstratum (harness) | POS automaton; request grammar; act transducer; admissibility arithmetic |
| 4 Substratum (machine) | dictionary address graph; tower; KN lattice; PPR iteration |
| 5 Hyposubstratum (memory) | hash-chained ledger; holonomy; topic field; promoted motifs |
| 6 Infrasubstratum (data/runtime) | Webster 1913, WordNet 3.0, Brown, Gutenberg, NPS Chat, your 173 research documents; Python, numpy, scipy, NLTK |
| 7 Cryptosubstratum (generator) | seeds; learned merges; the subject labels the dictionary carried from the start |

**One knock, seven answers (applied to "what does apple mean in a hospital?"):**
1. Registered as route *meaning*.
2. Surfaced as text.
3. Admitted by the request grammar.
4. Computed by PPR on the address graph under μ_med.
5. Recorded with its hash.
6. Grounded in Webster 1913 and WordNet 3.0.
7. Attributable to the dictionary's own (Med.) labels.

---

## 12. Experiment register (results, failures, counterexamples)

| ID | Question | Outcome |
|---|---|---|
| EXP-01 | Is a dictionary a closed self-system? | **Supported.** Single 33.5k core; all closures converge. Grounding set ≤ 11,360 (upper bound). |
| EXP-02 | Does an outside glossary change meaning computably? | **Supported.** ER scene above. Sense selection: 5/5 scripted probes correct. *Failure:* free-phrase context ("in the family"). *Gap:* *allergy* absent from the 1913 chart. |
| EXP-03 | Is G×I a working product? | **Supported.** G separates real from shuffled 61.8% vs 4.4%; I separates them −5.50 vs −7.91. All 4 anchor probes admissible. *Limit:* G rejects 38% of real sentences (too strict at min_count 25 or tagger noise). *Limit:* I mode phrases recur. |
| EXP-04 | Can an embedding be built from the dictionary alone? | **Supported.** ρ 0.483 vs 0.351 (biased reference, see caveat). *Refuted:* naive fusion beats both (0.431). |
| EXP-05 | Count vs recurrent estimator of I under a small budget | n-gram order 4: 2.27 bpc (in seconds). GRU: 3.32 bpc at 7 min, **2.25 bpc at 25 min**. *Refuted:* "more n-gram order is better" (order 6: 2.40). |
| EXP-06 | Do tower addresses round-trip across scripts? | **Supported.** 3,000/3,000; corruption detected. *Limit:* byte-level base splits non-Latin letters into partial bytes. |

---

## 13. Does this supersede what an LLM does? An honest boundary

**What this system does that an LLM, by construction, does not:**
- **Every output has a derivation.** `/why` and the ledger show source passages, computations and refusals.
- **It refuses rather than narrates.** Inadmissible arithmetic, unknown facts and dominated subjects are all refused.
- **Exactness where exactness exists:** rationals, address round-trips, graph paths.
- **Editability.** Change a glossary weight, a dictionary entry or a grammar rule, and behaviour changes *in that place only*.
- **Tiny compute.** It builds in about a minute on a CPU and runs in milliseconds per turn.
- **Determinism and replay.**

**What an LLM does that this system does not (yet):**
- Open-domain fluency over long contexts.
- Breadth of world knowledge.
- Paraphrase, analogy and reasoning chains learned from about 10¹³ tokens.
- **The in-grammar here has a two-word memory.** That one number explains most of the gap.

**The scaling path that keeps the architecture, so you can expand it with more data.**
1. **Scale I without a neural net.** ∞-gram models over suffix arrays (Liu et al., "Infini-gram", 2024) give unbounded-order n-gram estimates over trillions of tokens with no training. They slot into `KN3`'s interface unchanged. kNN-LM retrieval (Khandelwal et al. 2020) is a second non-parametric route.
2. **Scale the charts.** Wiktionary (CC BY-SA) as a third dictionary chart. Domain glossaries (MeSH for medicine, IUPAC for chemistry, OSM tags for streets). The atlas closes the *allergy* gap.
3. **Scale G.** Replace the POS automaton with a broad-coverage grammar: Universal Dependencies treebanks, or the English Resource Grammar for HPSG. G is then a precise harness *and* a parser for planning.
4. **Optional neural estimator behind the same harness.** If an LLM is ever used, it becomes one estimator of I inside G, glossaries and the ledger. It proposes; the pillars admit, source and record. This is the God Seed rule ("optional LLM only for authored proposal text validated by the same grammar") generalised.

**[H] (the hypothesis this program is for):** at equal data, a system with explicit G, an atlas of glossaries and a large non-parametric I matches a neural LM on *grounded* tasks (definition, contextual sense, sourced QA, constrained composition), and beats it on faithfulness and verifiability. *Test:* a held-out benchmark of sourced questions scored for answer correctness *and* citation correctness. A refutation is a result.

---

## 14. Application to the HOMELESS engine (alphabets of alphabets of a world)

| Pillar | Engine use |
|---|---|
| P1 Tower | Street-turn alphabet {S, L, R, U} × junction degree → promoted walk-letters, with addresses that decode back to the route. Asset and mesh names folded the same way. |
| P2 Self-system | The world's *lore dictionary*: every NPC, place and item defined by addresses of others. The grounding set is what the player must *experience* rather than be told. That is a design rule from a theorem. |
| P3 Glossary | NPC context: the same utterance read under an NPC's glossary (a medic, a dealer, a priest). The ER scene is a dialogue mechanic. |
| P4 G × I | Storylet grammar as G (STORY_GRAMMAR.md), authored-line usage as I; NPC lines generated inside the grammar and refused when inadmissible. |
| P5 Charts | Tri-world walks compare chart-invariant walk-words (Plicastratum 8.1). Embeddings of places by their *definitions* (OSM tags) and by their *usage* (traffic). |
| P6 Acts | Player and NPC exchanges as act words; cohort steering as a level-2 transducer, explainable by unfolding. |
| P7 Ledger | Member-mode journeys as a hash-chained ledger; non-abelian memory so that returning home after seven changes is a different program (P7.1). |
| P8 Addresses | Every world object and recipe is a GET-pure address; the agentic SDK navigates the same addresses the game resolves. |
| P9 Admissibility | Every converse ("which route leads here?", "who could have said this?") reports image or kernel failure instead of inventing. |

---

## 15. Open problems

1. Exact or near-exact minimum grounding set of Webster 1913, with quotations stripped (ILP or kernelised FVS).
2. Gluing axioms for the atlas. When do Webster, WordNet and the research charts agree on overlaps? Measure disagreement as a cocycle.
3. Non-abelian conversational memory: which group makes sessions that are *meaningfully* different equal to sessions that *feel* different to a user?
4. A code-point-level tower with morpheme certification from P2.
5. The sourced-QA benchmark of §13.
6. Myhill–Nerode for the in-grammar: approximate congruence classes from I, and whether they recover POS tags without supervision (Brown clustering, 1992, says partly yes).

## References
Barrett, Jacob & Marathe 2000 · Brin & Page 1998 · Chen & Goodman 1998 · Cho et al. 2014 · Chomsky 1957 · Collins & Loftus 1975 · Forsyth & Martell 2007 · Gage 1994 · Harnad 1990 · Harris 1954 · Haveliwala 2002 · Hokamp & Liu 2017 · Karp 1972 · Khandelwal et al. 2020 · Kneser & Ney 1995 · Lesk 1986 · Levy & Goldberg 2014 · Liu et al. 2024 (Infini-gram) · Mikolov et al. 2010 · Myhill 1957 / Nerode 1958 · Nevill-Manning & Witten 1997 · Petrov, Das & McDonald 2012 · Robertson & Zaragoza 2009 · Sennrich, Haddow & Birch 2016 · Vincent-Lamarre et al. 2016 · Willard & Louf 2023 · Wöhler 1828 · Brown et al. 1992 (class-based n-grams) · and the akadaan310 corpus: CGT, Grammar in Numbers, SubstrateIO, PURL, SNAD, Musa/S-Theory, Plicastratum, Relational Generativity.
