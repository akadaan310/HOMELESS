# nidaa-engine

A zero-dependency physics and interaction engine for celestial interfaces —
star fields, constellation maps, orbital menus. Canvas2D, ~60KB of source, no
build step required.

It began as a set of static star-chart screens. This turns those compositions
into a general engine: the layouts are parameterised generators, the motion is
real simulation rather than keyframes, and every element is interactive.

```
┌──────────┐   ┌──────────┐   ┌───────────┐   ┌──────────┐
│  Input   │ → │ Gestures │ → │   Scene   │ ← │ Director │
│ pointers │   │ tap/drag │   │  world +  │   │  stack + │
│ keys     │   │ pinch    │   │  ui + fx  │   │ transitions│
└──────────┘   └──────────┘   └─────┬─────┘   └──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐   ┌───────────┐   ┌──────────┐
              │  World   │   │  UIRoot   │   │ Renderer │
              │ bodies   │   │ spring    │   │ sprites  │
              │ forces   │   │ nodes     │   │ bloom    │
              │ solver   │   │ widgets   │   │ camera   │
              └──────────┘   └───────────┘   └──────────┘
```

## Quick start

```bash
npm run demo    # http://localhost:5173
npm run check   # headless self-test (59 assertions)
```

```js
import { createEngine, Scene, layouts, forces, drawLinkSet } from 'nidaa-engine';

class Home extends Scene {
  setup() {
    // 1. Generate a layout.
    for (const spec of layouts.field(this.rng, { count: 200, minSpacing: 30 })) {
      this.world.add({
        x: spec.x, y: spec.y, mass: 1, pickable: true,
        data: { homeX: spec.x, homeY: spec.y },
        visual: spec.visual,
      });
    }

    // 2. Add forces. Stars drift on curl noise and spring back home.
    this.world.addForce(forces.homing({ stiffness: 3, damping: 2 }));
    this.world.addForce(forces.flowField({ noise: this.noise, strength: 26 }));

    // 3. Make the pointer push them around.
    const push = this.world.addForce(forces.attractor({ strength: -46000, radius: 250 }));
    this.listen(this.input, 'move', (p) => push.moveTo(p.wx, p.wy));

    this.listen(this.gestures, 'tap', (p) => {
      forces.shockwave(this.world, p.wx, p.wy, { strength: 900, radius: 300 });
      this.effects.ripple(p.wx, p.wy, { radius: 300 });
      this.camera.shake(0.2);
    });
  }

  paint(ctx) {
    this.renderer.drawBloom(this.world.bodies, { time: this.time });
    this.renderer.drawBodies(this.world.bodies, { time: this.time });
  }
}

const engine = createEngine(document.querySelector('canvas'));
engine.register('home', (ctx) => new Home(ctx));
engine.goTo('home', { transition: 'none' });
engine.start();
```

`createEngine` returns a `Director` with `renderer`, `input`, `gestures` and
`camera` attached. Nothing else is required — no bundler, no config.

## Design decisions

**Fixed timestep, interpolated rendering.** Physics runs at a constant 1/120s
via an accumulator; rendering happens once per animation frame with an `alpha`
for interpolating. Springs and orbits behave identically on a 60Hz laptop and a
120Hz phone, and a 250ms tab-switch hitch cannot blow the simulation up.

**Springs, not tweens, for interaction.** Every UI transform is a damped
harmonic oscillator solved analytically. Springs are *interruptible*: retarget
one mid-flight and it carries its velocity into the new motion. That single
property is why hover → press → release chains feel continuous. Durations and
easing curves are still available (`Tween`) for things with a definite end.

**Layouts are data, not drawing.** Each generator returns plain specs, so the
same layout can seed a physics world, a static background, or a target set that
bodies animate *into*. Morphing between two screens is just retargeting homes.

**Sprites are cached.** An 8-point star with curved edges and a multi-stop bloom
is ~20 path operations. At 1500 stars that is 1.8M ops/second. Each (kind, size)
pair is rasterised once into an offscreen canvas and blitted thereafter — the
field scene draws 215 stars in ~1ms.

