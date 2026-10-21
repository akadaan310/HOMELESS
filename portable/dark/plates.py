"""§§63–66: bounded undirected edge replacement, explicit occupant policies.
This graph reference does not certify collision-safe continuous native motion.
"""
import copy
import math
from .life import Refusal, digest


def edge(e):
    return tuple(sorted(e))


class PlateWorld:
    def __init__(self, nodes, edges, occupants):
        self.nodes = copy.deepcopy(nodes)
        self.edges = {edge(e) for e in edges}
        self.occupants = copy.deepcopy(occupants)
        self.revision = 0

    def snapshot(self):
        return copy.deepcopy(dict(nodes=self.nodes, edges=sorted(self.edges), occupants=self.occupants, revision=self.revision))

    def reachable(self, source, destination):
        if source not in self.nodes or destination not in self.nodes:
            return False
        seen, todo = set(), [source]
        while todo:
            node = todo.pop()
            if node == destination:
                return True
            if node in seen:
                continue
            seen.add(node)
            for a,b in self.edges:
                if node == a: todo.append(b)
                if node == b: todo.append(a)
        return False

    def rewrite(self, expected_revision, remove, add, policies, max_displacement=3):
        before = self.snapshot()
        remove, add = edge(remove), edge(add)
        if expected_revision != self.revision or remove not in self.edges or add in self.edges or len(set(add)) != 2 or any(n not in self.nodes for n in add):
            raise Refusal('HD-064: stale revision or invalid edge match')
        if not math.isfinite(max_displacement) or max_displacement < 0 or set(policies) != set(self.occupants):
            raise Refusal('HD-065: every affected occupant needs bounded transport policy')
        next_occupants = copy.deepcopy(self.occupants)
        for identity, occupant in next_occupants.items():
            policy=policies[identity]
            if occupant['straddling'] or policy['policy']=='refuse':
                raise Refusal('HD-065: occupied refusal or boundary straddler')
            if policy['policy']=='carriage':
                offset=policy.get('offset',())
                if len(offset)!=2 or not all(math.isfinite(x) for x in offset) or math.hypot(*offset)>max_displacement:
                    raise Refusal('HD-065.1: displacement budget')
                occupant['position']=tuple(a+b for a,b in zip(occupant['position'],offset))
            elif policy['policy']=='relocation':
                destination=policy.get('destination')
                if destination not in self.nodes or not policy.get('authority') or type(policy.get('tick')) is not int or policy['tick'] < 0:
                    raise Refusal('HD-065: invalid witnessed relocation')
                if math.dist(occupant['position'],self.nodes[destination])>max_displacement:
                    raise Refusal('HD-065.1: relocation displacement budget')
                occupant.update(node=destination,position=self.nodes[destination])
            else:
                raise Refusal('HD-065: unsupported transport policy')
        self.edges.remove(remove); self.edges.add(add)
        self.occupants=next_occupants
        self.revision+=1
        return dict(before=before, after_hash=digest(self.snapshot()), policies=copy.deepcopy(policies),
                    effect_flags=['reachability'] + (['geometry'] if next_occupants != before['occupants'] else []), invalidated_paths=[list(remove)], revision=self.revision)

    def inverse(self, witness):
        if digest(self.snapshot()) != witness['after_hash']:
            raise Refusal('HD-064: inverse requires unchanged resulting state')
        old=witness['before']
        self.nodes=copy.deepcopy(old['nodes']); self.edges=set(map(tuple,old['edges']))
        self.occupants=copy.deepcopy(old['occupants']); self.revision+=1
