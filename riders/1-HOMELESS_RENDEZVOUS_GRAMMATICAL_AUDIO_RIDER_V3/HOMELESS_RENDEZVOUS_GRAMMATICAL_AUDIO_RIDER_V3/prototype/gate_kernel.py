"""Tiny CPU-only model of speculative media staging vs world-event activation.

Research fixture, NOT a speech engine, asset decoder, PlayCanvas renderer,
or authenticated world state service. Standard library only.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib, json, math
from typing import Any


def canon(d: Any) -> bytes:
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def hashdata(d: Any) -> str:
    return hashlib.sha256(canon(d)).hexdigest()


def voice_key(text: str, locale: str, voice: str, model_hash: str, phonemes: str,
              prosody: str = "neutral", codec: str = "opus", sample_rate: int = 24000) -> str:
    if not all((text.strip(), locale, voice, model_hash, phonemes, prosody, codec)) or sample_rate <= 0:
        raise ValueError("incomplete voice form")
    return hashdata({"text": text, "locale": locale, "voice": voice, "model": model_hash,
                     "phonemes": phonemes, "prosody": prosody, "codec": codec,
                     "sample_rate": sample_rate})


@dataclass(frozen=True)
class Resource:
    id: str
    kind: str
    bytes: int
    priority: int
    decode_ms: int = 0

    def __post_init__(self):
        if not self.id or self.bytes < 0 or self.priority < 0 or self.decode_ms < 0:
            raise ValueError("invalid resource declaration")


@dataclass(frozen=True)
class Gate:
    id: str
    kind: str
    revision: int
    distance_m: float
    speed_mps: float
    horizon_s: float
    activation_radius_m: float
    admitted: bool
    resources: tuple[Resource, ...]

    def __post_init__(self):
        if not self.id or self.revision < 0 or not all(math.isfinite(v) for v in
            (self.distance_m, self.speed_mps, self.horizon_s, self.activation_radius_m)):
            raise ValueError("invalid gate coordinates")
        if min(self.distance_m, self.speed_mps, self.horizon_s, self.activation_radius_m) < 0:
            raise ValueError("invalid negative extent")

    def prepare_eligible(self) -> bool:
        # No inferred motion when stationary; only explicit nearby proximity earns preload.
        if not self.admitted:
            return False
        if self.distance_m <= self.activation_radius_m:
            return True
        return self.speed_mps > 0 and self.distance_m / self.speed_mps <= self.horizon_s


@dataclass(frozen=True)
class Plan:
    revision: int
    staged: tuple[str, ...]
    staged_bytes: int
    decode_ms: int
    eligible_gates: tuple[str, ...]
    expired_gates: tuple[str, ...]
    digest: str


class BootstrapPlanner:
    def __init__(self, byte_budget: int, decode_budget_ms: int):
        if byte_budget < 0 or decode_budget_ms < 0:
            raise ValueError("invalid budget")
        self.byte_budget = byte_budget
        self.decode_budget_ms = decode_budget_ms

    def plan(self, gates: list[Gate], revision: int) -> Plan:
        if any(g.revision != revision for g in gates):
            raise ValueError("stale world revision")
        if len({g.id for g in gates}) != len(gates):
            raise ValueError("duplicate gate IDs")
        eligible = [g for g in gates if g.prepare_eligible()]
        expired = sorted(g.id for g in gates if not g.prepare_eligible())
        pool: dict[str, Resource] = {}
        for g in eligible:
            for item in g.resources:
                if item.id in pool and pool[item.id] != item:
                    raise ValueError("resource declaration conflict")
                pool[item.id] = item
        selected: list[str] = []
        current_bytes, current_decode = 0, 0
        # Greedy priority: deterministic and bounded; not generally globally optimal.
        for r in sorted(pool.values(), key=lambda r: (-r.priority, r.bytes, r.id)):
            if current_bytes + r.bytes <= self.byte_budget and current_decode + r.decode_ms <= self.decode_budget_ms:
                selected.append(r.id)
                current_bytes += r.bytes
                current_decode += r.decode_ms
        fields = {"revision": revision, "staged": selected, "bytes": current_bytes,
                  "decode_ms": current_decode, "eligible": sorted(g.id for g in eligible),
                  "expired": expired}
        return Plan(revision, tuple(selected), current_bytes, current_decode,
                    tuple(fields["eligible"]), tuple(expired), hashdata(fields))


@dataclass
class WorldCommitter:
    """Minimal authoritative ledger: prefetch cannot change state and has no commit method."""
    world_revision: int = 0
    committed: dict[str, dict] = field(default_factory=dict)

    def activate(self, gate: Gate, *, actual_distance_m: float, approved: bool,
                 event_id: str, outcome: str) -> dict:
        if not approved or not gate.admitted or actual_distance_m < 0 or \
            actual_distance_m > gate.activation_radius_m:
            raise PermissionError("activation predicate not satisfied")
        if not event_id or not outcome:
            raise ValueError("untyped world event")
        if event_id in self.committed:
            if self.committed[event_id]["gate"] != gate.id or self.committed[event_id]["outcome"] != outcome:
                raise ValueError("event ID reused with conflicting meaning")
            return self.committed[event_id]
        if gate.revision != self.world_revision:
            raise ValueError("stale world for activation")
        entry = {"world_revision": self.world_revision + 1, "gate": gate.id,
                 "event": event_id, "outcome": outcome,
                 "prior": hashdata(self.committed)}
        entry["hash"] = hashdata(entry)
        self.committed[event_id] = entry
        self.world_revision += 1
        return entry