**Seeded everything.** Every scene owns a `createRng(seed)`. The same seed always
produces the same field, which makes layouts reproducible across reloads,
screenshots and clients.

## Modules

| Module | Contents |
|---|---|
| `core` | `Vec2`, seeded `createRng`, curl `createNoise`, `Clock`, `Emitter`, `Pool`, `SpatialHash`, easing |
| `physics` | `Body`, `World`, `forces.*`, `constraints.*`, circle collisions |
| `render` | `Renderer`, `Camera`, `SpriteCache`, themes, link/tick/orbit/trail drawing |
| `interaction` | `Input` (pointer/touch/key), `Gestures` (tap/long-press/fling/pinch), `Picker`, `DragHandle`, `Inertia` |
| `ui` | `Spring`, `UINode` scene graph, `UIRoot`, `Effects`, widgets |
| `scene` | `Scene`, `Director`, transitions |
| `layout` | the composition generators |

### Forces

`uniform` · `pointGravity` (inverse-square, Plummer-softened) · `attractor`
(pointer pull/push) · `vortex` · `drag` (linear + quadratic) · `flowField`
(divergence-free curl noise) · `homing` (spring to a stored home) · `wander` ·
`flock` (boids over the spatial hash) · `speedLimit` · `shockwave` ·
`orbitalVelocity` (inject a true circular orbit)

### Constraints

`distance` · `minDistance` · `pin` · `ring` (confine to a circle/ellipse while
free to slide along it) · `containCircle` · `angleSpread` · `chain` · `necklace`

### Widgets

`StarButton` · `OrbitMenu` (inertial radial dial with detent snapping) ·
`Constellation` (graph laid out by depth, with locking/unlocking) · `Panel` ·
`Tooltip` · `ProgressRing`

## Demo scenes

Each scene in `demo/scenes/` is both an example and a reference composition made
interactive.

| Scene | What it demonstrates |
|---|---|
| **Field** | 240 bodies under curl drift + homing; pointer repulsion; proximity links rebuilt on a timer; tap shockwave |
| **Orbits** | True two-body gravity, softened; orbital velocity injection; comet trails; spring-based dragging |
| **Constellation** | Graph layout by depth, distance constraints, unlock propagation, sticky hover, world-anchored tooltips |
| **Dial** | `OrbitMenu` driven by fling velocity → inertia → detent snap; wheel and drag input |
| **Clusters** | Ring constraints + rigid sub-constellations; focus pulls one cluster in and pushes the rest out |
| **Cross** | Chained arms with elastic pull-to-commit; a drag past threshold fires, short of it snaps back |
| **Deep** | Three parallax planes with frame-rate-independent damping |

Keyboard: `←` `→` change scene, `1`–`7` jump, `space` pauses.

## Theming

A theme is one plain object. Swap it to re-skin everything:

```js
import { themes, compileTheme } from 'nidaa-engine';

renderer.setTheme({
  ...themes.midnightGold,
  palette: {
    ...themes.midnightGold.palette,
    primary: { core: '#fff', mid: '#7dd3fc', rim: '#0369a1', glow: '#0ea5e9' },
  },
});
```

`body.visual.kind` selects the palette entry, so a body tagged `'accent'` follows
the theme without any per-body colour.

## Performance notes

Measured in headless Chromium (software rasteriser) at 440×900 @2x:

| Scene | Bodies | Draw time |
|---|---|---|
| Field | 240 (215 drawn, 25 culled) | ~1.1 ms |
| Orbits | 80 | ~0.5 ms |
| Clusters | 35 | ~0.3 ms |

The levers, in order of impact: `maxDpr` (a 3× screen triples fill cost),
`bloom: false`, `culling` padding, and the rebuild interval for proximity links.

## Project layout

```
src/        engine (plain ESM, no build step)
types/      hand-written .d.ts, checked under --strict
demo/       gallery app + seven scenes
tools/      static server, headless self-test, screenshot capture
```

## License

MIT
