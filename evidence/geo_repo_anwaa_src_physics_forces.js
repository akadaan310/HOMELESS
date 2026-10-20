/**
 * @module physics/forces
 * Composable force generators.
 *
 * A force is just `(body, dt, world) => void` that calls `body.applyForce()`.
 * The factories below close over their configuration so a world can hold a flat
 * list of them, and any of them can be mutated live (drag the attractor, fade
 * gravity out during a transition) without rebuilding the world.
 */
import { TAU, clamp } from '../core/math.js';

/** Uniform field, e.g. a gentle downward pull for menu items settling. */
export function uniform(fx, fy) {
  const f = { fx, fy, enabled: true };
  f.apply = (b) => { if (f.enabled) b.applyForce(f.fx * b.mass, f.fy * b.mass); };
  return f;
}

/**
 * Newtonian point gravity with Plummer softening.
 *
 * Softening (`soft`) is what stops a body that wanders close to the centre from
 * being flung to infinity in a single step — real n-body code does the same.
 */
export function pointGravity({ x = 0, y = 0, strength = 12000, soft = 40, falloff = 2, maxRadius = Infinity, group = 0 } = {}) {
  const f = { x, y, strength, soft, falloff, maxRadius, group, enabled: true };
  f.apply = (b) => {
    if (!f.enabled || b.invMass === 0) return;
    if (f.group && !(b.group & f.group)) return;
    const dx = f.x - b.x, dy = f.y - b.y;
    const d2 = dx * dx + dy * dy;
    if (d2 > f.maxRadius * f.maxRadius) return;
    const d = Math.sqrt(d2 + f.soft * f.soft);
    const mag = (f.strength * b.mass) / Math.pow(d, f.falloff);
    b.applyForce((dx / d) * mag, (dy / d) * mag);
  };
  return f;
}

/**
 * Pointer attractor / repulsor. Negative strength repels.
 * `ease` gives a soft edge so bodies don't snap on and off at the boundary.
 */
export function attractor({ x = 0, y = 0, strength = 8000, radius = 260, soft = 30, enabled = false, group = 0 } = {}) {
  const f = { x, y, strength, radius, soft, enabled, group };
  f.moveTo = (nx, ny) => { f.x = nx; f.y = ny; return f; };
  f.apply = (b) => {
    if (!f.enabled || b.invMass === 0) return;
    if (f.group && !(b.group & f.group)) return;
    const dx = f.x - b.x, dy = f.y - b.y;
    const d2 = dx * dx + dy * dy;
    if (d2 > f.radius * f.radius) return;
    const d = Math.sqrt(d2 + f.soft * f.soft);
    const edge = 1 - Math.sqrt(d2) / f.radius;     // 1 at centre → 0 at rim
    const mag = (f.strength * b.mass * edge * edge) / (d * d);
    b.applyForce((dx / d) * mag, (dy / d) * mag);
  };
  return f;
}

/**
 * Tangential swirl about a point — adds rotation without changing orbital
 * energy much. This is the force that makes a disturbed field re-settle into a
 * spiral rather than a shapeless blob.
 */
export function vortex({ x = 0, y = 0, strength = 600, radius = 400, direction = 1 } = {}) {
  const f = { x, y, strength, radius, direction, enabled: true };
  f.apply = (b) => {
    if (!f.enabled || b.invMass === 0) return;
    const dx = b.x - f.x, dy = b.y - f.y;
    const d = Math.hypot(dx, dy);
    if (d < 1e-3 || d > f.radius) return;
    const falloff = 1 - d / f.radius;
    const mag = (f.strength * b.mass * falloff) / d;
    b.applyForce(-dy * mag * f.direction, dx * mag * f.direction);
  };
  return f;
}

/** Linear (v) + quadratic (v^2) drag. Linear alone reads as "in syrup". */
export function drag({ linear = 0.4, quadratic = 0 } = {}) {
  const f = { linear, quadratic, enabled: true };
  f.apply = (b) => {
    if (!f.enabled || b.invMass === 0) return;
    const speed = Math.hypot(b.vx, b.vy);
    if (speed < 1e-6) return;
    const mag = f.linear * speed + f.quadratic * speed * speed;
    b.applyForce((-b.vx / speed) * mag * b.mass, (-b.vy / speed) * mag * b.mass);
  };
  return f;
}

/**
 * Curl-noise advection. Divergence-free, so the field never develops sinks
 * where every particle piles up — this is the slow "breathing" drift.
 */
export function flowField({ noise, scale = 0.0016, strength = 90, speed = 0.06, offset = 0 } = {}) {
  const out = { x: 0, y: 0 };
  const f = { noise, scale, strength, speed, offset, time: offset, enabled: true };
  f.step = (dt) => { f.time += dt * f.speed; };
  f.apply = (b) => {
    if (!f.enabled || b.invMass === 0) return;
    f.noise.curl(b.x * f.scale + f.time, b.y * f.scale - f.time, 0.001, out);
    b.applyForce(out.x * f.strength * b.mass, out.y * f.strength * b.mass);
  };
  return f;
}

