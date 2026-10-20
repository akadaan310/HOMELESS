/**
 * @module physics/world
 * The simulation container: bodies, forces, constraints, broadphase.
 *
 * One fixed `step(dt)` does:
 *   1. clear accelerations, run force generators
 *   2. semi-implicit Euler integration (+ optional substeps)
 *   3. global damping and speed limits
 *   4. constraint relaxation passes
 *   5. collisions
 *   6. bounds, lifetimes, reaping
 */
import { Emitter } from '../core/emitter.js';
import { SpatialHash } from '../core/spatial-hash.js';
import { SwapList } from '../core/pool.js';
import { Body } from './body.js';
import { resolveCollisions } from './collision.js';

export class World extends Emitter {
  constructor(opts = {}) {
    super();
    this.bodies = [];
    this.forces = [];
    this.constraints = [];

    this.damping = opts.damping ?? 0.06;        // fraction of velocity lost per second
    this.substeps = opts.substeps ?? 1;
    this.constraintIterations = opts.constraintIterations ?? 3;
    this.collisions = opts.collisions ?? false;
    this.collisionOptions = opts.collisionOptions ?? {};
    this.maxSpeed = opts.maxSpeed ?? 4000;

    /** null = infinite space; otherwise {x,y,w,h, mode:'bounce'|'wrap'|'clamp'|'kill'} */
    this.bounds = opts.bounds ?? null;

    this.hash = opts.hash === false ? null : new SpatialHash(opts.cellSize ?? 80);
    this.hashEnabled = opts.hash !== false;
    this.time = 0;
    this.stepCount = 0;
    this._toRemove = new SwapList();
  }

  // ---------------------------------------------------------------- authoring

  add(bodyOrOpts) {
    const body = bodyOrOpts instanceof Body ? bodyOrOpts : new Body(bodyOrOpts);
    this.bodies.push(body);
    this.emit('bodyAdded', body);
    return body;
  }

  addMany(list) { return list.map((b) => this.add(b)); }

  remove(body) {
    const i = this.bodies.indexOf(body);
    if (i < 0) return false;
    this.bodies.splice(i, 1);
    this.constraints = this.constraints.filter((c) => c.a !== body && c.b !== body && c.body !== body);
    this.emit('bodyRemoved', body);
    return true;
  }

  addForce(force) { this.forces.push(force); return force; }
  removeForce(force) {
    const i = this.forces.indexOf(force);
    if (i >= 0) this.forces.splice(i, 1);
    return i >= 0;
  }

  addConstraint(c) {
    if (Array.isArray(c)) { c.forEach((x) => this.constraints.push(x)); return c; }
    this.constraints.push(c);
    return c;
  }

  removeConstraint(c) {
    const i = this.constraints.indexOf(c);
    if (i >= 0) this.constraints.splice(i, 1);
    return i >= 0;
  }

  clear() {
    this.bodies.length = 0;
    this.forces.length = 0;
    this.constraints.length = 0;
    this.hash?.clear();
    return this;
  }

  // ---------------------------------------------------------------- stepping

  step(dt) {
    const sub = dt / this.substeps;
    for (const f of this.forces) f.step?.(dt);

    for (let s = 0; s < this.substeps; s++) this._integrate(sub);

    for (let i = 0; i < this.constraintIterations; i++) {
      const cs = this.constraints;
      for (let c = 0; c < cs.length; c++) cs[c].solve();
    }

    if (this.collisions) resolveCollisions(this, this.collisionOptions);
    if (this.bounds) this._applyBounds();

    this._reap(dt);
    this.time += dt;
    this.stepCount++;
    this.emit('step', dt);
  }

  _integrate(dt) {
    const bodies = this.bodies;

    if (this.hashEnabled && this.hash) {
      this.hash.clear();
      for (let i = 0; i < bodies.length; i++) {
        const b = bodies[i];
        if (b.alive) this.hash.insert(b, b.x, b.y);
      }
    }

    for (let i = 0; i < bodies.length; i++) {
      const b = bodies[i];
      if (!b.alive || b.sleeping) continue;
      b.ax = 0; b.ay = 0;
    }

    const forces = this.forces;
    for (let f = 0; f < forces.length; f++) {
      const force = forces[f];
      if (force.isLimiter) continue;
      for (let i = 0; i < bodies.length; i++) {
        const b = bodies[i];
        if (b.alive && !b.sleeping && b.invMass !== 0) force.apply(b, dt, this);
      }
    }

    // Exponential damping is frame-rate independent; a naive `v *= 0.98` is not.
    const globalDamp = Math.pow(1 - this.damping, dt);

    for (let i = 0; i < bodies.length; i++) {
      const b = bodies[i];
      if (!b.alive) continue;
      b.px = b.x; b.py = b.y;
      if (b.sleeping || b.invMass === 0) continue;

      b.vx += b.ax * dt;
      b.vy += b.ay * dt;

      const d = b.damping ? Math.pow(1 - b.damping, dt) * globalDamp : globalDamp;
      b.vx *= d;
      b.vy *= d;

      const speed = Math.hypot(b.vx, b.vy);
      if (speed > this.maxSpeed) {
        const k = this.maxSpeed / speed;
        b.vx *= k; b.vy *= k;
      }

      b.x += b.vx * dt;
      b.y += b.vy * dt;
      b.age += dt;
    }

    for (let f = 0; f < forces.length; f++) {
      const force = forces[f];
      if (!force.isLimiter) continue;
      for (let i = 0; i < bodies.length; i++) {
        const b = bodies[i];
        if (b.alive && !b.sleeping) force.apply(b, dt, this);
      }
    }
  }

