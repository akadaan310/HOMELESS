# SENSORY CALCULUS — SOUND, DIFFERENTIAL MICRO-WEATHER, CINEMATIC CAMERA

**Principle:** The world communicates without pop-ups. Source sounds, spatial audio, camera, lighting and weather can follow player behavior *and* create enticing but non-coercive opportunities for discovery. The source world remains separately computable from expressive game effects. Visual and audio effects are not arbitrary screen sprites masquerading as dynamics.

## A. Sound as a first-class generative model

Unreal **MetaSounds** provides sample-accurate DSP graph timing and procedural synthesis; augment with positioned imported high quality recordings, ambisonics where available, reverb and occlusion probes, dialogue audio and vehicle audio response. Core source reference: https://dev.epicgames.com/documentation/unreal-engine/metasounds-the-next-generation-sound-sources-in-unreal-engine

`SoundProgram=(sources, waveform/harmonic representation, spatial source transform, propagation, occlusion, listener pose, environment impulse response, envelopes, event clock, modulation graph, priority, provenance)`. A typed sound alphabet has *onset*, *duration*, *spectrum*, *intensity*, *direction*, *texture*, *distance*, *repetition*, *semantic cue*, *source identity* and *response* operators.

Audio targets: authentic automotive idle/speed/gear shift, pneumatic brakes, trucks and motorcycles, bicycle/freewheel/scooter, Cessna/airliner overhead, harbor ship horn and wakes, wind/palms, rain and puddle drip, wet tire pass-by, crowd and small conversation, food cart, transit, shops, concert, balloon burner, nighttime streets and regional ambience. Gather highest quality source samples and map by scene/body/height/distance; per-family DSP only when it improves coherence. Run a bus system for diegetic car radio, external live-space music, distant concerts, voice/dialogue, sky motifs, and UI/minimal-haptic notifications. Never allow abrupt musical cuts from street to car: crossfade in spatial/occlusion domain.

**Reactive**: footstep/material/wetness, vehicle RPM, camera orientation, room occlusion, passing crowds. **Prospective**: subtle source-emitting cues to draw attention toward an event based on spatial direction; the event exists regardless of player decision. Optimize salience with caps and cooldowns; no repeated manipulative attempts if player declines or ignores.

**Sound quality tests**: sample-to-event timing errors, envelope continuity, click/pop ratio, normalized cross-correlation across looping boundaries, loudness consistency (LUFS and true peak), channel phase, HRTF/spatial direction error in standardized headphone test, distance attenuation monotonicity, occlusion filter stability, speech intelligibility with traffic noise, mixing voice/music headroom, end-to-end audio/video sync in pixel stream. Human audition is final subjective QA supplement; numerical traces are the automation gate.

**Scientific signal experiment**: Player voluntarily opts into randomization between equally game-consistent sound-cue policies A/B, record *aggregate* response (`notice`, `ignore`, `walk-toward`, `mute`, `dismiss`) and circumstances, confidence intervals, p-value or Bayesian interval and correction for multiple hypotheses. Never infer private emotional state or personal diagnosis from a missed sound. NPC attention model can use a parallel synthetic population experiment, with an explicit agent policy and counterfactual baseline.

## B. Differential anti-pattern weather (visual microburst-like art system)

Use genuine meteorological fields (when available) as separate data feed: temperature, humidity, pressure, wind vectors, cloud fraction and precipitation rate at weather model grid/time. **Game perturbation field** is its own authored, non-hazard effect. Do not assert that a fun micro-vortex in front of a car is a real atmospheric microburst or physical disaster.

Let `v(x,t)` be game wind field, `ξ(x,t)` smooth bounded event perturbation, and `m(x,t)` wetness. One candidate model:

`∂v/∂t + (v·∇)v = -∇p/ρ + ν∇²v + f_world + f_event`  (bounded Navier–Stokes-inspired approximation, not full atmosphere)

`∂m/∂t = r(x,t) - evaporation(m,T,wind) - drainage(x,m)`.

Derived VFX: compute a vorticity field `ω=∇×v`, drive Niagara swirl particles/volumetrics, debris direction, tree sway, cloth movement, reflected light modulation, wet road reflectance and sound pressure envelope. Use a smooth compact support spatial kernel centered at an authored event for transient physically-inspired bubble/swirl, conservative energy budget and safety-coded cancellation when camera/network cannot maintain frame time.

**Numerical verification**: divergence residual for projected incompressible mode, integrator stability/CFL-style restriction, vorticity continuity, wetness bounds 0–1, conservation within selected approximation, unit-scaled wind magnitude, reflection roughness range and no jitter in projection. Match shader illumination estimates with display buffers/known light position. Report side-by-side numeric metrics across dry/wet state and stress frame budget. A player-facing weather ability modifies only the fictional game effect field unless explicitly editing an authored future world scenario.

## C. Camera as control system

Modes: `trailing-elevated`, `over-shoulder`, `cinema-arc`, `street-eye`, `first-person-AR`, `free-look`, `vehicle-interior`, `vehicle-follow`, `distant-witness`, `portal-transition`, `balloon-aerial`.

Reference control problem: choose camera pose `q(t),x(t)` minimizing jerk, occlusion, target-fraction deviation and horizon roll while honoring collision and camera-operator comfort. Smooth velocity/acceleration with bounded controller; use critically damped spring with rigorous test signals, not ad-hoc lerp per variable frame. Apply gaze tracking and occlusion ray casts under frame budget. In streamed mode interpolate input latency and camera prediction separately from authoritative world state.

**VR/AR-like view** is a game camera/style, not a claim that generic phone display simulates true stereoscopic VR. Headset mode must be developed separately to meet head-pose, frame and comfort requirements.

**Tampa intro cinematography**: aerial/street macro view, world already active; soundscape establishes depth; a local signal propagated as a social *wave* of noticing, not an entire population freeze. Traffic subtly slows where sensible; pedestrians turn/continue at believable ratios; weather puddle highlights shift; a constellation-like sky trace or cloud light cue can echo; one continuous camera easing transition settles into playable follow cam. Player can choose skip, quieter intro and motion-reduced profile. All state persists after onboarding.

**Quantitative camera gates:** rotational/angular velocity bound, roll jitter amplitude, jerk p95/p99, target framing normalized error, occlusion exposure time, camera collision violation zero, 30/60/90fps path agreement, stream input delay and camera resilience to packet jitter. Supplement numerical results with direct human-in-game artistic judgment, not isolated screenshot-check loops.
