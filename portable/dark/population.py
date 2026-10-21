"""§§24–26: exact Hamilton allocation and synthetic population continuity."""
from fractions import Fraction
import hashlib
import json


def allocate(total, weights):
    if type(total) is not int or total < 0 or not weights:
        raise ValueError('nonnegative integer parent and nonempty weights required')
    values = {k: Fraction(v) for k, v in sorted(weights.items())}
    if any(v < 0 for v in values.values()) or sum(values.values()) <= 0:
        raise ValueError('nonnegative weights with positive sum required')
    quotas = {k: total * v / sum(values.values()) for k, v in values.items()}
    result = {k: q.numerator // q.denominator for k, q in quotas.items()}
    order = sorted(values, key=lambda k: (-(quotas[k] - result[k]), k))
    for k in order[:total - sum(result.values())]:
        result[k] += 1
    return result


class Population:
    """Lazy identity reference. Allocations are synthetic estimates, never real humans."""
    def __init__(self, allocations, source):
        if not allocations or any(type(v) is not int or v < 0 for v in allocations.values()) or not source:
            raise ValueError('counts and source required')
        self.allocations = dict(sorted(allocations.items()))
        self.source = source
        self.total = sum(allocations.values())
        self.realized = {}
        self.visitors = {}
        self.histories = {}
        self.allocation_hash = hashlib.sha256(json.dumps([source, self.allocations], sort_keys=True).encode()).hexdigest()

    def resolve(self, identity):
        if type(identity) is not int or not 0 <= identity < self.total:
            raise ValueError('identity outside allocated population')
        start = 0
        for shard, count in self.allocations.items():
            if identity < start + count:
                return {'id': f'synthetic:{self.allocation_hash}:{identity}', 'resident_shard': shard,
                        'present_shard': self.visitors.get(identity, shard)}
            start += count
        raise AssertionError('allocation invariant')

    def realize(self, identity):
        record = self.resolve(identity)
        self.realized.setdefault(identity, record)
        self.histories.setdefault(identity, [])
        return dict(self.realized[identity])

    def migrate(self, identity, destination):
        current = self.resolve(identity)
        if destination not in self.allocations:
            raise ValueError('unknown destination')
        self.realize(identity)
        self.visitors[identity] = destination
        self.realized[identity]['present_shard'] = destination
        self.histories[identity].append({'origin': current['present_shard'], 'destination': destination})

    def present_counts(self):
        result = dict(self.allocations)
        for identity, destination in self.visitors.items():
            resident = self.resolve(identity)['resident_shard']
            result[resident] -= 1
            result[destination] += 1
        return result

    def counts(self):
        return dict(demographic_estimate=self.total, realized_identities=len(self.realized),
                    stored_histories=len(self.histories), active_actors=0, visible_characters=0, voiced_characters=0)
