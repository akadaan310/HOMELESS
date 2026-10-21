"""HD-005.1 bounded admission subset; never executes policy text as host code.

JSON lexical grammar: UTF-8 JSON object; identifiers [a-z][a-z0-9_]{0,63}.
Predicates are registered boolean input names or {all:[predicate,...]},
{not:predicate}. Max policy 64 clauses, depth 8, fanout 16. No recursion,
loops, calls or implicit state. Unknown inputs fail closed. Operations are
registered externally; this evaluator proposes verdicts, not world commits.
"""
import hashlib
import json
import re

IDENT = re.compile(r'^[a-z][a-z0-9_]{0,63}$')
class PolicyError(ValueError):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def compile_policy(policy, predicates, operations, witnesses, tests):
    if not isinstance(policy, dict) or set(policy) != {'revision', 'constitution_sha256', 'clauses'}:
        raise PolicyError('unsupported policy schema')
    if type(policy['revision']) is not int or policy['revision'] != 1 or not isinstance(policy['constitution_sha256'], str) or not re.fullmatch('[0-9a-f]{64}', policy['constitution_sha256']):
        raise PolicyError('invalid revision/digest')
    clauses = policy['clauses']
    if not isinstance(clauses, list) or not 1 <= len(clauses) <= 64:
        raise PolicyError('clause budget')
    def check(p, depth=0):
        if depth > 8: raise PolicyError('predicate depth')
        if isinstance(p,str):
            if p not in predicates: raise PolicyError('unknown predicate: '+p)
        elif isinstance(p,dict) and set(p)=={'not'}: check(p['not'],depth+1)
        elif isinstance(p,dict) and set(p)=={'all'} and isinstance(p['all'],list) and 1<=len(p['all'])<=16:
            for q in p['all']: check(q,depth+1)
        else: raise PolicyError('unsupported predicate')
    ids=set(); signatures=set()
    for c in clauses:
        if not isinstance(c,dict) or set(c)!={'id','subject','when','may','requires','preserves','budget','witness','verifies'}:
            raise PolicyError('unsupported clause schema')
        if not all(isinstance(c[k],str) and IDENT.fullmatch(c[k]) for k in ('id','subject','may','witness','verifies')):
            raise PolicyError('invalid identifier')
        if c['id'] in ids: raise PolicyError('duplicate clause')
        ids.add(c['id'])
        if c['may'] not in operations or c['witness'] not in witnesses or c['verifies'] not in tests:
            raise PolicyError('unresolved operation/witness/test')
        if type(c['budget']) is not int or not 0<=c['budget']<=1000000: raise PolicyError('invalid budget')
        for k in ('when','requires','preserves'): check(c[k])
        # Refuse conflicting parallel definitions, rather than invent precedence.
        signature=(c['subject'],c['may'],canonical(c['when']))
        if signature in signatures: raise PolicyError('overlapping clause definitions')
        signatures.add(signature)
        if c['requires']=={'not':c['preserves']} or c['preserves']=={'not':c['requires']}:
            raise PolicyError('contradictory requirements')
    return Compiled(json.loads(canonical(policy)))

class Compiled:
    def __init__(self, policy):
        self._encoded=canonical(policy)
        self.digest=hashlib.sha256(self._encoded).hexdigest()
    def evaluate(self, subject, operation, inputs, cost):
        if not isinstance(inputs,dict) or len(inputs)>128 or any(not isinstance(k,str) or type(v) is not bool for k,v in inputs.items()):
            return dict(status='REFUSE',clause=None,witness='invalid_inputs',policy_digest=self.digest)
        def pred(p):
            if isinstance(p,str): return inputs.get(p) is True
            if 'not' in p:
                # Missing data cannot become permission through negation.
                return known(p['not']) and not pred(p['not'])
            return all(pred(x) for x in p['all'])
        def known(p):
            if isinstance(p,str): return type(inputs.get(p)) is bool
            if 'not' in p: return known(p['not'])
            return all(known(x) for x in p['all'])
        for c in json.loads(self._encoded)['clauses']:
            if c['subject']==subject and c['may']==operation and pred(c['when']):
                ok=type(cost) is int and 0<=cost<=c['budget'] and pred(c['requires']) and pred(c['preserves'])
                return dict(status='ADMIT' if ok else 'REFUSE',clause=c['id'],witness=c['witness'],policy_digest=self.digest,obligation=c['verifies'])
        return dict(status='REFUSE',clause=None,witness='no_applicable_clause',policy_digest=self.digest)