/**
 * Spring each body toward a home position stored on it (`b.data.homeX/homeY`).
 * Layouts (rings, grids, constellations) are expressed as homes; interaction
 * pushes bodies away and this pulls them back, which is the whole feel of the
 * interface.
 */
export function homing({ stiffness = 24, damping = 6, group = 0 } = {}) {
  const f = { stiffness, damping, group, enabled: true };
  f.apply = (b) => {
    if (!f.enabled || b.invMass === 0 || !b.data) return;
    if (f.group && !(b.group & f.group)) return;
    const hx = b.data.homeX, hy = b.data.homeY;
    if (hx === undefined) return;
    const k = b.data.homeStiffness ?? f.stiffness;
    b.applyForce((hx - b.x) * k * b.mass, (hy - b.y) * k * b.mass);
    b.applyForce(-b.vx * f.damping * b.mass, -b.vy * f.damping * b.mass);
  };
  return f;
}

/** Per-body random walk of heading — keeps idle fields from looking frozen. */
export function wander({ strength = 30, rate = 0.6 } = {}) {
  const f = { strength, rate, enabled: true };
  f.apply = (b, dt) => {
    if (!f.enabled || b.invMass === 0) return;
    const d = b.data ?? (b.data = {});
    d.wanderAngle = (d.wanderAngle ?? Math.random() * TAU) + (Math.random() - 0.5) * f.rate;
    b.applyForce(Math.cos(d.wanderAngle) * f.strength * b.mass, Math.sin(d.wanderAngle) * f.strength * b.mass);
  };
  return f;
}

/**
 * Boids. Uses the world's spatial hash, so cost scales with local density
 * rather than total population.
 */
export function flock({ radius = 90, separation = 34, weights = {}, maxSpeed = 220, group = 0 } = {}) {
  const w = { separate: 1.6, align: 0.8, cohere: 0.6, ...weights };
  const near = [];
  const f = { radius, separation, weights: w, maxSpeed, group, enabled: true };
  f.apply = (b, dt, world) => {
    if (!f.enabled || b.invMass === 0 || !world.hash) return;
    if (f.group && !(b.group & f.group)) return;
    world.hash.query(b.x, b.y, f.radius, near);
    let sx = 0, sy = 0, ax = 0, ay = 0, cx = 0, cy = 0, n = 0, ns = 0;
    for (let i = 0; i < near.length; i++) {
      const o = near[i];
      if (o === b || !o.alive) continue;
      const dx = o.x - b.x, dy = o.y - b.y;
      const d = Math.hypot(dx, dy);
      if (d > f.radius || d < 1e-4) continue;
      ax += o.vx; ay += o.vy; cx += o.x; cy += o.y; n++;
      if (d < f.separation) { sx -= dx / (d * d); sy -= dy / (d * d); ns++; }
    }
    if (n === 0) return;
    const m = b.mass;
    if (ns) b.applyForce(sx * f.separation * 60 * w.separate * m, sy * f.separation * 60 * w.separate * m);
    b.applyForce((ax / n - b.vx) * w.align * m, (ay / n - b.vy) * w.align * m);
    b.applyForce((cx / n - b.x) * w.cohere * m, (cy / n - b.y) * w.cohere * m);
  };
  return f;
}

/**
 * Give a body the velocity of a circular orbit around a gravity source.
 * v = sqrt(GM/r) — without this, bodies dropped into a gravity well just fall in.
 */
export function orbitalVelocity(body, source, direction = 1, eccentricity = 0) {
  const dx = body.x - source.x, dy = body.y - source.y;
  const r = Math.hypot(dx, dy);
  if (r < 1e-3) return body;
  const soft = source.soft ?? 40;
  const v = Math.sqrt((source.strength ?? 12000) / Math.sqrt(r * r + soft * soft)) * (1 + eccentricity);
  body.vx = (-dy / r) * v * direction;
  body.vy = (dx / r) * v * direction;
  return body;
}

/** Hard speed ceiling — applied as a post-step clamp, not a force. */
export function speedLimit(max) {
  const f = { max, enabled: true, isLimiter: true };
  f.apply = (b) => {
    if (!f.enabled) return;
    const s = Math.hypot(b.vx, b.vy);
    if (s > f.max) { const k = f.max / s; b.vx *= k; b.vy *= k; }
  };
  return f;
}

/** Radial impulse used for taps, impacts and scene entrances. */
export function shockwave(world, x, y, { strength = 2600, radius = 320, falloff = 2 } = {}) {
  for (const b of world.bodies) {
    if (b.invMass === 0) continue;
    const dx = b.x - x, dy = b.y - y;
    const d = Math.hypot(dx, dy);
    if (d > radius || d < 1e-4) continue;
    const k = Math.pow(clamp(1 - d / radius, 0, 1), falloff);
    b.applyImpulse((dx / d) * strength * k * b.mass, (dy / d) * strength * k * b.mass);
  }
}
