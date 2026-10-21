"""§§12.1,15,32,60: scoped event-memory reference, not authentication server."""
import copy
import hashlib
import json


class Refusal(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


class LifeWorld:
    def __init__(self):
        self.entities = {}
        self.events = []
        self.genesis = {}
        self.head = '0' * 64

    def register(self, identity, kind, policy='reserved'):
        if not identity or identity in self.entities or policy not in ('curious', 'reserved'):
            raise Refusal('HD-012.1: unique identity and supported policy required')
        record = dict(entity_id=identity, kind=kind, state={}, traits={}, memory=[], observations=[],
                      relations={}, affordances=[], policy=policy, capabilities=[], dynamics='passive',
                      schedule=[], budget={'max_observations':1024}, provenance='synthetic-fixture@1')
        self.genesis[identity] = copy.deepcopy(record)
        self.entities[identity] = record

    def commit(self, event_id, actor, tick, action, observers):
        observers = sorted(set(observers))
        body = dict(event_id=event_id, actor=actor, tick=tick, action=action, observers=observers)
        for old in self.events:
            if old['event_id'] == event_id:
                if any(old[k] != v for k,v in body.items()):
                    raise Refusal('HD-060: idempotency key collision')
                return copy.deepcopy(old)
        if actor not in self.entities or any(o not in self.entities for o in observers) or type(tick) is not int or tick < 0 or (self.events and tick < self.events[-1]['tick']):
            raise Refusal('HD-015/032: invalid actor, observer or monotonic tick')
        if not event_id or not isinstance(action,str) or not action:
            raise Refusal('HD-060: typed event required')
        if any(len(self.entities[o]['observations']) >= self.entities[o]['budget']['max_observations'] for o in observers):
            raise Refusal('HD-012.1: observation budget')
        body.update(sequence=len(self.events)+1, previous=self.head, read_set=[actor], write_set=observers,
                    causes=[], source_version='synthetic-fixture@1')
        body['hash'] = digest(body)
        self.events.append(body)
        self.head = body['hash']
        for observer in observers:
            self.entities[observer]['observations'].append(event_id)
            self.entities[observer]['memory'].append(dict(event_id=event_id, tick=tick, action=action))
        return copy.deepcopy(body)

    def react(self, identity, action):
        return 'notice' if self.entities[identity]['policy']=='curious' and action=='greeting' else 'continue'

    def snapshot(self):
        return copy.deepcopy(dict(schema=1, genesis=self.genesis, entities=self.entities, events=self.events, head=self.head))

    @classmethod
    def restore(cls, snapshot):
        if snapshot.get('schema') != 1:
            raise Refusal('HD-078: unsupported snapshot schema')
        world = cls()
        world.genesis = copy.deepcopy(snapshot['genesis'])
        world.entities = copy.deepcopy(snapshot['genesis'])
        for event in snapshot['events']:
            check = dict(event); stored = check.pop('hash', None)
            if digest(check) != stored or event['previous'] != world.head:
                raise Refusal('HD-060: tampered history')
            replayed=world.commit(event['event_id'],event['actor'],event['tick'],event['action'],event['observers'])
            if replayed != event:
                raise Refusal('HD-060: replay mismatch')
        if world.head != snapshot['head'] or world.entities != snapshot['entities']:
            raise Refusal('HD-060: snapshot/head mismatch')
        return world