  _applyBounds() {
    const { x, y, w, h, mode = 'bounce', padding = 0 } = this.bounds;
    const l = x + padding, r = x + w - padding, t = y + padding, bm = y + h - padding;

    for (const b of this.bodies) {
      if (!b.alive || b.invMass === 0) continue;
      const rad = b.radius;

      if (mode === 'wrap') {
        const ww = r - l, hh = bm - t;
        if (b.x < l - rad) { b.x += ww + rad * 2; b.px = b.x; }
        else if (b.x > r + rad) { b.x -= ww + rad * 2; b.px = b.x; }
        if (b.y < t - rad) { b.y += hh + rad * 2; b.py = b.y; }
        else if (b.y > bm + rad) { b.y -= hh + rad * 2; b.py = b.y; }
        continue;
      }

      if (mode === 'kill') {
        if (b.x < l - rad || b.x > r + rad || b.y < t - rad || b.y > bm + rad) b.alive = false;
        continue;
      }

      const bounce = mode === 'bounce';
      if (b.x - rad < l) { b.x = l + rad; if (bounce && b.vx < 0) b.vx *= -b.restitution; else if (!bounce) b.vx = 0; }
      else if (b.x + rad > r) { b.x = r - rad; if (bounce && b.vx > 0) b.vx *= -b.restitution; else if (!bounce) b.vx = 0; }
      if (b.y - rad < t) { b.y = t + rad; if (bounce && b.vy < 0) b.vy *= -b.restitution; else if (!bounce) b.vy = 0; }
      else if (b.y + rad > bm) { b.y = bm - rad; if (bounce && b.vy > 0) b.vy *= -b.restitution; else if (!bounce) b.vy = 0; }
    }
  }

  _reap(dt) {
    let dirty = false;
    for (let i = 0; i < this.bodies.length; i++) {
      const b = this.bodies[i];
      if (b.life !== Infinity) {
        b.life -= dt;
        if (b.life <= 0) b.alive = false;
      }
      if (!b.alive) dirty = true;
    }
    if (!dirty) return;
    const dead = this.bodies.filter((b) => !b.alive);
    this.bodies = this.bodies.filter((b) => b.alive);
    if (this.constraints.length) {
      const set = new Set(dead);
      this.constraints = this.constraints.filter(
        (c) => !set.has(c.a) && !set.has(c.b) && !set.has(c.body)
      );
    }
    for (const b of dead) this.emit('bodyRemoved', b);
  }

  // ---------------------------------------------------------------- querying

  /** Nearest pickable body to a point, or null. */
  pick(x, y, maxDistance = 40, filter = null) {
    let best = null, bestD = maxDistance;
    const candidates = this.hash ? this.hash.query(x, y, maxDistance) : this.bodies;
    for (const b of candidates) {
      if (!b.alive || !b.pickable) continue;
      if (filter && !filter(b)) continue;
      const d = Math.hypot(b.x - x, b.y - y) - (b.pickRadius || b.radius);
      if (d < bestD) { bestD = d; best = b; }
    }
    return best;
  }

  queryRadius(x, y, radius, out = []) {
    out.length = 0;
    const candidates = this.hash ? this.hash.query(x, y, radius) : this.bodies;
    const r2 = radius * radius;
    for (const b of candidates) {
      if (!b.alive) continue;
      const dx = b.x - x, dy = b.y - y;
      if (dx * dx + dy * dy <= r2) out.push(b);
    }
    return out;
  }

  get bodyCount() { return this.bodies.length; }

  /** Total kinetic energy — handy for auto-sleeping a settled scene. */
  get energy() {
    let e = 0;
    for (const b of this.bodies) if (b.invMass > 0) e += 0.5 * b.mass * (b.vx * b.vx + b.vy * b.vy);
    return e;
  }
}
