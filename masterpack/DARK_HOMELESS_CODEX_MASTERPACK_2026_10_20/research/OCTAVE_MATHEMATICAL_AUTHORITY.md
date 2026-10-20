# COMPUTATIONAL MATHEMATICAL AUTHORITY — GNU OCTAVE → DARK ENGINE

**Objective:** A deterministic, testable numeric and strategic authority for decisions, movement, camera, physics-parameter inference, traffic, social game theory, procedural events, content prioritization, sound timing and other gameplay. GNU Octave is the mathematician's reference and diagnostic laboratory—not a complete interpreter copied into the game APK.

## Reference solver catalog

- Core GNU Octave: `glpk` mixed integer/linear optimization, `qp` quadratic optimization, `sqp` constrained nonlinear optimization, `fminunc`/`fminsearch` baselines, `ode45`/`lsode` differential equations, `svd`/`qr`/`eig`/`chol`/sparse-matrix solvers, FFT and statistical regression.
- Octave Control package: `lqr`, `dlqr`, `kalman`, linear systems and state estimation where relevant.
- For in-engine runtime, choose bounded native/C++ solver implementations or lightweight services with identical typed input/output schemas. Octave batch jobs produce frozen reference witness files and numeric tolerances. Never stall the render thread on an iterative solve.

## Formal problem contract

`Problem = (variables, feasible-set, objectives, constraints, data-revisions, units, numerical-policy, optimizer, tie-break, seed, budget, observables)`.

`Result = (status, primal, dual-if-available, objective-value, residuals, optimality-gap/bound-if-known, seed, solver/version, resource-usage, witness-hash)`.

Status distinguishes `optimal-certified`, `locally-optimal`, `approximate-feasible`, `infeasible`, `unbounded`, `not-converged`, `timed-out`, `ambiguous-equilibria`, `unsupported`. Never call a local solution a global optimum without proof. A deterministic policy with random seeded draws is reproducible given fixed execution order; it is not a physical law.

## Mathematical model families

1. **Multimodal route planning:** graph `G=(V,E)`, costs for time/scenic/comfort/availability and path-language automaton `A`; solve shortest feasible path in product graph `G×A`. Octave may validate cost matrices and constraints. Multiobjective Pareto and explicit selection policy for scenic, curious, relaxed and purposeful walking. Transport edge types cannot silently mix pedestrian, road, flight or maritime.
2. **Vehicle control:** state `x=[position,heading,v,steering,slip,...]`, continuous/discrete plant dynamics, feasible steering/acceleration envelope, observer Kalman/LQR as baseline, trajectory optimization `min Σ(x-Q)^TQ(x-Q)+u^TRu+jerk^2`; reference controller in Octave; runtime deterministic simulation in Chaos under simulation budgets. Travel is fictional gameplay, never a live real-world driving controller.
3. **Camera:** optimize 3D camera path with jerk and roll/horizon regularizers, target framing, collision/occlusion and field-of-view preference. `argmin ∫ w_j||d³x/dt³||² + w_o occlusion + w_h horizon + w_d subject-distance`. Benchmark at 24,30,60,90fps time series, including asynchronous stream input.
4. **Game theory:** finite/bayesian/stochastic games with independent actor utility and partial observations, feasible negotiation actions, robust or bounded rational policies, clearly declared equilibrium-selection tie-break, ability to decline. Use Octave feasible-set/matrix computations for zero-sum/minimax and finite equilibria, an independent game-theory solver where Octave alone lacks routines. Keep interests/unknowns explicit; do not make NPCs puppets of the player.
5. **Causal event reach:** measured vs replayed causal dependency cones, paired-run counterfactual state, confidence intervals when experiments stochastic. A Shapley allocation can be used with exact enumeration for tiny coalitions, Monte Carlo with uncertainty for large ones.
6. **Program patterns:** graph signatures, spectral embeddings, nearest neighbors, SVD/projection loss and match certificates; optimize discovery thresholds against null baselines and held-out cities.
7. **Physical effects:** simplified incompressible/advective 2D/3D vector field perturbations, bounded viscosity, vorticity and camera-space render parameters. Differential model fidelity and stability tests, separate from real forecasts.
8. **Statistical sound routing:** predeclared comparisons for cue timing/spatial attention, interrupted time series, A/B design with voluntary user controls and statistical uncertainty. Statistical attribution never becomes permission for covert manipulation.

## Tampa origin data fixture

`home_earth_anchor = (Dale Mabry Highway N, West Spruce Street, Tampa, FL, USA)`. Use sourced intersection coordinates from verified map adapter, not a guessed longitude/latitude. Anchor geometry and routes for player spawn, traffic signal, sidewalk flow, intersection audio, nearby mall/airport travel, and fictional storefront/crowd. The actual sign identities are new in-game aliases. Dark has an explicit separate origin record for Marina del Rey.

## Quantitative acceptance

- `A01` identical input/seed/reference ⇒ same solver output/hash within declared floating-point tolerance and reproducibility policy.
- `A02` constraints under/overdetermine the solution as expected; numerical failures are classified before advancing world state.
- `A03` named objective, feasible actions and tie-break are logged for at least three NPC negotiation cases: agreement, refusal and indeterminate conflict.
- `A04` camera jerk, horizon and occlusion metrics improve vs a controlled baseline in scripted track under same hardware/time. Report metric values, not only 'cinematic'.
- `A05` autonomous walking trajectory obeys network topology, comfort acceleration and crossing constraints; user can always interrupt to manual mode.
- `A06` no numerical solve blocks the foreground UE game thread beyond budget.
- `A07` fixed mathematical benchmark corpus executable in an Octave CLI environment, with generated output JSON/hashes and corresponding native runtime values.

Official reference: https://docs.octave.org/ ; https://gnu-octave.github.io/pkg-control/ ; related prior research in the attached user-authored Octave/Tampa specification.
